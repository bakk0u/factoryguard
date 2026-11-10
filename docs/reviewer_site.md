# Recorded-results website

Dashboard: <https://bakk0u.github.io/factoryguard/>.
The owner reports successful [Pages publication](https://github.com/bakk0u/factoryguard/actions/runs/40520283007).
The release-documentation environment cannot reach the host, so public populated
results, navigation, report download and the deployed source commit remain
unverified here. See [verification record](release_verification.md).

## Review workflow

The locally redesigned source opens on **Start here**, with a plain-language
introduction, verified snapshot facts and a **Walk through an investigation** action.
The deterministic five-step example resets B01 replay and reveals exactly
observations 1–3 for channel A. It explains recorded RMS, forecasts, operating
context and warm-up/reference/timing limitations. It is labelled walkthrough
guidance; it is neither a saved AI answer nor a new model response. No API key,
provider request, fabricated anomaly or diagnosis is needed.

**Explore measurements** retains reset/play/step/full-history controls, charts,
keyboard-accessible history, period selection, notes and reports. A deeper
**Investigation queue** filters recorded notices from revealed observations; these
are review prompts, not confirmed faults. **AI assistant** jumps to the question
panel next to the selected-channel measurements (directly afterward on mobile).
Scope is visible, suggested questions populate without submitting, and generation
requires an explicit click. The static export clearly marks new answers unavailable;
the optional local service upgrades it to fixture or explicitly live mode. Citation
controls open values/units and stable source provenance in a focusable panel;
Escape closes the panel and returns focus. Detailed traces remain expandable.

**Methods & results** contains the baseline/selected method explanation, scoped
development results, filterable full comparisons, coverage and provenance.
**Engineering** explains the architecture, local setup and implemented versus
unverified safeguards. These are sections, without a new routing framework.
The Layout 3 view uses a narrow navigation rail, a revealed-notice Attention
column on wide screens, and a working canvas. The Attention filter and deeper
queue share the same revealed evidence. On smaller screens, the header's queue
button provides access without squeezing the measurement/assistant workspace.
Notice counts are actual records, not the mockup's example review count.

Engineering now has an interactive 14-component system map: recorded data →
forecasting → pinned results; dashboard → TypeScript → MCP → Python retrieval;
RAG/context → optional OpenAI generation → citation validation → evidence display.
Local traces are shown alongside request stages. Keyboard/click selection reveals
one concise example and expandable contracts/source links. Future hosting is
marked unimplemented; optional hybrid retrieval is marked unevaluated. Selecting
a diagram component never submits a question or executes a tool.

Charts, endpoint comparisons, short labels and disclosure sections replace the
long introductory/method paragraphs. Essential non-diagnosis, development-only,
replay and B04 qualifications remain visible; deeper timing, coverage, reference
and provenance explanations remain available. The five guidance questions sit
under Notice / Evidence / Findings stages and use the unchanged pinned B01 data.
Commanded values are optional. Matching coarse bins does not prove identical
conditions. References are development distributions, not healthy ranges.

Canonical sources are `src/factoryguard/release/dashboard.html` (replay/chart
engine), `site/reviewer.js` (existing notebook/exploration),
`site/reviewer_experience.js` (reviewer hierarchy), `site/reviewer.css` and
`site/layout3.css` (theme/layout), and `site/architecture.js` (interactive map).
`scripts/build_reviewer_site.py` inlines them; `assistant/web/assistant.js` upgrades
the shared assistant markup only on the optional local service. CSS is included in
context freshness hashes even though it has no AST symbols. Generated HTML is not
the editing source. The public deployment has not been updated by this local task.

The static site includes B01 (377 observations), B02 (1,116) and diagnostic B04
(1,114), all selected recorded forecasts/errors and 432 saved comparison rows.
B03, raw waveforms, model pickles, SQLite databases and private notes are excluded.
It needs no Python, external APIs or CDN resources. Opening the page does not
retrain models or connect to equipment.

## Notes and evidence exports

Website notes use browser-local storage, keyed by replay-snapshot SHA256 and
experiment. They survive browser restart where storage is available, remain
separate from generated evidence and are retained through replay resets. Legacy
notes are offered for explicit export, never silently merged/deleted. When storage
is blocked, notes remain in the current tab with a warning; export before closing.
Replay progress is not persisted. The optional local-server application uses
SQLite for both notes and replay state instead.

Reports include the selected recorded events, separate user notes, full source
manifest, website-build commit, model settings and available reference identifiers.
A reference-only hash, if available, is distinct from the containing replay.json
SHA256. Source runs in the snapshot are distinguished from sources matched to the
selected period. Unknown result-producing commit and generation time remain null
with explanations; a website-build commit is not substituted for either.

[Source manifest](../site/source-manifest.json) pins results by hashes, not file
dates. [Dataset attribution](../README.md#data-attribution-and-licensing) applies to
these transformed laboratory descriptors. No raw waveform is redistributed.

## Optional build and local review

With the [Python environment](development_release.md) installed:

```bash
python scripts/build_reviewer_site.py --output reports/local/reviewer-site
python -m http.server 8080 --directory reports/local
```

Visit `http://localhost:8080/reviewer-site/`, or open the generated `index.html`
directly. Direct-file storage support depends on browser policy. The
`factoryguard-reviewer-site` CI artifact contains this complete static site.

`node scripts/verify_reviewer_workflow.cjs` runs the actual browser workflow after
building (requires Playwright 1.62.1 and its Chromium). It starts a static server
automatically. CI runs Windows/Ubuntu tests, browser checks, demos and export.
An isolated local check on 2026-11-09 used Playwright 1.58.2 with installed Chrome
and passed direct-file opening; this does not generalize to every managed browser.
For the optional assistant, use `.venv/bin/python scripts/start_assistant.py` (offline
fixture default). To use an unoccupied separate port:
`FACTORYGUARD_ASSISTANT_PORT=8786 .venv/bin/python scripts/start_assistant.py`, then
open `http://127.0.0.1:8786/`. No question is automatically submitted.

`scripts/verify_reviewer_redesign.cjs` requires a health-confirmed offline service
and checks desktop/tablet/mobile, five-step guidance, suggestion no-submit behavior,
captured question/scope, selected-channel charts, fixture and mocked-generated
labels, citations/focus, queue filters, unavailable/loading/cancel/error states and
static-file use. Browser processes receive no provider key. Use
`FACTORYGUARD_SCREENSHOT_DIR` to keep screenshots under ignored `reports/local/`
rather than overwrite historical documentation screenshots.
The 2026-11-10 Layout 3 checks also cover parallel desktop columns, revealed-only
rail/filter behavior, every architecture node's explanation/example/source link,
keyboard focus return, future/unverified labels and zero diagram submissions.
Captures and the credential-free record are under `reports/local/layout3/`;
see [Layout 3 verification](results/assistant-v1/layout3.md).

Regeneration of the pinned snapshot requires the original release-v3 artifacts:
export the verified workspace, then run
`python scripts/freeze_reviewer_source.py EXPORT.html`. This compares against
saved ledgers and fails on missing files. Routine site builds use only committed
derived results. Do not regenerate data or refit models merely to publish docs.

## Publication maintenance

Publication is separate from CI artifacts and documentation. The Pages workflow
has a manual dispatch with explicit `PUBLISH` authorization and the `github-pages`
environment. Future updates require owner authorization; this documentation task
does not redeploy, enable Pages, change visibility, merge or publish a release.
GitHub Pages plan/access policies must be checked before any visibility change.
[Desktop screenshot](images/reviewer-desktop.png) · [Mobile screenshot](images/reviewer-mobile.png).
