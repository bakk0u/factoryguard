# Final investigation-alert checkpoint

2026-11-10 · local `feature/investigation-alerts-v1` · **prototype complete within scope**.
No outstanding correctness failure in the executed checks. This is deterministic
investigation alerting, not validated machine-fault detection or production readiness.
No paid requests, project forecasting fits/result changes, raw changes, B03 access, reserve
changes, push, merge or deployment. The local commit includes the previously
uncommitted v1 prerequisites and this bounded v2 milestone; unrelated work is preserved.

## V1 → V2

One [v2 policy and acceptance protocol](../../investigation_alert_protocol_v2.md)
was frozen before implementation/evaluation. No threshold search or outcome tuning.
The original [v1 record](../investigation-alerts-v1/report.md), policy, engine and
both evaluations remain unchanged.

| Weakness | V2 behavior and tradeoff |
| --- | --- |
| One extreme reading reused by overlapping level windows | Score provenance separates current observations from reused anchor/forecast/reference history. Three counted level confirmations require disjoint three-reading windows. A synthetic isolated extreme affects three windows but counts once and cannot activate level alone. Steps/ramps still activate. Earliest level-only activation moves from first high +2 to +6 observations; residual persistence remains three fresh readings. No new filter or recalibration. |
| Unsupported context hiding usable evidence | Residual, level and context retain separate eligibility, blocking reasons, qualifications, units and support. Unsupported bins disable only context. Full/limited/unavailable monitoring is separate from condition state. |
| Long Active episodes conflated with current support | Current assessment is supported, unresolved/unavailable, within hysteresis, or recovery pending. Fresh persistent additional signals escalate evidence scope inside the same episode. Frames explain continuation; transitions record assessment changes/escalation/reset/clearance. No extra activation notification. |
| Stale evidence or acknowledgment clearing a condition | Recovery needs three disjoint quiet supports for every required signal; missing required evidence blocks clearance. Acknowledgment never clears. Active level anchor/bin survive history resets and recovery; history/counters still reset. |

No continuously adapting baseline, broader bins or healthy labels were added.
Reused baselines and serial observations are correlated; disjoint support is not
statistical independence. Forecast residuals can reflect prediction-baseline history,
so a residual episode alone does not establish a sustained raw step or a fault.
An extreme reading inside the initial fixed anchor remains a baseline limitation.
The LLM neither detects nor changes conditions; CLI evaluation works with no key.

## Correctness fix, without hiding the first result

After the first v2 evaluation, a targeted synthetic gap regression demonstrated that
rebuilding the segment anchor could clear an unchanged elevated level. The first
fix preserved the active comparison but left a replacement anchor that started a
new Watch after recovery. The complete fix retains the active anchor/bin through
reset and subsequent recovery, satisfying the frozen **no adaptive baseline** and
fresh-recovery requirements. Neither assertion was removed. Both failure logs remain.

The original v2 output is `reports/local/alerts-v2/evaluation-frozen/`. A **single
separate correctness recheck** is `evaluation-corrected/`; both are preserved.
Configuration/protocol hashes and numerical thresholds/calibration are unchanged.
Episode counts and active durations match the first v2 run in every cell; some
assessment, score/support and confounding details changed. This was a bug fix,
not another policy candidate or a favorable-outcome selection.

## Development diagnostics

Same v1 blocks: B01 prefix 1–150, validation 151–263, reserved 264–377; B02 prefix
1–446, validation 447–781, reserved 782–1116. Each evaluation block starts with
frozen prefix calibration and empty history. Dashboard replay is continuous.
Saved forecasting settings were already selected on these inspected development
bearings. These comparisons are **not independent validation**.

V = validation; R = reserved development block. Active durations count observations,
not verified operating hours. Sup/U/H/Rec = supported / unresolved-unavailable /
hysteresis / recovery-pending active observations.

