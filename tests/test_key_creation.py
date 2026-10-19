import sys
import tempfile
from pathlib import Path
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from key_creation import new_spell
from lua_text import parse_pools

class CreationTests(unittest.TestCase):
    def test_insert_nested_new_race(self):
        with tempfile.TemporaryDirectory() as tmp:
            p=Path(tmp)/'Racial.lua'
            s='addon.localeData.deDE.racial = { Gnome = { SHADOW_BOLT = { ziel = { "x" }, gruppe = { "y" }, }, }, }\n'
            p.write_text(s)
            key=new_spell(p,('localeData','deDE','racial'),('Orc',),'CURSE_RECKLESSNESS',backup=False)
            parsed=parse_pools(p.read_text())
            self.assertEqual(key,('localeData','deDE','racial','Orc','CURSE_RECKLESSNESS'))
            self.assertEqual(parsed[key+('ziel',)].entries,['Neuer RP-Text'])
            self.assertEqual(parsed[('localeData','deDE','racial','Gnome','SHADOW_BOLT','ziel')].entries,['x'])
    def test_existing_race_and_duplicate(self):
        with tempfile.TemporaryDirectory() as tmp:
            p=Path(tmp)/'x.lua';p.write_text('addon.localeData.deDE.classTexts = { WARRIOR = { HELLO = { ziel = {"Hi"} } } }')
            new_spell(p,('localeData','deDE','classTexts'),('WARRIOR',),'BYE',backup=False)
            self.assertIn('BYE',p.read_text())
            with self.assertRaises(ValueError):new_spell(p,('localeData','deDE','classTexts'),('WARRIOR',),'BYE',backup=False)
    def test_reject_bad_key(self):
        with tempfile.TemporaryDirectory() as tmp:
            p=Path(tmp)/'x.lua';p.write_text('addon.localeData.deDE.racial = {}')
            with self.assertRaises(ValueError):new_spell(p,('localeData','deDE','racial'),('Bad-Key',),'TEST',backup=False)

if __name__=='__main__':unittest.main()
