# Layout 3 and interactive Engineering — local verification

Publication note: this report records the earlier local verification milestone.
Its no-commit/no-push wording describes that milestone. Current source publication
is commit `5469ddf31d617cd40b37b44cfcfe8f72e16f4897`; see `source-manifest.json` and
`verification.json` for the current clean source state and publication checks.

Verified 2026-11-10. Existing checkout: master based at `c23c79d`; earlier dirty
assistant/configuration/optimization work preserved. No branch switch or commit,
push, merge or deployment. Historical verification records and screenshots remain.

## Delivered

- **Layout 3:** compact bearing-brand navigation, wide-screen Attention rail,
  workspace header/queue action, Notice → Evidence → Findings stages, bearing
  illustration and orange interpretation notice. Midnight `#02070A`, Electric
  Blue `#0297DE`, Cantaloupe Orange `#FC734D` retain their roles. The mockup's
  example date/count/status were not fabricated: rail notices come from actual
  revealed observations, with shared search/type filters and evidence inspection.
- **Measurements beside assistant:** parallel desktop columns; stacked at tablet/
  mobile sizes, with measurements before assistant and deeper notebook/history.
  Existing question/scope transmission, suggestions, cancellation, citation panel,
  fixture/generated labels and expandable activity remain. No API contract changed.
- **Less text:** the default Start view has **119 visible words** in the recorded
  desktop browser measurement (panel `innerText`, excluding closed disclosures).
  Measure → Compare → Explain labels, a bearing illustration, actual three-point
  RMS chart, endpoint comparisons and compact limitations replace long paragraphs.
  Full method tables, reference detail, change evidence, timing, model settings and
  attribution remain expandable. No saved numerical evidence was removed.
- **Interactive Engineering:** 14 keyboard/clickable components cover recorded
  data, forecasting, pinned evidence, dashboard, TypeScript orchestration, MCP,
  Python retrieval, RAG/context, optional OpenAI generation, citation validation,
  answer/evidence display and local traces. Every component has a concise
  explanation, concrete example and expandable source/contract. Hosting is marked
  future/unimplemented; optional hybrid retrieval is implemented but unevaluated.
  Selection focuses the explanation; Back to diagram restores component focus.
  Diagram interactions never execute tools, submit questions or call a provider.

Canonical source: existing `release/dashboard.html` and `site/reviewer.js`,
`site/reviewer_experience.js`, `site/reviewer.css`, new `site/layout3.css` and
`site/architecture.js`. `scripts/build_reviewer_site.py` inlines them into the
portable site. Both CSS files participate in context freshness; CSS is not
misrepresented as an AST graph. No frontend framework, remote asset or dependency
was added. `assistant/web/assistant.js` only shortens its status wording here.

## Observed verification

- TypeScript build and **41/41 tests passed**, no failures/skips.
- Full Python suite **144/144 passed**, no failures/skips. Existing small synthetic
  test-fixture fits are not project forecasting-model retraining.
- Frozen lexical retrieval cases **40/40 passed**; unchanged manifest. These are
  documentation/evidence cases, not a new held-out-bearing evaluation.
- Real Chrome, isolated Playwright 1.58.2: **1440 desktop / 1024 tablet / 390 mobile**;
  no horizontal overflow across all views. Desktop parallel columns and mobile
  measurement → assistant → notebook order are asserted geometrically.
- Expanded redesign browser check: all 14 architecture components have matching
  explanations/examples/existing source paths; keyboard focus/return; future and
  unevaluated labels; no diagram submission; direct-file diagram interaction;
  revealed-only rail filtering; stage navigation; exact displayed RMS values;
  B01/A 1–3/as_of=3; suggestion no-submit; captured fixture request question/scope;
  exact evidence/provenance citation panels; Escape/focus return; reduced motion;
  offline/unavailable and mocked loading/cancellation/error/generated states.
- Existing static reviewer browser regression passed: replay, period controls,
  downloaded reports/provenance, notes/legacy/isolation/deletion, blocked storage,
  persistent-profile restart, run switching, keyboard, mobile, subpath/direct-file.
- Existing assistant browser regression passed: real local MCP/Python retrieval,
  offline deterministic fixture, channel C/1–8, answer/citations/report and mobile.
- No page errors or unexpected external requests in the recorded browser checks.
  Syntax, whitespace, Graphify update/freshness and unchanged pinned-source/model/
  result checks passed. A new assertion initially compared lowercase text with a
  CSS-uppercase status; it was corrected to case-insensitive semantic matching.

All generation checks use offline fixtures or intercepted browser mocks, not a
paid model. Browser/test/build children exclude provider credentials. The private
root configuration was not changed or displayed; it remains ignored/untracked
and mode 0600. No B03/raw access, real-data fit, saved forecasting-result change,
model/configuration change or paid request occurred. Original assistant bounds,
server scope gates and credential separation remain in force.

## Local review and artifacts

The offline fixture service is available at **http://127.0.0.1:8786/**. Restart:

```bash
FACTORYGUARD_ASSISTANT_PORT=8786 .venv/bin/python scripts/start_assistant.py
```

Static/keyless build:

```bash
.venv/bin/python scripts/build_reviewer_site.py --output reports/local/reviewer-site
```

Open the generated `index.html`. New generation is visibly unavailable there.
Browser verification script: `scripts/verify_reviewer_redesign.cjs`, configured
with `FACTORYGUARD_SCREENSHOT_DIR=reports/local/layout3` and an offline service.
Local screenshots, logs, retrieval results, source hashes and verification JSON:
`reports/local/layout3/`. Representative screenshots: `start-desktop.png`,
`start-mobile.png`, `guide-notice-desktop.png`, `guide-desktop.png`,
`assistant-desktop.png`, `engineering-desktop.png`, `engineering-mobile.png`.

## Limits

The one-minute comprehension goal has not been measured with unfamiliar users.
No Safari/Firefox or full screen-reader/WCAG audit was run. This verifies browser
operation and deterministic/mocked boundaries, not new real-model answer quality,
prompt-injection robustness or production security. Citation-ID membership does
not prove claim support. Human review, broader answer evaluation, real hybrid
validation and restricted hosting controls remain: authentication/TLS, trusted
origins, spend/concurrency bounds, durable idempotency, secret/evidence isolation
and trace retention. The public deployment has not been changed.
