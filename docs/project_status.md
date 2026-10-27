# Current project status: development release v3

## Investigation application follow-up

The investigation-reliability branch now adds six-observation same-bin descriptive
change evidence (two consecutive windows of three), including RMS/thermal/context
deltas and retained warning counts. Windows reset at runs, gaps and bin changes;
missingness and insufficient history remain unavailable. References remain fixed
and versioned, never absorbing replay observations. B04 remains uncorrected.

Notebook notes are stored separately in SQLite, survive replay reset/restart, and
require explicit deletion. Users select revealed 1-based periods and export JSON
reports separating generated evidence from user notes, with context, provenance,
reference support, model settings and software version. Portable HTML supports
browser-local notes where file-origin storage is available; reports are portable
copies. Controls serialize step/reset/run-switch/notebook actions and show errors.
Unused PLANNED-only code/config/tests and empty Docker/Compose scaffolds were
removed after active-import checks. Historical scientific records are preserved.

Local complete suite: 115 tests passed, no skips/failures. Desktop/mobile browser
acceptance covers notes, report content, reload, reset, controls and layout; the
existing replay browser acceptance also passes. No real-data fits/search occurred.
All 377 B01 observations, issued forecasts and settled errors exactly match the
previous standalone release. A clean Git-index checkout installed as a wheel in
the separate pinned environment passed all 115 tests and pip check, then created
and exported its bundled demo without dataset access. Notebook/browser checks
also verify the report's period length and separate notes, reload persistence
and reset preservation. Screenshots are committed under docs/images/.
Raw data and B03 were not accessed. The user reports both Windows and Ubuntu passed
for ae41254 in run 40400560440; that result does not cover these later changes.
Remote API access still returns Forbidden, so final-commit CI needs verification
through the user's other integration. See investigation_workflow.md for screenshots
and usage. The prior release history follows.

Verified 2026-10-25. The complete-release request supersedes earlier milestone
scope/search limits. B03 remains completely sealed; B04 remains a separate
diagnostic stress case. Raw archives and all raw measurements remain outside Git.

Implemented: streaming development ingestion/validation/features; 32-configuration
frozen modeling campaign (persistence, smoothing, Ridge, Extra Trees, histogram
boosting and CPU XGBoost; direct/delta and current/enriched features); complete
trial/error/coverage reporting; final artifact; persistent SQLite replay and a
loopback API; responsive history/context/event dashboard; portable offline HTML;
319 kB attributed real-data demo; full reproduction CLI, pinned dependencies,
Linux/Windows CI configuration and derived review-bundle script. Legacy synthetic
demo remains intact; unused scaffolds are explicitly documented in architecture.md.

All **192 candidate-fold evaluations** completed with no fitting failures, plus
32 learned outer refits. The chosen final smoother needs no learned pooled fit.
Smoothing retains **12.83% macro MAE gain** over persistence in development
selection. Extra Trees enriched-delta gains 7.98%, histogram boosting current-delta
6.88%, XGBoost current-delta 4.17%; direct models and Ridge often lose. Every
configuration and per-run/channel MAE/RMSE is in results/release-v3/. No outcome-
driven search expansion, damage labels, alarms, RUL or fault-performance claims.

Final-source campaign reproduced in a fresh pinned environment: inner-trial,
development, stress and quality-stratum CSVs are **byte-identical** to the initial
campaign, with identical selection. This was one unchanged-grid reproducibility
run, not another tuning round. Both runs/audits remain in reports/local/release-v3
and reports/local/release-v3-reproduction. Independent audit verified all 192
fold scaler/dependency records, 72 artifact replays and primary metrics without
refitting. Exact evidence is committed with the compact results.

Local verification: **109 tests pass**, no failures/skips. Tests cover causal
features, split/preprocessing isolation, direct/delta definitions, serialization,
missingness, gap resets, SQLite restart/reset, API visibility, sparse reference
counts, gradual/abrupt synthetic changes and failed-family retention. Dedicated
reserve tests use generated files only. The synthetic CLI validates 1080 rows /
3 machines with no errors/warnings. Desktop/mobile Playwright acceptance passed
after fixing long-warning mobile overflow: step/play/pause/reset, six histories,
inspection slider, 372 B01 broad replay pairs, temperature reference, no external
requests. Package installation from the pinned environment and wheel succeeded.

