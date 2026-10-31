"""Offline, read-only user addon manager tests."""
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from user_addon_manager import inspect_installed, check_installed


class UserAddonManagerTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.client = Path(self.temp.name) / "_classic_era_"
        self.client.mkdir()
        (self.client / "WowClassic.exe").write_bytes(b"dummy")
        (self.client / "WTF").mkdir()
        self.addons = self.client / "Interface" / "AddOns"
        self.addons.mkdir(parents=True)

    def test_read_versions_and_missing_addons(self):
        addon = self.addons / "HexerRP"
        addon.mkdir()
        (addon / "HexerRP.toc").write_text(
            "## Interface: 16001\n## Version: 0.3.0\n", encoding="utf-8"
        )
        rows = inspect_installed(self.addons, ("HexerRP", "DruidenRP"))
        self.assertEqual(rows[0].version, "0.3.0")
        self.assertEqual(rows[0].interface, "16001")
        self.assertEqual(rows[1].state, "Nicht installiert")
        self.assertEqual(sorted(x.name for x in addon.iterdir()), ["HexerRP.toc"])

    def test_no_local_source_required_for_github(self):
        with patch("user_addon_manager.check_addon") as mocked:
            check_installed(self.addons, ("HexerRP",))
        mocked.assert_called_once_with("HexerRP", self.addons, "stable")

    def test_check_installed_defaults_to_runtime_catalog(self):
        with (
            patch("user_addon_manager.known_addons", return_value=("HexerRP",)) as catalog,
            patch("user_addon_manager.check_addon") as mocked,
        ):
            check_installed(self.addons)
        catalog.assert_called_once_with()
        mocked.assert_called_once_with("HexerRP", self.addons, "stable")

    def test_invalid_target_rejected_without_network(self):
        with patch("user_addon_manager.check_addon") as mocked:
            with self.assertRaises(ValueError):
                check_installed(Path(self.temp.name), ("HexerRP",))
        mocked.assert_not_called()

    def test_untrusted_or_duplicate_names_rejected_before_path_or_network_use(self):
        for names in (("../outside",), ("UnknownRP",), ("HexerRP", "HexerRP")):
            with self.subTest(names=names):
                with patch("user_addon_manager.check_addon") as mocked:
                    with self.assertRaises(ValueError):
                        inspect_installed(self.addons, names)
                mocked.assert_not_called()
        self.assertFalse((self.addons.parent / "outside").exists())


if __name__ == "__main__":
    unittest.main()
