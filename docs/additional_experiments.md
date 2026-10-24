# Additional Paderborn experiments — acquisition report

This records the 2026-10-22 integrity/structural acquisition stage. The
subsequently authorized [B02/B04 development assessment](development_assessment.md)
adds full signal validation/features for those development runs only. B03
remains held out and was not opened in that assessment.

## Reconciled starting inventory

Before this expansion, the complete local download was **B01.zip (965,866,495 bytes)** plus the **description PDF (2,766,702 bytes)** and record metadata. B01 was already safely extracted and had 377 MAT recordings / 380 total files. Its ZIP/PDF published checksums and 380 source SHA256 hashes were reverified; no previously verified file was redownloaded. The original B01 extraction.json was preserved.

The 49 entries in official record.json describe remote availability, not 49 expected local downloads or an incomplete collection. The prior B01 download was complete for its authorized scope.

## Selected and verified downloads

Selection and roles were written in [experiment_roles.md](experiment_roles.md) and configs/dataset_roles.json before new signal inspection. The unchanged role plan is also saved beside the data as role_plan.json (SHA256 2c7351e8be67095c89c4691ae29178c8f1095eba4a3fc85636e7e677e4ab176e). Source: [Zenodo record 10868257](https://zenodo.org/records/10868257), DOI 10.5281/zenodo.10868257; description PDF March 25, 2024 v2, pp. 3–8, and the retained official metadata. The dataset is CC BY 4.0; attribution/citation details remain in dataset_assessment.md.

| Run | Predeclared role | Download bytes | Published MD5, matched | Extracted bytes | MAT headers / each CSV rows |
| --- | --- | ---: | --- | ---: | ---: |
| B02 | Development, matched conditions | 2,725,517,006 | `a75354d8e41eee9b6adf55f0f6c532a8` | 3,096,702,516 | 1,116 |
| B03 | **Held-out reserve: integrity/structure only** | 1,463,649,321 | `6c16eaa8d837b31da69fab1675521ddb` | 1,667,777,017 | 614 |
| B04 | Development, broader speed/load | 2,844,244,761 | `9d7c11dc6a83424b440ae6d184064dcb` | 3,214,822,752 | 1,114 |

New compressed bytes: **7,033,411,088**. New extracted bytes: **7,979,302,285**. Including reused B01, the four ZIPs total **7,999,277,583 bytes**. This is a selected subset, not the 152 GB collection. No B05–B17 archives were downloaded.

B02 matches B01’s documented 128 kHz, 1.6 s, A/C measurement family, 2 Hz sinusoidal loading and 2400–3000 rpm / 3300–3800 N static / 500–1400 N dynamic set ranges. B04 retains the acquisition family while extending set ranges to 1500–3000 rpm / 2500–3800 N static / 500–1500 N dynamic. B03 is a separate matched-condition run reserved before viewing signals. These are distinct experiments on the same laboratory platform, not independent plants or proof of domain generalization.

The public PDF lists vibration termination for B02/B04 and temperature termination for B03. Those descriptions are clearer than B01’s conflicting criterion, but exact statistics, per-run calibration, clock semantics and event times remain unverified. B05 was deferred because it was deliberately interrupted; cheaper B12 changes sample rate to 64 kHz and excitation to Gaussian noise. No runs were selected based on attractive feature behavior.

## Validation performed and held-out boundary

All three ZIP sizes and published MD5 checksums matched. Safe extraction preflighted paths, links, destination collisions, uncompressed size and free disk space, and checked member CRCs while copying into new directories. Final reconciliation checked the size and CRC of **all 3,233 extracted files across B01–B04** against their original archives after structural validation. Raw files and original archives remain outside Git.

For the 2,844 additional MAT files, only headers were interpreted: both A/C channels and measTime exist as double column vectors of shape (204800, 1), with consecutive documented measurement IDs. Each experiment’s temperature and operating CSV has the expected headers and row count, finite numeric cells, unique increasing timestamps, and exact cross-table timestamp alignment. No precomputed feature file was found in the additional archive root inventories.

**No new-run waveform values, signal trends, feature distributions, operational ranges, or endpoint outcomes were inspected.** This includes development B02/B04 in this acquisition step. Held-out B03 remains restricted to integrity/structure: no exploratory plots, extrema/RMS/kurtosis, feature selection, normalization or other model-guiding analysis. MAT sample values/finiteness and relative time-grid values have not been validated; header success must not be described as complete signal-quality validation. The B01 loader remains B01-specific.

No models, fitted normalization, alarm tuning, failure labels or RUL targets were created. One proposed held-out run is a limited reserve, not an established evaluation protocol. Per-run logs/calibration and endpoint interpretation need a separately scoped review, with B03’s held-out boundary preserved.

## Storage and provenance

All dataset files are under `/workspace/datasets/paderborn-10868257/`:

- ZIPs: `B01.zip`, `B02.zip`, `B03.zip`, `B04.zip`; extracted runs: `raw/B01` through `raw/B04`.
- `download_manifest.json`: consolidated actual local inventory, official URLs, exact sizes/checksums, roles, structural scope and final raw CRC counts.
- `B02.download.json`, `B03.download.json`, `B04.download.json`: original transfer receipts, UTC verification times, published MD5 and local archive SHA256.
- `B02.structure.json`, `B03.structure.json`, `B04.structure.json`: header/CSV checks, extraction sizes, limitations and per-file raw SHA256 hashes.
- `initial_inventory_expansion.json`, `role_plan.json`, `record.json`: starting inventory, predeclared roles and original official source catalog. B01’s original extraction.json is retained.

About **15.8 GiB** remained free after validation. No archive or extracted measurement is staged in Git. Only code, role configuration and documentation were added in the checkout.

Reproduction helper: `scripts/acquire_selected_paderborn.py --download B02` (or B03/B04) verifies/reuses a completed archive and preserves its original receipt. `--validate B02` safely extracts into a fresh directory or checks/reuses the existing raw copy, then performs structural checks only. `--manifest` reconciles all four archives against raw bytes. Use the existing `.venv/bin/python`; do not rerun the old B01 preparation command merely to populate the full remote catalog.

## Review evidence

The [B01 feature review](b01_feature_review.md) contains verified feature/missingness findings and gap-preserving histories; its plots contain **B01 only**. The complete test suite now has **50 passing tests**, including generated-fixture safeguards against redownloading a verified archive and against loading held-out waveform values during structural validation. No additional experiment was used to revise B01 bins or feature definitions.