Raw integrity check: all **380 B01 +1119 B02 +1117 B04 =2616 files** match their
recorded SHA256 values. B03 was not traversed, hashed, opened or evaluated.
Ordinary loaders still deny it. A hash-frozen plan and gated executable procedure
are prepared in configs/reserve_plan.json / release.holdout; the supplied
attestation is all false. Actual B03 execution remains unperformed and requires
later user approval after review. See review_handoff.md for the agenda and limits.

Local artifacts: reports/local/release-demo-final/dashboard.html (small demo),
reports/local/release-full/ (all development runs), and reports/local/reserve-plan-final/.
The source branch is development-release-v3. Clean-checkout and remote CI outcomes
are recorded in the completion note below after execution; no Windows pass is
inferred from merely adding its CI job. No public deployment or new data download.

## Completion verification

An exported clean Git-index checkout (no local reports, raw data or repository
virtual environment) was installed as a wheel into a separately created pinned
environment. All 109 tests passed there, pip check passed, and the bundled demo
and standalone export ran without dataset downloads. The unchanged-grid clean-
environment model reproduction produced byte-identical result CSVs. Git whitespace
checks pass; the attributed CSV retains its original CRLF bytes/hash explicitly.
The derived review ZIP contains 108 files, about 8.1 MB, with verified member
SHA256/CRC checks and no raw data. It remains ignored under reports/local/.

GitHub CLI authentication currently reports an invalid GH_TOKEN; therefore remote
CI execution cannot be claimed from that tool. Linux tests/browser workflow are
verified locally; Windows remains a configured CI target pending execution evidence.
This is an integration/verification limitation, not a claim that Windows failed.

## Historical project status: selection-v2

<!-- The following sections are retained historical evidence. -->

Verified 2026-10-23. Selection-v2 is complete: a predeclared small grid, fold-local preprocessing/estimator pipelines, causal temporal feature comparison, reciprocal B01→B02 and B02→B01 outer evaluations, full candidate/coverage reports, and an updated selected-method dashboard. **B03 stayed entirely sealed**. B04 was loaded only after method selection and used only for diagnostic stress predictions; its measurements are unchanged.

Direct inspection of the prior implementation/artifact established that forecast-v1 already standardized seven current inputs on B02 training-source mean/std and fitted a fixed alpha=10 Ridge increment model. It had no imputation, temporal features, clipping or prior tuning. This is recorded in [selection_protocol.md](selection_protocol.md). The current authorization supersedes the old no-search/B02-only constraints for this new milestone. Config and protocol hashes, grid, versions and split indices were saved before fitting. Prior outputs remain historical and reproducible.

The completed real-data budget was **18 configurations ×3 folds ×2 directions =108 candidate-fold evaluations**, including persistence and smoothing; 84 inner learned pipeline fits and eight outer refits, **92 learned pipeline fits total**. No trial failed, no search expansion occurred, and verification/report/dashboard work added no real-data fits. Generated-fixture tests exercise separate synthetic examples. Ridge includes its finite gate and StandardScaler inside each Pipeline; trees use a finite gate and independent A/C shallow trees. No imputation was required; unavailable values/history retain explicit reasons. Current regression inputs remain seven; the temporal variant has 14. Persistence/smoothing use only RMS. No quality/provenance fields become predictors.

**Selected family: exponential smoothing**, with **12.83% mean common-pair MAE improvement** over persistence across two runs/two channels, with improvement in all four cells. These results selected the method and are **development selection results, not unbiased final performance**. Inner B01 folds chose alpha=0.5; inner B02 folds chose alpha=0.2. Current Ridge has −19.76% macro MAE skill, temporal Ridge +1.33%, current trees −1.44%, temporal trees +1.91%; none qualify under the frozen consistency/simplicity rule. All grid settings, training diagnostics and unsuccessful outer methods remain reported.

| Evaluation / tuning run | Channel | Common n | Persistence MAE / RMSE V | Smoothing MAE / RMSE V |
| --- | --- | ---: | --- | --- |
| B01 / B02 (alpha=0.2) | A | 363 | 0.042879 / 0.078384 | 0.038399 / 0.073239 |
| B01 / B02 (alpha=0.2) | C | 363 | 0.028024 / 0.054088 | 0.024435 / 0.051420 |
| B02 / B01 (alpha=0.5) | A | 1110 | 0.026328 / 0.052718 | 0.022759 / 0.044271 |
| B02 / B01 (alpha=0.5) | C | 1110 | 0.019267 / 0.037871 | 0.016474 / 0.031348 |

