# Reviewer site (prepared, unpublished)

Build with `python scripts/build_reviewer_site.py --output reports/local/reviewer-site`.
Open the generated index.html directly, or preview under a Pages-like subpath:
`python -m http.server 8080 --directory reports/local`, then visit
`http://localhost:8080/reviewer-site/`. Visitors need only a browser.

The source manifest pins the explicitly selected release-v3 campaign snapshot by
SHA256, independent of filesystem timestamps. B01/B02 development observations
and B04 diagnostic observations are included, together with direction-specific
selected predictions, settled errors, fixed reference support and every saved
model-comparison metric. B03, raw waveforms, SQLite, model pickles and private
notes are excluded. Data attribution: Osarenren Kennedy Aimiyekagbon, Paderborn
University, DOI 10.5281/zenodo.10868257, CC BY 4.0. Derived descriptors retain
measurement warnings and provisional timestamp semantics.

The original campaign did not record producing commit or generation time.
These remain explicitly unknown. The independently reported d5be7be Windows/Linux
CI identifies verified software, not the original result-generating commit.
The build manifest separately records the website checkout commit. Hashes prove
snapshot consistency, not scientific validity or historical authorship.

The page opens with all observations visible. Reset starts sequential replay.
Notes use browser-local storage; they are neither uploaded nor included in the
published snapshot. Exported investigation reports include chosen notes separately.
No external APIs, CDN scripts, fonts or services are needed. Links to the source
DOI are optional navigation. Historical selection is not unbiased final performance;
reference distributions do not establish healthy ranges. B04 remains uncorrected.

## Publication requires separate authorization

1. Review and authorize publication of these attributed derived results explicitly.
2. Confirm GitHub plan eligibility: Pages works from public repositories on Free;
   private repository Pages requires an eligible paid plan (Pro/Team/Enterprise).
   A private repository does not generally make its Pages website private; confirm
   access policy and any Enterprise access-control options before enabling it.
3. Configure Pages to use GitHub Actions and require a reviewer on the `github-pages`
   environment. Make the workflow available on the default branch through a separately
   authorized review/merge (this task does not merge anything).
4. Manually dispatch `Authorized reviewer Pages publication` with `PUBLISH`, then
   approve the protected environment. It has no push/PR trigger.
5. Verify the actual URL reported by deployment and only then put it at the top of
   README. No live URL is claimed while unpublished.

## Verification of this snapshot

- Exact comparison with saved forecast ledgers: B01 377, B02 1,116 and B04 1,114
  observations and selected forecasts, including nulls and acquisition intervals.
- `python scripts/verify_reviewer_metrics.py`: 432 saved development/stress metric
  rows checked against existing model artifacts, including training partitions,
  with no fits. Requires the original local release-v3 artifacts; visitors do not.
- `python -m unittest discover -s tests -q`: 116 tests passed.
- `node scripts/verify_reviewer_browser.cjs`: populated first load, all experiments,
  Pages subpath, desktop/mobile layout, no console errors or external requests.
- `node scripts/verify_investigation_browser.cjs reports/local/reviewer-site http://127.0.0.1:8777/reviewer-site/`:
  reset, stepping, notes persistence and report content passed.
- [Desktop](images/reviewer-desktop.png) · [Mobile](images/reviewer-mobile.png).

To regenerate the pinned source from the original verified workspace, export it
with the release CLI and run `python scripts/freeze_reviewer_source.py EXPORT.html`.
This explicitly compares against release-v3 ledgers; missing files fail the build
rather than generating substitute measurements. Review and commit changed manifest
hashes deliberately. Routine site builds require only the committed snapshot.

Final-commit remote Windows/Linux CI remains to be checked through the connected
GitHub integration; local GitHub API access returns Forbidden. The earlier verified
CI run applies to d5be7be, not automatically to this website change.
