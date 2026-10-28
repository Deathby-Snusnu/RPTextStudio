"""Racial mage voices must be generated without breaking ordinary spells."""
import unittest
from addon_project_templates import source_files
from magier_racial_spell_voices import voice_lines, school_for
from magier_ambient_catalog import RACES
from magier_spell_catalog import SPELL_KEYS

class RacialMageVoiceTests(unittest.TestCase):
    def test_races_locales_and_schools(self):
        self.assertEqual(school_for("FIREBALL"), "FIRE")
        self.assertEqual(school_for("FROST_NOVA"), "FROST")
        self.assertEqual(school_for("ARCANE_MISSILES"), "ARCANE")
        for lang in ("deDE", "enUS", "frFR"):
            for race in RACES:
                for spell in ("FIREBALL", "FROST_NOVA", "ARCANE_MISSILES"):
                    lines = voice_lines(lang, race, spell)
                    self.assertGreaterEqual(len(lines), 2)
                    self.assertTrue(any(t.startswith("*") and t.endswith("*") for t in lines))
                    self.assertTrue(any(not t.startswith("*") for t in lines))

    def test_generated_lua_tables_and_fallback(self):
        files = source_files("MagierRP", "Magier RP", ("deDE", "enUS", "frFR"), "0.1.0", 16001)
        toc = files["MagierRP.toc"]
        for path in toc.splitlines():
            if path and not path.startswith("#"):
                self.assertIn(path.replace(chr(92), "/"), files)
        for lang in ("deDE", "enUS", "frFR"):
            lua = files[f"locales/{lang}/Racial.lua"]
            for race in RACES:
                self.assertIn(race + " = {", lua)
            for key in SPELL_KEYS:
                self.assertIn(key + " = {", lua)
        text = files["core/Text.lua"]
        self.assertIn('UnitRace("player")', text)
        self.assertIn("racePool", text)
        self.assertIn("pool = entry.gruppe", text)

if __name__ == "__main__":
    unittest.main()
