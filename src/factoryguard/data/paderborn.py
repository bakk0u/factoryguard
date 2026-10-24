"""Authorized B01/B02/B04 development ingestion, Zenodo record 10868257.

Their experiment logs specify 128 kHz, 1.6 s, and 10 g/V at 0 dB gain.
Raw arrays remain in volts. No failure/RUL labels or model inputs are created.
"""
from dataclasses import dataclass
from pathlib import Path
import re

import numpy as np
import pandas as pd
from scipy.io import loadmat, whosmat
from scipy.io.matlab import MatReadError


SAMPLE_RATE_HZ = 128_000
SAMPLE_COUNT = 204_800
G_PER_VOLT = 10.0
CHANNELS = ("accHorizRear_A", "accHorizFrontal_C")
TEMPERATURE_COLUMNS = (
    "Mean Abs. Temp. T1 / °C", "Mean Abs. Temp. T2 / °C", "Mean Room Temp. / °C",
)
OPERATING_COLUMNS = (
    "setDynLoad / N", "peak_dynLoad / N", "setStatLoad / N",
    "meanAbs_statLoad / N", "setSpeed / rpm", "meanAbs_speed / rpm",
)
TIME_FORMAT = "%d-%b-%Y %H:%M:%S"


@dataclass(frozen=True)
class Recording:
    measurement_id: int
    sample_time_seconds: np.ndarray
    rear_a_volts: np.ndarray
    frontal_c_volts: np.ndarray


DEVELOPMENT_COUNTS = {"B01": 377, "B02": 1116, "B04": 1114}


def require_development(experiment: str) -> None:
    if experiment not in DEVELOPMENT_COUNTS:
        raise ValueError(f"{experiment}: waveform/feature access denied; only B01/B02/B04 development runs are authorized")


def load_recording(path: str | Path, *, experiment: str = "B01") -> Recording:
    """Load one MAT record (~4.7 MiB of arrays), never a whole experiment.

    Preflight shapes before allocation. Validate all samples without sorting,
    clipping, unit conversion, or filling. MATLAB v7.3/HDF5 is not this format.
    """
    require_development(experiment)
    path = Path(path)
    match = re.fullmatch(rf"data_{experiment}_M(\d{{4}})\.mat", path.name)
    if match is None or int(match[1]) < 1:
        raise ValueError(f"Not a {experiment} measurement filename: {path.name}")
    required = (*CHANNELS, "measTime")
    try:
        info = {name: (shape, kind) for name, shape, kind in whosmat(path)}
    except (ValueError, OSError, TypeError, NotImplementedError, MatReadError) as error:
        raise ValueError(f"Unreadable MAT file {path.name}: {error}") from error
    for name in required:
        if name not in info:
            raise ValueError(f"{path.name}: missing MAT variable {name}")
        shape, kind = info[name]
        if shape not in ((SAMPLE_COUNT, 1), (1, SAMPLE_COUNT)) or kind != "double":
            raise ValueError(f"{path.name}: {name} must be a {SAMPLE_COUNT}-sample double vector")
    try:
        data = loadmat(path, variable_names=required, verify_compressed_data_integrity=True)
    except (ValueError, OSError, TypeError, MatReadError) as error:
        raise ValueError(f"Unreadable MAT payload {path.name}: {error}") from error
    arrays = {}
    for name in required:
        array = data[name]
        if np.iscomplexobj(array) or not np.isfinite(array).all():
            raise ValueError(f"{path.name}: {name} contains complex or nonfinite values")
        arrays[name] = array.reshape(-1)
    # Validated development measTime is seconds relative to each recording.
    expected = np.arange(SAMPLE_COUNT, dtype=float) / SAMPLE_RATE_HZ
    if not np.allclose(arrays["measTime"], expected, rtol=0, atol=1e-10):
        raise ValueError(f"{path.name}: measTime is not a zero-based 128 kHz sample grid")
    return Recording(int(match[1]), arrays["measTime"], arrays[CHANNELS[0]], arrays[CHANNELS[1]])


def load_table(path: str | Path, columns: tuple[str, ...]) -> pd.DataFrame:
    """Return a validated table with original values plus parsed naive Time.

    B01's observed headers differ from the general description PDF. Do not
    silently alias undocumented variants or invent a timezone for source times.
    """
    path = Path(path)
    frame = pd.read_csv(path, encoding="utf-8")
    if tuple(frame.columns) != ("Time", *columns):
        raise ValueError(f"{path.name}: unexpected columns: {list(frame.columns)}")
    if frame.empty:
        raise ValueError(f"{path.name}: empty table")
    times = pd.to_datetime(frame["Time"], format=TIME_FORMAT, errors="coerce")
    if times.isna().any() or times.duplicated().any() or not times.is_monotonic_increasing:
        raise ValueError(f"{path.name}: invalid, duplicate or out-of-order Time")
    for column in columns:
        values = pd.to_numeric(frame[column], errors="coerce")
        if not np.isfinite(values.to_numpy(dtype=float)).all():
            raise ValueError(f"{path.name}: {column} contains missing/nonnumeric/nonfinite values")
    return frame.assign(source_time=times)


class DevelopmentExperiment:
    """Validate inventory and small tables; iterate high-rate recordings lazily.

    Measurement ID to CSV row is an ordinal association, not an independently
    verified absolute timestamp: MAT contains only relative sample time.
    expected_measurements is overridable for generated tests/deliberate subsets.
    """

    def __init__(self, root: str | Path, *, experiment: str, expected_measurements: int | None = None):
        require_development(experiment)
        self.experiment = experiment
        expected_measurements = DEVELOPMENT_COUNTS[experiment] if expected_measurements is None else expected_measurements
        self.root = Path(root)
        self.temperatures = load_table(self.root / f"{experiment}_meanTemperatures.csv", TEMPERATURE_COLUMNS)
        self.operating = load_table(self.root / f"{experiment}_operatingConditions.csv", OPERATING_COLUMNS)
        if not self.temperatures["source_time"].equals(self.operating["source_time"]):
            raise ValueError("Temperature/operating timestamps do not align exactly")
        files = list((self.root / "vibrationData").iterdir())
        indexed = {}
        for path in files:
            match = re.fullmatch(rf"data_{experiment}_M(\d{{4}})\.mat", path.name)
            if not path.is_file() or match is None:
                raise ValueError(f"Unexpected vibrationData entry: {path.name}")
            indexed[int(match[1])] = path
        if (expected_measurements < 1 or len(self.temperatures) != expected_measurements
                or sorted(indexed) != list(range(1, expected_measurements + 1))):
            raise ValueError(f"{experiment} inventory: missing/extra measurement IDs or CSV row count mismatch")
        self.paths = tuple(indexed[i] for i in range(1, expected_measurements + 1))

    def recordings(self):
        """Consumer must process/release each record rather than collect arrays."""
        for path in self.paths:
            yield load_recording(path, experiment=self.experiment)


class B01Experiment(DevelopmentExperiment):
    """Backward-compatible B01 entry point; all original defaults retained."""
    def __init__(self, root: str | Path, *, expected_measurements: int = 377):
        super().__init__(root, experiment="B01", expected_measurements=expected_measurements)
