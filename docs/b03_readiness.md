# Next scientific task: readiness for a sealed B03 evaluation

This is a checklist, not authorization to open B03. No B03 data was accessed for
this documentation release. The [existing review handoff](review_handoff.md) and
[reserve plan](../configs/reserve_plan.json) remain unchanged.

- [ ] Complete an independent full pipeline review: acquisition/units, feature
  formulas, CSV/MAT association, causal issuance, gap and split resets, missingness,
  target availability, purging, training-only preprocessing, eligibility and reports.
- [ ] Freeze the reviewed method and environment before reserve access: smoothing
  alpha 0.5 versus persistence, no learned scaler/imputer for smoothing, the fixed
  finite-history/common-pair rules, >24 provisional-clock-second expiry and
  experiment resets. Keep warnings and broader baseline coverage separate.
- [ ] Freeze per-channel common MAE/RMSE and persistence skill, equal-channel
  aggregation, coverage/exclusions, operating-support/quality strata and the
  whole-run unevaluable rules. No alarm thresholds, labels or new selection.
- [ ] Verify the plan, final artifact, search manifest and implementation hashes
  against the exact reviewed checkout. The current plan SHA256 is
  `e7f2a0f7f6be1a3798c9a002890e17aa0b9f4ab1397572c444744121eb81186f`.
  A code-only check at master `fc772e5` found all seven implementation hashes
  matching. Final artifact/search-manifest hashes still need rechecking against
  the retained trusted artifacts before any future execution. Do not regenerate
  or edit the plan to bypass a mismatch; stop for review and documented resolution.
- [ ] Obtain separate authorization and an independent measurement-meaning review
  **before signal/outcome inspection**. Establish units, calibration, sampling,
  warm-up/command meaning, provisional timestamp/ordinal limits and termination
  ambiguity from documentation. Complete the existing attestation with source
  references. If meaning cannot be established, declare the run unevaluable.
- [ ] After authorization and validity gates, perform **one** frozen evaluation
  against persistence. Preserve unfavorable results, failures, warnings,
  unsupported conditions, excluded pairs and pending/expired forecasts. Do not
  refit, correct measurements, tune thresholds, choose a replacement run or select
  features from B03. Retain the attempt record even if evaluation fails.

One held-out bearing is one laboratory case study. It cannot establish population
generalization, fault detection, damage onset, health classes or RUL.
