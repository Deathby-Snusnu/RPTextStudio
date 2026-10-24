"""Review-first PySide6 wizard for generating MagierRP."""
from __future__ import annotations
from PySide6.QtWidgets import (QDialog, QVBoxLayout, QFormLayout, QLabel, QLineEdit,
    QSpinBox, QPlainTextEdit, QPushButton, QDialogButtonBox, QMessageBox)
from addon_project_generator import AddonProjectSpec, preview_project, generate_project


class AddonProjectWizard(QDialog):
    def __init__(self, project_root, parent=None):
        super().__init__(parent)
        self.project_root = project_root
        self.approved = None
        self.setWindowTitle("Neues Klassen-AddOn erstellen")
        self.resize(750, 520)
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("MagierRP · MAGE · deDE / enUS / frFR"))
        form = QFormLayout()
        self.name = QLineEdit("MagierRP")
        self.name.setReadOnly(True)
        self.title = QLineEdit("Magier RP")
        self.version = QLineEdit("0.1.0")
        self.interface = QSpinBox()
        self.interface.setRange(10000, 999999)
        self.interface.setValue(16001)
        for label, widget in (("AddOn-ID", self.name), ("Anzeigename", self.title),
                              ("Version", self.version), ("Interface", self.interface)):
            form.addRow(label, widget)
        layout.addLayout(form)
        self.output = QPlainTextEdit()
        self.output.setReadOnly(True)
        layout.addWidget(self.output)
        self.preview_button = QPushButton("Vorschau erstellen")
        self.preview_button.clicked.connect(self.preview)
        layout.addWidget(self.preview_button)
        actions = QDialogButtonBox(QDialogButtonBox.Cancel | QDialogButtonBox.Ok)
        self.commit_button = actions.button(QDialogButtonBox.Ok)
        self.commit_button.setText("AddOn erstellen")
        self.commit_button.setEnabled(False)
        actions.accepted.connect(self.create)
        actions.rejected.connect(self.reject)
        layout.addWidget(actions)
        for widget in (self.title, self.version):
            widget.textChanged.connect(self.invalidate)
        self.interface.valueChanged.connect(self.invalidate)

    def spec(self):
        return AddonProjectSpec(title=self.title.text(), version=self.version.text(),
                                interface=self.interface.value())

    def invalidate(self, *_):
        self.approved = None
        self.commit_button.setEnabled(False)

    def preview(self):
        try:
            self.approved = preview_project(self.project_root, self.spec())
            self.output.setPlainText(
                str(self.approved.addon_path) + "\n\nDateien:\n" +
                "\n".join(self.approved.files_to_create) +
                "\n\nRegistrierung:\n" + "\n".join(self.approved.registry_changes) +
                "\n\nHinweise:\n" + "\n".join(self.approved.warnings)
            )
            self.commit_button.setEnabled(True)
        except (OSError, ValueError) as exc:
            self.invalidate()
            QMessageBox.warning(self, "Vorschau fehlgeschlagen", str(exc))

    def create(self):
        if self.approved is None:
            return
        if QMessageBox.question(self, "MagierRP erstellen",
            "Das neue AddOn und sein Registereintrag werden lokal angelegt. Fortfahren?") != QMessageBox.Yes:
            return
        try:
            path = generate_project(self.project_root, self.spec(), self.approved)
        except (OSError, ValueError) as exc:
            QMessageBox.critical(self, "Erstellung fehlgeschlagen", str(exc))
            return
        QMessageBox.information(self, "MagierRP angelegt", str(path))
        self.accept()
