# B01 burst features, version 1

Current release-v3 adds a separate 27-input modeling variant without altering
these burst tables/formulas. It extends selection-v2's 14 inputs with trailing
three RMS means/std (population, ddof=0), prior-to-current thermal and measured
context changes, and current crest/kurtosis. Changes are per observation, not
time rates; histories reset at experiment/gap/split boundaries. See
release_protocol.md for the frozen definitions, complete-feature availability
and current-versus-enriched comparison. Selected smoothing uses only A/C RMS.
Contextual completed-observation comparisons are explicitly separate from future
forecast inputs. Earlier milestone-specific model prohibitions below are history.

Extension 2026-10-23: the same candidate formulas, centering, kurtosis estimator,
units, missing-value conventions and column roles are now reused for B02/B04.
See [development_assessment.md](development_assessment.md) for per-run log
confirmation, full validation and necessary quality-policy differences.
New-run schema version is development-burst-features-v1.1; B01 artifacts and
default API behavior remain unchanged. B03 is denied by waveform/feature/plot
entry points and remains held out. Cross-run bins remain exactly 250 rpm ×
250 N × 250 N on reported measured values.

B04 uses its documented temperature-dependent setpoint policy: before the
logged 13:45 decision, the active initial policy is uncertain and explicitly
flagged, with per-variable range envelopes across documented alternatives;
after it, checks use the logged Thigh bounds. Its combined local warning
includes this uncertainty. A separate recording_diagnostics.csv quality
companion flags B04 operating-context interpretation unresolved for all rows
and records measured/commanded ratios and differences without fitted
correction or discrepancy thresholds. These post-hoc quality annotations
are excluded from model inputs and are not online forecasts. Zero-command
ratios are missing with explicit flags. The common feature allowlist is
unchanged; no suspect raw values are dropped, clipped or rescaled.

The later forecast-v1 pipeline uses a separate explicit seven-column allowlist in configs/forecast_v1.json. The extractor schema retains an empty default model-input list: it never automatically feeds numeric metadata into a model. Definitions and historical feature-milestone results below remain unchanged.

## Scope and command

This milestone produces exactly **377 rows**, one per B01 vibration burst. It uses the observed format and source assumptions in [dataset_assessment.md](dataset_assessment.md). It does not create failure/RUL labels, fit normalization, or train/evaluate a model. Source files remain outside Git. Generated tables and plots are ignored local outputs.

From `/workspace/factoryguard`, using the existing virtual environment:

```bash
export MPLBACKEND=Agg
export MPLCONFIGDIR=/tmp/factoryguard-matplotlib
export XDG_CACHE_HOME=/tmp/factoryguard-cache
export OPENBLAS_NUM_THREADS=1
.venv/bin/python -m factoryguard.pipelines.features_paderborn \
  /workspace/datasets/paderborn-10868257/raw/B01 \
  --output reports/local/b01-features-new
```

The output directory must be new or empty and outside the raw-data directory. The CLI requires all 377 measurements. Python API overrides of the expected count exist for generated acceptance fixtures only; they do not make a partial experiment equivalent to B01.

The executed result is `reports/local/b01-features-v1/`, containing:

| File | Contents |
| --- | --- |
| `features.csv` | One row per burst, both channels, thermal/context values, provenance and quality |
| `schema.json` | Complete column list, roles, units, missing-value convention and candidate allowlist |
| `raw_integrity.json` | SHA256 hashes for every raw file, verified identical before/after extraction |
| `extraction.json` | Row count, warning counts, memory/runtime, comparison policy and limitations |
| `condition_counts.csv` | Counts and warning counts for every fixed operating-condition bin |
| `condition_comparisons.png` | Features within the four most populated loaded-operation bins |
| `condition_support.png` | All bins, including warm-up, with sample counts and sparsity warnings |

## Window and availability contract

Each source MAT file is one **1.6 s** window with **204,800 samples per channel at 128 kHz**. Both A and C are processed independently using all samples in that burst. There is no overlap, cross-file concatenation, waveform interpolation, resampling, clipping, filtering or rolling aggregation. Only the current recording's arrays are retained; the small descriptor table may be loaded for plots after extraction.

Features become available only after the entire burst is observed. All centering and moment calculations therefore use already-observed samples at that decision point. CSV-to-MAT mapping remains ordinal (M0001 to CSV row 1); absolute clock alignment is not independently verified. CSV `Time` has no timezone, and whether it marks acquisition start, end or another event is unknown. Source strings are retained; no absolute feature-availability timestamp is invented by adding 1.6 s.

The preceding CSV interval uses only the current and previous source times. Intervals strictly greater than **24 s** are flagged and start a new diagnostic acquisition segment. This is an inspection heuristic, not a missing-data repair or failure criterion. The first preceding interval is unknown/missing, not zero. Warm-up transitions are separately flagged. No feature bridges a gap or needs segment-level normalization.

## Exact vibration formulas

For one channel, let its real voltage samples be `x_i`, `i=1,...,N`, with `N=204800` for B01. Define:

