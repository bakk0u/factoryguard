# Graph Report - factoryguard  (2026-11-07)

## Corpus Check
- cluster-only mode — file stats not available

## Summary
- 688 nodes · 1926 edges · 38 communities (19 shown, 19 thin omitted)
- Extraction: 95% EXTRACTED · 5% INFERRED · 0% AMBIGUOUS · INFERRED: 89 edges (avg confidence: 0.86)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `589f5029`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- campaign.py
- json
- models/forecast.py
- pandas
- selection_dashboard.py
- Store
- test_selection.py
- raw_manifest
- verify_reviewer_workflow.cjs
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
- prepare.py
- build_readme_assets.py
- b01_plots.py
- inspect_paderborn.py
- features_paderborn.py
- ProjectContextTests
- pathlib

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
- `main()` --calls--> `predict()`  [INFERRED]
  scripts/verify_selection_outputs.py → src/factoryguard/models/selection.py
- `main()` --calls--> `prepare()`  [INFERRED]
  scripts/verify_selection_outputs.py → src/factoryguard/models/selection.py
- `digest()` --calls--> `sha256()`  [INFERRED]
  src/factoryguard/models/forecast.py → scripts/acquire_selected_paderborn.py
- `run()` --calls--> `sha256()`  [INFERRED]
  src/factoryguard/pipelines/select_forecast.py → scripts/acquire_selected_paderborn.py
- `demo()` --calls--> `sha256()`  [INFERRED]
  src/factoryguard/release/application.py → scripts/acquire_selected_paderborn.py

## Import Cycles
- None detected.

## Communities (38 total, 19 thin omitted)

### Community 0 - "campaign.py"
Cohesion: 0.07
Nodes (57): main(), main(), clean(), condition_key(), digest(), load_table(), Block, choose_inner() (+49 more)

### Community 1 - "json"
Cohesion: 0.08
Nodes (24): main(), download(), finalize_manifest(), load_plan(), sha256(), validate(), build(), bundle() (+16 more)

### Community 2 - "models/forecast.py"
Cohesion: 0.08
Nodes (27): main(), evaluate(), fit(), guard_run(), issue(), load_artifact(), _metric(), number() (+19 more)

### Community 3 - "pandas"
Cohesion: 0.17
Nodes (9): generate(), assess_table(), combined_load_check(), cross_support(), main(), plot_cross(), plot_history(), protect_output() (+1 more)

### Community 4 - "selection_dashboard.py"
Cohesion: 0.22
Nodes (7): build(), events_from_ledger(), export(), main(), serve(), records(), SelectionDashboardTests

### Community 5 - "Store"
Cohesion: 0.15
Nodes (10): export(), evidence(), encode(), Store, InvestigationTests, artifact(), ReleaseAppTests, data() (+2 more)

### Community 6 - "test_selection.py"
Cohesion: 0.13
Nodes (10): candidates(), FiniteGate, fit_candidate(), predict(), prepare(), splits(), candidate(), config() (+2 more)

### Community 7 - "raw_manifest"
Cohesion: 0.18
Nodes (3): burst_rows(), raw_manifest(), DevelopmentAssessmentTests

### Community 8 - "verify_reviewer_workflow.cjs"
Cohesion: 0.08
Nodes (15): {chromium}, fs, {chromium}, fs, {chromium}, fs, assert, {chromium} (+7 more)

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

### Community 32 - "build_readme_assets.py"
Cohesion: 0.44
Nodes (7): bearing(), circle(), hero(), rect(), shell(), text(), workflow()

### Community 33 - "b01_plots.py"
Cohesion: 0.31
Nodes (3): condition_groups(), _label(), plot_comparisons()

### Community 34 - "inspect_paderborn.py"
Cohesion: 0.18
Nodes (5): inspect_b01(), main(), _plot_excerpts(), _plot_overview(), peak_rss_mib()

### Community 35 - "features_paderborn.py"
Cohesion: 0.19
Nodes (4): ChannelFeatures, feature_schema(), extract_b01(), main()

### Community 38 - "pathlib"
Cohesion: 0.07
Nodes (6): compare(), notices(), OfflineDashboardTests, CampaignTests, ReviewerSiteTests, SelectedAcquisitionTests

## Knowledge Gaps
- **1 isolated node(s):** `factoryguard`
  These have ≤1 connection - possible missing edges. (Counts symbols only; 240 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **19 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `PaderbornTests` connect `PaderbornTests` to `pathlib`?**
  _High betweenness centrality (0.029) - this node is a cross-community bridge._
- **What connects `factoryguard` to the rest of the system?**
  _1 weakly-connected nodes found - possible missing edges._
- **Should `campaign.py` be split into smaller, more focused modules?**
  _Cohesion score 0.0652442250044084 - nodes in this community are weakly interconnected._
- **Why does `ValidationTests` connect `ValidationTests` to `pathlib`?**
  _High betweenness centrality (0.026) - this node is a cross-community bridge._
- **Should `json` be split into smaller, more focused modules?**
  _Cohesion score 0.08123904149620105 - nodes in this community are weakly interconnected._
- **Why does `data()` connect `Store` to `campaign.py`, `pathlib`, `test_selection.py`?**
  _High betweenness centrality (0.024) - this node is a cross-community bridge._
- **Should `models/forecast.py` be split into smaller, more focused modules?**
  _Cohesion score 0.07502131287297528 - nodes in this community are weakly interconnected._