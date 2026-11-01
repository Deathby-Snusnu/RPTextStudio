"""Regression checks for user-visible Qt dialogs, without starting a GUI."""

import ast
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MESSAGE_BOX_METHODS = {"about", "critical", "information", "question", "warning"}
TEXT_SETTER_METHODS = {
    "setDetailedText", "setInformativeText", "setText",
    "setToolTip", "setWindowTitle",
}
TEXT_WIDGETS = {"QCheckBox", "QLabel", "QPushButton"}


def _literal_fragments(expression):
    """Return static strings even when a dialog message contains f-strings."""
    return [
        node.value
        for node in ast.walk(expression)
        if isinstance(node, ast.Constant) and isinstance(node.value, str)
    ]


def _message_expression(call):
    """Find the user-facing text argument of common Qt dialog operations."""
    function = call.func
    if isinstance(function, ast.Attribute):
        if (isinstance(function.value, ast.Name)
                and function.value.id == "QMessageBox"
                and function.attr in MESSAGE_BOX_METHODS):
            return call.args[2] if len(call.args) >= 3 else None
        if function.attr in TEXT_SETTER_METHODS:
            return call.args[0] if call.args else None
    if isinstance(function, ast.Name) and function.id in TEXT_WIDGETS:
        return call.args[0] if call.args else None
    return None


def _message_box_call(path, method, title):
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    matches = [
        node for node in ast.walk(tree)
        if isinstance(node, ast.Call)
        and isinstance(node.func, ast.Attribute)
        and isinstance(node.func.value, ast.Name)
        and node.func.value.id == "QMessageBox"
        and node.func.attr == method
        and len(node.args) >= 3
        and isinstance(node.args[1], ast.Constant)
        and node.args[1].value == title
    ]
    if len(matches) != 1:
        raise AssertionError(f"Expected one {method} dialog titled {title!r}, found {len(matches)}")
    return matches[0]


class DialogEscapeSequenceTests(unittest.TestCase):
    def test_visible_gui_messages_do_not_contain_literal_control_sequences(self):
        """Literal backslash-n/r/t is not a line break or a tab in Qt."""
        escaped = (r"\n", r"\r", r"\t")
        for path in sorted(ROOT.glob("*.py")):
            tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
            for call in ast.walk(tree):
                if not isinstance(call, ast.Call):
                    continue
                message = _message_expression(call)
                if message is None:
                    continue
                for fragment in _literal_fragments(message):
                    for sequence in escaped:
                        with self.subTest(file=path.name, line=call.lineno, sequence=sequence):
                            self.assertNotIn(
                                sequence, fragment,
                                f"{path.name}:{call.lineno}: UI message contains {sequence!r} "
                                "instead of a control character",
                            )

    def test_download_confirmation_contains_a_real_blank_line(self):
        call = _message_box_call(
            ROOT / "user_addon_manager_gui.py", "question", "Downloads vorbereiten"
        )
        self.assertIn("\n\n", "".join(_literal_fragments(call.args[2])))

    def test_translation_errors_are_joined_with_real_newlines(self):
        call = _message_box_call(ROOT / "main.py", "warning", "Ungültige Übersetzung")
        message = call.args[2]
        self.assertIsInstance(message, ast.Call)
        self.assertIsInstance(message.func, ast.Attribute)
        self.assertEqual(message.func.attr, "join")
        self.assertIsInstance(message.func.value, ast.Constant)
        self.assertEqual(message.func.value.value, "\n")


if __name__ == "__main__":
    unittest.main()
