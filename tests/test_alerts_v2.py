"""Frozen v2 synthetic behavior; these are not fault-performance measurements."""
from copy import deepcopy
import json
import math
from pathlib import Path
import sqlite3
import tempfile
import unittest

from factoryguard.alerts.engine_v2 import AlertEngine, Policy, load_policy, replay
from factoryguard.alerts.engine import replay as replay_v1
from factoryguard.alerts.journal import AlertJournal, LocalNotifications
from test_alerts import event, calibration, policy as policy_v1


def policy():
    c = load_policy().config
    c['splits'] = policy_v1().config['splits']
    return Policy(c)


def ready(**kw):
    p = policy()
    return AlertEngine('B01', 'A', p, calibration=calibration(p, **kw), start_position=31)


def disjoint(test, groups):
    test.assertTrue(all(max(a) < min(b) for a, b in zip(groups, groups[1:])), groups)


class AlertV2Tests(unittest.TestCase):
    def test_v2_freeze_is_complete_and_tampering_fails_closed(self):
        from factoryguard.alerts.engine_v2 import ROOT
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp); (root/'configs').mkdir(); (root/'docs').mkdir()
            for name in ['configs/investigation_alerts_v2.json','configs/investigation_alerts_v2.freeze.json','docs/investigation_alert_protocol_v2.md']:
                (root/name).write_bytes((ROOT/name).read_bytes())
            self.assertEqual(load_policy(root).sha256,load_policy().sha256)
            f=root/'configs/investigation_alerts_v2.freeze.json'; x=json.loads(f.read_text()); x['files'].pop('docs/investigation_alert_protocol_v2.md'); f.write_text(json.dumps(x))
            with self.assertRaisesRegex(ValueError,'Incomplete frozen'): load_policy(root)
            f.write_bytes((ROOT/'configs/investigation_alerts_v2.freeze.json').read_bytes())
            c=root/'configs/investigation_alerts_v2.json'; c.write_text(c.read_text().replace('0.99','0.98'))
            with self.assertRaisesRegex(ValueError,'Frozen alert policy changed'): load_policy(root)

    def test_isolated_extreme_has_one_level_confirmation_and_no_episode(self):
        e = ready(level=.5, reference=False)
        for x in [1.]*6+[10.]+[1.]*15:
            e.process(event(a=x))
        highs = [f for f in e.frames if f['signals']['level']['ratio'] is not None and f['signals']['level']['ratio'] >= 1]
        self.assertEqual(len(highs), 3)
        self.assertEqual(sum(f['signals']['level']['fresh_high_confirmation'] for f in highs), 1)
        self.assertEqual(e.episodes, [])
        self.assertEqual(sum(f['signals']['residual']['fresh_high_confirmation'] for f in e.frames), 1)

    def test_sustained_step_and_ramp_activate_with_disjoint_support(self):
        for rows in [[1.]*6+[2.]*20, [1+i*.1 for i in range(28)]]:
            e = ready(level=.5, reference=False)
            for x in rows: e.process(event(a=x, forecast=x))
            self.assertEqual(e.state, 'Active alert')
            episode = e.episodes[0]
            self.assertEqual(episode['initiating_signals'], ['level'])
            groups = episode['evidence']['level']['confirmation_support']
            self.assertEqual(len(groups), 3); disjoint(self, groups)
            self.assertEqual(len({p for g in groups for p in g}), 9)
            self.assertTrue(all(max(g) <= episode['position'] for g in groups))

    def test_abrupt_residual_path_still_uses_three_fresh_readings(self):
        e = ready(level=10., reference=False); e.process(event())
        for _ in range(3): e.process(event(a=3.))
        self.assertEqual(e.state, 'Active alert')
        self.assertEqual(e.initiating, ['residual'])
        groups = e.episodes[0]['evidence']['residual']['confirmation_support']
        self.assertEqual(groups, [[32], [33], [34]])
        self.assertEqual(e.frames[-1]['assessment'], 'supported')

    def test_each_signal_has_specific_eligibility_without_reference_fallback(self):
        e = ready(reference=False)
        for _ in range(8): frame = e.process(event())
        self.assertEqual(frame['availability'], 'limited')
        self.assertTrue(frame['signals']['residual']['eligible'])
        self.assertTrue(frame['signals']['level']['eligible'])
        self.assertEqual(frame['signals']['context']['reasons'], ['reference_unsupported'])
        e = ready()
        for _ in range(8): frame = e.process(event())
        self.assertEqual(frame['availability'], 'available')
        frame = e.process(event(speed=9000.))
        self.assertEqual(frame['availability'], 'limited')
        self.assertIn('operating_context_confounded', frame['signals']['level']['qualifications'])
        row = event(); row['observation'].pop('context__measured_speed_rpm')
        frame = e.process(row)
        self.assertEqual(frame['signals']['context']['reasons'], ['operating_context_missing'])
        self.assertTrue(frame['signals']['residual']['eligible'])
        frame = e.process(event(warmup=True))
        self.assertEqual(frame['availability'], 'unavailable')
        self.assertTrue(all('warmup' in s['reasons'] for s in frame['signals'].values()))

    def test_unresolved_unavailable_and_hysteresis_do_not_clear(self):
        e = ready(residual=None, level=None)
        for _ in range(3): e.process(event(a=5., forecast=5.))
        self.assertEqual(e.state, 'Active alert')
        for _ in range(6): frame = e.process(event(speed=9000.))
        self.assertEqual(frame['assessment'], 'unresolved_unavailable')
        self.assertEqual(frame['quiet_streak'], 0)
        for _ in range(3): e.process(event())
        self.assertEqual(e.state, 'Cleared')
        self.assertEqual([n['kind'] for n in e.notifications], ['activation', 'clearance'])
        e = ready(level=10., reference=False); e.process(event())
        for _ in range(3): e.process(event(forecast=-1.))
        for _ in range(10): frame = e.process(event(forecast=.3))
        self.assertEqual(frame['assessment'], 'unresolved_hysteresis')
        self.assertEqual(e.state, 'Active alert')

    def test_fresh_recovery_and_resets_preserve_unresolved_episode(self):
        e = ready(level=.5, reference=False)
        for x in [1.]*6+[2.]*20: e.process(event(a=x, forecast=x))
        ep = e.episode_id
        for bad in [event(a=None), event(interval=25.), event(warmup=True)]:
            frame = e.process(bad)
            self.assertEqual(frame['state'], 'Active alert')
            self.assertEqual(frame['quiet_streak'], 0)
            self.assertEqual(frame['assessment'], 'unresolved_unavailable')
        # Reconstruct sufficient fixed-anchor history; clearance needs disjoint windows.
        for _ in range(6): e.process(event())
        self.assertNotEqual(e.state, 'Cleared')
        for _ in range(6): e.process(event())
        self.assertEqual(e.state, 'Cleared')
        clear = next(t for t in e.transitions if t['to'] == 'Cleared')
        disjoint(self, clear['evidence']['recovery_support']['level'])
        self.assertEqual(len(clear['evidence']['recovery_support']['level']), 3)
        self.assertEqual(e.episode_id, ep)
        self.assertEqual(len(e.notifications), 2)

    def test_escalation_records_new_evidence_without_duplicate_activation(self):
        e = ready(level=.5, reference=False); e.process(event())
        for _ in range(3): e.process(event(forecast=-1.))
        original = deepcopy(e.episodes[0])
        for _ in range(20): e.process(event(a=2., forecast=2.))
        escalations = [t for t in e.transitions if t['reason'] == 'additional_persistent_signal']
        self.assertEqual(len(escalations), 1)
        self.assertIn('level', e.initiating)
        self.assertEqual(e.episodes[0], original)
        self.assertEqual(len(e.notifications), 1)

    def test_active_level_cannot_reanchor_away_a_sustained_change_after_gap(self):
        e = ready(level=.5, reference=False)
        for x in [1.]*6+[2.]*20: e.process(event(a=x, forecast=x))
        self.assertEqual(e.state, 'Active alert')
        original = deepcopy(e.episodes[0])
        e.process(event(a=2., forecast=2., interval=25.))
        for _ in range(20): frame = e.process(event(a=2., forecast=2.))
        self.assertEqual(e.state, 'Active alert', 'reset cannot redefine a sustained active level as recovered')
        self.assertEqual(frame['signals']['level']['anchor_mean_v'], 1.)
        self.assertEqual(e.episodes[0], original)
        for _ in range(12): e.process(event())
        self.assertEqual(e.state, 'Cleared')

    def test_oscillation_and_alternating_signals_are_not_persistent(self):
        e = ready(level=10., reference=False); e.process(event())
        for ratio in [1.1, .9]*8: e.process(event(forecast=1-ratio))
        self.assertEqual(e.episodes, [])
        for _ in range(12): e.process(event())
        self.assertEqual(e.state, 'No active alert')

    def test_causal_channel_isolated_replay_and_unchanged_v1_calibration(self):
        p = policy(); rows = [event(1+math.sin(i)*.01) for i in range(100)]
        before = replay(rows, 'B01', 'A', p)
        changed = deepcopy(rows)
        for row in changed[75:]: row['rms_v'][0] = 9000.
        self.assertEqual(before['frames'][:75], replay(changed, 'B01', 'A', p)['frames'][:75])
        changed = deepcopy(rows)
        for row in changed:
            row['rms_v'][1] = 9000.; row['observation']['quality__C_sensor_range_exceeded'] = True
        self.assertEqual(before, replay(changed, 'B01', 'A', p))
        self.assertEqual(before, replay(deepcopy(rows), 'B01', 'A', p))
        v1 = replay_v1(rows, 'B01', 'A', policy_v1())
        for key in ['activation_v', 'counts', 'bins', 'input_sha256']:
            self.assertEqual(before['calibration'][key], v1['calibration'][key])
        self.assertTrue(all(f['signals']['residual']['activation_v'] is None for f in before['frames'][:30]))

    def test_journal_acknowledgment_export_and_delivery_are_append_only(self):
        e = ready(level=10., reference=False); e.process(event())
        for _ in range(3): e.process(event(forecast=-1.))
        with tempfile.TemporaryDirectory() as tmp:
            journal = AlertJournal(Path(tmp)/'alerts.sqlite'); adapter = LocalNotifications()
            original = e.export(); stream = journal.append(original, 'a'*64)
            journal.acknowledge(stream, e.episode_id, e.position)
            journal.deliver(stream, e.position, adapter); journal.deliver(stream, e.position, adapter)
            self.assertEqual(len(adapter.events), 1); self.assertEqual(original, e.export())
            self.assertEqual(journal.export(stream, e.position)['frames'], original['frames'])
            self.assertEqual(journal.export(stream, 30)['episodes'], [])
            with journal.connect() as con:
                with self.assertRaises(sqlite3.IntegrityError): con.execute('DELETE FROM transitions')
            for _ in range(3): e.process(event())
            journal.append(e.export(), 'a'*64); journal.deliver(stream, e.position, adapter)
            self.assertEqual(len(adapter.events), 2)
            self.assertEqual(len(journal.export(stream, e.position)['acknowledgments']), 1)
