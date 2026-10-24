"""Frozen next-observed-burst forecasting. No raw IO, labels or fault policy."""
from __future__ import annotations

from collections import Counter
from hashlib import sha256
import json
from pathlib import Path
import platform

import numpy as np
import pandas as pd

RUNS = ('B01', 'B02', 'B04')
INPUTS = ('feature__A_ac_rms_v', 'feature__C_ac_rms_v',
          'feature__T1_above_room_c', 'feature__T2_above_room_c',
          'context__measured_speed_rpm', 'context__measured_static_load_n',
          'context__measured_dynamic_peak_n')
TARGETS = INPUTS[:2]
CONTEXT = INPUTS[4:]
TIME = 'provenance__source_time'
RUN = 'provenance__experiment'
ID = 'provenance__measurement_id'
WARM = 'quality__documented_warmup_setpoints'


def guard_run(run):
    if run not in RUNS:
        raise ValueError('Only B01/B02/B04 development tables are allowed; B03 remains sealed')


def digest(path):
    h = sha256()
    with Path(path).open('rb') as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b''):
            h.update(block)
    return h.hexdigest()


def clean(value):
    if isinstance(value, dict):
        return {str(k): clean(v) for k, v in value.items()}
    if isinstance(value, (list, tuple, np.ndarray)):
        return [clean(v) for v in value]
    if isinstance(value, (np.bool_, bool)):
        return bool(value)
    if isinstance(value, (np.integer,)):
        return int(value)
    if isinstance(value, (float, np.floating)):
        return float(value) if np.isfinite(value) else None
    return value


def write_json(path, value):
    Path(path).write_text(json.dumps(clean(value), indent=2, allow_nan=False) + '\n')


def validate_frame(frame, run):
    guard_run(run)
    required = set(INPUTS) | {RUN, ID, TIME, WARM}
    if not required.issubset(frame.columns) or frame.empty:
        raise ValueError('Missing required columns or empty feature table')
    if set(frame[RUN]) != {run}:
        raise ValueError('Experiment mixing or incorrect experiment identity')
    if frame[ID].duplicated().any() or not frame[ID].is_monotonic_increasing:
        raise ValueError('Source IDs must be unique and increasing; never silently sort')
    times = pd.to_datetime(frame[TIME], format='%d-%b-%Y %H:%M:%S', errors='raise')
    if times.duplicated().any() or not times.is_monotonic_increasing:
        raise ValueError('Source times must be unique and increasing')
    if frame[WARM].isna().any() or not frame[WARM].isin([True, False]).all():
        raise ValueError('Warm-up metadata must be explicit boolean')
    for col in INPUTS:
        pd.to_numeric(frame[col], errors='raise')  # nonfinite preserved, never imputed
    return times


def load_table(path, run, expected_sha=None):
    guard_run(run)  # before any path access
    path = Path(path)
    if any(p.upper().startswith('B03') for p in path.resolve().parts):
        raise ValueError('Held-out path is forbidden')
    if expected_sha is not None and digest(path) != expected_sha:
        raise ValueError(f'{run} feature table checksum differs from frozen ledger')
    frame = pd.read_csv(path)
    validate_frame(frame, run)
    return frame


def validate_config(config):
    if (config['protocol'] != 'forecast-v1' or config['training_run'] != 'B02'
            or config['validation_run'] != 'B01' or config['stress_run'] != 'B04'
            or config['model'] != 'ridge_delta' or config['alpha'] != 10
            or config['gap_limit_s'] != 24 or config['support_min_count'] != 20
            or tuple(config['inputs']) != INPUTS or tuple(config['targets']) != TARGETS
            or set(config['tables']) != set(RUNS)):
        raise ValueError('Configuration differs from frozen forecast-v1 protocol')


def number(row, col):
    value = row.get(col, np.nan)
    return float(value) if value is not None else float('nan')


def condition_key(row):
    vals = [number(row, c) for c in CONTEXT]
    if not np.isfinite(vals).all():
        return 'undefined'
    return '|'.join(str(int(np.floor(v / 250) * 250)) for v in vals) + ('|warmup' if row[WARM] else '|loaded')