Raw observations are retained: 377/1116/1114 for B01/B02/B04. Common pairs are 363/1110/1111; broad persistence/smoothing pairs are 372/1114/1113. Exclusive exclusions are 9/4/2 insufficient-history pairs, 4/1/0 expired gaps, and one final pending forecast per run. No actual nonfinite input/target exclusions or negative issued forecasts occurred. Warning rows are never quality-filtered. Common-history exclusions change small warning subsets, so both common and own-available quality strata are saved; the B01 C range-warning pair remains in broader coverage. Fixed bins and sparse/unseen warnings remain. Smoothing does lose in some subsets, including B01 unseen-bin A and B02 local-warning pairs; these limitations are reported without changing selection.

Executed outputs: **reports/local/selection-v2/** contains the pre-search manifest/frozen protocol/config, inner_search.json/inner_trials.csv, all-candidate summary, each direction's inner choices and `.joblib`/JSON artifacts, development/stress metrics and coverage, quality strata, every-row candidate forecast ledgers, comparison/train-validation/history plots, selection.json, proposed_final_config.json, standalone dashboard.html, screenshots, tests.log, package freeze and verification reports. Artifacts/derived data remain ignored by Git. [selection_results.md](selection_results.md) contains full tables; [model_selection_explained.md](model_selection_explained.md) explains scaling, features, regularization, hyperparameters, validation, overfitting, results and limitations. [selection_demo.md](selection_demo.md) gives all commands.

The dashboard now shows the selected smoothing forecast against persistence, with the correct outer-direction alpha/run labels, common-pair metrics, all available forecast histories, quality/provenance, gaps and separate temperature notices. Save/open `reports/local/selection-v2/dashboard.html` locally; it is self-contained and uses no network. The full replay is embedded; sequential reveal is a presentation control. `dashboard/app.py` defaults to serving this selected replay on loopback only; the old --artifact option retains the historical v1 UI. Localhost inside this cloud environment is not an external preview URL. No public tunnel/deployment was made.

Verification: **95 tests passed, zero failures/skips** (78 previous plus 14 selection and three selected-dashboard tests). Tests cover formulas/history, future-data independence, gap and run resets, disjoint split dependencies/purging, fold-scaler isolation, missing-value coverage, independent tree channels, artifact reload, frozen-grid bounds, equal-cell/consistency/tie rules, freeze-before-fit and B04-after-selection orchestration, and causal issue/settlement in the dashboard. Chromium checks passed desktop/mobile layout, play/pause/reset, selected settings for both directions, all 377 B01 observations/363 common pairs and B04 warnings, with zero network requests/page errors. Managed Chromium blocks file-URL navigation, so exact standalone HTML bytes were verified using setContent; direct file navigation was not tested here.

Independent verification audited all 108 candidate folds, training-source IDs, purged targets and fold-local means/scales; reloaded **24 artifact/run predictions**; recomputed primary scores and selection; and verified all **2616 B01/B02/B04 raw file SHA256s** against existing manifests. B03 files/logs/headers/checksums/features were not opened. No additional dataset downloads, raw edits, failure labels, classification metrics, SMOTE or damage alarms were introduced. scikit-learn was installed as a code dependency. The synthetic demo passed again (1080 rows /3 machines, no model), at reports/local/20261023T175135666284Z/. Dependency checks passed.

**Final configuration proposal:** exponential smoothing **alpha=0.5**, chosen by averaging already recorded B01/B02 inner objectives and applying the predeclared tie rule. It uses only A/C RMS, no fitted scaler/imputer/coefficients; initialize per channel from its first valid observation and reset across gaps/runs. No pooled final fit or B03 evaluation was executed. The 12.83% score belongs to the direction-specific selection procedure, not a single alpha=0.5 unbiased deployment estimate. Freeze release code/config/versions and the complete missing/gap/metric/coverage rules before a later separately authorized, blinded B03 validity pass and one-shot comparison with persistence. If essential measurement meaning is unresolved, report not evaluable without outcome-driven correction. No B03-informed tuning/refitting/reselection. One reserve run is one lab case study. Timing/association, few independent runs, warning-subset sparsity, termination ambiguity and B04 scaling continue to limit physical/generalization claims.

---

The following statuses are historical snapshots. Their no-search constraints, chosen methods, test counts and next milestones describe the prior tasks, not current selection-v2 behavior.

# Historical forecast-v1 status (superseded by selection-v2)

Verified 2026-10-23. FactoryGuard now has a reproducible **next-observed-burst A/C RMS forecasting prototype**, persistence benchmark, saved JSON scaler/model/config artifacts, experiment-separated evaluation, sequential replay and a loopback-only local dashboard. This is a laboratory measurement-forecasting prototype, not proven fault detection or RUL. The current user request explicitly authorized this milestone and supersedes earlier training prohibitions; **B03 remains sealed**.

Implemented modules: models/forecast.py, pipelines/forecast.py, monitoring/dashboard.py and packaged dashboard.html; dashboard/app.py is a launcher. Commands/configuration are in [forecast_demo.md](forecast_demo.md), the authoritative pre-fit amendment in [modeling_protocol.md](modeling_protocol.md), and full findings/limits in [forecast_review.md](forecast_review.md). AGENTS, dataset_roles.json, README, feature definitions, architecture, setup guide and model card now distinguish this implementation from older milestones and the still-planned production services.

B02 alone fits 1114 eligible training pairs and all learned preprocessing. B01 supplies 372 experiment-separated development-validation pairs; B04 supplies 1113 separately labelled as-recorded stress pairs with unresolved context interpretation. B04 is never pooled, corrected or used to fit the model. The single ridge delta model has fixed alpha=10 and seven current-burst inputs. No next-context/flags, clocks, IDs, warning fields or segments enter prediction. The fixed specification was documented before fitting; there was no search, post-validation refit or tuning.

**Measured result: ridge loses to persistence on B01 and B04.** B01 A MAE/RMSE is 0.061381/0.086234 V versus persistence 0.043027/0.078994 V; C is 0.037758/0.055316 V versus 0.028006/0.053918 V. Ridge's B01 MAE skill is −42.66% A and −34.82% C. Small B02 gains are optimistic training diagnostics only. Keep persistence as the demonstrated benchmark, not a claim that the candidate is better. All primary and warm-up/range/gap/support-stratified scores/counts are retained in the report and machine-readable outputs.

Executed demonstration: `reports/local/forecast-v1/` contains model/config/SHA256, evaluation CSV/JSON/forecast ledgers/PNG histories, B01 sequential events, desktop/mobile dashboard screenshots, browser verification, package freeze, tests.log and independent verification.json. All are ignored local outputs. Start without re-fitting:

```bash
.venv/bin/python -m factoryguard.pipelines.forecast serve \
  --artifact reports/local/forecast-v1/model/model.json --port 8765
```

The loopback dashboard is at `http://127.0.0.1:8765` **inside the server machine**; this is not an accessible cloud preview URL on the user's computer. `/health` confirms server readiness. A self-contained B01 HTML replay is now available at `reports/local/forecast-v1/dashboard-B01-offline.html`; save/open it locally without a server. It reuses the saved events and makes no network requests. See forecast_demo.md for the distinction and export command. Play/pause/step/reset reveal prefix history. It distinguishes forecast deviations, measured/commanded context, gaps, warm-up, sensor-range/local warnings, B04's global caveat and a separate documented general 110 °C temperature reference. It shows no deviation thresholds or fault probabilities. A forecast expires beyond 24 provisional CSV-clock seconds: B01/B02/B04 have 4/1/0 expired transitions and one final pending forecast each. No interpolation, waveform concatenation or silent dropping. Target intervals vary (median 18 s, eligible range 11–24 s across runs); this is not a fixed horizon or operating-time estimate.

Verification: **78 tests passed**, zero failures/skips (58 existing, 17 forecasting acceptance tests, three standalone-export tests). Coverage includes full-prefix future independence, exclusion of future context/flags, experiment separation and pre-IO held-out rejection, training-only scaler and boundary sources, common-pair metrics, missing inputs/targets, exact gap boundary/clock expiry, artifact reload, output protection, fixed support bins, session/reset isolation, HTTP replay and CLI train/evaluate/replay round trip with checksum refusal. Chromium checked actual desktop/mobile rendering, step, pending forecasts, real B01 gap, B04 warning and play/pause/reset; no page errors. Independent audits reproduced all primary metrics and scaler statistics, and coefficients matched an augmented-least-squares ridge reference. All **2616 B01/B02/B04 raw files** match pre-existing SHA256 manifests. B03 was not opened, revalidated, plotted or used for selection. No download occurred.

The unchanged synthetic demo passed again (1080 readings/three machines, validation errors/warnings empty, explicitly synthetic, model_trained=false); fresh output `reports/local/20261023T150801347396Z/` includes validated JSON and PNG. Dependency checks and compilation passed. Runtime uses the existing .venv and existing NumPy/pandas/Matplotlib/SciPy dependencies; exact executed versions are captured in environment.txt. No new Python dependency is required by the dashboard.

Unresolved limits: very few independent compatible runs; B01 influenced feature design; B02 has stop/continuation history; provisional ordinal waveform/CSV alignment and timestamp meaning/timezone; unobserved future operating changes; retained sensor-range warnings; B04 scaling/measurement meaning and unmatched loaded contexts; ambiguous endpoint definitions. No failure labels, healthy periods, damage onset, operating exposure, RUL, fitted alarm thresholds or deployment were introduced. Fault models, production API, SQL storage, certified alerts and external deployment remain planned scaffolds.

**Next milestone:** separately authorize a blinded predefined B03 measurement-validity pass, then a one-shot report of unchanged persistence and ridge artifacts under the frozen rules, with no model/feature/threshold selection or refitting. Add only a separately reviewed evaluation-only reserve entry point; current CLIs deliberately reject B03. Keep artifact bytes unchanged and record B03 provenance separately after authorization. If units/calibration/association cannot be established, report not evaluable instead of rescaling from distributions. One held-out run is one lab case study, not population validation. Investigate B04 context independently of B03 outcomes. No additional downloads are needed.

---

# Historical milestone snapshots (superseded status statements)

The snapshots below describe what had been implemented **at those earlier milestones**. Their “no training”, planned dashboard and “next milestone” statements are historical and superseded by the current authorized forecast-v1 status above; source measurement caveats and provenance remain valid.

# Project status

## B02/B04 development assessment: 2026-10-23

Completed [development_assessment.md](development_assessment.md) and the proposed [modeling_protocol.md](modeling_protocol.md). B02/B04 every-burst validation now covers required A/C/time variables, shapes, all-sample finiteness, full zero-based 128 kHz grids and 1.6 s durations, not just acquisition headers. All **1116 B02 and 1114 B04** recordings passed; 2230 feature rows were retained, with no missing candidate features or nominal ±50 g exceedances. Logs independently confirm raw V, 10 g/V and 0 dB gain. Absolute CSV/MAT association, timezone and start/end meaning remain provisional.

Final artifacts: `reports/local/development-assessment-20261023-final/`. Each B02/B04 subdirectory contains features/schema/integrity/extraction manifests, condition comparisons/counts, histories, assessment and recording diagnostics. The B01 feature table is reused unchanged; its new histories/diagnostics are in the final output's B01 subdirectory. Cross-run support, selected comparisons and all-feature summaries are at the output root. Reproduce with `.venv/bin/python -m factoryguard.pipelines.assess_development --output reports/local/development-assessment-new` and the documented plotting/cache settings. The module never downloads or accesses real B03 files.

Observed limits:

- B02 has 51 documented warm-up-setpoint rows and one 282 s gap after M0921, consistent in timing with the log's stop/continuation. The log changes an accelerometer RMS rule from two to four crossings of 0.65 V; the exact channel/statistic/reset logic and failure time are not established. No crossing labels were inferred.
- B04 has 50 warm-up-setpoint rows and no intervals >24 s. Its log selects a higher-temperature loading policy at 13:45; 160 earlier non-warm-up rows are explicitly policy-ambiguous. All source values remain retained. Combined local warnings: 53 B02 rows, 210 B04 rows, with categories overlapping.
- B04 loaded measured/commanded speed ratio is 0.49815–0.50030 (median 0.49921); dynamic peak/amplitude median is 0.51777, while static-load median ratio is 0.99672. Scaling, acquisition semantics or control behavior are hypotheses, not resolved causes. No multiplier is applied. A separate post-hoc quality companion flags B04 operating-context interpretation unresolved for every row; this is not an online/model input.
- Unchanged measured bins have four loaded B01/B02 matches with at least 20 observations each: counts 31/62, 28/108, 26/64 and 23/93. B04 has **zero loaded-bin overlap** with either run as recorded. This does not prove physical operating conditions never overlapped. B02 has 46 groups/28 sparse; B04 56/32 sparse. No bins were broadened or source fields rescaled.
- B04's stop log omits the numeric RMS limit/channel; its last timestamp is only minute-consistent with the completion note. No healthy periods, damage onset, failure labels or operating time were inferred.

Verification: **58 tests passed**, no failures/skips, including eight new development checks for explicit profiles, all-sample invalid-data rejection, B04 policy handling, future independence, fixed-bin absent support, held-out rejection before I/O, raw-output protection and combined-command roundoff handling. Independent first/middle/last numerical references for B02/B04 and full thermal/context/schema/count checks passed. All **2616 development raw files** (B01/B02/B04) matched SHA256 baselines, including the original acquisition manifests. Golden B01 features remain unchanged. The synthetic demo again succeeded (1080 readings / three machines; `reports/local/20261023T105112043682Z/`), dependency checks passed, and generated PNGs were verified. B03 source files, trends and features were not opened or revalidated.

The next modeling proposal is next-observed-burst RMS forecasting versus persistence: B02 fitting, B01 development validation, B04 a separate measurement/coverage stress case, and B03 a sealed final reserve only after protocol/validity rules freeze. This is a proposal, not executed training/evaluation. Current blockers are physical interpretation of B04 context, provisional clock association and endpoint semantics; mathematical ingestion/features are working. No normalization was fitted, no alarms tuned, and no model/target table created.

## Implemented

The synthetic milestone-1 workflow still loads sensor-history CSVs, validates the explicit demo contract, produces descriptive statistics and PNG plots, and rejects invalid inputs without silently repairing raw records. The bundled 1,080-row, three-machine dataset is synthetic and has no verified failure labels. `run_step1.py` remains independent of the real dataset.

Paderborn B01 ingestion is now implemented against the actual data and source documentation:

- Scoped acquisition of the description PDF and **B01.zip only**, verification against published sizes and MD5 checksums, and bounded, safe extraction outside Git.
- A dataset-specific loader for B01's actual MAT variables and CSV headers, with inventory, channel, shape, finite-value, sampling-grid, timestamp, and table-alignment checks. It preserves voltages and source timezone-naive times without cleaning or relabelling.
- Bounded-memory inspection of every recording, per-record descriptive statistics, a JSON inspection report, temperature/operating-condition/RMS overview, and representative voltage excerpts. CSV-to-MAT absolute timing is an explicitly unverified ordinal association.
- Meaningful generated-fixture tests for malformed data, raw-file preservation, lazy recording iteration, and extraction safety. No dataset binary fixtures are committed.

See [dataset_assessment.md](dataset_assessment.md) for source attribution, units, licence, actual schema, documentation discrepancies, commands, and limitations.

The minimal B01 feature milestone is also implemented. A streaming extractor writes one row per complete burst, with separate A/C mean-removed RMS, crest factor and excess kurtosis, temperature-above-room features, measured and commanded operating context, and explicit provenance/quality fields. Constant signals produce zero RMS and missing ratio/moment features with channel-specific flags. No data is clipped, interpolated, concatenated across bursts, or removed by a quality mask. Exact formulas and the biased central-moment excess-kurtosis estimator are in [feature_definitions.md](feature_definitions.md).

`schema.json` distinguishes eight feature descriptors, context, provenance and quality. It provides an explicit 11-column candidate allowlist (eight descriptors plus three measured operating quantities) and an empty default model-input list. Numeric IDs, timestamps, warning flags, segments and commanded setpoints are not automatically candidate inputs. Timestamp meaning and ordinal alignment remain provisional.

## Feature milestone verification: 2026-10-22

- Runnable command: `.venv/bin/python -m factoryguard.pipelines.features_paderborn /workspace/datasets/paderborn-10868257/raw/B01 --output reports/local/b01-features-new` with the headless plotting/cache settings below. Use a fresh output directory.
- Executed feature table: `reports/local/b01-features-v1/features.csv`, **377 rows**, 277,408 bytes. All measurement IDs and suspect bursts are retained. No candidate values are undefined in the actual B01 run; generated constant-signal tests verify missing-value behavior.
- Output includes `schema.json`, `raw_integrity.json`, `extraction.json`, `condition_counts.csv`, `condition_comparisons.png` and `condition_support.png`, all under the same ignored directory.
- The extractor retained 51 warm-up rows, 33 speed-setpoint warnings, four long-gap flags, 10 A-channel and one C-channel range-warning bursts. There are 96 combined-warning rows; categories overlap. Warnings do not establish invalid data or health labels.
- Fixed measured-condition bins produced 51 groups; 46 contain fewer than 20 bursts. The four plotted non-warm-up groups contain 31/28/26/23 bursts. All groups have counts and warning summaries; sparse comparisons are flagged. No feature calculation depends on binning or the future table used for offline plot selection.
- Runtime including plotting: **15.111 s**, with **149.02 MiB peak process RSS** on Linux. One waveform recording is processed/released at a time; only small descriptor tables and hash manifests are retained.
- All **380 source files** matched SHA256 hashes before and after extraction, and an independent post-run check matched the saved manifest again. Raw data remains outside Git.
- Full suite: **48 tests passed**, no failures or skips, including 18 new feature acceptance tests. These cover analytic values, constant signals, the specified kurtosis estimator, scaling/offset behavior, tiny varying signals, per-channel quality, gaps, raw preservation, lazy loading, role separation, and **future-data independence of all earlier row fields**.
- Independent checks confirmed the AC/DC RMS identity against the earlier inspection for all bursts, direct RMS/crest/SciPy-kurtosis values on M0001/M0189/M0377, warning totals, schema separation, condition-count totals, and both PNG files.
- The original synthetic CLI succeeded again: 1,080 readings across three machines, output `reports/local/20261022T205941306826Z/`. Dependency checks passed. No failure labels, fitted normalization, model training or model evaluation were introduced.

## Verification: 2026-10-22

The existing cloud `.venv` was used; SciPy was added for MAT ingestion. Python 3.12.14, NumPy 2.5.4, pandas 2.3.3, Matplotlib 3.11.2, and SciPy 1.18.1 were used. Dependencies remain ranges without a lockfile. Earlier environment verification passed the original 12 tests; the expanded suite and real-data results are recorded here.

- Zenodo record page returned HTTP 200; API and description PDF were accessible. The earlier proxy 403 blocker is resolved for these requests.
- Description PDF: 2,766,702 bytes, published MD5 matched.
- B01.zip: 965,866,495 bytes, published MD5 `5e82d9d98f21e4a03a06c43b87858c6b` matched. Safe extraction produced 381 members (377 MAT recordings, three root files, one directory), totalling 1,091,469,303 uncompressed bytes; member CRCs passed during extraction. No other experiment was downloaded.
- B01 inspection: all 377 recordings passed structural validation, with 204,800 samples per record and 77,209,600 samples per channel. Both CSVs contain 377 rows. The final run took 9.47 seconds and recorded 128.19 MiB peak process RSS on Linux, retaining one recording at a time.
- Final real-data outputs: `reports/local/paderborn-b01-verified/inspection.json`, `recording_statistics.csv`, `overview.png`, and `vibration_excerpts.png` (ignored local outputs).
- The unchanged synthetic CLI again processed 1,080 readings across three machines, writing `reports/local/20261022T182115005417Z/`.
- `.venv/bin/python -m unittest discover -s tests -v`: **30 tests passed**, no failures or skips (12 original tests, 13 B01 loader tests, five archive-safety tests). Initial malformed-MAT tests exposed an unhandled SciPy MatReadError; the loader now reports it as a validation error and the tests pass.
- Dependency check: no broken requirements. All 380 extracted files still matched original ZIP member sizes and CRCs after inspection; the final JSON report, 377 statistics rows, and both PNGs passed independent output checks. Approximately 28 GiB remained free.

Use `MPLBACKEND=Agg`, `MPLCONFIGDIR=/tmp/factoryguard-matplotlib`, and `XDG_CACHE_HOME=/tmp/factoryguard-cache` for writable headless plotting caches. Inspection used `OPENBLAS_NUM_THREADS=1` to avoid unnecessary thread overhead. Raw files and the archive remain outside the checkout at `/workspace/datasets/paderborn-10868257/`.

## Data-quality and interpretation limits

Structural validity does not establish physical suitability or label validity. Inspection found:

- CSV times span 2021-10-19 08:46:54–10:59:32, with no declared timezone. Median recording spacing is 18 seconds and the longest gap is 1,147 seconds. The report preserves gaps without filling or treating bursts as continuous sampling.
- Warm-up accounts for 51 rows at 750 rpm. Outside this warm-up, 33 set-speed values exceed the documented main-run interval; the maximum set speed is about 3,551.69 rpm versus a documented 3,000 rpm upper bound. Values are retained, not clipped.
- After the log's 10 g/V conversion, 3,719 A-channel samples and 19 C-channel samples exceed the sensor's nominal ±50 g range. This flags calibration/range investigation; it does not prove saturation or justify silently removing samples.
- The general description says B01 had no preset failure criterion. Its experiment log says a temperature threshold ended the experiment at 09:13, while CSV data continues until 10:59:32. No threshold-based failure time, RUL target, or per-record health label has been inferred.
- B01's actual headers differ from the general PDF, and the described precomputed-features CSV is absent. The observed archive drives the implemented loader.

## Planned placeholders and next milestone

The B01 feature review is now documented in [b01_feature_review.md](b01_feature_review.md), with independently recomputed features/flags/group counts and gap-preserving feature/context histories. The audit found no missing candidate values, one correctly flagged unknown initial gap, and no changes to B01 source files or feature artifacts. All 48 tests passed again.

The user authorized additional independent-run acquisition. Roles were declared before new signal inspection in [experiment_roles.md](experiment_roles.md) and configs/dataset_roles.json: B02 matched-condition development, B04 extended-condition development, and B03 a proposed held-out reserve restricted to integrity/structural checks. All three archives are now downloaded, published-size/MD5 verified and safely extracted: **7,033,411,088 compressed bytes**, **7,979,302,285 extracted bytes**. Existing B01.zip and the description PDF were reverified and reused, never redownloaded. See [additional_experiments.md](additional_experiments.md) for exact checksums, provenance, storage and limitations; the official record.json catalog is remote availability, not an incomplete local download manifest.

Structural checks passed for **1116 B02**, **614 B03** and **1114 B04** MAT headers, with matching CSV row counts, finite numeric CSV cells, unique increasing timestamps and exact cross-table alignment. MAT headers are double (204800,1) vectors for A/C/measTime. No new-run waveform values, trends, feature distributions or endpoint outcomes were inspected. B03 remains unexposed to exploratory/model-guiding analysis; all new-run calibration, actual MAT time grids/value quality and exact endpoints remain unvalidated. Final byte checks confirmed all **3,233 raw files across B01–B04** match original ZIP sizes/CRCs. The consolidated outside-Git ledger is `/workspace/datasets/paderborn-10868257/download_manifest.json`; approximately 15.8 GiB remained free.

The full suite now has **50 passing tests**, including acquisition safeguards for verified-file reuse and header-only held-out validation. Original B01 source/feature artifacts remain unchanged. No normalization fitting, alarm tuning, labels, or model work was performed.

Feature families beyond the documented minimal burst descriptors, preprocessing, dataset splitting, model training/inference, model bundles, explanations, predictive metrics, alerts, SQL storage, API, dashboard, monitoring, shared configuration, and deployment remain unimplemented scaffolds. The implemented feature extractor produces candidate descriptors, not a validated prediction system. No model has been trained or evaluated.

The next milestone is to investigate B01's timing, calibration/range and operating-condition discrepancies and review feature stability within the documented operating bins. Preserve the explicit warm-up/gap policy and per-channel warnings before considering additional feature families. Keep source measurement IDs and units, fit no transformations on future/test data, and do not infer future-available labels from postmortem defects. B01 is for ingestion and feature development only. Additional dataset downloads, model training, evaluation design execution, and predictive claims require a separately authorized milestone.


## Preview access correction, 2026-10-23

The earlier localhost address was incorrectly presented as if accessible from the user's browser. The cloud server is healthy but no preview forwarding capability is available in this environment. Implemented a standalone B01 HTML export from existing replay outputs, preserving all forecasts/flags and gap/pending behavior. Browser checks using the exact HTML bytes passed step/play/pause/reset, gap and full-run exhaustion with zero network requests/page errors. Managed Chromium blocks direct file-URL navigation; `setContent` was used, so direct local file navigation was not verified here. No external deployment, refitting, new evaluation, raw modification or B03 access. Three export acceptance tests cover experiment guards, no network adapter, template validation and script-safe embedding.

## Prepared reviewer website

Static reviewer snapshot added on investigation-reliability; unpublished pending
separate authorization. Includes B01/B02 and uncorrected diagnostic B04, no B03.
116 tests passed; 432 saved metric rows verified without fitting; 2,607 exported
observations/predictions match saved ledgers. Browser workflows pass. See
[reviewer site](reviewer_site.md) for build, provenance gaps and publication steps.
New final-commit Windows/Linux CI must be verified separately.
