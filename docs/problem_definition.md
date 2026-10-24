# FactoryGuard
Goal: analyse industrial sensor histories and eventually warn about abnormal behaviour.
Milestone 1: read a CSV, validate it, summarise it and plot sensor histories.
The included dataset is synthetic: three machines, 360 minutes each, 1080 rows.
M002 has an injected temperature/vibration trend for visual exploration only.
There are no verified failures or labels, so no failure prediction or performance
claims can be made. Paderborn B01 has since been selected and inspected for
ingestion development; see dataset_assessment.md for unresolved interpretation
limits. No model may be trained or evaluated on this single experiment.
Future task: anomaly detection, or failure-within-horizon prediction if labels support it.
RUL is a later extension. No model, API or dashboard is implemented yet.


Current authorization: the completed forecast-v1 prototype is a next-observed-burst RMS forecasting task (B02 fitting, B01 development validation, B04 separate as-recorded stress). It supersedes the earlier single-B01 restriction for this explicitly experiment-separated objective. The local dashboard is implemented; the production API, fault/RUL targets and deployment remain planned. See modeling_protocol.md and forecast_review.md.
