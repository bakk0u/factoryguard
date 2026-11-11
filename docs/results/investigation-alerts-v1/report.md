# Investigation-alert prototype: implementation and recovery verification

2026-11-10. Local branch `feature/investigation-alerts-v1`, based on
`5469ddf31d617cd40b37b44cfcfe8f72e16f4897`. The alert changes remain uncommitted;
the base commit alone does not identify the implementation. The local recovery
record contains the final file inventory and SHA-256 manifest. Nothing was pushed,
merged or deployed. No paid requests, forecasting fits, saved-result changes,
raw-data changes, reserve-plan changes or B03 reads were made in this milestone.

## What works

This is a working **investigation-alert prototype**, with deterministic detection
independent of the assistant. It flags unusual measurements relative to specified
development references; it does not diagnose machine faults or establish health.

- Python combines saved forecast residuals, segment-relative RMS level changes
  and supported operating-bin comparisons. One signal can warrant investigation;
  correlated signals are not independent confirmation.
- Eligibility and monitoring availability are separate from the condition state:
  No active alert → Watch → Active alert → Cleared. Persistence, hysteresis, gap/
  history resets and channel isolation are explicit. Missing evidence cannot clear
  an active alert. Acknowledgment records review, not condition clearance.
- Append-only SQLite episode/transition/notification records, deterministic IDs,
  conflict checks, acknowledgment and delivery receipts support replay and local
  duplicate suppression. Delivery is an in-app/test adapter, not an external service.
- The dashboard shows state, availability, values and thresholds in V, rule
  version, limitations and an inspectable ledger. Investigate selects the period
  and question without submitting. Queue, notes, reports and citations still work.
- MCP summary retrieval supplies bounded, typed, selected-channel alert evidence
  with policy/engine/snapshot provenance. Retrieval and context assembly precede
  fixture generation. The assistant neither sets thresholds nor changes alerts.

Portable-dashboard acknowledgments are browser-local, partitioned by snapshot,
policy, channel, episode and visibility. The Python server API stores acknowledgments
in its separate journal. Neither changes the condition. Replay hides later records;
it does not delete the immutable journal. Static replay visibility is a UI/evidence
contract over a bundled snapshot, not confidential storage access control.

## Frozen policy and preserved evidence

The [protocol](../../investigation_alert_protocol.md), configuration and freeze
record preceded inspection of alert evaluation results. One candidate was evaluated;
no outcome-driven threshold or persistence adjustment followed. A pre-evaluation
schema clarification withheld selected-channel zero-variance observations; its
earlier protocol hash remains in the freeze amendment.

- Canonical policy SHA-256:
  `cb70ce84b6664f413a69617f2955d61a783b3b221f3dbe3ed7718acf9dd54864`.
- Frozen protocol SHA-256:
  `edd16b96c48f31d630e880a9b08ce52344bdb531b469f983867f2b8bed69ffcf`.
- Engine source SHA-256:
  `33fd90c72057907b26788bc58ce3134fdf710207f380b81e368a49d7bd432f15`.
- First evaluation: `reports/local/alerts-v1/evaluation-frozen/`; evaluation JSON
  SHA-256 `b7e946c34e9feed4d8815b413305c7acf8216d8ef43660a06a347290264473e5`.
- Correctness recheck: `reports/local/alerts-v1/evaluation-final/`; evaluation JSON
  SHA-256 `48e90ffbf490a365068778eb4f61cc688c62a783c2724e780ca2a8d36c9bcab6`.

The recheck followed malformed/missing channel-vector handling fixes against
synthetic input, without policy changes. Calibration and all numerical metrics are
identical in all eight cells; engine provenance and derived IDs identify the changed
code. Both evaluations remain intact. Recovery verified hashes of **25** frozen
files, including both evaluations and the policy inputs: zero mismatches. Recovery
did not run another evaluation. `evaluation_inspected:false` in the freeze describes
the freeze-time checkpoint, not the current review status.

## Ground truth and evaluation design

The documentation audit found no credible per-observation normal/fault intervals
or verified damage onset. B01 postmortem findings are experiment-level and its
termination records disagree. B02 changed its crossing-count stopping rule and
resumed after a gap; channel/statistic/count-reset semantics are insufficient for
event labels. B04's stop and temperature/loading rules do not define a fault event;
its measured speed/load interpretation remains unresolved. Warm-up, sensor-range
flags and gaps are measurement-quality findings, not confirmed machine failures.

