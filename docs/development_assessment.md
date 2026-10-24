# Development assessment: B01, B02 and B04 — 2026-10-23

This assessment records the completed pre-modeling milestone. The separately authorized forecasting prototype and measured results are now in [forecast_review.md](forecast_review.md); its [frozen protocol](modeling_protocol.md) supersedes the earlier proposal-only status. Measurement findings below are unchanged.

## Scope and evidence

B02 and B04 are now fully validated and assessed as development experiments; B01's existing verified feature table is reused. **B03 was not opened, plotted, revalidated or used for selection in this task.** Its held-out role is unchanged. No additional download, model training, normalization fitting, alarm tuning, failure label, damage onset, or operating-time estimate was introduced.

Sources are the official dataset description (March 25, 2024 v2, pp. 3–8), B02_log.pdf and B04_log.pdf (each pp. 1–2), and the actual source files. These describe the same rig and A/C housing accelerometers, bearing T1/T2 and room temperatures, and load/speed summaries. Logs are retained unchanged with the raw data; the acquisition manifest and per-file hashes remain outside Git.

Run the complete workflow from the checkout:

```bash
export MPLBACKEND=Agg MPLCONFIGDIR=/tmp/factoryguard-matplotlib
export XDG_CACHE_HOME=/tmp/factoryguard-cache OPENBLAS_NUM_THREADS=1
.venv/bin/python -m factoryguard.pipelines.assess_development \
  --output reports/local/development-assessment-new
```

The command accepts only B01/B02/B04 internally and rejects held-out waveform/feature access. It requires the already downloaded raw files and the existing B01 feature table; it never downloads anything. `--reuse-features` may be used when B02/B04 feature tables and integrity manifests already exist inside that assessment output, before the top-level assessment.json is written.

