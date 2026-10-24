"""Regression tests for invisible GitHub CLI subprocesses."""
import os
import unittest
from unittest.mock import patch
from subprocess_windows import hidden_subprocess_kwargs


class WindowsSubprocessTests(unittest.TestCase):
    def test_other_platforms_need_no_flags(self):
        with patch("subprocess_windows.os.name", "posix"):
            self.assertEqual(hidden_subprocess_kwargs(), {})

    @unittest.skipUnless(os.name == "nt", "Windows-only process startup fields")
    def test_windows_creation_flags(self):
        import subprocess
        opts = hidden_subprocess_kwargs()
        self.assertTrue(opts["creationflags"] & subprocess.CREATE_NO_WINDOW)
        self.assertTrue(opts["startupinfo"].dwFlags & subprocess.STARTF_USESHOWWINDOW)
        self.assertEqual(opts["startupinfo"].wShowWindow, subprocess.SW_HIDE)

    def test_github_api_uses_hidden_flags(self):
        from pathlib import Path
        source = (Path(__file__).resolve().parents[1] / "github_updates.py").read_text(encoding="utf-8")
        self.assertIn("**hidden_subprocess_kwargs()", source)


if __name__ == "__main__":
    unittest.main()
