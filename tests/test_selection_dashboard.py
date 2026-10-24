"""Selected replay presentation must retain causal issue/settlement boundaries."""
import copy
import json
from pathlib import Path
import tempfile
import unittest

from factoryguard.monitoring.selection_dashboard import events_from_ledger, build, export


def records(run='B01'):
    rows=[]
    for i in range(4):
        row={'provenance__experiment':run,'provenance__source_time':f'19-Oct-2021 09:00:{18*i:02d}',
             'quality__documented_warmup_setpoints':False,'quality__A_sensor_range_exceeded':i==2,
             'context__T1_c':111 if i==2 else 30,'context__T2_c':29}
        rows.append({'run':run,'source_id':i+1,'observation':row,'training_bin_count':20,
            'history_ready':i>=2,'common_pair':i==2,'common_exclusion':'pending_block_end' if i==3 else 'common' if i==2 else 'insufficient_history',
            'target_interval_s':18 if i<3 else None,'observed_target':[i+2,i+3] if i<3 else [None,None],
            'forecasts':{'smoothing':[i+1,i+2],'persistence':[i+1.1,i+2.1]}})
    return rows


class SelectionDashboardTests(unittest.TestCase):
    def test_issue_does_not_reveal_future_target_or_eligibility(self):
        original=records();changed=copy.deepcopy(original)
        changed[0]['observed_target']=[999,999];changed[0]['target_interval_s']=100
        changed[0]['common_pair']=True;changed[0]['common_exclusion']='expired_gap'
        a=events_from_ledger(original,'smoothing');b=events_from_ledger(changed,'smoothing')
        self.assertEqual(a[0],b[0]);self.assertIsNone(a[0]['issued']['target_id'])
        self.assertNotEqual(a[1]['resolved'],b[1]['resolved'])
        self.assertTrue(b[1]['acquisition_gap'])
        self.assertTrue(a[2]['temperature_reference_notices'])
        self.assertTrue(a[2]['issued']['source_quality']['quality__A_sensor_range_exceeded'])
        self.assertTrue(a[3]['resolved']['comparison_common'])

    def test_mixed_and_heldout_replays_rejected(self):
        with self.assertRaises(ValueError):events_from_ledger(records('B03'),'smoothing')
        with self.assertRaises(ValueError):events_from_ledger(records('B01')+records('B02'),'smoothing')

    def test_export_has_selected_labels_and_no_network_or_overwrite(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d);(root/'selection.json').write_text(json.dumps({'selected_group':'smoothing'}))
            for run,train in [('B01','B02'),('B02','B01'),('B04','B02')]:
                path=root/(f'{run}_outer_forecasts.jsonl' if run!='B04' else 'B04_from_B02_forecasts.jsonl')
                path.write_text('\n'.join(json.dumps(r) for r in records(run)))
                (root/f'{train}_inner_choices.json').write_text(json.dumps({'smoothing':{'params':{'alpha':.2 if train=='B02' else .5}}}))
            html,replays=build(root)
            self.assertNotIn('await fetch(',html)
            self.assertIn('r.comparison_common',html)
            self.assertIn('Exponential smoothing: current-observation weight',html)
            self.assertNotIn('B02 · Training-run replay',html)
            self.assertEqual(set(replays),{'B01','B02','B04'})
            out=root/'dashboard.html';export(root,out)
            with self.assertRaises(FileExistsError):export(root,out)
