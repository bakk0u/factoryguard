# What selection-v2 learned, and how it avoids leakage

**Selected method: exponential smoothing.** Under the rule written before search, it improves common-pair MAE by **12.83% on average**, weighting B01/B02 and A/C equally. Every run/channel improves. These are development selection results: they chose the method and are **not unbiased final performance**. B03 stayed sealed. Better RMS forecasts do not establish better fault detection.

The initial audit, exact formulas, candidate list, budget and boundary rules are in [selection_protocol.md](selection_protocol.md). [selection_results.md](selection_results.md) reports every grid setting and outer candidate, including failures to improve. Runnable commands and artifacts are in [selection_demo.md](selection_demo.md).

## What was already implemented

Direct inspection found a seven-input Ridge correction to persistence: completed-current A/C RMS, T1/T2 above ambient and measured speed/static load/dynamic peak. The old code fitted B02 source-pair population means/stds and a training mean increment/intercept. It did not impute, clip, interpolate, build temporal histories, use quality/provenance as predictors or correct B04 scaling. Alpha=10 was fixed before fitting; the only saved model artifact confirmed that setting and 1114 training pairs. No prior grid/search was present in the inspected implementation, artifacts or recorded protocol.

Selection-v2 explicitly supersedes the earlier B02-only/no-search restriction. Existing forecast-v1 results are preserved. The new preprocessing and model are a **single scikit-learn Pipeline** for each learned candidate, newly fitted in every fold. Persistence and smoothing have no learned feature preprocessing. The dependency addition is scikit-learn; there were no additional dataset downloads.

## Scaling and undefined values

Ridge penalizes large coefficients. Without scaling, a one-unit change means radically different things for volts and rpm, so coefficient penalties depend on units. StandardScaler subtracts the **training fold** mean and divides by its population standard deviation. For example, the B02 full outer-training scaler has A-RMS mean about 0.1814 V and scale 0.1632 V; measured-speed mean about 2623.39 rpm and scale 435.80 rpm. Inner folds have their own different values, recorded in inner_search.json. No validation/evaluation values change them. Constant columns use scale 1. Trees partition values by thresholds and do not need input scaling; no scaler is fitted for them.

No imputation was needed for the verified current inputs. A finite-value gate is inside each learned pipeline. Undefined current/history features make that forecast unavailable, with an explicit exclusion reason; every record/flag is retained. Missing history is not filled with a future value or a shorter window. Source measurements and the B04 discrepancy are never clipped, interpolated or corrected. Missingness and quality flags remain reporting information, not automatic predictors. Original zero-variance crest/kurtosis values remain undefined with their existing flags; those descriptors are not model inputs. Zero RMS itself is finite and is retained as zero.

## Temporal features and smoothing

The 14-input temporal variant adds previous A/C RMS, current-minus-previous A/C RMS, and trailing-three-burst measured speed/static/dynamic means to the seven current inputs. It needs t−2,t−1,t within one segment. These are observation-index features, not rates per operating second. Histories reset at each experiment, gap >24 s and inner validation-block start. Two observations initialize the new temporal history before a common forecast pair is available.

Smoothing is simpler: each channel's state is `s_t = alpha × current_RMS + (1−alpha) × previous_state`; the next-observed forecast is `s_t`. At alpha=0.5, half the state comes from the current observation. A small alpha smooths more but can lag a change. Initialize from the first finite current RMS after a reset, without a fitted initial level; a missing channel RMS clears that channel's state. It receives **only A/C RMS**, not the seven regression inputs. Speed/load/temperature remain useful dashboard context and comparison metadata. Smoothing can forecast before the three-burst common-history requirement, so its broader coverage is reported separately.

All methods issue after the current burst completes. No next-burst speed, load, temperature, quality, arrival time or gap duration is input. Forecasts expire when the next CSV interval exceeds 24 s. The horizon is next observed burst, not a fixed 18 s; clocks and ordinal association are still provisional, and elapsed CSV time is not operating time.

## Regularization, hyperparameters and the bounded search

Persistence copies current RMS. Smoothing averages past observed RMS with decreasing weight. Ridge learns a linear correction to persistence; its regularization alpha shrinks coefficients to reduce sensitivity to limited data. A shallow regression tree splits current/history inputs into a small number of regions and predicts a mean RMS increment. A/C use independent trees so the larger channel cannot dominate split fitting.

Hyperparameters are settings chosen before a model fit: smoothing alpha, Ridge penalty, tree depth and minimum leaf size. Smoothing alpha and Ridge alpha have unrelated meanings despite sharing a name. The search was limited to 18 configurations, three chronological folds and two directions: 108 candidate-fold evaluations, 84 inner learned-pipeline fits and eight full outer-training refits. No deep learning, randomized search, extra grids, seed sweep or post-result feature changes. All trials completed successfully. Baselines are part of the 108 evaluations but require no learned fit.

Inner choices were:

| Outer training run | Smoothing alpha | Ridge current / temporal alpha | Tree current / temporal depth, leaf |
| --- | --- | --- | --- |
| B01 | 0.5 | 100 / 100 | 2,30 / 2,30 |
| B02 | 0.2 | 100 / 100 | 2,10 / 2,10 |

A setting within 0.01 of its group's best inner mean MAE ratio could yield to a simpler setting under the frozen ordering. For example, B01 current Ridge alpha=1 had ratio 0.966921; alpha=100 had 0.976525, within that tolerance, so stronger regularization was chosen. This rule was not invented after seeing the outcome.

## Chronological validation and overfitting

