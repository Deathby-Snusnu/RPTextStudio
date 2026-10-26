"""Selected first-install packages must not include unselected or installed addons."""
import unittest
from unittest.mock import patch
from pathlib import Path
import tempfile

from batch_addon_install import prepare_missing
from addon_manager import InstallError


class GuidedSelectionTests(unittest.TestCase):
    def test_rejects_unknown_or_duplicate_selection_before_staging(self):
        with patch("batch_addon_install.inspect_client") as inspect, \
             patch("batch_addon_install.missing_names", return_value=("PaladinRP", "JaegerRP")), \
             patch("batch_addon_install.stage", side_effect=AssertionError("download attempted")):
            inspect.return_value.verified = True
            inspect.return_value.client_root.resolve.return_value = Path("wow").resolve()
            profile = type("Profile", (), {"client_root": Path("wow")})()
            for selected in ((), ("UnknownRP",), ("PaladinRP", "PaladinRP")):
                with self.subTest(selected=selected), self.assertRaises(InstallError):
                    prepare_missing(Path("wow/Interface/AddOns"), profile, names=selected)

    def test_selection_must_not_include_already_installed_addon(self):
        with patch("batch_addon_install.inspect_client") as inspect, \
             patch("batch_addon_install.missing_names", return_value=("JaegerRP",)), \
             patch("batch_addon_install.stage", side_effect=AssertionError("download attempted")):
            inspect.return_value.verified = True
            inspect.return_value.client_root.resolve.return_value = Path("wow").resolve()
            profile = type("Profile", (), {"client_root": Path("wow")})()
            with self.assertRaises(InstallError):
                prepare_missing(Path("wow/Interface/AddOns"), profile, names=("PaladinRP",))


if __name__ == "__main__":
    unittest.main()
