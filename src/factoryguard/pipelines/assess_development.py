"""Full-burst development assessment. B03 is deliberately absent and denied."""
import argparse
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Patch
import numpy as np
import pandas as pd

from factoryguard.data.paderborn import DEVELOPMENT_COUNTS, require_development
from factoryguard.features.b01_plots import condition_groups
from factoryguard.pipelines.features_paderborn import extract_b01, raw_manifest


RUNS = ("B01", "B02", "B04")


def combined_load_check(run, frame):
    """Documented command bounds; 1e-8 N tolerance is CSV roundoff only."""
    require_development(run)
    combined = frame.context__set_static_load_n + frame.context__set_dynamic_amplitude_n
    lower, upper = (4000., 5000.) if run == "B04" else (4300., 4900.)
    bad = (~frame.quality__documented_warmup_setpoints
           & ((combined < lower - 1e-8) | (combined > upper + 1e-8)))
    return combined, bad, (lower, upper)


def cross_support(frames):
    """Outer union of the original exact bins. Missing run/bin support is zero."""
    support = {}
    for run, frame in frames.items():
        require_development(run)
        if set(frame.provenance__experiment) != {run}:
            raise ValueError("Frame provenance does not match authorized run")
        for group, _ in condition_groups(frame):
            key = tuple(group[c] for c in ("speed_lower_rpm", "static_load_lower_n", "dynamic_peak_lower_n", "warmup"))
            row = support.setdefault(key, dict(zip(("speed_lower_rpm", "static_load_lower_n", "dynamic_peak_lower_n", "warmup"), key)))
            row[run + "_n"] = group["n"]
            row[run + "_warning_n"] = group["n_row_warning"]
    result = pd.DataFrame(list(support.values())).fillna(0)
    for run in frames:
        for suffix in ("_n", "_warning_n"):
            if run + suffix not in result:
                result[run + suffix] = 0
            result[run + suffix] = result[run + suffix].astype(int)
        result[run + "_sparse_n_lt20"] = result[run + "_n"] < 20
    return result.sort_values(["warmup", "speed_lower_rpm", "static_load_lower_n", "dynamic_peak_lower_n"]).reset_index(drop=True)


