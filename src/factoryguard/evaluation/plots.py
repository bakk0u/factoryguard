"""Plot validated sensor histories without requiring a GUI."""
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd
from ..data.schema import SENSORS

def plot_readings(frame: pd.DataFrame, output: Path) -> Path:
    output = Path(output)
    output.parent.mkdir(parents=True, exist_ok=True)
    figure, axes = plt.subplots(len(SENSORS), 1, figsize=(12, 10), sharex=True)
    for ax, (column, (label, _, _)) in zip(axes, SENSORS.items()):
        for machine, group in frame.groupby("machine_id"):
            ax.plot(pd.to_datetime(group["timestamp"], utc=True), group[column], label=str(machine), linewidth=1)
        ax.set_ylabel(label)
        ax.grid(alpha=0.25)
    axes[0].legend(loc="upper left", ncol=3)
    axes[0].set_title("FactoryGuard — sensor readings (source described in summary.json)")
    axes[-1].set_xlabel("Timestamp (UTC)")
    figure.autofmt_xdate()
    figure.tight_layout()
    figure.savefig(output, dpi=150)
    plt.close(figure)
    return output
