"""Static checks for the Inno Setup Windows installer configuration."""
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class InnoSetupTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.setup = (ROOT / "installer.iss").read_text(encoding="utf-8")
        cls.builder = (ROOT / "build_installer.bat").read_text(encoding="utf-8").lower()

    def test_per_user_installation(self):
        self.assertIn("PrivilegesRequired=lowest", self.setup)
        self.assertIn(r"DefaultDirName={localappdata}\Programs\RPTextStudio", self.setup)
        self.assertNotIn("PrivilegesRequiredOverridesAllowed", self.setup)

    def test_executable_and_shortcuts(self):
        self.assertIn('Source: "dist\\{#AppExe}"', self.setup)
        self.assertIn('Filename: "{app}\\{#AppExe}"', self.setup)
        self.assertIn("Tasks: desktopicon", self.setup)
        self.assertIn("Flags: unchecked", self.setup)

    def test_uninstaller_does_not_delete_user_data(self):
        self.assertIn("[UninstallDelete]", self.setup)
        self.assertNotIn("recursesubdirs", self.setup.lower())
        self.assertNotIn(r"{userappdata}", self.setup.lower())
        self.assertNotIn(r"{localappdata}\RPTextStudio", self.setup)

    def test_build_script_uses_both_compilers(self):
        self.assertIn("call \"%~dp0build_exe.bat\"", self.builder)
        self.assertIn("if errorlevel 1 goto :failed", self.builder)
        self.assertIn("iscc", self.builder)
        self.assertIn("installer.iss", self.builder)
        self.assertIn("dist\\rptextstudio.exe", self.builder)

    def test_setup_version_and_identity(self):
        self.assertIn("#define AppVersion", self.setup)
        self.assertIn("AppId=", self.setup)
        self.assertIn("OutputBaseFilename=RPTextStudio-Setup-{#AppVersion}", self.setup)


if __name__ == "__main__":
    unittest.main()
