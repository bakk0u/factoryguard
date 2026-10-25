# Development-release limitations

- B01/B02 are inspected development runs and only two independent bearings.
  Burst counts do not supply independent experimental replication. Outer results
  select methods and therefore are not final unbiased performance estimates.
- B04's measured speed/load interpretation remains unresolved; the application
  preserves it as recorded and makes no loaded-condition comparability claim.
  B03 remains sealed pending the user's pipeline review and later authorization.
- Ordinal CSV/MAT association is provisional; source clocks have unknown event
  semantics/timezone. Forecast horizon is next observed burst, not fixed seconds
  or operating time. Gaps are retained and forecasts expire after the fixed rule.
- Sensor range, calibration and bandwidth limit physical interpretation. Volts
  and flags are preserved; 10 g/V is documented, not silently applied/corrected.
  Warm-up is a regime, not a healthy reference. Endpoints do not support RUL.
- Sparse/unsupported measured bins have no reliable contextual comparison.
  Even supported bins describe development measurements with unknown health,
  changing thermal/vibration states and correlated observations. Quartiles are
  not safety limits. No alarm thresholds or fault precision/recall are calibrated.
- Smoothing can follow a gradual rise with small error. A level-change view helps
  investigation, but neither its synthetic acceptance test nor lower MAE proves
  fault detection. No maintenance action should be inferred from this prototype.
- The runtime is local offline replay, with one shared cursor per experiment and
  no authentication/live connector. Portable HTML embeds all future replay events
  and does not persist progress. It is not a deployed sensor service.
- Pinned Python packages improve reproducibility but do not pin every OS library
  or wheel hash. Linux is exercised locally; Windows verification depends on CI.
  Joblib artifacts must come from a trusted source and matching environment.
- B03's executable procedure is prepared and tested on generated data only. Its
  actual measurement-meaning gate may fail. One future reserve case cannot establish
  population performance. One-shot use requires review discipline; a CLI flag is
  not a tamper-proof authorization system.
