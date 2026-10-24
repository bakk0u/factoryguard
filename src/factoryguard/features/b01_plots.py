"""Offline descriptive comparisons; grouping is never used to calculate features."""
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
import numpy as np
import pandas as pd
from factoryguard.data.paderborn import require_development


SPARSE_COUNT = 20  # display heuristic, not a statistical adequacy guarantee
BIN_WIDTHS = {
    "context__measured_speed_rpm": 250,
    "context__measured_static_load_n": 250,
    "context__measured_dynamic_peak_n": 250,
}


def condition_groups(frame: pd.DataFrame):
    """Fixed half-open bins; warm-up never grouped together with loaded runs."""
    grouped = frame.copy()
    for column, width in BIN_WIDTHS.items():
        grouped[column + "__bin_lower"] = np.floor(grouped[column] / width).astype(int) * width
    keys = [column + "__bin_lower" for column in BIN_WIDTHS] + ["quality__documented_warmup_setpoints"]
    groups = []
    for key, part in grouped.groupby(keys, sort=True):
        speed, static, dynamic, warmup = key
        groups.append(({
            "speed_lower_rpm": int(speed), "static_load_lower_n": int(static),
            "dynamic_peak_lower_n": int(dynamic), "warmup": bool(warmup),
            "n": len(part), "n_without_row_warning": int((~part.quality__any_warning).sum()),
            "n_row_warning": int(part.quality__any_warning.sum()),
            "n_A_range_warning": int(part.quality__A_sensor_range_exceeded.sum()),
            "n_C_range_warning": int(part.quality__C_sensor_range_exceeded.sum()),
            "n_setpoint_warning": int(part[[f"quality__{c}_setpoint_outside_main_range"
                                            for c in ("speed", "static_load", "dynamic_load")]].any(axis=1).sum()),
            "n_preceding_gap_warning": int(part.quality__preceding_gap_gt24s.sum()),
            "sparse_n_lt20": len(part) < SPARSE_COUNT,
            "sparse_without_warning_n_lt20": int((~part.quality__any_warning).sum()) < SPARSE_COUNT,
        }, part))
    return groups


def _label(summary):
    s, l, d = (summary[k] for k in ("speed_lower_rpm", "static_load_lower_n", "dynamic_peak_lower_n"))
    return f"{s}–<{s+250} rpm; static {l}–<{l+250} N; dynamic peak {d}–<{d+250} N"


def plot_comparisons(frame: pd.DataFrame, output: Path) -> dict:
    runs = sorted(frame.provenance__experiment.unique())
    for run in runs:
        require_development(run)
    experiment = ", ".join(runs)
    if "B04" in runs:
        experiment += " (operating-context interpretation unresolved)"
    output = Path(output)
    groups = condition_groups(frame)
    summary = pd.DataFrame([s for s, _ in groups])
    summary.to_csv(output / "condition_counts.csv", index=False)
    ordered = sorted(groups, key=lambda item: (-item[0]["n"], _label(item[0])))
    selected = [item for item in ordered if not item[0]["warmup"]][:4]
    if selected:
        fig, axes = plt.subplots(len(selected), 3, figsize=(16, 3.2 * len(selected)), squeeze=False)
        initial = pd.to_datetime(frame.provenance__source_time, format="%d-%b-%Y %H:%M:%S").iloc[0]
        for row, (group, part) in enumerate(selected):
            times = pd.to_datetime(part.provenance__source_time, format="%d-%b-%Y %H:%M:%S")
            minutes = (times - initial).dt.total_seconds() / 60
            for col, (metric, unit) in enumerate((("ac_rms_v", "AC RMS (V)"),
                                                   ("crest_factor", "Crest factor"),
                                                   ("excess_kurtosis", "Excess kurtosis"))):
                ax = axes[row, col]
                for channel, color, marker in (("A", "tab:blue", "o"), ("C", "tab:green", "x")):
                    values = part[f"feature__{channel}_{metric}"]
                    ax.scatter(minutes, values, s=22, c=color, marker=marker)
                    flagged = part.quality__any_warning
                    ax.scatter(minutes[flagged], values[flagged], s=65,
                               facecolors="none", edgecolors="tab:red", linewidths=1)
                missing = int(part[[f"feature__{c}_{metric}" for c in ("A", "C")]].isna().sum().sum())
                note = f"n={group['n']}; row-warning={group['n_row_warning']}; missing A/C={missing}"
                if group["sparse_n_lt20"] or group["sparse_without_warning_n_lt20"]:
                    note += "\nSPARSE: total or without-warning n<20"
                ax.set_title(note, fontsize=9)
                ax.set_ylabel(unit)
                ax.set_xlabel("Minutes from first CSV time (provisional association)")
                ax.grid(alpha=0.2)
            axes[row, 0].text(0, 1.26, _label(group), transform=axes[row, 0].transAxes, fontsize=10)
        fig.suptitle(f"{experiment}: four most populated non-warmup operating bins\n"
                     "All rows retained; red rings mark row warnings; bins do not establish equivalent conditions", y=1.01)
        fig.legend(handles=[Line2D([], [], marker="o", color="tab:blue", linestyle="", label="A"),
                            Line2D([], [], marker="x", color="tab:green", linestyle="", label="C"),
                            Line2D([], [], marker="o", markerfacecolor="none", color="tab:red",
                                   linestyle="", label="Row warning (see table for exact cause)")],
                   loc="upper center", bbox_to_anchor=(0.5, 0.97), ncol=3)
        fig.tight_layout(rect=(0, 0, 1, 0.94))
        fig.savefig(output / "condition_comparisons.png", dpi=140, bbox_inches="tight")
        plt.close(fig)
    fig, ax = plt.subplots(figsize=(13, max(5, len(ordered) * 0.27)))
    labels = [_label(s) + (" [warm-up]" if s["warmup"] else "") for s, _ in ordered]
    colors = ["gray" if s["warmup"] else "tab:orange" if s["sparse_n_lt20"] else "tab:blue" for s, _ in ordered]
    counts = [s["n"] for s, _ in ordered]
    positions = np.arange(len(ordered))
    ax.barh(positions, counts, color=colors)
    for i, (s, _) in enumerate(ordered):
        ax.text(s["n"] + 0.3, i, f"n={s['n']}, row-warning={s['n_row_warning']}", va="center", fontsize=8)
    ax.set_yticks(positions, labels, fontsize=8)
    ax.invert_yaxis()
    ax.set_xlim(0, max(counts) * 1.55)
    ax.set_xlabel("Number of bursts (not independent experiments)")
    ax.set_title(f"{experiment} operating bins: orange n<20; gray warm-up\n"
                 "Fixed 250 rpm / 250 N / 250 N bins; sample counts do not certify adequacy")
    fig.tight_layout()
    fig.savefig(output / "condition_support.png", dpi=140)
    plt.close(fig)
    return {
        "plots_generated": True, "total_condition_groups": len(groups),
        "sparse_groups_n_lt20": int(summary.sparse_n_lt20.sum()),
        "sparse_threshold_bursts": SPARSE_COUNT,
        "selected_comparison_group_count": len(selected),
        "selected_groups": [s for s, _ in selected],
        "bin_widths": BIN_WIDTHS,
        "warning": "Coarse bins do not control all condition variation or prove comparable health. "
                   "Plot selection uses complete table only for visualization; feature rows are independent of grouping.",
    }
