"""Acceptance checks with generated signals only; no real-data fixtures."""
import csv
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import numpy as np
import pandas as pd
from scipy.io import savemat
from scipy.stats import kurtosis

from factoryguard.data.paderborn import (
    B01Experiment, CHANNELS, OPERATING_COLUMNS, SAMPLE_COUNT, SAMPLE_RATE_HZ, TEMPERATURE_COLUMNS,
)
from factoryguard.features.b01 import channel_features, feature_schema
from factoryguard.features.b01_plots import condition_groups
from factoryguard.pipelines.features_paderborn import burst_rows, extract_b01, raw_manifest


class ChannelFeatureTests(unittest.TestCase):
    def test_known_centered_values_and_offset(self):
        x = np.array([9., 11., 9., 11.])
        before = x.copy()
        result = channel_features(x)
        self.assertEqual(result.ac_rms_v, 1)
        self.assertEqual(result.crest_factor, 1)
        self.assertEqual(result.excess_kurtosis, -2)
        self.assertEqual(result.dc_mean_v, 10)
        np.testing.assert_array_equal(x, before)

    def test_sine_analytic_features(self):
        x = 2 * np.sin(2 * np.pi * np.arange(1024) / 128)
        result = channel_features(x)
        self.assertAlmostEqual(result.ac_rms_v, np.sqrt(2))
        self.assertAlmostEqual(result.crest_factor, np.sqrt(2))
        self.assertAlmostEqual(result.excess_kurtosis, -1.5)

    def test_impulse_and_population_moment_estimator(self):
        x = np.array([0.] * 7 + [4.])
        result = channel_features(x)
        self.assertAlmostEqual(result.ac_rms_v, np.sqrt(1.75))
        self.assertAlmostEqual(result.crest_factor, np.sqrt(7))
        self.assertAlmostEqual(result.excess_kurtosis, kurtosis(x, fisher=True, bias=True))
        self.assertNotAlmostEqual(result.excess_kurtosis, kurtosis(x, fisher=True, bias=False))

    def test_constant_zero_and_nonzero_return_missing_ratios(self):
        for value in (0., 0.1, 6.):
            with self.subTest(value=value):
                result = channel_features(np.full(1000, value))
                self.assertEqual(result.ac_rms_v, 0)
                self.assertTrue(np.isnan(result.crest_factor))
                self.assertTrue(np.isnan(result.excess_kurtosis))
                self.assertTrue(result.zero_variance)
                self.assertEqual(result.outside_sensor_range_samples, 1000 if value == 6 else 0)

    def test_scale_and_offset_invariance(self):
        x = np.array([-2., -1., 0., 1., 4.])
        original = channel_features(x)
        transformed = channel_features(-3 * x + 20)
        self.assertAlmostEqual(transformed.ac_rms_v, 3 * original.ac_rms_v)
        self.assertAlmostEqual(transformed.crest_factor, original.crest_factor)
        self.assertAlmostEqual(transformed.excess_kurtosis, original.excess_kurtosis)

    def test_tiny_nonconstant_signal_not_misclassified(self):
        result = channel_features(np.array([-1e-250, 1e-250]))
        self.assertFalse(result.zero_variance)
        self.assertEqual(result.ac_rms_v, 1e-250)
        self.assertEqual(result.crest_factor, 1)
        self.assertEqual(result.excess_kurtosis, -2)

    def test_sensor_count_uses_uncentered_values_and_strict_boundary(self):
        result = channel_features(np.array([-5.1, -5, 5, 5.1]))
        self.assertEqual(result.outside_sensor_range_samples, 2)

    def test_invalid_signals_rejected(self):
        for x in ([], [[1., 2.]], [np.nan], [np.inf], [1j], ["bad"]):
            with self.subTest(x=x):
                with self.assertRaises(ValueError):
                    channel_features(np.asarray(x))


class FeaturePipelineTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.base = Path(self.temp.name)
        self.root = self.base / "raw"
        (self.root / "vibrationData").mkdir(parents=True)
        self.times = ["19-Oct-2021 08:00:00", "19-Oct-2021 08:00:12", "19-Oct-2021 08:03:12"]
        self.sample_time = np.arange(SAMPLE_COUNT) / SAMPLE_RATE_HZ
        self.sine = np.sin(2 * np.pi * 100 * self.sample_time)
        for i in range(1, 4):
            self.write_mat(i, self.sine * i, np.full(SAMPLE_COUNT, 0.1) if i == 1 else self.sine)
        temperature = pd.DataFrame({"Time": self.times, TEMPERATURE_COLUMNS[0]: [25., 26., 28.],
                                    TEMPERATURE_COLUMNS[1]: [24., 25., 27.],
                                    TEMPERATURE_COLUMNS[2]: [20., 21., 22.]})
        operating = pd.DataFrame({"Time": self.times, OPERATING_COLUMNS[0]: [0., 1000., 900.],
                                  OPERATING_COLUMNS[1]: [10., 1020., 940.],
                                  OPERATING_COLUMNS[2]: [2500., 3400., 3600.],
                                  OPERATING_COLUMNS[3]: [2510., 3450., 3620.],
                                  OPERATING_COLUMNS[4]: [750., 3500., 2800.],
                                  OPERATING_COLUMNS[5]: [753., 2999., 2810.]})
        temperature.to_csv(self.root / "B01_meanTemperatures.csv", index=False)
        operating.to_csv(self.root / "B01_operatingConditions.csv", index=False)

    def write_mat(self, i, a, c):
        savemat(self.root / f"vibrationData/data_B01_M{i:04d}.mat", {
            CHANNELS[0]: np.asarray(a).reshape(-1, 1), CHANNELS[1]: np.asarray(c).reshape(-1, 1),
            "measTime": self.sample_time.reshape(-1, 1),
        })

    def run_extraction(self, name):
        output = self.base / name
        report = extract_b01(self.root, output, expected_measurements=3, make_plots=False)
        return output, report, pd.read_csv(output / "features.csv")

    def test_complete_rows_thermal_context_and_quality(self):
        before = raw_manifest(self.root)
        output, report, frame = self.run_extraction("out")
        self.assertEqual(report["rows"], 3)
        self.assertEqual(before, raw_manifest(self.root))
        self.assertEqual(frame.provenance__measurement_id.tolist(), [1, 2, 3])
        self.assertEqual(frame.feature__T1_above_room_c.tolist(), [5., 5., 6.])
        self.assertEqual(frame.feature__T2_above_room_c.tolist(), [4., 4., 5.])
        self.assertEqual(frame.context__set_speed_rpm.tolist(), [750., 3500., 2800.])
        self.assertEqual(frame.context__measured_speed_rpm.tolist(), [753., 2999., 2810.])
        self.assertTrue(frame.quality__documented_warmup_setpoints.iloc[0])
        self.assertTrue(frame.quality__speed_setpoint_outside_main_range.iloc[1])
        self.assertTrue(frame.provenance__ordinal_alignment_provisional.all())
        self.assertTrue((frame.provenance__timestamp_meaning == "unknown_start_or_end").all())
        self.assertEqual(json.loads((output / "raw_integrity.json").read_text())["verified_file_count"], 5)

    def test_missing_ratio_csv_encoding_and_per_channel_flags(self):
        output, _, frame = self.run_extraction("out")
        self.assertTrue(frame.quality__C_zero_variance.iloc[0])
        self.assertTrue(frame.quality__C_crest_factor_undefined.iloc[0])
        self.assertTrue(frame.quality__C_excess_kurtosis_undefined.iloc[0])
        self.assertTrue(np.isnan(frame.feature__C_crest_factor.iloc[0]))
        self.assertTrue(np.isnan(frame.feature__C_excess_kurtosis.iloc[0]))
        self.assertFalse(frame.quality__A_zero_variance.iloc[0])
        with (output / "features.csv").open() as stream:
            row = next(csv.DictReader(stream))
        self.assertEqual(row["feature__C_crest_factor"], "")

    def test_gap_preserved_no_filling_or_concatenation(self):
        _, _, frame = self.run_extraction("out")
        self.assertTrue(np.isnan(frame.quality__preceding_csv_gap_s.iloc[0]))
        self.assertEqual(frame.quality__preceding_csv_gap_s.iloc[1:].tolist(), [12., 180.])
        self.assertEqual(frame.quality__acquisition_segment.tolist(), [0, 0, 1])
        self.assertEqual(frame.quality__preceding_gap_gt24s.tolist(), [False, False, True])
        self.assertEqual(frame.provenance__sample_count.tolist(), [SAMPLE_COUNT] * 3)
        self.assertAlmostEqual(frame.feature__A_ac_rms_v.iloc[2], 3 / np.sqrt(2))

    def test_future_data_independence_all_earlier_fields(self):
        _, _, first = self.run_extraction("before")
        # Perturb only the future burst and its CSV context/timestamp.
        self.write_mat(3, np.full(SAMPLE_COUNT, 6.), self.sine * 7 + 2)
        for suffix in ("meanTemperatures", "operatingConditions"):
            path = self.root / f"B01_{suffix}.csv"
            data = pd.read_csv(path)
            data.loc[2, "Time"] = "19-Oct-2021 09:00:00"
            data.iloc[2, 1:] = data.iloc[2, 1:] + 10
            data.to_csv(path, index=False)
        _, _, second = self.run_extraction("after")
        pd.testing.assert_frame_equal(first.iloc[:2], second.iloc[:2])
        self.assertNotEqual(first.feature__A_ac_rms_v.iloc[2], second.feature__A_ac_rms_v.iloc[2])
        self.assertTrue(second.quality__A_sensor_range_exceeded.iloc[2])

    def test_source_rows_and_suspect_waveforms_not_clipped(self):
        self.write_mat(2, self.sine * 6, self.sine * 2)
        before = raw_manifest(self.root)
        _, _, frame = self.run_extraction("out")
        self.assertEqual(len(frame), 3)
        self.assertTrue(frame.quality__A_sensor_range_exceeded.iloc[1])
        self.assertAlmostEqual(frame.quality__A_raw_peak_abs_v.iloc[1], 6)
        self.assertAlmostEqual(frame.feature__A_ac_rms_v.iloc[1], 6 / np.sqrt(2))
        self.assertEqual(before, raw_manifest(self.root))

    def test_role_allowlist_excludes_numeric_ids_flags_and_setpoints(self):
        output, _, frame = self.run_extraction("out")
        schema = json.loads((output / "schema.json").read_text())
        self.assertEqual(schema["default_model_input_columns"], [])
        for column in schema["candidate_input_columns"]:
            self.assertIn(column, frame)
            self.assertFalse(column.startswith(("quality__", "provenance__")))
            self.assertFalse(column.startswith("context__set_"))
        self.assertEqual(len(schema["candidate_input_columns"]), 11)
        self.assertIn("provenance__measurement_id", schema["provenance_columns"])

    def test_laziness_does_not_read_next_burst_early(self):
        # Construction/manifest can inspect files, but waveform loading is lazy.
        experiment = B01Experiment(self.root, expected_measurements=3)
        hashes = raw_manifest(self.root)
        from factoryguard.pipelines import features_paderborn as module
        with patch.object(module, "load_recording", wraps=module.load_recording) as loader:
            rows = burst_rows(experiment, hashes)
            self.assertEqual(loader.call_count, 0)
            self.assertEqual(next(rows)["provenance__measurement_id"], 1)
            self.assertEqual(loader.call_count, 1)
            next(rows)
            self.assertEqual(loader.call_count, 2)

    def test_refuse_overwrite_and_raw_output(self):
        self.run_extraction("out")
        with self.assertRaisesRegex(ValueError, "new or empty"):
            self.run_extraction("out")
        with self.assertRaisesRegex(ValueError, "outside raw"):
            extract_b01(self.root, self.root / "derived", expected_measurements=3)

    def test_changed_raw_file_prevents_final_publication(self):
        from factoryguard.pipelines import features_paderborn as module
        initial = raw_manifest(self.root)
        changed = {**initial, "injected": "different"}
        with patch.object(module, "raw_manifest", side_effect=[initial, changed]):
            with self.assertRaisesRegex(ValueError, "changed during extraction"):
                self.run_extraction("out")
        self.assertFalse((self.base / "out/features.csv").exists())
        self.assertTrue((self.base / "out/features.csv.partial").exists())

    def test_comparison_counts_keep_all_rows_and_warn_sparse(self):
        _, _, frame = self.run_extraction("out")
        groups = condition_groups(frame)
        self.assertEqual(sum(summary["n"] for summary, _ in groups), 3)
        self.assertTrue(all(summary["sparse_n_lt20"] for summary, _ in groups))
        self.assertEqual(sum(summary["n_row_warning"] for summary, _ in groups), 3)
