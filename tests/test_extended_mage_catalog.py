"""Expanded MagierRP project generator: localized spells and safe target scope."""
import unittest
from addon_project_templates import source_files
from magier_spell_catalog import SPELL_KEYS, SPELL_DATA, FRIENDLY_KEYS, SELF_KEYS


class MageSpellCatalogTests(unittest.TestCase):
    def test_spell_coverage_and_locales(self):
        self.assertGreaterEqual(len(SPELL_KEYS), 25)
        self.assertEqual(len(set(SPELL_KEYS)), len(SPELL_KEYS))
        for language in ("deDE", "enUS", "frFR"):
            self.assertEqual(set(SPELL_DATA[language]), set(SPELL_KEYS))
            for key, entry in SPELL_DATA[language].items():
                with self.subTest(language=language, key=key):
                    self.assertTrue(entry["name"])
                    self.assertGreaterEqual(len(entry["gruppe"]), 2)
                    self.assertTrue(any(t.startswith("*") and t.endswith("*")
                                        for t in entry["gruppe"]))
                    self.assertTrue(all(t.startswith("*") == t.endswith("*")
                                        for t in entry["gruppe"] + entry["ziel"]))
                    if key not in SELF_KEYS:
                        self.assertTrue(any("%s" in t for t in entry["ziel"]))

    def test_generated_files_and_commands(self):
        files = source_files("MagierRP", "Magier RP", ("deDE", "enUS", "frFR"), "0.1.0", 16001)
        for language in ("deDE", "enUS", "frFR"):
            lua = files["locales/" + language + "/Texts.lua"]
            for key in SPELL_KEYS:
                self.assertIn(key + " = {", lua)
        text = files["core/Text.lua"]
        self.assertIn("UnitCanAssist", text)
        self.assertIn("selfOnly", text)
        commands = files["core/Commands.lua"]
        self.assertIn('key == "LIST"', commands)
        self.assertNotIn("\\n", commands)
        core = files["MagierRP.lua"]
        self.assertIn('addon.spellKeys', core)
        self.assertIn('if class ~= "MAGE"', core)

    def test_friendly_self_scope_disjoint(self):
        self.assertFalse(set(FRIENDLY_KEYS) & set(SELF_KEYS))
        self.assertTrue(set(FRIENDLY_KEYS) <= set(SPELL_KEYS))
        self.assertTrue(set(SELF_KEYS) <= set(SPELL_KEYS))


if __name__ == "__main__":
    unittest.main()
