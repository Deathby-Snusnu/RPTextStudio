"""Offline WoW discovery tests using temporary fake client trees."""
import tempfile
import unittest
from pathlib import Path
from wow_detection import discover_wow_installations, inspect_client, scan_selected_drives
from wow_installations import load_paths, save_paths


class WoWDetectionTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)

    def client(self, name="_classic_era_", exe=True, wtf=True):
        root = self.root / "World of Warcraft" / name
        (root / "Interface" / "AddOns").mkdir(parents=True)
        if exe:
            (root / "WowClassic.exe").write_bytes(b"mock")
        if wtf:
            (root / "WTF").mkdir()
        return root

    def test_detects_official_client(self):
        root = self.client()
        match = inspect_client(root)
        self.assertIsNotNone(match)
        self.assertEqual(match.client_type, "classic_era")
        self.assertTrue(match.verified)
        self.assertEqual(match.addons_path, root / "Interface" / "AddOns")

    def test_custom_client(self):
        root = self.root / "WoW-Forever"
        (root / "Interface").mkdir(parents=True)
        (root / "WTF").mkdir()
        match = inspect_client(root)
        self.assertIsNotNone(match)
        self.assertEqual(match.client_type, "custom")
        self.assertFalse(match.verified)

    def test_no_false_positive_from_addons_alone(self):
        root = self.root / "Unrelated"
        (root / "Interface" / "AddOns").mkdir(parents=True)
        self.assertIsNone(inspect_client(root))

    def test_dedup_and_client_directory_expansion(self):
        root = self.client()
        matches = discover_wow_installations(
            saved_paths=[root, root / "Interface" / "AddOns"],
            custom_paths=[root.parent],
            include_standard=False,
        )
        self.assertEqual(len(matches), 1)
        self.assertIn("gespeichert", matches[0].sources)

    def test_opt_in_scan_limits(self):
        client = self.client()
        found = scan_selected_drives((self.root,), max_depth=3, max_visits=100)
        self.assertIn(client, found)
        self.assertEqual(scan_selected_drives((self.root,), cancelled=lambda: True), [])

    def test_storage_roundtrip(self):
        path = self.root / "settings" / "installations.json"
        root = self.client()
        save_paths([root, root], path)
        self.assertEqual(load_paths(path), [root])

    def test_corrupted_storage_is_ignored(self):
        path = self.root / "installations.json"
        path.write_text("{ broken", encoding="utf-8")
        self.assertEqual(load_paths(path), [])


if __name__ == "__main__":
    unittest.main()
