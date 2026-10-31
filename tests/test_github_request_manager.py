"""Network-free regressions for the shared GitHub request guard."""
import io
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import github_request_manager as guard

class DummyResponse:
    def __init__(self, payload=b'{"ok":true}', headers=None):
        self.payload = payload
        self.headers = headers or {"ETag": '"abc"', "X-RateLimit-Limit":"60",
                                   "X-RateLimit-Remaining":"55"}
    def __enter__(self): return self
    def __exit__(self, *args): pass
    def read(self, size): return self.payload

class GuardTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.path = Path(self.tmp.name) / "cache.json"
        self._old = (guard._MEMORY, guard._NEXT_CALL, guard._BLOCK_UNTIL)
        guard._MEMORY, guard._NEXT_CALL, guard._BLOCK_UNTIL = {}, 0, 0
        self.addCleanup(self.restore)

    def restore(self):
        guard._MEMORY, guard._NEXT_CALL, guard._BLOCK_UNTIL = self._old

    def test_cached_second_call(self):
        with patch.object(guard, "_store_path", return_value=self.path), \
             patch.object(guard.urllib.request, "urlopen", return_value=DummyResponse()) as get:
            self.assertTrue(guard.get_json("/repos/Deathby-Snusnu/MagierRP")["ok"])
            self.assertTrue(guard.get_json("/repos/Deathby-Snusnu/MagierRP")["ok"])
            self.assertEqual(get.call_count, 1)
            self.assertTrue(self.path.exists())

    def test_preexisting_backoff_does_not_call_network(self):
        with patch.object(guard, "_store_path", return_value=self.path), \
             patch.object(guard.urllib.request, "urlopen") as get:
            with patch.object(guard.time, "time", return_value=100):
                guard._BLOCK_UNTIL = 160
                with self.assertRaises(guard.RequestGuardError):
                    guard.get_json("/repos/Deathby-Snusnu/MagierRP")
            get.assert_not_called()

    def test_reject_external_path(self):
        with self.assertRaises(guard.RequestGuardError):
            guard.get_json("/repos/SomeOtherOwner/Repo")

if __name__ == "__main__":
    unittest.main()
