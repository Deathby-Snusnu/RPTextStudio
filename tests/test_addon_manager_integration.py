"""Integration checks for the two independent addon-management components."""
import tempfile
import unittest
from pathlib import Path
from addon_manager import preview, install, rollback, InstallError
from wow_detection import discover_wow_installations
from wow_installations import save_paths, load_paths


class CombinedWorkflowTests(unittest.TestCase):
    def test_detect_preview_install_and_rollback(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            source = base / "project" / "addons"
            addon = source / "HexerRP"
            addon.mkdir(parents=True)
            (addon / "HexerRP.toc").write_text("## Interface: 16001\nHexerRP.lua\n")
            (addon / "HexerRP.lua").write_text("print('new')")
            client = base / "World of Warcraft" / "_classic_era_"
            target = client / "Interface" / "AddOns"
            target.mkdir(parents=True)
            (client / "WTF").mkdir()
            (client / "WowClassic.exe").write_bytes(b"fake executable")
            settings = base / "settings" / "installations.json"
            save_paths([client], settings)
            candidates = discover_wow_installations(load_paths(settings), include_standard=False)
            self.assertEqual(len(candidates), 1)
            self.assertTrue(candidates[0].verified)
            self.assertEqual(candidates[0].addons_path, target)
            plan = preview(source, target, ("HexerRP",))
            self.assertEqual(plan[0].added, ("HexerRP.lua", "HexerRP.toc"))
            with self.assertRaises(InstallError):
                install(source, target, ("HexerRP",))
            backup = install(source, target, ("HexerRP",), approved=plan)
            self.assertEqual((target / "HexerRP" / "HexerRP.lua").read_text(), "print('new')")
            rollback(target, backup)
            self.assertFalse((target / "HexerRP").exists())


if __name__ == "__main__":
    unittest.main()
