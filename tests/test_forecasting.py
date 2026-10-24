"""Behavioral acceptance tests using generated descriptors, never reserve data."""
import copy
from datetime import datetime, timedelta
import json
from pathlib import Path
import tempfile
from threading import Thread
import unittest
from unittest.mock import patch
from urllib.error import HTTPError
from urllib.request import Request, urlopen

import numpy as np
import pandas as pd

from factoryguard.models.forecast import (INPUTS, TARGETS, RUN, ID, TIME, WARM,
    Replay, condition_key, evaluate, fit, issue, load_artifact, load_table,
    replay_frame, validate_frame, write_json)
from factoryguard.monitoring.dashboard import Session, make_server
from factoryguard.pipelines.forecast import fresh


def config():
    return json.loads(Path('configs/forecast_v1.json').read_text())


def frame(run='B02', n=12):
    start = datetime(2021, 10, 25, 9, 0)
    data = {RUN: [run] * n, ID: list(range(1, n+1)),
            TIME: [(start + timedelta(seconds=18*i)).strftime('%d-%b-%Y %H:%M:%S') for i in range(n)],
            WARM: [i < 2 for i in range(n)],
            'quality__any_warning': [False]*n,
            'quality__preceding_gap_gt24s': [False]*n,
            'quality__A_sensor_range_exceeded': [False]*n,
            'quality__C_sensor_range_exceeded': [False]*n,
            'context__T1_c': [30.]*n, 'context__T2_c': [29.]*n}
    for i, col in enumerate(INPUTS):
        data[col] = np.linspace(0.1+i, 1.2+i, n)
    return pd.DataFrame(data)


