# Paderborn run-to-failure dataset assessment

## Source, terms, and intended use

Selected source: [Run-to-failure data set of ball bearings subjected to time-varying load and speed conditions](https://zenodo.org/records/10868257), DOI 10.5281/zenodo.10868257, creator Osarenren Kennedy Aimiyekagbon, Paderborn University. Record publication date is 2024-04-02. The description says version 2024-04-02, while the metadata version field says `2023-04-02`; preserve this discrepancy rather than silently correcting the source.

The record declares open access under **CC BY 4.0**: attribution, a licence reference, and identification of changes are required for reuse; do not imply endorsement. Cite the dataset/creator/DOI and, as requested by the record, Javanmardi et al. (2024), *Remaining Useful Lifetime Estimation of Bearings Operating under Time-Varying Conditions*, DOI 10.36001/phme.2024.v8i1.4101. This repository uses generated test fixtures rather than redistributing raw measurements.

Primary technical source: *Run-to-failure data set of ball bearings subjected to time-varying load and speed conditions*, March 25, 2024, v2, 9 pages (the description PDF attached to the record). Retrieved 2026-10-22. Its 2,766,702 bytes match published MD5 `7c6535acb48e620cb37b0f040cb9f83a`. The PDF and record metadata are stored outside Git at `/workspace/datasets/paderborn-10868257/`.

The initial authorization covered **B01 only**, for ingestion and feature development. The user subsequently authorized a small independent-run expansion: **B02/B04 development and B03 held-out reserve**, declared in [experiment_roles.md](experiment_roles.md) before new signal inspection. No models or labels are authorized. The existing synthetic demonstration remains unchanged and must still be labelled synthetic. These are accelerated laboratory experiments, not evidence of factory deployment performance.

## Sensors, units, and sampling

PDF pp. 2–3 and 5–7 describe 17 experiments on initially unseeded 61806-2RS bearings: 30 mm inner diameter, 42 mm outer diameter, 7 mm width, 19 balls. Two housing acceleration directions, A and C, are provided from three installed unidirectional accelerometers. Temperature positions T1 and T2 are on the bearing housing; ambient temperature is measured nearby.

| Measurement | Units and acquisition | Limits and interpretation |
| --- | --- | --- |
| `accHorizRear_A`, `accHorizFrontal_C` | Raw MAT signals in **V**, not g or mm/s; 128 kHz for B01–B09, 64 kHz from B10 onward | PCB Piezotronics 603C01, nominal sensitivity 100 mV/g ±10%, ±50 g range, 0.5–10,000 Hz 3 dB range, 25 kHz resonance; signal conditioner MMF M208B and NI-9223. Experiment log supplies conversion factors. Do not apply nominal sensitivity without the log's chain calibration. |
| `measTime` | Corresponding within-record sample time; actual MAT layout must be inspected | Sampling duration 1.6 s, measurement interval approximately 12 s. Gaps between recordings must not be plotted as continuous high-rate sampling. |
| T1, T2, ambient | CSV mean temperatures in °C; thermometers acquired at 10 Hz | MC 745691-02 Pt100, NI-9216; specified range −50 to 204 °C; accuracy ±(0.3 + 0.005×absolute temperature) °C. CSV values are summaries, not the original 10 Hz stream. |
| Dynamic and static load | CSV set and measured values in **N** | Set dynamic amplitude and measured peak; set static preload and measured mean absolute static load. |
| Shaft speed | CSV set and measured values in **rpm** | Set speed and measured mean absolute speed. |

Control and acquisition used MATLAB DAQ toolbox and NI cDAQ-9189. The PDF does not establish a timezone for `dateTime`; do not invent UTC. Retain source timestamps and explicitly document any alignment or duration assumptions. Sensor specifications and set ranges are not universal anomaly thresholds or automatic reasons to discard measurements.

## Operating conditions and failure criteria

PDF pp. 3–4: total bearing load combines a static preload through a lever and a shaker-generated dynamic component. Speed and load amplitudes vary between measurements, drawn within specified intervals; some later experiments have fixed conditions. B01–B06 use sinusoidal dynamic loading at 2 Hz; B07–B17 use Gaussian white noise up to 200 Hz.

For **B01**, Table 2 specifies rotating speed 2,400–3,000 rpm, static-load amplitude 3,300–3,800 N, and dynamic-load amplitude 500–1,400 N. Measured values need not equal set values; validate and report discrepancies without silently clipping them.

Generally an experiment ends when its vibration or temperature criterion is exceeded: vibration thresholds lie between 6 and 10 g and the temperature threshold is 110 °C. **B01 had no preset criterion**; B05 was deliberately interrupted, and Table 3 lists no criterion for B16. Thus an end-of-file is not uniformly a threshold-defined failure event. Table 3 (p. 8) describes B01 as approximately 2 h, 377 files, with inner race (IR), outer race (OR), and rolling-element (B) defects found after dismantling. Postmortem damage is experiment-level information, not a timestamped onset or per-sample label. No supervised failure labels or RUL targets are inferred here.

## Documented file contract

PDF pp. 6–8:

```text
B01/
  vibrationData/data_B01_M0001.mat ... data_B01_MXXXX.mat
  B01_meanTemperatures.csv
  B01_operatingConditions.csv
  B01_extractedFeatures.csv
  B01_log.pdf
```

The text says a subfolder and four files; the figure omits the extracted-features CSV, which p. 8 describes separately. Measurement identifiers are incremental. MAT variables are `accHorizRear_A`, `accHorizFrontal_C`, and `measTime`; the PDF recommends `scipy.io.loadmat`. Precomputed extracted features will not be used as trusted past-only features without auditing how they were computed.

Temperature CSV columns: `dateTime`, `Mean Abs. Temp. T1 / °C`, `Mean Abs. Temp. T2 / °C`, `Mean Amb. Temp. / °C`.

Operating CSV columns: `dateTime`, `setDynLoad / N`, `peak_dynLoad / N`, `setStatLoad / N`, `meanAbs_statLoad / N`, `setSpeed / rpm`, `meanAbs_speed / rpm`.

The loader must follow the actual archive's encoding, headers, time representation, and channel shapes; the synthetic CSV contract does not apply.

## Access, storage, and integrity

Zenodo previously failed at proxy CONNECT with HTTP 403. On resumption, both the record page and API returned successfully on 2026-10-22; the page returned HTTP 200. The record metadata supplies B01.zip size **965,866,495 bytes** and MD5 **`5e82d9d98f21e4a03a06c43b87858c6b`**. About 30 GiB was free on the workspace filesystem before download. The approximately 152 GB collection is outside scope and will not be downloaded.

Raw archives, PDF documentation, metadata, and extracted measurements stay outside the checkout under `/workspace/datasets/paderborn-10868257/`. ZIP files and repository-local external-data paths are also ignored by Git. Download uses a `.partial` name; extraction is permitted only after published size and checksum verification. The extraction helper preflights member paths, links, duplicate/case-colliding destinations, file/directory conflicts, total uncompressed size, and available space with a margin. It creates a fresh staging directory, checks member CRCs while copying, and renames only after success.

B01 download, checksum verification, safe extraction, experiment-log review, loader validation, and full inspection completed successfully. Executed evidence and unresolved interpretation limits follow. No model has been trained or evaluated.

## B01 archive and experiment-log evidence

B01.zip was downloaded completely, and its published size and MD5 matched before extraction. Safe extraction yielded **381 members**: 377 MAT recordings, two CSVs, one experiment-log PDF, and the vibrationData directory. Total uncompressed size was **1,091,469,303 bytes**. All member CRCs passed while extracting. Approximately 2.06 GB is needed for the archive plus extracted files, excluding documentation and reports; available space was checked before both operations.

Actual deviations from the general PDF are material:

- CSV timestamp column is **`Time`**, not `dateTime`; format is `19-Oct-2021 08:46:54`.
- The ambient-temperature header is **`Mean Room Temp. / °C`**, not `Mean Amb. Temp. / °C`.
- **B01_extractedFeatures.csv is absent.** There are three root files, rather than the four described in the text. The 377 count is the number of MAT measurements, not all files in the ZIP.
- Each inspected MAT contains three real double column vectors of shape **(204800, 1)**, with the documented channel names. `measTime` is seconds relative to the recording start: zero through 1.5999921875 in 1/128000-second steps. MAT files have no absolute date/time variable; matching M0001 to CSV row 1 is an ordinal association only, not an independently verified clock alignment.

The two-page **B01_log.pdf** supplies experiment-specific details. Page 1 states 128 kHz, 1.6 s, approximately 12 s pause, **10 g/V conversion**, and **0 dB gain**. Static plus dynamic set load is intended to lie in 4,300–4,900 N. Page 2 documents a 10-minute warm-up at 750 rpm and 2,500 N static load without dynamic load, after a new bearing had run for at most 15 minutes the previous day. It records start/end date 19 October 2021.

There is unresolved source disagreement: the general PDF says no criterion was preset for B01, but the log says the experiment completed because a temperature threshold was exceeded at **09:13**. The actual CSV continues until **10:59:32**. Neither statement is silently preferred for labelling; no failure time, RUL label, or healthy/faulty interval has been created.

## Executed inspection results

Final outputs are in `reports/local/paderborn-b01-verified/` (ignored by Git). All 377 MAT recordings passed shape/channel/finite-value/relative-time checks; both CSVs had 377 strictly increasing, unique source times with exact cross-table alignment. Full inspection covered **77,209,600 samples per channel**, not just the plotted excerpts. Runtime was **9.47 s**, with **128.19 MiB peak process RSS**. These figures are observed on this Linux cloud task, not hardware-independent promises.

The loader never concatenates an experiment's arrays. It reads one recording at a time, retains only per-record statistics and small CSV tables, and preflights MAT vector shapes before loading required variables. `recording_statistics.csv` contains min/max/mean/RMS/absolute peak in V and counts above nominal sensor range using the explicitly documented 10 g/V conversion. These are offline descriptive inspection statistics, not trained features. The plots show discrete observations without bridging acquisition gaps and 50 ms full-resolution excerpts from M0001, M0189 and M0377.

Observed warnings:

- Source time range is 2021-10-19 08:46:54–10:59:32 (7,958 seconds), timezone unspecified. Inter-record spacing min/median/max is **11/18/1147 s**. Four intervals exceed 24 s (1,147, 138, 26 and 26 s). Do not fill these gaps or assume one continuous 128 kHz signal.
- There are 51 warm-up rows at 750 rpm. Excluding the documented warm-up setpoints, **33 speed setpoints** lie outside 2,400–3,000 rpm; maximum set speed is 3,551.6927502193 rpm. The measured-speed maximum is 3,002.94293887047 rpm. Set and measured columns remain distinct; no clipping, smoothing or forced equality is applied.
- T1 range is 21.44–122.56 °C; T2 is 21.34–119.38 °C; room temperature is 21.42–26.54 °C. Crossing a documented temperature value is not used to create labels while termination metadata remains inconsistent.
- Using the log conversion, **3,719 A samples and 19 C samples** exceed nominal ±50 g sensor range. Further calibration and possible range/saturation investigation is required. The original voltages are preserved, and exceedances are warnings rather than silent deletions.

`valid=true` in inspection.json means the inventory, schema, finite numeric values and time/sample structure passed. It does **not** certify physical quality, failure criteria, clock alignment, or suitability for model evaluation.

## Reproduce ingestion and inspection

From the checkout, install the declared dependencies with `.venv/bin/python -m pip install -e .`. To acquire a fresh local copy, run:

```bash
.venv/bin/python scripts/prepare_paderborn.py /workspace/datasets/paderborn-10868257
```

This script requests only the record metadata, description PDF and B01.zip. It verifies existing downloaded files before use and refuses to overwrite an existing raw extraction or incomplete staging directory. In this task it was executed successfully after the already verified downloads were retained under their original published filenames. The original `curl` transfer used a `.partial` archive, which was renamed only after verification. Keep record.json and extraction.json with the local dataset for provenance; do not delete the archive to save space without an explicit retention decision.

For a fresh inspection output directory:

```bash
export MPLBACKEND=Agg
export MPLCONFIGDIR=/tmp/factoryguard-matplotlib
export XDG_CACHE_HOME=/tmp/factoryguard-cache
export OPENBLAS_NUM_THREADS=1
.venv/bin/python -m factoryguard.pipelines.inspect_paderborn \
  /workspace/datasets/paderborn-10868257/raw/B01 \
  --output reports/local/paderborn-b01-new-inspection
.venv/bin/python -m unittest discover -s tests -v
.venv/bin/python run_step1.py
```

The initial loader was explicitly B01-specific; the subsequently authorized [development assessment](development_assessment.md) verifies compatible B02/B04 logs and extends ingestion to those runs. B03 is not authorized for waveform/feature access and remains a held-out reserve. Do not substitute development assumptions for another run's documentation. The test suite uses generated MAT and CSV fixtures, including invalid inputs; raw source measurements are never embedded in tests. Raw files are read only, and the original synthetic workflow is preserved.

Final verification: **30 tests passed**, with no failures or skips (12 original validation tests, 13 B01 loader tests, and five archive-safety tests). Dependency checks passed and the unchanged synthetic CLI succeeded. After inspection, all **380 extracted files** were independently checked against their original ZIP member sizes and CRCs and still matched. The final report, its 377 statistics rows, and both PNG files were also independently verified. Approximately 28 GiB remained free on the workspace filesystem.

## Suitability decision and next work

The minimal burst-feature milestone has since been implemented and verified;
see [feature_definitions.md](feature_definitions.md) for its exact formulas,
missing-value/quality policy, operating comparisons and runnable command.
This does not resolve the source ambiguities below or authorize modelling.

B01 is suitable for implementing documented-format ingestion and exploratory, past-only feature development, with the above warnings retained. One experiment cannot provide independent model selection or evaluation evidence. Postmortem IR/OR/rolling-element defects do not establish per-window onset labels. Before predictive work, resolve timestamp/measurement alignment, gaps, warm-up treatment, range/calibration questions and conflicting termination metadata, and separately authorize a leakage-safe evaluation design. No model was trained or evaluated in the B01 milestone, which downloaded B01 only. The subsequent authorized B02/B03/B04 integrity/structural acquisition is documented in [additional_experiments.md](additional_experiments.md); B03 is a predeclared held-out reserve and has not been explored.