def fit(frame, config, table_hashes=None, config_sha=None):
    """Only B02 pair sources fit transforms; no validation frame is accepted."""
    validate_config(config)
    times = validate_frame(frame, 'B02')
    gaps = times.diff().dt.total_seconds().to_numpy()[1:]
    x = frame[list(INPUTS)].to_numpy(float)[:-1]
    current = frame[list(TARGETS)].to_numpy(float)[:-1]
    target = frame[list(TARGETS)].to_numpy(float)[1:]
    valid = (gaps <= config['gap_limit_s']) & np.isfinite(x).all(axis=1) & np.isfinite(target).all(axis=1)
    if valid.sum() < 2:
        raise ValueError('At least two valid training pairs required')
    x, delta = x[valid], (target - current)[valid]
    mean, scale = x.mean(axis=0), x.std(axis=0, ddof=0)
    scale[scale == 0] = 1
    z, intercept = (x - mean) / scale, delta.mean(axis=0)
    coef = np.linalg.solve(z.T @ z + config['alpha'] * np.eye(len(INPUTS)), z.T @ (delta - intercept))
    # Only sources whose training pair actually entered fitting count toward support.
    support = Counter(condition_key(frame.iloc[i]) for i in np.flatnonzero(valid))
    return clean({'artifact_version': 1, 'config': config, 'config_sha256': config_sha,
                  'table_sha256': table_hashes or {}, 'training_run': 'B02',
                  'training_pairs': int(valid.sum()), 'training_candidate_pairs': len(valid),
                  'training_excluded_gap': int((gaps > config['gap_limit_s']).sum()),
                  'training_excluded_nonfinite': int(((gaps <= config['gap_limit_s']) & ~valid).sum()),
                  'training_source_ids': frame.iloc[np.flatnonzero(valid)][ID].tolist(),
                  'input_mean': mean, 'input_scale': scale, 'delta_intercept': intercept,
                  'coefficients': coef, 'support_counts': dict(sorted(support.items())),
                  'versions': {'python': platform.python_version(), 'numpy': np.__version__, 'pandas': pd.__version__}})


def validate_artifact(artifact):
    validate_config(artifact['config'])
    if artifact['artifact_version'] != 1 or artifact['training_run'] != 'B02':
        raise ValueError('Invalid artifact role/version')
    for key, shape in [('input_mean', (7,)), ('input_scale', (7,)), ('delta_intercept', (2,)), ('coefficients', (7, 2))]:
        arr = np.asarray(artifact[key], dtype=float)
        if arr.shape != shape or not np.isfinite(arr).all():
            raise ValueError(f'Invalid artifact {key}')
    if (np.asarray(artifact['input_scale']) <= 0).any():
        raise ValueError('Invalid scaler')
    return artifact


def load_artifact(path):
    return validate_artifact(json.loads(Path(path).read_text()))


def issue(row, artifact):
    """Does not accept a future row, next arrival time or next quality metadata."""
    guard_run(row[RUN])
    x = np.array([number(row, c) for c in INPUTS])
    persistence = x[:2].copy()
    model = np.full(2, np.nan)
    if np.isfinite(x).all():
        z = (x - artifact['input_mean']) / artifact['input_scale']
        model = persistence + artifact['delta_intercept'] + z @ np.asarray(artifact['coefficients'])
    key = condition_key(row)
    n = artifact['support_counts'].get(key, 0)
    quality = {k: v for k, v in row.items() if k.startswith('quality__')}
    warnings = [k.removeprefix('quality__') for k, v in quality.items()
                if isinstance(v, (bool, np.bool_)) and v and k not in (WARM, 'quality__any_warning')]
    return clean({'run': row[RUN], 'source_id': row[ID], 'source_time': row[TIME],
                  'persistence': persistence, 'ridge': model,
                  'status': 'pending', 'target_id': None, 'target_time': None,
                  'support_key': key, 'support_n': n,
                  'support': 'supported' if n >= artifact['config']['support_min_count'] else ('sparse' if n else 'unseen'),
                  'source_warmup': bool(row[WARM]), 'source_quality': quality,
                  'source_context': {k: v for k, v in row.items() if k.startswith('context__')},
                  'source_warnings': warnings,
                  'context_interpretation_unresolved': row[RUN] == 'B04'})


class Replay:
    """Observe one completed row, settle previous forecast, then issue new one."""
    def __init__(self, artifact, run):
        guard_run(run)
        self.artifact, self.run = validate_artifact(artifact), run
        self.pending, self.last_time, self.last_id = None, None, None
        self.expired_since_observation = False

    def advance_time(self, timestamp):
        now = pd.Timestamp(timestamp)
        if self.last_time is not None and now < self.last_time:
            raise ValueError('Replay clock cannot move backwards')
        self.last_time = now
        if self.pending and (now - pd.to_datetime(self.pending['source_time'], format='%d-%b-%Y %H:%M:%S')).total_seconds() > self.artifact['config']['gap_limit_s']:
            expired = dict(self.pending, status='expired', expiry_reason='No observed target within 24 CSV-clock seconds')
            self.pending = None
            self.expired_since_observation = True
            return expired
        return None

    def observe(self, row):
        guard_run(row[RUN])
        if row[RUN] != self.run:
            raise ValueError('Reset replay between experiments')
        now = pd.to_datetime(row[TIME], format='%d-%b-%Y %H:%M:%S')
        if self.last_time is not None and now < self.last_time:
            raise ValueError('Replay observations must follow the clock')
        if self.last_id is not None and row[ID] <= self.last_id:
            raise ValueError('Replay IDs must increase')
        resolved = None
        if self.pending:
            dt = (now - pd.to_datetime(self.pending['source_time'], format='%d-%b-%Y %H:%M:%S')).total_seconds()
            if dt <= 0:
                raise ValueError('Replay times must strictly increase')
            resolved = dict(self.pending, status='eligible' if dt <= self.artifact['config']['gap_limit_s'] else 'expired',
                            target_id=row[ID], target_time=row[TIME], elapsed_csv_s=dt,
                            observed=[number(row, c) for c in TARGETS],
                            target_warmup=bool(row[WARM]),
                            target_quality={k: v for k, v in row.items() if k.startswith('quality__')})
            if resolved['status'] == 'expired':
                resolved['expiry_reason'] = 'Observed CSV interval exceeds 24 seconds'
        gap = self.expired_since_observation or (resolved is not None and resolved['status'] == 'expired')
        self.expired_since_observation = False
        self.last_time, self.last_id = now, row[ID]
        self.pending = issue(row, self.artifact)
        temperature = {k: number(row, k) for k in ('context__T1_c', 'context__T2_c') if number(row, k) >= 110}
        return clean({'observation': row, 'resolved': resolved, 'issued': self.pending,
                      'acquisition_gap': gap, 'temperature_reference_notices': temperature})


