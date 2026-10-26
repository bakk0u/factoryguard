# Development release architecture

The active workflow is `python -m factoryguard.release`: existing streaming
`data/paderborn.py` and `pipelines/features_paderborn.py` validate/extract raw
bursts; `release/modeling.py` adds causal features and candidate Pipelines;
`release/campaign.py` performs frozen nested development evaluation;
`release/reporting.py` audits saved results without fitting. Ordinary development
I/O rejects B03. The dedicated future reserve entry point is separately gated,
hash-frozen and unexecuted on real reserve data.

`release/application.py` creates replay workspaces and a loopback HTTP API.
`release/store.py` uses SQLite tables for immutable observations, metadata,
cursors and derived events, with transactional steps and restart persistence.
`release/context.py` computes descriptive other-run bin references and separated
notice evidence. `release/dashboard.html` renders history, comparisons, events
and gaps. Portable export computes replay into a database clone and embeds its
events in a standalone HTML; it is not a live service or a future-access boundary.
The small attributed demo is package data under `release/demo/`.

Training code never receives B04/B03; only B01/B02 blocks are accepted. Pipelines
own learned transforms. Deployment artifact settings are separate from the
out-of-run artifacts used in development replay. Full ledgers and artifacts
remain local; compact results and demo are committed.

## Legacy placeholders and compatibility

Update: unused PLANNED-only modules, YAML files, empty tests and Docker/Compose
scaffolds listed historically below have now been removed after import checks.
The active notebook persists in release/store.py; release/investigation.py computes
causal descriptive windows. The dashboard exports period reports with user notes
separate from machine-generated evidence. Historical inventories below are records
of prior releases, not current file lists.

The older `api/`, `storage/`, `alerts/` scaffold modules and files marked PLANNED
are **not** used by the release. The actual API and SQLite implementation live
in `release/` as above. Legacy generic `pipelines/train.py`, `infer.py`,
`evaluate.py`, generic model bundle/fault metrics, notebooks, YAML configurations,
Docker/compose scaffolds and placeholder test modules are not active capabilities
or deployment instructions. They remain explicitly historical for compatibility;
empty placeholder test files do not contribute to the test count. Real tests
are discovered executable unittest cases. Use README release commands.

`run_step1.py` preserves the original synthetic validation/plot demo. Historical
forecast-v1 and selection-v2 CLIs remain usable; `dashboard/app.py` is their
compatibility launcher and now defaults to the v3 workspace. The primary v3
entry point is `factoryguard.release`. No external service is required.

## Historical project inventory

Implemented behavior is documented in README.md and docs/project_status.md.
The following inventory originated with milestone 1. New ingestion modules are
`data/archive.py`, `data/paderborn.py`, and `pipelines/inspect_paderborn.py`, with
`scripts/prepare_paderborn.py` for scoped acquisition. See dataset_assessment.md.
The feature milestone adds `features/b01.py`, `features/b01_plots.py` and
`pipelines/features_paderborn.py`, with acceptance tests in
`tests/test_b01_features.py`. See feature_definitions.md for formulas and roles.
The development extension adds `pipelines/assess_development.py` and
`tests/test_development_assessment.py`. Shared ingestion explicitly permits
B01/B02/B04 and rejects B03 waveform access. Comparison bins/feature formulas
are reused; per-experiment policy changes are documented in development_assessment.md.
Modules marked PLANNED remain placeholders, not working features.

