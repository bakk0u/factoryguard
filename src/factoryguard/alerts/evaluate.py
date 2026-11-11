"""One frozen policy, chronological development blocks; no fault-accuracy claims."""
from collections import Counter
from copy import deepcopy
from hashlib import sha256
import argparse
import json
from pathlib import Path

from .engine import AlertEngine, ENGINE_SHA256, ROOT, load_policy, replay
from .journal import AlertJournal


def load_snapshot(root=ROOT):
    root = Path(root)
    manifest = json.loads((root/'site/source-manifest.json').read_text())
    data = (root/'site/source/replay.json').read_bytes()
    if sha256(data).hexdigest() != manifest['files']['replay.json']:
        raise ValueError('Pinned replay integrity mismatch')
    payload = json.loads(data)
    if set(payload['states']) != {'B01', 'B02', 'B04'}:
        raise ValueError('Only permitted pinned development/diagnostic states')
    return payload, manifest['files']['replay.json']


def dashboard_bundle(payload, policy=None, journal=None, snapshot=None):
    policy = policy or load_policy()
    if set(payload['states']) != {'B01', 'B02', 'B04'}:
        raise ValueError('Unexpected experiment in alert snapshot')
    result = {'version': policy.config['version'], 'policy_sha256': policy.sha256,
              'engine_sha256': ENGINE_SHA256, 'protocol': (ROOT/'docs/investigation_alert_protocol.md').read_text(), 'runs': {}}
    for run in ('B01', 'B02', 'B04'):
        result['runs'][run] = {}
        for channel in ('A', 'C'):
            stream = replay(payload['states'][run]['events'], run, channel, policy)
            if journal is not None: journal.append(stream, snapshot)
            # One timeline plus one immutable episode/transition ledger: no O(N²) history copies.
            frames = [{k:v for k,v in frame.items() if k not in ('episode', 'transitions', 'notifications', 'run', 'channel', 'policy_version', 'policy_sha256', 'engine_sha256')}
                      for frame in stream['frames']]
            result['runs'][run][channel] = {'stream': stream['stream'], 'frames': frames,
                'episodes': stream['episodes'], 'transitions': stream['transitions'],
                'notifications': stream['notifications']}
    return result


def metrics(engine):
    frames = engine.frames
    availability = Counter(f['availability'] for f in frames)
    durations = []
    for episode in engine.episodes:
        active = [f for f in frames if f['episode_id'] == episode['id'] and f['state'] == 'Active alert']
        clear = next((t for t in engine.transitions if t['episode_id'] == episode['id'] and t['to'] == 'Cleared'), None)
        durations.append({'episode_id': episode['id'], 'activation_position': episode['position'],
            'active_observations': len(active), 'clearance_position': clear['position'] if clear else None,
            'unresolved_at_block_end': clear is None})
    first_active = next((f for f in frames if f['episode']), None)
    first_unavailable = next((f for f in frames if f['availability'] == 'unavailable'), None)
    return {'observations': len(frames), 'availability': dict(availability),
        'coverage_fraction': (availability['available']+availability['limited'])/len(frames) if frames else None,
        'signal_eligible_observations': {s: sum(f['signals'][s]['eligible'] for f in frames) for s in ('residual','level','context')},
        'limitation_counts': dict(Counter(r for f in frames for r in f['reasons'])),
        'watches': sum(t['to'] == 'Watch' for t in engine.transitions),
        'activations': len(engine.episodes), 'clearances': sum(d['clearance_position'] is not None for d in durations),
        'activations_per_100_observations': 100*len(engine.episodes)/len(frames) if frames else None,
        'active_observations': sum(d['active_observations'] for d in durations), 'episodes': durations,
        'first_activation_example': first_active, 'first_unavailable_example': first_unavailable,
        'fault_event_metrics': {'false_alarms': None, 'missed_faults': None, 'precision': None, 'recall': None,
            'detection_delay': None, 'reason': 'No credible normal/fault event intervals/times; unlabelled is not normal.'}}


def evaluate(output, root=ROOT):
    from factoryguard.util import protect_output
    out = Path(protect_output(output, ROOT/'site/source', ROOT/'data', ROOT/'configs', ROOT/'src', ROOT/'docs'))
    if out.exists() and any(out.iterdir()): raise ValueError('Use a fresh alert evaluation output')
    out.mkdir(parents=True, exist_ok=True)
    policy = load_policy(root)
    freeze = json.loads((Path(root)/'configs/investigation_alerts_v1.freeze.json').read_text())
    # Persist the exact freeze/config before computing or displaying results.
    (out/'freeze.json').write_text(json.dumps(freeze, indent=2)+'\n')
    (out/'configuration.json').write_text(json.dumps(policy.config, indent=2)+'\n')
    payload, snapshot = load_snapshot(root)
    results = []
    for run, split in policy.config['splits'].items():
        events = payload['states'][run]['events']
        if len(events) != split['total']: raise ValueError('Frozen observation inventory changed')
        for channel in ('A','C'):
            training = AlertEngine(run, channel, policy)
            for e in events[:split['calibration_stop']]: training.process(e)
            for name, start, stop in [('validation', split['calibration_stop']+1, split['validation_stop']),
                                      ('reserved_policy_evaluation', split['validation_stop']+1, split['total'])]:
                engine = AlertEngine(run, channel, policy, calibration=training.calibration, start_position=start)
                for pos in range(start, stop+1): engine.process(events[pos-1], pos)
                results.append({'run': run, 'channel': channel, 'block': name, 'start': start, 'stop': stop,
                    'calibration': deepcopy(training.calibration), 'metrics': metrics(engine)})
                (out/f'{run}-{channel}-{name}.json').write_text(json.dumps(engine.export(), indent=2, allow_nan=False)+'\n')
    report = {'version': policy.config['version'], 'policy_sha256': policy.sha256, 'freeze': freeze, 'snapshot': snapshot,
        'candidates': 1, 'outcome_tuning': False, 'results': results,
        'limitations': ['Investigation alerts, not confirmed faults.', 'Only B01/B02 historically inspected development bearings.',
            'Saved forecast method/settings were already selected on development results; not unbiased held-out performance.',
            'Calibration quantiles are not guaranteed false-alarm rates.', 'Duration is in observed bursts, not operating hours.',
            'No B03 access or reserve-plan changes; B04 remains unavailable diagnostic context.']}
    (out/'evaluation.json').write_text(json.dumps(report, indent=2, allow_nan=False)+'\n')
    return report


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', required=True)
    args = parser.parse_args()
    report = evaluate(args.output)
    print(json.dumps({'policy': report['version'], 'blocks': len(report['results']),
        'results': [{k:r[k] for k in ('run','channel','block')}|{k:r['metrics'][k] for k in ('observations','activations','clearances','coverage_fraction')} for r in report['results']]} ,indent=2))
