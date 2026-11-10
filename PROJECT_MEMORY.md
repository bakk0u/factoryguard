# FactoryGuard project memory

Verified 2026-11-10 (Europe/Berlin). This is orientation, not a source of new
authorization. Read AGENTS.md first. Recheck Git state and graph freshness; facts
below describe the reviewed checkout and can age. Do not paste the whole history.

## Purpose and hard boundaries

Recorded laboratory bearing-condition investigation: RMS forecasts/deviations,
thermal/operating context, warnings, fixed references and descriptive changes.
Not validated faults, health classification, damage onset, safety alarms or RUL.
Runs are separate bearings; A/C are vibration channels. Preserve synthetic demo.

- B01/B02: development selection. B04: diagnostic only; unresolved speed/load
  scaling, never silently corrected. **B03 stays completely sealed**, including
  integrity reads, unless a later explicit authorization and review permit them.
- No new training/search, downloads, thresholds, deployment, merge or raw writes
  implied by old milestone instructions. Raw archives/waveforms remain outside
  Git; preserve warnings, gaps, missingness and provisional CSV/MAT timestamps.
- Forecasts use only current/past completed bursts, never next-burst context.
  Next-observed-burst arrival varies; >24 provisional CSV seconds expires a
  forecast/resets history. References are development distributions, not healthy.

## Verified state and evidence

