import tempfile
import unittest
from pathlib import Path
from spell_manager import candidate_keys, load_mappings, save_mappings, make_macro
from lua_text import parse_pools

class SpellManagerTests(unittest.TestCase):
    def test_macro_and_validation(self):
        macro = make_macro('HexerRP', 'Schattenblitz', 'SHADOW_BOLT', ['SHADOW_BOLT'])
        self.assertEqual(macro, '#showtooltip Schattenblitz\n/cast Schattenblitz\n/wrp shadow_bolt')
        with self.assertRaises(ValueError):
            make_macro('HexerRP', 'Schattenblitz\n/yell Spam', 'SHADOW_BOLT', ['SHADOW_BOLT'])
        with self.assertRaises(ValueError):
            make_macro('HexerRP', 'Schattenblitz', 'UNKNOWN', ['SHADOW_BOLT'])

    def test_persistence_and_backup(self):
        with tempfile.TemporaryDirectory() as root:
            p=Path(root)
            records=[{'addon':'HexerRP','spell':'Schattenblitz','key':'SHADOW_BOLT'}]
            save_mappings(p, records)
            self.assertEqual(load_mappings(p),records)
            save_mappings(p,records)
            self.assertFalse((p/'data'/'.rptextstudio-spells.json.bak').exists())
            save_mappings(p,[])
            self.assertTrue((p/'data'/'.rptextstudio-spells.json.bak').exists())

    def test_real_hexer_keys(self):
        addons=Path(__file__).resolve().parents[3]/'addons'
        source=addons/'HexerRP/locales/deDE/Texts.lua'
        if not source.exists():
            self.skipTest('Addon fixture not distributed with the editor')
        self.assertIn('SHADOW_BOLT',candidate_keys({source:parse_pools(source.read_text())},'HexerRP'))

if __name__=='__main__':
    unittest.main()
