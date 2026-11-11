# Graph Report - factoryguard  (2026-11-11)

## Corpus Check
- cluster-only mode — file stats not available

## Summary
- 1165 nodes · 3124 edges · 77 communities (39 shown, 38 thin omitted)
- Extraction: 95% EXTRACTED · 5% INFERRED · 0% AMBIGUOUS · INFERRED: 164 edges (avg confidence: 0.86)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `5082e443`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- alerts/evaluate.py
- acquire_selected_paderborn.py
- models/forecast.py
- test_selection.py
- AlertV2Tests
- Store
- json
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
- guard_run
- protect_output
- prepare.py
- dependencies
- ProjectContextTests
- package.json
- EvidenceService
- provider.ts
- env
- test_assistant_evidence.py
- assess_development.py
- README.md
- create_server
- contracts.ts
- compilerOptions
- orchestrator.ts
- protect_output
- clean
- mcp.ts
- AssistantEvidenceTests
- pathlib
- inspect_paderborn.py
- optimization.test.ts
- adversarial.test.ts
- AlertEngine
- build
- math
- reviewer_experience.js
- numpy
- DocumentationWorkflowTests
- AlertJournal
- mountInvestigationAlerts
- pipeline.test.ts
- unittest_mock
- Selection
- test_release_campaign.py
- SelectedAcquisitionTests
- build_reviewer_site.py
- SyntheticAssistantAdversarialTests

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
- `ForecastTests` --uses--> `Replay`  [INFERRED]
  tests/test_forecasting.py → src/factoryguard/models/forecast.py
- `ForecastTests` --uses--> `Session`  [INFERRED]
  tests/test_forecasting.py → src/factoryguard/monitoring/dashboard.py
- `AlertTests` --uses--> `Store`  [INFERRED]
  tests/test_alerts.py → src/factoryguard/release/store.py

## Import Cycles
- None detected.

## Communities (77 total, 38 thin omitted)

### Community 0 - "alerts/evaluate.py"
Cohesion: 0.17
Nodes (12): AlertEngine, canonical(), channel_value(), fingerprint(), finite(), load_policy(), Policy, replay() (+4 more)

### Community 1 - "acquire_selected_paderborn.py"
Cohesion: 0.09
Nodes (28): Authorized bounded selection milestone, Authorized forecasting prototype, Claims and next milestone, Current development release authorization, Data integrity and leakage prevention, Development and verification, graphify, Persistent context bootstrap (+20 more)

### Community 2 - "models/forecast.py"
Cohesion: 0.20
Nodes (7): evaluate(), _metric(), replay_frame(), validate_frame(), config(), ForecastTests, frame()

### Community 3 - "test_selection.py"
Cohesion: 0.15
Nodes (10): candidates(), FiniteGate, fit_candidate(), predict(), prepare(), splits(), candidate(), config() (+2 more)

### Community 4 - "AlertV2Tests"
Cohesion: 0.16
Nodes (5): LocalNotifications, AlertV2Tests, disjoint(), policy(), ready()

### Community 5 - "Store"
Cohesion: 0.10
Nodes (18): FactoryGuard project memory, Locate only the relevant components, Next work and maintenance, Purpose and hard boundaries, Session and verification commands, Verified state and evidence, export(), notices() (+10 more)

### Community 6 - "json"
Cohesion: 0.17
Nodes (12): build_html(), main(), main(), fit(), load_artifact(), validate_artifact(), validate_config(), write_json() (+4 more)

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

### Community 14 - "channel_features"
Cohesion: 0.18
Nodes (3): channel_features(), ChannelFeatures, ChannelFeatureTests

### Community 15 - "reviewer.js"
Cohesion: 0.23
Nodes (8): enhance(), friendly(), invalidateChangedPeriod(), investigationReport(), periodIdentity(), referenceIdentifiers(), view(), volatileNotes

### Community 26 - "event"
Cohesion: 0.25
Nodes (6): activate(), AlertTests, calibration(), event(), policy(), ready()

### Community 31 - "features_paderborn.py"
Cohesion: 0.20
Nodes (6): feature_schema(), plot_comparisons(), burst_rows(), extract_b01(), main(), peak_rss_mib()

### Community 32 - "guard_run"
Cohesion: 0.20
Nodes (5): guard_run(), issue(), number(), Replay, Session

### Community 33 - "protect_output"
Cohesion: 0.21
Nodes (8): load_policy(), Policy, replay(), dashboard_bundle(), evaluate(), load_snapshot(), metrics(), protect_output()

### Community 35 - "dependencies"
Cohesion: 0.33
Nodes (6): dependencies, fastify@5.12.8, @modelcontextprotocol/sdk@1.32.2, zod@4.6.7, fastify, zod

### Community 37 - "package.json"
Cohesion: 0.12
Nodes (18): devDependencies, tsx@4.23.15, @types/node@26.6.6, typescript@7.0.2, engines, node, name, private (+10 more)

