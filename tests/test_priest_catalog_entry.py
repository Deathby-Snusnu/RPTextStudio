"""PriesterRP catalog and safe macro generation contract."""
import unittest
from addon_catalog import load_catalog
from spell_manager import make_macro, validate_entry

class PriestCatalogTests(unittest.TestCase):
    def test_priest_catalog_entry(self):
        matches = [e for e in load_catalog() if e.id == "PriesterRP"]
        self.assertEqual(len(matches), 1)
        self.assertEqual(matches[0].repository, "Deathby-Snusnu/PriesterRP")
        self.assertEqual(matches[0].classes, ("PRIEST",))
    def test_priest_macro(self):
        macro = make_macro("PriesterRP", "Erneuerung", "RENEW", ["RENEW"])
        self.assertIn("/cast Erneuerung", macro)
        self.assertIn("/prrp renew", macro)
    def test_uncastable_lightwell_renew(self):
        with self.assertRaisesRegex(ValueError, "passiv"):
            validate_entry("PriesterRP", "Lichtbrunnen", "LIGHTWELL_RENEW", ["LIGHTWELL_RENEW"])
    def test_input_injection_disallowed(self):
        with self.assertRaises(ValueError):
            make_macro("PriesterRP", "Erneuerung\n/yell", "RENEW", ["RENEW"])

if __name__ == "__main__":
    unittest.main()
