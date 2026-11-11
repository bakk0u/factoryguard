# Graph Report - factoryguard  (2026-11-11)

## Corpus Check
- cluster-only mode — file stats not available

## Summary
- 1162 nodes · 3118 edges · 66 communities (37 shown, 29 thin omitted)
- Extraction: 95% EXTRACTED · 5% INFERRED · 0% AMBIGUOUS · INFERRED: 164 edges (avg confidence: 0.86)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `98a678d2`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- alerts/evaluate.py
- acquire_selected_paderborn.py
- models/forecast.py
- test_selection.py
- json
- Store
- shutil
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
- math
- build_reviewer_site.py
- prepare.py
- provider-error.test.ts
- ProjectContextTests
- package.json
- EvidenceService
- provider.ts
- env
- assess_development.py
- README.md
- create_server
- contracts.ts
- compilerOptions
- orchestrator.ts
- retrieval.py
- mcp.ts
- AssistantEvidenceTests
- pathlib
- hashlib
- protect_output
- inspect_paderborn.py
- optimization.test.ts
- adversarial.test.ts
- features_paderborn.py
- b01_plots.py
- Working on FactoryGuard
- reviewer_experience.js
- numpy
- DocumentationWorkflowTests
- mountInvestigationAlerts
- pipeline.test.ts

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
- `Persistent context bootstrap` --references--> `graphify()`  [INFERRED]
  AGENTS.md → scripts/project_context.py
- `Locate only the relevant components` --references--> `Store`  [INFERRED]
  PROJECT_MEMORY.md → src/factoryguard/release/store.py
- `build()` --calls--> `AlertJournal`  [INFERRED]
  scripts/build_reviewer_site.py → src/factoryguard/alerts/journal.py
- `AlertTests` --uses--> `Store`  [INFERRED]
  tests/test_alerts.py → src/factoryguard/release/store.py
- `fingerprint()` --calls--> `sha256()`  [INFERRED]
  src/factoryguard/alerts/engine.py → scripts/acquire_selected_paderborn.py

## Import Cycles
- None detected.

## Communities (66 total, 29 thin omitted)

### Community 0 - "alerts/evaluate.py"
Cohesion: 0.12
Nodes (12): AlertEngine, canonical(), channel_value(), fingerprint(), finite(), load_policy(), Policy, replay() (+4 more)

### Community 1 - "acquire_selected_paderborn.py"
Cohesion: 0.32
Nodes (10): digest(), environment(), executable(), graphify(), main(), normalize_hooks(), source_hashes(), stamp() (+2 more)

### Community 2 - "models/forecast.py"
Cohesion: 0.07
Nodes (21): evaluate(), guard_run(), issue(), Replay, replay_frame(), make_server(), do_GET(), do_POST() (+13 more)

### Community 3 - "test_selection.py"
Cohesion: 0.15
Nodes (10): candidates(), FiniteGate, fit_candidate(), predict(), prepare(), splits(), candidate(), config() (+2 more)

### Community 4 - "json"
Cohesion: 0.23
Nodes (9): download(), finalize_manifest(), load_plan(), sha256(), validate(), bundle(), build_html(), main() (+1 more)

### Community 5 - "Store"
Cohesion: 0.12
Nodes (16): FactoryGuard project memory, Locate only the relevant components, Next work and maintenance, Purpose and hard boundaries, Session and verification commands, Verified state and evidence, export(), compare() (+8 more)

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

### Community 15 - "reviewer.js"
Cohesion: 0.23
Nodes (8): enhance(), friendly(), invalidateChangedPeriod(), investigationReport(), periodIdentity(), referenceIdentifiers(), view(), volatileNotes

### Community 26 - "event"
Cohesion: 0.06
Nodes (23): AlertEngine, canonical(), channel_value(), fingerprint(), finite(), load_policy(), Policy, replay() (+15 more)

### Community 31 - "math"
Cohesion: 0.50
Nodes (7): bearing(), circle(), hero(), rect(), shell(), text(), workflow()

### Community 35 - "provider-error.test.ts"
Cohesion: 0.13
Nodes (16): dependencies, fastify@5.12.8, @modelcontextprotocol/sdk@1.32.2, openai@7.53.0, zod@4.6.7, ProviderDiagnostic, providerDiagnostic(), ProviderFailure (+8 more)

### Community 37 - "package.json"
Cohesion: 0.12
Nodes (18): devDependencies, tsx@4.23.15, @types/node@26.6.6, typescript@7.0.2, engines, node, name, private (+10 more)

### Community 38 - "EvidenceService"
Cohesion: 0.27
Nodes (3): evaluate(), EvidenceService, run_workflow()

### Community 39 - "provider.ts"
Cohesion: 0.16
Nodes (13): providerContext(), Answer, ContextPackage, ANSWER_JSON_SCHEMA, INSTRUCTIONS, ModelResult, OfflineFixtureProvider, OpenAIProvider (+5 more)

