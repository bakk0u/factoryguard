# Final local setup and integration verification

Verified locally 2026-11-09. Offline integration passes. The optimized live
dashboard investigation is **pending manual browser execution**: no browser tool,
Playwright, Puppeteer or Python Playwright is available in this environment. No
new investigation, CLI smoke or paid model request was submitted. This is not
production-readiness or real-model prompt-injection certification.

## Setup fix

The exact prior failure was
`test_release_modeling.ReleaseModelingTests.test_future_independence_all_families_and_formulations`:
`modeling.fit()` at `from xgboost import XGBRegressor` raised
`ModuleNotFoundError: No module named 'xgboost'`.

Active interpreter: repository `.venv/bin/python`, CPython 3.12.16, macOS 27.2,
arm64, base interpreter under ignored `.tools/python`. Node is 24.22.1.
The existing campaign pin was `xgboost-cpu==3.0.5`. An actual install attempt with
the existing requirements fell back to a source build and failed because CMake
was absent. The [official 3.0.5 guide](https://xgboost.readthedocs.io/en/release_3.0.0/install.html)
confirms CPU-package wheels target Linux/Windows amd64 and standard XGBoost wheels
support Apple Silicon. `requirements-campaign.txt` and `.[campaign]` now use
platform markers: `xgboost==3.0.5` on Darwin; the same CPU pin elsewhere. All core
and assistant locks remain unchanged. Installed with `--no-deps` against the
already-locked environment, followed by a requirements-file check and editable
metadata refresh. All pre-existing Python package versions were compared and
preserved; only XGBoost 3.0.5 was added.

Importing the installed macOS wheel then produced a concrete loader error:
`Library not loaded: @rpath/libomp.dylib`. Only then was native-runtime setup
diagnosed. No evidence indicated a Python architecture mismatch. Homebrew was
absent, so no global package manager/system change was made. Instead, public
Homebrew libomp 23.1.5 arm64 bottle SHA256
`64eacbcd08fbec3ebb7076be89466a53d5548a7dbee3542d756b788047277589`
was verified and its one known regular dylib member installed under `.tools/native`.
`scripts/setup_macos_openmp.py` links it into the repo-local base interpreter's
`lib/`, one of the loader's observed search locations, and refuses checksum
mismatch or replacing an unrelated library. Import now returns version 3.0.5.
Reproducible download/install/import/test commands and platform limits are in
[the assistant setup guide](../../assistant.md#optional-xgboost-test-setup-on-macos).
No new global loader environment setting, CMake or unrelated package upgrade was
required. A sandbox-DNS failure during metadata refresh was resolved with permitted
dependency-download access; the pinned build backend then succeeded.

## Final checks

| Check | Observed result |
| --- | --- |
| XGBoost import | Passed, 3.0.5, real native library |
| Exact previously failing test | 1 passed; original assertions and real synthetic fits retained |
| Full Python suite | **143 passed**, zero failures/errors/skips; includes application/dashboard/reviewer-site tests |
| Focused assistant Python suite | **21 passed**, zero failures/skips |
| TypeScript build | Passed |
| TypeScript assistant/dashboard/mock-provider suite | **41 passed**, zero failures/skips |
| Frozen lexical retrieval/evidence cases | **40/40 passed**, both splits 20/20; documentation recall@4 and MRR@4 remain 1.0 |
| Dependency compatibility | 68 installed packages checked; compatible; pre-existing versions unchanged |
| Source/result integrity | No saved forecasting results, model code/config or pinned site source changed |
| Dotenv | Existing file unchanged, ignored/untracked, current owner, 0600; tests never use its contents or real key |
| Required context/Graphify and whitespace | Updated/status checked, code-only graph; whitespace check passed |
| Optimized service startup | Explicit `scripts/start_assistant.py --live`; loopback GET health confirms live mode; dashboard and optimized assets served |
| Final live dashboard investigation | **Unsubmitted**; browser automation unavailable; no CLI substitution |

Complete logs, interpreter/package inventory, source fingerprint and intended
payload are saved privately under `reports/local/assistant/final-integration/`.
The exact final source fingerprint and full working-tree listing are in
`verification.json`; documentation/generated-graph edits are outside the runtime
fingerprint. Base HEAD is `c23c79d8f28559002aeba3579bee6cd9f9807ead`, branch master,
with the earlier configuration/diagnostic/optimization changes and this setup
work uncommitted. No branch switch, commit, push, merge or deployment occurred.

Small existing synthetic model fits ran only for tests. No project campaign,
real-data retraining, raw writes, saved-result changes or B03 file access occurred.
All non-generation test/install/browser-check subprocesses explicitly exclude
`OPENAI_API_KEY`. The MCP/Git/site-build environment boundaries, root-only dotenv,
process precedence, configured model, offline default and explicit live opt-in
are preserved. Startup generates no answer by itself.

## Adversarial checks and limits

New synthetic/mocked-provider checks cover instructions in user text and retrieved
text trying to override channel, reserved run and replay scope; requests for
nonexistent file/shell/credential tools; fabricated citation IDs; fake-key absence
from context and trace redaction; future rows already present behind a lower
authoritative SQLite cursor, including a cursor reset; selected-channel change/
reference projection; and documentation allowlists excluding fake private files.
Existing cancellation, cleanup, schema, bounds, configuration, API duplicate and
offline DOM citation tests also pass. Optional-only tests retain the repository's
normal dependency guards for core-only installs; **none skipped in this run**.

These demonstrate deterministic scope/tool/schema/visibility/redaction checks
when a malicious mock provider chooses forbidden actions. They do not demonstrate
that a real model will resist injected prose, produce supported causal reasoning,
or avoid unsupported claims. Hybrid retrieval was not evaluated or downloaded.

## Pending manual dashboard check

Service is running at **http://127.0.0.1:8785/**. Startup command:
`.venv/bin/python scripts/start_assistant.py --live`. No assistant runtime configuration, configured model or key
was changed. Preserve the existing 60-second request, three-turn, nine-tool,
2,200-output-tokens/turn, 30-second provider timeout/one-retry and 15-second MCP
bounds. At most one additional dashboard investigation is authorized.

1. Open the URL. Select B01, Explore measurements, then Reset replay.
2. Click Next observation exactly three times; do not use Play replay or reveal
   another observation. Set first/last period inputs to 1 and 3.
3. In Ask about this period, choose channel A. Select all default question text
   and replace it with the exact text below.
4. Open Network tools, then click Ask about this period **once**. Inspect the POST
   payload: exact question, B01/A/start=1/stop=3/as_of=3/mode=replay and the pinned
   replay snapshot. Do not resubmit, even on failure.
5. On success, inspect rendering, each citation control and the evidence/activity
   panel. Check the selected-channel numerical evidence and replay positions,
   units, uncertainty and claim support separately from citation membership. On
   failure, retain only safe diagnostics and the request ID; stop paid execution.

> What do the available measurements show in this selected period? Explain the data-quality and methodological limitations, and distinguish observations from possible explanations.

No final dashboard request ID, returned model, duration, turns or usage exists
yet. Retrieval-before-generation, actual rendered answer, citation interactions,
claim support and absence of unsupported damage/health/significance/trend/causal
language remain **unverified for the final optimized live version**. Earlier
successful runs in other reports must not be substituted. No screenshot or live
interaction is claimed here. Any fix after that eventual live run requires a
separately authorized follow-up check.

Offline setup/integration is complete; the full local integration stage remains
pending this manual live dashboard verification. Broader answer-quality review,
real-model prompt-injection evaluation and independent human scientific review
remain. Restricted hosting still needs authentication/TLS, trusted hosts/origins
and CSRF review, spending/rate/concurrency limits, durable submission idempotency,
secret/evidence/egress isolation, an explicit authoritative-cursor policy, trace
access/retention/deletion rules, and hosted lifecycle/security checks. Hosting and
billing settings were not implemented or changed.
