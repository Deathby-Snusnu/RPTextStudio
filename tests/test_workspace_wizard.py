"""Offline validation tests for integrated editor workflow."""
import unittest
try:
    from workspace_wizard import draft_issues
except ImportError:
    draft_issues = None

@unittest.skipIf(draft_issues is None, "PySide6 nicht installiert")
class WorkspaceDraftTests(unittest.TestCase):
    def test_preserves_placeholders(self):
        self.assertEqual(draft_issues("Hallo %s und %p",
            {"enUS":"Hello %s and %p","frFR":"Bonjour %s et %p"}),[])
    def test_missing_placeholder_is_blocked(self):
        self.assertTrue(draft_issues("Hallo %s",{"enUS":"Hello"}))
    def test_emote_format_is_blocked(self):
        self.assertTrue(draft_issues("*winkt*",{"enUS":"waves"}))
    def test_empty_original_is_blocked(self):
        self.assertTrue(draft_issues(" ",{}))
    def test_partial_translation_is_supported(self):
        self.assertEqual(draft_issues("Seid gegrüßt",{"enUS":"Greetings"}),[])

if __name__=="__main__":
    unittest.main()
