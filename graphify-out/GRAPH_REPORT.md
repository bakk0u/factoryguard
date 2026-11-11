# Graph Report - factoryguard  (2026-11-11)

## Corpus Check
- cluster-only mode — file stats not available

## Summary
- 1163 nodes · 3121 edges · 75 communities (39 shown, 36 thin omitted)
- Extraction: 95% EXTRACTED · 5% INFERRED · 0% AMBIGUOUS · INFERRED: 164 edges (avg confidence: 0.86)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `8c88bce6`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- alerts/evaluate.py
- acquire_selected_paderborn.py
- models/forecast.py
- test_selection.py
- retrieval.py
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
- argparse
- numpy
- campaign.py
- prepare.py
- pipeline.test.ts
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
- application.py
- mcp.ts
- AssistantEvidenceTests
- unittest
- pathlib
- inspect_paderborn.py
- optimization.test.ts
- adversarial.test.ts
- features_paderborn.py
- build
- b01_plots.py
- reviewer_experience.js
- selection.py
- DocumentationWorkflowTests
- mountInvestigationAlerts
- pipeline.test.ts
- test_assistant_config.py
- OfflineDashboardTests
- ReviewerSiteTests
- SelectedAcquisitionTests

## God Nodes (most connected - your core abstractions)
1. `run()` - 32 edges
2. `Store` - 31 edges
3. `clean()` - 31 edges
4. `event()` - 30 edges
5. `run()` - 28 edges
6. `digest()` - 26 edges
7. `data()` - 26 edges
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
- `fingerprint()` --calls--> `sha256()`  [INFERRED]
  src/factoryguard/alerts/engine.py → scripts/acquire_selected_paderborn.py

## Import Cycles
- None detected.

## Communities (75 total, 36 thin omitted)

### Community 0 - "alerts/evaluate.py"
Cohesion: 0.12
Nodes (13): AlertEngine, canonical(), channel_value(), fingerprint(), finite(), load_policy(), Policy, replay() (+5 more)

### Community 1 - "acquire_selected_paderborn.py"
Cohesion: 0.07
Nodes (35): Authorized bounded selection milestone, Authorized forecasting prototype, Claims and next milestone, Current development release authorization, Data integrity and leakage prevention, Development and verification, graphify, Persistent context bootstrap (+27 more)

### Community 2 - "models/forecast.py"
Cohesion: 0.15
Nodes (8): evaluate(), _metric(), Replay, replay_frame(), Session, config(), ForecastTests, frame()

### Community 3 - "test_selection.py"
Cohesion: 0.15
Nodes (10): candidates(), FiniteGate, fit_candidate(), predict(), prepare(), splits(), candidate(), config() (+2 more)

### Community 4 - "retrieval.py"
Cohesion: 0.33
Nodes (4): build_html(), main(), search_tokens(), tokens()

### Community 5 - "Store"
Cohesion: 0.11
Nodes (16): FactoryGuard project memory, Locate only the relevant components, Next work and maintenance, Purpose and hard boundaries, Session and verification commands, Verified state and evidence, export(), encode() (+8 more)

### Community 6 - "json"
Cohesion: 0.12
Nodes (19): main(), main(), fit(), guard_run(), load_artifact(), load_table(), validate_artifact(), validate_config() (+11 more)

### Community 7 - "DevelopmentAssessmentTests"
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

### Community 26 - "event"
Cohesion: 0.07
Nodes (23): AlertEngine, canonical(), channel_value(), fingerprint(), finite(), load_policy(), Policy, replay() (+15 more)

### Community 31 - "argparse"
Cohesion: 0.13
Nodes (17): main(), bundle(), main(), digest(), extract_b01(), main(), fresh(), read() (+9 more)

### Community 32 - "numpy"
Cohesion: 0.12
Nodes (10): generate(), markdown_table(), report(), condition_key(), issue(), number(), compare(), notices() (+2 more)

### Community 33 - "campaign.py"
Cohesion: 0.18
Nodes (15): choose_inner(), score(), select_method(), coverage(), ledger(), main(), run(), source_support() (+7 more)

### Community 35 - "pipeline.test.ts"
Cohesion: 0.17
Nodes (10): dependencies, fastify@5.12.8, @modelcontextprotocol/sdk@1.32.2, zod@4.6.7, waitForInvestigation(), base, fixture, request (+2 more)

### Community 37 - "package.json"
Cohesion: 0.12
Nodes (18): devDependencies, tsx@4.23.15, @types/node@26.6.6, typescript@7.0.2, engines, node, name, private (+10 more)

### Community 39 - "provider.ts"
Cohesion: 0.11
Nodes (22): openai@7.53.0, providerContext(), Answer, ContextPackage, ANSWER_JSON_SCHEMA, ProviderDiagnostic, providerDiagnostic(), ProviderFailure (+14 more)