### Community 40 - "env"
Cohesion: 0.08
Nodes (23): env, runs-on, steps, strategy, FACTORYGUARD_PYTHON, MPLBACKEND, OMP_NUM_THREADS, OPENBLAS_NUM_THREADS (+15 more)

### Community 42 - "assess_development.py"
Cohesion: 0.25
Nodes (5): assess_table(), combined_load_check(), main(), plot_cross(), plot_history()

### Community 43 - "README.md"
Cohesion: 0.25
Nodes (6): Explore the dashboard, From a change to an investigation, Results & evidence, Run it your way, Technical reading, Attributed derived demonstration

### Community 44 - "create_server"
Cohesion: 0.12
Nodes (3): Selection, create_server(), AlertEvidenceTests

### Community 45 - "contracts.ts"
Cohesion: 0.10
Nodes (21): assembleContext(), priority(), alertData, alertSignal, answerSchema, claim, envelopeSchema, errorSummary (+13 more)

### Community 46 - "compilerOptions"
Cohesion: 0.20
Nodes (9): compilerOptions, module, moduleResolution, outDir, rootDir, skipLibCheck, strict, target (+1 more)

### Community 47 - "orchestrator.ts"
Cohesion: 0.31
Nodes (9): withoutCredentials(), validateCitations(), Activity, Dependencies, investigate(), call(), InvestigationFailure, publicActivity() (+1 more)

### Community 48 - "retrieval.py"
Cohesion: 0.20
Nodes (4): passages(), search_tokens(), sha(), tokens()

### Community 52 - "mcp.ts"
Cohesion: 0.08
Nodes (22): loadLocalConfig(), LOCAL_NAMES, REPOSITORY_ROOT, requireLiveCredentials(), manifest, assert, {chromium}, fs (+14 more)

### Community 54 - "pathlib"
Cohesion: 0.05
Nodes (9): child_environment(), AssistantConfigTests, OptionalIsolationTests, OfflineDashboardTests, CampaignTests, data(), ReleaseModelingTests, ReviewerSiteTests (+1 more)

### Community 56 - "protect_output"
Cohesion: 0.27
Nodes (3): atomic_json(), protect_output(), raw_storage_root()

### Community 57 - "inspect_paderborn.py"
Cohesion: 0.33
Nodes (5): inspect_b01(), main(), _plot_excerpts(), _plot_overview(), peak_rss_mib()

### Community 58 - "optimization.test.ts"
Cohesion: 0.13
Nodes (4): envelope, request, Stream, sandbox

### Community 59 - "adversarial.test.ts"
Cohesion: 0.25
Nodes (4): requestSchema, TOOL_NAMES, base, snapshot

### Community 60 - "features_paderborn.py"
Cohesion: 0.20
Nodes (5): ChannelFeatures, feature_schema(), extract_b01(), main(), raw_manifest()

### Community 62 - "b01_plots.py"
Cohesion: 0.17
Nodes (4): condition_groups(), _label(), plot_comparisons(), cross_support()

### Community 63 - "Working on FactoryGuard"
Cohesion: 0.18
Nodes (10): Authorized bounded selection milestone, Authorized forecasting prototype, Claims and next milestone, Current development release authorization, Data integrity and leakage prevention, Development and verification, graphify, Persistent context bootstrap (+2 more)

### Community 65 - "numpy"
Cohesion: 0.05
Nodes (75): main(), generate(), main(), main(), main(), markdown_table(), report(), clean() (+67 more)

### Community 66 - "DocumentationWorkflowTests"
Cohesion: 0.21
Nodes (3): DocumentationIndex, SyntheticAssistantAdversarialTests, DocumentationWorkflowTests

### Community 69 - "pipeline.test.ts"
Cohesion: 0.19
Nodes (10): connectEvidence(), EvidenceClient, evidenceEnvironment(), EvidenceToolError, root(), ROOT, base, fixture (+2 more)

## Knowledge Gaps
- **1 isolated node(s):** `factoryguard`
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 415 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **29 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `EvidenceService` connect `EvidenceService` to `retrieval.py`, `protect_output`, `create_server`, `AssistantEvidenceTests`?**
  _High betweenness centrality (0.024) - this node is a cross-community bridge._
- **What connects `factoryguard` to the rest of the system?**
  _1 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `alerts/evaluate.py` be split into smaller, more focused modules?**
  _Cohesion score 0.12436974789915967 - nodes in this community are weakly interconnected._
- **Why does `channel_features()` connect `channel_features` to `numpy`, `features_paderborn.py`, `DevelopmentAssessmentTests`?**
  _High betweenness centrality (0.019) - this node is a cross-community bridge._
- **Should `models/forecast.py` be split into smaller, more focused modules?**
  _Cohesion score 0.06994535519125683 - nodes in this community are weakly interconnected._
- **Why does `AssistantEvidenceTests` connect `AssistantEvidenceTests` to `DocumentationWorkflowTests`, `pathlib`?**
  _High betweenness centrality (0.019) - this node is a cross-community bridge._
- **Should `test_selection.py` be split into smaller, more focused modules?**
  _Cohesion score 0.14962121212121213 - nodes in this community are weakly interconnected._