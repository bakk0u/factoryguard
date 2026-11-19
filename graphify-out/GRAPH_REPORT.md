# Graph Report - factoryguard  (2026-11-19)

## Corpus Check
- cluster-only mode — file stats not available

## Summary
- 1280 nodes · 3425 edges · 67 communities (34 shown, 33 thin omitted)
- Extraction: 94% EXTRACTED · 6% INFERRED · 0% AMBIGUOUS · INFERRED: 197 edges (avg confidence: 0.86)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `8fd62933`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- event
- json
- models/forecast.py
- prepare
- engine_v2.py
- Store
- b01_plots.py
- raw_manifest
- ref_playwright
- with
- publish
- PaderbornTests
- manifest.json
- ValidationTests
- selection_report.py
- reviewer.js
- ArchiveTests
- inspect_paderborn.py
- factoryguard
- FeaturePipelineTests
- ReviewerOutputGuardTests
- channel_features
- IntervalCalibrationTests
- test_forecast_uncertainty_audit.py
- SpeedEvidenceTests
- features_paderborn.py
- ProjectContextTests
- package.json
- assess_development.py
- provider.ts
- steps
- evidence.py
- dependencies
- README.md
- EvidenceService
- contracts.ts
- compilerOptions
- orchestrator.ts
- protect_output
- start_assistant.py
- ref_node_fs
- unittest
- hashlib
- optimization.test.ts
- adversarial.test.ts
- ReviewerSiteTests
- math
- reviewer_experience.js
- numpy
- mountInvestigationAlerts
- pipeline.test.ts
- test_offline_dashboard.py
- pathlib
- SelectedAcquisitionTests

## God Nodes (most connected - your core abstractions)
1. `run()` - 32 edges
2. `Store` - 31 edges
3. `clean()` - 31 edges
4. `event()` - 30 edges
5. `EvidenceService` - 28 edges
6. `run()` - 28 edges
7. `load_table()` - 27 edges
8. `data()` - 26 edges
9. `digest()` - 25 edges
10. `AlertTests` - 24 edges

## Surprising Connections (you probably didn't know these)
- `Locate only the relevant components` --references--> `Store`  [INFERRED]
  PROJECT_MEMORY.md → src/factoryguard/release/store.py
- `Persistent context bootstrap` --references--> `graphify()`  [INFERRED]
  AGENTS.md → scripts/project_context.py
- `build()` --uses--> `AlertJournal`  [INFERRED]
  scripts/build_reviewer_site.py → src/factoryguard/alerts/journal.py
- `AlertTests` --uses--> `Store`  [INFERRED]
  tests/test_alerts.py → src/factoryguard/release/store.py
- `ready()` --uses--> `AlertEngine`  [INFERRED]
  tests/test_alerts_v2.py → src/factoryguard/alerts/engine_v2.py

## Import Cycles
- None detected.

## Communities (67 total, 33 thin omitted)

### Community 0 - "event"
Cohesion: 0.07
Nodes (23): AlertEngine, channel_value(), fingerprint(), finite(), load_policy(), Policy, replay(), dashboard_bundle() (+15 more)

### Community 1 - "json"
Cohesion: 0.05
Nodes (43): Authorized bounded selection milestone, Authorized forecasting prototype, Claims and next milestone, Current development release authorization, Data integrity and leakage prevention, Development and verification, graphify, Persistent context bootstrap (+35 more)

### Community 2 - "models/forecast.py"
Cohesion: 0.07
Nodes (21): evaluate(), guard_run(), Replay, replay_frame(), make_server(), do_GET(), do_POST(), respond() (+13 more)

### Community 3 - "prepare"
Cohesion: 0.14
Nodes (10): candidates(), FiniteGate, fit_candidate(), predict(), prepare(), splits(), candidate(), config() (+2 more)

### Community 4 - "engine_v2.py"
Cohesion: 0.14
Nodes (12): AlertEngine, canonical(), channel_value(), fingerprint(), finite(), load_policy(), Policy, replay() (+4 more)

### Community 5 - "Store"
Cohesion: 0.09
Nodes (24): Current merged checkpoint — 2026-11-12, FactoryGuard project memory, Locate only the relevant components, Next work and maintenance, Proposed follow-up — 2026-11-13, Purpose and hard boundaries, Replay consistency checks, 19 November 2026, Session and verification commands (+16 more)

### Community 6 - "b01_plots.py"
Cohesion: 0.19
Nodes (4): condition_groups(), _label(), plot_comparisons(), cross_support()

### Community 7 - "raw_manifest"
Cohesion: 0.23
Nodes (3): burst_rows(), raw_manifest(), DevelopmentAssessmentTests

### Community 8 - "ref_playwright"
Cohesion: 0.13
Nodes (11): assert, { chromium }, fs, {chromium}, fs, {chromium}, fs, {chromium} (+3 more)

### Community 9 - "with"
Cohesion: 0.07
Nodes (26): MPLBACKEND, OMP_NUM_THREADS, OPENBLAS_NUM_THREADS, PYTHONUTF8, jobs, test, os, name (+18 more)

### Community 10 - "publish"
Cohesion: 0.08
Nodes (24): description, required, type, authorization, jobs, publish, name, on (+16 more)

### Community 12 - "manifest.json"
Cohesion: 0.12
Nodes (16): artifact_sha256, B03_accessed, changes, citation, creator, derived_csv_sha256, doi, evaluation (+8 more)

