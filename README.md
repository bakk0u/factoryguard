# FactoryGuard
A PyCharm-ready industrial sensor monitoring project.

**Implemented:** synthetic CSV ingestion/validation/plots; verified Paderborn development ingestion and burst features; next-observed-burst RMS forecasting versus persistence; saved artifacts, experiment-separated evaluation, sequential replay and a local dashboard.
**Scaffolded only:** fault/RUL models, alert thresholds, SQL, external API and deployment. Forecast deviations are not proven faults.

The bounded selection-v2 milestone selects **exponential smoothing**, with 12.83% mean MAE improvement over persistence across two development runs and two channels. These are **selection results, not unbiased final performance**. B03 remains sealed; B04 is post-selection stress only. See the [educational report](docs/model_selection_explained.md), [all candidate results](docs/selection_results.md), and [commands / selected dashboard](docs/selection_demo.md). The older forecast-v1 Ridge losses remain documented in forecast_review.md.

## Quick start
Open this folder in PyCharm with a Python 3.10+ virtual environment, then:

```bash
python -m pip install -e .
python run_step1.py
python -m unittest discover -s tests -v
```
You can also right-click `run_step1.py` and Run. Results are saved in the printed
`reports/local/<timestamp>` folder. A verified example is in `reports/example`.

The bundled 1080-row dataset is **synthetic**, not real industrial data.
The synthetic demo trains no model and makes no predictive-performance claim.

## Your CSV
```bash
python run_step1.py --input data/raw/your_readings.csv
```
Follow `docs/data_contract.md`. Invalid records cause a nonzero exit status and
a validation.json report; they are not silently repaired. Sampling gaps are warnings.
Explicit `--output` directories must be new or empty to avoid stale results.

## Reading order
Start with run_step1.py, then src/factoryguard/pipelines/prepare.py,
data/ingest.py, data/schema.py, data/validate.py and evaluation/plots.py.
See docs/architecture.md for the full file inventory and docs/demo_guide.md for setup.

## Real dataset: Paderborn B01
See [dataset assessment](docs/dataset_assessment.md) for source terms, observed
schema, documentation discrepancies, checksums, local paths, and runnable commands.
The initial B01 workflow is fully downloaded and inspected. A separately
authorized B02/B03/B04 acquisition is governed by [experiment roles](docs/experiment_roles.md);
B03 is a held-out reserve restricted to integrity and structure. Archives and raw measurements stay
outside Git. The current selection-v2 authorization uses reciprocal B01/B02 outer development evaluations and strictly inner chronological tuning. The synthetic demo remains independent.

The three additional archives are checksum-verified and structurally checked;
see [acquisition report](docs/additional_experiments.md). No new-run waveform
trends were inspected during that acquisition. B02/B04 have since received
[full development validation and assessment](docs/development_assessment.md);
B03 remains sealed. The [B01 review](docs/b01_feature_review.md)
contains independent feature verification and quality-aware histories.

For feature extraction commands, exact formulas, estimator conventions and
column roles, see [feature definitions](docs/feature_definitions.md). The
extractor retains all 377 bursts and separates candidate inputs from quality
and provenance fields. Generated tables and plots stay in `reports/local/`.

## Forecasting and replay
Follow [selection_demo.md](docs/selection_demo.md) for the bounded search, full reports and self-contained selected-method replay. The [pre-search protocol](docs/selection_protocol.md) specifies pipeline isolation, temporal features, purging, coverage and selection. Save/open reports/local/selection-v2/dashboard.html locally; cloud localhost is not an external preview URL. The original forecast-v1 CLI remains available for reproducing historical results.

## Next milestone
Freeze the proposed smoothing alpha=0.5 release and its measurement-validity/coverage rules before a separately authorized, blinded B03 validity pass and one-shot reserve evaluation. The proposed final configuration has not been executed on B03. No further dataset downloads are needed.

## Verification environment
Current verification details are in [project status](docs/project_status.md).
Dependency ranges are declared, not a platform-specific lockfile.
