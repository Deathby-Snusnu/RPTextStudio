"""Regression guards for the guided existing-add-on update entry point."""
import ast
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]


class ExistingUpdateFlowTests(unittest.TestCase):
    def test_gui_parses_and_preserves_protected_review(self):
        source = (ROOT / "user_addon_manager_gui.py").read_text(encoding="utf-8")
        ast.parse(source)
        self.assertIn('def update_selected(self):', source)
        self.assertIn('self._start("stage", name=name, staging_target=destination)', source)
        self.assertIn('self.install_selected()', source)
        self.assertIn('if plan.protected:', source)
        self.assertIn('replacements = self._choose_overwrites(plan)', source)
        self.assertIn('self._start("install", staging_target=(plan, profile))', source)

    def test_existing_update_reuses_installed_guard(self):
        source = (ROOT / "user_addon_manager_gui.py").read_text(encoding="utf-8")
        self.assertIn('self.installed[name].state != "Installiert"', source)
        self.assertIn('self._guided_update_name = None', source)


if __name__ == "__main__":
    unittest.main()
