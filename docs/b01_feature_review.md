# B01 feature review — 2026-10-22

## Verification and missing values

Reviewed feature_definitions.md, schema.json and the actual 377-row, 54-column table. All 754 channel/burst feature sets were recomputed from raw signals using independent NumPy/SciPy formulas. Maximum absolute differences were 2.22e−16 V for RMS, 1.78e−15 for crest factor and 3.94e−15 for excess kurtosis. Thermal features, operating context, all quality flags and all group counts were independently reconstructed. The 11 candidate columns are finite; schema roles are disjoint and complete, and default model inputs remain empty.

There are **no missing/undefined candidate features**. The only missing table cell is M0001's preceding-gap value, correctly paired with `preceding_gap_unknown=true`: there is no preceding observation. No channel has zero variance or undefined crest/kurtosis flags in B01. Constant-signal behavior is covered by generated-fixture tests; it cannot be inferred merely from this complete real-data table. Negative excess kurtosis and initially slightly negative temperature-minus-room values are valid signed values, not missing data.

All 380 raw SHA256 hashes and the original feature artifacts still matched after the audit. Audit evidence: `reports/local/b01-feature-review/audit.json`; repeat with `.venv/bin/python reports/local/b01-feature-review/review.py` using the documented writable plotting caches. Historical extraction runtime/RSS come from the saved extraction log, not this audit.

## Histories and descriptive findings

[Vibration histories](../reports/local/b01-feature-review/vibration_histories.png) show A/C RMS, crest factor and excess kurtosis. [Thermal and operating histories](../reports/local/b01-feature-review/thermal_operating_histories.png) show T1/T2 above room temperature alongside measured speed, static load and dynamic peak. Dots retain every burst; no interpolation bridges gaps. Blue identifies warm-up; gray marks >24 s acquisition gaps; red diamonds mark channel-specific nominal range warnings. Red rugs on the context plot refer to vibration warnings, not temperature/load faults. CSV clock meaning, timezone and ordinal MAT alignment remain provisional.

**Observed:**

- RMS spans 0.0146–1.4461 V for A and 0.0102–0.8617 V for C. Later amplitudes are higher, but the histories are not monotonic and operating conditions vary. The A RMS maximum is M0375, where both channels have range warnings.
- Crest-factor maxima occur at M0210: A 7.018, C 12.696, neither with a range warning. Both excess-kurtosis maxima occur at M0375: A 2.821, C 3.154. Thus amplitude and impulsiveness descriptors do not have identical histories; no single threshold or onset follows from them.
- T1/T2 above room temperature reach 96.85/93.67 °C at M0372. They are initially −0.037/−0.139 °C. The large 09:13:24–09:32:31 gap is followed by lower observed temperatures; the interval itself is unobserved.
- All 51 warm-up, 33 unusual-speed-setpoint, four long-gap and ten A/one C range-warning observations remain present. The 96 combined-warning rows overlap across categories; the remaining rows are not certified healthy.

**Possible explanations, not findings:** load/speed changes, thermal history, a pause/intervention, evolving mechanical behavior or acquisition/calibration effects could influence these histories. Range exceedances do not establish clipping. The conflicting termination records and postmortem defects do not identify damage onset, a failure timestamp or RUL labels.

## Comparison support

The original groups are unchanged: fixed half-open **250 rpm × 250 N static × 250 N dynamic-peak** bins, using measured values, with warm-up separate. All 377 observations appear in 51 groups; 46 groups have n<20. Twenty is a display heuristic, not a significance or independence criterion.

| Speed rpm | Static N | Dynamic peak N | Total n | With row warning |
| --- | --- | --- | ---: | ---: |
| [2500,2750) | [3500,3750) | [500,750) | 31 | 0 |
| [2750,3000) | [3250,3500) | [750,1000) | 28 | 1 |
| [2750,3000) | [3500,3750) | [750,1000) | 26 | 2 |
| [2500,2750) | [3250,3500) | [750,1000) | 23 | 1 |

These four loaded groups have useful support for inspecting repeated descriptor behavior within coarse operating ranges. They do not establish matched health or causal effects. For example, the largest group has only **2/1/28** observations in the first three existing acquisition segments; A median RMS is **0.1019/0.1199/0.4476 V**, respectively. The early samples are too few for a reliable early-versus-late conclusion. All other loaded bins remain sparse under the existing rule. Warm-up has 51 observations but a different regime and is not a loaded-operation reference. No groups were broadened to obtain support.

## Next independent experiments

The initial recommendation—B03 as the smallest matched-condition independent run, B02 as another matched run with vibration termination, then B04 for wider speed/load coverage—uses only official PDF pp. 3–8 and Zenodo archive metadata. Under the user's subsequent acquisition authorization, roles were declared **before** new signals were inspected: B02/B04 development, **B03 proposed held-out reserve**. See [experiment_roles.md](experiment_roles.md) for exact sizes, checksums, selection rationale and restrictions. No new-run feature trends or distributions belong in this B01 review; held-out B03 is limited to integrity/structure. Documented endpoint types still require future independent clarification before any evaluation labels are justified.
