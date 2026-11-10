# Dashboard investigation: offline audit and implementation review

Reviewed locally on 2026-11-09. No investigation, smoke, paid provider request,
embedding download, forecasting retraining, deployment or B03 access was performed
in this task. Mock/fixture investigations ran only inside offline tests.

## Original evidence and provenance

Request: `2d7ed00c-f795-4afe-a177-83fbfb7d5284`. Accepted selection:
B01 / A / inclusive positions 1–3 / as_of=3 / replay / snapshot
`9a3da297dd848bf079a0c8ff1fa9fd3be1dea42894e867fb51c2fdf35efa624a`.
Its actual question was **“What changed during this period, and what remains
uncertain?”**, the dashboard default, rather than the longer question previously
specified for manual verification. Do not attribute this answer to the longer prompt.

Observed saved response: completed, `gpt-5.4-mini-2026-03-17`, one model turn,
12,155 ms; 7,116 input / 1,801 output tokens. These figures belong to this request,
not the earlier CLI smoke. Producing source was `c23c79d` with a dirty worktree.
No precise wall-clock request-start time is inferred from artifact modification times.

The existing completed API response was preserved using a read-only loopback GET.
The original trace and response remain unchanged. Audit files are in ignored,
owner-accessible `reports/local/assistant/review-2d7ed00c/`:

- `original-trace.json`, `original-api-response.json`: preserved originals.
- `numeric-audit.json`: numerical assertions, units, signed differences and citation counts.
- `measurements.json`, `baseline-evaluation.json`, `final-evaluation.json`:
  offline measurements and the unchanged frozen-case results.
- `final-offline-retrieval.json`: separately labelled current implementation output;
  it does not replace or fill gaps in the original evidence.
- `suggested-corrections.md`: proposed editorial corrections, not a regenerated answer.

Original trace SHA256:
`dc51be0c3780b8f702a62cb14b5c72708c57f100d89cea32cd35ef1c8a4a7475`.
The original API answer/context exactly match the validated answer/context in the trace.
Missing records were not regenerated.

## Ordering, scope and citation resolution

Trace ordering: tool discovery at 377 ms; replay state → investigation summary →
quality report → measurements → documentation completed at 387 ms; bounded context
assembled at 388 ms; generation began afterward, returned at 12,154 ms; validation
and completion at 12,155 ms. All five initial tools succeeded. No additional tools
or model turns were needed. Generation occupied approximately 11,766 ms, discovery
approximately 335 ms, and the five evidence calls approximately 10 ms.

All **25 citation references resolve to five distinct records**: the period,
quality and three observation records. No documentation passage is cited by a
claim. This is ID membership, not entailment. All observation records are labelled
A, positions 1–3; state visibility is 3; documentation passages are marked
pre-replay methodology. Issued next-observation forecasts are available at issuance;
they do not reveal a later observed value. No position beyond 3 or B03 data was found.
Policy documentation mentioning sealed B03 is not B03 measurement access.

**Original channel isolation was incomplete:** nested `sudden`/`sustained` maps
included C-channel RMS changes, and forecast notices included both A/C errors.
The answer's quoted numbers use A, but the original context was not strictly
channel-exclusive. Future outputs now remove those off-channel numbers. The
original response is preserved with this finding, not retrospectively rewritten.

## Claim-by-claim support

Evidence shorthand below: O1/O2/O3 are original observation positions; P is the
original period record; Q is quality. The full citation IDs are retained in the
original response and numerical audit. “Supported” means supported by these
recorded derived measurements, not proof of physical calibration or causality.