```text
.env.example
.github/workflows/ci.yml
.gitignore
Dockerfile
README.md
artifacts/.gitkeep
compose.yaml
configs/alerts.yaml
configs/data.yaml
configs/features.yaml
configs/model.yaml
configs/monitoring.yaml
dashboard/api_client.py
dashboard/app.py
dashboard/charts.py
data/README.md
data/interim/.gitkeep
data/processed/.gitkeep
docs/data_contract.md
docs/demo_guide.md
docs/evaluation_protocol.md
docs/model_card.md
docs/problem_definition.md
notebooks/01_data_exploration.ipynb
notebooks/02_feature_exploration.ipynb
notebooks/03_error_analysis.ipynb
pyproject.toml
requirements.txt
run_step1.py
scripts/generate_demo_data.py
src/factoryguard/__init__.py
src/factoryguard/alerts/__init__.py
src/factoryguard/alerts/policy.py
src/factoryguard/alerts/state.py
src/factoryguard/api/__init__.py
src/factoryguard/api/app.py
src/factoryguard/api/routes.py
src/factoryguard/api/schemas.py
src/factoryguard/config.py
src/factoryguard/data/__init__.py
src/factoryguard/data/clean.py
src/factoryguard/data/ingest.py
src/factoryguard/data/replay.py
src/factoryguard/data/schema.py
src/factoryguard/data/split.py
src/factoryguard/data/validate.py
src/factoryguard/evaluation/__init__.py
src/factoryguard/evaluation/incidents.py
src/factoryguard/evaluation/metrics.py
src/factoryguard/evaluation/plots.py
src/factoryguard/evaluation/report.py
src/factoryguard/evaluation/thresholds.py
src/factoryguard/explanations/__init__.py
src/factoryguard/explanations/explain.py
src/factoryguard/features/__init__.py
src/factoryguard/features/build.py
src/factoryguard/features/preprocessing.py
src/factoryguard/logging_config.py
src/factoryguard/models/__init__.py
src/factoryguard/models/baseline.py
src/factoryguard/models/bundle.py
src/factoryguard/models/predict.py
src/factoryguard/models/train.py
src/factoryguard/monitoring/__init__.py
src/factoryguard/monitoring/data_quality.py
src/factoryguard/monitoring/drift.py
src/factoryguard/monitoring/service.py
src/factoryguard/pipelines/__init__.py
src/factoryguard/pipelines/evaluate.py
src/factoryguard/pipelines/infer.py
src/factoryguard/pipelines/prepare.py
src/factoryguard/pipelines/train.py
src/factoryguard/storage/__init__.py
src/factoryguard/storage/database.py
src/factoryguard/storage/repository.py
src/factoryguard/storage/schema.sql
tests/conftest.py
tests/test_alert_policy.py
tests/test_api.py
tests/test_features.py
tests/test_incident_metrics.py
tests/test_inference.py
tests/test_model_bundle.py
tests/test_preprocessing.py
tests/test_splits.py
tests/test_storage.py
tests/test_validation.py
```


## Implemented forecasting extension (forecast-v1)

Earlier inventory entries marked planned are historical. `models/forecast.py` implements the frozen two-output ridge/persistence core, training-only standardization, strict development-run guards, sequential replay and metrics. `pipelines/forecast.py` provides train/evaluate/replay/serve subcommands; `monitoring/dashboard.py` serves a loopback-only session API and bundled `dashboard.html`. `dashboard/app.py` forwards to that CLI. This is distinct from the still-planned production API, storage, fault-alert service and deployment scaffolds. JSON model artifacts and feature-table hashes support reload/reproducibility; no raw-waveform access is required during forecasting. See forecast_demo.md and forecast_review.md.


## Bounded selection-v2 extension

`models/selection.py` implements causal current/temporal features, independent replay blocks, finite gates, scikit-learn preprocessing/estimator pipelines, smoothing and fixed selection rules. `pipelines/select_forecast.py` executes only the predeclared inner grid/outer directions and writes every trial, artifact, coverage and source-row ledger; B04 loads only after selection. `evaluation/selection_report.py` renders saved results without fitting. `monitoring/selection_dashboard.py` exports/serves a self-contained selected-method replay. `dashboard/app.py` defaults to this selected replay while retaining explicit --artifact compatibility for forecast-v1. No source data is accessed by the dashboard; all B03 access remains denied.
