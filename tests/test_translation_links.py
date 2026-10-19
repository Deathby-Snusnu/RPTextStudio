import tempfile
import unittest
from pathlib import Path
from translation_links import FILE_NAME, pool_id, read_links, write_links, reference, resolve

class TranslationTests(unittest.TestCase):
    def test_different_indices(self):
        deutsch=['Ein Anfang','Ein anderer Satz']
        english=['Other','Different','A beginning']
        group={'deDE':reference(deutsch,0),'enUS':reference(english,2)}
        self.assertEqual(resolve(deutsch,group['deDE']),0)
        self.assertEqual(resolve(english,group['enUS']),2)

    def test_reorder_and_stale(self):
        ref=reference(['A','B','C'],1)
        self.assertEqual(resolve(['C','A','B'],ref),2)
        self.assertIsNone(resolve(['A','C'],ref))
        self.assertIsNone(resolve(['B','B'],{'index':3,'text':'B'}))

    def test_file_unchanged_on_identical_save(self):
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder)
            pid=pool_id('HexerRP/locales/deDE/Texts.lua',('a','b'))
            links={pid:[{'deDE':{'index':0,'text':'Hallo'},'enUS':{'index':3,'text':'Hello'}}]}
            write_links(root,links)
            before=(root/FILE_NAME).read_bytes()
            self.assertEqual(read_links(root),links)
            write_links(root,links)
            self.assertEqual((root/FILE_NAME).read_bytes(),before)
            self.assertFalse((root/(FILE_NAME+'.bak')).exists())

if __name__=='__main__':unittest.main()
