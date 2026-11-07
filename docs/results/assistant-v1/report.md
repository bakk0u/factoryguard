# Assistant evidence/retrieval verification

This is an **offline engineering evaluation**, not a live LLM quality score,
independent human-reviewed benchmark, fault detector or new bearing-model campaign.
Cases are explicitly labelled in [cases.json](../../../assistant/evaluation/cases.json):
40 expectations authored/reviewed against current source by the implementation
author, 20 development and 20 held-out questions. Independent human review remains
pending; the two question splits are not new independent bearing experiments.
No search/tuning was performed to improve held-out scores after evaluating them.

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
- **Remote CI:** new Windows/Ubuntu assistant workflow is configured, but final
  remote results must be checked separately if the local API remains Forbidden.

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
