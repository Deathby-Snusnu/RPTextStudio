"""Regression tests for Mage ambient and broad spell generator."""
import unittest
from addon_project_templates import source_files
from magier_ambient_catalog import RACES, THEMES, NEUTRAL
from magier_spell_catalog import SPELL_DATA, SPELL_KEYS

class ExpandedMageTests(unittest.TestCase):
    def test_all_locales_and_races(self):
        self.assertGreaterEqual(len(RACES), 10)
        for lang in ("deDE", "enUS", "frFR"):
            self.assertTrue(set(RACES).issubset(THEMES[lang]))
            self.assertTrue(NEUTRAL[lang])
            for race in RACES:
                self.assertGreaterEqual(len(THEMES[lang][race]), 3)

    def test_all_spell_pools_have_variation(self):
        self.assertGreaterEqual(len(SPELL_KEYS), 60)
        for lang in ("deDE", "enUS", "frFR"):
            for key in SPELL_KEYS:
                with self.subTest(lang=lang, key=key):
                    self.assertGreaterEqual(len(SPELL_DATA[lang][key]["gruppe"]), 6)

    def test_toc_and_ambient_command(self):
        files = source_files("MagierRP", "Magier RP", ("deDE", "enUS", "frFR"), "0.1.0", 16001)
        toc = files["MagierRP.toc"]
        for entry in toc.splitlines():
            if entry and not entry.startswith("#"):
                self.assertIn(entry.replace("\\", "/"), files)
        self.assertIn("addon.AmbientText()", files["MagierRP.lua"])
        self.assertIn('key == "AMBIENT"', files["core/Commands.lua"])
        for lang in ("deDE", "enUS", "frFR"):
            self.assertIn("NEUTRAL", files[f"locales/{lang}/Ambient.lua"])
            self.assertNotIn(r"\n", files[f"locales/{lang}/Ambient.lua"])

if __name__ == "__main__":
    unittest.main()
