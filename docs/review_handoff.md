# Technical review and sealed reserve handoff

## Prioritized review agenda

1. **Measurement meaning:** check official per-run calibration, 10 g/V versus
   voltage descriptors, sensor response/range, provisional ordinal CSV/MAT link
   and clock semantics. Resolve B04 speed/load interpretation from independent
   acquisition evidence. Do not use forecasts to infer a correction.
2. **Leakage and coverage:** inspect pre-search manifest, chronological source /
   target purging, validation-history reset, source feature allowlist, training-only
   scaler means, common versus broad masks and missing-value exclusions. Verify
   all results, including unsupported conditions and unfavorable direct models.
3. **Selection claims:** only B01/B02 supply development selection; both have been
   repeatedly inspected. Check equal-run/channel weighting, inner-only settings,
   simplicity rule, final alpha .5 versus direction-specific .2/.5, and the small
   independent-run count. B04 is not a third clean test.
4. **Monitoring interpretation:** inspect event evidence, reference counts and
   warning inclusion. Quartiles are development distributions, not healthy ranges.
   Low short-horizon error can coexist with a rising level; inspect the gradual
   change view alongside speed/load/temperature. No fault alarm metrics apply.
5. **Application and reproducibility:** test a fresh install, portable export,
   SQLite restart/reset, Unicode paths, Windows CI, artifact hashes and dependency
   compatibility. Review local pickle trust and the single-user loopback scope.
6. **Reserve readiness:** review the frozen procedure below before authorizing
   B03. Do not use review questions as reasons to inspect its trends early.

## Prepared, not executed: B03

`python -m factoryguard.release freeze --results reports/local/release-v3
--output reports/local/reserve-plan` creates an inspectable plan with final
settings, implementation hashes, development support counts, validity rules and
an all-false attestation template. It reads only development artifacts/tables.
The committed copy is configs/reserve_plan.json. A dry run is safe:

```bash
python -m factoryguard.release.holdout --plan configs/reserve_plan.json
```

It prints the plan without accessing a B03 path. No actual reserve check,
feature extraction, signal statistic, plot or score has been performed in this
release. Ordinary development loaders still deny B03. New lower-level pure
primitives are used only behind the dedicated reserve execution gate.

After the user's pipeline review and separate authorization, an independent
reviewer must attest the B03 log's measurement units/calibration/acquisition and
documented command/warm-up policy before waveform-derived analysis. Record source
pages and interpretation; retain provisional clock/ordinal caveats. If the fixed
meaning cannot be established, declare not evaluable. Do not alter the model or
replace the run. The template requires explicit booleans and plan hash; it is
an audit record, not cryptographic proof that a human did the review.

Only in that later authorized task:

```bash
python -m factoryguard.release.holdout --plan configs/reserve_plan.json --execute-after-review-approval --attestation /path/to/reviewed-attestation.json --raw-root /path/to/raw/B03 --archive /path/to/B03.zip --output reports/local/B03-once
```

Execution checks implementation hashes and attestation before reserve I/O; then
published archive MD5, extracted sizes/CRCs, 614-row/MAT inventory, exact CSV
alignment/increasing times and every waveform's real finite A/C vectors, 204800
samples, zero-based 128 kHz grid and 1.6 s duration. It streams one burst, writes
derived features separately, and verifies raw hashes unchanged. Structural or
meaning failures make the entire run unevaluable under the fixed rule; no tuning
or favorable exclusions. Range warnings remain in results. The executable is
tested on generated files only, including constant-signal missingness and gaps.

Then evaluate frozen smoothing alpha .5 and persistence once, reporting per-channel
common/broad MAE/RMSE, coverage, warnings/support and pending/expired forecasts.
No refitting, correction, labels or threshold selection. A fresh output is required
and an attempt manifest is written; social/review control, not a software lock,
enforces the one-shot rule. Save failure records too. One reserve bearing is one
laboratory case study, not population generalization, fault detection or RUL proof.

## Evidence still needed

More independent compatible bearing runs with verified measurement meaning and
predeclared train/evaluation roles are needed to estimate generalization stability.
Broader operating coverage, physical sensor calibration and clarified endpoints
are needed before fault/RUL objectives are defensible. No additional data is
downloaded automatically. The supported local investigation application can be
used while those scientific limitations remain explicit.
