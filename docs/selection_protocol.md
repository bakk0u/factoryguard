# Bounded preprocessing and model selection: selection-v2

Historical reproducibility document. The current complete development release
uses release_protocol.md and configs/release_v3.json; its broader frozen campaign
supersedes this milestone's budgets and proposal-only final fit limit. B03 stays
sealed. Earlier results below remain the original selection-v2 evidence.

## Inspected starting point (before search)

Directly inspected `models/forecast.py`, `pipelines/forecast.py`, configs/forecast_v1.json, the recorded protocol, and the actual reports/local/forecast-v1/model/model.json artifact. There is one model.json under the local reports tree. The existing estimator is a handwritten two-output ridge correction to persistence: predict next RMS minus current RMS, then add current RMS back. Its seven inputs, in order, are current A RMS, C RMS, T1 minus ambient, T2 minus ambient, measured speed, measured static load and measured dynamic peak. All become available after the completed current 1.6 s burst, conditional on provisional ordinal CSV/MAT association. It does not use next-burst context, commands, IDs, timestamps, warnings, crest/kurtosis or temporal history.

Existing learned preprocessing is population mean/std standardization on eligible B02 training-pair sources; constant scale becomes 1. Target increments are centered by their training mean, giving an unpenalized intercept; there is no target scaling. It has no imputation, feature selection, clipping, gap interpolation or B04 scaling correction. Nonfinite inputs yield unavailable ridge forecasts; invalid training pairs are explicitly excluded. Raw burst mean-removal and temperature-minus-ambient are deterministic feature definitions, not cross-record fitted preprocessing. Quality/provenance metadata is retained outside the input allowlist.

The actual artifact records 1114 B02 training pairs, alpha=10, and seven fitted means/scales. The code's config validator rejects other alpha values. Alpha 10 was a fixed design choice documented before that fit, not a validation optimum. Code, artifacts and recorded execution evidence show no earlier tuning/search. This audit is bounded to the available repository/artifacts; it is not a claim about unrecorded external work.

## Authorization and freeze

The current user request authorizes this bounded search and supersedes forecast-v1's B02-only/no-search constraints for **selection-v2 only**. Old artifacts/results remain historical. B03 stays sealed: no raw, header, log, feature, checksum or signal access. B04 is diagnostic only. No new downloads or raw edits. The search entry point writes the exact config, protocol text, their SHA256s, source-table hashes and split ledger **before fitting**. This document and configs/selection_v2.json are fixed before search outcomes are inspected.

## Features and target timing

Current set: the same seven inputs above. Temporal set: those seven plus previous A/C RMS (2), current minus previous A/C RMS (2), and trailing-three-burst arithmetic means of measured speed/static load/dynamic peak (3): **14 inputs** total. These are observation-index changes/means, not per-second rates. No target interval, next context or future flags enter inputs. Three completed bursts including the current one are required, all in the same acquisition segment. The means include t−2,t−1,t; lag/change use t−1,t. No learned feature selection. All raw values, range flags and warm-up regimes remain retained.

History resets at each experiment, every CSV interval >24 s, and the beginning of each independently replayed inner validation block. The first two observations after reset lack temporal readiness; no partial-window substitute. Nonfinite historical inputs make the affected temporal descriptors unavailable; no filling/interpolation. Exponential smoothing updates each channel after the current observation: s_t = alpha*x_t + (1−alpha)*s_(t−1), forecast next=s_t. Initialize at the first finite RMS after reset; a missing RMS clears that channel's state, and the next finite RMS reinitializes it. It uses all previous observations since reset with exponentially decreasing weight; it never carries state across a split boundary, gap or experiment.

Forecast next **observed** RMS after the current burst completes. On arrival, score only 0 < CSV interval <=24 s; otherwise expire the forecast and reset history. The last forecast remains pending. Timestamp meaning/timezone and ordinal association remain provisional; this is neither a fixed-time horizon nor operating time.

## Pipeline, missingness and candidates

Use one scikit-learn Pipeline for each learned candidate: finite-input gate → StandardScaler → Ridge, or finite-input gate → two independent shallow DecisionTreeRegressors (one per channel, in MultiOutputRegressor). Trees do not require input scaling. Both learned methods predict the two RMS increments and add the current channel RMS back. Independent trees prevent the larger-amplitude channel from dominating shared split decisions. No output clipping.

No imputation is planned: the current seven inputs are finite in the verified development tables, and missing history is a defined availability constraint. The finite gate rejects nonfinite fit/predict batches; the caller preserves every row and its explicit availability reason, supplying only valid rows to a pipeline. Missingness remains in the ledger/quality fields, not as an automatic predictor. If future data is missing, return unavailable predictions rather than fit an unplanned imputer. This is a deliberate complete-feature policy, with its coverage cost reported. StandardScaler is fit anew on each training fold's candidate source features only; no statistics from validation/outer evaluation/B04 enter a fit.

One small grid, no randomized search:

| Group | Settings in predeclared simplicity order | Configurations |
| --- | --- | ---: |
| Persistence | next=current; no fit | 1 |
| Exponential smoothing | alpha 0.8, 0.5, 0.2 | 3 |
| Ridge current | alpha 100, 10, 1 | 3 |
| Ridge temporal | alpha 100, 10, 1 | 3 |
| Tree current | depth/leaf: 2/30, 2/10, 4/30, 4/10; seed 42 | 4 |
| Tree temporal | same tree grid | 4 |

