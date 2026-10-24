"""User mode: read-only WoW addon overview with background discovery and GitHub checks."""
from __future__ import annotations
from pathlib import Path
from uuid import uuid4
from PySide6.QtCore import QObject, QThread, Signal, Slot
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QComboBox, QPushButton,
    QTableWidget, QTableWidgetItem, QMessageBox, QFileDialog,
)
from addon_manager import ADDONS
from wow_installations import load_paths
from wow_detection import discover_wow_installations, inspect_client
from user_addon_manager import inspect_installed, check_installed
from github_staging import stage


class UserScanWorker(QObject):
    done = Signal(object)
    failed = Signal(str)

    def __init__(self, operation: str, target: Path | None = None, channel: str = "stable",
                 name: str | None = None, staging_target: Path | None = None):
        super().__init__()
        self.operation = operation
        self.target = target
        self.channel = channel
        self.name = name
        self.staging_target = staging_target

    @Slot()
    def run(self):
        try:
            if self.operation == "discover":
                result = discover_wow_installations(saved_paths=load_paths())
            elif self.operation == "local":
                result = inspect_installed(self.target)
            elif self.operation == "github":
                result = check_installed(self.target, channel=self.channel)
            elif self.operation == "stage":
                result = stage(self.name, self.channel, self.staging_target)
            else:
                raise ValueError("Unbekannte Operation.")
            self.done.emit(result)
        except Exception as exc:
            self.failed.emit(str(exc))


class UserAddonManagerDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("RP Text Studio · AddOn-Verwaltung (Anwender)")
        self.resize(940, 540)
        self.thread = None
        self.worker = None
        self.candidates = []
        self.installed = {}
        self._scan_after_cleanup = False
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("Anwender-Modus: Nur lesen. Keine Dateien werden installiert oder verändert."))
        top = QHBoxLayout()
        self.installations = QComboBox()
        self.installations.currentIndexChanged.connect(self.select_installation)
        self.find_button = QPushButton("WoW suchen")
        self.find_button.clicked.connect(lambda: self._start("discover"))
        top.addWidget(QLabel("WoW:"))
        top.addWidget(self.installations, 1)
        top.addWidget(self.find_button)
        layout.addLayout(top)

        self.table = QTableWidget(0, 5)
        self.table.setHorizontalHeaderLabels(("AddOn", "Installiert", "Interface", "GitHub", "Status"))
        self.table.horizontalHeader().setStretchLastSection(True)
        layout.addWidget(self.table)

        actions = QHBoxLayout()
        self.channel = QComboBox()
        self.channel.addItem("Stabile Releases", "stable")
        self.channel.addItem("Entwicklungsstand", "development")
        self.check_button = QPushButton("GitHub-Versionen prüfen")
        self.check_button.clicked.connect(lambda: self._start("github"))
        self.check_button.setEnabled(False)
        self.stage_button = QPushButton("Paket prüfen und bereitstellen…")
        self.stage_button.clicked.connect(self.stage_selected)
        self.stage_button.setEnabled(False)
        self.table.currentCellChanged.connect(lambda *_: self._set_busy(self.thread is not None))
        actions.addWidget(self.channel)
        actions.addWidget(self.check_button)
        actions.addWidget(self.stage_button)
        actions.addStretch(1)
        layout.addLayout(actions)
        self.status = QLabel("Suche nach vorhandenen WoW-Installationen …")
        layout.addWidget(self.status)
        self._start("discover")

    def _set_busy(self, busy):
        self.find_button.setEnabled(not busy)
        self.installations.setEnabled(not busy)
        self.channel.setEnabled(not busy)
        self.check_button.setEnabled(not busy and self.current_target() is not None)
        self.stage_button.setEnabled(not busy and self.current_target() is not None and
                                     0 <= self.table.currentRow() < self.table.rowCount())

    def current_target(self):
        index = self.installations.currentIndex()
        return self.candidates[index].addons_path if 0 <= index < len(self.candidates) else None

    def stage_selected(self):
        if self.thread is not None:
            return
        row = self.table.currentRow()
        if not 0 <= row < self.table.rowCount():
            return
        name = self.table.item(row, 0).text()
        channel = self.channel.currentData()
        directory = QFileDialog.getExistingDirectory(self, "Lokalen Staging-Elternordner auswählen")
        if not directory:
            return
        destination = Path(directory) / (name + "-" + channel + "-" + uuid4().hex[:10])
        if QMessageBox.question(self, "GitHub-Paket vorbereiten",
            f"{name} aus dem GitHub-Kanal {channel} ausschließlich in diesen Ordner herunterladen "
            f"und prüfen?\n\n{destination}\n\nDeine WoW-AddOns bleiben unverändert.") != QMessageBox.Yes:
            return
        self._start("stage", name=name, staging_target=destination)

    def _start(self, operation, *, name=None, staging_target=None):
        if self.thread is not None:
            return
        target = self.current_target()
        if operation != "discover" and target is None:
            return
        self._set_busy(True)
        self.status.setText("Prüfung läuft …")
        self.thread = QThread(self)
        self.worker = UserScanWorker(operation, target, self.channel.currentData(), name,
                                     staging_target)
        self.worker.moveToThread(self.thread)
        self.thread.started.connect(self.worker.run)
        self.worker.done.connect(lambda result, op=operation: self._done(op, result))
        self.worker.failed.connect(self._failed)
        self.worker.done.connect(self.thread.quit)
        self.worker.failed.connect(self.thread.quit)
        self.thread.finished.connect(self.worker.deleteLater)
        self.thread.finished.connect(self._cleanup)
        self.thread.start()

    def _done(self, operation, results):
        if operation == "discover":
            self.candidates = [x for x in results if x.verified]
            self.installed.clear()
            self.table.setRowCount(0)
            self.installations.blockSignals(True)
            self.installations.clear()
            for found in self.candidates:
                self.installations.addItem(f"{found.display_name} · {found.client_root}")
            self.installations.blockSignals(False)
            if self.candidates:
                self.status.setText(f"{len(self.candidates)} WoW-Installation(en) erkannt.")
            else:
                self.status.setText("Keine bestätigte Installation gefunden. Über 'WoW-Installation suchen…' einen Pfad speichern.")
        elif operation == "local":
            self.installed = {x.name: x for x in results}
            self.table.setRowCount(len(results))
            for i, entry in enumerate(results):
                for j, value in enumerate((entry.name, entry.version or "—", entry.interface or "—",
                                          "Noch nicht geprüft", entry.state)):
                    self.table.setItem(i, j, QTableWidgetItem(value))
            self.status.setText("Lokale RP-AddOns eingelesen. Keine Änderungen vorgenommen.")
        elif operation == "stage":
            self.status.setText(f"Paket vorbereitet: {results.directory}")
            QMessageBox.information(self, "Paket geprüft und bereitgestellt",
                f"{results.name} {results.version} wurde ohne Installation vorbereitet.\n"
                f"Commit: {results.commit}\nSHA-256 (Archiv): {results.archive_sha256}\n"
                f"Dateien: {results.files}\nZiel: {results.directory}")
        else:
            for i, row in enumerate(results):
                if i < self.table.rowCount():
                    self.table.setItem(i, 3, QTableWidgetItem(row.available or "—"))
                    self.table.setItem(i, 4, QTableWidgetItem(row.status + ": " + row.detail))
            self.status.setText("GitHub-Versionsvergleich abgeschlossen. Keine Installation möglich.")
        if operation == "discover" and self.candidates:
            self._scan_after_cleanup = True

    def _failed(self, message):
        self.status.setText("Prüfung fehlgeschlagen: " + message)

    def _cleanup(self):
        if self.thread:
            self.thread.deleteLater()
        self.thread = None
        self.worker = None
        self._set_busy(False)
        if self._scan_after_cleanup:
            self._scan_after_cleanup = False
            self.select_installation()

    def select_installation(self, *_):
        if self.thread is not None:
            return
        self.table.setRowCount(0)
        if self.current_target() is not None:
            self._start("local")

    def reject(self):
        if self.thread is not None and self.thread.isRunning():
            self.status.setText("Laufende Suche wird abgeschlossen. Danach kann das Fenster geschlossen werden.")
            return
        super().reject()
