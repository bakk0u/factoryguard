# Evidence-grounded investigation assistant (optional, local)

This extension adds an optional TypeScript application service; the existing Python
CLI, SQLite replay app, saved forecasting results and static public site stay usable
independently. No forecasting model is retrained. The static site has no assistant
backend or credentials. Shared dashboard markup has an honest static unavailable
state; only the local assistant service injects the API integration script.

## Setup and one-command startup

Use the existing CPython 3.12 environment and Node.js >=22:

```bash
python -m pip install -r requirements-assistant-lock.txt
python -m pip install --no-deps -e .
npm ci --prefix assistant
python scripts/start_assistant.py
```

Open <http://127.0.0.1:8785/> on the same machine. The reviewer entry is **Start
here**. Choose **Walk through an investigation** for deterministic B01/A
observations 1–3, or **Explore measurements** to choose another revealed period.
The assistant sits beside the matching selected-channel plots (directly after
them on mobile), with visible experiment/channel/range/replay boundary. Suggested
questions populate the input without submitting. Only **Ask about this period**
submits. Default **offline mode** still retrieves real
saved measurements through actual MCP, but generation uses a visibly labelled
deterministic fixture. It demonstrates plumbing, not language-model capability.
No Python server, SDK or key is required by visitors to the existing public site.

The walkthrough uses local deterministic guidance, not a saved AI answer. New
responses are labelled **Offline fixture response** or **Newly generated answer**
and show their captured question and scope. Observations, possible explanations
and uncertainty/limitations remain separate. Citation buttons open matching
values, units, source text and provenance in a keyboard-focusable panel; Escape
closes it and restores focus. Detailed JSON and staged activity stay expandable.
The static export retains the walkthrough, suggestions and exploration with an
honest unavailable state for new generation. This presentation changes no backend
scope or validation rules. Browser tests target only a health-confirmed offline
service, and generated/error/cancel states can be mocked without a provider call.
Layout 3 keeps measurements beside the assistant on desktop and uses concise
labels/disclosures. Its interactive Engineering diagram explains the actual
retrieval-before-generation path and distinguishes future/unevaluated components;
diagram interactions make no API or model request.

### Optional XGBoost test setup on macOS

The complete Python regression suite exercises XGBoost on small synthetic fixtures.
With the locked assistant environment already installed, add the campaign extra:

```bash
env -u OPENAI_API_KEY .tools/bootstrap/bin/uv pip install --python .venv/bin/python --no-deps -r requirements-campaign.txt
```

