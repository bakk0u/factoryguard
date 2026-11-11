# FactoryGuard project memory

Verified 2026-11-11 (Europe/Berlin). This is orientation, not a source of new
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

- CI-fix work uses local `fix/pr8-ci`, based on PR #8's published head
  `754cf5d2f9e77479bd162ff9fd52d75e71853b88`. Original local checkpoint
  `1db617777c17ebc05185a9cc6db757cad8195035` remains on
  `feature/investigation-alerts-v1`; publication through the GitHub integration
  changed commit metadata, not its tree. PR #8 targets master. Current user
  authorization permits CI fixes and updates to that PR, not merge/deployment,
  paid requests, forecasting changes or B03 access. Preserve unrelated work.
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
- Earlier remote/public checks are historical. Current local checks below do not
  imply new CI, hosted verification or a live-model quality evaluation. Detailed
  release history is in Git and `docs/project_status.md`.

## Locate only the relevant components

| Question | Entry points / source of truth |
| --- | --- |
| CLI, local demo, export/API | `src/factoryguard/release/__main__.py`, `application.py` |
| Atomic SQLite replay, resets, notes | `src/factoryguard/release/store.py` (`Store`) |
| Reference bins / notices / sustained windows | `release/context.py`, `release/investigation.py` |
| Portable UI and reviewer-only controls | `release/dashboard.html`, `site/reviewer.js` |
| Static build, snapshot integrity | `scripts/build_reviewer_site.py`, `site/source-manifest.json` |
| Deterministic alerts / journal / evaluation | `src/factoryguard/alerts/{engine_v2,journal,evaluate_v2}.py` (v1 modules preserved), `configs/investigation_alerts_v2*.json`, `docs/investigation_alert_protocol_v2.md`, `site/alerts.js` |
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

Before each new prompt run status and the baseline query below. After material
changes run update. Missing/stale tools must be reported; no invented graph edges.
Start Codex from this root; AGENTS directs memory/bootstrap, not an automatic hook.

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

Windows: `.venv\Scripts\python.exe`. Match checks to risk; do not repeat the full
suite for docs-only changes. Browser checks need Playwright/Chrome; use fresh output
directories. Reproducibility: `docs/development_release.md`.

## Next work and maintenance

PR #8 CI follow-up (2026-11-11): development jobs installed only campaign/core
packages then discovered an optional Pydantic-dependent test; add existing locked
assistant dependencies for the full test phase, after core build/browser checks.
Runtime requirements remain optional. Strengthened isolation test blocks Pydantic,
MCP and embedding imports while running the demo and alert-enabled static build.
Windows real MCP calls timed out; child environments now explicitly bound numerical
threads and UTF-8, with fixed-code initialize/discovery/tool timeout diagnostics.
API tests wait for terminal state within the unchanged request deadline; all
assertions and real MCP coverage remain. Updated Windows logs isolated timeouts
to tool responses after ~1s discovery. Keep buffered stdout beneath SDK UTF-8 wrapping; child-buffering and large
Unicode regressions pass, including Windows, but did not resolve real evidence
call timeouts. Production stderr was piped but unread; consume/discard it to
prevent backpressure without logging raw diagnostics. A negative SDK reproducer
blocks without a consumer; the positive Unicode regression now forces >400 KB
of synthetic stderr before its response. Runtime timeout bounds stay unchanged. Windows still timed out after those
transport fixes; a test-only scoped preflight emits sanitized Python stack
locations (no raw diagnostics/locals/env) to identify the actual blocking call. First CI fix made all development jobs green but
did not by itself resolve Windows tool calls; original failed runs retained. Local 180 Python / 47 TS / 40 frozen
retrieval cases and build pass, no skips. Actual OS CI status is on PR #8 checks;
final job records: `reports/local/pr8-ci/`. Source details:
`docs/results/investigation-alerts-v2/ci-followup.md`. No frozen policy/result edits.

Investigation alerts v2 final checkpoint (2026-11-10): pure deterministic Python,
no LLM/key for detection. One frozen candidate, unchanged v1 thresholds/calibration,
no search or outcome tuning. Counted level confirmations and recovery require
three disjoint scoring windows; residual/context use distinct current observations.
Shared anchors/references and serial measurements are not independent evidence.
Isolated level-window echoes cannot activate alone; level decisions are delayed
four observations relative to earliest v1 activation. Raw trailing means unchanged.

