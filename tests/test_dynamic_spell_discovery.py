"""Discover macros from loaded addons without a hard-coded addon registry."""
import tempfile
import unittest
from pathlib import Path
from lua_text import parse_pools
from spell_manager import discover_commands, candidate_keys, make_macro

class DynamicSpellDiscoveryTest(unittest.TestCase):
    def test_new_addon_and_mage_discovered(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            files = {}
            for addon, slash, key in (("MagierRP", "/mrp", "FIREBALL"),
                                      ("PriesterRP", "/priest", "HEAL")):
                core = root / addon / "core"
                core.mkdir(parents=True)
                (core / "Commands.lua").write_text(
                    'SLASH_%s1 = "%s"\nSlashCmdList["%s"] = function(message) end\n'
                    % (addon.upper(), slash, addon.upper()), encoding="utf-8")
                locale = root / addon / "locales" / "deDE"
                locale.mkdir(parents=True)
                path = locale / "Texts.lua"
                files[path] = parse_pools(
                    'addon.localeData.deDE.texts = { %s = { ziel = { "Text", }, }, }' % key)
            commands = discover_commands(root, files)
            self.assertEqual(commands["MagierRP"], "/mrp")
            self.assertEqual(commands["PriesterRP"], "/priest")
            self.assertIn("FIREBALL", candidate_keys(files, "MagierRP"))
            self.assertIn("HEAL", candidate_keys(files, "PriesterRP"))
            self.assertEqual(make_macro("MagierRP", "Feuerball", "FIREBALL",
                candidate_keys(files, "MagierRP"), commands=commands),
                "#showtooltip Feuerball\n/cast Feuerball\n/mrp fireball")


    def test_dotted_slashcmdlist_handlers_are_discovered(self):
        # Existing JaegerRP, HexerRP and DruidenRP use dot notation.
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            files = {}
            for addon, slash, key in (
                ("JaegerRP", "/jrp", "RAPTOR_STRIKE"),
                ("HexerRP", "/wrp", "SHADOW_BOLT"),
                ("DruidenRP", "/drp", "MARK"),
            ):
                directory = root / addon / "core"
                directory.mkdir(parents=True)
                (directory / "Commands.lua").write_text(
                    f'SLASH_{addon.upper()}1 = "{slash}"\n'
                    f'SlashCmdList.{addon.upper()} = addon.HandleCommand\n',
                    encoding="utf-8",
                )
                locale = root / addon / "locales" / "deDE"
                locale.mkdir(parents=True)
                file = locale / "Texts.lua"
                files[file] = parse_pools(
                    "addon.localeData.deDE.texts = { "
                    + key + ' = { gruppe = { "RP-Text", }, }, }'
                )
            commands = discover_commands(root, files)
            self.assertEqual(commands, {
                "DruidenRP": "/drp", "HexerRP": "/wrp", "JaegerRP": "/jrp"
            })
            self.assertEqual(
                make_macro("JaegerRP", "Raptorstoß", "RAPTOR_STRIKE",
                           candidate_keys(files, "JaegerRP"), commands=commands),
                "#showtooltip Raptorstoß\n/cast Raptorstoß\n/jrp raptor_strike"
            )

    def test_dotted_handler_in_comments_or_literals_does_not_count(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            directory = root / "FakeRP" / "core"
            directory.mkdir(parents=True)
            (directory / "Commands.lua").write_text(
                'SLASH_FAKERP1 = "/fake"\n'
                '-- SlashCmdList.FAKERP = addon.HandleCommand\n'
                'local example = "SlashCmdList.FAKERP = handler"\n',
                encoding="utf-8",
            )
            locale = root / "FakeRP" / "locales" / "deDE"
            locale.mkdir(parents=True)
            path = locale / "Texts.lua"
            files = {path: parse_pools(
                'addon.localeData.deDE.texts = { TEST = { gruppe = {"Text",},},}'
            )}
            self.assertEqual(discover_commands(root, files), {})

    def test_no_unregistered_command(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            path = root / "TestRP" / "locales" / "deDE" / "Texts.lua"
            path.parent.mkdir(parents=True)
            files = {path: parse_pools('addon.localeData.deDE.texts = { TEST = { ziel = {"x",},},}') }
            self.assertEqual(discover_commands(root, files), {})
            with self.assertRaises(ValueError):
                make_macro("TestRP", "Test", "TEST", ["TEST"], commands={})

    def test_ignores_commented_out_handler_assignment(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            addon = root / "TestRP"
            (addon / "core").mkdir(parents=True)
            (addon / "core" / "Commands.lua").write_text(
                'SLASH_TESTRP1 = "/test"\n'
                '-- SlashCmdList["TESTRP"] = function(message) end\n',
                encoding="utf-8")
            locale = addon / "locales" / "deDE"
            locale.mkdir(parents=True)
            path = locale / "Texts.lua"
            files = {path: parse_pools(
                'addon.localeData.deDE.texts = { TEST = { ziel = {"x",},},}')}

            self.assertEqual(discover_commands(root, files), {})

if __name__ == "__main__":
    unittest.main()
