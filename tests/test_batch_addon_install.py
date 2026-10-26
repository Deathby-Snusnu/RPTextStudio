"""First-install batch tests without network or WoW runtime."""
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from addon_manager import ADDONS, InstallError
from batch_addon_install import missing_names, prepare_missing, install_missing, discard_missing
from wow_client_profiles import ClientProfile


class MissingAddonTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name) / "_classic_era_"
        self.root.mkdir()
        (self.root / "WowClassic.exe").write_bytes(b"stub")
        (self.root / "WTF").mkdir()
        self.target = self.root / "Interface" / "AddOns"
        self.target.mkdir(parents=True)
        self.profile = ClientProfile(self.root, "classic_era", "11509", "manual")

    def fake_stage(self, name, channel, destination):
        destination.mkdir()
        (destination / (name + ".toc")).write_text(
            "## Interface: 16001\n## Version: 0.1.0\ncore.lua\n", encoding="utf-8")
        (destination / "core.lua").write_text("PRINT('runtime')\n", encoding="utf-8")

    def test_empty_folder_installs_six_addons_with_interface(self):
        self.assertEqual(missing_names(self.target), ADDONS)
        with patch("batch_addon_install.stage", side_effect=self.fake_stage):
            batch = prepare_missing(self.target, self.profile)
        try:
            self.assertEqual(len(batch.plans), 6)
            self.assertTrue(all(not (self.target / name).exists() for name in ADDONS))
            backups = install_missing(batch)
            self.assertEqual(len(backups), 6)
            for name in ADDONS:
                self.assertIn("## Interface: 11509",
                              (self.target / name / (name + ".toc")).read_text())
            self.assertEqual(missing_names(self.target), ())
        finally:
            discard_missing(batch)

    def test_selected_subset_installs_only_selected_addon(self):
        selected = "JaegerRP"
        with patch("batch_addon_install.stage", side_effect=self.fake_stage) as staging:
            batch = prepare_missing(self.target, self.profile, names=(selected,))
        try:
            self.assertEqual([plan.name for plan in batch.plans], [selected])
            staging.assert_called_once()
            self.assertEqual(staging.call_args.args[0], selected)
            install_missing(batch)
            self.assertEqual(
                {path.name for path in self.target.iterdir() if path.name in ADDONS},
                {selected},
            )
            self.assertEqual(
                missing_names(self.target),
                tuple(name for name in ADDONS if name != selected),
            )
        finally:
            discard_missing(batch)

    def test_existing_addon_is_never_replaced(self):
        folder = self.target / "JaegerRP"
        folder.mkdir()
        (folder / "mywords.lua").write_text("persönlicher Text", encoding="utf-8")
        with patch("batch_addon_install.stage", side_effect=self.fake_stage) as downloader:
            batch = prepare_missing(self.target, self.profile)
        try:
            self.assertNotIn("JaegerRP", [p.name for p in batch.plans])
            self.assertEqual(len(batch.plans), 5)
            self.assertEqual(downloader.call_count, 5)
            install_missing(batch)
            self.assertEqual((folder / "mywords.lua").read_text(encoding="utf-8"),
                             "persönlicher Text")
        finally:
            discard_missing(batch)

    def test_state_change_rejects_batch_before_install(self):
        with patch("batch_addon_install.stage", side_effect=self.fake_stage):
            batch = prepare_missing(self.target, self.profile)
        try:
            (self.target / "HexerRP").mkdir()
            with self.assertRaises(InstallError):
                install_missing(batch)
            self.assertFalse((self.target / "JaegerRP").exists())
        finally:
            discard_missing(batch)


if __name__ == "__main__":
    unittest.main()
