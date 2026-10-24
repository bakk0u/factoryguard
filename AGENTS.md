# Working on FactoryGuard

## Scope and communication

- Work in small, reviewable milestones with a concrete outcome and acceptance checks. Finish the current milestone before expanding into modelling or services.
- Explain the problem, changes, results, and limitations in plain language. Distinguish implemented behavior from plans and assumptions.
- Read README.md and docs/ before changing behavior. Keep docs/project_status.md aligned with verified capabilities.
- Use the existing checkout: cloud tasks are already isolated. Do not create a Git worktree unless explicitly requested.

## Development and verification

Use the existing `.venv` Python from the repository root. For headless plotting in the cloud, set writable caches:

```bash
export XDG_CACHE_HOME=/tmp/factoryguard-cache
export MPLCONFIGDIR=/tmp/factoryguard-matplotlib
export MPLBACKEND=Agg
.venv/bin/python -m unittest discover -s tests -v
.venv/bin/python run_step1.py
```

- Write meaningful tests for new behavior and failure cases, including data boundaries and end-to-end outputs where relevant. Placeholder test modules do not count as tests.
- Verify the actual test count and exit status. Report failures, skips, and unrun checks honestly; do not weaken assertions to obtain a pass.
- Inspect the current run's validation.json, summary.json, and sensor_readings.png. Use fresh output directories so stale artifacts cannot mask failure.
- Preserve unrelated user changes. Never put credentials in code, logs, or documentation.

## Data integrity and leakage prevention

- Preserve raw data unchanged. Document source, licence, version, retrieval details, units, and checksums for imported data. Write transformations to separate derived outputs with traceable steps.
- Do not silently sort, drop, impute, relabel, or overwrite records. Make cleaning decisions explicit and test them.
- Use past-only features: every feature at prediction time must depend only on information already available then. Avoid future rows, centered windows, backward filling from the future, and future-derived aggregates. Explicitly define whether the current reading is available at the prediction instant.
- Choose chronological and machine/group-aware partitions appropriate to the intended deployment before fitting anything. Prevent overlapping feature/label windows from crossing partitions; apply a suitable gap when necessary.
- Fit imputers, scalers, feature selectors, and other learned transformations on training data only. Tune models and thresholds using validation data; reserve held-out test data for final evaluation.
- Define prediction time, label availability, and any prediction horizon explicitly. Never include target or post-failure information in features.

## Claims and next milestone

- Label synthetic data and results clearly in reports and explanations. The bundled demo has no verified failure labels; its injected trends do not establish predictive performance.
- Do not describe scaffolds as working features, anomaly scores as calibrated failure probabilities, or a model as trained until verified.
- The selected real dataset is Paderborn University Zenodo record 10868257. Read docs/dataset_assessment.md and docs/experiment_roles.md before changing its handling. The user authorized B02/B03/B04 acquisition in addition to existing B01. Roles are fixed in configs/dataset_roles.json: B01/B02/B04 are development; B03 is a proposed held-out reserve limited to integrity and structural checks. Never include B03 in exploratory plots, signal/feature distributions or model-guiding analysis. Do not download unselected experiments, train/evaluate models, invent failure labels, or fit normalization without a separately authorized milestone. Resolve timing, calibration, operating-range and termination ambiguities before predictive claims; the synthetic contract does not apply.
- Read docs/development_assessment.md and docs/modeling_protocol.md for B02's stop/continuation, B04's unresolved measured speed/load interpretation, and the proposal for future forecasting. Do not multiply B04's values to manufacture comparable operating bins. Use explicit development profiles and preserve candidate/quality/provenance roles; B03 waveform access is deliberately denied.

## Authorized forecasting prototype

The current forecast-v1 milestone explicitly authorizes B02-only fitting and preprocessing, B01 development validation, and a separately labelled as-recorded B04 stress evaluation. This supersedes earlier milestone-specific prohibitions on training. Follow the frozen amendment in docs/modeling_protocol.md and configs/forecast_v1.json. B03 remains sealed: no source, feature, signal or outcome access. Forecasts/deviations are not fault labels or RUL. Do not tune until a model wins.

## Authorized bounded selection milestone

The current user request authorizes selection-v2: B01/B02 reciprocal outer development evaluations and bounded expanding-window inner tuning under docs/selection_protocol.md and configs/selection_v2.json. This supersedes forecast-v1's no-search/B02-only scope for this new milestone. B04 is post-selection diagnostic only; B03 stays entirely sealed. Freeze the search before running it and retain unsuccessful trials. Propose, but do not execute, pooled final training or B03 evaluation.
