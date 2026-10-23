"""Collection layout and legacy project compatibility, with no network access."""
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from project_paths import addons_root, manual_path, metadata_path, project_root
from race_class_manager import REGISTRY, load_registry, register
from spell_manager import FILENAME, load_mappings, save_mappings
from translation_links import FILE_NAME, pool_id, read_links, write_links
from workspace_structures import create_profile, create_spell


class ProjectPathTests(unittest.TestCase):
    def test_collection_and_selected_addons_share_root_and_metadata(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory).resolve()
            (root / "apps" / "RPTextStudio").mkdir(parents=True)
            (root / "addons").mkdir()
            for selected in (root, root / "addons"):
                self.assertEqual(project_root(selected), root)
                self.assertEqual(addons_root(selected), root / "addons")
                self.assertEqual(metadata_path(selected, FILE_NAME), root / "data" / FILE_NAME)
            self.assertFalse((root / "data").exists())

    def test_flat_zip_and_legacy_projects_keep_their_addon_root(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory).resolve()
            (root / "HexerRP").mkdir()
            self.assertEqual(project_root(root), root)
            self.assertEqual(addons_root(root), root)
            self.assertEqual(metadata_path(root, FILE_NAME), root / "data" / FILE_NAME)

    def test_legacy_registers_read_then_write_to_data_without_losing_originals(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory).resolve()
            legacy = {
                FILE_NAME: {"version": 1, "pools": {}},
                FILENAME: {"schema": 1, "mappings": []},
                REGISTRY: {"version": 1, "races": {}, "classes": {}},
            }
            for name, payload in legacy.items():
                (root / name).write_text(json.dumps(payload), encoding="utf-8")
            original = {name: (root / name).read_bytes() for name in legacy}
            self.assertEqual(read_links(root), {})
            self.assertEqual(load_mappings(root), [])
            self.assertEqual(load_registry(root)["races"], {})
            write_links(root, {})
            save_mappings(root, [])
            register(root, "race", "NightElf", "Night elf", "Nature")
            for name in legacy:
                self.assertTrue((root / "data" / name).is_file())
                self.assertEqual((root / name).read_bytes(), original[name])
            # The new canonical copy wins over the preserved legacy file.
            self.assertIn("NightElf", load_registry(root)["races"])

    def test_translation_identity_is_unchanged_by_addons_prefix(self):
        key = ("localeData", "deDE", "texts", "HELLO")
        self.assertEqual(
            pool_id("HexerRP/locales/deDE/Texts.lua", key),
            pool_id("addons/HexerRP/locales/deDE/Texts.lua", key),
        )

    def test_new_structures_use_nested_addons_and_back_up_all_locales(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory).resolve()
            for lang in ("deDE", "enUS", "frFR"):
                folder = root / "addons" / "HexerRP" / "locales" / lang
                folder.mkdir(parents=True)
                (folder / "Texts.lua").write_text(
                    f'addon.localeData.{lang}.texts = {{ OLD = {{ "Hello" }}, }}',
                    encoding="utf-8",
                )
                (folder / "Racial.lua").write_text(
                    f'addon.localeData.{lang}.racial = {{ Gnome = {{ OLD = {{ "Hello" }}, }}, }}',
                    encoding="utf-8",
                )
            self.assertEqual(create_spell(root, "HexerRP", 0, "", "", "NEW"), 3)
            self.assertEqual(
                create_profile(root, "HexerRP", "race", "NightElf", "Night elf", "", True),
                3,
            )
            self.assertEqual(len(list((root / "addons").rglob("*.bak"))), 6)
            self.assertTrue((root / "data" / REGISTRY).is_file())
            self.assertFalse((root / "HexerRP").exists())

    def test_manual_is_available(self):
        self.assertTrue(manual_path().is_file())

    def test_gui_opens_collection_addons_and_flat_zip_layout(self):
        from PySide6.QtWidgets import QApplication, QMessageBox
        from main import Studio

        app = QApplication.instance() or QApplication([])
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory).resolve()
            (root / "apps").mkdir()
            locale = root / "addons" / "HexerRP" / "locales" / "deDE"
            locale.mkdir(parents=True)
            (locale / "Texts.lua").write_text(
                'addon.localeData.deDE.texts = { HELLO = { "Hello" }, }',
                encoding="utf-8",
            )
            write_links(root, {})
            studio = Studio()
            try:
                with patch.object(QMessageBox, "warning") as warning:
                    for selected in (root, root / "addons"):
                        studio.load(selected)
                        self.assertEqual(studio.root, root)
                        self.assertEqual(len(studio.files), 1)
                        self.assertTrue(all(p.is_relative_to(root / "addons") for p in studio.files))
                    # An unpacked runtime ZIP has no apps directory.
                    (root / "apps").rmdir()
                    studio.load(root / "addons")
                    self.assertEqual(studio.root, root / "addons")
                    self.assertEqual(len(studio.files), 1)
                    warning.assert_not_called()
            finally:
                studio.close()
                app.processEvents()


if __name__ == "__main__":
    unittest.main()
