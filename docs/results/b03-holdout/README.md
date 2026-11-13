# B03 sealed reserve: one frozen evaluation

**Executed once on 2026-11-13**, after owner authorization and the
[pre-execution review](review.md). The method, metrics and validity rules were frozen in
[`configs/reserve_plan.json`](../../../configs/reserve_plan.json) before any B03 signal was
read. Nothing was fitted, tuned, corrected or excluded afterwards. B03 can no longer serve
as an untouched holdout.

## Result

Next-observed-burst RMS forecast, exponential smoothing (alpha 0.5) against persistence.
611 common forecast pairs out of 614 bursts (2 lack history, 1 has no following burst).

| Channel | MAE smoothing (V) | MAE persistence (V) | MAE ratio | RMSE ratio |
| :--- | ---: | ---: | ---: | ---: |
| A | 0.02371 | 0.02768 | **0.857** | 0.821 |
| C | 0.01540 | 0.01792 | **0.859** | 0.815 |
| **Equal-channel macro** | | | **0.858** | |

**Smoothing reduced mean absolute error by 14.2% relative to persistence on a bearing run
that played no part in development.** The development estimate from reciprocal B01/B02
evaluation was 12.83%, so the held-out result is in line with it rather than a fall-off.

## Where the gain does and does not appear

| Stratum | n | MAE ratio A | MAE ratio C |
| :--- | ---: | ---: | ---: |
| Operating bin changed between bursts | 580 | 0.854 | 0.855 |
| Operating bin unchanged | 31 | 1.007 | 1.165 |
| Operating condition well supported in development | 514 | 0.860 | 0.862 |
| Operating condition sparse in development | 97 | 0.843 | 0.847 |

The improvement comes from the usual case in this rig, where speed and load are redrawn
before every burst and the last reading is a noisy predictor. In the 31 pairs where the
operating bin stayed the same, smoothing was no better than persistence on channel A and
16% worse on channel C. That subset is small, but the direction is a real limit: when
conditions hold steady, the latest reading is hard to beat.

No range warnings, local warnings, gaps over 24 s or unseen operating bins occurred in B03,
and the provided measurements contain no warm-up rows.

## Interval coverage (frozen calibrator, applied once)

The calibrator chosen on B01/B02 and frozen before B03 was opened
([method](../../uncertainty_calibration.md)), warm-started with B01 then B02 errors:

| Channel | Method | Coverage (target 90%) | Worst 100-forecast window | Last quarter of run | Mean half-width (V) | Interval score |
| :--- | :--- | ---: | ---: | ---: | ---: | ---: |
| A | **Frozen adaptive relative** | **89.5%** | 85% | 88.2% | 0.049 | **0.126** |
| A | Fixed width from B01/B02 | 93.8% | 62% | 75.0% | 0.076 | 0.271 |
| A | Fixed width from B03's first quarter | 81.3% | 47% | 51.8% | 0.025 | 0.315 |
| C | **Frozen adaptive relative** | **89.4%** | 84% | 86.8% | 0.036 | **0.087** |
| C | Fixed width from B01/B02 | 94.1% | 64% | 76.3% | 0.051 | 0.170 |
| C | Fixed width from B03's first quarter | 84.3% | 47% | 52.6% | 0.018 | 0.192 |

The fixed bands fail in the way the earlier audit warned: adequate early, then about half
coverage in the last quarter as the vibration level rises. The frozen adaptive band stayed
within about three points of target in every quarter and never dropped below 84% over any
100 consecutive forecasts, with less than half the interval score.

## What this does not establish

- One bearing is one laboratory case. It is not a population estimate; a second held-out
  run could give a different number.
- The forecast horizon is the next observed burst (about 12 s). This says nothing about
  remaining useful life, damage onset or fault detection.
- Adaptive conformal intervals track long-run coverage by construction. The independent
  evidence is that the band stayed stable through the late regime without being wide; it is
  not a guarantee of conditional coverage at any moment.
- The run ended by automatic stop at 110 °C. That fact was not used as a label.
- Timestamps have no declared time zone and measurement-to-row association is ordinal.

## Files

| File | Content |
| :--- | :--- |
| `result.json` | Complete output of the frozen runner, including raw-file SHA-256 inventory |
| `attempt.json` | Attempt manifest written before processing |
| `quality_strata.csv`, `operating_transitions.csv` | Strata, for the selected method and persistence |
| `features.csv`, `forecasts.npz`, `pairs_B03.csv` | Derived burst descriptors and forecast pairs (no raw waveforms) |
| `attestation.json`, `review.md` | Pre-execution gate record |
| [`../uncertainty-calibration-v1/applied_B03.json`](../uncertainty-calibration-v1/applied_B03.json) | Interval results above |

Data: Osarenren Kennedy Aimiyekagbon, Paderborn University, Zenodo 10868257, CC BY 4.0.
