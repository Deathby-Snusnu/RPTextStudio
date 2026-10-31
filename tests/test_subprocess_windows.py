"""Regression tests for invisible GitHub CLI subprocesses."""
import io
import os
import tempfile
import unittest
from pathlib import Path
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
        import github_request_manager as guard
        import github_updates
        class Response(io.BytesIO):
            status = 200
            headers = {}

            def getcode(self):
                return 200

        response = Response(b"{}")
        with tempfile.TemporaryDirectory() as tmp, \
             patch.multiple(guard, _MEMORY={}, _NEXT_CALL=0.0, _BLOCK_UNTIL=0.0), \
             patch.object(guard, "_store_path", return_value=Path(tmp) / "cache.json"), \
             patch.dict(os.environ, {"GH_TOKEN": "", "GITHUB_TOKEN": ""}), \
             patch("github_updates.urllib.request.urlopen", return_value=response) as request, \
             patch("subprocess.run") as run, \
             patch("subprocess.Popen") as popen:
            github_updates._api("/repos/Deathby-Snusnu/PaladinRP")
        request.assert_called_once()
        run.assert_not_called()
        popen.assert_not_called()
        args, kwargs = request.call_args
        url = args[0] if args else kwargs["url"]
        if hasattr(url, "full_url"):
            url = url.full_url
        self.assertTrue(str(url).startswith("https://"))


if __name__ == "__main__":
    unittest.main()
