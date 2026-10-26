"""Regression tests for invisible GitHub CLI subprocesses."""
import io
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

    def test_github_api_uses_https_without_subprocess(self):
        import github_updates
        with patch("github_updates.urllib.request.urlopen", return_value=io.BytesIO(b"{}")) as request, \
             patch("subprocess.run", side_effect=AssertionError("Subprocess called")):
            github_updates._api("/repos/Deathby-Snusnu/PaladinRP")
        self.assertTrue(request.call_args.args[0].full_url.startswith("https://"))


if __name__ == "__main__":
    unittest.main()
