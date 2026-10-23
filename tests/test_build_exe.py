import re
import unittest
from pathlib import Path
from xml.etree import ElementTree


ROOT = Path(__file__).resolve().parents[1]


class BuildExeTests(unittest.TestCase):
    def setUp(self):
        main = (ROOT / "main.py").read_text(encoding="utf-8")
        match = re.search(
            r"logo_path = Path\(__file__\)\.resolve\(\)\.parent / 'assets' / '([^']+)'",
            main,
        )
        self.assertIsNotNone(match)
        self.logo_name = match.group(1)

    def test_startup_logo_is_bundled_at_runtime_path(self):
        build = (ROOT / "build_exe.bat").read_text(encoding="utf-8")
        bundled_assets = {
            (source.replace("\\", "/"), destination)
            for source, destination in re.findall(
                r'--add-data "%~dp0([^";]+);([^"]+)"', build
            )
        }
        self.assertIn((f"assets/{self.logo_name}", "assets"), bundled_assets)
        logo = ElementTree.parse(ROOT / "assets" / self.logo_name).getroot()
        self.assertEqual(logo.tag, "{http://www.w3.org/2000/svg}svg")

    def test_missing_startup_logo_aborts_before_build(self):
        build = (ROOT / "build_exe.bat").read_text(encoding="utf-8")
        check = re.search(
            r'if not exist "%~dp0assets\\' + re.escape(self.logo_name) + r'" \((.*?)\)',
            build,
            re.DOTALL,
        )
        self.assertIsNotNone(check)
        self.assertIn("goto :failed", check.group(1))
        self.assertLess(check.start(), build.index(" -m PyInstaller"))

    def test_collection_starter_uses_current_sources_before_old_executable(self):
        start = (ROOT / "Start.bat").read_text(encoding="utf-8")
        guard = 'if exist "%~dp0..\\..\\addons\\" goto :start_python'
        self.assertIn(guard, start)
        self.assertLess(start.index(guard), start.index('set "STUDIO_EXE="'))
        self.assertIn('set "VENV_DIR=%~dp0..\\..\\.venv"', start)
        self.assertNotIn('call "%VENV_ACTIVATE%"', start)

    def test_build_bundles_manual_from_collection_docs(self):
        build = (ROOT / "build_exe.bat").read_text(encoding="utf-8")
        self.assertIn('set "MANUAL=%~dp0..\\..\\docs\\RPTextStudio\\HANDBUCH.md"', build)
        self.assertIn('--add-data "%MANUAL%;."', build)


if __name__ == "__main__":
    unittest.main()
