"""Offline regression tests for additive GitHub installation and backup."""
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from safe_github_install import preview_safe_install, install_safe
from addon_manager import rollback
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
        rollback(self.target, backup)
        self.assertFalse((existing / "NewFeature.lua").exists())
        self.assertEqual((existing / "Core.lua").read_text(), "LOCAL CODE")
        self.assertEqual((existing / "JaegerRP.toc").read_text().splitlines()[0], "## Interface: 16001")

    def test_explicitly_approved_replacement_creates_backup_and_rolls_back(self):
        existing = self.target / "JaegerRP"
        existing.mkdir()
        old_toc = "## Interface: 11509\n## Version: local\nCore.lua\n"
        (existing / "JaegerRP.toc").write_text(old_toc, encoding="utf8")
        (existing / "Core.lua").write_text("LOCAL CHANGES", encoding="utf8")
        (existing / "Personal.lua").write_text("KEEP PERSONAL TEXT", encoding="utf8")

        guarded = preview_safe_install("JaegerRP", self.source, self.target, self.profile)
        self.assertEqual(guarded.protected, ("Core.lua",))
        self.assertFalse(guarded.new_files)
        self.assertFalse(guarded.toc_changed)
        with self.assertRaises(Exception):
            install_safe(guarded, self.profile)
        self.assertEqual((existing / "Core.lua").read_text(), "LOCAL CHANGES")

        approved = preview_safe_install("JaegerRP", self.source, self.target, self.profile,
                                        approved_overwrites=("Core.lua",))
        self.assertEqual(approved.approved_overwrites, ("Core.lua",))
        backup = install_safe(approved, self.profile)
        self.assertEqual((existing / "Core.lua").read_text(), "NEW ENGINE")
        self.assertEqual((existing / "Personal.lua").read_text(), "KEEP PERSONAL TEXT")
        self.assertEqual((existing / "JaegerRP.toc").read_text(), old_toc)
        self.assertEqual((backup / "JaegerRP" / "Core.lua").read_text(), "LOCAL CHANGES")
        rollback(self.target, backup)
        self.assertEqual((existing / "Core.lua").read_text(), "LOCAL CHANGES")
        self.assertEqual((existing / "Personal.lua").read_text(), "KEEP PERSONAL TEXT")

    def test_approval_restricted_to_changed_existing_non_toc_files(self):
        existing = self.target / "JaegerRP"
        existing.mkdir()
        (existing / "JaegerRP.toc").write_text(
            "## Interface: 11509\n## Version: local\n", encoding="utf8"
        )
        (existing / "Core.lua").write_text("LOCAL", encoding="utf8")
        (existing / "JaegerRP_Classic.TOC").write_text("local metadata", encoding="utf8")
        (self.source / "JaegerRP_Classic.TOC").write_text("upstream metadata", encoding="utf8")
        plan = preview_safe_install("JaegerRP", self.source, self.target, self.profile)
        self.assertEqual(plan.protected, ("Core.lua",))
        for forbidden in (
            ("JaegerRP.toc",),
            ("JaegerRP_Classic.TOC",),
            ("missing.lua",),
            ("Core.lua", "Core.lua"),
        ):
            with self.subTest(forbidden=forbidden):
                with self.assertRaises(Exception):
                    preview_safe_install("JaegerRP", self.source, self.target, self.profile,
                                         approved_overwrites=forbidden)

    def test_approved_replacement_refuses_modified_local_file(self):
        existing = self.target / "JaegerRP"
        existing.mkdir()
        (existing / "JaegerRP.toc").write_text(
            "## Interface: 11509\n## Version: local\n", encoding="utf8"
        )
        core = existing / "Core.lua"
        core.write_text("MY FIRST EDIT", encoding="utf8")
        plan = preview_safe_install("JaegerRP", self.source, self.target, self.profile,
                                    approved_overwrites=("Core.lua",))
        core.write_text("MY SECOND EDIT", encoding="utf8")
        with self.assertRaises(Exception):
            install_safe(plan, self.profile)
        self.assertEqual(core.read_text(), "MY SECOND EDIT")

    def test_approved_replacement_keeps_existing_filename_spelling(self):
        existing = self.target / "JaegerRP"
        existing.mkdir()
        (existing / "jaegerRP.TOC").write_text(
            "## Interface: 11509\n## Version: local\n", encoding="utf8"
        )
        (existing / "core.lua").write_text("LOCAL", encoding="utf8")
        plan = preview_safe_install("JaegerRP", self.source, self.target, self.profile,
                                    approved_overwrites=("Core.lua",))
        install_safe(plan, self.profile)
        self.assertEqual((existing / "core.lua").read_text(), "NEW ENGINE")
        self.assertEqual({p.name for p in existing.iterdir()}, {"core.lua", "jaegerRP.TOC"})

    def test_case_only_collisions_preserve_existing_files_and_toc_bytes(self):
        existing = self.target / "JaegerRP"
        existing.mkdir()
        (existing / "core.lua").write_bytes(b"LOCAL CODE")
        toc_bytes = b"\xef\xbb\xbf## Interface: 16001\r\n## Version: local\nKeep\r\n"
        (existing / "jaegerRP.TOC").write_bytes(toc_bytes)

        plan = preview_safe_install("JaegerRP", self.source, self.target, self.profile)
        self.assertNotIn("Core.lua", plan.new_files)
        self.assertNotIn("JaegerRP.toc", plan.new_files)
        self.assertIn("Core.lua", plan.protected)
        self.assertTrue(plan.toc_changed)

        install_safe(plan, self.profile)
        self.assertEqual((existing / "core.lua").read_bytes(), b"LOCAL CODE")
        self.assertEqual({path.name for path in existing.iterdir()}, {"core.lua", "jaegerRP.TOC"})
        self.assertEqual(
            (existing / "jaegerRP.TOC").read_bytes(),
            b"\xef\xbb\xbf## Interface: 11509\r\n## Version: local\nKeep\r\n",
        )

    def test_new_addon_preview_reports_toc_adaptation_and_creates_target(self):
        self.target.rmdir()
        plan = preview_safe_install("JaegerRP", self.source, self.target, self.profile)
        self.assertTrue(plan.toc_changed)

        install_safe(plan, self.profile)
        self.assertIn("## Interface: 11509", (self.target / "JaegerRP" / "JaegerRP.toc").read_text())

    def test_failed_prepared_directory_rename_restores_original_bytes(self):
        existing = self.target / "JaegerRP"
        existing.mkdir()
        original = {
            "JaegerRP.toc": b"## Interface: 16001\n## Version: local\n",
            "Core.lua": b"LOCAL CODE",
            "custom.txt": b"PERSONAL DATA",
        }
        for rel, content in original.items():
            (existing / rel).write_bytes(content)
        plan = preview_safe_install("JaegerRP", self.source, self.target, self.profile)
        rename = Path.rename

        def fail_ready(path, destination):
            if path == existing and destination.parent.parent.name == ".addon-backups":
                manifest = destination.parent / "manifest.json"
                self.assertTrue(manifest.is_file())
                self.assertEqual(json.loads(manifest.read_text())["status"], "installing")
            if path.parent.name.startswith(".rpstudio-safe-") and path.name == "JaegerRP":
                raise OSError("injected prepared-directory rename failure")
            return rename(path, destination)

        with patch.object(Path, "rename", fail_ready):
            with self.assertRaises(OSError):
                install_safe(plan, self.profile)
        self.assertEqual({p.name: p.read_bytes() for p in existing.iterdir()}, original)

    def test_manifest_write_failure_leaves_original_bytes_untouched(self):
        existing = self.target / "JaegerRP"
        existing.mkdir()
        original = {
            "JaegerRP.toc": b"## Interface: 16001\n## Version: local\n",
            "Core.lua": b"LOCAL CODE",
            "custom.txt": b"PERSONAL DATA",
        }
        for rel, content in original.items():
            (existing / rel).write_bytes(content)
        plan = preview_safe_install("JaegerRP", self.source, self.target, self.profile)
        write_text = Path.write_text
        writes = 0

        def fail_manifest(path, *args, **kwargs):
            nonlocal writes
            if path.name == ".manifest.json.tmp":
                writes += 1
                if writes == 2:
                    raise OSError("injected final manifest write failure")
            return write_text(path, *args, **kwargs)

        with patch.object(Path, "write_text", fail_manifest):
            with self.assertRaises(OSError):
                install_safe(plan, self.profile)
        self.assertEqual({p.name: p.read_bytes() for p in existing.iterdir()}, original)

    def test_rollback_recovers_original_after_interrupted_directory_swap(self):
        existing = self.target / "JaegerRP"
        existing.mkdir()
        (existing / "Core.lua").write_bytes(b"ORIGINAL")
        backup = self.target / ".addon-backups" / "interrupted"
        backup.mkdir(parents=True)
        (backup / "manifest.json").write_text(json.dumps({
            "names": ["JaegerRP"],
            "previously_installed": ["JaegerRP"],
            "status": "installing",
        }), encoding="utf-8")
        existing.rename(backup / "JaegerRP")

        rollback(self.target, backup)

        self.assertEqual((existing / "Core.lua").read_bytes(), b"ORIGINAL")

    def test_refuses_changed_source_after_preview(self):
        plan = preview_safe_install("JaegerRP", self.source, self.target, self.profile)
        (self.source / "Core.lua").write_text("TAMPERED", encoding="utf8")
        with self.assertRaises(Exception):
            install_safe(plan, self.profile)
        self.assertFalse((self.target / "JaegerRP").exists())


if __name__ == "__main__":
    unittest.main()
