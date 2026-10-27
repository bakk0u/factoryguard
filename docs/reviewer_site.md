# Recorded-results website

Dashboard: <https://bakk0u.github.io/factoryguard/>.
The owner reports successful [Pages publication](https://github.com/bakk0u/factoryguard/actions/runs/40520283007).
The release-documentation environment cannot reach the host, so public populated
results, navigation, report download and the deployed source commit remain
unverified here. See [verification record](release_verification.md).

## Review workflow

**Overview** explains the problem, experiment roles and saved model comparisons.
**Explore an experiment** opens populated charts; optional reset/play/step controls
reveal a precomputed replay. Inspect a chart, slider or keyboard-accessible history
row, select period boundaries and review evidence alongside operating conditions.
**Methods and evidence** contains filterable full results, coverage and provenance.
Commanded values are optional. Matching coarse bins does not prove identical
conditions. References are development distributions, not healthy ranges.

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
Local managed Chromium blocks file URLs; CI requires the direct-file check.

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
