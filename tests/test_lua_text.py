import sys
import unittest
import tempfile
from pathlib import Path
sys.path.insert(0,str(Path(__file__).parents[1]))
from lua_text import parse_pools,update_file,validate_file

SAMPLE='''-- SPDX-License-Identifier: CC-BY-SA-4.0
local _, addon = ...
addon.localeData.deDE.texts = {
    SHADOW_BOLT = {
        name = "Schattenblitz",
        ziel = {
            "Hallo, %s.",
            "*zeigt auf %s.*",
        },
        gruppe = {
            "Gruess Euch!",
        },
    },
}
'''
class Tests(unittest.TestCase):
 def test_parse(self):
  p=parse_pools(SAMPLE)
  self.assertEqual(p[('localeData','deDE','texts','SHADOW_BOLT','ziel')].entries,['Hallo, %s.','*zeigt auf %s.*'])
 def test_roundtrip(self):
  with tempfile.TemporaryDirectory() as d:
   file=Path(d)/'Texts.lua';file.write_text(SAMPLE,encoding='utf8')
   update_file(file,{('localeData','deDE','texts','SHADOW_BOLT','ziel'):['Bonjour, %s.','*grinst.*']})
   result=file.read_text(encoding='utf8')
   self.assertIn('SPDX-License-Identifier',result)
   self.assertIn('"Gruess Euch!"',result)
   self.assertEqual(parse_pools(result)[('localeData','deDE','texts','SHADOW_BOLT','ziel')].entries,['Bonjour, %s.','*grinst.*'])
   self.assertEqual(len(list(Path(d).glob('*.bak'))),1)
 def test_nested(self):
  source='addon.localeData.frFR.raceClassTexts = { ["Gnome"] = { ["WARLOCK"] = { FLIRT = { ziel = {"Salut, %s."}, }, }, }, }'
  p=parse_pools(source)
  self.assertIn(('localeData','frFR','raceClassTexts','Gnome','WARLOCK','FLIRT','ziel'),p)
if __name__=='__main__':unittest.main()

class PreservationTests(unittest.TestCase):
 def test_percent_tokens_can_be_saved_and_validated(self):
  with tempfile.TemporaryDirectory() as d:
   file=Path(d)/'Texts.lua'
   key=('localeData','enUS','texts','TEST','ziel')
   file.write_text('addon.localeData.enUS.texts = { TEST = { ziel = {"100% ready"}, }, }')
   update_file(file,{key:['100%% ready']},backup=False)
   self.assertEqual(validate_file(file)[1],[])

 def test_unchanged_pool_is_byte_identical(self):
  with tempfile.TemporaryDirectory() as d:
   file=Path(d)/'Texts.lua'
   original='addon.localeData.enUS.texts = { TEST = { ziel = { "Hello", "World" }, }, }\n'
   file.write_bytes(original.encode())
   pools=parse_pools(original)
   update_file(file,{key:pool.entries for key,pool in pools.items()},backup=True)
   self.assertEqual(file.read_bytes(),original.encode())
   self.assertEqual(list(Path(d).glob('*.bak')),[])
 def test_changed_pool_preserves_untouched_pool(self):
  with tempfile.TemporaryDirectory() as d:
   file=Path(d)/'Texts.lua'
   original='addon.localeData.enUS.texts = { A = { ziel = {"OLD"}, }, B = { gruppe = {"KEEP"}, }, }'
   file.write_text(original)
   pools=parse_pools(original)
   updates={key:(['NEW'] if 'A' in key else pool.entries) for key,pool in pools.items()}
   update_file(file,updates,backup=False)
   self.assertIn('B = { gruppe = {"KEEP"}, }',file.read_text())
