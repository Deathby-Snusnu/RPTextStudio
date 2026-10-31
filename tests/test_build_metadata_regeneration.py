"""Validate the build source-cleanliness exception for generated metadata."""
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
import prepare_build

class BuildMetadataRegression(unittest.TestCase):
    def test_generated_metadata_is_excluded_from_git_clean_check(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            calls = []
            def fake_run(args, **kwargs):
                calls.append(args)
                class Result:
                    stdout = "" if "status" in args else "a" * 40 + "\n"
                return Result()
            with patch.object(prepare_build.subprocess, "run", side_effect=fake_run):
                result = prepare_build.prepare(root)
            self.assertEqual(result["version"], prepare_build.APP_VERSION)
            self.assertIn(":(exclude)build_info.json", calls[0])
            self.assertIn(":(exclude)build_version.issinc", calls[0])
            self.assertEqual((root / "build_info.json").exists(), True)
            self.assertIn(prepare_build.APP_VERSION, (root / "build_version.issinc").read_text())

    def test_other_dirty_files_still_abort(self):
        with tempfile.TemporaryDirectory() as temp:
            def fake_run(args, **kwargs):
                class Result:
                    stdout = " M main.py\n"
                return Result()
            with patch.object(prepare_build.subprocess, "run", side_effect=fake_run):
                with self.assertRaises(RuntimeError):
                    prepare_build.prepare(Path(temp))

if __name__ == "__main__":
    unittest.main()
