"""Static regression checks for safe sequential multi-addon updates."""
from pathlib import Path
import unittest

SOURCE = (Path(__file__).resolve().parents[1] / "user_addon_manager_gui.py")

class MultiSelectUpdateTests(unittest.TestCase):
    def test_multiple_rows_and_queue(self):
        text = SOURCE.read_text(encoding="utf-8")
        self.assertIn("setSelectionMode(QTableWidget.ExtendedSelection)", text)
        self.assertIn("self.table.selectionModel().selectedRows()", text)
        self.assertIn("self._update_queue = list(names)", text)
        self.assertIn("self._advance_update_queue()", text)
        self.assertIn('self._start("stage", name=name, staging_target=destination)', text)

    def test_every_addon_uses_existing_approval_flow(self):
        text = SOURCE.read_text(encoding="utf-8")
        self.assertIn("self.install_selected()", text)
        self.assertIn("completed_install = self._operation == \"install\" and self._batch_waiting_install", text)
        self.assertIn("self._scan_after_cleanup = False  # Batch scan once after last addon.", text)

if __name__ == "__main__":
    unittest.main()
