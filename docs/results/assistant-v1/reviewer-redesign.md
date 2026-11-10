# Reviewer dashboard redesign — local verification

Implemented 2026-11-09 on local master based at `c23c79d`, preserving the earlier
uncommitted assistant/configuration/diagnostic/optimization changes. No branch
switch, push, merge or deployment. The public website and historical documentation
screenshots are not claimed to show this local version.

## What changed

- **Start here** is the default. A plain-language introduction explains bearings,
  recorded laboratory data and operating/measurement context. One blue primary
  action starts a walkthrough; exploration, methods and GitHub are secondary.
  Three verified facts are computed from the pinned snapshot/selection artifacts:
  2,607 observations, two development bearing runs (B04 diagnostic separate),
  12.83% equal-run/channel development MAE improvement. Held-out/fault accuracy
  and validated machine-health diagnosis are explicitly not claimed.
- **Five-step deterministic guidance**, B01/A positions 1–3 with visibility 3:
  measured RMS → dip/partial recovery → temperature/speed/load context → warm-up,
  missing references/preceding gap/timing limits → bounded conclusions. Actual
  pinned values are used; no anomaly, label or causal verdict is manufactured.
  It resets and reveals existing replay data, not machinery or a forecasting fit.
  Guidance is labelled deterministic, with no saved AI answer substituted.
- **Measurements + assistant** share a desktop workspace. On small screens the
  assistant follows the measurement plots before notebook/history/queue. Period
  controls and experiment/channel/as_of are visible. Selected channel drives both
  the primary RMS plot and error curve; other/context charts remain expandable.
  Suggestions populate the question without submitting. A static export clearly
  marks generation unavailable but keeps guidance, suggestions, replay and reports.
- **Readable answers** separate observations, possible explanations and uncertainty/
  limitations; captured question/scope and fixture versus newly generated labels
  remain explicit. Citation buttons open exact matching evidence with relevant
  values/units, source text/path/hash and full record detail. The focusable panel
  opens at its heading, scrolls internally, closes with Escape and restores trigger
  focus. Technical traces stay expandable.
- **Deeper exploration** preserves notes, isolated/legacy storage, exports,
  replay/history/hover, optional commanded values and all 432 comparison rows.
  A source-backed notice queue adds search/type filters over revealed observations,
  honestly caps displayed matches at 30 and never calls notices confirmed faults.
  Methods explain repeat-last versus smoothing and development selection;
  Engineering links existing documentation/evaluation evidence and lists unverified
  safeguards without presenting the system as production-ready.
- **Visual direction** follows the supplied reference hierarchy: midnight
  `#02070A`, blue `#0297DE`, orange `#FC734D`, a restrained industrial rail/workspace,
  readable spacing and an original inline bearing SVG. Orange denotes attention
  to interpretation/quality, not confirmed danger. No external fonts/images/CDN.
  Focus visibility, keyboard controls, reduced motion and responsive layout are
  included. The supplied screenshot's browser chrome/private tabs were not copied.

## Canonical source and boundaries

The existing HTML replay/chart engine is
`src/factoryguard/release/dashboard.html`. `site/reviewer.js` continues to own
notebook/exploration enhancements. New `site/reviewer_experience.js` and
`site/reviewer.css` implement the hierarchy/theme. `scripts/build_reviewer_site.py`
inlines those sources into the portable export; no generated-only patch is used.
CSS is freshness-hashed without pretending it has AST graph symbols.
`assistant/web/assistant.js` upgrades the same markup through the existing API.
No frontend framework/router, provider SDK or application dependency was added.

Backend request validation, scope/cursor/channel gates, RAG/MCP, citations,
configured model, dotenv precedence, offline default, explicit live opt-in and
request/tool/turn/output/time/retry bounds remain. A small loading-state fix keeps
Cancel disabled until a request ID exists; pending/lost-ack and duplicate guards
remain. Citation formatting and shared markup do not change evidence. Direct
site builds now also explicitly strip provider credentials from their Git child;
browser test children and static-server children receive sanitized environments.
Tests use fake keys, not private configuration. No key was displayed or copied
into browser assets/screenshots. No live model investigation or paid smoke ran.

No saved forecasting results, raw data, feature/model code, dataset roles, source
manifest or pinned replay/comparison data changed. B03 was not accessed. The
standard suite's small synthetic fixture fits are verification, not real-data
retraining. A public static snapshot is still not an access-control boundary.

