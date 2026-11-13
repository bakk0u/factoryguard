# Measurement validity review

Scope: acquisition timing, units, operating conditions and the B04 scaling question that
earlier documents left open. Evidence is the dataset description (v2, 25 March 2024), the
per-run logs and the raw waveforms. No forecast or model output was used to reach any
conclusion here, and no measurement was corrected.

## Summary

| Question | Status | Basis |
| :--- | :--- | :--- |
| Vibration units and conversion | **Resolved** | Logs for B01-B04: saved in volts, 10 g/V, 0 dB gain. Features stay in volts |
| Sampling | **Resolved** | 128 kHz, 1.6 s, 204,800 samples; every recording's time grid validated at load |
| B04 logged shaft speed (about half the commanded value) | **Resolved: logging scale artefact** | Raw vibration spectra, below |
| B04 logged dynamic-load peak (about half the commanded amplitude) | **Open, qualified** | No independent evidence in the available signals |
| Burst timestamps | **Open, qualified** | No time zone; MAT files carry only relative time; row association is ordinal |
| Interval between bursts | **Qualified** | "Approximately 12 s"; forecasts are next-observed-burst, not fixed-horizon |
| Why runs ended | **Qualified** | Per-run threshold criterion; B01's sources disagree. Never used as a label |
| Sensor response | **Qualified** | 603C01: ±10% sensitivity, 0.5 Hz-10 kHz at 3 dB, 25 kHz resonance; content above 10 kHz is not flat |

## B04 shaft speed: resolved from the waveforms

**Problem.** In B04 the logged `meanAbs_speed` is 0.499 times the commanded `setSpeed` in
every loaded recording. In B01 and B02 the ratio is 1.003. Documentation does not say which
value describes the physical shaft.

**Independent evidence.** A rotating shaft leaves spectral lines at its rotation frequency
and harmonics in the housing vibration. For each recording,
[`scripts/audit_speed_evidence.py`](../../../scripts/audit_speed_evidence.py) measures how
prominent the lines are at 1x, 3x and 5x a hypothesised frequency (peak over the
surrounding spectrum), and separately searches 8-62 Hz for the frequency whose harmonics
stand out most, with no hypothesis supplied. Odd multiples are used because they are not
shared with a frequency twice as high, which is exactly the ambiguity in question.

**Validation on runs without the problem.**

| Run | Recordings | Line prominence at logged speed | At half the logged speed (control) | Free estimate within 1 Hz of logged speed |
| :--- | ---: | ---: | ---: | ---: |
| B01 | 326 | 60 | 2.6 | 87% |
| B02 | 1,065 | 71 | 3.1 | 100% |

The method finds the shaft where the log says it is, and finds nothing at a wrong frequency.

**B04.**

| Hypothesis for the true shaft frequency | Median line prominence | Free estimate within 1 Hz |
| :--- | ---: | ---: |
| Logged measured speed | **2.5** (same as the no-signal control) | 5.8% |
| Commanded speed (twice the logged value) | **46** | **90%** |
| Half the logged speed (control) | 1.7 | 1.1% |

In none of the 1,064 loaded B04 recordings were the lines at the logged speed more prominent
than at the commanded speed.

**Conclusion.** During B04 the shaft turned at the commanded speed (1500-3000 rpm). The
logged measured speed is under-reported by a factor of two, consistent with a scaling
setting in the acquisition for that run. This is a property of that log column, not of the
vibration or temperature measurements.

**Consequences, stated rather than applied.**

- B04's vibration, temperature and forecasts are unaffected: none of them use logged speed.
- Earlier statements that B04 has "zero loaded-bin overlap" with B01/B02 were produced with
  the logged speed and reflect the artefact. Using commanded speed, B04's 2400-3000 rpm
  operation overlaps the other runs.
- Published B04 results are **not** recomputed or relabelled here. Every B04 row keeps its
  `operating_context_interpretation_unresolved` flag in the saved data, because the
  dynamic-load column is still open and the saved snapshot is hash-pinned. B04 stays a
  diagnostic run.
- Any future use of B04 operating context should take speed from `setSpeed`, cite this
  review, and treat dynamic load as unverified.

## B04 dynamic load: still open

The logged dynamic-load peak is 0.49-0.53 of the commanded amplitude. The 2 Hz load is
outside what the accelerometer chain and a 1.6 s burst can resolve reliably, and the static
load does not share the factor. A peak-versus-peak-to-peak definition or a second scaling
setting are both plausible; neither can be shown from the available data. It remains
flagged, and no result depends on it.

## Timing

The description states a pause of approximately 12 s between 1.6 s bursts. CSV timestamps
have one-second resolution and no time zone. The pipeline therefore treats the series as
ordered bursts, resets history at gaps over 24 s, and reports forecasts as "next observed
burst". Nothing in this project converts burst counts into verified operating hours.

## Reproduce

```bash
python scripts/audit_speed_evidence.py --raw-root /path/to/raw --output docs/results/measurement-validity
```

Reads B01, B02 and B04 waveforms only; refuses B03. Per-recording values are in
`speed_evidence.csv`, the summary in `speed_evidence.json`.
