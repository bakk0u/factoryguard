"""Generated B01-format fixtures; no redistributed raw dataset samples."""
from pathlib import Path
import shutil
import tempfile
import unittest

import numpy as np
import pandas as pd
from scipy.io import savemat

from factoryguard.data.paderborn import (
    B01Experiment, CHANNELS, OPERATING_COLUMNS, SAMPLE_COUNT, SAMPLE_RATE_HZ,
    TEMPERATURE_COLUMNS, load_recording, load_table,
)


class PaderbornTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.path = self.root / "data_B01_M0001.mat"
        self.time = np.arange(SAMPLE_COUNT, dtype=float) / SAMPLE_RATE_HZ
        self.a = np.sin(2 * np.pi * 100 * self.time).reshape(-1, 1)
        self.c = np.full((SAMPLE_COUNT, 1), -0.25)

    def write_mat(self, **overrides):
        data = {CHANNELS[0]: self.a, CHANNELS[1]: self.c, "measTime": self.time.reshape(-1, 1)}
        data.update(overrides)
        savemat(self.path, data)

    def make_tables(self):
        for name, columns in (("meanTemperatures", TEMPERATURE_COLUMNS),
                              ("operatingConditions", OPERATING_COLUMNS)):
            frame = pd.DataFrame({"Time": ["19-Oct-2021 08:46:54", "19-Oct-2021 08:47:06"],
                                  **{column: [1.0, 2.0] for column in columns}})
            frame.to_csv(self.root / f"B01_{name}.csv", index=False)

    def make_experiment(self):
        self.make_tables()
        directory = self.root / "vibrationData"
        directory.mkdir()
        self.write_mat()
        shutil.copyfile(self.path, directory / self.path.name)
        shutil.copyfile(self.path, directory / "data_B01_M0002.mat")

    def test_voltage_roundtrip_and_source_unchanged(self):
        self.write_mat()
        before = self.path.read_bytes()
        result = load_recording(self.path)
        self.assertEqual(result.measurement_id, 1)
        np.testing.assert_array_equal(result.rear_a_volts, self.a[:, 0])
        np.testing.assert_array_equal(result.frontal_c_volts, self.c[:, 0])
        np.testing.assert_array_equal(result.sample_time_seconds, self.time)
        self.assertEqual(self.path.read_bytes(), before)

    def test_row_vector_supported(self):
        self.write_mat(**{CHANNELS[0]: self.a.T})
        self.assertEqual(load_recording(self.path).rear_a_volts.shape, (SAMPLE_COUNT,))

    def test_missing_channel_and_wrong_shape(self):
        savemat(self.path, {"measTime": self.time})
        with self.assertRaisesRegex(ValueError, "missing MAT variable"):
            load_recording(self.path)
        self.write_mat(**{CHANNELS[0]: np.zeros((1024, 200))})
        with self.assertRaisesRegex(ValueError, "double vector"):
            load_recording(self.path)

    def test_nonfinite_and_complex_channels(self):
        for value in (np.nan, np.inf, 1j):
            with self.subTest(value=value):
                channel = self.a.astype(complex if value == 1j else float)
                channel[4, 0] = value
                self.write_mat(**{CHANNELS[0]: channel})
                with self.assertRaisesRegex(ValueError, "complex or nonfinite"):
                    load_recording(self.path)

    def test_reject_bad_sample_grid(self):
        for change in ("reversed", "rate", "gap", "offset"):
            with self.subTest(change=change):
                times = self.time.copy()
                if change == "reversed":
                    times = times[::-1]
                elif change == "rate":
                    times *= 2
                elif change == "gap":
                    times[5] = times[4]
                else:
                    times += 1
                self.write_mat(measTime=times.reshape(-1, 1))
                with self.assertRaisesRegex(ValueError, "sample grid"):
                    load_recording(self.path)

    def test_foreign_filename_and_corrupt_file(self):
        with self.assertRaisesRegex(ValueError, "Not a B01"):
            load_recording(self.root / "data_B02_M0001.mat")
        self.path.write_bytes(b"not a MAT file")
        with self.assertRaises(ValueError):
            load_recording(self.path)

    def test_observed_headers_naive_times_and_no_mutation(self):
        self.make_tables()
        path = self.root / "B01_meanTemperatures.csv"
        before = path.read_bytes()
        frame = load_table(path, TEMPERATURE_COLUMNS)
        self.assertIsNone(frame.source_time.dt.tz)
        self.assertEqual(frame.Time.iloc[0], "19-Oct-2021 08:46:54")
        self.assertEqual(before, path.read_bytes())

    def test_reject_general_pdf_headers(self):
        self.make_tables()
        path = self.root / "B01_meanTemperatures.csv"
        pd.read_csv(path).rename(columns={"Time": "dateTime"}).to_csv(path, index=False)
        with self.assertRaisesRegex(ValueError, "unexpected columns"):
            load_table(path, TEMPERATURE_COLUMNS)

    def test_bad_table_timestamps(self):
        for values in (["bad", "bad"], ["19-Oct-2021 08:46:54"] * 2,
                       ["19-Oct-2021 08:47:06", "19-Oct-2021 08:46:54"]):
            with self.subTest(values=values):
                self.make_tables()
                path = self.root / "B01_meanTemperatures.csv"
                frame = pd.read_csv(path)
                frame["Time"] = values
                frame.to_csv(path, index=False)
                with self.assertRaisesRegex(ValueError, "Time"):
                    load_table(path, TEMPERATURE_COLUMNS)

    def test_bad_table_numeric_values_and_empty(self):
        for value in (np.nan, np.inf, "broken"):
            with self.subTest(value=value):
                self.make_tables()
                path = self.root / "B01_meanTemperatures.csv"
                frame = pd.read_csv(path).astype({TEMPERATURE_COLUMNS[0]: object})
                frame.loc[0, TEMPERATURE_COLUMNS[0]] = value
                frame.to_csv(path, index=False)
                with self.assertRaisesRegex(ValueError, "nonfinite"):
                    load_table(path, TEMPERATURE_COLUMNS)
        frame.iloc[:0].to_csv(path, index=False)
        with self.assertRaisesRegex(ValueError, "empty"):
            load_table(path, TEMPERATURE_COLUMNS)

    def test_inventory_and_table_alignment(self):
        self.make_experiment()
        self.assertEqual(len(B01Experiment(self.root, expected_measurements=2).paths), 2)
        with self.assertRaisesRegex(ValueError, "inventory"):
            B01Experiment(self.root)  # a two-row fixture is not a complete 377-record B01
        path = self.root / "B01_operatingConditions.csv"
        frame = pd.read_csv(path)
        frame.loc[1, "Time"] = "19-Oct-2021 08:47:07"
        frame.to_csv(path, index=False)
        with self.assertRaisesRegex(ValueError, "align exactly"):
            B01Experiment(self.root, expected_measurements=2)

    def test_missing_measurement_not_silently_skipped(self):
        self.make_experiment()
        path = self.root / "vibrationData/data_B01_M0002.mat"
        path.rename(path.with_name("data_B01_M0003.mat"))
        with self.assertRaisesRegex(ValueError, "inventory"):
            B01Experiment(self.root, expected_measurements=2)

    def test_lazy_recording_iteration(self):
        self.make_experiment()
        # Corrupt the second file. Construction and first consumption must not
        # materialize later signals; the error appears at second consumption.
        (self.root / "vibrationData/data_B01_M0002.mat").write_bytes(b"not MAT")
        experiment = B01Experiment(self.root, expected_measurements=2)
        iterator = experiment.recordings()
        self.assertEqual(next(iterator).measurement_id, 1)
        with self.assertRaises(ValueError):
            next(iterator)