| Original answer field | Finding against its cited evidence |
| --- | --- |
| Summary | RMS dip/recovery, increasing ambient-relative temperatures, warm-up and missing bin references are supported by O1–O3/Q/P. Speed/static/dynamic loads finish lower, but speed and dynamic peak load are not monotonically falling. The uncertainty/no-health conclusion is appropriate. The summary itself has no citation field; membership validation does not independently check its entailment. |
| Observations 1: RMS | Supported. O1–O3: 0.015924565978414, 0.0152243246678043, 0.0154325999391356 **V** round correctly to 0.0159246, 0.0152243, 0.0154326 V. Position 3 is above position 2 but below position 1. |
| Observations 2: temperatures | Supported. Ambient-relative T1 −0.037428721608002 → 0.4495224752571012 degC; T2 −0.1391999846530005 → 0.3401169217726014 degC. The four quoted four-decimal values and signs are correct. Both also increase at position 2. Negative offsets are below ambient, not negative absolute temperatures. |
| Observations 3: speed/load | Endpoint statement supported by P. Speed 753.116231066696 → 753.091175837907 rpm (−0.025055228789); static load 2544.03715298923 → 2537.89472880741 N (−6.14242418182); dynamic peak 10.3965994159118 → 10.3482840955735 N (−0.0483153203383). O2 shows speed/dynamic peak first increase. “Drifted downward” should explicitly mean net endpoint differences, not a trend. |
| Observations 4: warm-up/warnings | Supported. Q warmup_count=3, warning_positions=[1,2,3], unseen support count=3; O1–O3 carry warm-up/reference notices. Warm-up is an operating regime, not a verified healthy label. |
| Explanations 1: “sudden change” | Arithmetic supported: O3−O2 RMS = +0.00020827527133130026 V, correctly rounded +0.0002083 V. Definition is current-minus-previous in the unchanged coarse bin, not a detected abrupt physical event, damage threshold or sustained trend. At 3 vs 2, T1 +0.2456310792429015 degC, T2 +0.24829154978120369 degC, speed −0.02639747318892205 rpm, static load −2.063543403970016 N, dynamic peak −0.09835242578669856 N. These are concurrent observations; this paragraph belongs in observations, not causal explanations. |
| Explanations 2: “forecast deviations shrank over the period” | The quoted signed errors are correct: O2 −0.0007002413106097002 V; O3 −0.0003519177771564609 V, each exactly observed−settled forecast. The **absolute magnitude decreases between two scored arrivals** by 0.0003483235334532393 V. Signed error increases toward zero. O1 has no settled error. A general period trend, improved model performance or health improvement is unverified. |
| Explanations 3: reference support | Supported for this bin: all three records have status unseen, n=0, empty measures; notices state minimum display support 20. No displayed reference median/range is available. This is a fixed development reference, not a local fitted or healthy range. The wording should not imply that no reference exists anywhere. |
| Interpretations 1: context during warm-up | Dip/recovery and increasing temperatures are supported. “Consistent with changing operating conditions” is explicitly tentative, not established causation. Lack of references is not the only uncertainty: three observations, coarse bins, timing/calibration ambiguities and no causal design also prevent attribution. |
| Interpretations 2: contextual rather than intrinsic | P/O2/O3 establish the unchanged coarse bin and carry the explicit limitation that thermal/context differences remain possible explanations. “May” appropriately marks a hypothesis. Evidence cannot rank context against intrinsic bearing change or establish either cause. |
| Missing information 1: healthy reference | Supported as an unavailable/unsupported basis, not evidence that the bearing is unhealthy. Q/O1–O3 have no reference values; global limitations prohibit healthy-range claims. |
| Missing information 2: sustained change | Supported. All sustained fields are null. Definition compares last three against preceding three consecutive same-bin observations; three observations cannot supply both windows. |
| Missing information 3: clock/timezone | Supported. Observation timezone is unspecified and CSV clock/association is provisional. Do not infer exact physical elapsed time or UTC. |
| Limitations 1: no damage/fault/safety/RUL | Appropriate methodological constraint, explicitly carried in the assembled limitations. Not a diagnostic finding. |
| Limitations 2: coarse bins/context | Supported by recorded-change definition/limitations; possible context explanation remains unverified. |
| Limitations 3: warm-up not healthy | Supported by warm-up notices. |
| Limitations 4: B04 caveats | The selection is B01/A, so B04-specific scaling ambiguity is out of this run's scope. This is unnecessary discussion caused partly by irrelevant retrieved B04 text; it does not eliminate the general B01 limitations. |
| Suggested step 1: later window | A prospective suggestion, not evidence available in this request. No later window was read or requested in this review. Must remain separate from the current as_of=3 answer. |
| Suggested step 2: additional same-bin observations | A prospective suggestion only. Same-bin membership alone does not establish matched conditions or support causal attribution. |
| Suggested step 3: later reference support | Unverified future possibility. Q proves only current unseen support, not that future support will appear. No later data was regenerated to check it. |

