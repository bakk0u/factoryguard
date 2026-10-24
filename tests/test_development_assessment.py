"""Generated development fixtures; held-out guards are tested without real B03 I/O."""
from pathlib import Path
import tempfile
import contextlib
import io
import unittest
from unittest.mock import patch

import numpy as np
import pandas as pd
from scipy.io import savemat

from factoryguard.data.paderborn import (
    DevelopmentExperiment, SAMPLE_COUNT, SAMPLE_RATE_HZ, CHANNELS,
    OPERATING_COLUMNS, TEMPERATURE_COLUMNS, load_recording,
)
from factoryguard.features.b01_plots import plot_comparisons
from factoryguard.pipelines.assess_development import cross_support, main, combined_load_check
from factoryguard.pipelines.features_paderborn import burst_rows, extract_b01, raw_manifest


class DevelopmentAssessmentTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.time = np.arange(SAMPLE_COUNT) / SAMPLE_RATE_HZ
        self.sine = np.sin(2 * np.pi * 50 * self.time)

    def fixture(self, run):
        root = self.root / run
        (root / "vibrationData").mkdir(parents=True)
        times = ["17-Nov-2021 13:44:59", "17-Nov-2021 13:45:01"]
        for suffix, columns in (("meanTemperatures", TEMPERATURE_COLUMNS), ("operatingConditions", OPERATING_COLUMNS)):
            frame = pd.DataFrame({"Time": times, **{c: [25., 25.] for c in columns}})
            if suffix == "operatingConditions":
                frame["setSpeed / rpm"] = [3500., 3500.]
                frame["meanAbs_speed / rpm"] = [1750., 1750.]
                frame["setStatLoad / N"] = [3500., 3500.]
                frame["setDynLoad / N"] = [1000., 1000.]
            frame.to_csv(root / f"{run}_{suffix}.csv", index=False)
        for n in (1, 2):
            self.write_mat(root, run, n)
        return root

    def write_mat(self, root, run, n, *, times=None, values=None):
        savemat(root / f"vibrationData/data_{run}_M{n:04d}.mat", {
            CHANNELS[0]: (self.sine if values is None else values).reshape(-1, 1),
            CHANNELS[1]: np.full((SAMPLE_COUNT, 1), .1),
            "measTime": (self.time if times is None else times).reshape(-1, 1),
        })

    def test_explicit_run_inventory_and_compatible_features(self):
        for run in ("B02", "B04"):
            root = self.fixture(run)
            experiment = DevelopmentExperiment(root, experiment=run, expected_measurements=2)
            before = raw_manifest(root)
            rows = list(burst_rows(experiment, before))
            self.assertEqual(len(rows), 2)
            self.assertEqual(rows[0]["provenance__experiment"], run)
            self.assertAlmostEqual(rows[0]["feature__A_ac_rms_v"], 1 / np.sqrt(2))
            self.assertAlmostEqual(rows[0]["feature__A_excess_kurtosis"], -1.5)
            self.assertTrue(np.isnan(rows[0]["feature__C_crest_factor"]))
            self.assertTrue(rows[0]["quality__C_crest_factor_undefined"])
            self.assertEqual(raw_manifest(root), before)

    def test_b04_documented_policy_and_uncertainty_not_b01_ranges(self):
        root = self.fixture("B04")
        e = DevelopmentExperiment(root, experiment="B04", expected_measurements=2)
        rows = list(burst_rows(e, raw_manifest(root)))
        self.assertTrue(rows[0]["quality__initial_setpoint_policy_ambiguous"])
        self.assertFalse(rows[0]["quality__speed_setpoint_outside_main_range"])
        self.assertTrue(rows[0]["quality__any_warning"])
        self.assertFalse(rows[1]["quality__initial_setpoint_policy_ambiguous"])
        self.assertTrue(rows[1]["quality__speed_setpoint_outside_main_range"])

    def test_every_sample_grid_and_finiteness_checked_for_both_runs(self):
        for run in ("B02", "B04"):
            root = self.fixture(run)
            path = root / f"vibrationData/data_{run}_M0001.mat"
            self.assertEqual(len(load_recording(path, experiment=run).sample_time_seconds), SAMPLE_COUNT)
            times = self.time.copy()
            times[-2] = times[-3]
            self.write_mat(root, run, 1, times=times)
            with self.assertRaisesRegex(ValueError, "sample grid"):
                load_recording(path, experiment=run)
            values = self.sine.copy()
            values[-1] = np.inf
            self.write_mat(root, run, 1, values=values)
            with self.assertRaisesRegex(ValueError, "nonfinite"):
                load_recording(path, experiment=run)

    def test_b04_earlier_rows_independent_of_future_context_and_signal(self):
        root = self.fixture("B04")
        e = DevelopmentExperiment(root, experiment="B04", expected_measurements=2)
        first = pd.DataFrame(list(burst_rows(e, raw_manifest(root))))
        self.write_mat(root, "B04", 2, values=self.sine * 7)
        for suffix in ("meanTemperatures", "operatingConditions"):
            path = root / f"B04_{suffix}.csv"
            table = pd.read_csv(path)
            table.iloc[1, 1:] += 10
            table.to_csv(path, index=False)
        e = DevelopmentExperiment(root, experiment="B04", expected_measurements=2)
        second = pd.DataFrame(list(burst_rows(e, raw_manifest(root))))
        pd.testing.assert_frame_equal(first.iloc[:1], second.iloc[:1])
        self.assertNotEqual(first.feature__A_ac_rms_v.iloc[1], second.feature__A_ac_rms_v.iloc[1])

    def test_heldout_denied_before_any_waveform_or_table_io(self):
        with patch("factoryguard.data.paderborn.loadmat", side_effect=AssertionError("Held-out waveform access")), \
             patch("factoryguard.data.paderborn.load_table", side_effect=AssertionError("Held-out table access")):
            with self.assertRaisesRegex(ValueError, "access denied"):
                load_recording(self.root / "data_B03_M0001.mat", experiment="B03")
            with self.assertRaisesRegex(ValueError, "access denied"):
                DevelopmentExperiment(self.root, experiment="B03")
            with self.assertRaisesRegex(ValueError, "access denied"):
                extract_b01(self.root, self.root / "output", experiment_id="B03")
        frame = pd.DataFrame({"provenance__experiment": ["B03"]})
        with self.assertRaisesRegex(ValueError, "access denied"):
            plot_comparisons(frame, self.root)
        with self.assertRaisesRegex(ValueError, "access denied"):
            cross_support({"B03": frame})

    def test_native_measured_bins_preserve_absent_support(self):
        def frame(run, speed):
            return pd.DataFrame({"provenance__experiment": [run], "context__measured_speed_rpm": [speed],
                                 "context__measured_static_load_n": [3500.], "context__measured_dynamic_peak_n": [700.],
                                 **{f"quality__{name}": [False] for name in [
                                     "documented_warmup_setpoints", "any_warning", "A_sensor_range_exceeded", "C_sensor_range_exceeded",
                                     "speed_setpoint_outside_main_range", "static_load_setpoint_outside_main_range",
                                     "dynamic_load_setpoint_outside_main_range", "preceding_gap_gt24s"]}})
        support = cross_support({"B01": frame("B01", 2600), "B02": frame("B02", 2601), "B04": frame("B04", 1300)})
        self.assertEqual(len(support), 2)
        matched = support.loc[support.speed_lower_rpm.eq(2500)].iloc[0]
        self.assertEqual((matched.B01_n, matched.B02_n, matched.B04_n), (1, 1, 0))
        self.assertEqual(int(support.B04_n.sum()), 1)

    def test_assessment_cannot_write_under_heldout_or_other_raw_directories(self):
        with patch("sys.argv", ["assess_development", "--output", "/workspace/datasets/paderborn-10868257/raw/B03/derived"]), \
             patch.object(Path, "mkdir", side_effect=AssertionError("Raw directory write attempted")), \
             contextlib.redirect_stderr(io.StringIO()):
            with self.assertRaises(SystemExit) as raised:
                main()
        self.assertEqual(raised.exception.code, 2)

    def test_combined_load_boundary_roundoff_not_a_physical_excursion(self):
        frame = pd.DataFrame({"context__set_static_load_n": [3300., 3300., 2500.],
                              "context__set_dynamic_amplitude_n": [1000.-5e-12, 999., 0.],
                              "quality__documented_warmup_setpoints": [False, False, True]})
        _, outside, bounds = combined_load_check("B02", frame)
        self.assertEqual(bounds, (4300., 4900.))
        self.assertEqual(outside.tolist(), [False, True, False])
