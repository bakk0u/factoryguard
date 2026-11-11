"""Synthetic behavior contracts, not measured fault-detection performance."""
from copy import deepcopy
import json
import math
from pathlib import Path
import sqlite3
import tempfile
import unittest

from factoryguard.alerts.engine import AlertEngine, Policy, fingerprint, load_policy, replay
from factoryguard.alerts.journal import AlertJournal, LocalNotifications
from factoryguard.alerts.evaluate import metrics
from factoryguard.models.forecast import RUN, WARM


def policy():
    c = load_policy().config
    c['splits'] = {r: {'total': 100, 'calibration_stop': 30, 'validation_stop': 60} for r in ('B01','B02')}
    return Policy(c)


def calibration(p, channel='A', residual=1., level=1., reference=True):
    body = {'policy_sha256': p.sha256, 'run': 'B01', 'channel': channel,
        'prefix_stop': 30, 'input_sha256': 'a'*64, 'counts': {'residual': 30, 'level': 25},
        'activation_v': {'residual': residual, 'level': level},
        'bins': {'1000|2500|500|loaded': {'n': 30, 'median_v': 1., 'iqr_v': 1.}} if reference else {},
        'meaning': 'synthetic calibration fixture, not healthy'}
    return {**body, 'sha256': fingerprint(body)}


def event(a=1., forecast=1., *, c=1., c_forecast=1., interval=12., warmup=False, run='B01', speed=1100., range_a=False):
    return {'rms_v': [a,c], 'interval_s': interval,
        'resolved': {'status': 'scored', 'forecast_v': [forecast,c_forecast]},
        'observation': {RUN: run, WARM: warmup, 'quality__A_sensor_range_exceeded': range_a,
            'quality__C_sensor_range_exceeded': False, 'context__measured_speed_rpm': speed,
            'context__measured_static_load_n': 2600., 'context__measured_dynamic_peak_n': 600.}}


def ready(**kw):
    p = policy()
    return AlertEngine('B01','A',p,calibration=calibration(p,**kw),start_position=31)


def activate(engine):
    engine.process(event())
    for _ in range(3): engine.process(event(forecast=-1.))
    assert engine.state == 'Active alert'