### Community 39 - "provider.ts"
Cohesion: 0.11
Nodes (22): openai@7.53.0, providerContext(), Answer, ContextPackage, ANSWER_JSON_SCHEMA, ProviderDiagnostic, providerDiagnostic(), ProviderFailure (+14 more)

### Community 40 - "env"
Cohesion: 0.08
Nodes (25): env, runs-on, steps, strategy, FACTORYGUARD_PYTHON, MPLBACKEND, OMP_NUM_THREADS, OPENBLAS_NUM_THREADS (+17 more)

### Community 42 - "assess_development.py"
Cohesion: 0.17
Nodes (7): condition_groups(), assess_table(), combined_load_check(), cross_support(), main(), plot_history(), raw_storage_root()

### Community 43 - "README.md"
Cohesion: 0.25
Nodes (6): Explore the dashboard, From a change to an investigation, Results & evidence, Run it your way, Technical reading, Attributed derived demonstration

### Community 45 - "contracts.ts"
Cohesion: 0.10
Nodes (21): assembleContext(), priority(), alertData, alertSignal, answerSchema, claim, envelopeSchema, errorSummary (+13 more)

### Community 46 - "compilerOptions"
Cohesion: 0.20
Nodes (9): compilerOptions, module, moduleResolution, outDir, rootDir, skipLibCheck, strict, target (+1 more)

### Community 47 - "orchestrator.ts"
Cohesion: 0.33
Nodes (8): validateCitations(), Activity, Dependencies, investigate(), call(), InvestigationFailure, publicActivity(), createApp()

### Community 48 - "protect_output"
Cohesion: 0.19
Nodes (3): sha(), atomic_json(), run_workflow()

### Community 51 - "clean"
Cohesion: 0.19
Nodes (6): clean(), make_server(), do_GET(), do_POST(), respond(), html()

### Community 52 - "mcp.ts"
Cohesion: 0.08
Nodes (17): assert, {chromium}, fs, path, assert, {chromium}, fs, path (+9 more)

### Community 57 - "inspect_paderborn.py"
Cohesion: 0.23
Nodes (5): _label(), inspect_b01(), main(), _plot_excerpts(), _plot_overview()

### Community 58 - "optimization.test.ts"
Cohesion: 0.12
Nodes (5): waitForInvestigation(), envelope, request, Stream, sandbox

### Community 59 - "adversarial.test.ts"
Cohesion: 0.18
Nodes (5): requestSchema, TOOL_NAMES, EvidenceClient, base, snapshot

### Community 60 - "AlertEngine"
Cohesion: 0.23
Nodes (5): AlertEngine, canonical(), channel_value(), fingerprint(), finite()

### Community 61 - "build"
Cohesion: 0.24
Nodes (7): build(), events_from_ledger(), export(), main(), serve(), records(), SelectionDashboardTests

### Community 62 - "math"
Cohesion: 0.44
Nodes (7): bearing(), circle(), hero(), rect(), shell(), text(), workflow()

### Community 65 - "numpy"
Cohesion: 0.05
Nodes (62): main(), generate(), main(), main(), markdown_table(), report(), condition_key(), digest() (+54 more)

### Community 66 - "DocumentationWorkflowTests"
Cohesion: 0.17
Nodes (5): DocumentationIndex, passages(), search_tokens(), tokens(), DocumentationWorkflowTests

### Community 69 - "pipeline.test.ts"
Cohesion: 0.18
Nodes (16): loadLocalConfig(), LOCAL_NAMES, REPOSITORY_ROOT, requireLiveCredentials(), withoutCredentials(), manifest, connectEvidence(), drainEvidenceStderr() (+8 more)

## Knowledge Gaps
- **1 isolated node(s):** `factoryguard`
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 417 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **38 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `event()` connect `event` to `AlertV2Tests`, `test_alerts.py`?**
  _High betweenness centrality (0.022) - this node is a cross-community bridge._
- **What connects `factoryguard` to the rest of the system?**
  _1 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `acquire_selected_paderborn.py` be split into smaller, more focused modules?**
  _Cohesion score 0.08773784355179703 - nodes in this community are weakly interconnected._
- **Why does `AlertEngine` connect `AlertEngine` to `protect_output`, `event`?**
  _High betweenness centrality (0.021) - this node is a cross-community bridge._
- **Should `test_selection.py` be split into smaller, more focused modules?**
  _Cohesion score 0.14962121212121213 - nodes in this community are weakly interconnected._
- **Why does `Store` connect `Store` to `numpy`, `event`, `pathlib`?**
  _High betweenness centrality (0.020) - this node is a cross-community bridge._
- **Should `Store` be split into smaller, more focused modules?**
  _Cohesion score 0.10204081632653061 - nodes in this community are weakly interconnected._