Final artifacts for this task are in **reports/local/development-assessment-20261023-final/**. Earlier same-task staging artifacts are not the final assessment. B02's valid extraction was reused there; B04 was re-extracted after its initial-policy uncertainty was included in the combined warning. Each run has features.csv, schema.json, raw_integrity.json, extraction.json, condition counts/comparisons, recording_diagnostics.csv, assessment.json and histories.png. B01's feature table remains at reports/local/b01-features-v1/features.csv; its assessment/plots are in the final assessment's B01 subdirectory.

## Measurement validity and association

| Check | B02 | B04 |
| --- | ---: | ---: |
| Consecutive MAT bursts / both CSV row counts | 1116 | 1114 |
| Full arrays checked, not only headers | Every burst | Every burst |
| A/C/measTime shape | (204800,1) in source | (204800,1) in source |
| Real finite voltage and sample-time values | All passed | All passed |
| Entire zero-based sample grid | 128000 Hz, tolerance 1e-10 s | 128000 Hz, tolerance 1e-10 s |
| Last sample / record duration N/fs | 1.5999921875 s / 1.6 s | 1.5999921875 s / 1.6 s |
| Missing feature values / zero-variance channels | 0 / 0 | 0 / 0 |
| Source files SHA256-verified unchanged | 1119 | 1117 |

The two new runs cover **456,704,000 vibration samples per channel** in total. Loaded raw arrays are released one recording at a time. Burst count, finite values, exact sampling grid and duration checks are prerequisites to publishing the feature table; malformed data raises an error rather than silently skipping a measurement. All real bursts passed.

Both experiment logs explicitly state **volts**, **10 g/V**, **0 dB gain**, **128 kHz**, **1.6 s**, and an approximate 12 s pause. This independently supports reusing B01's feature formulas, units and strict ±5 V nominal sensor-range check. It is documentary confirmation, not an independent traceable calibration certificate. Temperature units remain °C, load N, speed rpm, with the general description's measurement meanings. The sensor's documented 0.5–10 kHz response does not become a calibrated 64 kHz bandwidth because of the sampling rate.

The CSVs use the same observed `Time`/`Mean Room Temp.` headers as B01. Time order is strictly increasing and unique; temperature and operating timestamps align exactly. MAT identifiers are consecutive, with one CSV row per file. MAT contains **relative sample time only**: no independent absolute timestamp was found. Matching M0001 to CSV row 1 is therefore still **provisional ordinal alignment**. CSV timezone and whether Time marks start/end remain unspecified. These caveats are retained in every feature row. Calibration/units must not be assumed for other runs, particularly the held-out reserve.

## Acquisition and operating conditions: observations

| Quantity | B01 | B02 | B04 |
| --- | ---: | ---: | ---: |
| Source CSV span (not operating time) | 08:46:54–10:59:32, 19 Oct | 08:59:35–14:36:36, 25 Oct | 12:45:09–18:26:58, 17 Nov |
| Median / maximum source interval, seconds | 18 / 1147 | 18 / 282 | 18 / 24 |
| Intervals strictly >24 s | 4 | 1 | 0 |
| Logged warm-up setpoint matches | 51 | 51 | 50 |
| A / C nominal-range-warning bursts | 10 / 1 | 0 / 0 | 0 / 0 |
| Local combined-warning rows | 96 | 53 | 210 |
| Fixed condition groups / groups n<20 | 51 / 46 | 46 / 28 | 56 / 32 |

All source dates above are in 2021 with no declared timezone. B02's one gap is **282 s, M0921→M0922, 13:32:36→13:37:18**. Its timing is consistent with the logged stop/continuation; the exact rig state during the unobserved interval is not established. B04's absence of intervals >24 s does not imply continuous waveform acquisition or continuous operation. Sampled waveform duration is only 1785.6 s for B02 and 1782.4 s for B04 across their much longer CSV spans. No gaps are filled and no burst arrays are concatenated.

Warm-up flags match the documented 750 rpm / 2500 N static / zero dynamic commands. They identify an operating regime, **not a healthy baseline**. Measured versus commanded values remain separate. Loaded-row medians are:

| Measured / commanded ratio | B01 | B02 | B04 |
| --- | ---: | ---: | ---: |
| Speed | 1.00279 | 1.00273 | **0.49921** |
| Static mean absolute load | 0.99310 | 0.99481 | 0.99672 |
| Dynamic peak / set amplitude | 1.03268 | 1.05927 | **0.51777** |

For B04, loaded speed ratios range **0.49815–0.50030**, and dynamic peak/amplitude ratios **0.49396–0.52826**. Measured speed across the run is 373.67–1494.46 rpm, despite commanded main-run ranges extending to 3000 rpm. Static load does not share the apparent factor of two. A possible scaling/acquisition-code issue, control behavior or measurement-definition mismatch requires independent confirmation; the observations do **not** establish which explanation is correct. Peak dynamic load and commanded amplitude are not guaranteed equal statistics. No field, waveform or bin is rescaled to force agreement.

Every B04 row is marked `quality__operating_context_interpretation_unresolved=true` in recording_diagnostics.csv. This is a **post-hoc run-level audit annotation**, excluded from candidate inputs, not an online alarm. That companion also retains per-record ratios/differences for all runs; dynamic ratios with zero commanded amplitude are missing and explicitly flagged as undefined (51/51/50 warm-up rows in B01/B02/B04). No ratio discrepancy threshold was fitted. The feature table's `quality__any_warning` remains a local convenience flag and does not replace this global context limitation or the alignment caveat.

## Per-run log details and termination limits

**B02:** log p. 1 confirms the same 2400–3000 rpm, 3300–3800 N static, 500–1400 N dynamic ranges and 2 Hz sinusoid as B01; combined commanded load is documented as 4300–4900 N. Log p. 2 says the experiment stopped at **13:32** after an accelerometer's RMS exceeded **0.65 V twice**, then continued with **four crossings** permitted; completion is recorded at **14:36**. The CSV ends at 14:36:36, consistent at minute precision. Which accelerometer, centering/window definition, consecutive versus accumulated counts and reset behavior are unspecified. The omitted third accelerometer might matter. We did not reconstruct or tune this alarm, assign a failure time, or treat the final row as an event label. The operator's changed rule makes the endpoint protocol-dependent.

**B04:** log p. 1 adds a temperature-dependent loading policy missing from the short general table. At a documented temperature decision after 60 minutes, >60 °C retains `Thigh`: 1500–3000 rpm, 2500–3800 N static and 500–1500 N dynamic; the lower-temperature alternative is 2400–3600 rpm, 3300–3800 N static and 750–1700 N dynamic. Combined commanded load is 4000–5000 N. Log p. 2 records selection of the higher-temperature ranges at **13:45**. Neighboring CSV rows show T1/T2 around 60 °C; they support the recorded context but do not identify an exact activation instant. The **60 °C decision is a loading policy, not a failure label**.

Before that logged clock time, the active initial policy is unspecified: 160 non-warm-up rows are explicitly flagged ambiguous, and checks use per-variable envelopes across the documented alternatives. After 13:45, checks use the logged Thigh ranges. This source-clock association is itself provisional; it does not estimate operating time. No nominal setpoints fall outside these applicable ranges. The B04 combined-warning count includes initial-policy ambiguity, producing 210 rows. This changes only quality bookkeeping; candidate feature definitions and comparison bins are unchanged.
The implemented pre-decision limits are per-variable envelopes of the two documented alternatives, not a claim to know the active joint policy. Independently checking the joint alternatives found all 160 initial rows within Thigh bounds, but that alone does not establish which policy was active. Combined static-plus-dynamic commands in B01/B02/B04 are within their documented log ranges using a fixed **1e−8 N CSV-roundoff tolerance**: exported sums can be about 5e−12 N below a boundary. This numerical guard is not a tuned physical/alarm tolerance; no source value is changed. The quality companion records the sums and outside-range flags (zero violations in each run).

At **18:26**, the log says accelerometer RMS exceeded the specified limit; the CSV ends 18:26:58. The log does not supply a numeric limit, channel, exact RMS implementation or event time. Do not borrow B02's 0.65 V or infer damage onset/RUL from this wording. B01's earlier termination contradiction also remains unresolved.

## Feature compatibility, histories and comparisons

Feature formulas are unchanged from feature_definitions.md: per-channel own-burst mean-removed RMS in V, centered-peak/RMS crest factor, and biased population-moment excess kurtosis; T1/T2 minus room temperature in °C. Zero variance yields zero RMS plus missing ratios and explicit flags. No filtering, clipping, fitted scaling, feature selection or extra target columns were added. Context/provenance/quality roles and the explicit 11-column candidate allowlist remain distinct, with no default model inputs. B04's additional initial-policy flag, per-run inventory and policy-aware range checks are the documented differences (schema development-burst-features-v1.1).

Per-run histories show all three vibration descriptors, thermal differences, and measured/commanded speed and loads. Warm-up is blue, unobserved >24 s gaps gray, B04's initial-policy uncertainty orange, and channel sensor-range warnings red. Points never bridge gaps. Within-run condition plots retain every observation, count row warnings and mark sparse groups.

The original **250 rpm × 250 N static × 250 N dynamic-peak**, half-open **measured-value** bins are unchanged; warm-up stays separate. Four loaded bins have at least 20 observations in B01 and B02:

| Lower bin edges rpm / static N / dynamic peak N | B01 n (warnings) | B02 n (warnings) | B04 n |
| --- | ---: | ---: | ---: |
| 2500 / 3500 / 500 | 31 (0) | 62 (0) | 0 |
| 2750 / 3250 / 750 | 28 (1) | 108 (1) | 0 |
| 2750 / 3500 / 750 | 26 (2) | 64 (0) | 0 |
| 2500 / 3250 / 750 | 23 (1) | 93 (0) | 0 |

These support descriptive cross-run comparisons, not matched health or causal differences. Repeated bursts are not independent experiments; temperature history and unobserved rig state can differ within the same bin. B04 has **zero loaded-bin overlap** with either other run using its reported measured context. This is not proof that actual physical conditions never overlapped: measurement interpretation is unresolved. No multiplier or broader bin was used to manufacture support. B04's 24 nonsparse groups support within-run descriptions only, with its context warning retained. The n<20 display rule is unchanged and is not a significance guarantee.

**Observed descriptors:** B02 A/C RMS ranges are 0.0158–0.7460 / 0.0117–0.4702 V; B04 ranges are 0.0140–0.8719 / 0.0104–0.5386 V. B04 C crest factor reaches 15.96 and excess kurtosis 5.98 without nominal ±50 g exceedances. Higher moments need not track RMS or terminate at the same maximum. T1/T2 above room reach 47.54/47.16 °C in B02 and 41.75/41.01 °C in B04. None of these facts establishes a healthy period, onset or failure.

## Verification and next objective

The final B02/B04 tables contain all 2230 recordings, with raw SHA256 matches before/after processing and against the original acquisition manifests. All **58 tests pass**, including explicit run support, the unchanged formulas, all-sample grid/finiteness rejection, B04 log-policy handling, future-data independence, absent support under native bins, combined-command roundoff handling and held-out denial before waveform/table I/O. B01 tests and the synthetic demo are retained. Verification results are in project_status.md.

A feasible first future objective is **next-observed-burst voltage RMS forecasting**, benchmarked against persistence, rather than failure prediction/RUL. The [proposed modeling protocol](modeling_protocol.md) fixes availability, experiment-level partitions, gap rules and a held-out process. B04 context interpretation and all endpoint/clock caveats limit physical claims; B03 must remain sealed until a complete protocol and blind measurement-validity checks are frozen. No model or forecast target table was created in this task.
