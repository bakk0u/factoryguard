# Persistent context and Graphify

## Operational verification (2026-11-07)

Real Graphify 0.9.103 is installed in `.tools/`; the custom standard-library script
is a safety/freshness wrapper, not an alternative graph engine. Status returned
FRESH; the required `Store replay notes reset` query returned real Store methods,
source locations and related tests within its 1,200-token cap. Memory snapshot
hash, 2,607 events, smoothing selection, 12.83% rounded gain and .2/.5/.2 direction
settings were checked against the pinned artifacts.

The integration and startup preference are committed on `graphify-project-memory`
(`387afe7`, `2dee5c5`); master is still `589f502` and does not yet contain them.
Selecting master in a future task will therefore not supply these instructions.
Use the integration branch or merge after review; no merge is performed here.

Root AGENTS provides the automatic instruction-discovery entry point. Reading
PROJECT_MEMORY and running the commands are agent actions required by those
instructions, not automatic memory injection or hook execution. The installed
Codex CLI 0.163.0 `debug prompt-input` diagnostic failed with read-only filesystem
errors, so this environment could not independently exercise a fresh-session
prompt assembly/skill discovery. Do not call that test passed. Existing-session
CLI retrieval, memory integrity and instruction files are verified. Restart from
the repository root with this branch selected; on a fresh clone run `setup`.

FactoryGuard now has two complementary context layers:

1. `PROJECT_MEMORY.md`: short, human-reviewed purpose, constraints, source map,
   results qualifications, verified history and next-task pointers. It is read
   at session startup through AGENTS.md and works without any external tools.
2. `graphify-out/graph.json`: local AST graph for scoped structural questions.
   Ask a bounded query, then verify behavior at the returned source locations.
   It does not interpret scientific validity or authorize data access.

## Verified official installation

Official upstream: <https://github.com/Graphify-Labs/graphify>, documentation:
<https://docs.graphify.com>. Reviewed upstream HEAD on 2026-11-07:
`16218bfc80d4ca2799734d045039f7ed1a5fa9fb`. Official PyPI package **graphifyy**
(double y); executable **graphify**. Installed and verified version **0.9.103**.
No similarly named third-party package is used.

The official README supports `uv tool install graphifyy` and project installation
with `graphify install --project --platform codex`. Installed-version CLI help was
checked rather than assuming commands from a previous conversation. In this
version the Codex installer writes `.codex/skills/graphify/`, an appended AGENTS.md
block and `.codex/hooks.json`. These are project-scoped, not user-global changes.
The optional Codex hook is intentionally a no-op upstream; its command delegates
through our root-relative helper so it does not require a global Graphify on PATH.
It performs no rebuild, model call or external request. Existing AGENTS instructions
are retained, with a short bootstrap/policy section added before the historical
milestone authorizations.

Launch future Codex sessions from the repository root so project instructions,
skills and the root-relative hook command are discoverable. The CLI was exercised
from this Codex session; installation does not retroactively reload the current
session's skill catalog or register an MCP tool. Root AGENTS guidance and the
standard-library helper provide the reliable query path without that reload.
Packaged skill copies retain upstream LICENSE/NOTICE material; this is not a new
licence declaration for FactoryGuard itself.

```bash
python scripts/project_context.py setup
python scripts/project_context.py build
python scripts/project_context.py status
python scripts/project_context.py query "Store replay notes reset"
python scripts/project_context.py explain "Store"
```

`setup` uses uv's officially supported isolated tool install, pinned to 0.9.103,
under ignored `.tools/uv-tools/` and `.tools/bin/`. Install uv separately if missing
using <https://docs.astral.sh/uv/getting-started/installation/>. FactoryGuard's
`.venv`, package requirements, runtime architecture, workflows and deployed site
do not gain Graphify dependencies. No user-global Codex configuration is edited.
The official skill supports optional parallel extraction, but this code-only setup
does not need it and does not enable agents or edit user-global `multi_agent` flags.

The helper runs from the repository root regardless of its caller's directory,
requires the pinned tool version, disables query logging, and forces
`GRAPHIFY_BACKEND=none` for every Graphify subprocess. No API keys or semantic LLM
calls are needed. Use `python` from an available Python 3.12 environment (or the
existing `.venv`); the helper itself uses only the standard library.

