"""Bounded nested development selection, with causal burst histories and pipelines."""
from dataclasses import dataclass
from datetime import datetime
import json

import numpy as np
import pandas as pd
from sklearn.base import BaseEstimator, TransformerMixin
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import Ridge
from sklearn.multioutput import MultiOutputRegressor
from sklearn.tree import DecisionTreeRegressor

from factoryguard.models.forecast import INPUTS, TARGETS, CONTEXT, TIME, ID, RUN, validate_frame

TEMPORAL_NAMES = (*INPUTS, 'history__A_previous_rms_v', 'history__C_previous_rms_v',
                  'history__A_recent_change_v', 'history__C_recent_change_v',
                  'history__speed_mean3_rpm', 'history__static_mean3_n', 'history__dynamic_mean3_n')
GROUPS = ('persistence', 'smoothing', 'ridge_current', 'ridge_temporal', 'tree_current', 'tree_temporal')


class FiniteGate(TransformerMixin, BaseEstimator):
    """An explicit no-imputation contract inside the fitted pipeline."""
    def fit(self, X, y=None):
        self.n_features_in_ = np.asarray(X).shape[1]
        self.transform(X)
        return self

    def transform(self, X):
        x = np.asarray(X, dtype=float)
        if x.ndim != 2 or x.shape[1] != self.n_features_in_ or not np.isfinite(x).all():
            raise ValueError('Pipeline requires finite explicitly available features; no imputation')
        return x


@dataclass
class Block:
    run: str
    frame: pd.DataFrame
    start: int
    stop: int
    X: dict
    current: np.ndarray
    target: np.ndarray
    gaps: np.ndarray
    target_interval: np.ndarray
    history_start: np.ndarray
    history_ready: np.ndarray
    arrival: np.ndarray
    common: np.ndarray
    exclusion: np.ndarray


def prepare(frame, run, start=0, stop=None):
    """Build independent replay block, retaining every row; no history before start."""
    validate_frame(frame, run)
    stop = len(frame) if stop is None else stop
    if not 0 <= start < stop <= len(frame):
        raise ValueError('Invalid chronological block')
    f = frame.iloc[start:stop].reset_index(drop=True).copy()
    clock = [datetime.strptime(t, '%d-%b-%Y %H:%M:%S') for t in f[TIME]]
    seconds = np.array([(t-clock[0]).total_seconds() for t in clock])
    gaps = np.r_[np.nan, np.diff(seconds)]
    interval = np.r_[np.diff(seconds), np.nan]
    current = f[list(TARGETS)].to_numpy(float)
    x = f[list(INPUTS)].to_numpy(float)
    temporal = np.full((len(f), 14), np.nan)
    temporal[:, :7] = x
    history_start = np.empty(len(f), dtype=int)
    ready = np.zeros(len(f), dtype=bool)
    segment_start = 0
    for i in range(len(f)):
        if i == 0 or gaps[i] > 24:
            segment_start = i
        history_start[i] = segment_start + start
        if i - segment_start >= 2:
            ready[i] = True
            temporal[i, 7:9] = current[i-1]
            temporal[i, 9:11] = current[i] - current[i-1]
            temporal[i, 11:] = x[i-2:i+1, 4:7].mean(axis=0)
    target = np.vstack([current[1:], [np.nan, np.nan]])
    arrival = (interval > 0) & (interval <= 24)
    finite = np.isfinite(x).all(axis=1) & np.isfinite(temporal).all(axis=1)
    # Both past RMS channels are needed throughout the three-observation history,
    # including t-2 although it is not an explicit RMS lag column.
    for i in np.flatnonzero(ready):
        finite[i] &= np.isfinite(current[i-2:i+1]).all()
    common = arrival & ready & finite & np.isfinite(target).all(axis=1)
    exclusion = np.full(len(f), 'common', dtype=object)
    for i in range(len(f)):
        if i == len(f)-1: reason = 'pending_block_end'
        elif not arrival[i]: reason = 'expired_gap'
        elif not np.isfinite(target[i]).all(): reason = 'nonfinite_target'
        elif not ready[i]: reason = 'insufficient_history'
        elif not finite[i]: reason = 'nonfinite_features_or_history'
        else: reason = 'common'
        exclusion[i] = reason
    return Block(run, f, start, stop, {'current': x, 'temporal': temporal}, current, target,
                 gaps, interval, history_start, ready, arrival, common, exclusion)


