"""The released MagierRP repository must be discoverable by the installer."""
import unittest
from addon_catalog import load_catalog

class MageCatalogTests(unittest.TestCase):
    def test_magier_exists_and_is_classed(self):
        matches = [a for a in load_catalog() if a.id == "MagierRP"]
        self.assertEqual(len(matches), 1)
        self.assertEqual(matches[0].repository, "Deathby-Snusnu/MagierRP")
        self.assertEqual(matches[0].classes, ("MAGE",))

if __name__ == "__main__":
    unittest.main()