Inner training expands from 40% to 60% to 80% of the outer training run; the following 20% blocks are validation. At each boundary, the source pair whose next target enters validation is purged. Validation histories/smoothing restart, and their first two observations initialize the common feature window. Training's last target is before the boundary; validation's earliest input history starts at it. No additional calendar embargo is needed for this feature/target design. This eliminates record overlap, but does not make adjacent bursts statistically independent.

Hyperparameters chosen only inside B01 are then evaluated on B02, and vice versa. B04 was first loaded after selection.json was written; its two frozen-artifact diagnostics could not choose settings or method. Neither reversed run was randomly split. All learned methods fit the same common eligible training pairs, so feature variants do not gain extra training rows silently.

Overfitting means learning details that reduce training error but do not carry forward. For B01, the depth-4/leaf-10 temporal tree had training MAE ratio **0.815760**, but chronological-validation ratio **1.187116**—worse than persistence. For B02, current Ridge alpha=1 had training ratio **0.861440** but validation ratio **1.529718**; stronger alpha=100 changed those to **0.908272 / 1.030206**. Training error alone would favor misleading choices. Some train/validation differences also reflect changing operating/thermal histories; this experiment does not isolate the causal source of each gap. The plots retain every trial.

## Selection results and coverage

The primary selection score is mean MAE/persistence-MAE across the four outer run/channel cells. This prevents B02's greater number of bursts or A's larger amplitude from dominating. RMSE is reported separately, not substituted when convenient. Qualifying alternatives needed >=2% macro gain, no run-average loss and no individual channel loss >5%. Among qualified methods within 0.02 ratio points of the best, simpler wins. Otherwise persistence would have been selected.

| Method | Mean outer MAE improvement |
| --- | ---: |
| Persistence | 0.00% |
| **Exponential smoothing** | **12.83%** |
| Ridge, current | −19.76% |
| Ridge, temporal | +1.33% |
| Tree, current | −1.44% |
| Tree, temporal | +1.91% |

Temporal Ridge improved B02 but worsened B01; neither tree met the rule. These unsuccessful candidates are retained. Smoothing's selected-direction scores are:

| Evaluation run / tuning run | Channel | Common n | Persistence MAE / RMSE (V) | Smoothing MAE / RMSE (V) |
| --- | --- | ---: | --- | --- |
| B01 / B02, alpha=0.2 | A | 363 | 0.042879 / 0.078384 | 0.038399 / 0.073239 |
| B01 / B02, alpha=0.2 | C | 363 | 0.028024 / 0.054088 | 0.024435 / 0.051420 |
| B02 / B01, alpha=0.5 | A | 1110 | 0.026328 / 0.052718 | 0.022759 / 0.044271 |
| B02 / B01, alpha=0.5 | C | 1110 | 0.019267 / 0.037871 | 0.016474 / 0.031348 |

B01/B02/B04 retain 377/1116/1114 observations. Common pairs are 363/1110/1111; broader persistence and smoothing cover 372/1114/1113 per channel. Exclusive exclusions are respectively 9/4/2 insufficient-history pairs, 4/1/0 expired gaps and one pending last forecast per run. There are no nonfinite exclusions or negative issued forecasts in these actual outputs. Generated tests cover missing-feature behavior. All methods use the same common masks; own-available results never substitute for them in selection.

Warnings are not removed. B01's common A range-warning subset contains seven pairs; its common C subset is empty because the relevant pair lacks initialized history. Broader coverage retains ten A and one C range-warning pairs, explicitly reported. Gap-adjacent sources are likewise absent from common-history scoring but retained in broader coverage. These are availability exclusions, not a finding that measurements are safe or healthy.

Benefits are not uniform. B01's unseen-bin subset (n=73 common pairs) has smoothing A MAE **0.014239 V versus persistence 0.010832 V**; C is 0.007028 versus 0.006991 V. B02's local-warning subset (n=50) also loses on both channels. Fixed 250 rpm/250 N/250 N bins, warm-up separation and >=20 occupancy support are unchanged; they are reporting strata only. All B04 common contexts are unseen relative to either tuning run. B04 smoothing diagnostics improve RMS forecast error, but its unresolved context scaling still prohibits matched-physical-condition claims. No B04 outcome alters selection.

## Proposed final configuration and reserve evaluation

The selected family is smoothing. Equal averaging of its already recorded B01/B02 inner objectives chooses **alpha=0.5** as the final proposal (ratios 0.934013 for 0.8, 0.864405 for 0.5, 0.860781 for 0.2; 0.5 is within the frozen 0.01 tie tolerance and simpler in the declared order). There are no regression coefficients, scaler or imputer to fit for this method. Initialize each channel from its first valid observation and reset at gaps/experiment boundaries. The 12.83% selection result belongs to the procedure with direction-specific alphas; it is **not** an unbiased estimate of a single frozen alpha=0.5 deployment.

`proposed_final_config.json` records this proposal; no combined-development final fit or B03 evaluation was executed. Before a later B03 task, freeze the release config/code/dependencies and obtain separate authorization for a blinded measurement-validity pass: units/gain/calibration, channels, finite samples, exact grids/durations, inventory/time order and association caveats. Do not inspect trends to pick a conversion, feature, exclusion rule or method. Unresolved essential measurement meaning means not evaluable. Then replay once using frozen smoothing and persistence, reset state, retain quality warnings, and report common plus broad coverage, per-channel MAE/RMSE and unsupported conditions. No B03 updates, method reselection or alarm tuning. One reserve bearing supports one laboratory case study, not population fault-detection or RUL claims.
