# Planned evaluation protocol
No ML evaluation occurs in milestone 1. Before modelling, choose task and labels,
chronological/group-aware partitions and a prediction horizon. Fit transformations
only on training data. Use past-only features; account for overlapping label windows.
Select thresholds on validation data and evaluate once on held-out test data.
Include false alarms per machine-time and incident recall/lead time where labels
permit. Do not report anomaly scores as calibrated failure probabilities.
