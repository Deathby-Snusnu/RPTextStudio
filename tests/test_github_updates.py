"""Offline GitHub version checker tests; no network needed."""
import base64
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

    def test_semver_suffixes_are_incomparable(self):
        with tempfile.TemporaryDirectory() as d:
            target = Path(d)
            addon = target / "HexerRP"
            addon.mkdir()
            for version in ("1.0.0-rc.1", "1.0.0+build.1"):
                with self.subTest(version=version):
                    (addon / "HexerRP.toc").write_text(
                        f"## Version: {version}\n## Interface: 16001\n"
                    )
                    with patch.object(updates, "_development", return_value=("1.0.0", "16001", "abcd")):
                        row = updates.check_addon("HexerRP", target, "development")
                    self.assertEqual(row.status, "Unvergleichbar")

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

    def test_stable_release_tag_with_semver_suffix_is_not_available(self):
        with tempfile.TemporaryDirectory() as d:
            for tag in ("v1.0.0-rc.1", "v1.0.0+build.1"):
                with self.subTest(tag=tag):
                    with patch.object(updates, "_api", return_value={"tag_name": tag}):
                        row = updates.check_addon("HexerRP", Path(d), "stable")
                    self.assertEqual(row.status, "Kein Release / nicht verfügbar")
                    self.assertEqual(row.detail, "Release-Tag ist keine numerische Version.")

    def test_stable_release_uses_tag_toc_for_interface(self):
        with tempfile.TemporaryDirectory() as d:
            addon = Path(d) / "HexerRP"
            addon.mkdir()
            (addon / "HexerRP.toc").write_text("## Version: 0.2.0\n## Interface: 16001\n")
            release = {
                "tag_name": "v0.3.0",
                "html_url": "https://github.com/Deathby-Snusnu/HexerRP/releases/tag/v0.3.0",
            }
            toc = {
                "encoding": "base64",
                "content": base64.b64encode(b"## Version: 0.3.0\n## Interface: 11000\n").decode(),
            }
            with patch.object(updates, "_api", side_effect=(release, toc)) as api:
                row = updates.check_addon("HexerRP", Path(d), "stable")
            self.assertEqual(row.status, "Kompatibilität prüfen")
            self.assertEqual(
                api.call_args_list[1].args[0],
                "/repos/Deathby-Snusnu/HexerRP/contents/HexerRP.toc?ref=v0.3.0",
            )

    def test_reject_unknown_repository(self):
        with tempfile.TemporaryDirectory() as d:
            with self.assertRaises(ValueError):
                updates.check_addon("NotInAllowlist", Path(d))


if __name__ == "__main__":
    unittest.main()
