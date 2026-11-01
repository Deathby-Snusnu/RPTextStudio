"""The standalone KriegerRP repo must be discoverable as a WARRIOR addon."""
import unittest
from addon_catalog import load_catalog
from spell_manager import make_macro

class WarriorCatalogTests(unittest.TestCase):
    def test_warrior_is_in_bundled_catalog(self):
        entries = [entry for entry in load_catalog() if entry.id == "KriegerRP"]
        self.assertEqual(len(entries), 1)
        self.assertEqual(entries[0].repository, "Deathby-Snusnu/KriegerRP")
        self.assertEqual(entries[0].classes, ("WARRIOR",))
    def test_passive_and_triggered_keys_cannot_generate_cast_macros(self):
        for key in ("TACTICAL_MASTERY", "DEVASTATE"):
            with self.subTest(key=key):
                with self.assertRaisesRegex(ValueError, "passiv"):
                    make_macro("KriegerRP", "Taktiker", key, [key],
                               commands={"KriegerRP": "/krp"})

    def test_no_duplicate_warrior_entries(self):
        names = [entry.id.casefold() for entry in load_catalog()]
        self.assertEqual(names.count("kriegerrp"), 1)

if __name__ == "__main__":
    unittest.main()