| Run/channel | Block, n | Episodes v1→v2 | Active observations v1→v2 | V2 episode durations | V2 cleared | Sup / U / H / Rec |
| --- | --- | --- | --- | --- | ---: | --- |
| B01/A | V, 113 | 1→1 | 54→50 | 50 | 0 | 50 / 0 / 0 / 0 |
| B01/A | R, 114 | 3→2 | 91→36 | 19, 17 | 1 | 9 / 12 / 10 / 5 |
| B01/C | V, 113 | 1→1 | 54→50 | 50 | 0 | 50 / 0 / 0 / 0 |
| B01/C | R, 114 | 1→1 | 105→98 | 98 | 0 | 78 / 4 / 10 / 6 |
| B02/A | V, 335 | 1→0 | 11→0 | — | 0 | 0 / 0 / 0 / 0 |
| B02/A | R, 335 | 1→1 | 251→249 | 249 | 0 | 249 / 0 / 0 / 0 |
| B02/C | V, 335 | 0→0 | 0→0 | — | 0 | 0 / 0 / 0 / 0 |
| B02/C | R, 335 | 1→1 | 248→245 | 245 | 0 | 245 / 0 / 0 / 0 |

Long supported and unresolved episodes remain; no expiry disguises them as cleared.
Fewer episodes does not mean fewer false alarms or better sensitivity. No credible
normal/fault intervals or onset exist; false alarms, missed faults, precision,
recall and detection delay remain null/unverified. Warm-up/range warnings and
stopping rules are not fault labels. B04 remains unavailable diagnostic context.

## Signal coverage and fresh evidence

Threshold values, calibration score counts, bin statistics and calibration input
hashes match v1 exactly in all eight cells. Eligibility counts are also unchanged.

| Run/channel/block | Residual eligible | Level eligible | Context eligible | Uncounted overlapping high level scores |
| --- | --- | --- | --- | ---: |
| B01/A/V | 112/113 | 108/113 | 0/113 | 37 |
| B01/A/R | 101/114 | 94/114 | 0/114 | 15 |
| B01/C/V | 112/113 | 108/113 | 0/113 | 37 |
| B01/C/R | 110/114 | 104/114 | 0/114 | 37 |
| B02/A/V | 334/335 | 330/335 | 175/335 | 2 |
| B02/A/R | 333/335 | 325/335 | 174/335 | 164 |
| B02/C/V | 334/335 | 330/335 | 175/335 | 0 |
| B02/C/R | 333/335 | 325/335 | 174/335 | 162 |

Specific blocking counts (prior = missing preceding forecast/history; range blocks
all signals in that selected channel):

| Cell | Residual prior | Level short history | Context unsupported bin | Selected-channel range |
| --- | ---: | ---: | ---: | ---: |
| B01/A/V | 1 | 5 | 113 | 0 |
| B01/A/R | 3 | 10 | 104 | 10 |
| B01/C/V | 1 | 5 | 113 | 0 |
| B01/C/R | 3 | 9 | 113 | 1 |
| B02/A,V and C,V (each) | 1 | 5 | 160 | 0 |
| B02/A,R and C,R (each) | 2 | 10 | 161 | 0 |

Changing operating bins additionally qualify level comparisons as confounded.
Exact per-frame reasons/qualification histograms are retained in the evaluation.
**No fully available rows**: any-signal coverage is 88.6–100%, all limited or
unavailable, not complete monitoring. B01 context remains unsupported; no support
threshold/bin was relaxed. Synthetic tests separately verify full monitoring with
supported references and missing forecast/calibration/context/quality handling.

All eight corrected streams pass the post-evaluation audit: scoring support stays
causal, activation/recovery sets are disjoint and notifications are unique per
episode/kind. Gaps/missingness reset counters, retain unresolved conditions and
cannot manufacture recovery. No future/channel/replay-boundary evidence is used.

## Verification and artifacts

Final observed checks, all bounded to 120 seconds each, no stalls or automatic retry
loop. Full command/exit/duration inventory, including initial runs, is
`reports/local/alerts-v2/executed-checks.json`; logs and status JSON are alongside it.
All subprocesses excluded the real provider credential. Existing services were
left untouched; the dedicated offline port-8788 test service was stopped afterward.

