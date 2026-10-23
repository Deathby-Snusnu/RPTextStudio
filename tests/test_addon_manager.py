"""Offline regression tests for the local WoW AddOn installer."""
import tempfile
import unittest
from pathlib import Path
from addon_manager import InstallError, install, preview, rollback


class AddonInstallerTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        root = Path(self.temp.name)
        self.source = root / "project" / "addons"
        self.target = root / "game" / "Interface" / "AddOns"
        self.source.mkdir(parents=True)
        self.target.mkdir(parents=True)
        (self.source / "HexerRP").mkdir()
        (self.source / "HexerRP" / "HexerRP.toc").write_text("HexerRP.lua\n", encoding="utf-8")
        (self.source / "HexerRP" / "HexerRP.lua").write_text("print('new')", encoding="utf-8")

    def test_preview_and_backup_and_rollback(self):
        old = self.target / "HexerRP"
        old.mkdir()
        (old / "HexerRP.lua").write_text("print('old')", encoding="utf-8")
        (old / "obsolete.lua").write_text("old", encoding="utf-8")
        plan = preview(self.source, self.target, ("HexerRP",))
        self.assertEqual(plan[0].added, ("HexerRP.toc",))
        self.assertEqual(plan[0].changed, ("HexerRP.lua",))
        self.assertEqual(plan[0].removed, ("obsolete.lua",))
        with self.assertRaises(InstallError):
            install(self.source, self.target, ("HexerRP",))
        backup = install(self.source, self.target, ("HexerRP",), approved=plan)
        self.assertFalse((old / "obsolete.lua").exists())
        self.assertEqual((old / "HexerRP.lua").read_text(), "print('new')")
        self.assertTrue((backup / "HexerRP" / "obsolete.lua").exists())
        rollback(self.target, backup)
        self.assertEqual((old / "HexerRP.lua").read_text(), "print('old')")
        self.assertTrue((old / "obsolete.lua").exists())

    def test_changed_source_invalidates_preview(self):
        plan = preview(self.source, self.target, ("HexerRP",))
        (self.source / "HexerRP" / "HexerRP.lua").write_text("updated", encoding="utf-8")
        with self.assertRaises(InstallError):
            install(self.source, self.target, ("HexerRP",), approved=plan)

    def test_blocks_wrong_target(self):
        with self.assertRaises(InstallError):
            preview(self.source, self.source, ("HexerRP",))

    def test_excludes_developer_files(self):
        (self.source / "HexerRP" / "tests").mkdir()
        (self.source / "HexerRP" / "tests" / "test.lua").write_text("test")
        plan = preview(self.source, self.target, ("HexerRP",))
        self.assertNotIn("tests/test.lua", plan[0].added)

    def test_requires_toc(self):
        (self.source / "HexerRP" / "HexerRP.toc").unlink()
        with self.assertRaises(InstallError):
            preview(self.source, self.target, ("HexerRP",))


if __name__ == "__main__":
    unittest.main()
