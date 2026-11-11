# Investigation alerts v1 — frozen before evaluation

2026-11-10. This task explicitly authorizes deterministic investigation alerts,
superseding the earlier forecast-only prohibition on thresholds for this milestone.
It does not authorize a forecasting campaign, B03 access or reserve-plan changes.
One policy candidate; no search or outcome-driven adjustment. The configuration
and this protocol are SHA256-frozen before running development alert evaluation.

## What is and is not labelled

Repository evidence: `dataset_assessment.md`, `development_assessment.md`,
`experiment_roles.md`, `feature_definitions.md`, `modeling_protocol.md`,
`selection_protocol.md` and `release_protocol.md`. B01 postmortem defects are
experiment-level; its general description/log/CSV disagree on termination.
B02 stopped around 13:32 and resumed with a different crossing-count rule; the
channel, precise RMS definition, accumulation/reset and event time are unknown.
B04's 18:26 stop lacks a numeric limit/channel/statistic; its 60 °C decision is a
loading policy. None supplies verified normal/fault intervals or damage onset.
Warm-up, range flags, gaps and operating-policy annotations are not fault labels.
No raw file or B03 log/feature/reserve artifact will be read for this milestone.

Outputs are **investigation alerts**, not diagnosed faults, healthy/safe states,
damage alarms, statistical significance or calibrated probabilities. Unusual
means relative to the specified development calibration, conditional on coverage.
Fault sensitivity, false-alarm rates, precision/recall and detection delay are
not identifiable from these annotations. Do not treat unlabelled periods as normal.

## Inputs, timing and calibration

Reuse the immutable, hash-pinned `site/source/replay.json` B01/B02 records and
existing saved selected-rule forecasts. Never refit/recompute/replace forecasting
results. They were already selected using B01/B02 development data; the new policy
blocks are not an unbiased previously unseen bearing test. A saved forecast may
carry earlier causal smoothing history; it is not retrained at an alert split.
All alert calculations use completed current/past observations only.

Fixed 1-based partitions (counts already documented before this milestone):

| Run | Calibration only | Validation | Reserved policy-evaluation block |
| --- | --- | --- | --- |
| B01 | 1–150 | 151–263 | 264–377 |
| B02 | 1–446 | 447–781 | 782–1116 |

Thresholds and references use only eligible values in that run/channel's calibration
prefix. Nothing alerts during calibration; no future prefix statistic is exposed
before the prefix completes. Exact linear empirical 0.99 quantiles; minimum 20
finite eligible scores per signal. A 1e−9 V floor is a numerical zero-scale guard,
not a physical damage threshold. No healthy interpretation or false-alarm guarantee
attaches to a calibration quantile. Freeze calibration after the prefix.

Evaluation initializes each validation/evaluation block independently with that
frozen prefix calibration and empty history/state. Its first saved residual is
withheld (prior observation outside block); RMS history cannot cross the boundary.
Saved forecasts themselves retain their original historical provenance. Runtime
dashboard replay is continuous after calibration and does not reset at the offline
evaluation boundary. Block initialization and continuous replay results are labelled
separately; no raw-dependency independence claim is made for saved forecasts.

## Three signals, each with inspectable units and provenance

1. **Residual:** absolute current selected-channel RMS minus the saved earlier
   forecast (V), after a valid preceding observation in the current block/segment.
   Activation threshold is the prefix score's 0.99 quantile.
2. **Sustained level:** absolute trailing-three mean RMS minus the first complete
   three-burst mean in the current eligible segment (V), starting at six observations
   so the windows do not overlap. This reuses the existing segment-anchor level
   definition, catching accumulated drift even when smoothing follows it. Activation
   threshold is the prefix score's 0.99 quantile. It is descriptive amplitude change;
   if operating bins differ in the segment, explicitly mark context confounding.
3. **Context comparison:** absolute RMS minus calibration-bin median, compared with
   3 × max(IQR, numerical floor). Use the existing half-open 250 rpm × 250 N static
   × 250 N dynamic bins, with warm-up separate; no wider fallback. Require 20 finite
   eligible calibration observations in that exact bin. No full other-run embedded
   reference or full-run statistic enters this new alert signal.

Any one signal can warrant an investigation. Activation requires **three consecutive
high observations of the same signal**; evidence streams are correlated and are not
independent votes. Switching which signal is high does not accumulate confirmation.
No requirement that all signals agree: a gradual level change can matter while
forecast residuals remain small. All values, thresholds, ratios and reference
support are retained, including unavailable signals and explicit reasons.

