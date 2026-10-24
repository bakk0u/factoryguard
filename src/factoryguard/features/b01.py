"""Per-burst descriptors. No fitted parameters, labels, or across-burst state."""
from dataclasses import dataclass

import numpy as np

from factoryguard.data.paderborn import G_PER_VOLT


@dataclass(frozen=True)
class ChannelFeatures:
    ac_rms_v: float
    crest_factor: float
    excess_kurtosis: float
    dc_mean_v: float
    raw_peak_abs_v: float
    outside_sensor_range_samples: int
    zero_variance: bool


def channel_features(values: np.ndarray) -> ChannelFeatures:
    """Center a completed burst by its own arithmetic mean.

    m2 = mean((x - mean(x))**2), m4 = mean((x - mean(x))**4).
    RMS = sqrt(m2); crest = max(abs(x-mean(x)))/sqrt(m2);
    excess kurtosis = m4/m2**2 - 3 (population-moment, biased estimator).
    Undefined ratios are NaN. Scaling below is numerical stabilization only.
    """
    raw = np.asarray(values)
    if (raw.ndim != 1 or raw.size == 0 or np.iscomplexobj(raw)
            or not np.issubdtype(raw.dtype, np.number) or not np.isfinite(raw).all()):
        raise ValueError("Expected a nonempty finite real numeric vector")
    x = raw.astype(np.float64, copy=False)
    constant = bool(np.all(x == x[0]))
    mean = float(x[0]) if constant else float(x.mean())
    centered = x - mean
    if not np.isfinite(centered).all():
        raise ValueError("Centering exceeded float64 numeric range")
    peak = float(np.max(np.abs(centered)))
    if constant:
        rms, crest, kurtosis = 0.0, float("nan"), float("nan")
    else:
        scaled = centered / peak
        m2 = float(np.mean(scaled * scaled))
        m4 = float(np.mean((scaled * scaled) ** 2))
        rms = peak * np.sqrt(m2)
        crest = 1 / np.sqrt(m2)
        kurtosis = m4 / (m2 * m2) - 3
    return ChannelFeatures(
        float(rms), float(crest), float(kurtosis), mean,
        float(np.max(np.abs(x))),
        int(np.count_nonzero(np.abs(x) > 50 / G_PER_VOLT)), constant,
    )


FEATURE_COLUMNS = tuple(
    f"feature__{channel}_{name}" for channel in ("A", "C")
    for name in ("ac_rms_v", "crest_factor", "excess_kurtosis")
) + ("feature__T1_above_room_c", "feature__T2_above_room_c")

CONTEXT_COLUMNS = (
    "context__measured_speed_rpm", "context__measured_static_load_n", "context__measured_dynamic_peak_n",
    "context__set_speed_rpm", "context__set_static_load_n", "context__set_dynamic_amplitude_n",
    "context__T1_c", "context__T2_c", "context__room_c",
)

# A reviewed allowlist is required; selecting every numeric column is unsafe.
CANDIDATE_INPUT_COLUMNS = FEATURE_COLUMNS + CONTEXT_COLUMNS[:3]


def feature_schema() -> dict:
    return {
        "schema_version": "b01-features-v1",
        "feature_columns": list(FEATURE_COLUMNS),
        "context_columns": list(CONTEXT_COLUMNS),
        "candidate_input_columns": list(CANDIDATE_INPUT_COLUMNS),
        "default_model_input_columns": [],
        "selection_policy": "Candidate inputs require explicit review/selection; never select all numeric columns.",
        "non_input_prefixes": ["provenance__", "quality__"],
        "missing_value_encoding": "Empty CSV cell (NaN on reading); never substitute zero for undefined ratios.",
        "vibration_unit": "V; log conversion 10 g/V, not applied to candidate features",
        "kurtosis_estimator": "m4/m2^2 - 3; central moments divided by N; no finite-sample bias correction",
        "availability": "Only after the complete 1.6 s burst; CSV timestamp start/end meaning and ordinal alignment provisional",
    }
