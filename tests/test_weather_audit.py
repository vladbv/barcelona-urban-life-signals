"""Check join cardinality and the distinction between absent weather and zero rain."""
import unittest

import pandas as pd

from src.audit_weather import VARIABLE, inspect_frames


def inputs():
    weather = pd.DataFrame({'DATA_LECTURA': ['2025-01-01', '2025-01-01', '2025-01-02'],
                            'CODI_ESTACIO': ['X4'] * 3, VARIABLE: ['TM', 'PPT', 'PPT'],
                            'VALOR': [10.0, 0.0, 2.0]})
    variables = pd.DataFrame({VARIABLE: ['TM', 'PPT'], 'UNITAT': ['°C', 'mm']})
    stations = pd.DataFrame({'CODI_ESTACIO': ['X4', 'X4', 'X2'],
                             'NOM_ESTACIO': ['Raval', 'Raval', 'Zoo'],
                             'ALTITUD': [33, 33, 7], 'LATITUD': [41.38, 41.38, 41.39],
                             'LONGITUD': [2.16, 2.16, 2.18], VARIABLE: ['TM', 'PPT', 'TM']})
    return weather, variables, stations


class WeatherAuditTests(unittest.TestCase):
    def test_sensor_metadata_cannot_multiply_observations(self):
        daily, summary, identities, naive = inspect_frames(*inputs())
        self.assertEqual(naive, 6)
        self.assertEqual(len(identities), 2)
        self.assertEqual(daily.record_present.sum(), 3)
        self.assertEqual(summary['Recorded days'].sum(), 3)
        self.assertFalse(daily.duplicated(['date', 'station', 'variable']).any())

    def test_missing_and_zero_rain_remain_distinct(self):
        daily, summary, _, _ = inspect_frames(*inputs())
        values = daily.set_index(['station', 'variable', 'date'])
        dry = values.loc[('X4', 'PPT', pd.Timestamp('2025-01-01'))]
        absent = values.loc[('X4', 'TM', pd.Timestamp('2025-01-02'))]
        self.assertEqual(dry.value, 0)
        self.assertTrue(dry.record_present)
        self.assertTrue(pd.isna(absent.value))
        self.assertFalse(absent.record_present)
        self.assertTrue(summary.loc[summary.Station.eq('X2'), 'Absent dates'].eq(365).all())

    def test_duplicate_keys_and_conflicting_metadata_are_rejected(self):
        weather, variables, stations = inputs()
        with self.assertRaisesRegex(ValueError, 'unique'):
            inspect_frames(pd.concat([weather, weather.iloc[:1]]), variables, stations)
        stations.loc[1, 'ALTITUD'] = 99
        with self.assertRaisesRegex(ValueError, 'Conflicting'):
            inspect_frames(weather, variables, stations)

    def test_unknown_keys_units_and_negative_rain_are_rejected(self):
        for case in ('unknown_station', 'wrong_unit', 'negative_rain'):
            weather, variables, stations = inputs()
            if case == 'unknown_station':
                weather.loc[0, 'CODI_ESTACIO'] = 'ZZ'
            elif case == 'wrong_unit':
                variables.loc[1, 'UNITAT'] = 'cm'
            else:
                weather.loc[1, 'VALOR'] = -1
            with self.subTest(case=case), self.assertRaises(ValueError):
                inspect_frames(weather, variables, stations)

    def test_null_measurement_is_not_an_absent_row(self):
        weather, variables, stations = inputs()
        weather.loc[0, 'VALOR'] = float('nan')
        _, summary, _, _ = inspect_frames(weather, variables, stations)
        row = summary.loc[summary.Station.eq('X4') & summary.Variable.eq('Mean temperature')].iloc[0]
        self.assertEqual(row['Recorded days'], 1)
        self.assertEqual(row['Numeric days'], 0)
        self.assertEqual(row['Null values'], 1)
        self.assertEqual(row['Absent dates'], 364)


if __name__ == '__main__':
    unittest.main()
