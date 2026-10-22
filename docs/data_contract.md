# Milestone 1 data contract
One row represents one machine reading. Required CSV headers:
`timestamp,machine_id,temperature_c,vibration_mm_s,pressure_bar,torque_nm`.
Timestamps must be ISO 8601; explicit UTC offsets are recommended. Naive timestamps
are interpreted as UTC. Records must be chronological within each machine.
Machine/timestamp pairs must be unique. IDs must not be missing or blank.
Sensors must be finite numbers with no missing values in milestone 1.
Demo admissible ranges: temperature -40..200 °C, vibration RMS 0..100 mm/s,
pressure 0..100 bar, torque 0..10000 N·m. These are illustrative validation
bounds, not engineering limits or alert thresholds. Change the contract for a
real dataset after checking units and machine specifications.
Expected cadence is 60 seconds; irregular intervals produce warnings.
Extra columns are allowed and ignored. There is no label column yet.
Validation does not silently sort, drop records, impute or overwrite raw data.