- Publication preparation 2026-11-10: `feature/assistant-setup-layout3` is based on
  master `c23c79d` (PR #6), following assistant PR #5. Current owner authorization
  permits the scoped assistant/setup/dashboard commit, feature push, draft PR to
  master and sanitized artifacts on `review-handoff`; no merge or deployment.
  Check live Git/PR state. Handoff policy is `docs/coordination/STATUS.md` on
  `review-handoff`; preserve its reviewer-owned `REVIEW.md`. Pages requires an
  explicit manual `PUBLISH` dispatch; feature/PR pushes only run offline CI checks.
- PR #1 merged in `fc772e5`. Reviewer/report work: `bb718c4`; source-review fixes:
  `f10b225`, `bb718c4`; site artifact upload: `d6a69a9`. Release docs: `5491b34`,
  `c2c791e`; public verification record: `77445c8`, live link: `2b9108f`.
- Public site: https://bakk0u.github.io/factoryguard/ . The committed
  `docs/release_verification.md` records an independently connected-browser check
  of populated B01 and downloaded JSON on 2026-10-27: build/source `fc772e5`,
  Pages run 40520283007. Original model-result producing commit/time remain
  unknown/null; website-build commit is separate. Do not replace known verified
  evidence with an environment-specific proxy failure or claim a fresh check.
- Saved reviewer snapshot: 377 B01 + 1,116 B02 + 1,114 B04 = 2,607 complete events;
  432 model comparison rows. `site/source-manifest.json` pins the derived data.
  Replay SHA256: `9a3da297dd848bf079a0c8ff1fa9fd3be1dea42894e867fb51c2fdf35efa624a`.
- Smoothing selected: 12.83% equal-run/channel MAE improvement versus persistence
  in reciprocal B01/B02 **development selection**, not held-out accuracy or fault
  detection. B01 alpha .2, B02 .5, B04 diagnostic .2; final pooled rule .5 is
  separate. All evaluated variants remain, including unfavorable ones.
- Prior handover: 116 Python tests; exact exported-event and comparison-row
  preservation; hosted browser regression checks. Earlier independently reported
  Windows/Ubuntu CI: d5be7be, run 40402759560. Do not infer later CI passes.
- Context integration check on 2026-11-07: all **122 local tests passed** (116
  existing + 6 context integrity/isolation tests). Local AST graph: 688 nodes,
  1,926 relationships; `export() → Store` verified EXTRACTED. Incremental no-change
  update and CLI query/path/explain retrieval succeeded. No new remote CI claim.
- API operations previously returned Forbidden; Git transport worked. Direct
  `file://` tests were blocked by local managed Chromium policy; CI requires them.
  Release v0.3.0 was proposed (package version .3.0); tag/release/About state must
  be rechecked, not assumed from the old proposed notes. No software LICENSE is
  declared in the reviewed root; dataset descriptors are attributed CC BY 4.0.

## Locate only the relevant components

| Question | Entry points / source of truth |
| --- | --- |
| CLI, local demo, export/API | `src/factoryguard/release/__main__.py`, `application.py` |
| Atomic SQLite replay, resets, notes | `src/factoryguard/release/store.py` (`Store`) |
| Reference bins / notices / sustained windows | `release/context.py`, `release/investigation.py` |
| Portable UI and reviewer-only controls | `release/dashboard.html`, `site/reviewer.js` |
| Static build, snapshot integrity | `scripts/build_reviewer_site.py`, `site/source-manifest.json` |
| Optional evidence assistant | `assistant/src/` (Fastify/MCP client/Responses orchestration), `src/factoryguard/assistant/` (Python read-only evidence/MCP/index/workflows), `docs/assistant.md` |
| Streaming loading / burst features | `src/factoryguard/data/paderborn.py`, `features/b01.py`, `pipelines/features_paderborn.py` |
| Frozen campaign / causal features / audit | `release/campaign.py`, `release/modeling.py`, `release/reporting.py`, `models/selection.py` |
| Scientific definitions / qualifications | `docs/feature_definitions.md`, `development_assessment.md`, `release_protocol.md`, `model_card.md` |
| Full saved comparisons / architecture | `docs/results/release-v3/`, `docs/architecture.md` (legacy inventories are historical) |
| Future reserve gate | `docs/b03_readiness.md`, `docs/review_handoff.md`, `configs/reserve_plan.json`, `release/holdout.py` (do not execute) |

Paths abbreviated as `release/...` are under `src/factoryguard/`; doc names after
`docs/...` stay in docs/. `docs/project_status.md` has a current entry followed by
a long historical log; read only relevant milestones. Source overrides stale prose.

## Session and verification commands

User preference: at the start of every session and before each new prompt, run
the status and baseline query below. After making changes, run the context update
before handoff. If stale, update before retrying the query; report unavailable
tooling honestly. Additional queries should be specific to the actual task.

Automatic-loading contract: launch Codex from the repository root on a branch
containing this integration. Codex loads root AGENTS instructions; they direct
the agent to read this file and run commands. Memory is not automatically inlined
and the optional hook does not execute startup commands. A fresh native prompt
diagnostic was blocked here by the Codex runtime's read-only filesystem; no
end-to-end future-session auto-load claim is made. Fresh clones need `setup` for
the ignored tool environment. No missing tool silently falls back to a fake graph.

Run from repository root. Existing `.venv` is the application environment
(CPython 3.12, requirements-lock.txt; campaign tests add requirements-campaign.txt).
Graphify lives separately in ignored `.tools/`, never install it into `.venv`.

```bash
python scripts/project_context.py status
python scripts/project_context.py query "Store replay notes reset"
python scripts/project_context.py explain "Store"
# If missing: python scripts/project_context.py setup
# If stale:   python scripts/project_context.py update
```

Read returned source locations, not the full graph/report. Default query budget
is 1,200 tokens, depth 2; narrow questions instead of automatically raising it.
For no Graphify installation, use the map and targeted rg; memory still works.
For Graphify, no semantic API key, cloud/MCP server, or hooks rebuilding on Git
operations. The optional application's read-only evidence MCP server is separate.

```bash
MPLCONFIGDIR=/tmp/factoryguard-matplotlib XDG_CACHE_HOME=/tmp/factoryguard-cache \
  .venv/bin/python -m unittest discover -s tests -v
.venv/bin/python scripts/build_reviewer_site.py --output reports/local/reviewer-site
CHROMIUM_PATH=/usr/bin/chromium node scripts/verify_reviewer_workflow.cjs
```

Windows: use `.venv\Scripts\python.exe`; omit Linux cache/browser overrides.
The browser check requires Playwright/Chromium. Do not run it or the full suite
for every documentation-only change. Match checks to risk; fresh demo output
paths avoid stale artifacts. Use `docs/development_release.md` for full setup.
Website notes are browser-local, isolated by snapshot+experiment (warned tab-only
fallback); SQLite persistence applies to the optional local-server app, not Pages.

## Next work and maintenance

Reviewer redesign / Layout 3 (2026-11-10): canonical replay engine stays in
`release/dashboard.html` + `site/reviewer.js`; `site/reviewer_experience.js` and
`site/reviewer.css` add Start here, deterministic five-step B01/A 1–3 guidance,
verified artifact-derived facts, scoped assistant next to selected-channel plots,
readable answer sections/citations, queue filters and methods/engineering views.
`site/layout3.css` adds the approved narrow rail/Attention/workspace layout;
`site/architecture.js` provides 14 interactive system components with examples,
source contracts, focus return and distinct future/unevaluated labels. No diagram
action submits a request. Start has 119 visible words; charts/labels/disclosures
keep scientific limits accessible. Revealed-only rail filters share queue evidence.
Build script inlines sources; CSS is freshness-hashed. Static guidance requires no
key and explicitly marks new generation unavailable. Local assistant defaults to
fixture mode, suggestions do not submit, and traces stay expandable. No saved AI
answer or paid generation was used. Existing backend/model/config bounds remain.
Real Chrome via isolated `.tools/browser` Playwright 1.58.2 passed desktop/mobile,
keyboard/focus, citation and mocked states; legacy reviewer/notes/report/direct-file
and MCP-backed fixture browser checks passed. Build, **41 TS / 144 Python / 40 frozen
cases** passed without skips. Offline local service on `http://127.0.0.1:8786/`;
no claim of a new live-model check, remote CI or production readiness. Captures:
`reports/local/layout3/`; details: `docs/results/assistant-v1/layout3.md` (previous
redesign report/captures preserved). Current checks include all architecture
components, desktop parallel columns, tablet/mobile/no overflow and static map.

XGBoost setup is resolved: Python 3.12.16/macOS 27.2 arm64 uses pinned XGBoost
3.0.5 and checksum-verified local libomp in `.tools` via
`scripts/setup_macos_openmp.py`. Campaign markers use `xgboost` on Darwin and
`xgboost-cpu` elsewhere; unrelated packages unchanged. Reproducible setup/history:
`docs/results/assistant-v1/final-local-integration.md`. No saved-model retraining.

Local runtime uses `.venv` Python 3.12.16 and Node 24.22.1; prior environment
is preserved in ignored `.tools/venv-before-python312`. Core/assistant locks stay
pinned. Root-only dotenv parsing in `assistant/src/config.ts` preserves process
precedence, model choice and offline default; `.env.local` remains ignored,
untracked and owner-only. Python/MCP/site-build/Git children exclude credentials.
Safe provider diagnostics retain selected bounded/redacted status/code/type/
parameter/request ID/message without raw errors/headers/bodies/causes; SDK logging
is off. Earlier authorized smoke/credit-balance failures and one successful
`gpt-5.4-mini-2026-03-17` pipeline check are recorded in `docs/assistant.md`.
Those historical results do not verify the latest changed dashboard version or
imply permission for another paid request.

Dashboard offline audit (2026-11-09): preserved actual API response and trace for
`2d7ed00c-f795-4afe-a177-83fbfb7d5284`. B01/A 1–3/as_of=3, default dashboard
question, returned `gpt-5.4-mini-2026-03-17`, 12,155 ms, one turn, 7,116 input /
1,801 output tokens. All 25 citation references resolve to five records; quoted
numbers are correct. Qualify descriptive “sudden,” two-point absolute error change
and endpoint-only speed/load differences. Causal attribution remains unverified;
original nested off-channel numbers were a scope defect, now projected out.
Original artifacts remain unchanged; no original citation interaction was observed.
Screenshot rendering/control evidence is user-supplied, not a new browser check.

Offline changes: in-flight scope-aware coalescing and lost-connection guards,
compact response activities, one-pass/bounded context with explicit missing
truncation/conflict detection, lossless provider provenance/tool-schema compaction,
refusal/incomplete handling, lexical normalization and idempotent MCP close.
No evidence cache, pooled MCP or parallel retrieval. Build, 37 TS tests, 18 assistant
Python tests and 40 frozen cases passed. Full Python suite: 140 run, 139 passed,
one absent optional-XGBoost error. Result bytes 75,430→27,283; schemas 6,247→1,875;
assembly median 0.1621→0.0641 ms. Selected values/units/citations preserved;
canonical context slightly grew. No token/billing savings inferred. No new live
calls; prior local live server stopped after preserving the response. Changed
version needs new authorization for live verification. Details/corrections and
remaining hosted-demo/human/prompt-injection work:
`docs/results/assistant-v1/dashboard-offline-review.md`; local preserved artifacts
and measurements: `reports/local/assistant/review-2d7ed00c/`.

Assistant workflow contracts/lifecycle: `docs/assistant.md`. Historical assistant
verification/CI and hybrid/telemetry limitations are in
`docs/results/assistant-v1/report.md`. Hybrid quality and independent human review
remain unverified; no model download or paid evaluation is implied by these notes.

Scientific next step remains readiness review, not B03 evaluation:
freeze method/preprocessing/eligibility/metrics, compare reviewed implementation
and artifact hashes with the existing plan, independently review measurement
meaning before signals/outcomes, then obtain separate authorization for one
evaluation against persistence with unfavorable outcomes retained. Never update
the plan simply to bypass mismatches.

After a material change, update only affected facts/pointers/checks here; keep
this file around 1,500 words or less. Put detailed decisions in docs/ and Git.
Run context update after source/config/memory changes; freshness uses content
hashes rather than commit/date alone. A stale graph is not proof of behavior.
