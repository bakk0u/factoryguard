"""Milestone 1: load, validate, summarise and plot. No training yet."""
from pathlib import Path
import hashlib
import json
import pandas as pd
from ..data.ingest import load_csv
from ..data.schema import SENSORS
from ..data.validate import validate_readings
from ..evaluation.plots import plot_readings

def run_step1(input_path: Path, output_dir: Path, source_kind: str = "user-provided") -> dict:
    input_path, output_dir = Path(input_path), Path(output_dir)
    # A fresh directory prevents stale plots being confused with a failed run.
    if output_dir.exists() and any(output_dir.iterdir()):
        raise ValueError(f"Output directory is not empty; choose a new --output: {output_dir}")
    output_dir.mkdir(parents=True, exist_ok=True)
    frame = load_csv(input_path)
    validation = validate_readings(frame)
    (output_dir / "validation.json").write_text(json.dumps(validation, indent=2), encoding="utf-8")
    if not validation["valid"]:
        raise ValueError("Validation failed. See " + str(output_dir / "validation.json"))
    times = pd.to_datetime(frame["timestamp"], utc=True, format="ISO8601")
    summary = {
        "source_kind": source_kind,
        "input_file": input_path.name,
        "sha256": hashlib.sha256(input_path.read_bytes()).hexdigest(),
        "rows": len(frame), "machines": validation["machines"],
        "start_utc": times.min().isoformat(), "end_utc": times.max().isoformat(),
        "sensor_statistics": frame[list(SENSORS)].apply(pd.to_numeric).describe().to_dict(),
        "model_trained": False,
    }
    (output_dir / "summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    plot_readings(frame, output_dir / "sensor_readings.png")
    return summary