- Arithmetic mean: `mu = (1/N) * sum(x_i)`.
- Within-burst centered samples: `y_i = x_i - mu`.
- Central population moments: `m2 = (1/N) * sum(y_i^2)` and `m4 = (1/N) * sum(y_i^4)`.
- Centered peak: `p = max(abs(y_i))`.

| Candidate field, for each `A` and `C` | Definition | Unit |
| --- | --- | --- |
| `feature__A_ac_rms_v` / `feature__C_ac_rms_v` | `sqrt(m2)` | V |
| `feature__A_crest_factor` / `feature__C_crest_factor` | `p / sqrt(m2)` | Dimensionless |
| `feature__A_excess_kurtosis` / `feature__C_excess_kurtosis` | `m4 / m2^2 - 3` | Dimensionless |

The kurtosis estimator is the **biased central-moment estimator**, using denominator N for both moments, with Fisher excess convention (subtract 3). There is **no finite-sample bias correction** and no N−1 variance correction. For nonconstant signals this matches `scipy.stats.kurtosis(x, fisher=True, bias=True)` up to floating-point rounding. Excess kurtosis may legitimately be negative; it is not clipped.

For numerical stability, the implementation computes moments of `z_i=y_i/p`, then restores RMS as `p*sqrt(mean(z_i^2))`; crest factor is `1/sqrt(mean(z_i^2))`. The fourth/second moment ratio is scale invariant. This temporary within-formula scaling is numerical stabilization, not fitted normalization. There is no global experiment statistic or future-data dependency.

Exactly constant vectors are detected by equality of all samples. Their mean is set to the constant itself to avoid summation rounding creating artificial variance (for example, repeated 0.1). They return RMS **0 V**, crest factor **missing**, excess kurtosis **missing**, and explicit per-channel `zero_variance`, `crest_factor_undefined` and `excess_kurtosis_undefined` flags. Missing values are empty CSV cells and NaN when read with pandas; they are never replaced with zero. No near-zero epsilon is used to classify small but varying signals as constant. Nonfinite, complex, empty or malformed input is rejected rather than converted into apparently valid features.

The earlier inspection table used uncentered RMS; this feature table deliberately uses mean-removed RMS. They obey `uncentered_RMS^2 = ac_RMS^2 + mu^2` within rounding. The DC mean is retained only as a quality diagnostic.

## Voltage, sensor range and thermal quantities

Raw vibration and RMS remain in **V**. The B01 log states **10 g/V at 0 dB gain**. Under that stated linear conversion, RMS in g would be `10 * RMS_in_V`, and crest factor/kurtosis would be unchanged. Candidate features are not converted to g and no stronger calibration claim is made.

Sensor-range quality counts use the **original uncentered samples**: `count(abs(x_i) > 50/10)` = `count(abs(x_i) > 5 V)`. Equality at ±5 V is not an exceedance. Raw absolute peak and DC mean are quality fields, not candidate inputs. Centering cannot erase a raw over-range warning. Exceedance does not prove clipping, and absence of exceedance does not certify physical accuracy. All samples remain in the feature calculation, with flags retained.

These are unfiltered voltage descriptors. The 128 kHz sample rate does not establish calibrated response out to 64 kHz: the documented accelerometer response is about 0.5–10 kHz, with resonance near 25 kHz. No spectral fault diagnosis is made. Features from flagged recordings, especially peaks and higher moments, need calibration/range investigation before predictive use.

Thermal candidates use the same ordinal CSV row:

- `feature__T1_above_room_c = T1 - room_temperature`.
- `feature__T2_above_room_c = T2 - room_temperature`.

These are differences in °C. They are not standardized or smoothed. The source CSV supplies temperature summaries; this pipeline does not reconstruct a 10 Hz temperature waveform.

## Roles and selection policy

A column's numeric dtype does not make it a model input. `schema.json` explicitly separates:

| Prefix / category | Meaning and policy |
| --- | --- |
| `feature__` | Eight candidate descriptors: six vibration features and two thermal differences |
| `context__` | Measured speed (rpm), measured mean absolute static load (N), measured dynamic-load peak (N), their corresponding setpoints, and original T1/T2/room temperatures |
| `provenance__` | DOI, experiment, measurement ID, MAT path and SHA256, original source time, unknown timezone/timestamp semantics, provisional ordinal alignment, feature availability and acquisition dimensions; never automatically inputs |
| `quality__` | Gap/segment diagnostics, warm-up/regime flags, setpoint warnings, per-channel raw DC/peak/range counts, zero-variance/undefined-moment flags and combined warning; never automatically inputs |

`candidate_input_columns` is an explicit **11-column allowlist**: the eight features plus measured speed, measured static load and measured dynamic peak. It excludes IDs, hashes, timestamps, warning flags, segments, commanded setpoints and absolute temperatures. These retained context fields can support inspection without being silently added to a future model. `default_model_input_columns` is empty: actual input selection requires a future explicit decision, especially while alignment is provisional. Do not use `select_dtypes` to choose all numeric columns.

