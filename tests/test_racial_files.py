import unittest
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from lua_text import parse_pools, update_file

class RacialParserTests(unittest.TestCase):
    def test_nested_racial_key(self):
        content='addon.localeData.deDE.racial = { Gnome = { SHADOW_BOLT = { ziel = { "Hallo %s", "*winkt %s zu.*" }, gruppe={ "*winkt.*" } } } }'
        pools=parse_pools(content)
        self.assertIn(('localeData','deDE','racial','Gnome','SHADOW_BOLT','ziel'),pools)
        self.assertEqual(pools[('localeData','deDE','racial','Gnome','SHADOW_BOLT','gruppe')].entries,['*winkt.*'])
