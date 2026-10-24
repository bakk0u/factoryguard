"""Stream authorized development bursts using the original B01 feature definitions."""
import argparse
import csv
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import resource
import time

import numpy as np
import pandas as pd

from factoryguard.data.paderborn import (
    B01Experiment, DevelopmentExperiment, SAMPLE_COUNT, SAMPLE_RATE_HZ, TEMPERATURE_COLUMNS,
    load_recording, require_development,
)
from factoryguard.features.b01 import channel_features, feature_schema


def raw_manifest(root: Path) -> dict[str, str]:
    """Hash source files in bounded chunks; reject links rather than follow them."""
    result = {}
    for path in sorted(Path(root).rglob("*")):
        if path.is_symlink():
            raise ValueError(f"Unexpected raw-data link: {path}")
        if path.is_file():
            digest = hashlib.sha256()
            with path.open("rb") as stream:
                for chunk in iter(lambda: stream.read(1024 * 1024), b""):
                    digest.update(chunk)
            result[path.relative_to(root).as_posix()] = digest.hexdigest()
    return result


def burst_rows(experiment: B01Experiment, source_hashes: dict):
    """Only the current burst, its table row and previous context affect output."""
    previous_time, previous_warmup, segment = None, None, 0
    for index, path in enumerate(experiment.paths):
        # Do not advance a recording generator while retaining its prior arrays.
        recording = load_recording(path, experiment=experiment.experiment)
        temp = experiment.temperatures.iloc[index]
        operating = experiment.operating.iloc[index]
        now = temp["source_time"]
        gap = None if previous_time is None else float((now - previous_time).total_seconds())
        gap_flag = gap is not None and gap > 24
        segment += int(gap_flag)
        warmup = bool(operating["setSpeed / rpm"] == 750
                      and operating["setStatLoad / N"] == 2500
                      and operating["setDynLoad / N"] == 0)
        row = {
            "provenance__dataset_doi": "10.5281/zenodo.10868257",
            "provenance__experiment": experiment.experiment,
            "provenance__measurement_id": recording.measurement_id,
            "provenance__mat_file": path.relative_to(experiment.root).as_posix(),
            "provenance__mat_sha256": source_hashes[path.relative_to(experiment.root).as_posix()],
            "provenance__source_time": temp["Time"],
            "provenance__timezone": "unspecified",
            "provenance__ordinal_alignment_provisional": True,
            "provenance__timestamp_meaning": "unknown_start_or_end",
            "provenance__feature_availability": "complete_burst_only_absolute_time_provisional",
            "provenance__sample_rate_hz": SAMPLE_RATE_HZ,
            "provenance__sample_count": SAMPLE_COUNT,
            "provenance__burst_duration_s": SAMPLE_COUNT / SAMPLE_RATE_HZ,
            "feature__T1_above_room_c": float(temp[TEMPERATURE_COLUMNS[0]] - temp[TEMPERATURE_COLUMNS[2]]),
            "feature__T2_above_room_c": float(temp[TEMPERATURE_COLUMNS[1]] - temp[TEMPERATURE_COLUMNS[2]]),
            "context__measured_speed_rpm": float(operating["meanAbs_speed / rpm"]),
            "context__measured_static_load_n": float(operating["meanAbs_statLoad / N"]),
            "context__measured_dynamic_peak_n": float(operating["peak_dynLoad / N"]),
            "context__set_speed_rpm": float(operating["setSpeed / rpm"]),
            "context__set_static_load_n": float(operating["setStatLoad / N"]),
            "context__set_dynamic_amplitude_n": float(operating["setDynLoad / N"]),
            "context__T1_c": float(temp[TEMPERATURE_COLUMNS[0]]),
            "context__T2_c": float(temp[TEMPERATURE_COLUMNS[1]]),
            "context__room_c": float(temp[TEMPERATURE_COLUMNS[2]]),
            "quality__preceding_csv_gap_s": gap,
            "quality__preceding_gap_unknown": gap is None,
            "quality__preceding_gap_gt24s": gap_flag,
            "quality__acquisition_segment": segment,
            "quality__documented_warmup_setpoints": warmup,
            "quality__warmup_regime_transition": previous_warmup is not None and warmup != previous_warmup,
        }
        ranges = (
            ("speed", "setSpeed / rpm", 2400, 3000),
            ("static_load", "setStatLoad / N", 3300, 3800),
            ("dynamic_load", "setDynLoad / N", 500, 1400),
        )
        if experiment.experiment == "B04":
            # Log p1 defines alternatives; p2 records Thigh selection at 13:45.
            # Before that recorded decision, only the union is defensible.
            decided = now >= pd.Timestamp("2021-11-17 13:45:00")
            ranges = (("speed", "setSpeed / rpm", 1500, 3000 if decided else 3600),
                      ("static_load", "setStatLoad / N", 2500, 3800),
                      ("dynamic_load", "setDynLoad / N", 500, 1500 if decided else 1700))
            row["quality__initial_setpoint_policy_ambiguous"] = not decided and not warmup
        for name, column, low, high in ranges:
            row[f"quality__{name}_setpoint_outside_main_range"] = bool(
                not warmup and not low <= operating[column] <= high)
        for channel, values in (("A", recording.rear_a_volts), ("C", recording.frontal_c_volts)):
            features = channel_features(values)
            for name in ("ac_rms_v", "crest_factor", "excess_kurtosis"):
                row[f"feature__{channel}_{name}"] = getattr(features, name)
            row.update({
                f"quality__{channel}_dc_mean_v": features.dc_mean_v,
                f"quality__{channel}_raw_peak_abs_v": features.raw_peak_abs_v,
                f"quality__{channel}_outside_sensor_50g_samples": features.outside_sensor_range_samples,
                f"quality__{channel}_sensor_range_exceeded": features.outside_sensor_range_samples > 0,
                f"quality__{channel}_zero_variance": features.zero_variance,
                f"quality__{channel}_crest_factor_undefined": features.zero_variance,
                f"quality__{channel}_excess_kurtosis_undefined": features.zero_variance,
            })
        row["quality__any_warning"] = bool(
            gap_flag or warmup or row["quality__warmup_regime_transition"]
            or row.get("quality__initial_setpoint_policy_ambiguous", False)
            or any(row[f"quality__{name}_setpoint_outside_main_range"]
                   for name in ("speed", "static_load", "dynamic_load"))
            or any(row[f"quality__{c}_{name}"] for c in ("A", "C")
                   for name in ("sensor_range_exceeded", "zero_variance")))
        previous_time, previous_warmup = now, warmup
        del recording, values
        yield row


