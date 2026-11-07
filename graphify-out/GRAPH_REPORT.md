# Graph Report - factoryguard  (2026-11-07)

## Corpus Check
- cluster-only mode — file stats not available

## Summary
- 891 nodes · 2364 edges · 47 communities (25 shown, 22 thin omitted)
- Extraction: 96% EXTRACTED · 4% INFERRED · 0% AMBIGUOUS · INFERRED: 105 edges (avg confidence: 0.86)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `85b99afd`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- campaign.py
- json
- clean
- pandas
- selection_dashboard.py
- Store
- build_readme_assets.py
- raw_manifest
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
- OfflineDashboardTests
- EvidenceService
- features_paderborn.py
- inspect_paderborn.py
- SelectedAcquisitionTests
- ProjectContextTests
- package.json
- pathlib
- orchestrator.ts
- env
- pipeline.test.ts
- provider.ts
- contracts.ts
- compilerOptions

## God Nodes (most connected - your core abstractions)
1. `run()` - 32 edges
2. `clean()` - 31 edges
3. `run()` - 28 edges
4. `digest()` - 26 edges
5. `load_table()` - 26 edges
6. `Store` - 25 edges
7. `execute()` - 24 edges
8. `audit()` - 22 edges
9. `data()` - 22 edges
10. `ForecastTests` - 21 edges

## Surprising Connections (you probably didn't know these)
- `digest()` --calls--> `sha256()`  [INFERRED]
  src/factoryguard/models/forecast.py → scripts/acquire_selected_paderborn.py
- `run()` --calls--> `sha256()`  [INFERRED]
  src/factoryguard/pipelines/select_forecast.py → scripts/acquire_selected_paderborn.py
- `demo()` --calls--> `sha256()`  [INFERRED]
  src/factoryguard/release/application.py → scripts/acquire_selected_paderborn.py
- `main()` --calls--> `run_cli()`  [INFERRED]
  dashboard/app.py → src/factoryguard/pipelines/forecast.py
- `main()` --calls--> `server()`  [INFERRED]
  dashboard/app.py → src/factoryguard/release/application.py

## Import Cycles
- None detected.

## Communities (47 total, 22 thin omitted)

### Community 0 - "campaign.py"
Cohesion: 0.05
Nodes (61): main(), main(), digest(), load_table(), Block, candidates(), choose_inner(), errors() (+53 more)

### Community 1 - "json"
Cohesion: 0.09
Nodes (23): main(), main(), download(), finalize_manifest(), load_plan(), sha256(), validate(), build() (+15 more)

### Community 2 - "clean"
Cohesion: 0.07
Nodes (30): main(), clean(), evaluate(), fit(), guard_run(), issue(), load_artifact(), Replay (+22 more)

### Community 3 - "pandas"
Cohesion: 0.16
Nodes (8): condition_groups(), assess_table(), combined_load_check(), cross_support(), main(), plot_cross(), plot_history(), raw_storage_root()

### Community 4 - "selection_dashboard.py"
Cohesion: 0.24
Nodes (7): build(), events_from_ledger(), export(), main(), serve(), records(), SelectionDashboardTests

### Community 5 - "Store"
Cohesion: 0.16
Nodes (9): export(), encode(), Store, InvestigationTests, artifact(), ReleaseAppTests, data(), ReleaseModelingTests (+1 more)

### Community 6 - "build_readme_assets.py"
Cohesion: 0.50
Nodes (7): bearing(), circle(), hero(), rect(), shell(), text(), workflow()

### Community 7 - "raw_manifest"
Cohesion: 0.21
Nodes (3): burst_rows(), raw_manifest(), DevelopmentAssessmentTests

### Community 8 - "ref_playwright"
Cohesion: 0.18
Nodes (8): {chromium}, fs, {chromium}, fs, {chromium}, fs, {chromium}, fs

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

### Community 32 - "EvidenceService"
Cohesion: 0.06
Nodes (13): evaluate(), EvidenceService, Selection, create_server(), DocumentationIndex, passages(), sha(), tokens() (+5 more)

### Community 33 - "features_paderborn.py"
Cohesion: 0.17
Nodes (6): ChannelFeatures, feature_schema(), _label(), plot_comparisons(), extract_b01(), main()

### Community 34 - "inspect_paderborn.py"
Cohesion: 0.27
Nodes (5): inspect_b01(), main(), _plot_excerpts(), _plot_overview(), peak_rss_mib()

### Community 37 - "package.json"
Cohesion: 0.09
Nodes (27): dependencies, fastify@5.12.8, @modelcontextprotocol/sdk@1.32.2, openai@7.53.0, zod@4.6.7, devDependencies, tsx@4.23.15, @types/node@26.6.6 (+19 more)

### Community 38 - "pathlib"
Cohesion: 0.06
Nodes (12): generate(), markdown_table(), report(), condition_key(), _metric(), number(), _validate_frame_fields(), compare() (+4 more)

### Community 39 - "orchestrator.ts"
Cohesion: 0.17
Nodes (13): requestSchema, validateCitations(), manifest, connectEvidence(), EvidenceClient, EvidenceToolError, root(), ROOT (+5 more)

### Community 40 - "env"
Cohesion: 0.08
Nodes (23): env, runs-on, steps, strategy, FACTORYGUARD_PYTHON, MPLBACKEND, OMP_NUM_THREADS, OPENBLAS_NUM_THREADS (+15 more)

### Community 41 - "pipeline.test.ts"
Cohesion: 0.10
Nodes (12): assert, { chromium }, base, fixture, request, assert, {chromium}, fs (+4 more)

### Community 44 - "provider.ts"
Cohesion: 0.16
Nodes (12): Answer, answerSchema, ContextPackage, TOOL_NAMES, INSTRUCTIONS, ModelResult, OfflineFixtureProvider, OpenAIProvider (+4 more)

### Community 45 - "contracts.ts"
Cohesion: 0.17
Nodes (13): assembleContext(), priority(), claim, envelopeSchema, errorSummary, EvidenceRecord, expectedUnits, InvestigationRequest (+5 more)

### Community 46 - "compilerOptions"
Cohesion: 0.20
Nodes (9): compilerOptions, module, moduleResolution, outDir, rootDir, skipLibCheck, strict, target (+1 more)

## Knowledge Gaps
- **1 isolated node(s):** `factoryguard`
  These have ≤1 connection - possible missing edges. (Counts symbols only; 316 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **22 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `PaderbornTests` connect `PaderbornTests` to `pathlib`?**
  _High betweenness centrality (0.020) - this node is a cross-community bridge._
- **What connects `factoryguard` to the rest of the system?**
  _1 weakly-connected nodes found - possible missing edges._
- **Should `campaign.py` be split into smaller, more focused modules?**
  _Cohesion score 0.051493563304586924 - nodes in this community are weakly interconnected._
- **Why does `ValidationTests` connect `ValidationTests` to `pathlib`?**
  _High betweenness centrality (0.018) - this node is a cross-community bridge._
- **Should `json` be split into smaller, more focused modules?**
  _Cohesion score 0.0852994555353902 - nodes in this community are weakly interconnected._
- **Why does `data()` connect `Store` to `campaign.py`, `pathlib`?**
  _High betweenness centrality (0.016) - this node is a cross-community bridge._
- **Should `clean` be split into smaller, more focused modules?**
  _Cohesion score 0.07155399473222125 - nodes in this community are weakly interconnected._