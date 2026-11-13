"""Causality, coverage accounting and freeze integrity of the interval calibrators."""
import json
from hashlib import sha256
from pathlib import Path
import unittest

import numpy as np

from factoryguard.evaluation import intervals as iv

ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / 'docs/results/uncertainty-calibration-v1'


class IntervalCalibrationTests(unittest.TestCase):
    def setUp(self):
        rng = np.random.default_rng(7)
        self.errors = np.abs(rng.normal(0, 1, 600))
        self.scale = np.full(600, 2.0)
        self.warm = np.abs(rng.normal(0, 1, 300))
        self.warm_scale = np.full(300, 2.0)

    def test_conformal_quantile_rank(self):
        self.assertEqual(iv.conformal_quantile([], .9), float('inf'))
        self.assertEqual(iv.conformal_quantile([1, 2, 3, 4, 5, 6, 7, 8, 9, 10], .9), 10.0)   # ceil(11*.9)=10
        self.assertEqual(iv.conformal_quantile(list(range(1, 100)), .9), 90.0)

    def test_every_calibrator_is_causal(self):
        """Changing an error can only change widths issued strictly after it."""
        for candidate in iv.candidates():
            base = iv.widths(candidate, self.errors, self.scale, self.warm, self.warm_scale)
            changed_errors = self.errors.copy()
            changed_errors[300] = 1e6
            changed = iv.widths(candidate, changed_errors, self.scale, self.warm, self.warm_scale)
            np.testing.assert_array_equal(base[:301], changed[:301], err_msg=candidate['id'])
            self.assertEqual(len(base), len(self.errors))

    def test_warm_start_issues_a_finite_interval_from_the_first_forecast(self):
        for candidate in iv.candidates():
            widths = iv.widths(candidate, self.errors, self.scale, self.warm, self.warm_scale)
            self.assertTrue(np.isfinite(widths).all(), candidate['id'])
        cold = iv.rolling(self.errors, self.scale, [], [], window=60)
        self.assertTrue(np.isinf(cold[0]))          # without history nothing is claimed

    def test_stationary_coverage_is_near_nominal_and_scored_correctly(self):
        widths = iv.rolling(self.errors, self.scale, self.warm, self.warm_scale, window=240)
        result = iv.score(self.errors, widths)
        self.assertAlmostEqual(result['coverage'], float((self.errors <= widths).mean()))
        self.assertTrue(.85 < result['coverage'] < .95)
        self.assertEqual(len(result['coverage_by_quarter']), 4)
        self.assertLessEqual(result['worst_rolling_coverage'], result['coverage'])

    def test_relative_and_adaptive_bands_follow_a_level_shift(self):
        """Errors that grow with the signal level break a fixed band; the relative adaptive one recovers."""
        level = np.r_[np.full(300, 1.0), np.full(300, 6.0)]
        errors = self.errors * level
        fixed = iv.score(errors, iv.fixed_transfer(errors, level, self.warm))
        adaptive = iv.score(errors, iv.rolling(errors, level, self.warm, np.ones(300), 240, relative=True, gamma=.02))
        self.assertLess(fixed['last_quarter_coverage'], .6)
        self.assertGreater(adaptive['last_quarter_coverage'], .8)

    def test_fixed_early_baseline_abstains_until_calibrated(self):
        widths = iv.fixed_early(self.errors, self.scale)
        self.assertTrue(np.isnan(widths[:150]).all() and np.isfinite(widths[150:]).all())
        self.assertEqual(iv.score(self.errors, widths)['n'], 450)

    def test_frozen_calibrator_matches_committed_development_pairs(self):
        frozen = json.loads((RESULTS / 'frozen_calibrator.json').read_text(encoding='utf-8'))
        self.assertEqual(frozen['development_runs'], ['B01', 'B02'])
        self.assertIn(frozen['selected']['id'], {c['id'] for c in iv.candidates()})
        for run, digest in frozen['pairs_sha256'].items():
            self.assertEqual(sha256((RESULTS / f'pairs_{run}.csv').read_bytes()).hexdigest(), digest)
        self.assertNotIn('B03', json.dumps(frozen['pairs_sha256']))


if __name__ == '__main__':
    unittest.main()
