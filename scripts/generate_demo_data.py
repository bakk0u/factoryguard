"""Create reproducible SYNTHETIC demo readings. No actual failure labels."""
from pathlib import Path
import numpy as np
import pandas as pd

def generate(destination: Path) -> None:
    rng = np.random.default_rng(42)
    count = 360
    parts = []
    for index in range(3):
        t = np.arange(count)
        drift = np.maximum(t - 240, 0) / 120 if index == 1 else np.zeros(count)
        parts.append(pd.DataFrame({
            "timestamp": pd.date_range("2026-01-01", periods=count, freq="min", tz="UTC").astype(str),
            "machine_id": f"M{index + 1:03d}",
            "temperature_c": 65 + index * 2 + np.sin(t / 25) + rng.normal(0, .4, count) + 12 * drift,
            "vibration_mm_s": 2 + .1 * index + rng.normal(0, .08, count) + 2 * drift,
            "pressure_bar": 6 + rng.normal(0, .04, count),
            "torque_nm": 120 + index * 5 + rng.normal(0, 2, count),
        }))
    destination.parent.mkdir(parents=True, exist_ok=True)
    pd.concat(parts, ignore_index=True).to_csv(destination, index=False, float_format="%.4f")

if __name__ == "__main__":
    generate(Path(__file__).resolve().parents[1] / "data/raw/demo_sensors.csv")
