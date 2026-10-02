"""Preserve original snapshots and reject incomplete downloads."""
import io
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from src import data_catalog


class DownloadTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.root = Path(self.directory.name)
        self.destination = self.root / "snapshot.csv"
        self.resources = [{"id": "test", "url": "https://example.org/data.csv"}]
        patcher = patch.object(data_catalog, "RAW_DATA_DIR", self.root)
        patcher.start()
        self.addCleanup(patcher.stop)

    def response(self, body, length):
        response = io.BytesIO(body)
        response.headers = {"Content-Length": str(length)}
        return response

    def test_complete_download_installed_without_temporary_files(self):
        with patch.object(data_catalog, "urlopen", return_value=self.response(b"a,b\n", 4)):
            data_catalog.download_resource(self.resources, "test", self.destination)
        self.assertEqual(self.destination.read_bytes(), b"a,b\n")
        self.assertEqual(list(self.root.iterdir()), [self.destination])

    def test_truncated_download_leaves_no_snapshot(self):
        with patch.object(data_catalog, "urlopen", return_value=self.response(b"a", 10)):
            with self.assertRaisesRegex(ValueError, "Incomplete"):
                data_catalog.download_resource(self.resources, "test", self.destination)
        self.assertEqual(list(self.root.iterdir()), [])

    def test_existing_snapshot_is_never_overwritten(self):
        self.destination.write_bytes(b"original")
        with patch.object(data_catalog, "urlopen") as fetch:
            with self.assertRaises(FileExistsError):
                data_catalog.download_resource(self.resources, "test", self.destination)
            fetch.assert_not_called()
        self.assertEqual(self.destination.read_bytes(), b"original")


if __name__ == "__main__":
    unittest.main()
