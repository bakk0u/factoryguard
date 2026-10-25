"""Bounded-memory B01 inspection; descriptive statistics, no model or labels."""
import argparse
import csv
from datetime import datetime, timezone
import json
from pathlib import Path
from factoryguard.util import peak_rss_mib
import time

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from factoryguard.data.paderborn import (
    B01Experiment, G_PER_VOLT, SAMPLE_COUNT, SAMPLE_RATE_HZ,
    TEMPERATURE_COLUMNS, load_recording,
)


def inspect_b01(root: Path, output: Path) -> dict:
    output = Path(output)
    if output.exists() and any(output.iterdir()):
        raise ValueError("Inspection output must be new or empty")
    output.mkdir(parents=True, exist_ok=True)
    started = time.perf_counter()
    report = {
        "dataset_doi": "10.5281/zenodo.10868257", "experiment": "B01",
        "source_kind": "real laboratory run-to-failure experiment",
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "model_trained": False, "model_evaluated": False, "labels_inferred": False,
        "sample_rate_hz": SAMPLE_RATE_HZ, "samples_per_recording": SAMPLE_COUNT,
        "raw_vibration_unit": "V", "log_conversion_g_per_volt": G_PER_VOLT,
        "validation_scope": "inventory, required channels, shapes, finite values and sample/time structure; not physical suitability or failure-label validity",
        "timestamp_timezone": "unspecified; source times kept naive",
        "mat_to_csv_alignment": "M identifier to CSV row by ordinal position only; not independently timestamp-verified",
        "errors": [], "warnings": [
            "General PDF and B01 log disagree on termination criterion; no failure target inferred.",
            "Log end time (09:13) disagrees with CSV acquisition ending at 10:59:32.",
            "Precomputed features mentioned by the PDF are absent from B01.zip.",
        ],
        "files_inspected": 0, "vibration_samples_per_channel": 0,
    }
    try:
        experiment = B01Experiment(root)
        times = experiment.temperatures["source_time"]
        intervals = times.diff().dt.total_seconds().dropna()
        report.update(
            temperature_rows=len(times), operating_rows=len(experiment.operating),
            first_source_time=str(times.iloc[0]), last_source_time=str(times.iloc[-1]),
            elapsed_source_seconds=float((times.iloc[-1] - times.iloc[0]).total_seconds()),
            interval_seconds={"min": float(intervals.min()), "median": float(intervals.median()),
                              "max": float(intervals.max())},
            temperature_ranges_c={c: [float(experiment.temperatures[c].min()),
                                      float(experiment.temperatures[c].max())]
                                  for c in TEMPERATURE_COLUMNS},
            operating_ranges={c: [float(experiment.operating[c].min()),
                                  float(experiment.operating[c].max())]
                              for c in experiment.operating.columns if c not in ("Time", "source_time")},
        )
        # Deliberate warm-up is in the B01 log: do not reject it against main-run ranges.
        report["warmup_set_speed_750rpm_rows"] = int(experiment.operating["setSpeed / rpm"].eq(750).sum())
        operating = experiment.operating
        warmup = (operating["setSpeed / rpm"].eq(750) & operating["setDynLoad / N"].eq(0)
                  & operating["setStatLoad / N"].eq(2500))
        report["setpoints_outside_main_run_ranges_excluding_documented_warmup"] = {
            column: int((~warmup & ~operating[column].between(low, high)).sum())
            for column, low, high in (("setSpeed / rpm", 2400, 3000),
                                      ("setStatLoad / N", 3300, 3800),
                                      ("setDynLoad / N", 500, 1400))}
        if any(report["setpoints_outside_main_run_ranges_excluding_documented_warmup"].values()):
            report["warnings"].append("Non-warmup setpoints exceed documented operating ranges; retained unchanged for investigation.")
        report["gaps_over_24_seconds"] = [
            {"after_csv_row_1_based": int(i), "seconds": float(intervals.loc[i])}
            for i in intervals.index if intervals.loc[i] > 24]
        if intervals.max() > 24:
            report["warnings"].append("Recording gaps exceed 24 s; preserve gaps, do not treat as continuous sampling.")
        rows = []  # bounded small metadata: one statistics row per recording, no signal arrays
        with (output / "recording_statistics.csv").open("w", newline="", encoding="utf-8") as stream:
            writer = None
            for path in experiment.paths:
                try:
                    recording = load_recording(path)
                except (ValueError, OSError, TypeError) as error:
                    report["errors"].append(f"{path.name}: {error}")
                    continue
                row = {"file": path.name, "measurement_id": recording.measurement_id,
                       "source_time_ordinal_association": str(times.iloc[recording.measurement_id - 1])}
                for channel, values in (("A", recording.rear_a_volts), ("C", recording.frontal_c_volts)):
                    row.update({f"{channel}_min_v": float(values.min()),
                                f"{channel}_max_v": float(values.max()),
                                f"{channel}_mean_v": float(values.mean()),
                                f"{channel}_rms_v": float(np.sqrt(np.dot(values, values) / len(values))),
                                f"{channel}_peak_abs_v": float(np.abs(values).max()),
                                f"{channel}_outside_sensor_50g_samples": int((np.abs(values) * G_PER_VOLT > 50).sum())})
                if writer is None:
                    writer = csv.DictWriter(stream, fieldnames=list(row))
                    writer.writeheader()
                writer.writerow(row)
                rows.append(row)
                report["files_inspected"] += 1
                report["vibration_samples_per_channel"] += len(recording.sample_time_seconds)
                del recording, values
        if rows:
            statistics = pd.DataFrame(rows)
            report["outside_sensor_50g_samples"] = {
                channel: int(statistics[f"{channel}_outside_sensor_50g_samples"].sum()) for channel in ("A", "C")}
            if any(report["outside_sensor_50g_samples"].values()):
                report["warnings"].append("Converted sample magnitudes exceed nominal ±50 g sensor range; calibration/saturation needs investigation.")
            _plot_overview(experiment, statistics, output)
            _plot_excerpts(experiment, output)
    except (ValueError, OSError, TypeError) as error:
        report["errors"].append(str(error))
    report["valid"] = not report["errors"] and report["files_inspected"] == 377
    report["elapsed_processing_seconds"] = round(time.perf_counter() - started, 3)
    report["peak_process_rss_mib"] = peak_rss_mib()
    report["memory_strategy"] = "one 204800-sample MAT at a time; retain only per-record statistics and small CSV tables"
    (output / "inspection.json").write_text(json.dumps(report, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    return report


def _plot_overview(experiment, statistics, output):
    times = experiment.temperatures["source_time"]
    elapsed = (times - times.iloc[0]).dt.total_seconds() / 60
    fig, axes = plt.subplots(4, 1, figsize=(12, 12), sharex=True)
    for column in TEMPERATURE_COLUMNS:
        axes[0].plot(elapsed, experiment.temperatures[column], ".", label=column)
    axes[0].set_ylabel("Temperature (°C)")
    axes[1].plot(elapsed, experiment.operating["setSpeed / rpm"], ".", label="Set speed")
    axes[1].plot(elapsed, experiment.operating["meanAbs_speed / rpm"], ".", label="Measured speed")
    axes[1].set_ylabel("Speed (rpm)")
    for column in ("setStatLoad / N", "setDynLoad / N", "meanAbs_statLoad / N", "peak_dynLoad / N"):
        axes[2].plot(elapsed, experiment.operating[column], ".", label=column)
    axes[2].set_ylabel("Load (N)")
    ids = statistics["measurement_id"].to_numpy(dtype=int) - 1
    for channel in ("A", "C"):
        # Points, no connecting line across unrecorded time intervals.
        axes[3].plot(elapsed.iloc[ids], statistics[f"{channel}_rms_v"], ".", label=f"{channel}: 1.6 s RMS")
    axes[3].set_ylabel("Vibration RMS (V)")
    axes[3].set_xlabel("Minutes from first CSV time (MAT association by ordinal position)")
    for ax in axes:
        ax.legend(fontsize="small")
        ax.grid(alpha=0.2)
    fig.suptitle("B01 real laboratory data — inspection only; no failure labels or model")
    fig.tight_layout()
    fig.savefig(output / "overview.png", dpi=140)
    plt.close(fig)


def _plot_excerpts(experiment, output):
    fig, axes = plt.subplots(3, 1, figsize=(12, 8))
    for ax, index in zip(axes, (0, len(experiment.paths) // 2, len(experiment.paths) - 1)):
        recording = load_recording(experiment.paths[index])
        stop = int(0.05 * SAMPLE_RATE_HZ)
        ax.plot(recording.sample_time_seconds[:stop], recording.rear_a_volts[:stop], label="A")
        ax.plot(recording.sample_time_seconds[:stop], recording.frontal_c_volts[:stop], label="C", alpha=0.7)
        ax.set_title(f"M{recording.measurement_id:04d}: first 50 ms, all samples in excerpt")
        ax.set_ylabel("Voltage (V)")
        ax.legend()
        del recording
    axes[-1].set_xlabel("Seconds relative to recording start")
    fig.suptitle("B01 voltage excerpts — not a continuous experiment waveform")
    fig.tight_layout()
    fig.savefig(output / "vibration_excerpts.png", dpi=140)
    plt.close(fig)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("root", type=Path, help="Extracted B01 directory")
    parser.add_argument("--output", required=True, type=Path, help="New/empty output directory")
    args = parser.parse_args()
    report = inspect_b01(args.root, args.output)
    print(json.dumps(report, indent=2))
    return 0 if report["valid"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