Calibration uses only B01 observations 1–150 or B02 1–446, separately by channel.
Validation is B01 151–263 / B02 447–781; reserved policy evaluation is B01 264–377 /
B02 782–1116. Each evaluation block starts with frozen prefix calibration and
empty alert history. Dashboard replay is continuous instead; its episodes need
not match independently initialized block episodes. Saved forecasts retain their
original causal history and prior development-selection provenance.

Residual/level activation uses empirical prefix quantile .99, minimum 20 scores;
context uses an exact 250 rpm × 250 N × 250 N bin with at least 20 prefix values,
median and 3 IQR scale. The numerical floor is 1e−9 V. Three same-signal high
observations activate; three quiet observations at 0.6 of activation thresholds
can clear. The RMS window is three observations; gaps >24 provisional CSV seconds
reset history. See the frozen protocol for the complete eligibility/clearing rules.

These are inspected development bearings whose saved forecasting method was
already selected on development results. The reserved blocks are not an unbiased
held-out bearing test. Calibration data are not labelled healthy; quantile .99
does not guarantee a 1% false-alarm rate.

## Results retained without tuning

V = validation; R = reserved policy-evaluation block. Durations are observations,
not verified operating hours. “Covered” means at least one eligible signal, not
complete monitoring or correct detection.

| Run/channel | Block | Observations | Activations | Clearances | Active observations | Limited / unavailable | Covered |
| --- | --- | ---: | ---: | ---: | ---: | --- | ---: |
| B01/A | V | 113 | 1 | 0 | 54 | 112 / 1 | 99.1% |
| B01/A | R | 114 | 3 | 2 | 91 | 101 / 13 | 88.6% |
| B01/C | V | 113 | 1 | 0 | 54 | 112 / 1 | 99.1% |
| B01/C | R | 114 | 1 | 0 | 105 | 110 / 4 | 96.5% |
| B02/A | V | 335 | 1 | 1 | 11 | 335 / 0 | 100% |
| B02/A | R | 335 | 1 | 0 | 251 | 335 / 0 | 100% |
| B02/C | V | 335 | 0 | 0 | 0 | 335 / 0 | 100% |
| B02/C | R | 335 | 1 | 0 | 248 | 335 / 0 | 100% |

**No row has fully available monitoring.** B01 has zero context-eligible
observations in either block. B02 has 175 context-eligible observations in validation
and 174 in the reserved block per channel; unsupported bins remain unsupported.
Changing operating conditions also confound level comparisons. Long unresolved
episodes and limited coverage are retained, not corrected to improve appearance.

Consecutive three-observation rolling scores overlap. An isolated extreme reading
can affect three successive level windows and satisfy persistence. A synthetic
regression explicitly preserves this behavior: three high windows do not establish
three independent changes or sustained elevated raw readings. Correlated channels
and repeated blocks also do not yield independent performance observations.

False alarms, missed faults, precision, recall and detection delay are **null /
unverified**, because event ground truth and exposure semantics are insufficient.
Zero alerts does not demonstrate health; many alerts does not demonstrate fault
sensitivity. No statistical significance, damage, causal or safety claim follows.

## Completed checks and recovery

At recovery start, a filtered process inspection found no running test, build,
evaluation or context command. Two existing assistant launchers were left alone.
Completed checks were reused rather than rerun. Only the missing full Python
verification and final alert display/browser check were launched, once each, with
120-second limits. Both completed without timeout; no retry loop was used.

| Check | Result / evidence |
| --- | --- |
| TypeScript build | Passed before interruption; retained checkpoint |
| TypeScript tests | **43/43 passed**, 0 failed/skipped; saved test log |
| Full Python suite | **168/168 passed**, 0 failed/skipped; 12.801 s outer duration |
| Frozen lexical retrieval cases | **40/40 passed**, 20/20 each split; document recall/MRR at 4 both 1.0 |
| Static and assistant site builds | Passed; retained build logs |
| Final alert Chrome workflow | Passed, 3.448 s; desktop/mobile, acknowledgment, reset, scope, citation, export, local policy, asset boundary |
| Existing redesign Chrome workflow | Passed; 15 architecture nodes, keyboard/focus, suggestions, mocked loading/error/cancel, static/direct-file, responsive views |
| Existing assistant Chrome workflow | Passed; real MCP, offline fixture, matching evidence, report, desktop/mobile |
| Existing reviewer Chrome workflow | Passed; notes/isolation, replay/reset, filters, report provenance, blocked storage, mobile, direct-file |
| Frozen-artifact hashes | 25/25 unchanged during recovery |
| Protected tracked paths | No diff in source snapshot/manifest, model sources, saved release results, reserve configuration or `.gitattributes` |
| Private configuration | Metadata only: ignored, untracked, current-owner, mode 0600; no content read or change |

