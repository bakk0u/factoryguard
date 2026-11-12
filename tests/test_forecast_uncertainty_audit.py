"""Synthetic checks for the read-only forecast uncertainty audit."""
import importlib.util
from pathlib import Path
import unittest

SPEC = importlib.util.spec_from_file_location(
    'forecast_uncertainty_audit',
    Path(__file__).resolve().parents[1] / 'scripts/audit_forecast_uncertainty.py'
)
AUDIT = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(AUDIT)


def row(value, step, scored=True):
    return {'rms_v': [value, value + 1],
            'resolved': {'status': 'scored' if scored else 'expired_gap',
                         'forecast_v': [value - step, value + 1 - step],
                         'persistence_v': [value - 2 * step, value + 1 - 2 * step]}}


class ForecastUncertaintyAuditTests(unittest.TestCase):
    def test_uses_only_scored_finite_past_errors(self):
        rows = [row(5.0, 1.0) for _ in range(60)]
        rows[0] = row(5.0, 999.0, scored=False)
        rows[10]['resolved']['forecast_v'][0] = None
        self.assertEqual(len(AUDIT.errors(rows, 'A', 'smoothing')), 58)
        result = AUDIT.audit_run(rows, 'A', 'smoothing')
        self.assertEqual(result['n_calibration'] + result['n_later'], 58)
        self.assertAlmostEqual(result['half_width_v'], 1.0)
        self.assertEqual(result['covered'], result['n_later'])

    def test_later_errors_do_not_change_calibrated_width(self):
        rows = [row(10.0, 1.0) for _ in range(60)]
        original = AUDIT.audit_run(rows, 'A', 'smoothing')
        for e in rows[15:]:
            e['resolved']['forecast_v'][0] = -100.0
        changed = AUDIT.audit_run(rows, 'A', 'smoothing')
        self.assertEqual(original['half_width_v'], changed['half_width_v'])
        self.assertLess(changed['coverage'], original['coverage'])

    def test_sealed_inventory_enforced(self):
        with self.assertRaisesRegex(ValueError, 'B03'):
            AUDIT.audit_payload({'states': {'B01': {}, 'B02': {}, 'B03': {}, 'B04': {}}})


if __name__ == '__main__':
    unittest.main()
