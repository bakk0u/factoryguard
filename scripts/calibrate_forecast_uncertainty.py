"""Select a causal interval calibrator on B01/B02, then apply it frozen elsewhere.

    # development: reciprocal B01<->B02 selection, writes the frozen choice
    python scripts/calibrate_forecast_uncertainty.py select --features DIR --output docs/results/uncertainty-calibration-v1
    # diagnostic / independent application of the frozen choice (no selection, no tuning)
    python scripts/calibrate_forecast_uncertainty.py apply --pairs PAIRS.csv --label B04 --output ...

Pre-declared selection rule (written before any result existed):
  * forecasts are the frozen release method (exponential smoothing, alpha 0.5) on the common mask;
  * each candidate is run on B01 warm-started only with B02's errors, and on B02 warm-started
    only with B01's errors, channels A and C separately (four cells);
  * primary criterion: smallest mean absolute gap between coverage and the 90% target over the
    four cells; candidates within 0.01 of the best are tied;
  * tie-break 1: smallest mean interval (Winkler) score relative to the fixed-transfer baseline;
  * tie-break 2: the simpler candidate (no adaptive step before adaptive, larger window first).
B03 never enters selection. B04 is diagnostic only (unresolved speed/load scaling).
"""
from __future__ import annotations

import argparse
import json
from hashlib import sha256
from pathlib import Path

import numpy as np
import pandas as pd

from factoryguard.evaluation import intervals as iv

CHANNELS = ('A', 'C')
CANDIDATE = dict(id='smoothing_0.5', group='smoothing', kind='smoothing', features='current',
                 formulation='direct', params={'alpha': 0.5}, rank=1)


def pairs_from_features(path, run, expected_sha=None):
    """Frozen-method forecasts for a development run, through the release code path."""
    from factoryguard.models.forecast import load_table
    from factoryguard.release import modeling as m
    block = m.prepare(load_table(path, run, expected_sha), run)
    prediction = m.predict(CANDIDATE, None, block)
    return pairs_frame(run, block.target, prediction, block.common)


def pairs_frame(run, target, prediction, common):
    frame = pd.DataFrame({'run': run, 'source_index': np.arange(len(target)), 'common': common.astype(bool)})
    for j, ch in enumerate(CHANNELS):
        frame[f'target_{ch}_v'] = target[:, j]
        frame[f'forecast_{ch}_v'] = prediction[:, j]
    return frame


def series(frame, channel):
    f = frame[frame['common']]
    target, forecast = f[f'target_{channel}_v'].to_numpy(float), f[f'forecast_{channel}_v'].to_numpy(float)
    return np.abs(target - forecast), np.abs(forecast)


def evaluate(candidate, frame, warm_frames, channel):
    errors, scale = series(frame, channel)
    warm = [series(w, channel) for w in warm_frames]
    warm_errors = np.concatenate([w[0] for w in warm]) if warm else np.array([])
    warm_scale = np.concatenate([w[1] for w in warm]) if warm else np.array([])
    return iv.score(errors, iv.widths(candidate, errors, scale, warm_errors, warm_scale))


