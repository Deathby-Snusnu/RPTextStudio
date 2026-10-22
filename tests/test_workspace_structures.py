"""Offline tests for safe structure planning."""
import tempfile
import unittest
from pathlib import Path
from workspace_structures import (
    create_profile, create_spell, plan_spell, plan_profile,
)
from lua_text import parse_pools
from race_class_manager import load_registry

LOCALES = ("deDE", "enUS", "frFR")


def lua_file(locale, base, extra=""):
    return (
        f"addon.localeData.{locale}.{base} = {{\n"
        '    EXISTING = { ziel = { "Hi" }, gruppe = { "Hello" }, },\n'
        f"{extra}"
        "}\n"
    )


def backup_snapshot(paths):
    backups = {}
    for path in paths:
        backup = path.with_suffix(path.suffix + ".existing.bak")
        backup.write_bytes(b"existing backup")
        backups[backup] = backup.read_bytes()
    return backups


def assert_unchanged(test, originals, backups):
    for path, contents in originals.items():
        test.assertEqual(path.read_bytes(), contents)
    test.assertEqual(
        {path: path.read_bytes() for path in backups},
        backups,
    )
    test.assertEqual(
        {path for original in originals for path in original.parent.glob(original.name + ".*.bak")},
        set(backups),
    )

class StructurePlanTests(unittest.TestCase):
    def test_missing_file_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaises(ValueError):
                plan_spell(Path(tmp),"HexerRP",0,"","","SHADOW_BOLT")

    def test_invalid_key_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaises(ValueError):
                plan_spell(Path(tmp),"HexerRP",0,"","","NO WAY")

    def test_registry_only_profile_does_not_mutate(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp)
            self.assertEqual(plan_profile(root,"HexerRP","race","NightElf",
                                          "Nachtelf","Naturverbunden",False),[])
            self.assertEqual(list(root.iterdir()),[])

    def test_duplicate_registry_profile(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp)
            (root/".rptextstudio-races-classes.json").write_text(
                '{"version":1,"races":{"NightElf":{}},"classes":{}}',
                encoding="utf-8")
            with self.assertRaises(ValueError):
                plan_profile(root,"HexerRP","race","NightElf","Nachtelf","",False)

    def test_duplicate_in_last_spell_locale_preserves_files_and_backups(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            paths = []
            for locale in LOCALES:
                path = root / "HexerRP" / "locales" / locale / "Texts.lua"
                path.parent.mkdir(parents=True)
                extra = (
                    '    NEW_SPELL = { ziel = { "Already here" }, },\n'
                    if locale == "frFR" else ""
                )
                path.write_text(lua_file(locale, "texts", extra), encoding="utf-8")
                paths.append(path)
            originals = {path: path.read_bytes() for path in paths}
            backups = backup_snapshot(paths)

            with self.assertRaises(ValueError):
                create_spell(root, "HexerRP", 0, "", "", "NEW_SPELL")

            assert_unchanged(self, originals, backups)

    def test_invalid_last_spell_locale_preserves_files_and_backups(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            paths = []
            for locale in LOCALES:
                path = root / "HexerRP" / "locales" / locale / "Texts.lua"
                path.parent.mkdir(parents=True)
                contents = lua_file(locale, "texts")
                if locale == "frFR":
                    contents += lua_file(locale, "other")
                path.write_text(contents, encoding="utf-8")
                paths.append(path)
            originals = {path: path.read_bytes() for path in paths}
            backups = backup_snapshot(paths)

            with self.assertRaises(ValueError):
                create_spell(root, "HexerRP", 0, "", "", "NEW_SPELL")

            assert_unchanged(self, originals, backups)

    def test_duplicate_in_last_profile_locale_preserves_files_and_backups(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            paths = []
            for locale in LOCALES:
                path = root / "HexerRP" / "locales" / locale / "Racial.lua"
                path.parent.mkdir(parents=True)
                extra = (
                    '    NightElf = { RP_GREETING = { ziel = { "Already here" }, }, },\n'
                    if locale == "frFR" else ""
                )
                path.write_text(lua_file(locale, "racial", extra), encoding="utf-8")
                paths.append(path)
            originals = {path: path.read_bytes() for path in paths}
            backups = backup_snapshot(paths)

            with self.assertRaises(ValueError):
                create_profile(root, "HexerRP", "race", "NightElf", "Nachtelf", "", True)

            assert_unchanged(self, originals, backups)
            self.assertFalse((root / ".rptextstudio-races-classes.json").exists())

    def test_successful_spell_creation_updates_all_locales_and_backups(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            paths = []
            for locale in LOCALES:
                path = root / "HexerRP" / "locales" / locale / "Texts.lua"
                path.parent.mkdir(parents=True)
                path.write_text(lua_file(locale, "texts"), encoding="utf-8")
                paths.append(path)
            originals = {path: path.read_bytes() for path in paths}

            self.assertEqual(create_spell(root, "HexerRP", 0, "", "", "NEW_SPELL"), 3)

            for locale, path in zip(LOCALES, paths):
                pools = parse_pools(path.read_text(encoding="utf-8"))
                key = ("localeData", locale, "texts", "NEW_SPELL")
                self.assertEqual(pools[key + ("ziel",)].entries, ["Neuer RP-Text"])
                self.assertEqual(pools[key + ("gruppe",)].entries, ["Neuer RP-Text"])
                self.assertEqual(list(path.parent.glob(path.name + ".*.bak"))[0].read_bytes(), originals[path])

    def test_successful_profile_creation_updates_lua_backups_and_registry(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            paths = []
            for locale in LOCALES:
                path = root / "HexerRP" / "locales" / locale / "Racial.lua"
                path.parent.mkdir(parents=True)
                path.write_text(lua_file(locale, "racial"), encoding="utf-8")
                paths.append(path)
            originals = {path: path.read_bytes() for path in paths}

            self.assertEqual(
                create_profile(root, "HexerRP", "race", "NightElf", "Nachtelf", "Naturverbunden", True),
                3,
            )

            for locale, path in zip(LOCALES, paths):
                pools = parse_pools(path.read_text(encoding="utf-8"))
                key = ("localeData", locale, "racial", "NightElf", "RP_GREETING")
                self.assertEqual(pools[key + ("ziel",)].entries, ["Neuer RP-Text"])
                self.assertEqual(pools[key + ("gruppe",)].entries, ["Neuer RP-Text"])
                self.assertEqual(list(path.parent.glob(path.name + ".*.bak"))[0].read_bytes(), originals[path])
            profile = load_registry(root)["races"]["NightElf"]
            self.assertEqual(profile, {
                "name": "Nachtelf",
                "style": "Naturverbunden",
                "addons": ["HexerRP"],
            })

if __name__=="__main__":
    unittest.main()