## Verification

Local runtime: Python 3.12.16, Node 24.22.1. Isolated browser tooling was installed
under ignored `.tools/browser` (Playwright 1.58.2), using the existing installed
headless Google Chrome; application npm locks were not changed. The verification
service is explicitly offline at `http://127.0.0.1:8786/`, separate from any earlier
live service. Browser scripts require offline health before submitting a fixture.

- TypeScript build and **41 TypeScript tests passed**, no failures/skips.
  Updated DOM regression covers suggestion no-submit, captured scope, distinct
  generated label and correct citation-panel record. Existing configuration,
  adversarial scope, fake-secret, cancellation, duplicate and MCP tests still pass.
- **144 Python tests passed**, no errors/skips, including a new canonical-source/
  static-generation/build-child-secret-boundary check. Pinned build checks preserve
  all 2,607 events, model settings and all 432 saved comparison rows exactly.
- All **40 frozen retrieval cases passed**, with unchanged case manifest and
  existing lexical metrics. No hybrid retrieval/model quality evaluation is claimed.
- Existing `verify_reviewer_workflow.cjs` passed in real Chrome: keyboard/history,
  replay/period controls, run switching, downloaded report provenance, note
  isolation/legacy export/deletion, blocked storage, persistent-profile restart,
  mobile layout, subpath and **direct-file opening**. Selectors/expander setup, optional screenshot destinations and sanitized child
  environments changed for the new layout; numerical and
  persistence assertions were retained.
- Existing `assistant/test/browser.cjs` passed with real MCP/Python retrieval and
  the deterministic offline fixture: channel C/period 1–8, answer rendering,
  citations, legacy report and desktop/mobile. It now refuses a live-mode service.
- New `verify_reviewer_redesign.cjs` passed in real Chrome: default Start view;
  keyboard focus/activation; all five guidance steps; exact B01/A 1–3/as_of=3;
  no automatic POST; suggestion population; selected-channel chart switching;
  explicit fixture question/scope transmission; exact citation record/source/hash;
  Escape/focus return; queue filters; methods/engineering; no horizontal overflow
  at 1440/1024/390 widths; mobile measurement→assistant→notebook order; reduced
  motion; direct-file static walkthrough/unavailable state; and mocked loading,
  cancellation, failure and newly-generated-answer paths. Primary button text
  contrast was checked against the 4.5:1 threshold. No page errors or unexpected
  external requests were observed in the recorded checks.
- Syntax, whitespace and local code-only Graphify update/freshness checks passed.
  The macOS temporary-directory symlink issue in a standalone context-test run was
  resolved by the established `TMPDIR=/private/tmp` test environment; no assertion
  was weakened.

The screenshots demonstrate browser rendering and fixture/mock interactions,
not real-model answer quality. Local logs and `browser-verification.json` are
under ignored `reports/local/redesign/`; representative captures include
`start-desktop.png`, `start-mobile.png`, `guide-desktop.png`, `guide-mobile.png`,
`assistant-desktop.png`, `assistant-mobile.png`, `citation-desktop.png`.
Historical `docs/images/` captures were preserved.

## Startup and remaining limits

From the repository root, after dependencies are installed:

```bash
FACTORYGUARD_ASSISTANT_PORT=8786 .venv/bin/python scripts/start_assistant.py
```

Open **http://127.0.0.1:8786/**. This is the offline fixture default. Click the
walkthrough action without submitting any assistant question. A static alternative:

```bash
.venv/bin/python scripts/build_reviewer_site.py --output reports/local/reviewer-site
```

Open `reports/local/reviewer-site/index.html`; new generation is visibly unavailable.
No API key is needed by either the walkthrough or the offline fixture.

Remaining: no live-model/browser investigation was performed for this redesign;
newly-generated/error/cancel UI checks use mocks. Broader answer entailment and
prompt-injection evaluation, hybrid retrieval validation and independent human
review remain. Chrome was tested locally, not Firefox/Safari or a new remote CI
run; this is not a full WCAG/screen-reader/security certification. External
documentation links target existing GitHub documents; offline exports cannot open
them without connectivity. Deployment has not been updated. Restricted hosting
still needs authentication/TLS, trusted origins/CSRF review, spending/concurrency
controls, durable idempotency, secret/evidence/egress isolation and trace retention.
