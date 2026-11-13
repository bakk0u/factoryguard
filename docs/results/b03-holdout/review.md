# B03 reserve: pre-execution review record

Written and committed **before** the reserve evaluation was executed. It records how each
gate in the [readiness checklist](../../b03_readiness.md) was met, and where a gate could
only be met in substance rather than to the letter.

## Authorization

The repository owner was asked on 2026-11-13 whether to authorize one frozen B03 evaluation
against persistence, told that it is a one-time, irreversible step and that an unfavourable
result would be kept, and answered "Authorize B03 once".

## Independent pipeline reproduction

Done in a fresh environment (Python 3.13, scikit-learn 1.9.1, xgboost 3.0.5, numpy 2.5.4)
from archives downloaded directly from Zenodo record 10868257.

| Check | Result |
| :--- | :--- |
| Archive MD5 against the Zenodo record | B01, B02, B04 and B03 all match |
| Feature extraction B01 / B02 / B04 from raw waveforms | SHA-256 of all three `features.csv` files **identical** to the published `table_sha256` |
| Development selection campaign rerun (32 candidates, 192 fold evaluations) | Same selection: smoothing, final candidate `smoothing_0.5` |
| `development_metrics.csv` (288 rows) and `stress_metrics.csv` (144 rows) against the published files | Every persistence, smoothing, tree, boosting and XGBoost value identical; Ridge values differ by at most 9e-13 relative (floating point) |
| Method ranking and qualification flags, all 18 groups | Identical |
| Seven implementation hashes in `configs/reserve_plan.json` | Match the current source |
| Plan SHA-256 | `e7f2a0f7f6be1a3798c9a002890e17aa0b9f4ab1397572c444744121eb81186f`, unchanged |
| Test suite | 183 passed before this work |

Reviewed in code: causal issuance (the forecast for burst *t+1* reads only bursts up to *t*),
history resets at gaps over 24 s and at experiment boundaries, no scaler or imputer for the
smoothing rule, the common-mask and finite-history rules, and that the reserve runner
performs no fitting.

## Gate met in substance, not to the letter: artifact hashes

The checklist asks to recheck `final_artifact_sha256` and `search_manifest_sha256` "against
the retained trusted artifacts". Those artifacts live in the owner's original local
workspace and are not in this repository. The rerun here produces files with **different**
hashes, for a reason that was checked: the search manifest embeds a hash of a config that
contains absolute table paths, and the joblib artifact embeds interpreter-specific pickling.

Resolution, recorded rather than worked around:

- the plan was not regenerated or edited;
- neither file is read by the reserve execution: the frozen method is the state rule
  "exponential smoothing, alpha 0.5", defined in hash-pinned source, with no pickle loaded;
- what those hashes were meant to protect, that the frozen method is the one development
  selected, was established more strongly by reproducing the selection and every metric from
  raw data.

A reader who requires the literal hash comparison should treat that single item as open.

## Measurement meaning (documentation only, before any signal access)

Only `B03_log.pdf` was extracted and read before execution.

| Attestation | Evidence |
| :--- | :--- |
| Volts, 10 g/V, 0 dB | B03 log p. 1: "unit of the saved vibration data is Volts", conversion 10 g/V, gain 0 dB |
| 128 kHz, 1.6 s | B03 log p. 1; dataset description p. 5 (128 kHz up to B09) |
| Warm-up and command ranges | Log p. 2: 10 min at 750 rpm, 2500 N, no dynamic load. Log p. 1: 2400-3000 rpm, 3300-3800 N static, 500-1400 N dynamic at 2 Hz, combined 4300-4900 N. Same as B01/B02 |
| Ordinal alignment and clock limits | MAT files carry only relative sample time; measurement id to CSV row is an ordinal link, timestamps have no declared time zone. Accepted as a stated limit, as for B01/B02 |
| Termination not used as a label | Log p. 2: automatic stop at 110 °C housing temperature after about 3 h 13 min. Recorded as context only; no label, threshold or alert is derived from it |
| No inspection for selection | No B03 signal, feature, plot or score existed when the method, metrics and interval calibrator were frozen (see git history) |

Shaft speed: an independent spectral check on B01/B02 shows the logged measured speed agrees
with the rotation frequency visible in the vibration spectrum
([measurement validity](../measurement-validity/README.md)); B03 shares their documented
command ranges.

## What will be run, once

```bash
python -m factoryguard.release.holdout --plan configs/reserve_plan.json \
  --execute-after-review-approval --attestation docs/results/b03-holdout/attestation.json \
  --raw-root <raw>/B03 --archive <B03.zip> --output <fresh directory>
```

Frozen smoothing alpha 0.5 against persistence; per-channel common MAE/RMSE and skill,
equal-channel macro ratio, coverage, strata and transitions. Then the interval calibrator
frozen in [`uncertainty_calibration.md`](../../uncertainty_calibration.md) is applied once
to the saved forecast pairs. The outcome is published whatever it shows.

## Reviewer

The review and attestation were carried out by an AI assistant (Claude) at the owner's
request, independent of the tools that built the pipeline but not a human bearing or
measurement specialist. The attestation is an audit record of what was checked and against
which pages, not expert certification.
