# Forecast uncertainty calibration (v1)

The [chronological audit](forecast_uncertainty.md) showed that a fixed nominal-90% band,
set from the first quarter of a run, covered far less than 90% of later errors. This study
replaces that band with a causal calibrator chosen on development data and then checked,
unchanged, on data that played no part in choosing it.

## Method and selection (development: B01 and B02 only)

- Forecasts are the frozen release method (exponential smoothing, alpha 0.5) on the common
  mask, produced through the release code path.
- Every calibrator is strictly online: the half-width issued with a forecast uses only errors
  of forecasts already resolved. A calibrator for a new run is warm-started with errors from
  other runs, so it issues an interval from the first forecast.
- Candidates: one transferred fixed width; rolling conformal quantiles over 30/60/120/240
  resolved forecasts, on absolute error or on error relative to the forecast level; each with
  or without an adaptive conformal step (gamma 0.005 or 0.02). 25 candidates in total.
- Reciprocal evaluation: B01 warm-started with B02 only, and B02 with B01 only, per channel.
- Selection rule, written into `scripts/calibrate_forecast_uncertainty.py` before any result
  existed: smallest mean gap to 90% coverage over the four run/channel cells; ties within 0.01
  broken by lower interval (Winkler) score, then by simplicity.

Selected and frozen: **`aci_rel_w240_g0.02`**, a 240-forecast rolling quantile of relative
error with adaptive step 0.02. The frozen choice and the hashes of the development forecast
pairs are in [`frozen_calibrator.json`](results/uncertainty-calibration-v1/frozen_calibrator.json);
every candidate's development result, including the worse ones, is in
[`development_candidates.csv`](results/uncertainty-calibration-v1/development_candidates.csv).

## What the development numbers do and do not show

Adaptive conformal methods steer long-run coverage toward the target by construction, so a
development coverage near 90% is expected and is not evidence of calibration on its own. The
informative figures are the interval score (how wide the band had to be), the worst coverage
over any 100 consecutive forecasts, and coverage in the final quarter of a run, where the
bearing's vibration level has changed most.

## Independent check (pre-registered before B03 was opened)

This file, the frozen calibrator and the development pairs were committed before the sealed
B03 reserve run was accessed. After the single frozen B03 forecasting evaluation
([readiness checklist](b03_readiness.md)), the frozen calibrator is applied once to B03's
saved forecast pairs, warm-started with B01 then B02 errors:

```bash
python scripts/calibrate_forecast_uncertainty.py apply --pairs <B03 pairs.csv> --label B03
```

Reported, whatever the outcome: coverage, mean half-width, interval score, worst rolling-100
coverage and coverage by quarter, for the frozen calibrator and for both fixed baselines.
Nothing is re-selected or tuned on B03. B04 is reported as a diagnostic only because its
speed/load scaling is unresolved.

## Results

Development (reciprocal B01/B02, used for selection) and independent application of the
frozen calibrator. Target coverage 90%.

| Run | Role | Channel | Frozen adaptive: coverage | Worst 100-forecast window | Last quarter | Fixed transfer: coverage / last quarter | Fixed early same-run: coverage / last quarter |
| :--- | :--- | :--- | ---: | ---: | ---: | ---: | ---: |
| **B03** | **Independent, applied once** | A | **89.5%** | 85% | 88.2% | 93.8% / 75.0% | 81.3% / 51.8% |
| **B03** | **Independent, applied once** | C | **89.4%** | 84% | 86.8% | 94.1% / 76.3% | 84.3% / 52.6% |
| B04 | Diagnostic only | A | 89.8% | 83% | 89.2% | 71.7% / 36.1% | 37.8% / 14.9% |
| B04 | Diagnostic only | C | 89.8% | 84% | 88.8% | 78.6% / 42.6% | 37.4% / 12.0% |

On B03 the frozen calibrator's interval score was 0.126 V (A) and 0.087 V (C), against
0.271 / 0.170 for the transferred fixed width and 0.315 / 0.192 for the same-run fixed
width: closer to target, more stable, and narrower where it could be.

Development figures for every candidate are in `development_summary.csv`; the selected one
averaged a 0.3-point gap to target across the four development cells with a worst
100-forecast window of 78%.

**What changed in practice.** A fixed band is set when the bearing is quiet and is then too
narrow for the rest of the run: about half of late errors fell outside it. Scaling the band
with the forecast level and correcting it after each resolved forecast keeps coverage near
target through the late, high-vibration regime on a run the method had never seen.

**Limits.** One independent run. Coverage is marginal over the run, not conditional on any
operating state; a 100-forecast window fell to 84%. The adaptive step reacts after misses,
so the first forecasts after an abrupt change are the least protected. B04 agreement is
encouraging but B04 is not clean evidence.

Interval coverage is a statement about forecast error. It is not a fault probability, an alert
threshold or a health indicator.