Additional omission: O1 flags the preceding gap as unknown; its duration cannot be
recovered from this answer/evidence. No >24-second gap boundary occurs *inside*
the selected period, but that does not establish uninterrupted acquisition before
O1. The answer should mention this uncertainty. It makes no explicit fault or
causal verdict, but the “explanations” heading overstates the first two empirical
paragraphs. Neither the ID checker nor schema validation proves scientific support.

## Browser evidence versus offline verification

The task's supplied screenshot establishes answer rendering and visible citation
controls as user-supplied evidence. No actual original citation interaction was
observed in this review, and no screenshot file for this request was located in
the saved local assistant artifacts. No fresh browser automation was available.
Source review confirms labels are `index+1` into facts followed by passages, and
click handlers find the exact stable ID and display that record. Offline VM/DOM
tests exercise that mapping, intended API selection, lost-SSE and lost-POST guards,
and acknowledged cancellation. These tests are not observed browser interactions
with the original response, screenshots or a substitute live dashboard investigation.

## Changes and measurements

The working checkout stayed on master `c23c79d`, retaining the earlier local
configuration/diagnostic changes; no branch switch, commit or merge was made.
All changes below postdate the successful dashboard request and are **offline
verified only**. The previous live server was stopped after preserving its GET result.

| Area | Change and reason |
| --- | --- |
| API | Coalesce identical **in-flight** validated requests, keyed by the complete normalized request (session/question/snapshot/run/channel/period/as_of/mode/retrieval_mode). Capacity remains three jobs and 50 retained slots; validation/body limit unchanged. Completed responses are not reused to bypass a reset cursor. API result activities and server progress storage retain metadata rather than repeating retrieved evidence, assembled contexts and final answers. Canonical context/answer remain in the result; complete staged evidence remains in the owner-only trace. |
| Frontend | Keep the submission locked after lost POST acknowledgement or SSE instead of inviting an accidental extra paid request. An identified request can still be cancelled; cancellation acknowledgement releases the UI and says cleanup may still be finishing. No automatic submission/retry was added. Unknown POST status requires trace/manual recovery; in-flight coalescing is not durable idempotency across completion/restarts. Citation mapping needed no rewrite. |
| RAG | Parse envelopes once, account serialized record sizes incrementally, explicitly report truncated missing-entry lists and reject conflicting records sharing a citation ID. Stopword removal and a small explicit lexical normalization improve broad change-question ordering without changing chunks, source hashes, IDs or visibility rules. All selected numerical values, units, scientific warnings and limitations remain. Off-channel change/reference values and A/C notices are scoped to the selected channel. Supported-reference filtering is tested separately; the original selected bin had no reference measures. |
| Provider/orchestrator | Lossless source-table transport preserves every record ID and source. Model tool schemas omit application-owned selection and prune only unreachable definitions; MCP still receives immutable validated selection on every call. Precompute the fixed answer schema, explicitly reject refusal/incomplete responses, and clarify prompt v2: sudden=current−previous, two errors are not a trend, concurrent changes are not causes. API activities are compacted, but trace detail is preserved. Stateless Responses, store=false and safe diagnostics remain. |
| MCP | Make close idempotent across abort/finally/error paths. Retain fresh per-request subprocess/discovery, the credential-free environment allowlist and authoritative cursor rechecks. No cross-request evidence cache or subprocess pool was added. Five serial calls cost only about 10 ms in the saved trace; parallelism/reuse adds scope/reset/trace complexity without a material demonstrated benefit. |

