# Additional Paderborn experiments: roles declared before inspection

Declared 2026-10-22, before downloading or inspecting any additional run's signal trends or feature distributions. Selection uses only the official description PDF (March 25, 2024 v2, pp. 3–8) and the saved Zenodo record 10868257 metadata. This is a proposed development/evaluation allocation, not an executed evaluation or a claim that endpoints are validated.

| Experiment | Proposed role | Selection reason | Published archive bytes | Published MD5 |
| --- | --- | --- | ---: | --- |
| B01 | Existing development/exploration | Already downloaded and fully inspected; ambiguous termination; never a standalone evaluation set | 965866495 | 5e82d9d98f21e4a03a06c43b87858c6b |
| B02 | Additional development | Independent matched-condition experiment: same 128 kHz, 1.6 s bursts, 2 Hz sinusoidal load and documented 2400–3000 rpm, 3300–3800 N static, 500–1400 N dynamic ranges as B01. PDF lists a vibration termination criterion and about 6 h / 1116 measurements. | 2725517006 | a75354d8e41eee9b6adf55f0f6c532a8 |
| B04 | Additional development for operating coverage | Same nominal measurement channels/rate and sinusoidal excitation; extends documented speed to 1500–3000 rpm, static load to 2500–3800 N, dynamic load to 500–1500 N. PDF lists vibration termination, about 6 h / 1114 measurements. | 2844244761 | 9d7c11dc6a83424b440ae6d184064dcb |
| B03 | **Proposed held-out evaluation reserve** | Independent matched-condition experiment with a documented temperature termination criterion (about 3 h / 614 measurements). Smallest matched-condition candidate; reserve it before seeing signal/feature behavior. | 1463649321 | 6c16eaa8d837b31da69fab1675521ddb |

Only B02, B03 and B04 are newly authorized here: **7,033,411,088 bytes** combined compressed downloads. B01 and the description PDF must be verified/reused, never redownloaded merely because a new acquisition step is running. The full 152 GB collection remains out of scope.

All selected runs use the same documented A/C vibration, temperature and operating-summary families. Experiment-specific gain/conversion, actual headers, calibration, timestamp association and endpoint interpretation must still be checked. The current loader/feature extractor is B01-specific and is not automatically certified for the new runs.

## Guardrails before future work

- B03 is not included in plots, descriptive feature distributions, normalization decisions, feature selection, alarm tuning, or other model-guiding analysis. For now, permit only archive integrity, safe extraction, file inventory, CSV schema/finite-value/time-order checks and MAT header/shape/type checks. Do not compute its RMS, extrema, kurtosis, trends or event labels. No B03 source log content is needed to carry out these structural checks; its general documented endpoint type comes from the already public description.
- This acquisition task also limits B02/B04 to integrity and structure; their development role permits later explicitly scoped exploration, but no trend exploration is needed to validate a download.
- Neither a PDF table entry nor the last file establishes an exact event time. Vibration thresholds vary from 6–10 g and the exact statistic/threshold require log review. Temperature criterion documentation does not resolve clock alignment or endpoint validity automatically. Do not invent labels or transfer B01's calibration to other runs.
- Do not change these roles based on attractive trends or outcomes. Any future evaluation design must address experiment-level independence, coverage, censoring, endpoint semantics and leakage explicitly. A single held-out experiment remains a very limited reserve, not evidence of generalization.
- Preserve all original archives and raw files outside Git at `/workspace/datasets/paderborn-10868257/`, using `raw/B02`, `raw/B03`, and `raw/B04` for extracted experiments. Save a download/validation ledger alongside the existing B01 extraction manifest instead of overwriting it.

B05 is smaller but deliberately interrupted, so it offers no straightforward failure endpoint. B12 is smaller but changes acquisition to 64 kHz and loading to Gaussian excitation; it is less suitable for this first compatibility expansion. Larger multipart experiments are deferred. Selection and grouping must not be expanded to obtain a desired feature result.
