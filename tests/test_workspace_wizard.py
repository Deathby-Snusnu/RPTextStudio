"""Offline validation tests for integrated editor workflow."""
import unittest
try:
    from workspace_wizard import draft_issues, has_pending_text_drafts
except ImportError:
    draft_issues = None
    has_pending_text_drafts = None

@unittest.skipIf(draft_issues is None or has_pending_text_drafts is None, "PySide6 nicht installiert")
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
    def test_pending_source_edit_is_detected(self):
        self.assertTrue(has_pending_text_drafts("Bearbeitet", "Original", {}))
    def test_pending_translation_is_detected(self):
        self.assertTrue(has_pending_text_drafts("Original", "Original", {"enUS":"Draft"}))
    def test_unchanged_text_is_not_pending(self):
        self.assertFalse(has_pending_text_drafts("Original", "Original", {"enUS":""}))
    def test_text_without_selection_is_pending(self):
        self.assertTrue(has_pending_text_drafts("Entwurf", None, {}))

if __name__=="__main__":
    unittest.main()
