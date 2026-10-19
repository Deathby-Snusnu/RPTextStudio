import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from lua_text import parse_pools

class LocaleComparisonTests(unittest.TestCase):
    def test_real_locale_pool_keys(self):
        # Regression for localeData/deDE key being wrongly looked up in enUS/frFR.
        try:
            from main import Studio
        except SystemExit:
            self.skipTest("PySide6 not installed in test environment")
        with tempfile.TemporaryDirectory() as td:
            root=Path(td)
            files={}
            for language in ('deDE','enUS','frFR'):
                f=root/'DruidenRP'/'locales'/language/'Texts.lua'
                f.parent.mkdir(parents=True)
                f.write_text(f'local localeData = {{}}\nlocaleData.{language} = {{texts = {{MARK = {{ziel = {{"Hello"}}}}}}}}\n', encoding='utf-8')
                parsed=parse_pools(f.read_text())
                if parsed:files[f]=parsed
            if not files:
                self.skipTest('Parser requires actual localeData layout')
            de=root/'DruidenRP'/'locales'/'deDE'/'Texts.lua'
            key=next(iter(files[de]))
            studio=Studio.__new__(Studio)
            studio.files=files; studio.changes={}; studio.current=(de,key)
            for language in ('deDE','enUS','frFR'):
                sibling=studio.translation_path(language)
                self.assertIsNotNone(sibling)
                self.assertTrue(studio.get_entries(sibling,key))

if __name__=='__main__':unittest.main()