## Eligibility, availability, state and reset rules

Selected-channel RMS must be finite/nonnegative. Selected-channel sensor-range
exceedance or documented zero variance, warm-up, missing/nonfinite values and B04's unresolved diagnostic
context prevent monitoring. These are separate quality/availability findings,
not fault events. Other-channel values/flags do not gate this channel.
History resets at missing/invalid readings, warm-up and CSV gaps >24 s. The first
post-reset residual is unavailable. Unknown/nonfinite/nonpositive arrival intervals
also reset history. Exactly 24 s remains eligible. Experiment/channel state is
separate; out-of-order/duplicate processing is rejected by the pure engine.

Missing operating context prevents context comparisons; residual/level may still
support **limited** monitoring. Unsupported bins, unavailable scales, short history
and differing segment bins are explicit limitations. Availability is **available**
only when all three signals are eligible and context matches; **limited** when some
evidence is eligible; **unavailable** when none is eligible. It is independent from
condition state. Missing evidence never implies healthy operation.

- **No active alert → Watch:** first high eligible signal.
- **Watch → Active alert:** the same signal high for three consecutive observations.
  One immutable episode is created, with one activation notification.
- **Watch → No active alert:** three consecutive eligible quiet observations below
  clearing thresholds. Missing/gap invalidates the watch history, without claiming
  health or condition clearance.
- **Active alert → Cleared:** three consecutive observations where every initiating
  signal is still eligible and below 0.6 × its activation threshold, and no other
  eligible signal exceeds its clearing threshold. A never-supported signal is not
  mandatory for clearance; an unavailable initiating signal blocks clearance.
- **Cleared → Watch:** a new high condition starts a new episode after persistence.

While active, missing data, gaps or reset **retain the unresolved active condition**,
reset persistence/history and append a history-reset transition. They never clear
it. High evidence that persists after activation remains in the same episode; no
repeat activation notification. Condition clearance creates one local notification.
Acknowledgment is an independent append-only user action, never a clearance or
threshold input. Replay reset reconstructs the visible prefix; old journal records
remain immutable and are filtered by stream/run/channel/visibility. A reset may hide
an episode before its activation position, not claim it was cleared.

## Persistence, local delivery and evidence integration

Immutable episode activations, transitions, acknowledgments and notification IDs
use a SQLite journal, matching the existing local persistence architecture. No
forecast event or raw record is modified. Deterministic IDs include policy,
calibration, run/channel and replay-stream identity; conflicts fail closed. Inserts
are idempotent; update/delete triggers protect journal records. A testable local
adapter delivers only newly inserted activation/clearance notifications. No email,
text, webhook, machine control or external notification transport.

The portable dashboard embeds Python-produced alert evidence separately from the
unchanged forecast snapshot. It reveals only the current cursor/channel and retains
browser-local acknowledgment, notes and report behavior. It has no second JavaScript
threshold engine. Assistant summary retrieval may include bounded selected-period
alert evidence after deterministic processing; IDs/provenance include the policy
and calibration. The LLM cannot change state/thresholds and is unnecessary for
detection. No paid model request or new assistant tool budget is authorized.

## Metrics, acceptance and reporting

Report each run/channel/block separately: availability coverage/reasons, each
signal's eligible counts, watches, activation/clearance episodes, activation frequency
per 100 observed bursts, active duration in **observations**, unresolved episodes,
and deterministic examples chosen by a fixed first-activation/first-unavailable
rule. Do not convert CSV spans into operating hours. No event-label metrics or
outcome-selected best examples. B04 is not used to calibrate/select policy.

Acceptance is implementation correctness, not a favorable alert rate: all synthetic
state/eligibility/isolation/causality/persistence tests pass; replay is identical;
one activation notification per episode; no automatic clearance on missing/gaps;
no changed saved forecasts; exact scoped citations; no paid requests/B03 access.
Unsupported calibration/reference cells remain unavailable; do not lower support
or tune thresholds to produce more alerts. Retain unfavorable coverage/frequency
and both blocks. If these correctness criteria fail, fix code against this unchanged
policy and rerun offline; do not select a different policy based on outcomes.

Broader quality requires independently verified event definitions, intervention/
censoring and exposure semantics, multiple independent bearings and prospective
human review. This task neither opens B03 nor edits its reserve plan. Existing
readiness blockers remain, plus a separately reviewed frozen alert policy, validated
measurement meaning and appropriate event ground truth before any fault claim.