def select(features, output):
    features, output = Path(features), Path(output)
    output.mkdir(parents=True, exist_ok=True)
    frames = {run: pairs_from_features(features / run / 'features.csv', run) for run in ('B01', 'B02')}
    for run, frame in frames.items():
        frame.to_csv(output / f'pairs_{run}.csv', index=False)
    rows = []
    reference = {}
    grid = [dict(id='fixed_early_same_run', kind='fixed_early')] + iv.candidates()
    for candidate in grid:
        for run, other in (('B01', 'B02'), ('B02', 'B01')):
            for channel in CHANNELS:
                result = evaluate(candidate, frames[run], [frames[other]], channel)
                rows.append({'candidate': candidate['id'], 'run': run, 'warm_start': other, 'channel': channel, **result})
                if candidate['id'] == 'fixed_transfer':
                    reference[(run, channel)] = result['interval_score_v']
    table = pd.DataFrame(rows)
    table['coverage_gap'] = (table['coverage'] - iv.NOMINAL).abs()
    table['relative_interval_score'] = [r.interval_score_v / reference[(r.run, r.channel)] for r in table.itertuples()]
    table.to_csv(output / 'development_candidates.csv', index=False)
    eligible = table[table['candidate'] != 'fixed_early_same_run']      # needs a quarter of the run before it can start
    summary = eligible.groupby('candidate').agg(mean_coverage_gap=('coverage_gap', 'mean'),
                                                min_coverage=('coverage', 'min'), max_coverage=('coverage', 'max'),
                                                mean_relative_interval_score=('relative_interval_score', 'mean'),
                                                worst_rolling_coverage=('worst_rolling_coverage', 'min')).reset_index()
    order = {c['id']: i for i, c in enumerate(sorted(iv.candidates(), key=lambda c: (bool(c.get('gamma')), -c.get('window', 10**6))))}
    best = summary['mean_coverage_gap'].min()
    tied = summary[summary['mean_coverage_gap'] <= best + 0.01].copy()
    tied['simplicity'] = tied['candidate'].map(order)
    winner = tied.sort_values(['mean_relative_interval_score', 'simplicity']).iloc[0]['candidate']
    summary.sort_values('mean_coverage_gap').to_csv(output / 'development_summary.csv', index=False)
    chosen = next(c for c in iv.candidates() if c['id'] == winner)
    frozen = {'protocol': 'uncertainty-calibration-v1', 'nominal_level': iv.NOMINAL, 'forecast': CANDIDATE,
              'selected': chosen, 'selection_rule': __doc__.split('Pre-declared selection rule')[1].split('B03 never')[0].strip(),
              'development_runs': ['B01', 'B02'], 'warm_start_for_new_runs': 'B01 then B02 common-mask errors, in that order',
              'pairs_sha256': {run: sha256((output / f'pairs_{run}.csv').read_bytes()).hexdigest() for run in frames},
              'tied_candidates': tied['candidate'].tolist(),
              'status': 'selected on development runs; independent coverage is whatever the frozen application measures'}
    (output / 'frozen_calibrator.json').write_text(json.dumps(frozen, indent=2) + '\n', encoding='utf-8')
    print(summary.sort_values('mean_coverage_gap').head(12).to_string(index=False))
    print('selected', winner, 'from tie set', tied['candidate'].tolist())
    return frozen


def apply(pairs, label, output, results):
    """Frozen application: reads the selected calibrator and development pairs; selects nothing."""
    results, output = Path(results), Path(output)
    frozen = json.loads((results / 'frozen_calibrator.json').read_text(encoding='utf-8'))
    warm = []
    for run in frozen['development_runs']:
        path = results / f'pairs_{run}.csv'
        if sha256(path.read_bytes()).hexdigest() != frozen['pairs_sha256'][run]:
            raise ValueError('Development pairs changed after the calibrator was frozen')
        warm.append(pd.read_csv(path))
    frame = pd.read_csv(pairs)
    out = {'label': label, 'calibrator': frozen['selected'], 'nominal_level': frozen['nominal_level'], 'channels': {}}
    for channel in CHANNELS:
        out['channels'][channel] = {
            'frozen_calibrator': evaluate(frozen['selected'], frame, warm, channel),
            'fixed_transfer_baseline': evaluate(dict(id='fixed_transfer', kind='fixed_transfer'), frame, warm, channel),
            'fixed_early_same_run_baseline': evaluate(dict(id='fixed_early_same_run', kind='fixed_early'), frame, warm, channel)}
    output.mkdir(parents=True, exist_ok=True)
    (output / f'applied_{label}.json').write_text(json.dumps(out, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(out, indent=2))
    return out


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = parser.add_subparsers(dest='command', required=True)
    a = sub.add_parser('select'); a.add_argument('--features', required=True); a.add_argument('--output', required=True)
    a = sub.add_parser('apply'); a.add_argument('--pairs', required=True); a.add_argument('--label', required=True)
    a.add_argument('--results', default='docs/results/uncertainty-calibration-v1'); a.add_argument('--output')
    args = parser.parse_args()
    if args.command == 'select':
        select(args.features, args.output)
    else:
        apply(args.pairs, args.label, args.output or args.results, args.results)


if __name__ == '__main__':
    main()