def splits(frame, run, config):
    n = len(frame)
    result = []
    for fold, (a, b) in enumerate(config['split_fractions']):
        boundary, end = int(n*a), int(n*b)
        if boundary < 4 or end-boundary < 4:
            raise ValueError('Too few observations for frozen expanding-window folds')
        result.append((prepare(frame, run, 0, boundary), prepare(frame, run, boundary, end),
                       {'fold': fold, 'train_start': 0, 'train_stop_exclusive': boundary,
                        'validation_start': boundary, 'validation_stop_exclusive': end,
                        'purged_cross_boundary_source_index': boundary-1,
                        'purged_cross_boundary_source_id': int(frame.iloc[boundary-1][ID]),
                        'first_possible_common_validation_source_index': boundary+2,
                        'history_reset_at_validation_start': True}))
    return result


def candidates(config):
    out = [{'id': 'persistence', 'group': 'persistence', 'kind': 'persistence', 'features': 'current', 'params': {}, 'rank': 0}]
    for i, alpha in enumerate(config['smoothing_alpha']):
        out.append({'id': f'smoothing_a{alpha:g}', 'group': 'smoothing', 'kind': 'smoothing', 'features': 'current', 'params': {'alpha': alpha}, 'rank': i})
    for features in ('current', 'temporal'):
        for i, alpha in enumerate(config['ridge_alpha']):
            out.append({'id': f'ridge_{features}_a{alpha:g}', 'group': f'ridge_{features}', 'kind': 'ridge', 'features': features, 'params': {'alpha': alpha}, 'rank': i})
        for i, params in enumerate(config['tree_grid']):
            out.append({'id': f'tree_{features}_d{params["max_depth"]}_l{params["min_samples_leaf"]}', 'group': f'tree_{features}', 'kind': 'tree', 'features': features, 'params': params, 'rank': i})
    return out


def fit_candidate(candidate, block, seed=42):
    if block.run not in ('B01', 'B02'):
        raise ValueError('Only an outer B01/B02 training run may fit; B04 is diagnostic')
    if candidate['kind'] in ('persistence', 'smoothing'):
        return None
    x = block.X[candidate['features']][block.common]
    delta = (block.target-block.current)[block.common]
    if len(x) < 2:
        raise ValueError('Insufficient valid common training pairs')
    if candidate['kind'] == 'ridge':
        steps = [('finite', FiniteGate()), ('scale', StandardScaler()),
                 ('estimate', Ridge(alpha=candidate['params']['alpha'], solver='cholesky'))]
    else:
        estimator = MultiOutputRegressor(DecisionTreeRegressor(**candidate['params'], random_state=seed), n_jobs=1)
        steps = [('finite', FiniteGate()), ('estimate', estimator)]
    return Pipeline(steps).fit(x, delta)


def predict(candidate, fitted, block):
    """Forecast all source rows, including final pending rows. No target access."""
    if candidate['kind'] == 'persistence':
        return block.current.copy()
    if candidate['kind'] == 'smoothing':
        out = np.full_like(block.current, np.nan)
        state = np.full(2, np.nan)
        alpha = candidate['params']['alpha']
        for i, rms in enumerate(block.current):
            if i == 0 or block.gaps[i] > 24:
                state[:] = np.nan
            finite = np.isfinite(rms)
            state[~finite] = np.nan
            initialize = finite & ~np.isfinite(state)
            update = finite & ~initialize
            state[initialize] = rms[initialize]
            state[update] = alpha*rms[update] + (1-alpha)*state[update]
            out[i] = state
        return out
    x = block.X[candidate['features']]
    valid = np.isfinite(x).all(axis=1) & np.isfinite(block.current).all(axis=1)
    if candidate['features'] == 'temporal':
        valid &= block.history_ready
        for i in np.flatnonzero(valid):
            valid[i] &= np.isfinite(block.current[i-2:i+1]).all()
    out = np.full_like(block.current, np.nan)
    if valid.any():
        out[valid] = block.current[valid] + fitted.predict(x[valid])
    return out


