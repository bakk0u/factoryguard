# FactoryGuard project memory

Verified 2026-11-07 (Europe/Berlin). This is orientation, not a source of new
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

- Integration base: master `589f50297b32af9b3e4b7baee66462b5c67227f0`, fetched
  2026-11-07; includes visual README (`8723456`) and merged documentation PRs #2/#3.
  Memory integration branch: `graphify-project-memory`. Check `git status -sb`
  and `git log -5 --oneline`; do not assume branch names imply current remote state.
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
| Streaming loading / burst features | `src/factoryguard/data/paderborn.py`, `features/b01.py`, `pipelines/features_paderborn.py` |
| Frozen campaign / causal features / audit | `release/campaign.py`, `release/modeling.py`, `release/reporting.py`, `models/selection.py` |
| Scientific definitions / qualifications | `docs/feature_definitions.md`, `development_assessment.md`, `release_protocol.md`, `model_card.md` |
| Full saved comparisons / architecture | `docs/results/release-v3/`, `docs/architecture.md` (legacy inventories are historical) |
| Future reserve gate | `docs/b03_readiness.md`, `docs/review_handoff.md`, `configs/reserve_plan.json`, `release/holdout.py` (do not execute) |

Paths abbreviated as `release/...` are under `src/factoryguard/`; doc names after
`docs/...` stay in docs/. `docs/project_status.md` has a current entry followed by
a long historical log; read only relevant milestones. Source overrides stale prose.

## Session and verification commands

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
No semantic API key, cloud, MCP server, or hooks that rebuild on Git operations.

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

Current task is optional persistent context integration only. No new application
feature is implied. Scientific next step is readiness review, not B03 evaluation:
freeze method/preprocessing/eligibility/metrics, compare reviewed implementation
and artifact hashes with the existing plan, independently review measurement
meaning before signals/outcomes, then obtain separate authorization for one
evaluation against persistence with unfavorable outcomes retained. Never update
the plan simply to bypass mismatches.

After a material change, update only affected facts/pointers/checks here; keep
this file around 1,500 words or less. Put detailed decisions in docs/ and Git.
Run context update after source/config/memory changes; freshness uses content
hashes rather than commit/date alone. A stale graph is not proof of behavior.
