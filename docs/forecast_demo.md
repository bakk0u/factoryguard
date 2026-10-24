# Reproduce the local forecasting prototype

From `/workspace/factoryguard`, use the existing `.venv`. No new dependency is needed beyond the current numpy/pandas/matplotlib/scipy environment. The synthetic demo remains `run_step1.py` and is independent of this real-data workflow. Keep archives and raw source files outside Git. B03 is never opened by these commands. Do not download more data.

```bash
export XDG_CACHE_HOME=/tmp/factoryguard-cache
export MPLCONFIGDIR=/tmp/factoryguard-matplotlib
export MPLBACKEND=Agg
export OPENBLAS_NUM_THREADS=1
.venv/bin/python -m pip install -e .
.venv/bin/python -m unittest discover -s tests -v
.venv/bin/python run_step1.py

.venv/bin/python -m factoryguard.pipelines.forecast train \
  --config configs/forecast_v1.json --output reports/local/forecast-demo/model
.venv/bin/python -m factoryguard.pipelines.forecast evaluate \
  --artifact reports/local/forecast-demo/model/model.json \
  --output reports/local/forecast-demo/evaluation
.venv/bin/python -m factoryguard.pipelines.forecast replay \
  --artifact reports/local/forecast-demo/model/model.json --run B01 \
  --output reports/local/forecast-demo/replay-B01
.venv/bin/python -m factoryguard.pipelines.forecast serve \
  --artifact reports/local/forecast-demo/model/model.json --port 8765
```

Open `http://127.0.0.1:8765` in a browser **on the same machine as the server**. In a cloud workspace, this address refers to the cloud machine and is not a browser-accessible preview URL on your computer. This environment does not expose a preview/port-forwarding tool. For a portable preview, use the standalone export below. The server binds only loopback; no external deployment. If 8765 is occupied, choose a different `--port`. For the **already executed** demonstration, use `reports/local/forecast-v1/model/model.json` with `serve` directly, without retraining. `/health` reports readiness. Stop with Ctrl-C. Training/evaluation/replay output directories must be fresh; choose another directory on repeat runs. All outputs are ignored by Git.

The default config names the three existing verified descriptor tables. If rebuilding from already downloaded raw sources is needed, regenerate B01 using `features_paderborn` and B02/B04 using `assess_development` (see feature_definitions.md/development_assessment.md), then copy the config and change **only** its `tables` paths to those fresh derived tables. Commands reject changes to the frozen model, features, roles or gap policy. Do not run acquisition scripts. The tables are small; waveforms are not loaded during training/replay. B03 feature access is not supported.

`model.json` is a non-executable JSON artifact containing the exact config, original config SHA256, all three table SHA256s, training source IDs, learned means/scales, delta intercept, coefficients, support counts and package versions. `config.json` and `model.sha256` accompany it. Table checksums must match on evaluation/replay/server startup. The executed software freeze is `reports/local/forecast-v1/environment.txt`. Numeric reproduction across different BLAS/platforms may differ at floating-point roundoff; no stochastic fitting or split is used.

Evaluation writes per-run JSON metrics, a tidy `metrics.csv` with all strata, per-run `.forecasts.jsonl` ledgers including expired/pending forecasts, and gap-preserving PNG histories. Errors are observed minus forecast, in volts. Scores use common finite pairs; empty/zero-denominator metrics are null. B02 results are training diagnostics. B01 is development validation; B04 is separately labelled as-recorded stress. Nothing here is an unbiased multi-bearing generalization estimate.

Replay writes one `events.jsonl` event per observed row, containing the full observed feature/provenance/quality record, any previous forecast settlement and the new pending forecast. The final forecast stays pending. At issuance the next arrival/context/flags are unavailable. Explicit clock expiry is also supported by the `Replay.advance_time()` API; the browser demonstrates burst arrivals at adjustable replay pace, not a simulated real-time acquisition clock. At each gap arrival it retains the expired forecast and breaks plotted lines. The browser server holds only the small descriptor tables and reveals prefix history to each session, never unrevealed records or future end times. Session reset clears history and never joins experiments.

Use Play, Pause, Next burst and Reset. Channel histories, signed forecast errors, measured/commanded context and temperatures are separate. Blue warm-up rings do not mean healthy; amber sensor triangles and the quality panel retain suspect data. B04's global context warning persists. A red temperature reference notice is distinct from purple forecast deviations. There are no deviation thresholds or failure probabilities. Expand the provenance section for current flags and cumulative common-pair metrics. Keyboard controls use standard labelled buttons/selects; SVG histories include titles/hover values.

Optional browser acceptance (requires an existing Playwright/Chromium installation, not a runtime app dependency): start the executed forecast-v1 server, then `node scripts/verify_forecast_dashboard.cjs`. It checks step/pending behavior, a real B01 gap, play/pause/reset, B04 warnings and mobile layout, and writes screenshots under the ignored forecast-v1 directory. `scripts/verify_forecast_outputs.py` independently recomputes actual metrics/scaler statistics and SHA256-checks **only B01/B02/B04** raw files against existing manifests; it never traverses B03.

Limitations and the concrete later B03 proposal are in [forecast_review.md](forecast_review.md). Do not infer damage onset, fault precision/recall or RUL from this replay.


## Standalone preview without cloud port access

The generated `reports/local/forecast-v1/dashboard-B01-offline.html` (2.75 MB) is a self-contained B01 development replay: save/download that HTML file, then open it in your browser. It needs no Python server, network connection or other assets. Play/pause/step/reset show the existing 377 observation events, including four expired transitions and the final pending forecast. B02/B04 selection is removed from this B01-only preview.

Recreate with `.venv/bin/python scripts/export_b01_dashboard.py --output reports/local/forecast-v1/dashboard-B01-offline-new.html`. It packages the already executed B01 events; no training, new model evaluation, raw access or held-out access occurs. It refuses to overwrite a file. The entire precomputed B01 replay is embedded, so sequential reveal is a presentation control, not an access boundary. This does not change the server's prefix-only API or the forecasts' past-only computation.

Offline controls were browser-tested with zero network requests and no page errors. The managed Chromium environment blocks `file:` URL navigation, so the exact standalone bytes were tested via Playwright `setContent` instead; direct `file:` navigation was not verified here. The generated screenshot is `dashboard-B01-offline.png`, and method/results are in `offline-verification.json`. No public tunnel or external deployment was created.