class ForecastTests(unittest.TestCase):
    def setUp(self):
        self.train = frame(); self.artifact = fit(self.train, config())

    def test_fixed_training_run_and_no_mixed_experiments(self):
        with self.assertRaises(ValueError):
            fit(frame('B01'), config())
        mixed = self.train.copy(); mixed.loc[2, RUN] = 'B01'
        with self.assertRaises(ValueError):
            fit(mixed, config())
        with self.assertRaises(ValueError):
            fit(self.train, dict(config(), alpha=1))

    def test_training_only_scaler_excludes_final_target_and_gap_source(self):
        altered = self.train.copy()
        altered.loc[11, list(INPUTS)] = 1e7
        a = fit(altered, config())
        np.testing.assert_allclose(a['input_mean'], altered.iloc[:-1][list(INPUTS)].mean())
        self.assertNotIn(12, a['training_source_ids'])
        validation = frame('B01'); validation.loc[:, list(INPUTS)] = -1e10
        before = copy.deepcopy(self.artifact)
        replay_frame(validation, self.artifact, 'B01')
        self.assertEqual(self.artifact, before)
        # A gap source must not enter the transform or source support counts.
        gap = self.train.copy()
        gap.loc[6:, TIME] = gap.loc[6:, TIME].map(lambda t: (datetime.strptime(t, '%d-%b-%Y %H:%M:%S') + timedelta(seconds=100)).strftime('%d-%b-%Y %H:%M:%S'))
        a = fit(gap, config())
        self.assertNotIn(6, a['training_source_ids'])
        np.testing.assert_allclose(a['input_mean'], gap.iloc[[0,1,2,3,4,6,7,8,9,10]][list(INPUTS)].mean())

    def test_future_data_independence_full_replay_prefix(self):
        original = frame('B01'); altered = original.copy()
        altered.loc[6:, list(INPUTS)] = 10000
        altered.loc[6:, 'quality__A_sensor_range_exceeded'] = True
        altered.loc[6:, 'context__T1_c'] = 150
        a = replay_frame(original, self.artifact, 'B01')
        b = replay_frame(altered, self.artifact, 'B01')
        self.assertEqual(a[:6], b[:6])
        self.assertEqual(a[5]['issued'], b[5]['issued'])
        self.assertNotEqual(a[6]['resolved']['observed'], b[6]['resolved']['observed'])

    def test_issuance_ignores_commands_ids_flags_and_absolute_clock(self):
        row = self.train.iloc[3].to_dict(); original = issue(row, self.artifact)
        changed = dict(row, context__set_speed_rpm=99999, quality__any_warning=True,
                       provenance__measurement_id=3000, provenance__source_time='25-Oct-2021 22:00:00')
        changed[WARM] = not row[WARM]
        pred = issue(changed, self.artifact)
        self.assertEqual(original['ridge'], pred['ridge'])
        self.assertEqual(original['persistence'], pred['persistence'])

    def test_gap_exact_boundary_and_pending(self):
        table = frame('B01', 4)
        table[TIME] = ['25-Oct-2021 09:00:00','25-Oct-2021 09:00:24','25-Oct-2021 09:00:49','25-Oct-2021 09:01:07']
        ev = replay_frame(table, self.artifact, 'B01'); report = evaluate(ev, 'B01')
        self.assertIsNone(ev[0]['resolved'])
        self.assertEqual(ev[1]['resolved']['status'], 'eligible')
        self.assertEqual(ev[2]['resolved']['status'], 'expired')
        self.assertTrue(ev[2]['acquisition_gap'])
        self.assertEqual(report['eligible'], 2); self.assertEqual(report['expired'], 1)
        self.assertEqual(report['pending'], 1)
        self.assertEqual(ev[-1]['issued']['target_id'], None)

    def test_explicit_clock_expiry_and_no_duplicate_settlement(self):
        replay = Replay(self.artifact, 'B01'); rows = frame('B01').to_dict('records')
        replay.observe(rows[0]); self.assertIsNone(replay.advance_time('2021-10-25 09:00:24'))
        expired = replay.advance_time('2021-10-25 09:00:25')
        self.assertEqual(expired['status'], 'expired')
        self.assertIsNone(replay.advance_time('2021-10-25 09:00:26'))
        event = replay.observe(rows[2])
        self.assertIsNone(event['resolved']); self.assertTrue(event['acquisition_gap'])
        with self.assertRaises(ValueError):
            replay.observe(rows[1])

    def test_replay_rejects_cross_run_and_non_increasing_ids(self):
        r = Replay(self.artifact, 'B01'); row = frame('B01').iloc[0].to_dict()
        r.observe(row)
        with self.assertRaises(ValueError): r.observe(frame('B02').iloc[1].to_dict())
        with self.assertRaises(ValueError): r.observe(row)
        bad = frame('B01'); bad.loc[2, TIME] = bad.loc[1, TIME]
        with self.assertRaises(ValueError): validate_frame(bad, 'B01')

    def test_reload_predictions_and_replay_are_identical(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d)/'model.json'; write_json(p, self.artifact)
            loaded = load_artifact(p)
        self.assertEqual(replay_frame(frame('B01'), loaded, 'B01'), replay_frame(frame('B01'), self.artifact, 'B01'))

    def test_nonfinite_inputs_and_targets_are_reported_not_imputed(self):
        table = frame('B01'); table.loc[1, INPUTS[2]] = np.nan
        table.loc[3, TARGETS[0]] = np.nan
        events = replay_frame(table, self.artifact, 'B01')
        self.assertEqual(events[1]['issued']['ridge'], [None, None])
        self.assertIsNotNone(events[1]['issued']['persistence'][0])
        result = evaluate(events, 'B01')['channels']['A']['all']
        self.assertEqual(result['eligible'], 11)
        self.assertEqual(result['missing_target'], 1)
        self.assertEqual(result['ridge']['unavailable_prediction_n'], 2)
        self.assertLess(result['common_n'], result['persistence']['available_n'])

    def test_metrics_common_pairs_exact_reference_and_zero_baseline(self):
        events = replay_frame(frame('B01'), self.artifact, 'B01')
        result = evaluate(events, 'B01')['channels']['A']['all']
        err = np.array([e['resolved']['observed'][0]-e['resolved']['ridge'][0] for e in events[1:]])
        self.assertAlmostEqual(result['ridge']['mae_v'], np.abs(err).mean())
        self.assertAlmostEqual(result['ridge']['rmse_v'], np.sqrt((err*err).mean()))
        for event in events[1:]: event['resolved']['persistence'] = event['resolved']['observed'][:]
        self.assertIsNone(evaluate(events, 'B01')['channels']['A']['all']['mae_v_skill'])

    def test_quality_retained_and_distinct_thermal_reference(self):
        table = frame('B04'); table.loc[1,'quality__A_sensor_range_exceeded'] = True
        table.loc[1,'context__T1_c'] = 110
        ev = replay_frame(table, self.artifact, 'B04')
        self.assertTrue(ev[1]['issued']['context_interpretation_unresolved'])
        self.assertTrue(ev[1]['temperature_reference_notices'])
        self.assertTrue(ev[1]['issued']['source_quality']['quality__A_sensor_range_exceeded'])
        self.assertEqual(evaluate(ev,'B04')['channels']['A']['strata']['sensor_range_either']['common_n'],2)

    def test_support_preserves_fixed_sparse_unseen_groups(self):
        artifact = copy.deepcopy(self.artifact); row = self.train.iloc[2].to_dict(); key = condition_key(row)
        for n, expected in ((0,'unseen'),(19,'sparse'),(20,'supported')):
            artifact['support_counts'] = {key:n}
            self.assertEqual(issue(row, artifact)['support'], expected)
        row[INPUTS[4]] = 250
        self.assertNotEqual(condition_key(row),key)

    def test_heldout_rejected_before_io_and_frozen_checksum(self):
        with patch('pathlib.Path.open', side_effect=AssertionError('IO forbidden')):
            with self.assertRaises(ValueError): load_table('/never/B03/features.csv','B03')
            with self.assertRaises(ValueError): Replay(self.artifact,'B03')
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'features.csv'; frame('B01').to_csv(p,index=False)
            with self.assertRaisesRegex(ValueError,'checksum'): load_table(p,'B01','wrong')

    def test_output_protection(self):
        with self.assertRaises(ValueError): fresh('/workspace/datasets/paderborn-10868257/raw/B02/new')
        with tempfile.TemporaryDirectory() as d:
            Path(d,'existing').write_text('keep')
            with self.assertRaises(ValueError): fresh(d)

    def test_session_does_not_reveal_future_and_exhaustion_idempotent(self):
        session = Session(self.artifact,'B01',frame('B01',3))
        self.assertEqual(session.state()['events'],[])
        one = session.step(); self.assertEqual(len(one['events']),1)
        self.assertIsNone(one['pending']['target_id'])
        session.step(); final = session.step()
        self.assertTrue(final['exhausted']); self.assertEqual(session.step(),final)

    def test_cli_round_trip_and_frozen_table_ledger(self):
        from factoryguard.pipelines.forecast import run_cli
        import contextlib
        import io
        with tempfile.TemporaryDirectory() as d, contextlib.redirect_stdout(io.StringIO()):
            root=Path(d); cfg=config()
            for run in ('B01','B02','B04'):
                table=root/f'{run}.csv'; frame(run,4).to_csv(table,index=False)
                cfg['tables'][run]=str(table)
            cp=root/'config.json'; write_json(cp,cfg)
            run_cli(['train','--config',str(cp),'--output',str(root/'model')])
            artifact=root/'model/model.json'
            self.assertTrue((root/'model/model.sha256').is_file())
            run_cli(['evaluate','--artifact',str(artifact),'--output',str(root/'evaluation')])
            summary=json.loads((root/'evaluation/summary.json').read_text())
            self.assertEqual(summary['B01']['channels']['A']['all']['common_n'],3)
            run_cli(['replay','--artifact',str(artifact),'--run','B01','--output',str(root/'replay')])
            events=[json.loads(line) for line in (root/'replay/events.jsonl').read_text().splitlines()]
            self.assertEqual(len(events),4)
            self.assertEqual(events[-1]['issued']['status'],'pending')
            self.assertTrue((root/'evaluation/B04.png').is_file())
            # Modifying validation inputs cannot trigger silent re-fitting or reuse.
            with (root/'B01.csv').open('a') as stream: stream.write('\n')
            with self.assertRaisesRegex(ValueError,'checksum'):
                run_cli(['replay','--artifact',str(artifact),'--run','B01','--output',str(root/'changed')])

    def test_http_replay_controls_and_heldout_guard(self):
        tables = {r:frame(r,3) for r in ('B01','B02','B04')}
        server = make_server(self.artifact,0,tables)
        thread=Thread(target=server.serve_forever,daemon=True);thread.start()
        base=f'http://127.0.0.1:{server.server_port}'
        def post(route,data):
            req=Request(base+route,data=json.dumps(data).encode(),headers={'Content-Type':'application/json'})
            with urlopen(req) as response: return json.load(response)
        try:
            with urlopen(base+'/health') as response: self.assertEqual(json.load(response)['B03'],'sealed')
            with urlopen(base) as response: self.assertIn(b'One burst at a time',response.read())
            state=post('/api/reset',{'run':'B01'});self.assertEqual(state['revealed'],0)
            one=post('/api/step',{'session':state['session']});self.assertEqual(one['revealed'],1)
            two=post('/api/step',{'session':state['session']});self.assertEqual(two['revealed'],2)
            self.assertEqual(two['events'][0],one['events'][0])
            with self.assertRaises(HTTPError): post('/api/reset',{'run':'B03'})
            reset=post('/api/reset',{'run':'B04','session':state['session']})
            self.assertEqual(reset['events'],[])
            with self.assertRaises(HTTPError): post('/api/step',{'session':state['session']})
        finally:
            server.shutdown();server.server_close();thread.join()


if __name__=='__main__': unittest.main()
