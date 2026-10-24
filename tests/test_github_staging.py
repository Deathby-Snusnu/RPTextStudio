"""Offline tests for bounded, non-installing GitHub archive staging."""
import io
import stat
import tempfile
import unittest
import zipfile
from pathlib import Path
from unittest.mock import patch
from github_staging import _validate_zip, stage, DownloadError


class GitHubStagingTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)

    def archive(self, files: dict[str, str | bytes]):
        target = self.root / "source.zip"
        with zipfile.ZipFile(target, "w") as z:
            for name, data in files.items():
                z.writestr(name, data)
        return target

    def valid(self):
        return {
            "owner-HexerRP-abc/HexerRP.toc": "## Version: 0.3.0\n## Interface: 16001\nHexerRP.lua\n",
            "owner-HexerRP-abc/HexerRP.lua": "print('ready')",
            "owner-HexerRP-abc/tests/not-for-runtime.lua": "test",
        }

    def test_validates_only_runtime_files(self):
        entries, version, interface = _validate_zip(self.archive(self.valid()), "HexerRP")
        self.assertEqual(version, "0.3.0")
        self.assertEqual(interface, "16001")
        self.assertEqual(set(entries), {"HexerRP.toc", "HexerRP.lua"})

    def test_blocks_traversal(self):
        content = self.valid()
        content["owner-HexerRP-abc/../escape.lua"] = "bad"
        with self.assertRaises(DownloadError):
            _validate_zip(self.archive(content), "HexerRP")

    def test_blocks_duplicate_case_insensitive_paths(self):
        content = self.valid()
        content["owner-HexerRP-abc/hexerrp.lua"] = "duplicate"
        with self.assertRaises(DownloadError):
            _validate_zip(self.archive(content), "HexerRP")

    def test_blocks_symlink(self):
        archive = self.root / "link.zip"
        with zipfile.ZipFile(archive, "w") as z:
            for name, data in self.valid().items():
                z.writestr(name, data)
            link = zipfile.ZipInfo("owner-HexerRP-abc/shortcut.lua")
            link.create_system = 3
            link.external_attr = (stat.S_IFLNK | 0o777) << 16
            z.writestr(link, "../outside")
        with self.assertRaises(DownloadError):
            _validate_zip(archive, "HexerRP")

    def test_toc_missing_dependency(self):
        content = self.valid()
        del content["owner-HexerRP-abc/HexerRP.lua"]
        with self.assertRaises(DownloadError):
            _validate_zip(self.archive(content), "HexerRP")

    def test_staging_never_targets_wow(self):
        wow = self.root / "Interface" / "AddOns"
        wow.mkdir(parents=True)
        with patch("github_staging._resolve", side_effect=AssertionError("network")):
            with self.assertRaises(DownloadError):
                stage("HexerRP", "stable", wow / "test")

    def test_successful_staging_does_not_modify_existing_files(self):
        archive = self.archive(self.valid())
        destination = self.root / "prepared-HexerRP"
        def fetch(commit, name, output):
            output.write_bytes(archive.read_bytes())
            return "x" * 64
        with patch("github_staging._resolve", return_value=("a" * 40, "0.3.0")), \
             patch("github_staging._download", side_effect=fetch):
            result = stage("HexerRP", "stable", destination)
        self.assertEqual(result.version, "0.3.0")
        self.assertEqual((destination / "HexerRP.lua").read_text(), "print('ready')")
        self.assertFalse((destination / "tests").exists())
        self.assertFalse((self.root / "Interface").exists())

    def test_version_mismatch_leaves_no_destination(self):
        archive = self.archive(self.valid())
        destination = self.root / "rejected"
        def fetch(commit, name, output):
            output.write_bytes(archive.read_bytes())
            return "x" * 64
        with patch("github_staging._resolve", return_value=("a" * 40, "0.4.0")), \
             patch("github_staging._download", side_effect=fetch):
            with self.assertRaises(DownloadError):
                stage("HexerRP", "stable", destination)
        self.assertFalse(destination.exists())


if __name__ == "__main__":
    unittest.main()
