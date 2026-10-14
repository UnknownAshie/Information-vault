import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import app
from app import (
    find_entries,
    load_entries,
    make_entry,
    next_entry_id,
    save_entries,
)


class InfoVaultTests(unittest.TestCase):
    def test_save_and_load_entries(self):
        with tempfile.TemporaryDirectory() as directory:
            file_path = Path(directory) / "data" / "entries.json"
            entries = [make_entry("Wi-Fi", "Network: example", 1)]

            save_entries(entries, file_path)

            self.assertEqual(load_entries(file_path), entries)

    def test_next_entry_id_increments_from_highest_id(self):
        entries = [
            make_entry("First", "First information", 1),
            make_entry("Third", "Third information", 3),
        ]

        self.assertEqual(next_entry_id(entries), 4)
        self.assertEqual(next_entry_id([]), 1)

    def test_load_missing_file_returns_empty_list(self):
        with tempfile.TemporaryDirectory() as directory:
            file_path = Path(directory) / "missing.json"

            self.assertEqual(load_entries(file_path), [])

    def test_search_matches_title_and_content_case_insensitively(self):
        entries = [
            make_entry("Wi-Fi", "Network password is stored securely", 1),
            make_entry("Shopping", "Buy coffee", 2),
        ]

        results = find_entries(entries, "COFFEE")

        self.assertEqual([entry["title"] for entry in results], ["Shopping"])

    def test_fourth_menu_choice_deletes_entry_by_integer_id(self):
        entry = make_entry("Wi-Fi", "Network: example", 1)
        with patch("builtins.input", side_effect=["4", "1", "y", "5"]):
            with patch.object(app, "load_entries", return_value=[entry]):
                with patch.object(app, "save_entries") as save_entries_mock:
                    app.run()

        save_entries_mock.assert_called_once_with([])

    def test_load_rejects_invalid_data_shape(self):
        with tempfile.TemporaryDirectory() as directory:
            file_path = Path(directory) / "entries.json"
            file_path.write_text(json.dumps({"not": "a list"}), encoding="utf-8")

            with self.assertRaises(ValueError):
                load_entries(file_path)


if __name__ == "__main__":
    unittest.main()
