"""Public GitHub access must not require GitHub CLI or an account."""
import io
import json
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import github_updates
import github_staging


class Response:
    def __init__(self, payload):
        self.payload = payload
    def __enter__(self):
        return self
    def __exit__(self, *args):
        return False
    def read(self, size=-1):
        return self.payload[:size]


class PublicGithubTests(unittest.TestCase):
    def test_public_api_does_not_need_cli_or_token(self):
        with patch.dict(os.environ, {}, clear=True), \
             patch("github_updates.urllib.request.urlopen", return_value=Response(b'{"tag_name":"v1.0.0"}')) as call, \
             patch("subprocess.run", side_effect=AssertionError("CLI called")):
            result = github_updates._api("/repos/Deathby-Snusnu/PaladinRP/releases/latest")
        self.assertEqual(result["tag_name"], "v1.0.0")
        self.assertIsNone(call.call_args.args[0].get_header("Authorization"))

    def test_explicit_token_can_authenticate(self):
        with patch.dict(os.environ, {"GH_TOKEN": "example"}, clear=True), \
             patch("github_updates.urllib.request.urlopen", return_value=Response(b"{}")) as call:
            github_updates._api("/repos/Deathby-Snusnu/PaladinRP")
        self.assertEqual(call.call_args.args[0].get_header("Authorization"), "Bearer example")

    def test_zip_download_public_request_without_token(self):
        class Opener:
            def open(self, req, timeout=None):
                self.req = req
                return Response(b"public archive bytes")
        opener = Opener()
        with tempfile.TemporaryDirectory() as root, \
             patch.dict(os.environ, {}, clear=True), \
             patch("github_staging.build_opener", return_value=opener), \
             patch("subprocess.run", side_effect=AssertionError("CLI called")):
            output = Path(root) / "archive.zip"
            digest = github_staging._download("a" * 40, "PaladinRP", output)
            self.assertEqual(output.read_bytes(), b"public archive bytes")
            self.assertEqual(len(digest), 64)
            self.assertIsNone(opener.req.get_header("Authorization"))

    def test_url_restricted_to_owner(self):
        with self.assertRaises(github_updates.GitHubCheckError):
            github_updates._api("/repos/Other/PaladinRP")


if __name__ == "__main__":
    unittest.main()
