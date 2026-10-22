"""Report structural errors and data-quality warnings without modifying input."""
import numpy as np
import pandas as pd
from .schema import REQUIRED_COLUMNS, SENSORS, EXPECTED_INTERVAL_SECONDS

def validate_readings(frame: pd.DataFrame) -> dict:
    errors, warnings = [], []
    result = {"rows": len(frame), "machines": 0, "errors": errors, "warnings": warnings}
    missing = sorted(set(REQUIRED_COLUMNS) - set(frame.columns))
    if missing:
        errors.append(f"Missing required columns: {', '.join(missing)}")
    if frame.empty:
        errors.append("Dataset is empty.")
    if errors:
        result["valid"] = False
        return result
    ids = frame["machine_id"].astype("string")
    bad_ids = ids.isna() | ids.str.strip().eq("")
    if bad_ids.any():
        errors.append(f"Missing/blank machine IDs: {int(bad_ids.sum())}")
    result["machines"] = int(ids[~bad_ids].nunique())
    times = pd.to_datetime(frame["timestamp"], errors="coerce", utc=True, format="ISO8601")
    if times.isna().any():
        errors.append(f"Invalid/missing timestamps: {int(times.isna().sum())}")
    keys = pd.DataFrame({"machine_id": ids, "timestamp": times})
    duplicates = keys.duplicated().sum()
    if duplicates:
        errors.append(f"Duplicate machine/timestamp keys: {int(duplicates)}")
    for column, (_, lower, upper) in SENSORS.items():
        values = pd.to_numeric(frame[column], errors="coerce")
        bad = ~np.isfinite(values.to_numpy(dtype=float, na_value=np.nan))
        if bad.any():
            errors.append(f"{column}: {int(bad.sum())} missing, nonnumeric or infinite values")
        outside = values.notna() & ((values < lower) | (values > upper))
        if outside.any():
            errors.append(f"{column}: {int(outside.sum())} values outside demo range [{lower}, {upper}]")
    for machine, group in keys.dropna().groupby("machine_id", sort=False):
        if not group["timestamp"].is_monotonic_increasing:
            errors.append(f"{machine}: timestamps are not in increasing order")
        delta = group["timestamp"].sort_values().diff().dt.total_seconds().dropna()
        irregular = delta.ne(EXPECTED_INTERVAL_SECONDS).sum()
        if irregular:
            warnings.append(f"{machine}: {int(irregular)} sampling intervals differ from 60 seconds")
    result["valid"] = not errors
    return result
