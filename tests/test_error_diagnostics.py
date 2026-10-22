"""Check error direction, cancellation and denominators without fitting a model."""
import unittest

import numpy as np
import pandas as pd

from src.validate_iris_models import MODELS, summarise_errors


def example():
    frame = pd.DataFrame({'date': pd.to_datetime(['2025-04-01', '2025-04-02',
                                                '2025-04-03', '2025-06-01']),
                          'month': ['April', 'April', 'April', 'June'],
                          'count': [10, 10, 10, 0]})
    for model in MODELS:
        frame[model] = [6.0, 12.0, 10.0, 0.0]
    return frame


class ErrorDiagnosticTests(unittest.TestCase):
    def test_sign_exact_matches_and_month_denominators(self):
        result = summarise_errors(example())
        self.assertEqual(len(result), 6)
        for model in MODELS:
            april = result.set_index(['Month', 'Model']).loc[('April', model)]
            self.assertEqual(april['Days'], 3)
            self.assertEqual(april['Underpredicted days'], 1)
            self.assertEqual(april['Overpredicted days'], 1)
            self.assertEqual(april['Exact days'], 1)
            self.assertAlmostEqual(april['Mean error'], 2 / 3)
            self.assertEqual(april['MAE'], 2)
        june = result.loc[result.Month.eq('June')]
        self.assertTrue(june['Exact days'].eq(1).all())
        self.assertTrue(june.MAE.eq(0).all())
        self.assertTrue(result[['Underpredicted days', 'Overpredicted days', 'Exact days']]
                        .sum(axis=1).eq(result.Days).all())

    def test_cancelling_errors_do_not_disappear_from_mae(self):
        frame = example().iloc[:2].copy()
        for model in MODELS:
            frame[model] = [5.0, 15.0]
        result = summarise_errors(frame)
        self.assertTrue(result['Mean error'].eq(0).all())
        self.assertTrue(result.MAE.eq(5).all())

    def test_invalid_predictions_are_rejected(self):
        for value in [np.nan, np.inf, -1]:
            frame = example()
            frame.loc[0, MODELS[0]] = value
            with self.subTest(value=value), self.assertRaises(ValueError):
                summarise_errors(frame)
        frame = example()
        frame.loc[1, 'date'] = frame.loc[0, 'date']
        with self.assertRaises(ValueError):
            summarise_errors(frame)
        with self.assertRaises(ValueError):
            summarise_errors(example().iloc[:0])


if __name__ == '__main__':
    unittest.main()
