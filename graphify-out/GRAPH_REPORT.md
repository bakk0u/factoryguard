# Graph Report - factoryguard  (2026-11-07)

## Corpus Check
- cluster-only mode — file stats not available

## Summary
- 918 nodes · 2410 edges · 49 communities (27 shown, 22 thin omitted)
- Extraction: 95% EXTRACTED · 5% INFERRED · 0% AMBIGUOUS · INFERRED: 124 edges (avg confidence: 0.86)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `d7c2806b`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- numpy
- acquire_selected_paderborn.py
- json
- pandas
- selection_dashboard.py
- Store
- build_readme_assets.py
- extract_b01
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
- test_selection.py
- EvidenceService
- features_paderborn.py
- inspect_paderborn.py
- prepare.py
- ProjectContextTests
- package.json
- pathlib
- orchestrator.ts
- env
- pipeline.test.ts
- b01_plots.py
- README.md
- provider.ts
- contracts.ts
- compilerOptions

## God Nodes (most connected - your core abstractions)
1. `run()` - 32 edges
2. `clean()` - 31 edges
3. `run()` - 28 edges
4. `Store` - 26 edges
5. `digest()` - 26 edges
6. `load_table()` - 26 edges
7. `execute()` - 24 edges
8. `audit()` - 22 edges
9. `data()` - 22 edges
10. `ForecastTests` - 21 edges

## Surprising Connections (you probably didn't know these)
- `Locate only the relevant components` --references--> `Store`  [INFERRED]
  PROJECT_MEMORY.md → src/factoryguard/release/store.py
- `Persistent context bootstrap` --references--> `graphify()`  [INFERRED]
  AGENTS.md → scripts/project_context.py
- `InvestigationTests` --uses--> `Store`  [INFERRED]
  tests/test_investigation.py → src/factoryguard/release/store.py
- `main()` --calls--> `predict()`  [INFERRED]
  scripts/verify_selection_outputs.py → src/factoryguard/models/selection.py
- `main()` --calls--> `prepare()`  [INFERRED]
  scripts/verify_selection_outputs.py → src/factoryguard/models/selection.py

## Import Cycles
- None detected.

## Communities (49 total, 22 thin omitted)

### Community 0 - "numpy"
Cohesion: 0.07
Nodes (57): main(), main(), clean(), condition_key(), digest(), load_table(), Block, choose_inner() (+49 more)

### Community 1 - "acquire_selected_paderborn.py"
Cohesion: 0.08
Nodes (29): Authorized bounded selection milestone, Authorized forecasting prototype, Claims and next milestone, Current development release authorization, Data integrity and leakage prevention, Development and verification, graphify, Persistent context bootstrap (+21 more)

### Community 2 - "json"
Cohesion: 0.05
Nodes (31): main(), main(), markdown_table(), report(), evaluate(), fit(), guard_run(), issue() (+23 more)

### Community 3 - "pandas"
Cohesion: 0.20
Nodes (7): assess_table(), combined_load_check(), cross_support(), main(), plot_cross(), plot_history(), raw_storage_root()

### Community 4 - "selection_dashboard.py"
Cohesion: 0.24
Nodes (7): build(), events_from_ledger(), export(), main(), serve(), records(), SelectionDashboardTests

### Community 5 - "Store"
Cohesion: 0.16
Nodes (12): FactoryGuard project memory, Locate only the relevant components, Next work and maintenance, Purpose and hard boundaries, Session and verification commands, Verified state and evidence, export(), encode() (+4 more)

### Community 6 - "build_readme_assets.py"
Cohesion: 0.50
Nodes (7): bearing(), circle(), hero(), rect(), shell(), text(), workflow()

### Community 7 - "extract_b01"
Cohesion: 0.20
Nodes (4): burst_rows(), extract_b01(), raw_manifest(), DevelopmentAssessmentTests

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

### Community 14 - "channel_features"
Cohesion: 0.24
Nodes (3): channel_features(), ChannelFeatures, ChannelFeatureTests

### Community 15 - "reviewer.js"
Cohesion: 0.23
Nodes (8): enhance(), friendly(), invalidateChangedPeriod(), investigationReport(), periodIdentity(), referenceIdentifiers(), view(), volatileNotes

### Community 31 - "test_selection.py"
Cohesion: 0.14
Nodes (10): candidates(), FiniteGate, fit_candidate(), predict(), prepare(), splits(), candidate(), config() (+2 more)

### Community 32 - "EvidenceService"
Cohesion: 0.06
Nodes (15): build_html(), main(), evaluate(), EvidenceService, Selection, create_server(), DocumentationIndex, passages() (+7 more)

### Community 34 - "inspect_paderborn.py"
Cohesion: 0.33
Nodes (5): inspect_b01(), main(), _plot_excerpts(), _plot_overview(), peak_rss_mib()

### Community 37 - "package.json"
Cohesion: 0.09
Nodes (27): dependencies, fastify@5.12.8, @modelcontextprotocol/sdk@1.32.2, openai@7.53.0, zod@4.6.7, devDependencies, tsx@4.23.15, @types/node@26.6.6 (+19 more)

### Community 38 - "pathlib"
Cohesion: 0.05
Nodes (12): generate(), compare(), notices(), evidence(), OptionalIsolationTests, InvestigationTests, OfflineDashboardTests, CampaignTests (+4 more)

### Community 39 - "orchestrator.ts"
Cohesion: 0.17
Nodes (13): requestSchema, validateCitations(), manifest, connectEvidence(), EvidenceClient, EvidenceToolError, root(), ROOT (+5 more)

### Community 40 - "env"
Cohesion: 0.08
Nodes (23): env, runs-on, steps, strategy, FACTORYGUARD_PYTHON, MPLBACKEND, OMP_NUM_THREADS, OPENBLAS_NUM_THREADS (+15 more)

### Community 41 - "pipeline.test.ts"
Cohesion: 0.10
Nodes (12): assert, { chromium }, base, fixture, request, assert, {chromium}, fs (+4 more)

### Community 42 - "b01_plots.py"
Cohesion: 0.24
Nodes (3): condition_groups(), _label(), plot_comparisons()

### Community 43 - "README.md"
Cohesion: 0.25
Nodes (6): Explore the dashboard, From a change to an investigation, Results & evidence, Run it your way, Technical reading, Attributed derived demonstration

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
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 336 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **22 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Store` connect `Store` to `numpy`, `pathlib`?**
  _High betweenness centrality (0.021) - this node is a cross-community bridge._
- **What connects `factoryguard` to the rest of the system?**
  _1 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `numpy` be split into smaller, more focused modules?**
  _Cohesion score 0.07148514851485148 - nodes in this community are weakly interconnected._
- **Why does `PaderbornTests` connect `PaderbornTests` to `pathlib`?**
  _High betweenness centrality (0.019) - this node is a cross-community bridge._
- **Should `acquire_selected_paderborn.py` be split into smaller, more focused modules?**
  _Cohesion score 0.07541478129713423 - nodes in this community are weakly interconnected._
- **Why does `ValidationTests` connect `ValidationTests` to `prepare.py`?**
  _High betweenness centrality (0.017) - this node is a cross-community bridge._
- **Should `json` be split into smaller, more focused modules?**
  _Cohesion score 0.054431960049937576 - nodes in this community are weakly interconnected._