| Check / exact entry point | Final result |
| --- | --- |
| `.venv/bin/python -m unittest discover -s tests -v` | **180/180**, 0 skipped, exit 0; 12 v2 tests included |
| `npm test --prefix assistant` | **44/44**, 0 skipped, exit 0; mocked providers/fake credentials |
| `npm run build --prefix assistant` | Passed |
| `.venv/bin/python scripts/build_reviewer_site.py --output reports/local/reviewer-site` | Passed |
| Same builder, `--output reports/local/assistant-site --alert-journal reports/local/assistant/alerts.sqlite` | Passed; private journal excluded from assets |
| `.venv/bin/python -m factoryguard.assistant.workflows index` | Passed; lexical only |
| `.venv/bin/python -m factoryguard.assistant.evaluate --output reports/local/alerts-v2/final-retrieval-cases.json` | **40/40** frozen cases, 20/20 each split; recall/MRR at 4 = 1.0 |
| `node scripts/verify_investigation_alerts.cjs` | Passed: actual evidence, disjoint support, status, ack/reset/channel isolation, export, matching citation, desktop/mobile |
| `node scripts/verify_reviewer_redesign.cjs` | Passed: keyboard, responsive views, source controls, mocked/offline states, direct-file |
| `node assistant/test/browser.cjs` | Passed: real MCP-backed offline fixture, selected channel/period, citations/report, desktop/mobile |
| `node scripts/verify_reviewer_workflow.cjs http://127.0.0.1:8788/` | Passed: notes/restart/replay/export, storage failures, mobile and direct-file |

Failures retained: `gap-anchor-regression.log` (demonstrated bug),
`synthetic-v2-anchor-fixed.log` (incomplete first fix), `reviewer-browser.log`
(`spawn python ENOENT` before app assertions). Fixed tests pass without weakening
assertions. The reviewer command's explicit URL avoids its absent default launcher.
Staged whitespace review also caught one trailing blank line in the new test;
it was removed without changing logic/assertions. Expected STALE messages from
context-integrity fixtures are not final graph failures.

Final memory/Graphify freshness, whitespace/staged review, frozen-artifact hashes,
source inventory and commit identity are recorded in the local completion record.
V1 preservation covers 27 original files, including engine/report; v2 policy and
both evaluation outputs are hash-checked. Protected forecasting/snapshot/raw/reserve
paths have no diff. `.env.local` was only metadata-checked: private, ignored,
untracked, current-owner; never read, altered or committed. No private DB/traces,
raw payloads or screenshots containing credentials enter the commit.

Screenshots from the final corrected build:

- [Desktop alert beside assistant](../../../reports/local/alerts-v2/final-browser/dashboard-alert-desktop.png)
- [Mobile alert and evidence](../../../reports/local/alerts-v2/final-browser/dashboard-alert-mobile.png)
- [Unresolved episode / unavailable assessment](../../../reports/local/alerts-v2/final-browser/unresolved-assessment-desktop.png)
- [Matching citation](../../../reports/local/alerts-v2/final-browser/alert-citation-desktop.png)

Continuous B01/A first activation is observation **214** (v1: 210). Acknowledgment
leaves it active. Investigate populates the period/question without submission;
one explicit offline fixture request in the alert workflow retrieves/assembles
before generation and opens matching evidence. Repeated browser workflows use
fixtures/mocks only; no real model, token usage or billing savings are claimed.
Full monitoring is synthetic-tested; recorded browser examples remain limited/
unavailable. Live-model answer quality, real-model prompt-injection robustness,
independent scientific/security review and hosted operation remain unverified.

Reproduce locally from the locked Python 3.12 / Node >=22 environment:

```bash
env -u OPENAI_API_KEY FACTORYGUARD_ASSISTANT_PORT=8788 .venv/bin/python scripts/start_assistant.py
```

Open <http://127.0.0.1:8788/>. B01/A replay through 214 shows the supported episode;
through 363 shows unresolved/unavailable assessment. Default 1–3 remains calibration-
unavailable. No model key is needed. Browser commands use the installed Chrome /
isolated Playwright and explicit offline URL; exact variables are in local `verification-environment.json`.

**Verdict:** investigation-alert prototype complete within this milestone. Missing
ground truth, operating/exposure ambiguity and development-selection dependence
prevent stronger alarm-performance claims. Long episodes and coverage limitations
are retained rather than tuned away. No further implementation campaign or reserve
evaluation is part of this checkpoint.
