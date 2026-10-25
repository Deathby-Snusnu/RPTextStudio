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

    def test_paladin_categories_are_discovered(self):
        samples = {
            "Abilities.lua": 'addon.localeData.deDE.Abilities = { ["LAYONHANDS"] = { ziel = { "Segen, %s", }, }, ["DIVINE_SHIELD"] = { gruppe = { "Schild", }, }, }',
            "Blessings.lua": 'addon.localeData.deDE.Blessings = { ["MIGHT"] = { ziel = { "Kraft, %s", }, }, }',
            "GreaterBlessings.lua": 'addon.localeData.deDE.GreaterBlessings = { ["GREATER_MIGHT"] = { gruppe = { "Kraft", }, }, }',
            "Auras.lua": 'addon.localeData.deDE.Auras = { ["DEVOTION"] = { gruppe = { "Schutz", }, }, }',
            "Seals.lua": 'addon.localeData.deDE.Seals = { ["FURY"] = { gruppe = { "Zorn", }, }, }',
            "Ambient.lua": 'addon.localeData.deDE.ambient = { PRAYER = { "Gebet", }, }',
        }
        files = {
            Path("addons/PaladinRP/locales/deDE") / filename: parse_pools(source)
            for filename, source in samples.items()
        }
        found = candidate_keys(files, "PaladinRP")
        for key in ("LAYONHANDS", "DIVINE_SHIELD", "MIGHT",
                    "GREATER_MIGHT", "DEVOTION", "FURY"):
            self.assertIn(key, found)
        self.assertNotIn("PRAYER", found)

    def test_all_other_class_spell_keys(self):
        examples = {
            "HexerRP": ("SHADOW_BOLT", "IMMOLATE"),
            "JaegerRP": ("HUNTERS_MARK", "ARCANE_SHOT"),
            "DruidenRP": ("MARK", "GIFT"),
        }
        for addon, (first, second) in examples.items():
            with self.subTest(addon=addon):
                source = (
                    "addon.localeData.deDE.texts = { "
                    + first + ' = { ziel = { "Ziel, %s", }, }, '
                    + second + ' = { gruppe = { "Gruppe", }, } }'
                )
                path = Path("addons") / addon / "locales" / "deDE" / "Texts.lua"
                actual = candidate_keys({path: parse_pools(source)}, addon)
                self.assertIn(first, actual)
                self.assertIn(second, actual)
                other = candidate_keys({path: parse_pools(source)}, "PaladinRP")
                self.assertEqual(other, [])

    def test_flat_racial_keys_and_ambient_exclusion(self):
        racial = Path("addons/PaladinRP/locales/deDE/Racial.lua")
        ambient = Path("addons/PaladinRP/locales/deDE/Ambient.lua")
        pools = {
            racial: parse_pools('addon.localeData.deDE.Racial = { ["Dwarf"] = { ["MIGHT"] = { "Text", }, }, }'),
            ambient: parse_pools('addon.localeData.deDE.ambient = { PRAYER = { "Gebet", }, }'),
        }
        self.assertIn("MIGHT", candidate_keys(pools, "PaladinRP"))
        self.assertNotIn("PRAYER", candidate_keys(pools, "PaladinRP"))

    def test_real_hexer_keys(self):
        addons=Path(__file__).resolve().parents[3]/'addons'
        source=addons/'HexerRP/locales/deDE/Texts.lua'
        if not source.exists():
            self.skipTest('Addon fixture not distributed with the editor')
        self.assertIn('SHADOW_BOLT',candidate_keys({source:parse_pools(source.read_text())},'HexerRP'))

if __name__=='__main__':
    unittest.main()
