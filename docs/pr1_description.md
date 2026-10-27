## Recorded bearing investigation and reviewer site

FactoryGuard provides an offline, attributed real-data investigation dashboard:
Overview, experiment exploration, and methods/evidence. B01/B02 development and
uncorrected B04 diagnostic results are preserved; B03 stays sealed.

The reviewer site opens with populated results and provides optional replay,
observed/forecast/persistence vibration histories, thermal and operating context,
quality-aware references, descriptive changes, keyboard inspection, local notes,
and selected-period report downloads. Reports retain the full source manifest,
model/build metadata, and explicitly labelled reference-only versus containing
replay-snapshot hashes. Unknown original producing commit/time remain null.

Period evidence survives presentation changes and invalidates on run, selected
boundaries or revealed-history changes. The overview explicitly summarizes only
the best-performing evaluated variant per family; 12.83% remains equal-run/channel
development-selection MAE improvement, not independent final-test performance.
Every evaluated variant and qualification remains available.

## Verification and handover

- 116 Python tests passed, including exact preservation of all 2,607 observations,
  predictions, errors and all 432 saved comparison rows.
- Hosted desktop/mobile browser regression checks cover selection, presentation
  changes, reset/replay/full history, keyboard focus, isolated notes, deletion,
  legacy export, blocked storage, full browser restart and downloaded provenance.
- CI runs Windows/Ubuntu checks and uploads `factoryguard-reviewer-site` as a
  complete extract-and-open site, with no visitor Python/API/CDN requirement.
- Final remote CI verification remains pending through the connected integration.
  Direct `file://` testing is blocked by the local managed Chromium policy; the
  check remains mandatory in CI (no policy skip in CI).
- Screenshots: `docs/images/reviewer-desktop.png`, `docs/images/reviewer-mobile.png`.

The site remains unpublished. No merge, visibility change, new data, retraining,
raw modification, B04 correction or B03 access. Ready for final review after CI;
publication requires separate authorization under `docs/reviewer_site.md`.
