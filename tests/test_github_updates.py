"""Offline GitHub version checker tests; no network needed."""
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
import github_updates as updates


class VersionCheckerTests(unittest.TestCase):
    def test_parse_toc(self):
        self.assertEqual(updates.parse_toc("## Interface: 16001\n## Version: 0.3.10\n"),
                         ("0.3.10", "16001"))

    def test_numeric_comparison(self):
        self.assertEqual(updates.compare_versions("0.3.9", "0.3.10"), -1)
        self.assertEqual(updates.compare_versions("0.3.10", "0.3.9"), 1)
        self.assertEqual(updates.compare_versions("0.2", "0.2.0"), 0)
        self.assertIsNone(updates.compare_versions("v1.2", "1.2"))

    def test_development_newer(self):
        with tempfile.TemporaryDirectory() as d:
            target = Path(d)
            addon = target / "HexerRP"
            addon.mkdir()
            (addon / "HexerRP.toc").write_text("## Version: 0.3.9\n## Interface: 16001\n")
            with patch.object(updates, "_development", return_value=("0.3.10", "16001", "abcd")):
                row = updates.check_addon("HexerRP", target, "development")
            self.assertEqual(row.status, "Neuer Quellstand")
            self.assertEqual(row.commit_sha, "abcd")

    def test_interface_mismatch(self):
        with tempfile.TemporaryDirectory() as d:
            addon = Path(d) / "HexerRP"
            addon.mkdir()
            (addon / "HexerRP.toc").write_text("## Version: 0.2.0\n## Interface: 16001\n")
            with patch.object(updates, "_development", return_value=("0.3.0", "11000", "abcd")):
                self.assertEqual(updates.check_addon("HexerRP", Path(d), "development").status,
                                 "Kompatibilität prüfen")

    def test_missing_local(self):
        with tempfile.TemporaryDirectory() as d:
            with patch.object(updates, "_development", return_value=("0.3.0", "16001", "abcd")):
                self.assertEqual(updates.check_addon("HexerRP", Path(d), "development").status,
                                 "Nicht installiert")

    def test_no_stable_release(self):
        with tempfile.TemporaryDirectory() as d:
            with patch.object(updates, "_release", side_effect=updates.GitHubCheckError("404")):
                row = updates.check_addon("DruidenRP", Path(d), "stable")
                self.assertEqual(row.status, "Kein Release / nicht verfügbar")

    def test_reject_unknown_repository(self):
        with tempfile.TemporaryDirectory() as d:
            with self.assertRaises(ValueError):
                updates.check_addon("NotInAllowlist", Path(d))


if __name__ == "__main__":
    unittest.main()
