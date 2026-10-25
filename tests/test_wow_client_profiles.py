"""Offline tests of per-client profiles and non-writing TOC preview."""
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from wow_client_profiles import (
    save_profile, get_profile, preview_toc, compatibility, interface_line,
)


class ClientProfileTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.base = Path(self.tmp.name)
        self.root = self.base / "_classic_era_"
        self.root.mkdir()
        (self.root / "WowClassic.exe").write_bytes(b"dummy")
        (self.root / "Interface" / "AddOns").mkdir(parents=True)
        self.settings = self.base / "profiles.json"

    def test_profile_roundtrip_without_modifying_toc(self):
        addon = self.root / "Interface" / "AddOns" / "JaegerRP"
        addon.mkdir()
        toc = addon / "JaegerRP.toc"
        toc.write_text("## Interface: 16001\n## Version: 0.5.0\n")
        save_profile(self.root, "11509", self.settings)
        self.assertEqual(get_profile(self.root, self.settings).interface, "11509")
        self.assertEqual(toc.read_text(), "## Interface: 16001\n## Version: 0.5.0\n")

    def test_invalid_interface_rejected(self):
        for value in ("abc", "0", "16001, 11509", "00000", "12"):
            with self.subTest(value=value), self.assertRaises(ValueError):
                save_profile(self.root, value, self.settings)

    def test_toc_preview_requires_explicit_compatibility(self):
        toc = "## Interface: 16001\r\n## Version: 0.5.0\r\n"
        with self.assertRaises(ValueError):
            preview_toc(toc, "11509")
        self.assertEqual(preview_toc(toc, "11509", compatible=True),
                         "## Interface: 11509\r\n## Version: 0.5.0\r\n")

    def test_toc_preview_replaces_empty_interface_without_changing_version(self):
        toc = "## Interface:\n## Version: 0.5.0\n"
        self.assertEqual(preview_toc(toc, "11509", compatible=True),
                         "## Interface: 11509\n## Version: 0.5.0\n")

    def test_toc_preview_rejects_duplicate_interface_fields(self):
        toc = "## Interface:\n## Interface: 16001\n"
        with self.assertRaises(ValueError):
            preview_toc(toc, "11509", compatible=True)

    def test_interface_line_uses_preview_header_matching(self):
        for line in ("##Interface: 16001", "## Interface : 16001"):
            with self.subTest(line=line):
                self.assertEqual(interface_line(line), line)

    def test_no_automatic_compatibility_for_classic_era(self):
        profile = save_profile(self.root, "11509", self.settings)
        self.assertEqual(compatibility("JaegerRP", profile), "Nicht als kompatibel bestätigt")


if __name__ == "__main__":
    unittest.main()