The requirements file and `.[campaign]` now select `xgboost==3.0.5` on macOS and
retain `xgboost-cpu==3.0.5` elsewhere. The latter has Linux/Windows amd64 wheels,
not macOS wheels; see the [official 3.0.5 installation guide](https://xgboost.readthedocs.io/en/release_3.0.0/install.html).
Core/assistant pins are unchanged. If pip is present, the equivalent command is
`.venv/bin/python -m pip install --no-deps -r requirements-campaign.txt`.
On a fresh environment install the existing core/assistant lock first; `--no-deps`
here deliberately preserves its already-installed package versions.

Only diagnose OpenMP if import actually reports missing `libomp.dylib`. Standard
Homebrew users can install it with `brew install libomp`. In this checkout, no
Homebrew is installed: the observed macOS 27.2/arm64 setup uses an official public
Homebrew libomp 23.1.5 bottle in ignored `.tools/`, checksum-verified before reading
a single known archive member. No system package or global loader setting changes:

```bash
env -u OPENAI_API_KEY curl --fail --location --silent --show-error -H 'Authorization: Bearer QQ==' \
  https://ghcr.io/v2/homebrew/core/libomp/blobs/sha256:64eacbcd08fbec3ebb7076be89466a53d5548a7dbee3542d756b788047277589 \
  -o .tools/libomp-23.1.5-arm64.tar.gz
env -u OPENAI_API_KEY .venv/bin/python scripts/setup_macos_openmp.py .tools/libomp-23.1.5-arm64.tar.gz
env -u OPENAI_API_KEY .venv/bin/python -c 'import xgboost; print(xgboost.__version__)'
env -u OPENAI_API_KEY .venv/bin/python -m unittest discover -s tests -p test_release_modeling.py -k future_independence -v
```

`QQ==` is the public registry's anonymous download value, not a private API key.
The helper is for macOS arm64 with the repository-local `.tools` Python used by
`.venv`; it refuses another interpreter location, wrong checksum or replacement
of an unrelated library. It links the local runtime into that interpreter's lib
directory, where the observed loader searches. Other macOS versions/architectures
should use their supported runtime rather than assume this bottle is compatible.
The installed package imports as `xgboost` on both distribution paths. This setup
does not run a project campaign or modify saved forecasting results.

Local startup and live smoke use Node's standard `util.parseEnv` parser with only
the repository-root `.env.local`, independent of the working directory. They never
search parent directories or load `.env` or `assistant/.env.local`. Existing process
values take precedence, including empty values. Keep `.env.local` ignored,
untracked and owner-only (`chmod 600 .env.local` on POSIX); do not commit or print it.
No file is created or overwritten by startup. `assistant/.env.example` lists names.

For opt-in live generation, provide `OPENAI_API_KEY` privately in that file or the
server environment and run `.venv/bin/python scripts/start_assistant.py --live`.
Model defaults to `gpt-5.4-mini`; `FACTORYGUARD_LLM_MODEL` is preserved. Live startup
rejects missing/blank credentials before generation. Offline startup removes the
process credential and never loads the file credential. Only the Node generation
server/live smoke receives it; Python site builds, MCP and Git subprocesses do not.
The launcher does not parse credentials in Python. Browser assets and traces do
not contain keys. Configuration files cannot enable live mode or the smoke gate.

After explicit approval, run this from the repository root (POSIX):

```bash
FACTORYGUARD_ALLOW_LIVE=1 npm run live-smoke --prefix assistant
```

PowerShell: set `$env:FACTORYGUARD_ALLOW_LIVE='1'`, then run the npm command.
This performs one fixed B01/A replay investigation at observations 1–3, with a
60-second overall timeout, at most three model turns, 2,200 output tokens per turn,
nine evidence calls and at most one SDK retry per turn. It preserves the configured
model and prints only status/model/usage/latency metadata. No live model check is
claimed without executing it. Preparation and offline checks make no paid requests.

## Retrieve → assemble → generate

```mermaid
flowchart LR
  UI[Existing dashboard selection] --> API[Fastify runtime validation]
  API --> ORCH[TypeScript request orchestrator]
  ORCH --> CLIENT[Official MCP TypeScript client]
  CLIENT <-->|stdio MCP discovery and calls| PY[Official Python MCP server]
  PY --> EV[Read-only evidence services]
  EV --> SNAP[Pinned B01 B02 B04 replay and saved metrics]
  EV --> SQLITE[Optional already-revealed SQLite events]
  PY --> DOC[Allowlisted versioned documentation index]
  CLIENT --> PKG[Bounded context package]
  PKG --> LLM[Responses API or offline fixture]
  LLM --> CHECK[Schema and citation validation]
  CHECK --> UI
  ORCH --> TRACE[Local staged trace]
```

Before the **first** generation call, orchestration retrieves replay state, Python
period summary, quality report, an observation page and documentation through the
MCP client. It does not give a language model an empty context and hope for a tool
call. Subsequent model turns may request more retrieval, with the original user
selection enforced again on every call. OpenAI requests are deliberately stateless
per turn: each receives the question plus the newly assembled context package;
Responses history/`previous_response_id` is not partially replayed.

The versioned package contains numerical records with units, provisional timestamps,
channel/experiment/position, stable source IDs and snapshot hashes; approved passages
with path/section/document hashes; missing-evidence entries; warnings and limits.
It deduplicates IDs and passage content, prioritizes summaries/quality and bounds
serialized context to 28,000 characters. Omitted records and missing passages are
explicit. Numerical calculations run only in Python, using saved values/errors.
The LLM receives no raw waveforms or private investigation notes.

Structured answers separate observations, retrieved explanations, interpretations,
missing evidence, limitations and suggested steps. Claims carry evidence IDs;
the application rejects IDs absent from the assembled package. Citation membership
is mechanically checked; semantic entailment and general factual correctness of
live model prose are **not** established by this check or the offline fixture.

## Contracts and read-only tools

`Selection`: experiment B01/B02/B04, channel A/C, inclusive **1-based observation
positions** start/stop, as_of, replay/retrospective mode and exact snapshot SHA256.
These are not elapsed operating-time windows. Unknown fields, sealed/invalid runs,
invalid channels/periods and mismatched snapshots are rejected. The server exposes
seven SDK-discovered tools:

| Tool | Bounded result |
| --- | --- |
| list_experiments | Allowed runs/roles only, no B03 |
| get_replay_state | Selected visible position and provisional timestamp |
| get_measurements | At most 12 bursts/page, units, saved issued/settled forecasts/errors, warnings |
| get_investigation_summary | Whole selected visible period, deterministic RMS/error summaries |
| get_data_quality_report | Gap/warning positions (first 30 with total counts), warm-up/reference support |
| get_model_comparison | At most 12 saved rows for selected run/channel/group; retrospective only |
| search_documentation | At most six approved passages, versioned citations |

The exact runtime contracts are in `assistant/src/contracts.ts`, Python Selection
and MCP-discovered schemas. Observation units/finite-or-null values, channel/position
scope, final answer structure and citation membership are checked at runtime.
There is no SQL tool, arbitrary path parameter, shell tool, note tool or machine
control. Model tool schemas are derived from MCP discovery rather than invented.

Default replay uses the explicitly supplied as_of position on a public precomputed
snapshot. It is a causal evidence boundary, not access control over already-public
files. Set `FACTORYGUARD_EVIDENCE_WORKSPACE` for authoritative local cursor checks:
Python opens SQLite read-only, reads only events at/before the revealed cursor,
and checks them against the pinned events. TypeScript never writes SQLite. No
ordinary loader/guard is relaxed for B03.

Replay never exposes future observations/outcomes, and full-run comparison scores
are withheld. Only pre-replay methodological documentation is searched in this
mode; retrospective analysis is explicitly labelled. Fixed other-development-run
references are pre-existing baselines, not the selected run's future observations.
Settled errors are grouped by target arrival within the selected period; the
issuing burst can precede the period. All suspect measurements remain recorded.

## Reliable Python-owned workflows and retrieval

```bash
python -m factoryguard.assistant.workflows validate
python -m factoryguard.assistant.workflows refresh
python -m factoryguard.assistant.workflows index
python -m factoryguard.assistant.workflows bundle --selection '{"experiment":"B01","channel":"A","start":1,"stop":8,"as_of":8,"mode":"replay","snapshot":"9a3da297dd848bf079a0c8ff1fa9fd3be1dea42894e867fb51c2fdf35efa624a"}'
python -m factoryguard.assistant.evaluate
```

Evaluation writes the per-case JSON report and exits 1 when any case fails, so
CI can detect retrieval regressions. Keep the frozen case manifest unchanged.
See the [verification follow-up](results/assistant-v1/report.md#follow-up-verification--2026-11-07)
for the Windows fixture cleanup fix and current dependency/review limitations.

All outputs default to ignored `reports/local/assistant/`. Validation checks pinned
source hashes/allowed experiments; refresh reuses content-addressed derived
summaries when unchanged; bundles are atomic selected-period evidence outputs.
Index refresh handles changed/deleted documents in one SQLite transaction with
run records; injected interruptions roll back and reruns recover. Repeated unchanged
inputs do not duplicate records or embeddings. Temporary files are fsynced and
atomically renamed. Source/raw output protection is reused. Dagster was deliberately
not added: a small explicit runner has one orchestration owner, fewer dependencies
and no scheduler; the required operations are independently callable.

Documentation is an explicit allowlist (`assistant/retrieval.py`): current feature
definitions, frozen release protocol, investigation workflow, and retrospective-only
current model card/development assessment. Historical model-card sections, raw
data, notes, secrets and all other files are excluded. Initial retrieval is a
reproducible lexical term-frequency/IDF baseline. Stable passage IDs include
source path, section, document hash and chunk position; text is deduplicated.
Stale/deleted indexed passages fail closed until refreshed.

Optional local embeddings: FastEmbed 0.9.1, `BAAI/bge-small-en-v1.5`, MIT,
384-dimensional quantized ONNX from `Qdrant/bge-small-en-v1.5-onnx-Q`. An explicit
`index --embeddings` downloads weights into ignored `.tools/embeddings`; successful
builds record exact ONNX/tokenizer/config hashes and refuse a changed cache during
query. Hybrid ranking is reciprocal-rank fusion (constant 60) of lexical and local
embedding ranks. Query uses cached weights only. No embedding/vector cloud service.
The model download was blocked here by `huggingface.co` proxy 403; real hybrid
quality/latency cannot be reported. Missing vectors never silently become synthetic
embeddings or an unlabelled lexical fallback. Do not recommend hybrid over the
baseline until a real comparison succeeds.

## SDKs, limits, lifecycle and trace interpretation

Verified official SDK documentation/source: OpenAI TypeScript README Responses API
and declarations from installed `openai@7.53.0`; official MCP TypeScript client/
stdio APIs at `@modelcontextprotocol/sdk@1.32.2`; Python SDK tag v1.30.0 commit
`8c2fa6eabacde869d75568e33b9d466b58c2f512`, FastMCP typed tools and stdio. Python
1.30.0 is an explicitly pinned supported maintenance line (v2.3.0 was current);
do not upgrade major versions without integration tests. Fastify 5.12.8 and Zod
4.6.7 supply the application/runtime boundary. npm lock and optional Python lock
pin dependencies without changing the existing core requirement pins.

Each investigation owns a fresh local MCP subprocess and closes it on success,
error or cancellation. A subsequent request starts cleanly after failure; invalid
requests are not retried. MCP requests time out after 15s. The model has at most
three turns, nine total evidence calls, 2,200 output tokens/turn, SDK timeout 30s
and at most one SDK retry for transient provider failures. Whole-request timeout
is 60s, three concurrent jobs, 50 retained job slots. The API is loopback-only with
same-origin checks; it is not authenticated multiuser/enterprise infrastructure.

Offline review follow-up: identical in-flight validated requests from the same
session coalesce to one job; all question/selection/retrieval fields participate.
Completed responses are not an evidence cache: a deliberate later request rechecks
the current cursor. Frontend SSE loss or unknown POST acknowledgement keeps the
submission locked, without automatic resubmission. An identified job can be
cancelled; acknowledgement releases the UI while cleanup may still be finishing.
This is not durable idempotency across completion/restarts or hosted access control.

Prompt v2 clarifies descriptive current-minus-previous changes, signed versus
absolute errors and non-causal interpretation. Provider input uses a lossless
shared-source table; full canonical provenance remains in the trace/browser
context. Model tool schemas omit application-owned selection and unreachable
definitions; the MCP client always inserts validated selection independently.
Refusal/incomplete responses fail explicitly. Response activity metadata no longer
duplicates full tool/context/answer payloads; those remain in the local trace.
Numerical evidence is scoped to the selected channel, including change/reference
maps and forecast notices. Lexical retrieval v2 normalizes a small explicit word
list without changing chunk IDs or document visibility. Context assembly validates
once, rejects conflicting citation IDs and explicitly reports missing-list truncation.
No cross-request evidence cache or shared MCP process was added.

The [dashboard offline audit](results/assistant-v1/dashboard-offline-review.md)
reviews saved request `2d7ed00c-f795-4afe-a177-83fbfb7d5284` claim by claim and
distinguishes its original live result from these later offline-only changes.

POST `/api/investigations` returns 202/request_id; GET that URL returns state/result,
GET `/events` streams staged progress over SSE, POST `/cancel` aborts. The browser
shows no partial free-form model claims while a structured answer is incomplete.
Controls use the existing selected experiment/channel/period/replay context.

Local atomic trace JSON records request/session IDs, prompt version, selection,
retrieval configuration, tool results/failures, assembled packages, model identity,
usage when available, latency and validated final answer. Failure stages distinguish
retrieval, assembly and generation (or API/trace validation). The trace also records
checkout HEAD and a dirty-worktree flag, rather than misrepresenting uncommitted
code as a clean source revision. Provider refusals/
malformed JSON fail explicitly; unsupported citations are rejected. Model response
token usage is null when unavailable, never estimated from fixture text. No monetary
cost is recorded because no documented pricing configuration is supplied. User
questions/traces can be sensitive: retain locally, never add them to Git. Credential
patterns and the configured key are redacted; no environment dump is stored.

Provider failures now carry `provider_error` in the failure trace/event, local API
failure and smoke stderr: category (API/connection/local), HTTP status, API code,
type, parameter, request ID, and a message capped at 500 characters. Missing fields
remain null. Only selected scalar fields are retained; API messages come from the
message field rather than the SDK's potentially serialized error body. Credentials
are redacted before bounding; structured dumps and unsafe messages are omitted.
No raw exception/cause, headers, request bodies or environment is emitted. SDK
logging is explicitly `off`, even if `OPENAI_LOG=debug` is inherited. See the
[official SDK error documentation](https://developers.openai.com/api/reference/typescript).

The single authorized live smoke on 2026-11-09 retrieved all five initial evidence
results for B01/A observations 1–3, assembled context at 420 ms and failed during
generation at 3,637 ms. The old handler retained only `error.name` (`Error`), so no
HTTP status, API code, request ID, original message, returned model or usage can
be recovered. This does not identify an authentication, quota, invalid-request or
connection cause, or prove the API received the request. Schema construction
succeeds offline. The diagnostic fix passed the build and 30 offline TypeScript
tests, including mocked SDK failures, credential redaction, logging suppression,
trace and local API propagation. It made no further live requests. A new bounded
smoke requires fresh explicit authorization; pipeline success, answer quality and
browser verification remain separate claims.

Later on 2026-11-09, one separately authorized smoke returned HTTP 429,
`credit_balance_exhausted` / `insufficient_quota`. After the user reported adding
credits and authorized one further execution, the unchanged bounded smoke passed:
`gpt-5.4-mini-2026-03-17`, 7,109 input tokens, 2,174 output tokens, one model turn,
13,685 ms. Replay state → investigation summary → quality report → measurements →
documentation retrieval all preceded context assembly and generation. All 29
citation references resolve to eight retrieved IDs; schema/citation validation
passed. The selected scope is B01/A observations 1–3, as_of=3. The answer notes
warm-up/reference limitations, provisional timing and missing sustained-change
evidence; it does not establish fault/health/RUL. This is one successful live
pipeline check, not broad answer-quality or new dashboard/browser verification.
The ignored local trace is
`reports/local/assistant/traces/c3e49924-14c9-46ed-8704-c58e8cef5e86.json`.
No command was rerun automatically and no configuration/model/billing change was
made by the assistant. Any further live execution needs fresh authorization.

## Verification, interpretation and troubleshooting

[Evaluation report](results/assistant-v1/report.md) distinguishes executed offline
checks from unexecuted live/hybrid/human review. Tests:

```bash
python -m unittest discover -s tests -v
npm run build --prefix assistant
npm test --prefix assistant
CHROMIUM_PATH=/usr/bin/chromium node assistant/test/browser.cjs
```

For existing-only installs, optional assistant tests explicitly skip when MCP is
absent. Install the optional lock to execute them. Browser checks require Playwright
and Chromium in addition to application dependencies. On Windows omit the Linux
browser override and use the appropriate executable path. No browser test data is
silently substituted for the real MCP-backed evidence.

- Missing key: default offline mode works; live requires a server key and explicit
  flag. Do not put keys into browser storage, a URL or the static site.
- Missing/stale documentation index: run the Python index workflow; numerical-only
  responses carry explicit missing-document limitations.
- Snapshot mismatch: restore matching pinned artifacts; never waive the hash check.
- SQLite ahead-of-cursor request: reveal observations through the existing app or
  choose a visible period. Do not query future rows to fill missing evidence.
- Retrieval versus model failure: inspect the trace's staged events, not only an
  empty answer. Cancel/retry starts a new bounded request; avoid retry loops.
- Embedding 403: obtain the approved model through permitted access, verify/store
  its hashes and run the frozen lexical/hybrid comparison. Do not bypass policy.

CV suggestions supported by implementation (avoid claims of fault-detection or
unexecuted LLM accuracy):

- Built an optional TypeScript/Python investigation assistant with official MCP
  tool discovery, deterministic numerical evidence, replay-safe retrieval and
  schema/citation validation.
- Implemented atomic documentation-index workflows, bounded orchestration and
  staged failure traces, with offline end-to-end tests and a frozen 40-case
  evidence/retrieval evaluation set.
