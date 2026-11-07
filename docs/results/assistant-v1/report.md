# Assistant evidence/retrieval verification

This is an **offline engineering evaluation**, not a live LLM quality score,
independent human-reviewed benchmark, fault detector or new bearing-model campaign.
Cases are explicitly labelled in [cases.json](../../../assistant/evaluation/cases.json):
40 expectations authored/reviewed against current source by the implementation
author, 20 development and 20 held-out questions. Independent human review remains
pending; the two question splits are not new independent bearing experiments.
No search/tuning was performed to improve held-out scores after evaluating them.

## Follow-up verification — 2026-11-07

GitHub API access worked in a fresh checkout of `d7c2806`. The original
[assistant run](https://github.com/bakk0u/factoryguard/actions/runs/42392110001)
passed on Ubuntu but failed on Windows: two tests left fixture SQLite connections
open and temporary-directory cleanup raised `WinError 32`. Application connections
already used explicit closing. The fixtures now close deterministically; new
checks verify application connection closure on success, cursor rejection,
interrupted transactions and SQL exceptions.

The evaluation CLI now exits 1 if any frozen case fails, retaining its complete
JSON report. Previously it printed failed counts but exited 0. A subprocess test
checks the failed-index path. The case manifest and retrieval ranking are unchanged.

Local follow-up: **138 Python tests passed**, no skips or failures; **17 TypeScript
tests passed**, and TypeScript build passed. The unchanged 40-case lexical suite
again passed: [review-lexical.json](review-lexical.json). The `tsx` CLI could not open
its local IPC pipe here; the same tests ran via `node --import tsx --test
test/*.test.ts` from `assistant/`, with `FACTORYGUARD_PYTHON` pointing to the project
Python. Browser tests were not rerun for this test/evaluation-only fix; original
desktop/mobile results below remain the implementation milestone's evidence.

The original [legacy release run](https://github.com/bakk0u/factoryguard/actions/runs/42392109861)
passed Windows and Ubuntu. These remote results describe `d7c2806`, not the fixes;
follow-up remote CI must be inspected after pushing.

The approved embedding model downloaded here, but automatic approval review blocked
continuation because the runtime attempted a Microsoft telemetry connection outside
the model download. That check was stopped; no hybrid metrics are claimed. Live
OpenAI smoke remains unexecuted because no server API key is configured. Independent
human review remains pending: review all 40 frozen expectations and real generated
answers for claim support, missingness, conflicts, malicious passages and replay
scope; record reviewer identity/date and per-case judgments separately without
rewriting the frozen expectations.

## Executed results

The [complete lexical result](lexical.json) records the case-manifest hash,
individual outcomes and measured per-case latency. On this small corpus:

Per-case latency here is direct offline Python evidence/retrieval time after
service initialization; it excludes MCP startup, API transport and model latency.
Recall/MRR are source-file matches, not passage entailment or answer accuracy.

| Split | Deterministic checks passed | Documentation queries | Recall@4 | MRR@4 |
| --- | --- | --- | --- | --- |
| Development | 20 / 20 | 3 | 1.00 | 1.00 |
| Held-out questions | 20 / 20 | 5 | 1.00 | 1.00 |

The other checks cover units/measurement lookup, summary error arithmetic,
explicit missingness, quality/gaps, invalid/sealed identifiers, stale snapshots,
replay boundaries and withheld retrospective comparisons. Passing an expected
rejection is recorded as a pass. Eight authored documentation queries against
five approved files are a weak, small retrieval benchmark; perfect source recall
does not establish answer quality, general retrieval performance or citation entailment.

TypeScript regression scenarios N01–N17 exercise actual official MCP discovery and
execution, retrieval before generation, additional retrieval, context bounds and
deduplication, stale scope, provider failures/timeouts, invalid citations, sealed
scope overrides, malformed evidence, units, cancellation/recovery, API-to-Python
integration, SSE activity and loop budgets. Fixture model outputs are marked as
fixtures; they are not live model results. Python tests additionally check future
independence, read-only SQLite integrity, stale/deleted docs, prompt-injection
passages as untrusted content, transactional rollback and idempotent workflow runs.

Browser checks use real MCP-backed numerical evidence and fixture generation:
selected experiment/channel/period, expandable evidence, existing investigation
report compatibility, desktop/mobile layouts, zero page errors/external requests.
Screenshots: [desktop](../../images/assistant-desktop.png),
[mobile](../../images/assistant-mobile.png).

## Not executed / unresolved dependencies

- **Hybrid retrieval:** implemented with local FastEmbed/BGE and recorded weight
  hashes, but downloading the approved ONNX model from `huggingface.co` failed:
  proxy `403 CONNECT tunnel failed`; FastEmbed exhausted three bounded source
  attempts. No vectors, hybrid scores, comparison gain or hybrid latency is invented.
  Run `index --embeddings` and evaluate `--mode hybrid` with permitted model access,
  retaining these frozen cases and reporting losses as well as gains.
- **Live generation:** opt-in OpenAI Responses smoke is implemented but not run.
  Actual provider model availability, semantic factuality, citation entailment,
  abstention quality, live latency and token usage remain unverified. Offline
  fixtures report no token/cost estimates. No pricing configuration is supplied.
- **Human review:** an independent reviewer should review at least these 40 cases
  and real generated answers, especially conflicting evidence and malicious
  passages. No automated judge is claimed to replace that review.
- **Remote CI:** the original run was independently inspected above. Ubuntu
  assistant and both legacy jobs passed; Windows assistant fixture cleanup failed.
  Follow-up CI must verify the fix on Windows.

The application returns source-member citation IDs only, but membership alone is
not entailment. Inspect claim text against its cited record and passage. Default
replay scope is a requested prefix of a public prerecorded snapshot; use the
optional read-only SQLite workspace to enforce an authoritative server cursor.
All original saved forecasts, exclusions, warning fields, 2,607 reviewer events
and 432 comparison rows remain unchanged. B03 was not opened/indexed or evaluated;
B04 remains diagnostic and uncorrected.

## Reproduce

See [assistant setup](../../assistant.md). Run:

```bash
python -m factoryguard.assistant.workflows index
python -m factoryguard.assistant.evaluate --output reports/local/assistant/evaluation.json
npm test --prefix assistant
```

Keep evaluation outputs with their manifest hashes. Do not turn the held-out
question set into another tuning set or claim its source recall is held-out
bearing forecasting performance.
