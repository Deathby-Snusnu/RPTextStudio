"""Regression checks for school-specific mage vocabulary."""
import unittest
from magier_voice_banks import BANKS, theme_for
from magier_spell_catalog import SPELL_KEYS, SPELL_DATA

class MageVoiceVarietyTests(unittest.TestCase):
    def test_school_and_utility_themes(self):
        self.assertEqual(theme_for("FIREBALL"), "FIRE")
        self.assertEqual(theme_for("FROST_NOVA"), "FROST")
        self.assertEqual(theme_for("ARCANE_MISSILES"), "ARCANE")
        self.assertEqual(theme_for("POLYMORPH"), "POLYMORPH")
        self.assertEqual(theme_for("PORTAL_STORMWIND"), "PORTAL")
        self.assertEqual(theme_for("CONJURE_FOOD"), "CONJURE")

    def test_localized_banks_and_spell_integration(self):
        for lang in ("deDE", "enUS", "frFR"):
            for key in SPELL_KEYS:
                with self.subTest(lang=lang, key=key):
                    theme = theme_for(key)
                    additions = BANKS[lang][theme]
                    self.assertGreaterEqual(len(additions), 2)
                    self.assertTrue(set(additions) <= set(SPELL_DATA[lang][key]["gruppe"]))
                    self.assertTrue(any(x.startswith("*") and x.endswith("*") for x in additions))
                    self.assertTrue(any(not x.startswith("*") for x in additions))

if __name__ == "__main__":
    unittest.main()
