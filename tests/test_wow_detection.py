"""Offline WoW discovery tests using temporary fake client trees."""
import stat
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest import mock

import wow_detection
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

    def test_junction_reparse_points_are_rejected(self):
        details = SimpleNamespace(
            st_mode=stat.S_IFDIR | 0o755,
            st_file_attributes=0x400,
        )
        with mock.patch.object(Path, "lstat", return_value=details):
            self.assertTrue(wow_detection._linked(self.root))

    def test_scan_bounds_entries_even_with_a_wide_directory(self):
        root = self.root / "wide"
        root.mkdir()
        examined = []

        def children(_):
            for index in range(20):
                examined.append(index)
                yield root / str(index)

        with mock.patch.object(Path, "iterdir", children), \
                mock.patch.object(
                    wow_detection, "_usable_dir", side_effect=lambda path: path == root
                ):
            scan_selected_drives(
                (root,), max_depth=1, max_visits=20, max_entries=3,
            )
        self.assertEqual(examined, [0, 1, 2])

    def test_scan_bounds_queued_work_by_visit_limit(self):
        root = self.root / "wide"
        root.mkdir()
        examined = []

        def children(_):
            for index in range(20):
                examined.append(index)
                yield root / str(index)

        with mock.patch.object(Path, "iterdir", children), \
                mock.patch.object(
                    wow_detection, "_usable_dir", return_value=True,
                ):
            scan_selected_drives((root,), max_depth=1, max_visits=1)
        self.assertEqual(examined, [0])

    def test_extended_scan_filters_nonlocal_drives_before_directory_access(self):
        with mock.patch.object(wow_detection, "_windows_drive_type", return_value=4), \
                mock.patch.object(wow_detection, "_usable_dir") as usable_dir:
            self.assertEqual(scan_selected_drives((self.root,)), [])
        usable_dir.assert_not_called()

    def test_local_drive_listing_excludes_mapped_drives(self):
        def drive_type(path):
            return 3 if str(path) == "C:\\" else 4

        with mock.patch.object(wow_detection.os, "name", "nt"), \
                mock.patch.object(wow_detection, "_windows_drive_type", side_effect=drive_type):
            self.assertEqual(wow_detection._local_drive_roots(), (Path("C:\\"),))

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
