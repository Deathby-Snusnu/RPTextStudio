import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class BuildExeTests(unittest.TestCase):
    def test_startup_logo_is_bundled_at_runtime_path(self):
        build = (ROOT / "build_exe.bat").read_text(encoding="utf-8")
        bundled_assets = {
            (source.replace("\\", "/"), destination)
            for source, destination in re.findall(
                r'--add-data "%~dp0([^";]+);([^"]+)"', build
            )
        }
        self.assertIn(("assets/rp_text_studio.svg", "assets"), bundled_assets)
        self.assertTrue((ROOT / "assets" / "rp_text_studio.svg").is_file())

    def test_missing_startup_logo_aborts_before_build(self):
        build = (ROOT / "build_exe.bat").read_text(encoding="utf-8")
        check = re.search(
            r'if not exist "%~dp0assets\\rp_text_studio\.svg" \((.*?)\)',
            build,
            re.DOTALL,
        )
        self.assertIsNotNone(check)
        self.assertIn("goto :failed", check.group(1))
        self.assertLess(check.start(), build.index(" -m PyInstaller"))


if __name__ == "__main__":
    unittest.main()
