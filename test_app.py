import json
import tempfile
import unittest
from pathlib import Path

from app import find_entries, load_entries, make_entry, save_entries


class InfoVaultTests(unittest.TestCase):
    def test_save_and_load_entries(self):
        with tempfile.TemporaryDirectory() as directory:
            file_path = Path(directory) / "data" / "entries.json"
            entries = [make_entry("Wi-Fi", "Network: example")]

            save_entries(entries, file_path)

            self.assertEqual(load_entries(file_path), entries)

    def test_load_missing_file_returns_empty_list(self):
        with tempfile.TemporaryDirectory() as directory:
            file_path = Path(directory) / "missing.json"

            self.assertEqual(load_entries(file_path), [])

    def test_search_matches_title_and_content_case_insensitively(self):
        entries = [
            make_entry("Wi-Fi", "Network password is stored securely"),
            make_entry("Shopping", "Buy coffee"),
        ]

        results = find_entries(entries, "COFFEE")

        self.assertEqual([entry["title"] for entry in results], ["Shopping"])

    def test_load_rejects_invalid_data_shape(self):
        with tempfile.TemporaryDirectory() as directory:
            file_path = Path(directory) / "entries.json"
            file_path.write_text(json.dumps({"not": "a list"}), encoding="utf-8")

            with self.assertRaises(ValueError):
                load_entries(file_path)


if __name__ == "__main__":
    unittest.main()