class AlertTests(unittest.TestCase):
    def test_zero_variance_and_missing_quality_metadata_withhold_monitoring(self):
        for field,value in [('quality__A_zero_variance',True),(WARM,None),('quality__A_sensor_range_exceeded',None)]:
            e=ready();activate(e);row=event();row['observation'][field]=value
            frame=e.process(row)
            self.assertEqual(frame['availability'],'unavailable');self.assertEqual(frame['state'],'Active alert')
        e=ready();activate(e);row=event();row['rms_v']=None
        self.assertEqual(e.process(row)['state'],'Active alert')
        row=event();row['resolved']['forecast_v']=None
        self.assertFalse(e.process(row)['signals']['residual']['eligible'])
        p=policy();c=AlertEngine('B01','C',p,calibration=calibration(p,channel='C'),start_position=31)
        row=event();row['rms_v']=[1.]
        self.assertEqual(c.process(row)['availability'],'unavailable')

    def test_isolated_spike_watch_without_activation_and_quiet_dismissal(self):
        e = ready(level=10.)
        e.process(event()); e.process(event(a=3.))
        self.assertEqual(e.state, 'Watch')
        for _ in range(3): e.process(event())
        self.assertEqual(e.state, 'No active alert')
        self.assertEqual(e.episodes, [])

    def test_sustained_level_can_activate_when_residual_is_small(self):
        e = ready(residual=1.,level=.5,reference=False)
        for x in [1.]*3+[2.]*9: e.process(event(a=x,forecast=x))
        self.assertEqual(e.state, 'Active alert')
        self.assertEqual(e.initiating, ['level'])
        self.assertEqual(e.frames[-1]['availability'], 'limited')
        self.assertEqual(e.frames[-1]['signals']['residual']['value_v'], 0.)

    def test_overlapping_level_windows_can_echo_one_extreme_sample_without_independent_confirmation(self):
        e=ready(residual=1.,level=.5,reference=False)
        for x in [1.]*6+[10.]+[1.]*3:e.process(event(a=x,forecast=1.))
        self.assertEqual(e.episodes[0]['initiating_signals'],['level'])
        self.assertEqual(sum(f['signals']['residual']['ratio'] is not None and f['signals']['residual']['ratio']>=1 for f in e.frames),1)
        self.assertEqual(len(e.episodes),1,'an investigation episode is not proof of three independent unusual readings')

    def test_gradual_drift_accumulates_against_segment_anchor(self):
        e = ready(level=.2,reference=False)
        for i in range(20):
            x = 1+i*.05; e.process(event(a=x,forecast=x))
        self.assertEqual(e.state, 'Active alert')
        self.assertEqual(e.initiating, ['level'])
        self.assertGreater(e.frames[-1]['signals']['level']['value_v'], .2)

    def test_context_support_and_context_change_are_explicit_not_votes(self):
        e = ready(residual=None,level=None)
        for _ in range(3): e.process(event(a=5.,forecast=5.))
        self.assertEqual(e.state, 'Active alert'); self.assertEqual(e.initiating,['context'])
        self.assertEqual(e.frames[-1]['signals']['context']['reference_n'],30)
        frame = e.process(event(a=5.,speed=2000.,forecast=5.))
        self.assertFalse(frame['signals']['context']['eligible'])
        self.assertEqual(frame['state'], 'Active alert')
        self.assertEqual(frame['availability'],'unavailable')
        self.assertIn('level_operating_context_confounded', frame['reasons'])

    def test_missing_gap_and_warmup_do_not_clear_active_condition(self):
        for bad in [event(a=None,forecast=None),event(interval=25.),event(warmup=True),event(range_a=True),event(interval=None)]:
            e=ready();activate(e);frame=e.process(bad)
            self.assertEqual(e.state,'Active alert');self.assertEqual(frame['quiet_streak'],0)
            self.assertEqual([t['reason'] for t in frame['transitions']],['history_reset'])
            self.assertEqual(len(e.episodes),1)
            self.assertEqual(len(e.notifications),1)
        e=ready();activate(e);e.process(event(a=None,interval=40.))
        self.assertEqual(len(e.frames[-1]['transitions']),1,'combined gap/missing reset is one immutable transition')

    def test_exact_gap_boundary_and_unknown_interval_history_gate(self):
        e=ready();e.process(event());frame=e.process(event(interval=24.))
        self.assertTrue(frame['signals']['residual']['eligible'])
        frame=e.process(event(interval=24.001))
        self.assertFalse(frame['signals']['residual']['eligible'])
        self.assertFalse(frame['signals']['level']['eligible'])

    def test_hysteresis_oscillation_and_persistence_by_same_signal(self):
        e=ready(level=10.,reference=False);e.process(event())
        for ratio in [1.1,.9]*5:e.process(event(forecast=1-ratio))
        self.assertEqual(e.state,'Watch');self.assertEqual(e.episodes,[])
        for _ in range(3):e.process(event(forecast=.5))
        self.assertEqual(e.state,'No active alert')
        activate(e)
        for _ in range(6):e.process(event(forecast=.3)) # ratio .7, above clearing threshold
        self.assertEqual(e.state,'Active alert')
        for _ in range(3):e.process(event())
        self.assertEqual(e.state,'Cleared')
        self.assertEqual([n['kind'] for n in e.notifications],['activation','clearance'])

    def test_activation_signals_are_not_independent_confirmation(self):
        e=ready(level=10.,reference=True);e.process(event())
        # Alternating residual and context crossings cannot combine into a streak.
        for _ in range(4):
            e.process(event(a=1.,forecast=-1.));e.process(event(a=5.,forecast=5.))
        self.assertEqual(e.episodes,[])

    def test_training_prefix_only_and_future_change_independence(self):
        p=policy();rows=[event(1+math.sin(i)*.01,forecast=1) for i in range(100)]
        before=replay(rows,'B01','A',p)
        changed=deepcopy(rows)
        for r in changed[75:]:r['rms_v'][0]=1000.;r['resolved']['forecast_v'][0]=-900.
        after=replay(changed,'B01','A',p)
        self.assertEqual(before['frames'][:75],after['frames'][:75])
        self.assertEqual(before['calibration'],after['calibration'])
        self.assertTrue(all(f['availability']=='unavailable' for f in before['frames'][:30]))
        self.assertTrue(all(f['signals']['residual']['activation_v'] is None for f in before['frames'][:30]))
        self.assertFalse(before['frames'][30]['signals']['residual']['eligible'],'boundary residual purged')
        self.assertEqual(before['calibration']['prefix_stop'],30)

    def test_other_channel_and_embedded_full_run_references_cannot_change_alerts(self):
        p=policy();rows=[event() for _ in range(100)];before=replay(rows,'B01','A',p)
        changed=deepcopy(rows)
        for row in changed:
            row['rms_v'][1]=9999.;row['resolved']['forecast_v'][1]=-9999.
            row['observation']['quality__C_sensor_range_exceeded']=True
            row['context_reference']={'n':100000,'measures':{'future':999}}
            row['level_change_from_segment_first3_v']=[999,999]
        self.assertEqual(before,replay(changed,'B01','A',p))

    def test_block_reset_scope_validation_and_unavailable_calibration(self):
        p=policy();self.assertRaises(ValueError,AlertEngine,'B03','A',p)
        self.assertRaises(ValueError,AlertEngine,'B01','C',p,calibration=calibration(p),start_position=31)
        self.assertRaises(ValueError,AlertEngine,'B01','A',p,calibration=calibration(p),start_position=10)
        e=ready();self.assertRaises(ValueError,e.process,event(run='B02'))
        e.process(event());self.assertRaises(ValueError,e.process,event(),31)
        e=AlertEngine('B04','A',p)
        self.assertEqual(e.process(event(run='B04'))['availability'],'unavailable')
        rows=[event(warmup=True) for _ in range(30)]+[event() for _ in range(10)]
        report=replay(rows,'B01','A',p)
        self.assertIsNone(report['calibration']['activation_v']['residual'])
        self.assertTrue(all(not f['signals']['residual']['eligible'] for f in report['frames']))

    def test_missing_initiating_signal_blocks_clearance_even_when_other_signal_quiet(self):
        e=ready(residual=None,level=None);[e.process(event(a=5.)) for _ in range(3)]
        self.assertEqual(e.initiating,['context'])
        for _ in range(5):e.process(event(speed=9000.))
        self.assertEqual(e.state,'Active alert')

    def test_journal_restart_acknowledgment_immutability_notifications_and_export(self):
        with tempfile.TemporaryDirectory() as tmp:
            path=Path(tmp)/'alerts.sqlite';journal=AlertJournal(path);adapter=LocalNotifications()
            e=ready();activate(e);original=e.export();stream=journal.append(original,'a'*64)
            journal.deliver(stream,e.position,adapter);journal.deliver(stream,e.position,adapter)
            self.assertEqual(len(adapter.events),1)
            ack=journal.acknowledge(stream,e.episode_id,e.position)
            self.assertEqual(e.state,'Active alert');self.assertEqual(original,e.export())
            self.assertEqual(ack,journal.acknowledge(stream,e.episode_id,e.position))
            journal=AlertJournal(path);journal.append(original,'a'*64)
            exported=journal.export(stream,e.position)
            self.assertEqual(exported['episodes'],original['episodes']);self.assertEqual(len(exported['acknowledgments']),1)
            self.assertEqual(journal.export(stream,30)['episodes'],[])
            self.assertEqual(journal.export(stream,30)['acknowledgments'],[])
            with journal.connect() as con:
                with self.assertRaises(sqlite3.IntegrityError):con.execute('UPDATE episodes SET position=1')
                with self.assertRaises(sqlite3.IntegrityError):con.execute('DELETE FROM transitions')
            changed=deepcopy(original);changed['frames'][0]['state']='Cleared'
            with self.assertRaises(ValueError):journal.append(changed,'a'*64)
            self.assertRaises(ValueError,journal.acknowledge,stream.replace(':A:',':C:'),e.episode_id,e.position)
            for _ in range(3):e.process(event())
            journal.append(e.export(),'a'*64);journal.deliver(stream,e.position,adapter)
            self.assertEqual(len(adapter.events),2)
            self.assertEqual(len(e.episodes),1)
            for _ in range(3):e.process(event(forecast=-1.))
            self.assertEqual(len(e.episodes),2);self.assertNotEqual(e.episodes[0]['id'],e.episodes[1]['id'])

    def test_deterministic_replay_and_duration_in_observations(self):
        rows=[event() for _ in range(30)]+[event(a=3.) for _ in range(15)]
        first=replay(rows,'B01','A',policy());second=replay(deepcopy(rows),'B01','A',policy())
        self.assertEqual(first,second)
        e=ready();activate(e);m=metrics(e)
        self.assertEqual(m['active_observations'],1)
        self.assertIsNone(m['fault_event_metrics']['false_alarms'])

    def test_configuration_and_freeze_fail_closed(self):
        p=policy();bad=p.config;bad['clear_fraction']=1.
        self.assertRaises(ValueError,Policy,bad)
        self.assertLess(p.config['clear_fraction'],1.,'configuration copies cannot mutate the frozen policy')
        bad=p.config.copy();bad['gap_limit_csv_s']=float('inf')
        self.assertRaises(ValueError,Policy,bad)

    def test_existing_store_persists_separate_journal_and_cursor_reset_hides_future(self):
        from test_release_modeling import data
        from test_release_application import artifact
        from factoryguard.models.forecast import INPUTS
        from factoryguard.release.store import Store
        from unittest.mock import patch
        with tempfile.TemporaryDirectory() as tmp:
            frame=data(n=70)
            frame[list(INPUTS[:2])]=1.
            frame.loc[31:,list(INPUTS[:2])]=3.
            frame['quality__A_sensor_range_exceeded']=False;frame['quality__C_sensor_range_exceeded']=False
            store=Store(Path(tmp)/'replay.sqlite');store.initialize({'B01':frame},{'runs':['B01']})
            for _ in range(50):store.step('B01',artifact(),{})
            original=deepcopy(store.state('B01')['events'])
            with patch('factoryguard.alerts.engine_v2.load_policy',return_value=__import__('test_alerts_v2').policy()):
                result=store.alerts('B01','A');self.assertTrue(result['episodes'])
                episode=result['episodes'][0]['id']
                acknowledged=store.alerts('B01','A',acknowledge=episode)
                self.assertEqual(len(acknowledged['acknowledgments']),1)
                self.assertEqual(result['frames'],acknowledged['frames'])
                self.assertEqual(store.state('B01')['events'],original)
                self.assertEqual(Store(store.path).alerts('B01','A')['acknowledgments'],acknowledged['acknowledgments'])
                with self.assertRaises(ValueError):store.alerts('B01','A',51)
                with self.assertRaises(ValueError):store.alerts('B01','C',acknowledge=episode)
                store.reset('B01');hidden=store.alerts('B01','A')
                self.assertEqual(hidden['episodes'],[]);self.assertEqual(hidden['acknowledgments'],[])
                with AlertJournal(Path(tmp)/'alerts.sqlite').connect() as con:
                    self.assertGreater(con.execute('SELECT count(*) FROM episodes').fetchone()[0],0)
