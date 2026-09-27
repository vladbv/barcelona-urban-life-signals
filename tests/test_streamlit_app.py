"""Exercise the viewer against a small controlled CSV, without a browser server."""

from datetime import date
from pathlib import Path
import tempfile
import unittest

import pandas as pd
from streamlit.testing.v1 import AppTest

from test_iris_signals import sample_frame


class ViewerTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.path = Path(self.directory.name) / "prepared.csv"
        sample_frame().to_csv(self.path, index=False)
        source = Path("streamlit_app.py").read_text(encoding="utf-8").replace(
            'DATA_PATH = Path("data/processed/iris_2025_clean.csv")',
            f"DATA_PATH = Path({str(self.path)!r})",
        )
        self.app = AppTest.from_string(source, default_timeout=30)

    def metric(self, label):
        return next(item.value for item in self.app.metric if item.label == label)

    def test_default_view_and_empty_date_range(self):
        self.app.run()
        self.assertFalse(self.app.exception)
        self.assertEqual(self.metric("Observed requests"), "4")
        self.assertTrue(any("Generate the full-year report for this data snapshot" in item.value for item in self.app.caption))
        self.app.date_input[0].set_value((date(2025, 1, 2), date(2025, 1, 14))).run()
        self.assertFalse(self.app.exception)
        self.assertTrue(any("No records match" in item.value for item in self.app.warning))
        self.assertEqual(len(self.app.metric), 0)

    def test_missing_district_filter_and_single_day(self):
        self.app.run()
        self.app.multiselect[1].select("(missing)").run()
        self.assertFalse(self.app.exception)
        self.assertEqual(self.metric("Observed requests"), "1")
        self.assertEqual(self.metric("Missing district"), "100.0%")
        self.app.date_input[0].set_value((date(2025, 1, 15), date(2025, 1, 15))).run()
        self.assertFalse(self.app.exception)
        self.assertEqual(self.metric("Mean per calendar day"), "1.0")
        self.assertTrue(any("not estimable" in item.value for item in self.app.caption))

    def test_incomplete_date_range_is_not_silently_reset(self):
        self.app.run()
        self.app.date_input[0].set_value((date(2025, 1, 1),)).run()
        self.assertFalse(self.app.exception)
        self.assertTrue(any("Select an end date" in item.value for item in self.app.info))
        self.assertEqual(len(self.app.metric), 0)

    def test_changed_input_invalidates_cached_data(self):
        self.app.run()
        frame = sample_frame()
        added = frame.iloc[[0]].copy()
        added["fitxa_id"] = 5
        pd.concat([frame, added]).to_csv(self.path, index=False)
        self.app.run()
        self.assertFalse(self.app.exception)
        self.assertEqual(self.metric("Observed requests"), "5")

    def test_missing_input_is_actionable(self):
        self.path.unlink()
        self.app.run()
        self.assertFalse(self.app.exception)
        self.assertTrue(any("dataset is missing" in item.value for item in self.app.error))


if __name__ == "__main__":
    unittest.main()
