# Graph Report - factoryguard  (2026-11-11)

## Corpus Check
- cluster-only mode — file stats not available

## Summary
- 1183 nodes · 3172 edges · 72 communities (37 shown, 35 thin omitted)
- Extraction: 95% EXTRACTED · 5% INFERRED · 0% AMBIGUOUS · INFERRED: 167 edges (avg confidence: 0.86)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `4d2f4616`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- alerts/evaluate.py
- acquire_selected_paderborn.py
- ForecastTests
- test_selection.py
- engine_v2.py
- Store
- b01_plots.py
- DevelopmentAssessmentTests
- ref_playwright
- with
- publish
- PaderbornTests
- manifest.json
- ValidationTests
- channel_features
- reviewer.js
- ArchiveTests
- factoryguard
- event
- FeaturePipelineTests
- features_paderborn.py
- AlertV2Tests
- AlertEngine
- dependencies
- ProjectContextTests
- package.json
- EvidenceService
- provider.ts
- env
- test_assistant_evidence.py
- assess_development.py
- README.md
- mcp_server.py
- contracts.ts
- compilerOptions
- orchestrator.ts
- evidence.py
- test_assistant_config.py
- mcp.ts
- AssistantEvidenceTests
- unittest
- pathlib
- inspect_paderborn.py
- optimization.test.ts
- adversarial.test.ts
- ReviewerSiteTests
- math
- reviewer_experience.js
- numpy
- DocumentationIndex
- mountInvestigationAlerts
- pipeline.test.ts
- OfflineDashboardTests
- Selection
- build_reviewer_site.py
- SelectedAcquisitionTests

## God Nodes (most connected - your core abstractions)
1. `run()` - 32 edges
2. `Store` - 31 edges
3. `clean()` - 31 edges
4. `event()` - 30 edges
5. `run()` - 28 edges
6. `data()` - 26 edges
7. `digest()` - 26 edges
8. `load_table()` - 26 edges
9. `EvidenceService` - 25 edges
10. `execute()` - 24 edges

## Surprising Connections (you probably didn't know these)
- `Locate only the relevant components` --references--> `Store`  [INFERRED]
  PROJECT_MEMORY.md → src/factoryguard/release/store.py
- `Persistent context bootstrap` --references--> `graphify()`  [INFERRED]
  AGENTS.md → scripts/project_context.py
- `build()` --calls--> `AlertJournal`  [INFERRED]
  scripts/build_reviewer_site.py → src/factoryguard/alerts/journal.py
- `AlertTests` --uses--> `Store`  [INFERRED]
  tests/test_alerts.py → src/factoryguard/release/store.py
- `ready()` --calls--> `AlertEngine`  [INFERRED]
  tests/test_alerts.py → src/factoryguard/alerts/engine_v2.py

## Import Cycles
- None detected.

## Communities (72 total, 35 thin omitted)

### Community 0 - "alerts/evaluate.py"
Cohesion: 0.12
Nodes (13): AlertEngine, canonical(), channel_value(), fingerprint(), finite(), load_policy(), Policy, replay() (+5 more)

### Community 1 - "acquire_selected_paderborn.py"
Cohesion: 0.06
Nodes (39): Authorized bounded selection milestone, Authorized forecasting prototype, Claims and next milestone, Current development release authorization, Data integrity and leakage prevention, Development and verification, graphify, Persistent context bootstrap (+31 more)

### Community 2 - "ForecastTests"
Cohesion: 0.10
Nodes (14): evaluate(), guard_run(), issue(), Replay, replay_frame(), make_server(), do_GET(), do_POST() (+6 more)

### Community 3 - "test_selection.py"
Cohesion: 0.15
Nodes (10): candidates(), FiniteGate, fit_candidate(), predict(), prepare(), splits(), candidate(), config() (+2 more)

### Community 4 - "engine_v2.py"
Cohesion: 0.15
Nodes (11): canonical(), channel_value(), fingerprint(), finite(), load_policy(), Policy, dashboard_bundle(), evaluate() (+3 more)

### Community 5 - "Store"
Cohesion: 0.11
Nodes (16): FactoryGuard project memory, Locate only the relevant components, Next work and maintenance, Purpose and hard boundaries, Session and verification commands, Verified state and evidence, export(), encode() (+8 more)

### Community 6 - "b01_plots.py"
Cohesion: 0.22
Nodes (4): condition_groups(), _label(), plot_comparisons(), cross_support()

### Community 7 - "DevelopmentAssessmentTests"
Cohesion: 0.21
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

### Community 26 - "event"
Cohesion: 0.25
Nodes (6): replay(), activate(), AlertTests, event(), policy(), ready()

### Community 31 - "features_paderborn.py"
Cohesion: 0.25
Nodes (4): ChannelFeatures, feature_schema(), extract_b01(), main()

### Community 32 - "AlertV2Tests"
Cohesion: 0.16
Nodes (5): LocalNotifications, AlertV2Tests, disjoint(), policy(), ready()

### Community 35 - "dependencies"
Cohesion: 0.33
Nodes (6): dependencies, fastify@5.12.8, @modelcontextprotocol/sdk@1.32.2, zod@4.6.7, fastify, zod

