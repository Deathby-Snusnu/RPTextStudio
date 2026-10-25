"""Offline regression tests for text-only, three-way Lua merge preview."""
import unittest
from rp_text_merge import preview_text_merge


def lua(*items):
    return 'addon.texts = { HUNTERS_MARK = { ziel = {\n' + ''.join(
        '    "' + s + '",\n' for s in items
    ) + '} } }\n'


class TextMergeTests(unittest.TestCase):
    def test_new_texts_added_in_repo_order_without_overwriting_local(self):
        result = preview_text_merge(
            lua("Original", "Alter Standard"),
            lua("Mein OldSooty-Text", "Original"),
            lua("Original", "Alter Standard", "Neue Jagd", "Neuer Emote"))
        pool = result.pools[0]
        self.assertEqual(pool.result, ("Mein OldSooty-Text", "Original", "Neue Jagd", "Neuer Emote"))
        self.assertEqual(result.additions, 2)

    def test_locally_rewritten_original_is_not_reinserted(self):
        result = preview_text_merge(lua("Standard"), lua("Meine Version"), lua("Standard"))
        self.assertEqual(result.additions, 0)
        self.assertEqual(result.pools[0].result, ("Meine Version",))

    def test_no_duplicates_for_preexisting_local_new_text(self):
        result = preview_text_merge(lua("Alt"), lua("Alt", "Neu"), lua("Alt", "Neu", "Neu"))
        self.assertEqual(result.additions, 0)

    def test_no_baseline_does_not_guess(self):
        result = preview_text_merge('addon.texts = {}\n', lua("Lokal"), lua("Repo"))
        self.assertEqual(result.conflicts, 1)
        self.assertEqual(result.safe_updates, {})

    def test_new_pool_requires_review(self):
        local = lua("Lokal")
        upstream = local.replace('} } }', '}, gruppe = { "Neu", } } }')
        result = preview_text_merge(local, local, upstream)
        self.assertEqual(result.conflicts, 1)
        self.assertEqual(result.safe_updates, {})

    def test_new_nonliteral_text_list_requires_review(self):
        local = lua("Alt")
        upstream = ('addon.texts = { HUNTERS_MARK = { ziel = {"Alt"}, '
                    'gruppe = {"Neu", build_text()} } }\n')
        result = preview_text_merge(local, local, upstream)
        conflict = next(pool for pool in result.pools if pool.path[-1] == "gruppe")
        self.assertEqual(result.conflicts, 1)
        self.assertEqual(conflict.status, "Konflikt")
        self.assertEqual(result.safe_updates, {})

    def test_no_disk_modification(self):
        old, local, new = lua("Alt"), lua("Eigene Texte"), lua("Alt", "Repo")
        preview_text_merge(old, local, new)
        self.assertEqual(local, lua("Eigene Texte"))


if __name__ == "__main__":
    unittest.main()
