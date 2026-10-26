# FactoryGuard

A local **offline bearing-measurement monitoring application**. Follow vibration,
temperature and operating conditions, compare completed observations with relevant
development history, and inspect next-observed-burst RMS forecasts and deviations.
It does not establish bearing health, fault-detection accuracy or remaining life.

The development release integrates streaming ingestion, validated burst features,
a recorded model campaign, SQLite replay history, a loopback API, a responsive
dashboard and portable HTML export. **B03 remains sealed.** B04 is a separate
diagnostic case with unresolved speed/load interpretation.

## Run the small demo — no dataset download

The [investigation workflow](docs/investigation_workflow.md) adds same-condition
change windows, local notes retained across resets, and selected-period JSON
reports. Experiments are separate bearing runs; A/C are vibration channels.

Use CPython **3.12** for the pinned environment. From a clone of this branch:

```bash
python -m venv .venv
# Linux: source .venv/bin/activate
# Windows PowerShell: .venv\Scripts\Activate.ps1
python -m pip install -r requirements-lock.txt
python -m pip install --no-deps -e .
python -m factoryguard.release demo --output reports/local/demo
python -m factoryguard.release serve --workspace reports/local/demo --port 8765
```

Open **http://127.0.0.1:8765 on the same machine**. Play, pause or step through
observations; inspect context, warnings and reference counts. SQLite preserves
progress across restarts. This is recorded-data replay, not a live sensor service.

Without a server or cloud port forwarding:

```bash
python -m factoryguard.release export --workspace reports/local/demo --output reports/local/demo/dashboard.html
```

Download/save that HTML and open it locally. The full prerecorded replay is
embedded; no CDN/API is needed and reveal controls are a presentation feature.
HTML does not persist progress. Output directories/files must be fresh.

The bundled real-data demo is **319 kB**: all 377 B01 feature rows with flags and
provenance, B02 reference-bin summaries and the B02-selected smoothing rule.
Source: Osarenren Kennedy Aimiyekagbon, Paderborn University,
[Zenodo DOI 10.5281/zenodo.10868257](https://doi.org/10.5281/zenodo.10868257),
CC BY 4.0. [Attribution and changes](src/factoryguard/release/demo/ATTRIBUTION.md).
No raw vibration recordings are bundled. The legacy `python run_step1.py`
demonstration remains available and is explicitly **synthetic**.

## What the results establish

32 frozen configurations compare persistence, smoothing, Ridge, Extra Trees,
histogram gradient boosting and CPU XGBoost; direct/increment targets and current/
history features. All 192 inner candidate-fold evaluations completed.
**Smoothing remains selected**, with 12.83% equal-run/channel MAE improvement over
persistence on B01/B02 development comparisons. Final alpha is .5;
direction-specific evaluation settings are retained in the dashboard.
These are selection results, not unbiased final performance or fault detection.

- [All model comparisons and per-channel results](docs/results/release-v3/results.md)
- [Frozen campaign and supported decisions](docs/release_protocol.md)
- [Setup, reproduction and release bundles](docs/development_release.md)
- [Model card and limitations](docs/model_card.md)
- [Review agenda and prepared B03 procedure](docs/review_handoff.md)
- [Verification and status](docs/project_status.md)

## Full-data reproduction

Raw B01/B02/B04 must already exist outside Git. Nothing below downloads data.
Set `FACTORYGUARD_RAW_ROOT` to the dataset directory for custom storage; this
also protects it from application output writes. Quote paths with spaces.

```bash
python -m pip install -r requirements-campaign.txt
python -m factoryguard.release extract --raw-root /path/to/dataset/raw --output reports/local/features
python -m factoryguard.release campaign --config reports/local/features/release_v3.json --output reports/local/campaign
python -m factoryguard.release audit --results reports/local/campaign
python -m factoryguard.release report --results reports/local/campaign --output reports/local/campaign/report
python -m factoryguard.release prepare --results reports/local/campaign --output reports/local/full-demo
python -m factoryguard.release serve --workspace reports/local/full-demo --port 8765
```

Extraction processes one burst at a time, validates all samples and checks raw
hashes before/after. Existing verified tables can instead be specified in a copy
of configs/release_v3.json; change only the three paths. No B03 access, scaling
correction, new labels or additional downloads occur.

## Verification

```bash
python -m pip install -r requirements-campaign.txt
python -m unittest discover -s tests -v
python -m pip check
python run_step1.py --output reports/local/synthetic-check
```

CI targets CPython 3.12 on Linux and Windows; executed results are recorded
separately in project status. [Architecture](docs/architecture.md) distinguishes
active components from legacy placeholders. Raw archives, SQLite workspaces,
fitted artifacts, full ledgers and generated dashboards stay outside Git.
No public deployment is made.
