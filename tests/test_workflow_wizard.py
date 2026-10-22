import unittest
try:
    from workflow_wizard import prerequisites
except ImportError:
    prerequisites = None

@unittest.skipIf(prerequisites is None, "PySide6 nicht installiert")
class WorkflowPrerequisiteTests(unittest.TestCase):
    def test_project_needed(self):
        self.assertTrue(prerequisites("check", has_project=False,has_pool=False,has_row=False,locale="deDE"))
    def test_translation_requires_german_selection(self):
        issues=prerequisites("translate",has_project=True,has_pool=True,has_row=True,locale="enUS")
        self.assertEqual(len(issues),1)
    def test_ready(self):
        self.assertEqual(prerequisites("translate",has_project=True,has_pool=True,has_row=True,locale="deDE"),[])
    def test_spell_requires_pool(self):
        self.assertTrue(prerequisites("spell",has_project=True,has_pool=False,has_row=False,locale="deDE"))

if __name__=="__main__":
    unittest.main()
