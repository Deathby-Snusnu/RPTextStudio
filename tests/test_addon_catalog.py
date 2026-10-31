"""Unit tests for universal, class-neutral add-on catalog."""
import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from addon_catalog import catalog_ids, load_catalog, parse_catalog


class CatalogTests(unittest.TestCase):
    def test_bundled_catalog_contains_existing_addons(self):
        names = set(catalog_ids())
        expected = {"DruidenRP", "HexerRP", "JaegerRP", "PaladinRP",
                    "RPChatMod", "RPControlCenter"}
        self.assertTrue(expected.issubset(names))

    def test_future_class_is_data_not_code(self):
        source = {"schema": 1, "addons": [
            {"id": "MagierRP", "title": "Magier RP",
             "repository": "Deathby-Snusnu/MagierRP",
             "supported_clients": [], "classes": ["MAGE"]}
        ]}
        items = parse_catalog(json.dumps(source).encode())
        self.assertEqual(items[0].id, "MagierRP")
        self.assertEqual(items[0].classes, ("MAGE",))
        self.assertEqual(items[0].supported_clients, ())

    def test_duplicate_and_untrusted_repositories_rejected(self):
        entry = {"id": "MagierRP", "title": "Magier RP",
                 "repository": "Deathby-Snusnu/MagierRP",
                 "supported_clients": [], "classes": ["MAGE"]}
        for entries in ([entry, entry], [dict(entry, repository="Other/MagierRP")],
                        [dict(entry, id="../bad")], [dict(entry, supported_clients="all")]):
            with self.subTest(entries=entries), self.assertRaises(ValueError):
                parse_catalog(json.dumps({"schema": 1, "addons": entries}).encode())

    def test_size_limit_and_missing_file(self):
        with self.assertRaises(ValueError):
            parse_catalog(b" " * (512 * 1024 + 1))
        with tempfile.TemporaryDirectory() as folder:
            with self.assertRaises(ValueError):
                load_catalog(Path(folder) / "missing.json")


if __name__ == "__main__":
    unittest.main()