def assess_table(run, frame, output):
    require_development(run)
    times = pd.to_datetime(frame.provenance__source_time, format="%d-%b-%Y %H:%M:%S")
    gaps = times.diff().dt.total_seconds()
    diagnostics = frame[["provenance__experiment", "provenance__measurement_id", "provenance__source_time"]].copy()
    # Post-hoc run-level audit annotation, not an online/model input. No
    # numerical discrepancy threshold is fitted and no scale correction made.
    diagnostics["quality__operating_context_interpretation_unresolved"] = run == "B04"
    combined, outside_combined, combined_bounds = combined_load_check(run, frame)
    diagnostics["quality__combined_command_load_n"] = combined
    diagnostics["quality__combined_command_outside_log_range"] = outside_combined
    ratios = {}
    for name, measured, command in (
        ("speed", "measured_speed_rpm", "set_speed_rpm"),
        ("static_load", "measured_static_load_n", "set_static_load_n"),
        ("dynamic_peak", "measured_dynamic_peak_n", "set_dynamic_amplitude_n"),
    ):
        denominator = frame["context__" + command]
        ratio = frame["context__" + measured] / denominator.where(denominator.ne(0))
        diagnostics[f"quality__{name}_measured_to_command_ratio"] = ratio
        diagnostics[f"quality__{name}_ratio_undefined_zero_command"] = denominator.eq(0)
        diagnostics[f"quality__{name}_measured_minus_command"] = frame["context__" + measured] - denominator
        loaded = ratio[~frame.quality__documented_warmup_setpoints].dropna()
        ratios[name] = {"loaded_n": len(loaded), "min": float(loaded.min()),
                        "median": float(loaded.median()), "max": float(loaded.max()),
                        "zero_command_rows": int(denominator.eq(0).sum())}
    diagnostics.to_csv(output / run / "recording_diagnostics.csv", index=False)
    groups = condition_groups(frame)
    report = {
        "experiment": run, "rows": len(frame), "source_first": str(times.iloc[0]), "source_last": str(times.iloc[-1]),
        "operating_context_interpretation_unresolved": run == "B04",
        "context_review_flag_location": "recording_diagnostics.csv (post-hoc quality companion, excluded from candidate inputs)",
        "combined_command_range_check": {"log_bounds_n": list(combined_bounds), "csv_roundoff_tolerance_n": 1e-8,
                                          "loaded_outside_count": int(outside_combined.sum())},
        "elapsed_csv_seconds_not_operating_time": float((times.iloc[-1] - times.iloc[0]).total_seconds()),
        "gap_seconds": {"min": float(gaps.min()), "median": float(gaps.median()), "max": float(gaps.max())},
        "gaps_gt24s": [{"after_measurement": int(i), "seconds": float(gaps.loc[i]),
                         "before_time": str(times.iloc[i-1]), "after_time": str(times.iloc[i])}
                        for i in frame.index[gaps.gt(24)]],
        "measured_to_command_ratios": ratios,
        "feature_ranges": frame[[c for c in frame if c.startswith("feature__")]].agg(["min", "median", "max"]).to_dict(),
        "quality_boolean_counts": {c: int(frame[c].sum()) for c in frame if c.startswith("quality__") and frame[c].dtype == bool},
        "sensor_exceedance_samples": {c: int(frame[f"quality__{c}_outside_sensor_50g_samples"].sum()) for c in ("A", "C")},
        "groups": len(groups), "sparse_groups_lt20": sum(s["sparse_n_lt20"] for s, _ in groups),
        "missing_features": int(frame[[c for c in frame if c.startswith("feature__")]].isna().sum().sum()),
        "measured_context_ranges": {c: [float(frame[c].min()), float(frame[c].max())] for c in frame if c.startswith("context__measured_")},
    }
    (output / run / "assessment.json").write_text(json.dumps(report, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    return report


def plot_history(run, frame, output):
    require_development(run)
    times = pd.to_datetime(frame.provenance__source_time, format="%d-%b-%Y %H:%M:%S")
    elapsed = (times - times.iloc[0]).dt.total_seconds() / 60
    panels = [
        ([(f"feature__{c}_ac_rms_v", c) for c in ("A", "C")], "AC RMS (V)"),
        ([(f"feature__{c}_crest_factor", c) for c in ("A", "C")], "Crest factor"),
        ([(f"feature__{c}_excess_kurtosis", c) for c in ("A", "C")], "Excess kurtosis"),
        ([(f"feature__T{n}_above_room_c", f"T{n}-room") for n in (1, 2)], "Temperature difference (°C)"),
        ([("context__measured_speed_rpm", "Measured"), ("context__set_speed_rpm", "Commanded")], "Speed (rpm)"),
        ([("context__measured_static_load_n", "Measured mean absolute"), ("context__set_static_load_n", "Commanded")], "Static load (N)"),
        ([("context__measured_dynamic_peak_n", "Measured peak"), ("context__set_dynamic_amplitude_n", "Commanded amplitude")], "Dynamic load (N)"),
    ]
    fig, axes = plt.subplots(7, 1, figsize=(14, 18), sharex=True)
    warmup = frame.quality__documented_warmup_setpoints
    warm_groups = warmup.ne(warmup.shift()).cumsum()
    for k, (ax, (series, label)) in enumerate(zip(axes, panels)):
        if "quality__initial_setpoint_policy_ambiguous" in frame:
            uncertain = frame.quality__initial_setpoint_policy_ambiguous
            if uncertain.any():
                ax.axvspan(elapsed[uncertain].min(), elapsed[uncertain].max(), color="orange", alpha=.08)
        for _, part in frame[warmup].groupby(warm_groups[warmup]):
            ax.axvspan(elapsed.loc[part.index].min(), elapsed.loc[part.index].max(), color="tab:blue", alpha=.12)
        for i in frame.index[frame.quality__preceding_gap_gt24s]:
            ax.axvspan(elapsed.iloc[i-1], elapsed.iloc[i], color="gray", alpha=.2)
        for column, name in series:
            ax.scatter(elapsed, frame[column], s=8, label=name)
            if k < 3:
                flagged = frame[f"quality__{name}_sensor_range_exceeded"]
                ax.scatter(elapsed[flagged], frame.loc[flagged, column], marker="D", s=40,
                           facecolors="none", edgecolors="crimson")
        ax.set_ylabel(label)
        ax.legend(fontsize=8, loc="upper left")
        ax.grid(alpha=.2)
    axes[-1].set_xlabel("Minutes from first CSV timestamp — not operating time; ordinal association provisional")
    context_note = " — OPERATING-CONTEXT INTERPRETATION UNRESOLVED" if run == "B04" else ""
    fig.suptitle(f"{run}: all {len(frame)} bursts retained; no interpolation or labels{context_note}\n"
                 "Blue: warm-up; gray: >24 s gaps; orange: B04 initial policy uncertain; red diamonds: channel range warnings")
    fig.tight_layout(rect=(0, 0, 1, .965))
    fig.savefig(output / run / "histories.png", dpi=130)
    plt.close(fig)


def plot_cross(frames, support, output):
    loaded = support[~support.warmup].copy()
    loaded["matched_support"] = loaded[["B01_n", "B02_n"]].min(axis=1)
    selected = loaded[loaded.matched_support.gt(0)].sort_values(
        ["matched_support", "speed_lower_rpm", "static_load_lower_n", "dynamic_peak_lower_n"], ascending=[False, True, True, True]).head(4)
    selected.to_csv(output / "selected_cross_comparisons.csv", index=False)
    summaries = []
    fig, axes = plt.subplots(len(selected), 3, figsize=(16, 3.5 * len(selected)), squeeze=False)
    for row_index, (_, group) in enumerate(selected.iterrows()):
        parts = {}
        for run, frame in frames.items():
            parts[run] = frame[~frame.quality__documented_warmup_setpoints
                              & frame.context__measured_speed_rpm.between(group.speed_lower_rpm, group.speed_lower_rpm + 250, inclusive="left")
                              & frame.context__measured_static_load_n.between(group.static_load_lower_n, group.static_load_lower_n + 250, inclusive="left")
                              & frame.context__measured_dynamic_peak_n.between(group.dynamic_peak_lower_n, group.dynamic_peak_lower_n + 250, inclusive="left")]
            for column in [c for c in frame if c.startswith("feature__")]:
                data = parts[run][column]
                summaries.append({"experiment": run, "speed_lower_rpm": group.speed_lower_rpm,
                                  "static_load_lower_n": group.static_load_lower_n, "dynamic_peak_lower_n": group.dynamic_peak_lower_n,
                                  "feature": column, "n": len(data), "warning_n": int(parts[run].quality__any_warning.sum()),
                                  "median": data.median(), "q25": data.quantile(.25), "q75": data.quantile(.75)})
        for column_index, (metric, label) in enumerate((("ac_rms_v", "AC RMS (V)"), ("crest_factor", "Crest factor"), ("excess_kurtosis", "Excess kurtosis"))):
            ax = axes[row_index, column_index]
            labels = []
            for run_index, run in enumerate(RUNS):
                part = parts[run]
                for channel_index, channel in enumerate(("A", "C")):
                    position = run_index * 2 + channel_index + 1
                    labels.append(f"{run}\n{channel}")
                    data = part[f"feature__{channel}_{metric}"].dropna()
                    if len(data):
                        ax.boxplot([data], positions=[position], widths=.6, showfliers=True)
                        flags = part.quality__any_warning
                        ax.scatter(np.full(flags.sum(), position), part.loc[flags, f"feature__{channel}_{metric}"],
                                   s=13, facecolors="none", edgecolors="crimson")
            ax.set_xticks(range(1, 7), labels, fontsize=7)
            ax.set_ylabel(label)
            ax.grid(alpha=.2)
            sparse = ", ".join(r for r in RUNS if len(parts[r]) < 20)
            ax.set_title("B01/B02/B04 n: " + "/".join(str(len(parts[r])) for r in RUNS)
                         + "; warnings: " + "/".join(str(int(parts[r].quality__any_warning.sum())) for r in RUNS)
                         + f"\nSparse/absent: {sparse or 'none'}", fontsize=8)
        axes[row_index, 0].text(0, 1.34, f"Measured bin: {group.speed_lower_rpm}–<{group.speed_lower_rpm+250} rpm, "
                              f"{group.static_load_lower_n}–<{group.static_load_lower_n+250} N static, "
                              f"{group.dynamic_peak_lower_n}–<{group.dynamic_peak_lower_n+250} N dynamic peak",
                              transform=axes[row_index, 0].transAxes, fontsize=9)
    pd.DataFrame(summaries).to_csv(output / "cross_feature_summaries.csv", index=False)
    fig.suptitle("Development runs only: unchanged 250 rpm / 250 N / 250 N measured bins\n"
                 "Boxes = median/IQR; red points = retained row warnings; no supported B04 match is invented")
    fig.tight_layout(rect=(0, 0, 1, .94))
    fig.savefig(output / "cross_comparisons.png", dpi=130)
    plt.close(fig)
    counts = loaded[[r + "_n" for r in RUNS]].to_numpy()
    fig, ax = plt.subplots(figsize=(9, max(6, len(loaded) * .15)))
    ax.imshow(counts, aspect="auto", cmap="Blues")
    ax.set_xticks(range(3), RUNS)
    ax.set_yticks(range(len(loaded)), [f"{int(g.speed_lower_rpm)}/{int(g.static_load_lower_n)}/{int(g.dynamic_peak_lower_n)}" for _, g in loaded.iterrows()], fontsize=5)
    for i in range(len(loaded)):
        for j in range(3):
            ax.text(j, i, str(counts[i, j]), ha="center", va="center", fontsize=6,
                    color="crimson" if counts[i, j] < 20 else "black")
    ax.set_ylabel("Exact bin lower edges: rpm / static N / dynamic-peak N")
    ax.set_title("All loaded bins: per-run counts; red = n<20 including zero\nNo rescaling, bin broadening or held-out observations")
    fig.tight_layout()
    fig.savefig(output / "cross_support.png", dpi=130)
    plt.close(fig)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--reuse-features", action="store_true", help="Reuse current assessment's B02/B04 tables after integrity checks")
    args = parser.parse_args()
    output = args.output
    raw_base = Path("/workspace/datasets/paderborn-10868257/raw")
    if output.resolve() == raw_base or raw_base in output.resolve().parents:
        parser.error("Assessment output must be outside all raw experiment directories")
    output.mkdir(parents=True, exist_ok=True)
    if (output / "assessment.json").exists():
        parser.error("Assessment already exists; use a fresh output directory")
    tables = {"B01": Path("reports/local/b01-features-v1")}
    for run in ("B02", "B04"):
        tables[run] = output / run
        if not args.reuse_features:
            extract_b01(raw_base / run, tables[run], expected_measurements=DEVELOPMENT_COUNTS[run], experiment_id=run)
    frames, reports = {}, {}
    for run in RUNS:
        baseline = json.loads((tables[run] / "raw_integrity.json").read_text(encoding="utf-8"))["files"]
        if raw_manifest(raw_base / run) != baseline:
            raise ValueError(f"{run} raw integrity differs from extracted table provenance")
        frame = pd.read_csv(tables[run] / "features.csv")
        if len(frame) != DEVELOPMENT_COUNTS[run] or set(frame.provenance__experiment) != {run}:
            raise ValueError("Wrong run or feature count")
        (output / run).mkdir(exist_ok=True)
        frames[run] = frame
        reports[run] = assess_table(run, frame, output)
        plot_history(run, frame, output)
    support = cross_support(frames)
    support.to_csv(output / "cross_support.csv", index=False)
    plot_cross(frames, support, output)
    loaded = support[~support.warmup]
    report = {"experiments": reports,
              "loaded_bins_all_three_n_positive": int((loaded[[r+"_n" for r in RUNS]] > 0).all(axis=1).sum()),
              "loaded_bins_B01_B02_n_ge20": int((loaded[[r+"_n" for r in ("B01", "B02")]] >= 20).all(axis=1).sum()),
              "loaded_bins_B04_with_any_B01_B02": int((loaded.B04_n.gt(0) & (loaded.B01_n.gt(0) | loaded.B02_n.gt(0))).sum()),
              "held_out_access_performed": False, "normalization_fitted": False, "model_trained": False, "labels_created": False}
    (output / "assessment.json").write_text(json.dumps(report, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
