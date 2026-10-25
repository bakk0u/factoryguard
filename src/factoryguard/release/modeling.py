"""Frozen v3 candidate definitions. No raw I/O or holdout access."""
import numpy as np
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import Ridge
from sklearn.ensemble import ExtraTreesRegressor, HistGradientBoostingRegressor
from sklearn.multioutput import MultiOutputRegressor

from factoryguard.models.forecast import INPUTS
from factoryguard.models.selection import FiniteGate, TEMPORAL_NAMES
from factoryguard.models import selection as old

DESCRIPTORS = tuple(f'feature__{c}_{s}' for c in 'AC' for s in ('crest_factor', 'excess_kurtosis'))
ENRICHED = (*TEMPORAL_NAMES, 'history__A_mean3', 'history__C_mean3',
            'history__A_std3', 'history__C_std3', 'history__T1_change',
            'history__T2_change', 'history__speed_change', 'history__static_change',
            'history__dynamic_change', *DESCRIPTORS)


def prepare(frame, run, start=0, stop=None):
    block = old.prepare(frame, run, start, stop)
    return enrich(block)


def enrich(block):
    """Extend a validated block; does no I/O or experiment authorization."""
    f = block.frame
    extra = np.full((len(f), 13), np.nan)
    extra[:, 9:] = f[list(DESCRIPTORS)].to_numpy(float)
    for i in np.flatnonzero(block.history_ready):
        extra[i, :2] = block.current[i-2:i+1].mean(axis=0)
        extra[i, 2:4] = block.current[i-2:i+1].std(axis=0, ddof=0)
        extra[i, 4:9] = block.X['current'][i, 2:] - block.X['current'][i-1, 2:]
    block.X['temporal'] = np.column_stack((block.X['temporal'], extra))
    finite = np.isfinite(block.X['temporal']).all(axis=1)
    block.exclusion[block.common & ~finite] = 'nonfinite_features_or_history'
    block.common &= finite
    return block


def candidates():
    out = [dict(id='persistence', group='persistence', kind='persistence', features='current',
                formulation='direct', params={}, rank=0)]
    for i, a in enumerate((.8, .5, .2)):
        out.append(dict(id=f'smoothing_{a}', group='smoothing', kind='smoothing',
                        features='current', formulation='direct', params={'alpha': a}, rank=i))
    grids = {'ridge': [{'alpha': 100.}, {'alpha': 10.}],
             'extra': [{'min_samples_leaf': 30}, {'min_samples_leaf': 10}],
             'boost': [{'learning_rate': .03}, {'learning_rate': .1}],
             'xgb': [{}]}
    for kind, grid in grids.items():
        for features in ('current', 'temporal'):
            for formulation in ('delta', 'direct'):
                group = f'{kind}_{features}_{formulation}'
                for rank, params in enumerate(grid):
                    out.append(dict(id=f'{group}_{rank}', group=group, kind=kind, features=features,
                                    formulation=formulation, params=params, rank=rank))
    return out


def groups():
    return list(dict.fromkeys(c['group'] for c in candidates()))


def fit(candidate, blocks):
    if any(b.run not in ('B01', 'B02') for b in blocks):
        raise ValueError('Only B01/B02 may fit release models')
    kind = candidate['kind']
    if kind in ('persistence', 'smoothing'):
        return None
    x = np.concatenate([b.X[candidate['features']][b.common] for b in blocks])
    y = np.concatenate([(b.target-b.current if candidate['formulation']=='delta' else b.target)[b.common]
                        for b in blocks])
    if len(x) < 2:
        raise ValueError('Insufficient common training pairs')
    params = candidate['params']
    steps = [('finite', FiniteGate())]
    if kind == 'ridge':
        steps += [('scale', StandardScaler())]
        estimator = Ridge(**params, solver='cholesky')
    elif kind == 'extra':
        estimator = MultiOutputRegressor(ExtraTreesRegressor(n_estimators=64, max_depth=4,
                    **params, random_state=42, n_jobs=1), n_jobs=1)
    elif kind == 'boost':
        estimator = MultiOutputRegressor(HistGradientBoostingRegressor(max_iter=60,
                    max_leaf_nodes=7, min_samples_leaf=20, l2_regularization=1,
                    early_stopping=False, **params, random_state=42), n_jobs=1)
    elif kind == 'xgb':
        from xgboost import XGBRegressor
        estimator = MultiOutputRegressor(XGBRegressor(n_estimators=60, max_depth=2,
                    learning_rate=.05, reg_lambda=10, min_child_weight=20,
                    objective='reg:squarederror', tree_method='hist', device='cpu',
                    n_jobs=1, random_state=42), n_jobs=1)
    else:
        raise ValueError(f'Unknown candidate {kind}')
    return Pipeline(steps + [('estimate', estimator)]).fit(x, y)


def predict(candidate, fitted, block):
    # Existing prediction code reads only source features/history, never target.
    result = old.predict(candidate, fitted, block)
    if candidate['kind'] not in ('persistence', 'smoothing') and candidate['formulation']=='direct':
        result -= block.current
    return result


def select(outer):
    if set(outer) != {'B01', 'B02'}:
        raise ValueError('Exactly B01/B02 outer selection required')
    rows = []
    for group in groups():
        cells = [outer[r][group][c]['mae_ratio'] for r in ('B01','B02') for c in 'AC']
        per_run = [np.mean(cells[:2]), np.mean(cells[2:])]
        macro = float(np.mean(cells))
        rows.append(dict(group=group, macro_mae_ratio=macro, macro_mae_skill=1-macro,
                         qualified=bool(np.isfinite(cells).all() and macro<=.98
                                        and max(per_run)<=1 and max(cells)<=1.05)))
    eligible = [r for r in rows if r['qualified']]
    best = min((r['macro_mae_ratio'] for r in eligible), default=1.)
    selected = next((r['group'] for r in eligible if r['macro_mae_ratio']<=best+.02), 'persistence')
    return {'selected_group': selected, 'method_results': rows,
            'label': 'development selection results, not unbiased final performance'}
