# Review submission layout3-20261110-5469ddf

Source: [5469ddf31d617cd40b37b44cfcfe8f72e16f4897](https://github.com/bakk0u/factoryguard/commit/5469ddf31d617cd40b37b44cfcfe8f72e16f4897) on `feature/assistant-setup-layout3`, based on `c23c79d8f28559002aeba3579bee6cd9f9807ead`. Source tree matches local authored commit `f1fcc5b` exactly. Tracked worktree is clean; ignored private/local files remain local. `source-manifest.json` lists all 45 feature changes and their SHA256 hashes, plus the 15 dashboard-patch paths.

## Independent review inputs

- [Scoped dashboard patch](dashboard.patch), against the source base above. It includes all required new UI/CSS/architecture files. Backend/setup changes are excluded from this patch but available in the full feature branch; use that complete branch to reproduce the combined integration checks.
- [Approved Layout 3 reference](layout3-reference.png). Owner-supplied design reference, not measured evidence. Its sample dates/counts/sensor warning are not fabricated into the walkthrough. PNG text/EXIF metadata removed; encoded image data unchanged.
- [Desktop entry](start-desktop.png), [mobile entry](start-mobile.png), [guided notice](guide-notice-desktop.png), [mobile guide](guide-mobile.png), [measurements beside assistant](assistant-desktop.png), [mobile assistant](assistant-mobile.png), [Engineering](engineering-desktop.png), [mobile Engineering](engineering-mobile.png), [citation panel](citation-desktop.png).
- [Verification report](verification-report.md), [exact commands/results](verification.json), [compact observed logs](validation-excerpts.txt), [browser checks](browser-verification.json), [image provenance](image-provenance.json), and `SHA256SUMS`.

## Three design requirements

- [x] Layout 3 hierarchy, palette, wide-screen Attention rail and desktop parallel measurements/assistant; actual revealed notices replace illustrative mockup statuses.
- [x] Interactive whole-system architecture: data/forecasting, dashboard, TypeScript, MCP, Python retrieval, RAG/context, optional OpenAI, citations and traces; concrete examples and distinct future/unevaluated states.
- [x] Concise introduction (119 visible words), diagrams/charts/labels and expandable detail. Essential non-diagnosis, development-only, timing/reference and B04 limits preserved. One-minute comprehension is not empirically verified.

## Functional regression coverage

- [x] Suggestions do not submit; captured question/scope equals the outgoing fixture request.
- [x] B01/A 1–3/as_of=3 guide, revealed-only notice rail, selected-channel charts.
- [x] Exact citation record/source/provenance, keyboard/Escape/focus return.
- [x] Offline/unavailable, loading/cancel/error/generated states (fixtures/mocks, not real model).
- [x] Replay, report downloads, isolated/legacy notes, blocked storage and restart.
- [x] Desktop/tablet/mobile geometry, no overflow, static/direct-file map and guide.

No source or visual review by the independent reviewer is claimed yet. READY_FOR_REVIEW means this package is available. `REVIEW.md` remains reviewer-owned. Current owner authorization covers this source push and draft PR; the older handoff language does not authorize a merge or deployment. Remaining quality/security/hosting work is documented, not implemented.

No dotenv files, credentials, environments, raw data, databases, private traces, notes or B03 content are included. Screenshots show offline fixture/mocked UI, not a new live-model answer. Only sanitized artifacts live here; original local records are preserved.
