"""WoW target selection for RP Text Studio.

The dialog discovers installation candidates read-only and saves only a user-confirmed
target. The target is not used for deployment until the separate installer approves it.
"""
from __future__ import annotations

from pathlib import Path
from PySide6.QtCore import QObject, QThread, Signal, Slot, Qt
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QListWidget, QListWidgetItem,
    QLineEdit, QPushButton, QFileDialog, QMessageBox, QCheckBox,
)
from wow_detection import discover_wow_installations, inspect_client, _candidate_roots
from wow_installations import load_paths, save_paths


class ScanWorker(QObject):
    finished = Signal(list)
    failed = Signal(str)

    def __init__(self, saved: list[Path], deep_scan=False, drives=()):
        super().__init__()
        self.saved = saved
        self.deep_scan = deep_scan
        self.drives = drives
        self.stopped = False

    @Slot()
    def run(self):
        try:
            matches = discover_wow_installations(
                saved_paths=self.saved, deep_scan=self.deep_scan, drives=self.drives,
                cancelled=lambda: self.stopped,
            )
            self.finished.emit(matches)
        except (OSError, ValueError) as exc:
            self.failed.emit(str(exc))


class WoWDetectionDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("WoW-Installation suchen")
        self.resize(850, 530)
        self.selected_path: Path | None = None
        self.thread = None
        self.worker = None
        self.matches = []
        self._pending_completion = None
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("Erkannte WoW-Clients. Kein Installationsziel wird automatisch ausgewählt."))
        self.list = QListWidget()
        self.list.currentRowChanged.connect(self._selection_changed)
        layout.addWidget(self.list)
        row = QHBoxLayout()
        self.manual = QLineEdit()
        self.manual.setPlaceholderText(r"Manueller Clientordner oder ...\Interface\AddOns")
        self.manual.textChanged.connect(self._selection_changed)
        browse = QPushButton("Durchsuchen…")
        browse.clicked.connect(self._browse)
        row.addWidget(self.manual, 1)
        row.addWidget(browse)
        layout.addLayout(row)
        self.extended = QCheckBox("Erweiterte Suche auf lokalen Laufwerken (langsamer)")
        layout.addWidget(self.extended)
        buttons = QHBoxLayout()
        self.scan = QPushButton("Erneut suchen")
        self.scan.clicked.connect(self.start_scan)
        self.stop = QPushButton("Abbrechen")
        self.stop.clicked.connect(self.stop_scan)
        self.stop.setEnabled(False)
        self.select = QPushButton("Installationsziel übernehmen")
        self.select.setEnabled(False)
        self.select.clicked.connect(self._confirm)
        buttons.addWidget(self.scan)
        buttons.addWidget(self.stop)
        buttons.addWidget(self.select)
        layout.addLayout(buttons)
        self.start_scan()

    def _browse(self):
        directory = QFileDialog.getExistingDirectory(self, "WoW-Clientverzeichnis wählen")
        if directory:
            self.manual.setText(directory)

    def _selection_changed(self, *_):
        if self._pending_completion is not None:
            self.select.setEnabled(False)
            return
        self.select.setEnabled(bool(self.manual.text().strip()) or self.list.currentRow() >= 0)

    def start_scan(self):
        if self.thread is not None:
            return
        self.scan.setEnabled(False)
        self.stop.setEnabled(True)
        self.matches = []
        self.list.clear()
        self.list.addItem("Suche läuft …")
        self.list.item(0).setFlags(self.list.item(0).flags() & ~Qt.ItemFlag.ItemIsSelectable)
        self.select.setEnabled(bool(self.manual.text().strip()))
        import string
        drives = tuple(Path(f"{letter}:\\") for letter in string.ascii_uppercase) \
            if self.extended.isChecked() else ()
        self.thread = QThread(self)
        self.worker = ScanWorker(load_paths(), self.extended.isChecked(), drives)
        self.worker.moveToThread(self.thread)
        self.thread.started.connect(self.worker.run)
        self.worker.finished.connect(self._results)
        self.worker.failed.connect(self._error)
        self.worker.finished.connect(self.thread.quit)
        self.worker.failed.connect(self.thread.quit)
        self.thread.finished.connect(self._cleanup_thread)
        self.thread.start()

    def _results(self, matches):
        self.matches = matches
        self.list.clear()
        for match in matches:
            label = (f"{match.display_name}  [{match.client_type}, {match.confidence}]\n"
                     f"{match.addons_path}\nFund: {', '.join(match.sources)}")
            self.list.addItem(label)
        if not matches:
            self.list.addItem("Keine Installation erkannt. Pfad manuell auswählen.")
            self.list.item(0).setFlags(self.list.item(0).flags() & ~Qt.ItemFlag.ItemIsSelectable)
        self.select.setEnabled(
            self._pending_completion is None and bool(self.manual.text().strip())
        )
        self.scan.setEnabled(self._pending_completion is None)
        self.stop.setEnabled(False)

    def _error(self, message):
        self.list.clear()
        self.list.addItem("Suche fehlgeschlagen: " + message)
        self.scan.setEnabled(self._pending_completion is None)
        self.stop.setEnabled(False)

    def _cleanup_thread(self):
        if self.worker:
            self.worker.deleteLater()
        if self.thread:
            self.thread.deleteLater()
        self.thread = None
        self.worker = None
        pending = self._pending_completion
        self._pending_completion = None
        if pending is not None:
            (QDialog.accept if pending else QDialog.reject)(self)

    def stop_scan(self):
        if self.worker:
            self.worker.stopped = True
        self.stop.setEnabled(False)

    def _confirm(self):
        if self.manual.text().strip():
            roots = _candidate_roots(Path(self.manual.text().strip()))
            matching = [item for root in roots if (item := inspect_client(root, "manuell"))]
            if not matching:
                QMessageBox.warning(self, "Nicht erkannt",
                    "Der manuelle Pfad enthält keine ausreichend plausiblen WoW-Clientmerkmale.")
                return
            if len(matching) > 1:
                QMessageBox.warning(self, "Mehrere Clients erkannt",
                    "Der ausgewählte Ordner enthält mehrere WoW-Clients. "
                    "Bitte wähle das konkrete Clientverzeichnis aus.")
                return
            chosen = matching[0]
        else:
            index = self.list.currentRow()
            if not 0 <= index < len(self.matches):
                return
            chosen = self.matches[index]
        if not chosen.verified:
            if QMessageBox.question(self, "Installation bestätigen",
                f"Die Installation ist nicht eindeutig erkannt:\n{chosen.client_root}\n"
                "Diesen Pfad trotzdem als WoW-Ziel speichern?") != QMessageBox.Yes:
                return
        try:
            paths = load_paths()
            save_paths([*paths, chosen.client_root])
        except (OSError, ValueError) as exc:
            QMessageBox.critical(self, "Speichern fehlgeschlagen", str(exc))
            return
        self.selected_path = chosen.addons_path
        self.accept()

    def _complete(self, accepted):
        if self._pending_completion is not None:
            return
        if self.thread is not None and self.thread.isRunning():
            self._pending_completion = accepted
            self.stop_scan()
            self.scan.setEnabled(False)
            self.select.setEnabled(False)
            self.list.setEnabled(False)
            self.manual.setEnabled(False)
            self.extended.setEnabled(False)
            return
        (QDialog.accept if accepted else QDialog.reject)(self)

    def accept(self):
        self._complete(True)

    def reject(self):
        self._complete(False)

    def closeEvent(self, event):
        if self.thread is not None and self.thread.isRunning():
            self.reject()
            event.ignore()
            return
        super().closeEvent(event)
