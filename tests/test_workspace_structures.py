"""Offline tests for safe structure planning."""
import tempfile
import unittest
from pathlib import Path
from workspace_structures import plan_spell, plan_profile

class StructurePlanTests(unittest.TestCase):
    def test_missing_file_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaises(ValueError):
                plan_spell(Path(tmp),"HexerRP",0,"","","SHADOW_BOLT")

    def test_invalid_key_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaises(ValueError):
                plan_spell(Path(tmp),"HexerRP",0,"","","NO WAY")

    def test_registry_only_profile_does_not_mutate(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp)
            self.assertEqual(plan_profile(root,"HexerRP","race","NightElf",
                                          "Nachtelf","Naturverbunden",False),[])
            self.assertEqual(list(root.iterdir()),[])

    def test_duplicate_registry_profile(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp)
            (root/".rptextstudio-races-classes.json").write_text(
                '{"version":1,"races":{"NightElf":{}},"classes":{}}',
                encoding="utf-8")
            with self.assertRaises(ValueError):
                plan_profile(root,"HexerRP","race","NightElf","Nachtelf","",False)

if __name__=="__main__":
    unittest.main()
