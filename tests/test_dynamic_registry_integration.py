"""Integration tests for dynamic registration and safe installation."""
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from addon_registry import discover, load_registry, register
from addon_project_generator import AddonProjectSpec, preview_project, generate_project
from addon_manager import preview, install, rollback
from github_updates import check_addon


class DynamicRegistryIntegration(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name) / "project"
        (self.root / "addons").mkdir(parents=True)
        self.target = Path(self.temp.name) / "game" / "Interface" / "AddOns"
        self.target.mkdir(parents=True)

    def test_new_mage_detected_installed_and_rolled_back(self):
        spec = AddonProjectSpec()
        generated = generate_project(self.root, spec, preview_project(self.root, spec))
        self.assertIn("MagierRP", discover(self.root))
        self.assertEqual(load_registry(self.root)["addons"][0]["repository"], None)
        plan = preview(self.root / "addons", self.target, ("MagierRP",))
        self.assertTrue(plan[0].is_changed)
        backup = install(self.root / "addons", self.target, ("MagierRP",), approved=plan)
        self.assertTrue((self.target / "MagierRP" / "MagierRP.toc").exists())
        rollback(self.target, backup)
        self.assertFalse((self.target / "MagierRP").exists())

    def test_no_repository_does_not_make_network_request(self):
        spec = AddonProjectSpec()
        generate_project(self.root, spec, preview_project(self.root, spec))
        with patch("github_updates._api", side_effect=AssertionError("network called")):
            result = check_addon("MagierRP", self.target, "stable", project=self.root)
        self.assertEqual(result.status, "Nicht zugeordnet")

    def test_legacy_addon_falls_back_to_known_repository(self):
        folder = self.root / "addons" / "JaegerRP"
        folder.mkdir()
        (folder / "JaegerRP.toc").write_text("## Version: 0.3.0\n", encoding="utf-8")
        with patch("github_updates._release", return_value=("0.4.0", None, "v0.4.0")), \
                patch("github_updates._release_interface", return_value=None):
            result = check_addon("JaegerRP", self.target, "stable", project=self.root)
        self.assertEqual(result.status, "Nicht installiert")

    def test_invalid_external_repository_rejected(self):
        folder = self.root / "addons" / "MagierRP"
        folder.mkdir()
        (folder / "MagierRP.toc").write_text("## Version: 0.1.0\n", encoding="utf-8")
        register(self.root, {"id": "MagierRP", "repository": "SomeoneElse/MagierRP"})
        with self.assertRaises(ValueError):
            check_addon("MagierRP", self.target, project=self.root)


if __name__ == "__main__":
    unittest.main()
