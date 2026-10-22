# FactoryGuard
Goal: analyse industrial sensor histories and eventually warn about abnormal behaviour.
Milestone 1: read a CSV, validate it, summarise it and plot sensor histories.
The included dataset is synthetic: three machines, 360 minutes each, 1080 rows.
M002 has an injected temperature/vibration trend for visual exploration only.
There are no verified failures or labels, so no failure prediction or performance
claims can be made. Select a real documented time-series dataset before modelling.
Future task: anomaly detection, or failure-within-horizon prediction if labels support it.
RUL is a later extension. No model, API or dashboard is implemented yet.
