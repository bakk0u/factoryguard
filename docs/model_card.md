# Current selected method: exponential smoothing (selection-v2)

Intended use: descriptive next-observed-burst A/C RMS forecasting in volts, with separate measurement/gap/temperature notices. No fault probabilities, alarms, labels or RUL. B03 remains sealed.

The bounded 108 candidate-fold search selected exponential smoothing, macro common-pair MAE improvement 12.83% over persistence with equal run/channel weights. This is development selection performance, not unbiased final performance. B01 is replayed with alpha=0.2 selected inside B02; B02 with alpha=0.5 selected inside B01. Full per-run/channel metrics and unsuccessful Ridge/tree candidates are in selection_results.md. B04 is post-selection as-recorded stress only, with unresolved context interpretation.

Smoothing uses only current/past A/C RMS: s_t=alpha*x_t+(1-alpha)*s_(t-1); predict next=s_t. Initialize on first finite RMS, reset on gaps >24 s or experiment boundary, and clear a channel state when its RMS is missing. No scaler, imputer or trained coefficients. It issues after a complete burst; next arrival/context/flags remain unavailable. Final forecasts remain pending. Common comparison requires the same initialized three-burst history as the regression candidates; broad own/persistence coverage is also reported. No warning rows are silently removed.

Final release proposal: **alpha=0.5**, using equal-weight already recorded inner objectives and the frozen tie preference. No pooled final fit or B03 evaluation has been executed. The proposed artifact is reports/local/selection-v2/proposed_final_config.json. Freeze release code/dependencies and rules before a separately authorized blinded B03 validity pass and one-shot evaluation; do not use B03 to choose corrections/features/settings. A single reserve run cannot establish population performance or industrial fault detection.

Known limitations: only two compatible independent development bearings; designs and selection used both; variable arrival intervals; provisional ordinal/absolute-time meaning; unknown next operating changes; inconsistent quality-subset gains; sparse/unseen bins; B04 measurement ambiguity; no verified health/onset/endpoints. The selected method improves recorded-RMS forecasting under this development protocol only. See model_selection_explained.md and selection_demo.md.

---

# Historical forecast-v1 model card

Purpose: forecast the next observed completed burst's mean-removed A/C RMS in **volts**, and show descriptive forecast deviations in sequential replay. No fault labels, probabilities, alarm calibration or RUL. Local laboratory prototype only; no external deployment.

Persistence copies current RMS. The single learned comparator is two-output ridge increment regression, alpha=10, with an explicit seven-input allowlist and B02-only fitted population standardization. B02 supplies 1114 training pairs; B01 is experiment-separated development validation already used for feature design. B04 is a separate as-recorded stress case with unresolved context interpretation; it is never pooled. B03 remains sealed. No hyperparameter tuning or post-result refit occurred.

The candidate loses to persistence on B01: A MAE/RMSE 0.061381/0.086234 V versus 0.043027/0.078994 V; C 0.037758/0.055316 V versus 0.028006/0.053918 V (n=372 each). It also loses on B04. Small B02 gains are optimistic resubstitution only. Persistence remains the demonstrated benchmark. Full per-run/channel/quality/support metrics and failures are in [forecast_review.md](forecast_review.md).

Model/artifact contract: [modeling_protocol.md](modeling_protocol.md), frozen amendment; configs/forecast_v1.json. Artifact: reports/local/forecast-v1/model/model.json (numeric JSON, exact config and table hashes, scaler, coefficients, source IDs and versions). Commands: [forecast_demo.md](forecast_demo.md). All learned preprocessing uses training only. No imputation or clipping; nonfinite model inputs produce explicit unavailable forecasts. Sensor-range warnings are preserved, and negative forecasts would be retained/reported.

Issue after current 1.6 s burst completion. No future context/flags or future elapsed interval as inputs. Target arrival is variable; expiry beyond 24 provisional CSV-clock seconds; first observation has no preceding forecast, final prediction remains pending. Ordinal association, timezone and clock start/end meaning remain unresolved. No operating-time or end-of-experiment labels. The limited independent-run count, rig sharing, warm-up bias, unseen/sparse contexts, B04 interpretation and ambiguous termination prohibit strong generalization or physical fault claims. The dashboard's separate 110 °C general reference is not a certified safety alarm or failure criterion.

Later B03 evaluation requires separate authorization and frozen blinded measurement-validity gates. Keep saved artifacts and both methods unchanged, report unsupported/unevaluable cases, and do not use that one run to tune/select a winner.
