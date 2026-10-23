"""Read-only GitHub update status dialog, with background network worker."""
from __future__ import annotations

from pathlib import Path
from PySide6.QtCore import QObject, QThread, Signal, Slot
from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel,
    QTableWidget, QTableWidgetItem, QPushButton, QComboBox, QMessageBox)
from addon_manager import ADDONS
from github_updates import check_all


class UpdateWorker(QObject):
    completed = Signal(object)
    failed = Signal(str)

    def __init__(self, target: Path, names: tuple[str, ...], channel: str):
        super().__init__()
        self.target = target
        self.names = names
        self.channel = channel

    @Slot()
    def run(self):
        try:
            self.completed.emit(check_all(self.target, self.names, self.channel))
        except (OSError, ValueError, RuntimeError) as exc:
            self.failed.emit(str(exc))


class GitHubUpdateDialog(QDialog):
    def __init__(self, target: Path, names: tuple[str, ...] = ADDONS, parent=None):
        super().__init__(parent)
        self.target = Path(target)
        self.names = names
        self.thread = None
        self.worker = None
        self.setWindowTitle("GitHub-Update-Prüfung (nur lesen)")
        self.resize(950, 460)
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("Versionsvergleich aus den sechs privaten GitHub-Repositories. "
                                "Es werden keine Dateien heruntergeladen oder installiert."))
        row = QHBoxLayout()
        row.addWidget(QLabel("Update-Kanal:"))
        self.channel = QComboBox()
        self.channel.addItem("Stabile Releases", "stable")
        self.channel.addItem("Entwicklungsstand (main)", "development")
        row.addWidget(self.channel)
        self.refresh = QPushButton("Jetzt prüfen")
        self.refresh.clicked.connect(self.start)
        row.addWidget(self.refresh)
        row.addStretch(1)
        layout.addLayout(row)
        self.table = QTableWidget(0, 5)
        self.table.setHorizontalHeaderLabels(("AddOn", "Installiert", "GitHub", "Ergebnis", "Hinweis"))
        self.table.horizontalHeader().setStretchLastSection(True)
        layout.addWidget(self.table)
        self.status = QLabel("Bereit. Für private GitHub-Repositories: 'gh auth login' ausführen.")
        layout.addWidget(self.status)

    def start(self):
        if self.thread is not None:
            return
        self.refresh.setEnabled(False)
        self.channel.setEnabled(False)
        self.status.setText("GitHub-Versionen werden geprüft …")
        self.thread = QThread(self)
        self.worker = UpdateWorker(self.target, self.names, self.channel.currentData())
        self.worker.moveToThread(self.thread)
        self.thread.started.connect(self.worker.run)
        self.worker.completed.connect(self.populate)
        self.worker.failed.connect(self.show_error)
        self.worker.completed.connect(self.thread.quit)
        self.worker.failed.connect(self.thread.quit)
        self.thread.finished.connect(self.cleanup)
        self.thread.start()

    def populate(self, records):
        self.table.setRowCount(len(records))
        for i, record in enumerate(records):
            for j, value in enumerate((record.name, record.installed or "—",
                                      record.available or "—", record.status, record.detail)):
                self.table.setItem(i, j, QTableWidgetItem(str(value)))
        self.status.setText("Prüfung beendet. Versionsstand ist keine Installationsfreigabe.")
        self.refresh.setEnabled(True)
        self.channel.setEnabled(True)

    def show_error(self, message):
        self.status.setText("Prüfung fehlgeschlagen.")
        QMessageBox.warning(self, "GitHub-Update-Prüfung", message)
        self.refresh.setEnabled(True)
        self.channel.setEnabled(True)

    def cleanup(self):
        if self.worker:
            self.worker.deleteLater()
        if self.thread:
            self.thread.deleteLater()
        self.thread = None
        self.worker = None

    def reject(self):
        if self.thread is not None and self.thread.isRunning():
            self.status.setText("Prüfung läuft. Bitte das Ende der Abfrage abwarten.")
            return
        super().reject()