### Community 37 - "package.json"
Cohesion: 0.12
Nodes (18): devDependencies, tsx@4.23.15, @types/node@26.6.6, typescript@7.0.2, engines, node, name, private (+10 more)

### Community 38 - "EvidenceService"
Cohesion: 0.25
Nodes (3): evaluate(), EvidenceService, run_workflow()

### Community 39 - "provider.ts"
Cohesion: 0.13
Nodes (18): openai@7.53.0, Answer, ContextPackage, ANSWER_JSON_SCHEMA, ProviderDiagnostic, providerDiagnostic(), ProviderFailure, redact() (+10 more)

### Community 40 - "env"
Cohesion: 0.07
Nodes (28): continue-on-error, env, runs-on, steps, strategy, FACTORYGUARD_PYTHON, MPLBACKEND, OMP_NUM_THREADS (+20 more)

### Community 42 - "assess_development.py"
Cohesion: 0.29
Nodes (5): assess_table(), combined_load_check(), main(), plot_cross(), plot_history()

### Community 43 - "README.md"
Cohesion: 0.25
Nodes (6): Explore the dashboard, From a change to an investigation, Results & evidence, Run it your way, Technical reading, Attributed derived demonstration

### Community 44 - "mcp_server.py"
Cohesion: 0.13
Nodes (7): disable(), enable(), flush(), write(), mark(), create_server(), get_investigation_summary()

### Community 45 - "contracts.ts"
Cohesion: 0.10
Nodes (22): assembleContext(), priority(), providerContext(), alertData, alertSignal, answerSchema, claim, envelopeSchema (+14 more)

### Community 46 - "compilerOptions"
Cohesion: 0.20
Nodes (9): compilerOptions, module, moduleResolution, outDir, rootDir, skipLibCheck, strict, target (+1 more)

### Community 47 - "orchestrator.ts"
Cohesion: 0.31
Nodes (9): validateCitations(), Activity, Dependencies, investigate(), call(), InvestigationFailure, publicActivity(), OfflineFixtureProvider (+1 more)

### Community 48 - "evidence.py"
Cohesion: 0.16
Nodes (5): search_tokens(), tokens(), atomic_json(), protect_output(), raw_storage_root()

### Community 52 - "mcp.ts"
Cohesion: 0.08
Nodes (17): assert, {chromium}, fs, path, assert, {chromium}, fs, path (+9 more)

### Community 57 - "inspect_paderborn.py"
Cohesion: 0.18
Nodes (6): plot_readings(), inspect_b01(), main(), _plot_excerpts(), _plot_overview(), peak_rss_mib()

### Community 58 - "optimization.test.ts"
Cohesion: 0.11
Nodes (7): waitForInvestigation(), envelope, next(), request, Stream, sandbox, next()

### Community 59 - "adversarial.test.ts"
Cohesion: 0.18
Nodes (5): requestSchema, TOOL_NAMES, EvidenceClient, base, snapshot

### Community 62 - "math"
Cohesion: 0.50
Nodes (7): bearing(), circle(), hero(), rect(), shell(), text(), workflow()

### Community 65 - "numpy"
Cohesion: 0.05
Nodes (75): main(), generate(), main(), main(), main(), clean(), condition_key(), digest() (+67 more)

### Community 66 - "DocumentationIndex"
Cohesion: 0.15
Nodes (5): DocumentationIndex, passages(), sha(), SyntheticAssistantAdversarialTests, DocumentationWorkflowTests

### Community 69 - "pipeline.test.ts"
Cohesion: 0.16
Nodes (19): loadLocalConfig(), LOCAL_NAMES, REPOSITORY_ROOT, requireLiveCredentials(), withoutCredentials(), manifest, connectEvidence(), drainEvidenceStderr() (+11 more)

## Knowledge Gaps
- **1 isolated node(s):** `factoryguard`
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 424 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **35 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `AssistantEvidenceTests` connect `AssistantEvidenceTests` to `test_assistant_evidence.py`, `DocumentationIndex`?**
  _High betweenness centrality (0.027) - this node is a cross-community bridge._
- **What connects `factoryguard` to the rest of the system?**
  _1 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `alerts/evaluate.py` be split into smaller, more focused modules?**
  _Cohesion score 0.11522048364153627 - nodes in this community are weakly interconnected._
- **Why does `EvidenceService` connect `EvidenceService` to `DocumentationIndex`, `Selection`, `mcp_server.py`, `evidence.py`, `AssistantEvidenceTests`?**
  _High betweenness centrality (0.025) - this node is a cross-community bridge._
- **Should `acquire_selected_paderborn.py` be split into smaller, more focused modules?**
  _Cohesion score 0.05555555555555555 - nodes in this community are weakly interconnected._
- **Why does `PaderbornTests` connect `PaderbornTests` to `test_b01_features.py`?**
  _High betweenness centrality (0.022) - this node is a cross-community bridge._
- **Should `ForecastTests` be split into smaller, more focused modules?**
  _Cohesion score 0.09528214616096208 - nodes in this community are weakly interconnected._