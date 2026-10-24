# Forecast-v1: measured results and limitations

Implemented and executed 2026-10-23. The frozen ridge candidate **does not improve on persistence in B01 development validation**. Retain persistence as the demonstrated benchmark; the ridge candidate remains an unsuccessful development comparison. Neither output is a proven fault, failure probability or RUL. No hyperparameters, features, bins or thresholds were changed after seeing results.

## Protocol, authorization and reproducibility

The current user request supersedes earlier acquisition/feature-only prohibitions. AGENTS, README, configs/dataset_roles.json, model status and project status now explicitly scope that authorization to this prototype. The original proposal in modeling_protocol.md is historical; its **frozen execution amendment** and configs/forecast_v1.json govern execution. The feature schema's empty default model-input list remains intentional: forecasting uses its own explicit seven-column allowlist, never all numeric columns. B04's global interpretation warning is additional to local quality flags. These resolve the prior documentation inconsistencies without changing raw data or feature definitions.

Before the first fit, the execution amendment fixed B02 fitting, B01 development validation, B04 separate as-recorded stress, B03 sealed; ridge delta regression with alpha=10; seven current-burst inputs; train-only population mean/std; no imputation/clipping; and the existing >24-second gap rule. Current A/C RMS, two temperature-above-ambient values and three measured operating quantities are the only inputs. The model adds a learned two-channel increment to persistence. Current crest/kurtosis, commands, clocks, IDs, warning flags, source segments and all next-row context/flags are excluded.

The seven-input scaler and regularized delta regression used **1114 B02 pairs**; one long-gap transition was excluded from fitting, but both records are retained. The final burst is a target only, not a training source. Source-pair IDs, scaler, intercept, coefficients and bin support are saved. No validation/reserve data fits preprocessing. B02 was recorded after B01 in calendar time: this is retrospective experiment-separated laboratory validation, not a prospective historical-deployment claim.

Executed outputs: `reports/local/forecast-v1/model/model.json`, `evaluation/summary.json`, `evaluation/metrics.csv`, per-run `.forecasts.jsonl` and PNG histories, and `replay-B01/events.jsonl`. Exact config/table hashes are in the artifact; environment.txt captures executed package versions. Commands and setup are in [forecast_demo.md](forecast_demo.md). The numeric JSON artifact reloads identically. No additional download or B03 source/feature access occurred.

## Primary as-recorded scores

MAE/RMSE in volts, on identical common finite channel pairs. Skill = 1 − ridge error / persistence error; negative is worse. All suspect/range-warning measurements remain included. There were no unavailable finite-input predictions, missing RMS targets or negative predictions on these scored pairs. B02 resubstitution is optimistic and does not establish generalization.

| Role / run | Channel | n | Persistence MAE / RMSE | Ridge MAE / RMSE | MAE / RMSE skill |
| --- | --- | ---: | --- | --- | --- |
| Development validation B01 | A | 372 | 0.043027 / 0.078994 | 0.061381 / 0.086234 | −42.66% / −9.17% |
| Development validation B01 | C | 372 | 0.028006 / 0.053918 | 0.037758 / 0.055316 | −34.82% / −2.59% |
| Training diagnostic B02 | A | 1114 | 0.026358 / 0.052718 | 0.025644 / 0.048841 | +2.71% / +7.35% |
| Training diagnostic B02 | C | 1114 | 0.019246 / 0.037820 | 0.018251 / 0.033782 | +5.17% / +10.68% |
| Separate stress B04 | A | 1113 | 0.072726 / 0.112027 | 0.088666 / 0.116242 | −21.92% / −3.76% |
| Separate stress B04 | C | 1113 | 0.039907 / 0.065175 | 0.052363 / 0.066970 | −31.21% / −2.76% |

| Run | Observations / forecasts issued | Eligible | Expired gaps | Final pending | Eligible CSV intervals: min / median / max s |
| --- | ---: | ---: | ---: | ---: | --- |
| B01 | 377 | 372 | 4 | 1 | 11 / 18 / 23 |
| B02 | 1116 | 1114 | 1 | 1 | 11 / 18 / 23 |
| B04 | 1114 | 1113 | 0 | 1 | 12 / 18 / 24 |

The target is **next observed burst**, not a fixed 18-second forecast. At issuance the next arrival time is unknown. A forecast settles only if the arrival interval is <=24 s; otherwise its ledger entry is expired, no error is scored, and a new forecast is issued at the new observation. No gap is filled or crossed by a scored pair. Explicit clock expiry before arrival is also implemented. The final forecast has no observed target and remains pending. CSV clock meaning/timezone and ordinal waveform association remain provisional; these intervals are not operating time.

## Support, quality and observed weaknesses

Support uses the original half-open 250 rpm ×250 N static ×250 N measured dynamic-peak bins, with warm-up separate. Only B02 fitting-pair sources count toward training-bin occupancy. Supported means >=20; 1–19 is sparse, 0 is unseen. This tests occupancy, not joint state/transition equivalence or healthy coverage. B01/B02's documented loaded overlap remains the same; bins were not widened.

