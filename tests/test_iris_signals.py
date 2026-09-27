"""Regression checks for denominators, sparse calendars, selection and lag tails."""

import tempfile
import unittest
from pathlib import Path

import pandas as pd

from src.iris_signals import (
    OTHER, build_tables, category_summary, closure_histogram, composition_counts, composition_shares,
    daily_metrics, read_prepared, validate_prepared, volume_lag_correlation,
    weekday_summary,
)
from src.profile_iris import markdown_table


def sample_frame():
    registration = pd.to_datetime(["2025-01-01", "2025-01-15", "2025-01-15", "2025-01-15"])
    lag = pd.Series([0, 3, 60, 61])
    return pd.DataFrame({
        "fitxa_id": [1, 2, 3, 4], "registration_date": registration,
        "closure_date": registration + pd.to_timedelta(lag, unit="D"),
        "closure_lag_days": lag, "area": ["cleaning", "cleaning", "parks", None],
        "district": ["A", "A", "A", None], "support": ["mobile", "mobile", "web", None],
        "request_type": ["INCIDENCIA", "INCIDENCIA", "ISSUE", "ISSUE"],
    })


class SignalTests(unittest.TestCase):
    def test_missing_district_group_retains_its_missingness(self):
        summary = category_summary(sample_frame(), "district").set_index("district")
        self.assertEqual(summary.loc["(missing)", "missing_district_rows"], 1)
        self.assertEqual(summary.loc["(missing)", "missing_district_percent"], 100)
        self.assertEqual(summary.loc["A", "missing_district_rows"], 0)

    def test_markdown_table_accepts_categorical_and_nullable_columns(self):
        table = pd.DataFrame({
            "category": pd.Categorical(["a", None]),
            "count": pd.Series([1, None], dtype="Int64"),
        })
        rendered = markdown_table(table)
        self.assertIn("category", rendered)
        self.assertIn("a", rendered)
        self.assertNotIn("<NA>", rendered)

    def test_sparse_calendar_has_zeros_and_true_seven_day_window(self):
        daily = daily_metrics(sample_frame(), pd.Timestamp("2025-01-01"), pd.Timestamp("2025-01-15"))
        self.assertEqual(len(daily), 15)
        self.assertEqual(daily["requests"].sum(), 4)
        self.assertEqual(daily.loc[1, "requests"], 0)
        self.assertTrue(pd.isna(daily.loc[1, "median_closure_lag_days"]))
        self.assertTrue(daily.loc[:5, "rolling_7_day"].isna().all())
        self.assertAlmostEqual(daily.loc[6, "rolling_7_day"], 1 / 7)
        self.assertAlmostEqual(daily.loc[14, "rolling_7_day"], 3 / 7)

    def test_weekday_denominator_includes_zero_record_days(self):
        daily = daily_metrics(sample_frame(), pd.Timestamp("2025-01-01"), pd.Timestamp("2025-01-15"))
        wednesday = weekday_summary(daily).set_index("weekday").loc["Wednesday"]
        self.assertEqual(wednesday["calendar_days"], 3)
        self.assertAlmostEqual(wednesday["mean_daily_requests"], 4 / 3)

    def test_weekday_outside_selected_range_is_undefined(self):
        daily = daily_metrics(sample_frame(), pd.Timestamp("2025-01-01"), pd.Timestamp("2025-01-01"))
        monday = weekday_summary(daily).set_index("weekday").loc["Monday"]
        self.assertTrue(pd.isna(monday["mean_daily_requests"]))

    def test_composition_retains_smaller_and_missing_categories(self):
        frame = sample_frame()
        counts = composition_counts(frame, "district", "area", top_columns=1)
        shares = composition_shares(counts)
        self.assertEqual(counts.loc["A"].sum(), 3)
        self.assertEqual(counts.loc["A", OTHER], 1)
        self.assertEqual(counts.loc["(missing)", OTHER], 1)
        self.assertAlmostEqual(shares.loc["A", "cleaning"], 200 / 3)
        self.assertTrue(shares.sum(axis=1).round(9).eq(100).all())

    def test_lag_histogram_preserves_zero_sixty_and_overflow(self):
        counts = closure_histogram(sample_frame()).set_index("lag_days")["requests"]
        self.assertEqual(counts.sum(), 4)
        self.assertEqual(counts.loc["0"], 1)
        self.assertEqual(counts.loc["31–60"], 1)
        self.assertEqual(counts.loc[">60"], 1)

    def test_all_summary_counts_reconcile_with_headline_cohort(self):
        frame = sample_frame()
        older = frame.iloc[[0]].copy()
        older["fitxa_id"] = 5
        older["registration_date"] = pd.Timestamp("2024-12-31")
        older["closure_lag_days"] = 1
        frame = pd.concat([frame, older], ignore_index=True)
        validate_prepared(frame)
        tables = build_tables(frame)
        for name in ["daily", "weekday", "monthly", "areas", "districts", "channels", "request_types", "closure_lag"]:
            with self.subTest(table=name):
                self.assertEqual(tables[name]["requests"].sum(), 4)
        self.assertEqual(tables["monthly"]["closures_all_export"].sum(), 5)
        december = tables["monthly"].set_index("month").loc["2025-12"]
        self.assertEqual(december["max_observable_lag_at_month_start"], 30)
        self.assertEqual(december["max_observable_lag_at_month_end"], 0)

    def test_undefined_correlation_is_not_a_number_claim(self):
        self.assertIsNone(volume_lag_correlation(pd.DataFrame({
            "requests": [1, 1, 1], "median_closure_lag_days": [0, 2, 4],
        })))
        self.assertIsNone(volume_lag_correlation(pd.DataFrame({
            "requests": [1, 2], "median_closure_lag_days": [0, 4],
        })))

    def test_input_validation_rejects_conflicting_records_and_dates(self):
        frame = sample_frame()
        validate_prepared(frame)
        for column, value in [("fitxa_id", 2), ("registration_date", pd.NaT),
                              ("closure_lag_days", -1), ("closure_date", pd.Timestamp("2026-01-01"))]:
            broken = frame.copy()
            broken.loc[0, column] = value
            with self.subTest(column=column), self.assertRaises(ValueError):
                validate_prepared(broken)

    def test_invalid_csv_date_fails_with_clear_message(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "bad.csv"
            frame = sample_frame().astype({"registration_date": "str"})
            frame.loc[0, "registration_date"] = "not-a-date"
            frame.to_csv(path, index=False)
            with self.assertRaisesRegex(ValueError, "registration_date"):
                read_prepared(path)


if __name__ == "__main__":
    unittest.main()
