# Optional evidence-first investigation assistant

Stacked on `graphify-project-memory` (starting commit `85b99af`); review the
persistent-context branch separately before integrating into master. No merge or
public deployment is included.

The local optional assistant now follows **retrieve → assemble context → generate**.
Fastify validates the selected experiment/channel/period/snapshot/as-of position;
the official TypeScript MCP client discovers and calls seven read-only Python
tools. Numerical summaries, quality warnings and approved documentation are
retrieved before the first Responses API call. Context is bounded/deduplicated,
missing evidence is explicit, scope is enforced on additional retrieval and final
citation IDs must belong to the context. Progress, cancellation, failures and
the final answer are traced in separate retrieval/assembly/generation stages.

Python owns deterministic evidence and transactional index/refresh/bundle workflows.
TypeScript never writes SQLite. The local service reuses the reviewer dashboard,
adding an optional period question interface with inspectable citations. Public
static Pages, old CLI/export/notes, 2,607 saved events, 432 comparison rows and
direction-specific model settings remain unchanged. B03 stays sealed, B04
uncorrected, and no forecasting model is fitted or selected.

## Verification

- 122-test clean starting baseline; final 135 Python tests and 17 TypeScript tests passed.
- Actual MCP discovery/tool execution and API→MCP→Python end-to-end checks.
- Mandatory retrieval ordering, further retrieval, runtime units/scope, citation
  rejection, malformed responses, failures/timeouts, cancellation/recovery and redaction.
- Forty frozen offline cases (20 development / 20 held-out questions) passed their
  deterministic checks; documentation source recall@4 was 3/3 and 5/5 respectively.
  This is not a live LLM or independent human-reviewed accuracy result.
- Browser desktop/mobile, selected channel/period/replay prefix, evidence clicks
  and old report compatibility passed with no page errors or external requests.
- Synthetic demo, B01 demo/export, optional-dependency isolation and pip check passed.
- New optional Windows/Ubuntu workflow runs type/MCP/Python/evidence checks; final
  remote CI results remain pending if the local API returns Forbidden.

## Limitations and reproduction

`python scripts/start_assistant.py` is the single startup command after optional
setup in `docs/assistant.md`. Default generation is an explicitly labelled offline
fixture using real retrieved evidence. Live mode and a separate bounded smoke test
are opt-in with a server-only key; not executed here. Citation membership is not
semantic entailment. The optional BGE/ONNX embedding download failed from
`huggingface.co` with proxy 403, so real hybrid scores/gains are unmeasured rather
than replaced by synthetic vectors. Independent human review of cases and generated
answers remains pending. The 40-case benchmark is small and authored, not a claim
of general RAG quality or held-out bearing performance.

Architecture/contracts/setup/troubleshooting: `docs/assistant.md`.
Evaluation: `docs/results/assistant-v1/report.md` and `lexical.json`.
Screenshots: `docs/images/assistant-desktop.png`, `docs/images/assistant-mobile.png`.
