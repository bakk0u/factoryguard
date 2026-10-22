"""Meaningful contract and end-to-end checks; run with unittest."""
from pathlib import Path
import json
import sys
import tempfile
import unittest
import numpy as np
import pandas as pd
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from factoryguard.data.ingest import load_csv
from factoryguard.data.validate import validate_readings
from factoryguard.pipelines.prepare import run_step1

class ValidationTests(unittest.TestCase):
    def setUp(self):
        self.frame = load_csv(ROOT / "data/raw/demo_sensors.csv").iloc[:5].copy()
    def test_valid_input_not_mutated(self):
        before = self.frame.copy(deep=True)
        self.assertTrue(validate_readings(self.frame)["valid"])
        pd.testing.assert_frame_equal(self.frame, before)
    def test_missing_column(self):
        self.assertFalse(validate_readings(self.frame.drop(columns="torque_nm"))["valid"])
    def test_empty(self):
        self.assertFalse(validate_readings(self.frame.iloc[:0])["valid"])
    def test_bad_sensor_values(self):
        for value in [np.nan, np.inf, -1, "broken"]:
            with self.subTest(value=value):
                frame = self.frame.astype({"vibration_mm_s": "object"})
                frame.loc[frame.index[0], "vibration_mm_s"] = value
                self.assertFalse(validate_readings(frame)["valid"])
    def test_blank_machine(self):
        self.frame.loc[0, "machine_id"] = " "
        self.assertFalse(validate_readings(self.frame)["valid"])
    def test_bad_timestamp(self):
        self.frame.loc[0, "timestamp"] = "not-a-date"
        self.assertFalse(validate_readings(self.frame)["valid"])
    def test_duplicates(self):
        frame = pd.concat([self.frame, self.frame.iloc[:1]])
        self.assertFalse(validate_readings(frame)["valid"])
    def test_unsorted(self):
        self.assertFalse(validate_readings(self.frame.iloc[::-1])["valid"])
    def test_gap_is_warning(self):
        result = validate_readings(self.frame.drop(index=2))
        self.assertTrue(result["valid"])
        self.assertTrue(result["warnings"])
    def test_same_timestamp_different_machines(self):
        extra = self.frame.copy(); extra["machine_id"] = "M999"
        self.assertTrue(validate_readings(pd.concat([self.frame, extra]))["valid"])
    def test_end_to_end_and_existing_output_guard(self):
        with tempfile.TemporaryDirectory() as temp:
            output = Path(temp) / "results"
            summary = run_step1(ROOT / "data/raw/demo_sensors.csv", output, "synthetic-demo")
            self.assertEqual(summary["rows"], 1080)
            self.assertGreater((output / "sensor_readings.png").stat().st_size, 1000)
            self.assertTrue(json.loads((output / "validation.json").read_text())["valid"])
            with self.assertRaises(ValueError):
                run_step1(ROOT / "data/raw/demo_sensors.csv", output)
    def test_invalid_input_writes_report_not_plot(self):
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "bad.csv"
            self.frame.drop(columns="torque_nm").to_csv(path, index=False)
            output = Path(temp) / "results"
            with self.assertRaises(ValueError):
                run_step1(path, output)
            self.assertTrue((output / "validation.json").exists())
            self.assertFalse((output / "sensor_readings.png").exists())

if __name__ == "__main__":
    unittest.main()