Provider work consulted current [official Structured Outputs guidance](https://developers.openai.com/api/docs/guides/structured-outputs?api-mode=responses).
The strict schema/Responses interface is retained; schema adherence is not claim
entailment, and refusal/incomplete handling is explicit. Model configuration,
process precedence, root-only dotenv parsing, offline default, explicit live opt-in,
redaction and SDK logLevel=off remain. Bounds remain 60 seconds/request, 15s/MCP,
30s/provider, at most three model turns, nine evidence calls, 2,200 output tokens
per turn and one SDK retry. No bounds were increased.

Offline measurements on the preserved input (see `measure.mjs` and `measurements.json`):

| Measurement | Baseline | Final |
| --- | ---: | ---: |
| Assembly median, nine batches × 150 iterations | 0.1621 ms | 0.0641 ms |
| Canonical context UTF-16 characters | 19,755 | 19,792 |
| Provider context JSON UTF-8 bytes | 19,757 | 19,152 |
| Model tool-schema JSON UTF-8 bytes | 6,247 | 1,875 |
| Result bytes, controlled same-context activity compaction | 75,430 | 27,283 |
| Structured fact records | 6 | 6 |
| Original selected observation values/units preserved | baseline | all unchanged |
| Records omitted for context budget | 0 | 0 |
| Frozen lexical cases | 40/40 | 40/40 |
| Documentation recall@4 / MRR@4, both splits | 1.0 / 1.0 | 1.0 / 1.0 |

The canonical context slightly grows because relevance ordering changes which
same-size-bounded passages are included. One original documentation ID overlaps
the final four; its content hash is unchanged. Numerical citation IDs are unchanged.
The question now retrieves contextual-change methodology instead of unrelated
holdout/training excerpts; this is author source review, not an independent
relevance score. Frozen cases contain only eight positive documentation questions.
Doc-search medians were 1.372 vs 1.324 ms (15 searches each), too small/noisy for a
performance claim. Five new offline cold-discovery samples had median 233.7 ms;
they are not a like-for-like measured optimization against the live 335 ms phase.

The response reduction is about 64%, tool schemas about 70%, assembly about 60%.
These are deterministic JSON sizes/microbenchmarks. They do **not** establish new
model token usage, billing savings, end-to-end live speed or improved answer quality.
No new provider call was used for measurement. Hybrid retrieval was not exercised
or verified; no weights/telemetry/network workaround was attempted.

## Checks, tradeoffs and remaining work

- TypeScript build passed; **37 TypeScript tests passed**, zero skips/failures.
  Includes config precedence, secret/subprocess boundaries, safe mocked API errors,
  schema pruning, lossless provenance, scope isolation, missing-evidence reporting,
  conflicting citations, API body/capacity/duplicate guards, cancellation/cleanup,
  trace preservation and offline frontend citation/lost-connection behavior.
- **18 focused assistant Python tests passed**, zero skips/failures, including
  selected-channel preservation and cursor-reset rejection with a reused service.
- Full Python suite: **140 run; 139 passed; one error, zero skips**. The existing
  all-model-family synthetic test requires absent optional XGBoost. No assertions
  were weakened or dependencies substituted. Included dashboard/application and
  pinned reviewer-site checks passed. Real browser automation remains unavailable.
- All **40 unchanged frozen cases passed** before and after; manifest hash matches.
  Existing saved forecasting/site source artifacts and original trace/response
  hashes remain unchanged. Required project context update/status and whitespace
  checks passed; graph remains local code-only, no semantic backend.
- No evidence cache means repeated deliberate requests still pay local MCP startup
  and reload the pinned snapshot. It avoids stale cursor/reset/channel/version
  leakage. In-flight duplicate suppression is per process, not hosted durable
  exactly-once submission semantics. Lost-ack recovery is deliberately conservative.
- Provider transport/schema/prompt, changed retrieval and frontend guards require
  a future **separately authorized** live/dashboard check. None was run here. The
  original live success does not validate this changed version.
- Remaining quality work: a broader predeclared claim-entailment/numerical review
  set, targeted misleading-change/causal-language cases, prompt-injection tests
  across retrieved documents/tool output/questions and independent human review.
  This single author-reviewed answer is not a general quality/security evaluation.
- Restricted hosting still needs authentication/invite access, TLS, trusted
  hosts/origins and CSRF review, per-user spending/rate/concurrency controls,
  durable submission identifiers, secret/evidence/egress isolation, explicitly
  chosen server-authoritative cursor policy (public snapshots are not access
  control), restricted trace access/retention/deletion, and hosted lifecycle/security
  tests. No hosting work was implemented.
