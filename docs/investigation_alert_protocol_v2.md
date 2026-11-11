# Investigation alerts v2 — one frozen final policy

2026-11-10. This amendment addresses fresh evidence, signal availability and
long-episode interpretation only. The v1 protocol/configuration, first evaluation
and correctness recheck remain immutable. One v2 candidate, no search or adjustment
after inspecting v2 development results. No fault labels, B03 access, reserve-plan
changes, model fitting or saved-forecast changes are authorized.

## Unchanged scientific contract

Reuse v1's B01/B02 calibration, validation and reserved development blocks, saved
forecasts, numerical thresholds and references: quantile .99, minimum 20 scores /
20 exact-bin reference observations, 3 IQR, 1e−9 V numerical floor, clear fraction
.6, activation/clearing persistence 3, window 3, gap limit 24 provisional CSV seconds.
No expanded bins, full-run statistics, adaptive baseline or healthy interpretation.
Calibration computes the exact v1 scores and values on each run/channel prefix.
Only provenance hashes identify v2. B04 remains unavailable diagnostic context.

Both versions' inspected development results are diagnostics, not independent
validation. No credible normal/fault intervals, damage onset or verified operating
exposure exist. Precision/recall, false alarms, missed faults and detection delay
remain unverified/null. Durations are observations, never operating hours.

## Fresh-evidence persistence

Retain the causal trailing-three **mean** versus fixed first-three segment mean;
no filter or threshold recalibration. Every score records its current scoring
observation positions separately from its reused baseline/history provenance:

- Residual: the current completed reading is the fresh innovation; the prior
  saved forecast/history is reused context, not an extra confirmation.
- Level: the three trailing reading positions are the scoring support; the fixed
  segment anchor is explicitly reused baseline support.
- Context: the current completed reading is the scoring support; the frozen
  prefix/bin is a reused reference, not new evidence.

For each signal, retain up to three high confirmations. A current eligible score
at/above activation is counted only if **all** its scoring positions are later than
the last counted scoring position. An overlapping high score is visible but does
not increment persistence. Any eligible below-activation score or ineligible score
resets that signal's high streak. Missing/gap/history reset clears all confirmation
and recovery histories. Different signals never pool votes. Shared baselines and
serially correlated measurements are not statistically independent evidence.

A single extreme reading after a stable anchor can contaminate up to three level
windows, but can contribute to only one level confirmation, so cannot activate the
level signal alone. Residuals still assess every new reading; three fresh high
residuals can activate an abrupt-change investigation. A single residual spike
starts Watch, not Active. Sustained steps and ramps can activate level persistence
using three disjoint high windows. Earliest level activation is the first high
window end plus six observations (instead of plus two); this is an explicit delay
tradeoff. A spike inside the initial anchor can bias the fixed baseline: this
existing limitation is not repaired by adaptation or represented as healthy data.

Recovery requires three quiet confirmations: all eligible signals below their
clearing thresholds, and every initiating/escalated signal eligible. Every required
signal's scoring support must be disjoint from that used for the prior recovery
confirmation. Nonquiet/ineligible evidence resets recovery; overlapping quiet
scores do not increment it. No stale repeated window can establish clearance.

## Per-signal monitoring and episode assessment

Every signal records eligibility, specific blocking/qualification reasons, units,
score/threshold, support positions, fresh-confirmation status and counted support.
Missing forecasts/history/calibration disable residual/level as applicable;
unsupported/missing context disables only context comparison. Quality flags and
invalid readings block the selected channel only. Warm-up and gaps retain v1 reset
semantics. Level comparison can remain usable but context-confounded, explicitly
qualified. Full monitoring means all three eligible without that confounding;
limited means some eligible or qualified; unavailable means no eligible signal.
No monitoring state or missing evidence asserts health. Replay never exposes later
calibration, another channel or beyond-cursor records.

Condition state remains No active alert / Watch / Active alert / Cleared. For an
active episode, separately report:

- Supported now: at least one currently eligible activation-level crossing.
- Unresolved, assessment unavailable: no current crossing and at least one required
  signal unavailable. Preserve the episode and explain missing evidence.
- Recovery pending: all required evidence eligible and all eligible signals quiet;
  show fresh recovery count until clearance.
- Unresolved, within hysteresis band: assessable but neither high nor quietly
  recoverable. Do not call this supported activation or healthy operation.

A new signal reaching its own fresh persistence escalates the **evidence scope**
of an existing episode. Add it to required recovery signals and reset recovery;
record why, without claiming physical severity or creating another activation
notification. Current assessment/reason and crossing evidence are stored every
frame; append transitions for assessment changes, new persistent signals, resets,
activation and clearance. Original activation records stay immutable. Acknowledgment
is a separate action and never changes condition/assessment. One activation and one
clearance notification per episode; no duplicate continuation/escalation delivery.
The investigation action selects evidence for human review without an LLM request.

## Frozen acceptance and diagnostic reporting

Before development evaluation, synthetic tests must establish: one isolated extreme
reading contributes at most one level confirmation and no activation; sustained
step/ramp can activate; residual abrupt-change path remains; disjoint support at
activation and recovery; unavailable initiating evidence cannot clear; hysteresis,
gaps, operating transitions, channel/replay/future isolation, duplicate suppression,
acknowledgment separation, append-only persistence/export and deterministic replay.
Provider tests are mocked; detection must work without an LLM/key.

Evaluate exactly the existing eight B01/B02 run/channel/block cells once for this
candidate. Retain unfavorable results. Report v1/v2 counts, active durations in
observations, assessment categories, per-signal coverage and reasons, fresh support
checks and unchanged calibration values. No target alert rate or performance score
is an acceptance criterion. Bugs may be corrected against this frozen policy with
any necessary rerun disclosed and original output preserved; do not tune outcomes.

Finish with full Python/TS checks, build, all 40 frozen lexical cases, browser
regressions, exports/citations/status display and frozen-artifact integrity. Preserve
offline default, explicit live opt-in, secret boundaries and existing request bounds.
No paid calls, new features, redesign, hosting, external delivery or further campaign.
