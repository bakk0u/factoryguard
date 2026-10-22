# FactoryGuard — milestone 1
A PyCharm-ready industrial sensor monitoring project.

**Implemented:** CSV ingestion, explicit sensor contract, validation, summary
statistics, sensor-history plots, CLI, synthetic demo generator and unit/integration tests.
**Scaffolded only:** feature engineering, model training, alerts, SQL, API,
dashboard, monitoring and deployment. Their files explicitly say PLANNED.

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
No model is trained and no predictive performance is claimed.

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

## Next milestone
Choose a documented real sensor-history dataset, revise the contract to match its
units and labels, explore it, and design a leakage-safe split before training.

## Verification environment
Executed with Python in the build environment, pandas 2.2.3, NumPy 2.3.5 and
Matplotlib 3.10.8. Dependency ranges are declared, not a platform-specific lockfile.
