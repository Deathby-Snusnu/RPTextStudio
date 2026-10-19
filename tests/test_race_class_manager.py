import unittest
import tempfile
from pathlib import Path
from race_class_manager import register,load_registry,add_lua_profile,validate_profile
from lua_text import parse_pools

class RaceClassManagerTests(unittest.TestCase):
    def test_registry(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td)
            register(root,'race','NightElf','Nachtelf','Naturverbunden, geheimnisvoll, traditionsbewusst')
            self.assertEqual(load_registry(root)['races']['NightElf']['name'],'Nachtelf')
            with self.assertRaises(ValueError):register(root,'race','NightElf','Nachtelf','')
            register(root,'class','DRUID','Druide','Wald und Wandel')
            self.assertIn('DRUID',load_registry(root)['classes'])
    def test_invalid(self):
        for key in ('bad-key','9Orc','nil'):
            with self.assertRaises(ValueError):validate_profile('race',key,'Name','Stil')
    def test_lua_realistic_structure(self):
        for kind,file,base in [('race','Racial.lua','racial'),('class','Classes.lua','classes')]:
            with self.subTest(kind=kind),tempfile.TemporaryDirectory() as td:
                root=Path(td)
                for lang in ('deDE','enUS','frFR'):
                    p=root/'SampleRP'/'locales'/lang/file;p.parent.mkdir(parents=True)
                    p.write_text('local _, addon = ...\naddon.localeData = addon.localeData or {}\naddon.localeData.'+lang+' = addon.localeData.'+lang+' or {}\naddon.localeData.'+lang+'.'+base+' = {\n    Gnome = { HELLO = { ziel = { "Hi" }, gruppe = { "Hallo" }, }, },\n}\n',encoding='utf-8')
                count=add_lua_profile(root,'SampleRP',kind,'NightElf' if kind=='race' else 'DRUID')
                self.assertEqual(count,3)
                for lang in ('deDE','enUS','frFR'):
                    p=root/'SampleRP'/'locales'/lang/file
                    pools=parse_pools(p.read_text())
                    k='NightElf' if kind=='race' else 'DRUID'
                    self.assertIn(('localeData',lang,base,k,'RP_GREETING','ziel'),pools)
                    self.assertIn(('localeData',lang,base,'Gnome','HELLO','ziel'),pools)
                    with self.assertRaises(ValueError):add_lua_profile(root,'SampleRP',kind,k)