Warm-up matches the logged setpoints exactly: 750 rpm, 2500 N static load, zero dynamic amplitude. It is a regime flag, not a healthy label. Main-run warnings compare non-warm-up setpoints against 2400–3000 rpm, 3300–3800 N static load and 500–1400 N dynamic amplitude, inclusively. Measured and commanded values remain distinct.

`quality__any_warning` combines warm-up, a warm-up regime transition, a preceding interval >24 s, any out-of-range main-run setpoint, a channel sensor-range exceedance or zero variance. It is a convenience flag, not a judgement that the whole row is invalid. A raw-range issue on A can therefore ring both plotted A/C observations as a row warning; inspect the channel-specific flags to locate the cause. Provisional alignment and unresolved failure criteria are global limitations even on rows without this combined warning.

No quality mask is applied to extraction or plots. All 377 rows remain present. For malformed source data the command fails with an error instead of silently skipping a burst. A checksum change during extraction prevents publication of the final feature CSV; diagnostic partial output remains explicitly named `.partial`.

## Comparing operating conditions

Condition plots use **measured**, not commanded, values in fixed half-open bins:

- Speed: `[250*k, 250*(k+1))` rpm.
- Static load: `[250*k, 250*(k+1))` N.
- Dynamic-load peak: `[250*k, 250*(k+1))` N.

Each dimension uses its own integer k (`floor(value/250)`). Warm-up and loaded operation are grouped separately. Bin widths are explicit inspection choices, not fitted scaling or normalization. Coarse bins do not remove within-bin speed/load variation, temperature effects or clock uncertainty. With only per-burst operating summaries, within-burst stationarity cannot be established.

`condition_counts.csv` covers every group and sums to all 377 bursts. Counts distinguish total rows, rows with/without the combined warning, channel range warnings, setpoint warnings and preceding-gap warnings. A group is marked sparse when total n<20; a separate flag notes fewer than 20 rows without warnings. Twenty is a display heuristic, not a significance criterion or a claim of independent samples.

`condition_comparisons.png` shows AC RMS, crest factor and excess kurtosis for A/C within the four largest non-warm-up bins. It retains flagged points with red rings, reports total and warning counts, and reports missing A/C values that cannot be plotted. Point positions use provisional CSV times; no line bridges a gap. `condition_support.png` shows all groups, including groups absent from the comparison panels, with n<20 in orange and warm-up gray. Plot selection uses the complete descriptor table solely for offline display; neither grouping nor panel selection affects features or quality/provenance rows.

## Executed result and acceptance evidence

The real B01 run produced **377 rows**, with no undefined candidate cells in this dataset. Constant-signal behavior is exercised with generated fixtures. It retained 51 warm-up rows, 33 speed-setpoint warnings, four preceding-gap warnings, 10 A-channel range-warning bursts and one C-channel range-warning burst. There are 96 combined-warning rows; warning categories overlap.

All **380 source files** matched SHA256 hashes before and after extraction. The run took **15.111 s** and reported **149.02 MiB peak process RSS** on Linux, including plotting. The one-recording memory strategy is also tested by checking that requesting one feature row loads only one waveform. Small tables, file paths and hashes are retained; experiment-sized arrays are not.

There are **51 condition groups**, **46 with n<20**. The four displayed loaded-operation groups contain 31, 28, 26 and 23 bursts, respectively. These are repeated observations from one experiment, not independent experiments or evidence of predictive performance.

The 18 new acceptance tests cover analytic alternating and sinusoidal signals, an impulse checked against SciPy's specified estimator, offset/scale behavior, tiny nonconstant inputs, constant/zero variance, nonfinite input rejection, raw range counting before centering, CSV missing-value encoding, separate channel flags, thermal/context mapping, gap preservation, retained suspect samples, explicit input roles, lazy loading, overwrite/raw-output protection, raw-change detection, and condition-group counts/sparsity. Future-data independence is tested by changing a later waveform and its temperature, operating values and timestamp, then checking **every field in earlier output rows remains identical**. Global integrity manifests and offline plot selection can legitimately change; they are not feature inputs.

Independent checks against the real output verify all 377 IDs, original warning totals, the AC/DC RMS identity for every burst, and direct RMS/crest/SciPy-kurtosis calculations for M0001/M0189/M0377. No failure labels, learned normalization, model fitting, or model evaluation occurs.


## Selection-v2 temporal extension

Base burst definitions and raw tables remain unchanged. The separate selection pipeline compares the same seven current regression inputs with a fixed 14-column set: add prior A/C RMS, current-minus-prior A/C RMS, and trailing-three-observation means of measured speed/static/dynamic context. All are past/current only; require three complete finite-history observations, reset across >24 s gaps, experiments and inner validation boundaries. See selection_protocol.md for exact availability and split/purge rules. No ID/quality/provenance fields become predictors. Persistence and the selected exponential smoother consume only A/C RMS; the broader seven-column regression allowlist does not describe their actual inputs. No fitted imputation or B04 scaling correction was introduced.