def extract_b01(root: Path, output: Path, *, expected_measurements: int = 377,
                make_plots: bool = True, experiment_id: str = "B01") -> dict:
    """The CLI requires full B01; expected_measurements supports generated tests."""
    require_development(experiment_id)
    root, output = Path(root).resolve(), Path(output).resolve()
    if output == root or root in output.parents:
        raise ValueError("Feature output must be outside raw data")
    if output.exists() and any(output.iterdir()):
        raise ValueError("Feature output must be new or empty")
    experiment = (B01Experiment(root, expected_measurements=expected_measurements) if experiment_id == "B01"
                  else DevelopmentExperiment(root, experiment=experiment_id, expected_measurements=expected_measurements))
    output.mkdir(parents=True, exist_ok=True)
    started = time.perf_counter()
    before = raw_manifest(root)
    partial = output / "features.csv.partial"
    rows_written = 0
    with partial.open("x", newline="", encoding="utf-8") as stream:
        writer = None
        for row in burst_rows(experiment, before):
            if writer is None:
                writer = csv.DictWriter(stream, fieldnames=list(row))
                writer.writeheader()
            # CSV has empty cells for undefined moments, never textual zero.
            writer.writerow({k: None if isinstance(v, float) and np.isnan(v) else v for k, v in row.items()})
            rows_written += 1
    after = raw_manifest(root)
    if before != after:
        raise ValueError("Raw source files changed during extraction; only partial output retained")
    if rows_written != expected_measurements:
        raise ValueError("Feature row count does not match required measurement count")
    partial.rename(output / "features.csv")
    frame = pd.read_csv(output / "features.csv")  # small descriptor table only, never waveforms
    schema = feature_schema()
    if experiment_id != "B01":
        schema["schema_version"] = "development-burst-features-v1.1"
        schema["experiment"] = experiment_id
        schema["differences_from_b01"] = "Same features/units/estimators; experiment-specific file inventory and log-based setpoint policy."
    schema.update(
        table_columns=list(frame.columns),
        provenance_columns=[c for c in frame if c.startswith("provenance__")],
        quality_columns=[c for c in frame if c.startswith("quality__")],
        timestamp_format="%d-%b-%Y %H:%M:%S; timezone unspecified",
        gap_policy="Flag preceding CSV interval >24 s; heuristic only, no filling or removal",
    )
    (output / "schema.json").write_text(json.dumps(schema, indent=2) + "\n")
    (output / "raw_integrity.json").write_text(json.dumps({
        "algorithm": "sha256", "all_source_files_unchanged": True,
        "verified_file_count": len(before), "files": before,
    }, indent=2) + "\n")
    if make_plots:
        from factoryguard.features.b01_plots import plot_comparisons
        comparison_summary = plot_comparisons(frame, output)
    else:
        comparison_summary = {"plots_generated": False}
    report = {
        "schema_version": schema["schema_version"],
        "experiment": experiment_id,
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "rows": rows_written, "samples_per_burst": SAMPLE_COUNT,
        "raw_files_unchanged": True, "raw_file_count": len(before),
        "labels_created": False, "normalization_fitted": False, "model_trained": False,
        "quality_flag_counts": {c: int(frame[c].sum()) for c in schema["quality_columns"]
                                if frame[c].dtype == bool},
        "undefined_candidate_cells": int(frame[schema["candidate_input_columns"]].isna().sum().sum()),
        "comparison_summary": comparison_summary,
        "elapsed_seconds": round(time.perf_counter() - started, 3),
        "peak_process_rss_mib_linux": round(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024, 2),
        "warnings": [
            "Ordinal MAT/CSV association and timestamp start/end meaning remain provisional.",
            {"B01": "Termination information conflicts; no failure or RUL labels inferred.",
             "B02": "Log records a stop/continuation and changed crossing-count rule; no event labels inferred.",
             "B04": "Log records RMS termination but omits numeric limit/channel/statistic details; no labels inferred."}[experiment_id],
            "Sensor-range exceedances, suspect setpoints, warm-up and gaps are retained.",
            "Candidate fields are descriptors, not approved model inputs. No fitted normalization.",
        ],
    }
    (output / "extraction.json").write_text(json.dumps(report, indent=2, allow_nan=False) + "\n")
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("root", type=Path, help="Extracted B01 directory")
    parser.add_argument("--output", type=Path, required=True, help="New/empty directory outside raw data")
    args = parser.parse_args()
    try:
        result = extract_b01(args.root, args.output)
    except (ValueError, OSError) as error:
        parser.exit(1, f"Feature extraction failed: {error}\n")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
