# Graph Report - factoryguard  (2026-11-10)

## Corpus Check
- cluster-only mode — file stats not available

## Summary
- 1007 nodes · 2642 edges · 71 communities (39 shown, 32 thin omitted)
- Extraction: 95% EXTRACTED · 5% INFERRED · 0% AMBIGUOUS · INFERRED: 128 edges (avg confidence: 0.86)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `c23c79d8`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- holdout.py
- json
- ForecastTests
- holdout.py
- hashlib
- Store
- build_readme_assets.py
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
- FeaturePipelineTests
- prepare
- application.py
- features_paderborn.py
- inspect_paderborn.py
- provider-error.test.ts
- ProjectContextTests
- package.json
- EvidenceService
- orchestrator.ts
- env
- dependencies
- b01_plots.py
- README.md
- pandas
- contracts.ts
- compilerOptions
- orchestrator.ts
- campaign.py
- project_context.py
- mcp.ts
- test_forecasting.py
- numpy
- pathlib
- OptionalIsolationTests
- selection_dashboard.py
- optimization.test.ts
- adversarial.test.ts
- ReviewerSiteTests
- start_assistant.py
- argparse
- Working on FactoryGuard
- reviewer_experience.js
- OfflineDashboardTests
- SelectedAcquisitionTests
- AssistantConfigTests
- server
- data

## God Nodes (most connected - your core abstractions)
1. `run()` - 32 edges
2. `clean()` - 31 edges
3. `run()` - 28 edges
4. `Store` - 26 edges
5. `digest()` - 26 edges
6. `load_table()` - 26 edges
7. `execute()` - 24 edges
8. `EvidenceService` - 23 edges
9. `audit()` - 22 edges
10. `data()` - 22 edges

## Surprising Connections (you probably didn't know these)
- `Persistent context bootstrap` --references--> `graphify()`  [INFERRED]
  AGENTS.md → scripts/project_context.py
- `Locate only the relevant components` --references--> `Store`  [INFERRED]
  PROJECT_MEMORY.md → src/factoryguard/release/store.py
- `digest()` --calls--> `sha256()`  [INFERRED]
  src/factoryguard/models/forecast.py → scripts/acquire_selected_paderborn.py
- `run()` --calls--> `sha256()`  [INFERRED]
  src/factoryguard/pipelines/select_forecast.py → scripts/acquire_selected_paderborn.py
- `demo()` --calls--> `sha256()`  [INFERRED]
  src/factoryguard/release/application.py → scripts/acquire_selected_paderborn.py

## Import Cycles
- None detected.

## Communities (71 total, 32 thin omitted)

### Community 0 - "holdout.py"
Cohesion: 0.13
Nodes (7): Block, _prepare_validated(), candidates(), fit(), groups(), predict(), select()

### Community 1 - "json"
Cohesion: 0.16
Nodes (10): download(), finalize_manifest(), load_plan(), sha256(), validate(), bundle(), build_html(), main() (+2 more)

### Community 2 - "ForecastTests"
Cohesion: 0.09
Nodes (15): evaluate(), guard_run(), issue(), number(), Replay, replay_frame(), make_server(), do_GET() (+7 more)

### Community 3 - "holdout.py"
Cohesion: 0.24
Nodes (11): digest(), _validate_frame_fields(), errors(), metrics(), ratio(), strata_rows(), code_hashes(), execute() (+3 more)

### Community 5 - "Store"
Cohesion: 0.14
Nodes (14): FactoryGuard project memory, Locate only the relevant components, Next work and maintenance, Purpose and hard boundaries, Session and verification commands, Verified state and evidence, export(), notices() (+6 more)

### Community 6 - "build_readme_assets.py"
Cohesion: 0.44
Nodes (7): bearing(), circle(), hero(), rect(), shell(), text(), workflow()

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
Cohesion: 0.09
Nodes (3): plot_readings(), run_step1(), ValidationTests

### Community 15 - "reviewer.js"
Cohesion: 0.23
Nodes (8): enhance(), friendly(), invalidateChangedPeriod(), investigationReport(), periodIdentity(), referenceIdentifiers(), view(), volatileNotes

### Community 31 - "prepare"
Cohesion: 0.15
Nodes (10): candidates(), FiniteGate, fit_candidate(), predict(), prepare(), splits(), candidate(), config() (+2 more)

### Community 32 - "application.py"
Cohesion: 0.24
Nodes (13): fresh(), create(), demo(), full(), load_artifact(), folds(), read(), write() (+5 more)

### Community 33 - "features_paderborn.py"
Cohesion: 0.14
Nodes (4): ChannelFeatures, feature_schema(), extract_b01(), main()

### Community 34 - "inspect_paderborn.py"
Cohesion: 0.33
Nodes (5): inspect_b01(), main(), _plot_excerpts(), _plot_overview(), peak_rss_mib()

### Community 35 - "provider-error.test.ts"
Cohesion: 0.13
Nodes (17): openai@7.53.0, ContextPackage, ANSWER_JSON_SCHEMA, ProviderDiagnostic, providerDiagnostic(), ProviderFailure, redact(), INSTRUCTIONS (+9 more)

### Community 37 - "package.json"
Cohesion: 0.12
Nodes (18): devDependencies, tsx@4.23.15, @types/node@26.6.6, typescript@7.0.2, engines, node, name, private (+10 more)