| Eligible forecast source stratum | B01 | B02 | B04 |
| --- | ---: | ---: | ---: |
| Supported bin | 235 | 903 | 0 |
| Sparse bin | 61 | 211 | 0 |
| Unseen bin | 76 | 0 | 1113 |
| Source warm-up setpoints (includes outbound transition) | 51 | 51 | 50 |
| Both source/target loaded | 321 | 1063 | 1063 |
| Warm-up transition or adjacent transition flag | 2 | 2 | 2 |
| Either-row local warning | 111 | 53 | 210 |
| A sensor-range warning at either end | 10 | 0 | 0 |
| C sensor-range warning at either end | 1 | 0 | 0 |
| Source follows a long acquisition gap | 4 | 1 | 0 |

Strata overlap; do not sum them. Full per-channel MAE/RMSE and availability counts for every stratum, including zero-count cases with null metrics, are in metrics.csv and run JSON. All B04 rows additionally carry the global context-interpretation caveat even outside its local-warning subset. All B04 measured bins, including its warm-up, are unseen in B02 training; this describes reported values, not proven physical disjointness.

**Descriptive findings:** Ridge loses to persistence even in B01's supported-bin subset: A MAE 0.071712 versus 0.053977 V (n=235), C 0.043695 versus 0.035062 V. Its B01 target-warm-up MAEs are 0.014798/0.010360 V versus persistence 0.000193/0.000149 V (A/C, n=50). Its B02 target-warm-up errors are also much worse despite modest overall in-sample gains. B01's sensor-range strata are small: n=10 for A, n=1 for C; A MAEs 0.232648 ridge /0.234599 persistence V and C 0.145235/0.073923 V. These do not support a robust favorable subgroup claim. All 1113 B04 eligible forecasts are context-unseen and the candidate loses overall. These unfavorable results are retained.

**Possible explanations, not established causes:** one global linear increment may transfer poorly across temperature trajectories, changes in speed/load and experiment-specific dynamics. The nearly constant warm-up RMS makes persistence particularly strong; a learned global correction can introduce bias there. Future speed/load changes are deliberately unknown at issuance. B04's near-half speed/dynamic measured-to-command ratios complicate physical interpretation. This task did not identify causal effects, damage onset, failures, healthy intervals or operating exposure. No post-result feature engineering or corrective multiplication was attempted.

## Replay, monitoring and notices

The loopback dashboard reveals one burst at a time with play/pause/step/reset. A/C observed RMS and settled ridge/persistence forecasts, continuous signed errors, measured/commanded speed/load, absolute T1/T2/room and the pending next-observed predictions are visible. Lines break across acquisition gaps. Warm-up rings, sensor-range markers, local flags and B04's global warning are distinct from forecast deviations. Quality fields remain available in event/provenance details and are never model inputs.

No deviation threshold was selected. The general description's **110 °C reference (p. 4)** appears as a separate temperature panel/reference notice at T1/T2 >=110 °C. It is not a run-specific stopping criterion, a certified safety alarm or a fault label. B01's termination discrepancy persists; B02's 0.65 V stop/continue condition is channel/statistic/crossing ambiguous; B04's stopping limit is unspecified. B04's 60 °C loading decision is not the 110 °C reference. No failure/RUL metrics are reported.

## Verification and later B03 evaluation

The acceptance suite checks future-data independence of the full emitted prefix, exclusion of next context/flags, experiment rejection before IO, training-only scaler/source-pair boundaries, fixed config/bin rules, common-pair metrics, missing inputs/targets, gap expiry including exactly 24 s, pending final forecasts, artifact reload, session isolation and local HTTP replay. Chromium exercised the actual dashboard at desktop/mobile sizes, step/play/pause/reset and a real B01 gap with no page errors. Independent audits reproduce MAE/RMSE and scaler parameters and verify ridge coefficients against augmented least squares. All 2616 development raw files match pre-existing SHA256 baselines. The synthetic workflow remains successful and clearly labelled synthetic. See project_status.md for final test count.

Concrete later milestone: retain both the frozen persistence benchmark and this unchanged unsuccessful ridge candidate for a transparent **one-shot B03 case study**, not an attempt to select a winning model. First obtain authorization to unseal. Add only a reviewed evaluation-only reserve entry point (the current CLIs deliberately reject B03); preserve the model artifact bytes and record reserve provenance separately. Independently/blindly apply predefined checksum/schema/channel/finite/sample-grid/duration/clock-order gates and review B03 log units, gain/calibration and CSV/MAT association. Do not use signal distributions to choose rescaling, exclusions or features. If essential measurement meaning is unresolved, report not evaluable. Then extract the already frozen descriptors once, using no fitted transformation except the saved B02 scaler; apply the same missing/gap/support/quality rules and report both frozen methods per channel with all counts. No refitting, normalization update, model selection or threshold adjustment based on B03. Preserve the complete results even if ridge loses. One held-out run supplies at most one laboratory case; dependent bursts cannot establish industrial fault detection, population generalization or RUL accuracy. Resolve B04 scaling through independent acquisition evidence in a separate investigation; do not use B03 to solve it.
