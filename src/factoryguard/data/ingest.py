"""Read a CSV without silently cleaning or reordering records."""
from pathlib import Path
import pandas as pd

def load_csv(path: str | Path) -> pd.DataFrame:
    path = Path(path)
    if not path.is_file():
        raise FileNotFoundError(f"Sensor CSV not found: {path}")
    return pd.read_csv(path, dtype={"machine_id": "string"})