### Community 38 - "EvidenceService"
Cohesion: 0.06
Nodes (16): evaluate(), EvidenceService, Selection, create_server(), DocumentationIndex, passages(), search_tokens(), sha() (+8 more)

### Community 39 - "orchestrator.ts"
Cohesion: 0.15
Nodes (10): Selection, connectEvidence(), EvidenceClient, evidenceEnvironment(), EvidenceToolError, root(), ROOT, base (+2 more)

### Community 40 - "env"
Cohesion: 0.08
Nodes (23): env, runs-on, steps, strategy, FACTORYGUARD_PYTHON, MPLBACKEND, OMP_NUM_THREADS, OPENBLAS_NUM_THREADS (+15 more)

### Community 41 - "dependencies"
Cohesion: 0.29
Nodes (7): dependencies, fastify@5.12.8, @modelcontextprotocol/sdk@1.32.2, zod@4.6.7, fastify, @modelcontextprotocol/sdk, zod

### Community 42 - "b01_plots.py"
Cohesion: 0.12
Nodes (9): condition_groups(), _label(), plot_comparisons(), assess_table(), combined_load_check(), cross_support(), main(), plot_cross() (+1 more)

### Community 43 - "README.md"
Cohesion: 0.25
Nodes (6): Explore the dashboard, From a change to an investigation, Results & evidence, Run it your way, Technical reading, Attributed derived demonstration

### Community 44 - "pandas"
Cohesion: 0.23
Nodes (11): main(), fit(), load_artifact(), load_table(), validate_artifact(), validate_config(), validate_frame(), write_json() (+3 more)

### Community 45 - "contracts.ts"
Cohesion: 0.14
Nodes (15): assembleContext(), priority(), providerContext(), Answer, answerSchema, claim, envelopeSchema, errorSummary (+7 more)

### Community 46 - "compilerOptions"
Cohesion: 0.20
Nodes (9): compilerOptions, module, moduleResolution, outDir, rootDir, skipLibCheck, strict, target (+1 more)

### Community 47 - "orchestrator.ts"
Cohesion: 0.29
Nodes (10): withoutCredentials(), validateCitations(), Activity, Dependencies, investigate(), call(), InvestigationFailure, publicActivity() (+2 more)

### Community 48 - "campaign.py"
Cohesion: 0.16
Nodes (15): main(), choose_inner(), score(), select_method(), coverage(), ledger(), main(), run() (+7 more)

### Community 51 - "project_context.py"
Cohesion: 0.32
Nodes (10): digest(), environment(), executable(), graphify(), main(), normalize_hooks(), source_hashes(), stamp() (+2 more)

### Community 52 - "mcp.ts"
Cohesion: 0.10
Nodes (18): loadLocalConfig(), LOCAL_NAMES, REPOSITORY_ROOT, requireLiveCredentials(), manifest, assert, {chromium}, fs (+10 more)

### Community 54 - "numpy"
Cohesion: 0.17
Nodes (9): generate(), clean(), condition_key(), _metric(), compare(), reference(), evidence(), enrich() (+1 more)

### Community 57 - "selection_dashboard.py"
Cohesion: 0.24
Nodes (7): build(), events_from_ledger(), export(), main(), serve(), records(), SelectionDashboardTests

### Community 58 - "optimization.test.ts"
Cohesion: 0.11
Nodes (6): envelope, next(), request, Stream, sandbox, next()

### Community 59 - "adversarial.test.ts"
Cohesion: 0.25
Nodes (4): requestSchema, TOOL_NAMES, base, snapshot

### Community 62 - "argparse"
Cohesion: 0.28
Nodes (3): main(), markdown_table(), report()

### Community 63 - "Working on FactoryGuard"
Cohesion: 0.18
Nodes (10): Authorized bounded selection milestone, Authorized forecasting prototype, Claims and next milestone, Current development release authorization, Data integrity and leakage prevention, Development and verification, graphify, Persistent context bootstrap (+2 more)

### Community 68 - "server"
Cohesion: 0.38
Nodes (6): main(), html(), server(), do_GET(), do_POST(), reply()

## Knowledge Gaps
- **1 isolated node(s):** `factoryguard`
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 380 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **32 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `channel_features()` connect `channel_features` to `features_paderborn.py`, `numpy`, `DevelopmentAssessmentTests`?**
  _High betweenness centrality (0.022) - this node is a cross-community bridge._
- **What connects `factoryguard` to the rest of the system?**
  _1 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `holdout.py` be split into smaller, more focused modules?**
  _Cohesion score 0.12857142857142856 - nodes in this community are weakly interconnected._
- **Why does `ValidationTests` connect `ValidationTests` to `hashlib`?**
  _High betweenness centrality (0.021) - this node is a cross-community bridge._
- **Should `ForecastTests` be split into smaller, more focused modules?**
  _Cohesion score 0.09308510638297872 - nodes in this community are weakly interconnected._
- **Why does `AssistantEvidenceTests` connect `EvidenceService` to `pathlib`?**
  _High betweenness centrality (0.020) - this node is a cross-community bridge._
- **Should `hashlib` be split into smaller, more focused modules?**
  _Cohesion score 0.1437908496732026 - nodes in this community are weakly interconnected._