18 configurations ×3 inner folds ×2 directions = **108 candidate-fold evaluations**, including baselines. 84 of these fit learned pipelines; eight further learned pipelines refit the inner-selected settings on the full outer-training run (four groups ×two directions). No additional settings, seed repetitions or outcome-driven search expansion. Every inner trial is reported. Only each group's inner-selected settings proceed to outer evaluation; do not expose every grid setting to outer-based hyperparameter choice. Each two-output tree pipeline fits two small trees, explicitly part of this budget.

## Splits, purging and training coverage

Outer directions: B01→B02 and B02→B01. For an outer training run of N observations, inner folds have train prefix [0,floor(0.4N)), validation [floor(0.4N),floor(0.6N)); then 0.6/0.8; then 0.8/1.0. No shuffle. Train features/targets both lie in the train prefix. Drop the source pair at index boundary−1 because its target is the first validation observation. Validation targets must lie within that validation block; its last observation is pending, not scored. Record these boundary pair exclusions explicitly.

Each validation block starts fresh history/smoothing state. Common scoring begins only after its first two observations, so its earliest feature dependencies are at/after the boundary. Training's last permissible target is boundary−1, while validation's earliest temporal dependencies start at boundary. **No additional time embargo is needed for this design**: the target-crossing pair is purged and two observations initialize the new history, leaving raw-record dependencies disjoint. Reusing training-tail history would be a different protocol and is deliberately not implemented. Correlation can persist despite this separation; no claim of independent bursts.

For fair training comparisons, learned current/temporal pipelines both fit on the same valid temporal-ready training pairs (the intersection). Baselines do not fit. This sacrifices a few current-only training rows transparently. All methods are scored on identical common pairs, requiring three valid source-history observations, finite current/temporal inputs and both finite target RMS values, and no target gap. Do not drop quality-warning rows. Also report broad persistence coverage per channel (finite current/target RMS and no target gap), every method's own available coverage, common coverage and mutually exclusive exclusion reasons. All observations are preserved in forecast ledgers, including expired and final pending rows.

## Inner tuning and outer method selection

Inner objective: arithmetic mean of per-channel MAE/persistence-MAE ratios over channels and the three validation folds, equal weight to each fold/channel. Both methods use identical common pairs. A zero persistence MAE yields ratio 1 if candidate MAE is also zero, otherwise infinity; an empty cell invalidates the candidate objective (never silently omit it). Choose the simplest grid setting within **0.01** of the group's best mean ratio, using grid order above. This choice reads only that outer training run. Record training resubstitution and validation MAE/RMSE for every trial to expose overfitting.

Outer aggregation: mean of the four ratios (two runs ×two channels), giving each run/channel equal weight regardless of burst count/amplitude. Report raw per-run/channel MAE/RMSE, persistence-relative skill and counts as well. RMSE is secondary reporting, not a secretly substituted tuning objective. For a non-persistence method to qualify, its macro MAE ratio must be <=0.98 (at least 2% gain), each run's mean channel ratio <=1.0, and no individual run/channel ratio >1.05. Among qualifying methods, choose the simplest within 0.02 of the best macro ratio. Simplicity order: persistence, smoothing, Ridge current, Ridge temporal, tree current, tree temporal. If none qualify, select persistence. Tolerances are pragmatic predeclared preferences, not significance tests.

The two outer runs **are development selection results**, not unbiased final performance, because they now select the method and both informed design. Do not tune until a method wins. B04 cannot affect tuning/selection: load and predict it only after selection is written, using each frozen outer-fit candidate separately and labelling both stress results by training run. No measured scaling correction or broader support bins. Show quality/support strata as diagnostics; do not select favorable subgroups.

## Final-training proposal and B03 reserve

After selecting a group, propose its final hyperparameter using the mean of its already recorded inner objectives across B01 and B02, with the same 0.01 simplicity tie rule; do not use per-setting outer/B04 results. Proposed final fit would combine eligible B01/B02 training pairs, retain run resets, and learn preprocessing on that combined development pool only. **Do not execute that pooled final fit in this milestone**; save the proposed config. Persistence needs no learned fit; smoothing still needs per-run state initialization. The dashboard uses saved outer-direction predictions, so its B01/B02 curves remain out-of-run development results; B04 display uses the B02-trained stress artifact, clearly labelled.

Before B03 is opened in a later separately authorized task, freeze chosen method/settings, feature and missing policies, pipeline/version hashes, training runs, gap/state rules, coverage/metrics and the blind measurement-validity gate. Review units/calibration and acquisition meaning independently without signal-distribution-driven corrections. Require documented channels, real finite samples, exact 128 kHz grids/1.6 s durations, inventories, unique increasing CSV time and explicit provisional association. Retain range warnings; structural/meaning failures make affected data/run unevaluable under predefined rules, not grounds for choosing a new model. Train the proposed final artifact before any B03 outcome access, then evaluate once with frozen rules and persistence on common and broad coverage. No updates/refits/threshold selection from B03. One reserve run gives one lab case study, not population evidence or fault/RUL validation. No SMOTE, classification metrics, damage alarms or failure labels.
