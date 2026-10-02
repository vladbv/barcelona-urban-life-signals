"""Check year-end inclusion, fixed follow-up boundaries, and identity conflicts."""
import unittest

import pandas as pd

from src.audit_iris_observation import compare_sources


def record(identifier, registered, closed):
    start, end = pd.Timestamp(registered), pd.Timestamp(closed)
    return {'fitxa_id': identifier, 'registration_date': start, 'closure_date': end,
            'closure_lag_days': (end - start).days, 'area': 'Cleaning', 'element': 'Street',
            'detail': 'Clean', 'request_type': 'Original', 'district': None}


class ObservationTests(unittest.TestCase):
    def setUp(self):
        self.base = pd.DataFrame([record(1, '2025-12-01', '2025-12-01')])
        self.later = pd.DataFrame([
            record(2, '2025-12-31', '2026-01-30'),  # Exactly 30 days.
            record(3, '2025-12-31', '2026-01-31'),  # Excluded at 30 days.
            record(4, '2025-12-31', '2026-03-31'),  # Exactly 90 days.
            record(5, '2026-01-01', '2026-02-01'),  # Outside registration cohort.
        ])

    def test_fixed_windows_include_endpoints_and_exclude_other_registrations(self):
        cohort, daily, monthly, _, cutoff = compare_sources(self.base, self.later)
        day = daily.set_index('registration_date').loc[pd.Timestamp('2025-12-31')]
        self.assertEqual(len(cohort), 4)
        self.assertEqual(day.closed_within_30d, 1)
        self.assertEqual(day.closed_within_90d, 3)
        self.assertEqual(monthly.later_closure_records.sum(), 3)
        self.assertEqual(cutoff, pd.Timestamp('2026-03-31'))
        self.assertEqual(len(daily), 365)

    def test_incomplete_followup_is_unknown_not_zero(self):
        _, daily, monthly, _, _ = compare_sources(self.base, self.later.iloc[[0]])
        last = daily.iloc[-1]
        self.assertTrue(last.eligible_30d)
        self.assertFalse(last.eligible_90d)
        self.assertTrue(pd.isna(last.closed_within_90d))
        self.assertTrue(pd.isna(monthly.iloc[-1].closed_within_90d))

    def test_overlapping_ids_require_investigation(self):
        later = self.later.copy()
        later.loc[0, 'fitxa_id'] = 1
        with self.assertRaisesRegex(ValueError, 'both exports'):
            compare_sources(self.base, later)

    def test_invalid_lags_and_duplicate_ids_are_rejected(self):
        for column, value in [('closure_lag_days', -1), ('fitxa_id', 3)]:
            later = self.later.copy()
            later.loc[0, column] = value
            with self.subTest(column=column), self.assertRaises(ValueError):
                compare_sources(self.base, later)


if __name__ == '__main__':
    unittest.main()
