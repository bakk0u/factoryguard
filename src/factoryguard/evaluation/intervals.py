"""Causal prediction intervals for next-observed RMS forecasts.

Every calibrator is strictly online: the half-width issued with forecast ``t`` uses
only absolute errors of forecasts already resolved before ``t``. A calibrator may be
warm-started with errors from *other* runs so it can issue intervals from the first
forecast of a new run. Nothing here fits a forecasting model or defines an alert.

These are marginal coverage tools. Serial dependence, regime changes and bearing
degradation mean a nominal level is a target to be measured, never a guarantee.
"""
from __future__ import annotations

import math
from collections import deque

import numpy as np

NOMINAL = 0.90


def conformal_quantile(values, level):
    """Finite-sample split-conformal rank quantile; +inf when there is no history."""
    n = len(values)
    if n == 0:
        return math.inf
    ordered = np.sort(np.asarray(values, dtype=float))
    rank = math.ceil((n + 1) * min(max(level, 0.0), 1.0))
    return float(ordered[min(rank, n) - 1])


def fixed_early(errors, scale, level=NOMINAL, fraction=0.25):
    """Existing audit baseline: one width from the first quarter of the same run."""
    errors = np.asarray(errors, dtype=float)
    cut = len(errors) // 4
    width = conformal_quantile(errors[:cut], level)
    out = np.full(len(errors), np.nan)
    out[cut:] = width
    return out


def fixed_transfer(errors, scale, warm, level=NOMINAL):
    """One width taken from other runs' errors; never updated."""
    return np.full(len(errors), conformal_quantile(warm, level))


def rolling(errors, scale, warm, warm_scale, window, level=NOMINAL, relative=False, gamma=0.0):
    """Rolling conformal half-widths.

    relative: calibrate error / forecast level and multiply back, so the band scales
              with the signal as a bearing's vibration level changes.
    gamma>0:  adaptive conformal inference (Gibbs & Candes, 2021): the working miscoverage
              is nudged after every resolved forecast so long-run coverage tracks the target.
    """
    errors = np.asarray(errors, dtype=float)
    scale = np.asarray(scale, dtype=float)
    norm = (lambda e, s: e / max(s, 1e-9)) if relative else (lambda e, s: e)
    history = deque((norm(e, s) for e, s in zip(warm, warm_scale)), maxlen=window)
    alpha_target = 1 - level
    alpha = alpha_target
    out = np.empty(len(errors))
    for t in range(len(errors)):
        q = conformal_quantile(history, 1 - alpha)
        width = q * max(scale[t], 1e-9) if relative else q
        out[t] = width
        miss = float(errors[t] > width)
        if gamma:
            alpha = min(max(alpha + gamma * (alpha_target - miss), 0.001), 0.5)
        history.append(norm(errors[t], scale[t]))          # revealed only after the forecast was issued
    return out


def candidates():
    out = [dict(id='fixed_transfer', kind='fixed_transfer')]
    for relative in (False, True):
        for window in (30, 60, 120, 240):
            for gamma in (0.0, 0.005, 0.02):
                name = f"{'aci' if gamma else 'rolling'}_{'rel' if relative else 'abs'}_w{window}" + (f'_g{gamma}' if gamma else '')
                out.append(dict(id=name, kind='rolling', window=window, relative=relative, gamma=gamma))
    return out


def widths(candidate, errors, scale, warm, warm_scale, level=NOMINAL):
    if candidate['kind'] == 'fixed_early':
        return fixed_early(errors, scale, level)
    if candidate['kind'] == 'fixed_transfer':
        return fixed_transfer(errors, scale, warm, level)
    return rolling(errors, scale, warm, warm_scale, candidate['window'], level,
                   candidate['relative'], candidate['gamma'])


def score(errors, half_width, level=NOMINAL, window=100):
    """Coverage, sharpness and stability of a sequence of symmetric intervals."""
    errors = np.asarray(errors, dtype=float)
    half_width = np.asarray(half_width, dtype=float)
    keep = np.isfinite(half_width)
    e, w = errors[keep], half_width[keep]
    if not len(e):
        return dict(n=0)
    hit = e <= w
    alpha = 1 - level
    winkler = 2 * w + (2 / alpha) * np.maximum(e - w, 0)
    rolling_cov = (np.convolve(hit, np.ones(window), 'valid') / window) if len(e) >= window else np.array([hit.mean()])
    quarters = [float(part.mean()) for part in np.array_split(hit, 4)]
    return dict(n=int(len(e)), coverage=float(hit.mean()), mean_half_width_v=float(w.mean()),
                median_half_width_v=float(np.median(w)), interval_score_v=float(winkler.mean()),
                worst_rolling_coverage=float(rolling_cov.min()), coverage_by_quarter=quarters,
                last_quarter_coverage=quarters[-1])
