"""Contract for the demo CSV. Limits are illustrative, not safety thresholds."""
SENSORS = {
    "temperature_c": ("Temperature (°C)", -40, 200),
    "vibration_mm_s": ("Vibration RMS (mm/s)", 0, 100),
    "pressure_bar": ("Pressure (bar)", 0, 100),
    "torque_nm": ("Torque (N·m)", 0, 10000),
}
REQUIRED_COLUMNS = ["timestamp", "machine_id", *SENSORS]
EXPECTED_INTERVAL_SECONDS = 60
