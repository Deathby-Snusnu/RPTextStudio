"""PySide6 interface for reviewed local AddOn deployments."""
from __future__ import annotations
from pathlib import Path
from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QLineEdit, QFileDialog, QCheckBox, QPlainTextEdit, QMessageBox)
from addon_manager import ADDONS, InstallError, install, preview, rollback
from project_paths import addons_root


class AddonManagerDialog(QDialog):
    def __init__(self, project: Path, parent=None):
        super().__init__(parent)
        self.project = Path(project)
        self.plan = None
        self.setWindowTitle("RP Text Studio · AddOn-Installer")
        self.resize(830, 600)
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("Lokale Entwicklungsversionen installieren oder aktualisieren"))
        row = QHBoxLayout()
        self.target = QLineEdit()
        self.target.setPlaceholderText(r"C:\Games\World of Warcraft\_classic_era_\Interface\AddOns")
        browse = QPushButton("Durchsuchen…")
        browse.clicked.connect(self.browse)
        row.addWidget(self.target, 1)
        row.addWidget(browse)
        detect = QPushButton('WoW suchen…')
        detect.clicked.connect(self.detect_wow)
        row.addWidget(detect)
        layout.addLayout(row)
        layout.addWidget(QLabel("Ziel: ausschließlich Interface\\AddOns, niemals das Entwicklungsprojekt."))
        self.checkboxes = []
        for name in ADDONS:
            checkbox = QCheckBox(name)
            checkbox.setChecked(True)
            checkbox.stateChanged.connect(self.invalidate)
            self.checkboxes.append(checkbox)
            layout.addWidget(checkbox)
        self.target.textChanged.connect(self.invalidate)
        self.output = QPlainTextEdit()
        self.output.setReadOnly(True)
        layout.addWidget(self.output, 1)
        buttons = QHBoxLayout()
        self.scan_button = QPushButton("Vorschau erstellen")
        self.scan_button.clicked.connect(self.scan)
        self.apply_button = QPushButton("Auswahl installieren / aktualisieren")
        self.apply_button.setEnabled(False)
        self.apply_button.clicked.connect(self.apply)
        self.rollback_button = QPushButton("Backup wiederherstellen…")
        self.rollback_button.clicked.connect(self.restore)
        buttons.addWidget(self.scan_button)
        buttons.addWidget(self.apply_button)
        buttons.addWidget(self.rollback_button)
        layout.addLayout(buttons)
        self.last_backup = None

    def invalidate(self, *_):
        self.plan = None
        self.apply_button.setEnabled(False)

    def selected(self):
        return tuple(c.text() for c in self.checkboxes if c.isChecked())

    def detect_wow(self):
        from wow_detection_dialog import WoWDetectionDialog
        chooser = WoWDetectionDialog(self)
        if chooser.exec() and chooser.selected_path:
            self.target.setText(str(chooser.selected_path))

    def browse(self):
        folder = QFileDialog.getExistingDirectory(self, "WoW AddOns-Verzeichnis wählen")
        if folder:
            self.target.setText(folder)

    def scan(self):
        try:
            self.plan = preview(addons_root(self.project), Path(self.target.text()),
                                self.selected())
            lines = []
            for c in self.plan:
                lines.append(f"{c.name}: +{len(c.added)} neu, ~{len(c.changed)} geändert, -{len(c.removed)} entfernt")
                lines.extend("  + " + p for p in c.added)
                lines.extend("  ~ " + p for p in c.changed)
                lines.extend("  - " + p for p in c.removed)
            self.output.setPlainText("\n".join(lines) or "Keine AddOns gewählt.")
            self.apply_button.setEnabled(any(c.is_changed for c in self.plan))
        except (InstallError, OSError, ValueError) as exc:
            self.invalidate()
            QMessageBox.warning(self, "Vorschau fehlgeschlagen", str(exc))

    def apply(self):
        if not self.plan:
            return
        response = QMessageBox.question(self, "Installation bestätigen",
            "Die angezeigten AddOns werden vollständig ersetzt. Bestehende Ordner werden "
            "unter .addon-backups gesichert. Aus der Vorschau entfernte Dateien "
            "werden in der neuen Installation nicht übernommen. Fortfahren?")
        if response != QMessageBox.Yes:
            return
        try:
            backup = install(addons_root(self.project), Path(self.target.text()),
                             self.selected(), approved=self.plan)
            self.last_backup = backup
            QMessageBox.information(self, "Installation abgeschlossen",
                                    f"Backup: {backup}")
        except (InstallError, OSError, ValueError) as exc:
            QMessageBox.critical(self, "Installation fehlgeschlagen", str(exc))
        self.invalidate()

    def restore(self):
        folder = QFileDialog.getExistingDirectory(self, "Backup aus .addon-backups auswählen")
        if not folder:
            return
        if QMessageBox.question(self, "Wiederherstellen",
              "Die gesicherten AddOns wiederherstellen? Aktuelle Versionen bleiben separat erhalten.") != QMessageBox.Yes:
            return
        try:
            rollback(Path(self.target.text()), Path(folder))
            QMessageBox.information(self, "Wiederherstellung", "Backup wurde wiederhergestellt.")
        except (InstallError, OSError, ValueError, KeyError) as exc:
            QMessageBox.critical(self, "Wiederherstellung fehlgeschlagen", str(exc))
        self.invalidate()
