"""Synthetic checks of the spectral shaft-speed audit (no dataset files needed)."""
import importlib.util
from pathlib import Path
import unittest

import numpy as np

SPEC = importlib.util.spec_from_file_location(
    'speed_evidence', Path(__file__).resolve().parents[1] / 'scripts/audit_speed_evidence.py')
AUDIT = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(AUDIT)


def burst(shaft_hz, seed=0):
    rng = np.random.default_rng(seed)
    t = np.arange(AUDIT.N) / AUDIT.FS
    x = sum(np.sin(2 * np.pi * k * shaft_hz * t) / k for k in range(1, 7)) + rng.normal(0, 2.0, AUDIT.N)
    return np.abs(np.fft.rfft((x - x.mean()) * np.hanning(AUDIT.N)))[: int(700 / AUDIT.DF) + 1]


class SpeedEvidenceTests(unittest.TestCase):
    def test_true_speed_is_prominent_and_half_speed_is_not(self):
        amplitude = burst(45.0)
        self.assertGreater(AUDIT.odd_harmonic_prominence(amplitude, 45.0), 10)
        self.assertLess(AUDIT.odd_harmonic_prominence(amplitude, 22.5), 4)   # the factor-two ambiguity

    def test_free_estimate_recovers_the_shaft_frequency(self):
        for shaft in (27.0, 41.3, 49.6):
            self.assertAlmostEqual(AUDIT.free_estimate(burst(shaft, seed=int(shaft))), shaft, delta=0.5)

    def test_out_of_band_frequency_is_missing_not_guessed(self):
        self.assertTrue(np.isnan(AUDIT.prominence(burst(45.0), 5.0)))

    def test_reserve_run_is_refused(self):
        with self.assertRaisesRegex(ValueError, 'B01/B02/B04'):
            AUDIT.audit_run('/nonexistent', 'B03')

    def test_summary_separates_the_two_hypotheses(self):
        import pandas as pd
        frame = pd.DataFrame({'run': ['B04'] * 4, 'measured_hz': [20.0] * 4, 'commanded_hz': [40.0] * 4,
                              'prominence_at_measured': [2.0] * 4, 'prominence_at_commanded': [50.0] * 4,
                              'prominence_at_half_measured': [2.0] * 4, 'prominence_at_double_measured': [50.0] * 4,
                              'free_estimate_hz': [40.1, 39.8, 40.0, 20.2]})
        s = AUDIT.summarise(frame)['B04']
        self.assertEqual(s['free_estimate_within_1hz_of_commanded'], 0.75)
        self.assertEqual(s['free_estimate_within_1hz_of_measured'], 0.25)
        self.assertEqual(s['share_measured_more_prominent_than_commanded'], 0.0)


if __name__ == '__main__':
    unittest.main()