### Community 13 - "ValidationTests"
Cohesion: 0.12
Nodes (3): main(), run_step1(), ValidationTests

### Community 15 - "reviewer.js"
Cohesion: 0.23
Nodes (8): enhance(), friendly(), invalidateChangedPeriod(), investigationReport(), periodIdentity(), referenceIdentifiers(), view(), volatileNotes

### Community 17 - "inspect_paderborn.py"
Cohesion: 0.18
Nodes (6): plot_readings(), inspect_b01(), main(), _plot_excerpts(), _plot_overview(), peak_rss_mib()

### Community 35 - "features_paderborn.py"
Cohesion: 0.25
Nodes (4): ChannelFeatures, feature_schema(), extract_b01(), main()

### Community 37 - "package.json"
Cohesion: 0.12
Nodes (18): devDependencies, tsx@4.23.15, @types/node@26.6.6, typescript@7.0.2, engines, node, name, private (+10 more)

### Community 38 - "assess_development.py"
Cohesion: 0.25
Nodes (5): assess_table(), combined_load_check(), main(), plot_cross(), plot_history()

### Community 39 - "provider.ts"
Cohesion: 0.13
Nodes (18): openai@7.53.0, Answer, ContextPackage, ANSWER_JSON_SCHEMA, ProviderDiagnostic, providerDiagnostic(), ProviderFailure, redact() (+10 more)

### Community 40 - "steps"
Cohesion: 0.07
Nodes (28): continue-on-error, env, runs-on, steps, strategy, FACTORYGUARD_PYTHON, MPLBACKEND, OMP_NUM_THREADS (+20 more)

### Community 41 - "evidence.py"
Cohesion: 0.14
Nodes (6): build_html(), main(), canonical(), search_tokens(), tokens(), OptionalIsolationTests

### Community 42 - "dependencies"
Cohesion: 0.33
Nodes (6): dependencies, fastify@5.12.8, @modelcontextprotocol/sdk@1.32.2, zod@4.6.7, fastify, zod

### Community 43 - "README.md"
Cohesion: 0.22
Nodes (7): Explore the dashboard, From a change to an investigation, Project status · v0.5.0, Results & evidence, Run it your way, Technical reading, Attributed derived demonstration

### Community 44 - "EvidenceService"
Cohesion: 0.05
Nodes (17): disable(), enable(), flush(), write(), mark(), evaluate(), EvidenceService, Selection (+9 more)

### Community 45 - "contracts.ts"
Cohesion: 0.10
Nodes (22): assembleContext(), priority(), providerContext(), alertData, alertSignal, answerSchema, claim, envelopeSchema (+14 more)

### Community 46 - "compilerOptions"
Cohesion: 0.20
Nodes (9): compilerOptions, module, moduleResolution, outDir, rootDir, skipLibCheck, strict, target (+1 more)

### Community 47 - "orchestrator.ts"
Cohesion: 0.31
Nodes (9): validateCitations(), Activity, Dependencies, investigate(), call(), InvestigationFailure, publicActivity(), OfflineFixtureProvider (+1 more)

### Community 48 - "protect_output"
Cohesion: 0.23
Nodes (4): sha(), atomic_json(), protect_output(), raw_storage_root()

### Community 52 - "ref_node_fs"
Cohesion: 0.08
Nodes (17): assert, {chromium}, fs, path, assert, {chromium}, fs, path (+9 more)

### Community 58 - "optimization.test.ts"
Cohesion: 0.11
Nodes (7): waitForInvestigation(), envelope, next(), request, Stream, sandbox, next()

### Community 59 - "adversarial.test.ts"
Cohesion: 0.18
Nodes (5): requestSchema, TOOL_NAMES, EvidenceClient, base, snapshot

### Community 62 - "math"
Cohesion: 0.11
Nodes (19): audit_payload(), audit_run(), errors(), finite_number(), main(), render(), bearing(), circle() (+11 more)

### Community 65 - "numpy"
Cohesion: 0.05
Nodes (71): generate(), main(), main(), main(), clean(), condition_key(), digest(), fit() (+63 more)

### Community 69 - "pipeline.test.ts"
Cohesion: 0.16
Nodes (19): loadLocalConfig(), LOCAL_NAMES, REPOSITORY_ROOT, requireLiveCredentials(), withoutCredentials(), manifest, connectEvidence(), drainEvidenceStderr() (+11 more)

## Knowledge Gaps
- **1 isolated node(s):** `factoryguard`
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 459 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **33 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `ValidationTests` connect `ValidationTests` to `hashlib`?**
  _High betweenness centrality (0.028) - this node is a cross-community bridge._
- **What connects `factoryguard` to the rest of the system?**
  _1 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `event` be split into smaller, more focused modules?**
  _Cohesion score 0.06569133677567413 - nodes in this community are weakly interconnected._
- **Why does `channel_features()` connect `channel_features` to `numpy`, `features_paderborn.py`, `raw_manifest`?**
  _High betweenness centrality (0.024) - this node is a cross-community bridge._
- **Should `json` be split into smaller, more focused modules?**
  _Cohesion score 0.053208137715179966 - nodes in this community are weakly interconnected._
- **Should `models/forecast.py` be split into smaller, more focused modules?**
  _Cohesion score 0.07247223845704266 - nodes in this community are weakly interconnected._
- **Should `prepare` be split into smaller, more focused modules?**
  _Cohesion score 0.1411764705882353 - nodes in this community are weakly interconnected._