"""Build provenance and title must use the same version."""
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
import app_build_info


class BuildInfoTests(unittest.TestCase):
    def test_title_for_development(self):
        with patch.object(app_build_info, "INFO_FILE", Path("not-present-anywhere.json")):
            self.assertIn(app_build_info.APP_VERSION, app_build_info.window_title())
            self.assertIn("Quellcode", app_build_info.window_title())

    def test_embedded_commit(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "build_info.json"
            path.write_text(json.dumps({"version": app_build_info.APP_VERSION,
                                        "commit": "a" * 40}), encoding="utf-8")
            with patch.object(app_build_info, "INFO_FILE", path), \
                    patch.object(app_build_info.sys, "frozen", True, create=True):
                self.assertIn("aaaaaaaaaaaa", app_build_info.window_title())

    def test_source_launch_ignores_leftover_metadata(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "build_info.json"
            path.write_text(json.dumps({"version": app_build_info.APP_VERSION,
                                        "commit": "a" * 40}), encoding="utf-8")
            with patch.object(app_build_info, "INFO_FILE", path):
                self.assertIn("Quellcode", app_build_info.window_title())

    def test_mismatched_version_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "build_info.json"
            path.write_text(json.dumps({"version": "0.0.0", "commit": "a" * 40}), encoding="utf-8")
            with patch.object(app_build_info, "INFO_FILE", path), \
                    patch.object(app_build_info.sys, "frozen", True, create=True):
                self.assertIn("Quellcode", app_build_info.window_title())


if __name__ == "__main__":
    unittest.main()
