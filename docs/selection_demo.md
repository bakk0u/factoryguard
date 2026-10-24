# Reproduce selection-v2 and open the selected dashboard

Use the existing checkout and .venv. The feature tables must already exist at the paths in configs/selection_v2.json. No dataset download or raw access is needed for search, reporting or dashboard export. B03 paths are rejected; B04 is diagnostic only. The new dependency is scikit-learn (the executed version is recorded with the frozen manifest and package freeze).

```bash
cd /workspace/factoryguard
export XDG_CACHE_HOME=/tmp/factoryguard-cache
export MPLCONFIGDIR=/tmp/factoryguard-matplotlib
export MPLBACKEND=Agg
export OPENBLAS_NUM_THREADS=1
.venv/bin/python -m pip install -e .
.venv/bin/python -m unittest discover -s tests -v

# Fresh output directory; the completed run is reports/local/selection-v2.
.venv/bin/python -m factoryguard.pipelines.select_forecast \
  --config configs/selection_v2.json --output reports/local/selection-v2-reproduction
.venv/bin/python -m factoryguard.evaluation.selection_report \
  --results reports/local/selection-v2-reproduction
.venv/bin/python -m factoryguard.monitoring.selection_dashboard export \
  --results reports/local/selection-v2-reproduction \
  --output reports/local/selection-v2-reproduction/dashboard.html
```

Save/download **reports/local/selection-v2/dashboard.html** and open it in a browser for the already completed demonstration. It is self-contained, with no network requests: B01/B02 out-of-run development selection replays and a separately labelled B04 stress replay. The whole precomputed replay is embedded; sequential reveal is a presentation control, not an access boundary. It does not fit or recalculate forecasts. B01 displays alpha=0.2 selected within B02; B02 displays alpha=0.5 selected within B01; B04 displays the fixed B02-tuned alpha=0.2 stress replay. The proposed final alpha=0.5 is not misrepresented as the source of every displayed forecast.

The dashboard shows selected/persistence forecasts, signed deviations, context, gaps, warm-up and sensor-range warnings, and the separate documented temperature reference. The common-pair counter/metrics use the exact selection mask; plots retain all available forecasts, including initialization rows outside that mask. All flags remain in provenance details. No fault/damage alarms or RUL are presented.

Optional same-machine serving:

```bash
.venv/bin/python -m factoryguard.monitoring.selection_dashboard serve \
  --html reports/local/selection-v2/dashboard.html --port 8765
```

`http://127.0.0.1:8765` is reachable **on the server machine**, not automatically from a browser outside this cloud environment. There is no preview-port tool available here. Use the self-contained HTML for access without port forwarding; no public deployment or tunnel was made. Managed Chromium blocks direct file-URL navigation, so browser checks load the exact HTML bytes with Playwright setContent and verify that no network requests occur. Health route is `/health`.

Outputs include:

- `pre_search_manifest.json`, frozen config/protocol, source hashes, versions and split/purge ledger, written before fitting.
- `inner_search.json` and `inner_trials.csv`: every setting/fold's training and chronological-validation results, exclusions, source IDs and scaler statistics. `all_candidate_summary.csv` and inner_train_validation.png summarize all 18 configurations.
- `B01_inner_choices.json`, `B02_inner_choices.json`: settings fixed using only that training run, before outer predictions. Local `.joblib` artifacts contain fitted pipelines (or baseline settings) and source metadata; inspectable companion JSON includes input names and SHA256. Load only the locally generated artifacts with the matching dependency environment.
- `development_metrics.csv`, `method_comparison.csv`, `selection.json`, `development_coverage.json`: all groups, per-run/channel common and own coverage, full outer-training diagnostics and the selection rule's outcome.
- `stress_metrics.csv`, `stress_coverage.json`: both frozen outer artifacts on B04, first loaded after selection. `quality_strata.csv` covers common and own-available warning/support strata, including empty subsets.
- Source-row `.jsonl` forecast ledgers: original observations and all quality/provenance, all candidate forecasts, target arrival interval, common eligibility/reason and final pending row. These permit numerical audit and selected replay without refitting.
- `proposed_final_config.json`: smoothing alpha=0.5 proposal; no pooled final fit or B03 evaluation. `verification.json`, browser-verification.json, tests.log and environment.txt document checks.

Audit without refitting: `.venv/bin/python scripts/verify_selection_outputs.py --results reports/local/selection-v2`. It reloads artifacts, checks recorded metrics/scalers/selection, supplements both coverage strata, and SHA256-checks only B01/B02/B04 raw directories against existing manifests. Raw checks are read-only. Generate the complete documented tables with `selection_report --results reports/local/selection-v2 --document docs/selection_results.md`.

The one actual development search used the declared 108 candidate-fold evaluations and 92 learned pipeline fits including eight outer refits. Generated-fixture tests exercise the same orchestration independently; they do not search real development data again. Re-running the explicit reproduction command is a reproducibility run, not permission to expand the grid or tune until a method wins.

Optional browser acceptance: `node scripts/verify_selection_dashboard.cjs reports/local/selection-v2` with the existing Playwright/Chromium tools. It checks the standalone file without network requests, both direction-specific settings, all B01 common counts, play/pause/reset, B04 caveats and mobile layout. `dashboard/app.py` now defaults to the selected HTML replay; passing the old explicit `--artifact` option still launches the historical forecast-v1 dashboard.
