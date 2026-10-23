"""Project generation and dynamic registry regression tests (offline)."""
import tempfile
import unittest
from pathlib import Path
from addon_project_generator import AddonProjectSpec, preview_project, generate_project
from addon_registry import discover, available, load_registry
from addon_project_templates import source_files
from lua_text import parse_pools


class GeneratorTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        (self.root / "addons").mkdir()

    def test_generates_mage_toc_locales_and_registry(self):
        spec = AddonProjectSpec()
        plan = preview_project(self.root, spec)
        self.assertFalse((self.root / "addons" / "MagierRP").exists())
        path = generate_project(self.root, spec, plan)
        self.assertTrue((path / "MagierRP.toc").exists())
        self.assertEqual(discover(self.root)["MagierRP"], path)
        self.assertEqual(available(self.root)[0]["class_token"], "MAGE")
        self.assertIsNone(load_registry(self.root)["addons"][0]["repository"])
        toc = (path / "MagierRP.toc").read_text(encoding="utf-8")
        self.assertLess(toc.index("locales\\Init.lua"), toc.index("core\\Text.lua"))
        for lang in ("deDE", "enUS", "frFR"):
            file = path / "locales" / lang / "Texts.lua"
            pools = parse_pools(file.read_text(encoding="utf-8"))
            self.assertIn(("localeData", lang, "texts", "FIREBALL", "ziel"), pools)
            self.assertIn(("localeData", lang, "texts", "FROSTBOLT", "gruppe"), pools)
            self.assertIn(("localeData", lang, "texts", "ARCANE_MISSILES", "ziel"), pools)
        self.assertIn('class ~= "MAGE"', (path / "MagierRP.lua").read_text())

    def test_rejects_duplicate_without_overwriting(self):
        spec = AddonProjectSpec()
        generate_project(self.root, spec, preview_project(self.root, spec))
        with self.assertRaises(FileExistsError):
            preview_project(self.root, spec)

    def test_invalid_spec_has_no_side_effects(self):
        with self.assertRaises(ValueError):
            preview_project(self.root, AddonProjectSpec(interface=1))
        self.assertEqual(list((self.root / "addons").iterdir()), [])

    def test_stale_preview_rejected(self):
        spec = AddonProjectSpec()
        plan = preview_project(self.root, spec)
        with self.assertRaises(ValueError):
            generate_project(self.root, AddonProjectSpec(version="0.1.1"), plan)

    def test_templates_complete(self):
        files = source_files("MagierRP", "Magier RP", ("deDE", "enUS", "frFR"), "0.1.0", 16001)
        for path in files["MagierRP.toc"].splitlines():
            if path and not path.startswith("#"):
                self.assertIn(path.replace("\\", "/"), files)


if __name__ == "__main__":
    unittest.main()