def replay_frame(frame, artifact, run):
    validate_frame(frame, run)
    replay = Replay(artifact, run)
    return [replay.observe(row) for row in frame.to_dict('records')]


def _metric(records, channel):
    actual = np.array([r['observed'][channel] if r['observed'][channel] is not None else np.nan for r in records])
    predictions = {m: np.array([r[m][channel] if r[m][channel] is not None else np.nan for r in records]) for m in ('persistence', 'ridge')}
    common = np.isfinite(actual) & np.isfinite(predictions['persistence']) & np.isfinite(predictions['ridge'])
    out = {'eligible': len(records), 'common_n': int(common.sum()), 'missing_target': int((~np.isfinite(actual)).sum())}
    for model, pred in predictions.items():
        available = np.isfinite(actual) & np.isfinite(pred)
        err = actual[common] - pred[common]
        out[model] = {'available_n': int(available.sum()), 'unavailable_prediction_n': int((~np.isfinite(pred)).sum()),
                      'negative_prediction_n': int((pred < 0).sum()),
                      'mae_v': float(np.mean(np.abs(err))) if len(err) else None,
                      'rmse_v': float(np.sqrt(np.mean(err ** 2))) if len(err) else None}
    for metric in ('mae_v', 'rmse_v'):
        p, m = out['persistence'][metric], out['ridge'][metric]
        out[metric + '_skill'] = 1 - m / p if p is not None and p > 0 else None
    return out


def evaluate(events, run):
    guard_run(run)
    resolved = [e['resolved'] for e in events if e['resolved'] is not None]
    eligible = [r for r in resolved if r['status'] == 'eligible']
    report = {'run': run, 'role': {'B02': 'training resubstitution (optimistic)', 'B01': 'development validation', 'B04': 'as-recorded stress; context interpretation unresolved'}[run],
              'observations': len(events), 'issued': len(events), 'eligible': len(eligible),
              'expired': sum(r['status'] == 'expired' for r in resolved), 'pending': int(bool(events)),
              'source_support_counts_all_issued': dict(Counter(e['issued']['support'] for e in events)),
              'channels': {}, 'strata_overlap': True}
    for j, channel in enumerate('AC'):
        strata = {
            'source_warmup': lambda r: r['source_warmup'],
            'target_warmup': lambda r: r['target_warmup'],
            'loaded_both': lambda r: not r['source_warmup'] and not r['target_warmup'],
            'warmup_transition': lambda r: r['source_warmup'] != r['target_warmup'] or r['source_quality'].get('quality__warmup_regime_transition', False) or r['target_quality'].get('quality__warmup_regime_transition', False),
            'sensor_range_either': lambda r: r['source_quality'].get(f'quality__{channel}_sensor_range_exceeded', False) or r['target_quality'].get(f'quality__{channel}_sensor_range_exceeded', False),
            'local_warning_either': lambda r: r['source_quality'].get('quality__any_warning', False) or r['target_quality'].get('quality__any_warning', False),
            'no_local_warning_either': lambda r: not r['source_quality'].get('quality__any_warning', False) and not r['target_quality'].get('quality__any_warning', False),
            'gap_adjacent': lambda r: r['source_quality'].get('quality__preceding_gap_gt24s', False),
            **{s: (lambda r, s=s: r['support'] == s) for s in ('supported', 'sparse', 'unseen')},
        }
        report['channels'][channel] = {'all': _metric(eligible, j), 'strata': {s: _metric([r for r in eligible if predicate(r)], j) for s, predicate in strata.items()}}
    intervals = [r['elapsed_csv_s'] for r in eligible]
    report['eligible_interval_s'] = {'min': min(intervals) if intervals else None, 'median': float(np.median(intervals)) if intervals else None, 'max': max(intervals) if intervals else None}
    return clean(report)
