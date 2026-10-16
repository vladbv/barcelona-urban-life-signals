"""Check count selection, conjugacy and separation of training from later labels."""
import unittest
from unittest.mock import patch

import numpy as np
import pandas as pd

from src.model_iris_counts import AREA, ORIGIN, daily_outcome, evaluate, gamma_update, split_days


def record(identifier, lag, area=AREA):
    registered = pd.Timestamp('2025-12-31')
    return {'fitxa_id': identifier, 'area': area, 'registration_date': registered,
            'closure_date': registered + pd.Timedelta(days=lag), 'closure_lag_days': lag}


def calendar_counts():
    dates = pd.date_range('2025-01-01', '2025-12-31')
    return pd.DataFrame({'date': dates, 'count': 20 + dates.dayofweek * 3,
                         'weekday': dates.dayofweek, 'day_of_year': dates.dayofyear})


class CountModelTests(unittest.TestCase):
    def test_conjugacy_counts_zero_days_as_exposure(self):
        self.assertEqual(gamma_update([0, 2, 4], alpha=2, beta=1), (8, 4))
        self.assertEqual(gamma_update([0, 0], alpha=2, beta=1), (2, 3))

    def test_rejects_invalid_counts_and_priors(self):
        for counts in ([], [-1], [1.5], [np.nan], [[1, 2]]):
            with self.subTest(counts=counts), self.assertRaises(ValueError):
                gamma_update(counts)
        for alpha, beta in ((0, 1), (1, -1), (np.inf, 1), (1, np.nan)):
            with self.subTest(alpha=alpha, beta=beta), self.assertRaises(ValueError):
                gamma_update([1], alpha, beta)

    def test_outcome_counts_inclusive_boundaries_and_keeps_zero_days(self):
        frame = pd.DataFrame([record(1, 0), record(2, 30), record(3, 31),
                              record(4, 90), record(5, 0, 'Different category')])
        for horizon, expected in ((30, 2), (90, 4)):
            daily = daily_outcome(frame, horizon)
            self.assertEqual(len(daily), 365)
            self.assertEqual(daily['count'].sum(), expected)
            self.assertEqual(daily['count'].iloc[-1], expected)
            self.assertTrue(daily['count'].iloc[:-1].eq(0).all())

    def test_invalid_source_records_are_rejected(self):
        frame = pd.DataFrame([record(1, 0), record(2, 30)])
        for column, value in [('fitxa_id', 1), ('closure_lag_days', 29),
                              ('closure_date', pd.Timestamp('2026-04-01'))]:
            invalid = frame.copy()
            invalid.loc[1, column] = value
            with self.subTest(column=column), self.assertRaises(ValueError):
                daily_outcome(invalid, 30)
        with self.assertRaises(ValueError):
            daily_outcome(frame.assign(area='Unknown category'), 30)

    def test_only_mature_labels_enter_training(self):
        for horizon, end in ((30, '2025-08-31'), (90, '2025-07-02')):
            train, test = split_days(calendar_counts(), horizon)
            self.assertEqual(train.date.max(), pd.Timestamp(end))
            self.assertTrue((train.date + pd.Timedelta(days=horizon) < ORIGIN).all())
            self.assertEqual(test.date.min(), ORIGIN)
            self.assertEqual(len(test), 92)
            self.assertTrue(set(train.date).isdisjoint(test.date))

    @patch('src.model_iris_counts.DRAWS', 1000)
    def test_future_and_immature_labels_cannot_change_predictions(self):
        daily = calendar_counts()
        original = evaluate(daily, 30)
        altered = daily.copy()
        altered.loc[altered.date.gt('2025-08-31'), 'count'] += 1000
        changed = evaluate(altered, 30)
        columns = ['Weekday average', 'Gamma–Poisson', 'Decision tree',
                   'predictive_low', 'predictive_high']
        pd.testing.assert_frame_equal(original['predictions'][columns],
                                      changed['predictions'][columns])
        self.assertGreater(changed['metrics'].MAE.min(), original['metrics'].MAE.max())
        posterior = original['posterior'].iloc[0]
        self.assertAlmostEqual(posterior.posterior_mean,
                               (2 + posterior.sum_counts) / (.01 + posterior.train_days))
        self.assertGreater(posterior.predictive_high - posterior.predictive_low,
                           posterior.rate_high - posterior.rate_low)


if __name__ == '__main__':
    unittest.main()