The interrupted Python run had one error: a newly added retrieval test requested
12 passages while the documented API maximum is 6. Its source had already been
corrected to 6 before recovery. The final full run confirms the correction; no
assertion, dependency or test was removed/skipped. Expected STALE messages at the
end of its log come from context-integrity test fixtures, not a stale final graph.

Meaningful synthetic tests cover spikes, drift, sustained changes, unsupported
references, warm-up/range/zero variance, missingness/gaps, hysteresis, separate
acknowledgment/clearance, notification suppression, causal future independence,
channel isolation, immutable/idempotent persistence and scoped exports. Provider
tests use mocks and fake credentials. This verifies deterministic enforcement,
not real-model prompt-injection resistance or fault-detection performance.

Final browser evidence uses actual recorded B01/A continuous replay, whose first
activation is observation 210. At that cursor the UI shows residual 0.058674 V
against activation 0.073041 V, and level 0.261890 V against 0.042779 V; context
comparison is unavailable. It correctly remains active on level evidence without
requiring the residual to agree. The investigation action selects 208–210 without
POST; one explicit **offline fixture** request then retrieves and assembles context
before generation and opens its matching alert citation. No live model was called.
The original first evaluation and prior screenshots were not replaced.

Recovery logs/status/integrity/inventory: `reports/local/alerts-v1/recovery-01/`.
Representative screenshots (observed in Chrome, not inferred from source):

- [Desktop alert and assistant](../../../reports/local/alerts-v1/recovery-01/browser/dashboard-alert-desktop.png)
- [Mobile alert and ledger](../../../reports/local/alerts-v1/recovery-01/browser/dashboard-alert-mobile.png)
- [Matching alert citation](../../../reports/local/alerts-v1/recovery-01/browser/alert-citation-desktop.png)
- [Calibration unavailable](../../../reports/local/alerts-v1/recovery-01/browser/calibration-unavailable.png)

## Reproduction and remaining work

Use the existing Python 3.12 / Node >=22 locked environment. Existing services were
not terminated. The verified offline service is <http://127.0.0.1:8787/>; from a
free port, the same startup is:

```bash
env -u OPENAI_API_KEY FACTORYGUARD_ASSISTANT_PORT=8787 .venv/bin/python scripts/start_assistant.py
```

Select Explore measurements → B01/A → reveal through 210 to inspect the continuous
example. The default 1–3 guided example is correctly monitoring-unavailable during
calibration. No model key is required; do not enable live mode for this verification.

```bash
env -u OPENAI_API_KEY MPLBACKEND=Agg MPLCONFIGDIR=/tmp/factoryguard-matplotlib XDG_CACHE_HOME=/tmp/factoryguard-cache .venv/bin/python -m unittest discover -s tests -v
env -u OPENAI_API_KEY npm run build --prefix assistant
env -u OPENAI_API_KEY npm test --prefix assistant
env -u OPENAI_API_KEY .venv/bin/python scripts/project_context.py status
```

The alert browser regression is `scripts/verify_investigation_alerts.cjs`; point
`FACTORYGUARD_BROWSER_BASE` at the offline service, `NODE_PATH` at the isolated
Playwright install and `CHROMIUM_PATH` at the installed browser. Use a fresh
`FACTORYGUARD_SCREENSHOT_DIR` to preserve earlier captures. The evaluation CLI
`python -m factoryguard.alerts.evaluate --output <fresh-directory>` is documented
for reproducibility, **not an outstanding recovery check or a tuning invitation**.

There are no outstanding implementation-verification failures from this checklist.
Final context freshness, whitespace check and file inventory are recorded in the
recovery completion record. No production readiness is claimed. SQL triggers are
application immutability safeguards, not tamper-proof storage against a privileged
database owner; local receipt deduplication is not external exactly-once delivery.

Stronger alarm-performance claims require independent event/normal definitions,
validated measurement/operating semantics, censoring and exposure definitions,
multiple independent bearings, independent human review and prospective evaluation.
The overlapping-window policy and long dwell need scientific review before a
separately frozen future policy; this milestone preserves them. B03 remains sealed;
its evaluation and reserve-plan changes require separate authorization. Real-model
alert-answer quality and adversarial prompt-injection evaluation remain unverified.
Restricted hosting additionally needs authentication/TLS, trusted-origin policy,
spending/concurrency limits, secret/evidence isolation, retention/access controls
and independent security review. None is implemented or deployed by this recovery.
