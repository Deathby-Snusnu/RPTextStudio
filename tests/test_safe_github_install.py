"""Offline regression tests for additive GitHub installation and backup."""
import tempfile
import unittest
from pathlib import Path
from safe_github_install import preview_safe_install, install_safe
from wow_client_profiles import ClientProfile


class SafeGitHubInstallTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name) / "_classic_era_"
        self.root.mkdir()
        (self.root / "WowClassic.exe").write_bytes(b"stub")
        (self.root / "WTF").mkdir()
        self.target = self.root / "Interface" / "AddOns"
        self.target.mkdir(parents=True)
        self.profile = ClientProfile(self.root, "classic_era", "11509", "manual")
        self.source = Path(self.tmp.name) / "Staging"
        self.source.mkdir()
        (self.source / "JaegerRP.toc").write_text("## Interface: 16001\n## Version: 0.5.0\nCore.lua\n", encoding="utf8")
        (self.source / "Core.lua").write_text("NEW ENGINE", encoding="utf8")

    def test_existing_local_text_and_code_protected_with_new_file_added(self):
        existing = self.target / "JaegerRP"
        existing.mkdir()
        (existing / "JaegerRP.toc").write_text("## Interface: 16001\n## Version: 0.4.0\n", encoding="utf8")
        (existing / "Core.lua").write_text("LOCAL CODE", encoding="utf8")
        (existing / "MyCustom.lua").write_text("OWN WORDS", encoding="utf8")
        (self.source / "NewFeature.lua").write_text("NEW", encoding="utf8")
        plan = preview_safe_install("JaegerRP", self.source, self.target, self.profile)
        self.assertIn("Core.lua", plan.protected)
        self.assertIn("NewFeature.lua", plan.new_files)
        backup = install_safe(plan, self.profile)
        self.assertEqual((existing / "Core.lua").read_text(), "LOCAL CODE")
        self.assertEqual((existing / "MyCustom.lua").read_text(), "OWN WORDS")
        self.assertEqual((existing / "NewFeature.lua").read_text(), "NEW")
        self.assertIn("## Interface: 11509", (existing / "JaegerRP.toc").read_text())
        self.assertEqual((backup / "JaegerRP" / "Core.lua").read_text(), "LOCAL CODE")

    def test_refuses_changed_source_after_preview(self):
        plan = preview_safe_install("JaegerRP", self.source, self.target, self.profile)
        (self.source / "Core.lua").write_text("TAMPERED", encoding="utf8")
        with self.assertRaises(Exception):
            install_safe(plan, self.profile)
        self.assertFalse((self.target / "JaegerRP").exists())


if __name__ == "__main__":
    unittest.main()
