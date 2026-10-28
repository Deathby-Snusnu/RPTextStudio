"""Contract for RPControlCenter to adjust mage racial spell commentary."""
import unittest
from addon_project_templates import source_files

class MageControlCenterContract(unittest.TestCase):
    def test_exposes_addon_and_mutable_setting(self):
        files = source_files("MagierRP", "Magier RP", ("deDE","enUS","frFR"), "0.1.0", 16001)
        self.assertIn("_G.MagierRP = addon", files["MagierRP.lua"])
        self.assertIn("racialTextChance = 40", files["config/Settings.lua"])
        self.assertIn("addon.db.racialTextChance", files["core/Database.lua"])
        self.assertIn("addon.db.racialTextChance or 40", files["core/Text.lua"])

if __name__ == "__main__":
    unittest.main()
