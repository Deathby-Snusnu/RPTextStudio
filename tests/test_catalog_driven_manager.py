"""Catalog-backed user-mode and installer discovery, including future classes."""
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from addon_catalog import catalog_ids
from addon_manager import known_addons
from batch_addon_install import missing_names
from user_addon_manager import inspect_installed
from github_staging import _resolve, DownloadError


class CatalogDrivenManagerTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.catalog = self.root / "catalog.json"
        self.target = self.root / "Interface" / "AddOns"
        self.target.mkdir(parents=True)
        self.data = {
            "schema": 1,
            "addons": [
                {"id": "MagierRP", "title": "Magier RP",
                 "repository": "Deathby-Snusnu/MagierRP",
                 "supported_clients": [], "classes": ["MAGE"]},
                {"id": "KriegerRP", "title": "Krieger RP",
                 "repository": "Deathby-Snusnu/KriegerRP",
                 "supported_clients": [], "classes": ["WARRIOR"]},
            ],
        }
        self.catalog.write_text(json.dumps(self.data), encoding="utf-8")
        self.patcher = patch("addon_catalog.BUILTIN_PATH", self.catalog)
        self.patcher.start()
        self.addCleanup(self.patcher.stop)

    def test_runtime_catalog_includes_future_classes(self):
        self.assertEqual(known_addons(), ("MagierRP", "KriegerRP"))
        self.assertEqual(catalog_ids(), ("MagierRP", "KriegerRP"))

    def test_missing_installations_follow_catalog(self):
        self.assertEqual(missing_names(self.target), ("MagierRP", "KriegerRP"))
        (self.target / "MagierRP").mkdir()
        self.assertEqual(missing_names(self.target), ("KriegerRP",))

    def test_user_overview_follows_catalog(self):
        with patch("user_addon_manager.inspect_client", return_value=object()):
            rows = inspect_installed(self.target)
        self.assertEqual(tuple(x.name for x in rows), ("MagierRP", "KriegerRP"))
        self.assertEqual(rows[0].state, "Nicht installiert")

    def test_stage_recognizes_catalog_id_but_not_unlisted_addon(self):
        with patch("github_staging._api", side_effect=[
            {"default_branch": "main"}, {"sha": "a" * 40}
        ]):
            self.assertEqual(_resolve("MagierRP", "development")[0], "a" * 40)
        with self.assertRaises(DownloadError):
            _resolve("UnknownRP", "development")

    def test_invalid_catalog_fails_closed(self):
        self.catalog.write_text('{"schema": 1, "addons": [{"id": "../unsafe"}]}',
                                encoding="utf-8")
        with self.assertRaises(ValueError):
            known_addons()
        with self.assertRaises(ValueError):
            missing_names(self.target)


if __name__ == "__main__":
    unittest.main()