Signals retain separate eligibility/reasons, score/threshold/units and provenance.
Availability is full/limited/unavailable (internal full enum remains `available`).
Condition Watch/Active/Cleared is separate from current supported/unresolved-
unavailable/hysteresis/recovery-pending assessment. Additional persistent signals
escalate evidence scope without another activation notification. Acknowledgment is
not clearance. SQLite journal and portable browser-local acknowledgment stay
separate; cursor-scoped exports/citations, queue/investigate and notes still work.

A synthetic regression found reset reanchoring could clear an unchanged elevated
level. Fixed against the frozen no-adaptation requirement: retain active level
anchor/bin across history reset and subsequent recovery. Failed regression and
first v2 evaluation retained; one separate correctness recheck, no threshold or
policy-file change. All eight cells keep identical calibration, episode counts
and active durations before/after this fix; some assessment details changed.
V1 engine/config/protocol/report and both evaluations remain byte-identical.
See `docs/results/investigation-alerts-v2/report.md`; local logs/evaluations and
final screenshots: `reports/local/alerts-v2/` (`final-browser/`).

Final **180 Python / 44 TS / 40 frozen lexical cases**, TS build/site builds and
four Chrome workflows pass, zero skips. Legacy browser launcher initially lacked
`python`; explicit URL argument works. No stalls/retry loops/paid calls. One local
checkpoint commit includes previously uncommitted v1 prerequisites and final v2;
Git HEAD and local completion record identify it. All artifacts remain local.
Graph1158nodes/3119edges before final documentation refresh. Existing services
left untouched; dedicated offline test service on8788 stopped after checks.
Reproduce: `env -u OPENAI_API_KEY FACTORYGUARD_ASSISTANT_PORT=8788 .venv/bin/python scripts/start_assistant.py`.

B01 prefix1–150, validation151–263, reserved264–377; B02 prefix1–446,
validation447–781, reserved782–1116, unchanged inspected development diagnostics.
No fully available evaluation rows: B01 context unsupported, B02 context partial;
long active episodes remain. No normal/fault event intervals/onset exist. Precision,
recall, false alarms and delay remain null, durations observations not hours.
B04 remains unavailable diagnostic; B03 completely sealed. Prototype complete
within scope, not validated fault alarms or production. Independent human,
real-model quality/prompt-injection and restricted-hosting evaluations unverified.

Layout3 source remains `release/dashboard.html` + `site/reviewer.js`,
`site/reviewer_experience.js`, `site/reviewer.css`, `site/layout3.css` and
`site/architecture.js` (now15 interactive nodes). Start here, deterministic B01/A
1–3 guidance, desktop parallel measurements/assistant, mobile order, citations,
notes/report/queue remain. Suggestions/diagram/investigate never auto-submit.
Canonical builder inlines source; static mode is useful without a backend/key.
Prior redesign: `docs/results/assistant-v1/layout3.md`, captures
`reports/local/layout3/`; final alert screenshots are separate and do not replace it.

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
is off. Historical live checks in `docs/assistant.md` do not validate changed versions or
authorize another paid request.

Historical dashboard response/trace `2d7ed00c-f795-4afe-a177-83fbfb7d5284` is
preserved under `reports/local/assistant/review-2d7ed00c/`. Audit found correct
quoted numbers but qualified trend/causal wording and an off-channel projection
bug, fixed afterward. That live response does not validate changed alert code.

Offline optimization history, measurements, corrections and remaining human/
prompt-injection/hosting work: `docs/results/assistant-v1/dashboard-offline-review.md`;
original artifacts: `reports/local/assistant/review-2d7ed00c/`. No evidence cache,
pooled MCP or parallel retrieval was added. New versions need separate explicit
live authorization; prior historical model results do not validate changed code.

Assistant workflow contracts/lifecycle: `docs/assistant.md`. Historical assistant
verification/CI and hybrid/telemetry limitations are in
`docs/results/assistant-v1/report.md`. Hybrid quality and independent human review
remain unverified; no model download or paid evaluation is implied by these notes.

B03 remains sealed; the existing readiness plan is not changed by alert work.
No further implementation/evaluation campaign is authorized by this checkpoint.

After a material change, update only affected facts/pointers/checks here; keep
this file around 1,500 words or less. Put detailed decisions in docs/ and Git.
Run context update after source/config/memory changes; freshness uses content
hashes rather than commit/date alone. A stale graph is not proof of behavior.