def errors(y, pred, mask):
    e = y[mask]-pred[mask]
    return {'n': int(mask.sum()), 'mae_v': float(np.abs(e).mean()) if len(e) else None,
            'rmse_v': float(np.sqrt(np.mean(e*e))) if len(e) else None}


def ratio(value, baseline):
    if value is None or baseline is None:
        return float('inf')
    if baseline == 0:
        return 1.0 if value == 0 else float('inf')
    return value/baseline


def metrics(block, prediction, common=True):
    out = {}
    for j, c in enumerate('AC'):
        mask = block.common.copy() if common else block.arrival & np.isfinite(block.current[:, j]) & np.isfinite(block.target[:, j])
        # On common pairs an unavailable candidate is an error, not a smaller denominator.
        if common and not np.isfinite(prediction[mask]).all():
            raise ValueError('Candidate unavailable on predeclared common pairs')
        mask &= np.isfinite(prediction[:, j])
        m = errors(block.target[:, j], prediction[:, j], mask)
        p = errors(block.target[:, j], block.current[:, j], mask)
        out[c] = {**m, 'persistence_mae_v': p['mae_v'], 'persistence_rmse_v': p['rmse_v'],
                  'mae_ratio': ratio(m['mae_v'], p['mae_v']), 'rmse_ratio': ratio(m['rmse_v'], p['rmse_v'])}
    return out


def score(stats):
    return float(np.mean([stats[c]['mae_ratio'] for c in 'AC']))


def choose_inner(trials, group, tolerance=.01):
    options = [t for t in trials if t['candidate']['group'] == group and np.isfinite(t['validation_score'])]
    if not options:
        raise ValueError(f'No valid chronological validation trials for {group}')
    best = min(t['validation_score'] for t in options)
    return min((t for t in options if t['validation_score'] <= best+tolerance), key=lambda t:t['candidate']['rank'])['candidate']


def select_method(outer, config):
    """Only two B01/B02 development result cells per group; no B04 accepted."""
    if set(outer) != {'B01', 'B02'}:
        raise ValueError('Selection requires exactly B01/B02 outer evaluation runs')
    rows = []
    for group in GROUPS:
        cells = [outer[run][group][c]['mae_ratio'] for run in ('B01', 'B02') for c in 'AC']
        per_run = {r: float(np.mean([outer[r][group][c]['mae_ratio'] for c in 'AC'])) for r in ('B01','B02')}
        macro = float(np.mean(cells))
        qualified = (np.isfinite(cells).all() and macro <= 1-config['selection_min_macro_improvement']
                     and max(per_run.values()) <= config['selection_max_run_ratio']
                     and max(cells) <= config['selection_max_channel_ratio'])
        rows.append({'group': group, 'macro_mae_ratio': macro, 'macro_mae_skill': 1-macro,
                     'run_mae_ratios': per_run, 'max_channel_ratio': max(cells), 'qualified': bool(qualified)})
    eligible = [r for r in rows if r['qualified']]
    selected = 'persistence'
    if eligible:
        best = min(r['macro_mae_ratio'] for r in eligible)
        selected = min((r['group'] for r in eligible if r['macro_mae_ratio'] <= best+config['selection_simplicity_tolerance']), key=config['complexity_order'].index)
    return {'selected_group': selected, 'method_results': rows, 'label': 'development selection results; not unbiased final performance'}