## Coverage, exclusions and limitations

`.graphifyignore` prunes raw/data storage, reports, saved payloads in site/source,
dependencies, skills, docs and generated outputs. The graph never reads B03 data,
private notes, archives or waveforms. AST source/test references to a reserve guard
are code, not access to reserve data. `.graphifyrc` sets query budget 1,200 tokens
and depth 2; narrow questions if output is truncated instead of reading the full
graph. No cloud/MCP service, Git hook, watcher or background process is installed.

The graph records modules/symbols, imports, calls, containment and inferred
resolution with EXTRACTED/INFERRED confidence labels. It is an aid, not exhaustive
static proof: some top-level scripts have no modelled symbols; notebook contents,
Markdown and JavaScript embedded inside dashboard HTML are not semantically
indexed. Refer to PROJECT_MEMORY.md for direct documentation/UI pointers. The
upstream report's "cluster-only: file stats unavailable" is not a claim of full
repository coverage. The initial corpus was 85 code files before integrating
newer remote work and this helper; current node/edge counts are in provenance.

Verified example: `explain Store` identifies `release/store.py:L20`, its connection/
step/reset/note methods, and EXTRACTED calls from application export/server/create,
with associated replay/concurrency tests. `scripts/project_context.py` validates
the real application-to-Store relationship, source-file existence and graph schema,
and rejects excluded/traversing graph paths or dangling edges. The integration
tests and query smoke checks ensure this is useful retrieval, not a placeholder.

## Updates and freshness

After source/config/memory changes or a branch switch/pull:

```bash
python scripts/project_context.py update
python scripts/project_context.py status
```

The official **incremental** command in 0.9.103 is `graphify update .`: it uses
local AST extraction/cache and changed-file detection. It does **not** accept
`--code-only`; that flag belongs to initial `graphify extract . --code-only`.
Our helper then runs `cluster-only . --no-label --no-viz` and records provenance.
If no graph exists, update performs the initial code-only build. For a fresh
clone with the committed graph but no local cache, the first update can reparse
the corpus; subsequent updates reuse the local manifest/cache. Documentation-only
changes are summarized manually in project memory, not sent to a semantic backend.

`graphify-out/provenance.json` records graph SHA256, tool version, base commit,
counts and content hashes of narrowly scoped Git-listed source/config files plus
memory/instructions. Additions/deletions are detected. Status rejects a stale
fingerprint or modified graph before queries. A commit-ID difference alone is
not stale when indexed content is identical; the recorded source commit may be
the parent of the integration commit. Do not claim the entire repo is fresh from
mtime alone or from a successful command without checking content.

Only graph.json, GRAPH_REPORT.md and provenance.json are versioned. Caches, paths,
logs, HTML and local tool environments are ignored. Source paths in the persisted
graph are relative. Upstream defaults may write local absolute markers in ignored
cache files; these are not part of the shared context. On legitimate removals,
upstream may refuse graph shrink; review the diff before any explicit force rebuild.
Never use force to bypass a raw-storage or reserve-plan restriction.

## Maintaining memory

Keep PROJECT_MEMORY.md around 1,500 words or less. Update affected facts, cite
paths/commits and exact checks, and record blockers without rewriting historical
evidence. Move long decisions to docs/ and Git. Read only task-relevant sources
after a query; do not load the whole graph, report, skill sidecars or project log
into every session. When Graphify is missing/unavailable, follow the file map and
targeted rg; the core context remains usable offline without an installation.

Tests: `python -m unittest discover -s tests -p test_project_context.py -v` requires
no installed Graphify, API or raw files. Full existing application tests should
still pass using the project's documented environment. No numerical results,
features, model settings, raw files or reserve plans are changed by this integration.

Verified locally on 2026-11-07: all 122 tests passed (116 existing plus six context
tests). The graph contains 688 nodes / 1,926 relationships with real relative
locations. Query/explain retrieval and the one-hop EXTRACTED `export() → Store`
path succeeded; an unchanged incremental run skipped extraction. Zero LLM token
cost is reported for this AST build; no percentage token-savings claim is made
without a workload benchmark. Current tests did not execute models against B03.
