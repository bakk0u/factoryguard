# Forecast uncertainty: descriptive audit only

Run from the repository root:

```bash
python scripts/audit_forecast_uncertainty.py --output reports/local/forecast-uncertainty.md
```

The script verifies the pinned `site/source/replay.json` checksum and uses only
saved B01/B02 scored events, with B04 diagnostic-only and B03 sealed. It compares
the selected direction-specific smoothing forecasts with persistence, in volts.

For each run, channel and method, the first chronological quarter of finite
scored absolute errors supplies a fixed nominal-90% two-sided error band.
The remaining errors measure historical coverage. The quantile rule is explicit
in the script and does not look at later errors before setting the width.

**Critical limitations:** the bearings and model family were used during
development selection. Serial measurements are correlated, time gaps and
operating regimes change, and there is no exchangeability, independent held-out
fault truth, or verified 90% conditional coverage. These bounds are an
exploratory *post-selection diagnostic*, not deployable calibrated intervals,
alarm thresholds, probabilities of damage, or maintenance guidance. The script
writes a generated report under ignored `reports/local/`; frozen datasets,
saved predictions, evaluation outputs and alert policies are not modified.

The generation must be executed and the console output checked before
any numerical coverage claim is copied into a release or CV. Earlier informal
coverage estimates must not be presented as reproducible results.