### Community 40 - "env"
Cohesion: 0.08
Nodes (23): env, runs-on, steps, strategy, FACTORYGUARD_PYTHON, MPLBACKEND, OMP_NUM_THREADS, OPENBLAS_NUM_THREADS (+15 more)

### Community 42 - "assess_development.py"
Cohesion: 0.22
Nodes (6): assess_table(), combined_load_check(), main(), plot_cross(), plot_history(), raw_storage_root()

### Community 43 - "README.md"
Cohesion: 0.25
Nodes (6): Explore the dashboard, From a change to an investigation, Results & evidence, Run it your way, Technical reading, Attributed derived demonstration

### Community 44 - "create_server"
Cohesion: 0.12
Nodes (3): Selection, create_server(), AlertEvidenceTests

### Community 45 - "contracts.ts"
Cohesion: 0.10
Nodes (22): assembleContext(), priority(), alertData, alertSignal, answerSchema, claim, envelopeSchema, errorSummary (+14 more)

### Community 46 - "compilerOptions"
Cohesion: 0.20
Nodes (9): compilerOptions, module, moduleResolution, outDir, rootDir, skipLibCheck, strict, target (+1 more)

### Community 47 - "orchestrator.ts"
Cohesion: 0.31
Nodes (9): withoutCredentials(), validateCitations(), Activity, Dependencies, investigate(), call(), InvestigationFailure, publicActivity() (+1 more)

### Community 48 - "protect_output"
Cohesion: 0.20
Nodes (3): evaluate(), atomic_json(), protect_output()

### Community 51 - "application.py"
Cohesion: 0.23
Nodes (10): clean(), create(), demo(), full(), html(), load_artifact(), server(), do_GET() (+2 more)

### Community 52 - "mcp.ts"
Cohesion: 0.08
Nodes (22): loadLocalConfig(), LOCAL_NAMES, REPOSITORY_ROOT, requireLiveCredentials(), manifest, assert, {chromium}, fs (+14 more)

### Community 57 - "inspect_paderborn.py"
Cohesion: 0.27
Nodes (5): inspect_b01(), main(), _plot_excerpts(), _plot_overview(), peak_rss_mib()

### Community 58 - "optimization.test.ts"
Cohesion: 0.13
Nodes (4): envelope, request, Stream, sandbox

### Community 59 - "adversarial.test.ts"
Cohesion: 0.25
Nodes (3): TOOL_NAMES, base, snapshot

### Community 61 - "build"
Cohesion: 0.24
Nodes (7): build(), events_from_ledger(), export(), main(), serve(), records(), SelectionDashboardTests

### Community 62 - "b01_plots.py"
Cohesion: 0.22
Nodes (4): condition_groups(), _label(), plot_comparisons(), cross_support()

### Community 65 - "selection.py"
Cohesion: 0.11
Nodes (15): Block, errors(), metrics(), _prepare_validated(), ratio(), folds(), enrich(), fit() (+7 more)

### Community 66 - "DocumentationWorkflowTests"
Cohesion: 0.15
Nodes (5): DocumentationIndex, passages(), sha(), SyntheticAssistantAdversarialTests, DocumentationWorkflowTests

### Community 69 - "pipeline.test.ts"
Cohesion: 0.27
Nodes (8): connectEvidence(), drainEvidenceStderr(), EvidenceClient, evidenceEnvironment(), EvidenceToolError, root(), ROOT, @modelcontextprotocol/sdk

## Knowledge Gaps
- **1 isolated node(s):** `factoryguard`
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 415 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **36 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `data()` connect `Store` to `numpy`, `test_alerts_api.py`, `test_selection.py`, `unittest`, `test_alerts.py`, `argparse`?**
  _High betweenness centrality (0.028) - this node is a cross-community bridge._
- **What connects `factoryguard` to the rest of the system?**
  _1 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `alerts/evaluate.py` be split into smaller, more focused modules?**
  _Cohesion score 0.11764705882352941 - nodes in this community are weakly interconnected._
- **Why does `ValidationTests` connect `ValidationTests` to `pathlib`?**
  _High betweenness centrality (0.021) - this node is a cross-community bridge._
- **Should `acquire_selected_paderborn.py` be split into smaller, more focused modules?**
  _Cohesion score 0.06594071385359952 - nodes in this community are weakly interconnected._
- **Why does `frame()` connect `models/forecast.py` to `numpy`, `test_alerts_api.py`, `json`?**
  _High betweenness centrality (0.017) - this node is a cross-community bridge._
- **Should `models/forecast.py` be split into smaller, more focused modules?**
  _Cohesion score 0.14516129032258066 - nodes in this community are weakly interconnected._