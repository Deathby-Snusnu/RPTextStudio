"""User mode: read-only WoW addon overview with background discovery and GitHub checks."""
from __future__ import annotations
from pathlib import Path
from uuid import uuid4
from PySide6.QtCore import QObject, QThread, Signal, Slot
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QComboBox, QPushButton,
    QTableWidget, QTableWidgetItem, QMessageBox, QFileDialog, QInputDialog,
)
from addon_manager import ADDONS
from wow_installations import load_paths
from wow_detection import discover_wow_installations, inspect_client
from user_addon_manager import inspect_installed, check_installed
from github_staging import stage
from safe_github_install import preview_safe_install, install_safe
from addon_manager import rollback
from wow_client_profiles import get_profile, save_profile, compatibility, interface_line, preview_toc


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
            elif self.operation == "install":
                plan, profile = self.staging_target
                result = install_safe(plan, profile)
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
        self.staged_packages = {}
        self._scan_after_cleanup = False
        self._operation = None
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("Anwender-Modus: GitHub-Pakete prüfen und nach Bestätigung mit Bestandsschutz installieren."))
        top = QHBoxLayout()
        self.installations = QComboBox()
        self.installations.currentIndexChanged.connect(self.select_installation)
        self.find_button = QPushButton("WoW suchen")
        self.find_button.clicked.connect(lambda: self._start("discover"))
        top.addWidget(QLabel("WoW:"))
        top.addWidget(self.installations, 1)
        top.addWidget(self.find_button)
        self.profile_button = QPushButton("Interface-Profil…")
        self.profile_button.clicked.connect(self.edit_client_profile)
        top.addWidget(self.profile_button)
        self.toc_button = QPushButton("TOC-Vorschau…")
        self.toc_button.clicked.connect(self.preview_selected_toc)
        top.addWidget(self.toc_button)
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
        self.install_button = QPushButton("Geprüftes Paket installieren…")
        self.install_button.clicked.connect(self.install_selected)
        self.install_button.setEnabled(False)
        actions.addWidget(self.install_button)
        actions.addStretch(1)
        layout.addLayout(actions)
        self.status = QLabel("Suche nach vorhandenen WoW-Installationen …")
        layout.addWidget(self.status)
        self._start("discover")

    def _set_busy(self, busy):
        self.find_button.setEnabled(not busy)
        self.profile_button.setEnabled(not busy and self.current_target() is not None)
        self.toc_button.setEnabled(not busy and self.current_target() is not None and
                                   0 <= self.table.currentRow() < self.table.rowCount())
        self.installations.setEnabled(not busy)
        self.channel.setEnabled(not busy)
        self.check_button.setEnabled(not busy and self.current_target() is not None)
        self.stage_button.setEnabled(not busy and self.current_target() is not None and
                                     0 <= self.table.currentRow() < self.table.rowCount())
        self.install_button.setEnabled(not busy and self.current_target() is not None and
                                        self.selected_staged() is not None)

    def current_target(self):
        index = self.installations.currentIndex()
        return self.candidates[index].addons_path if 0 <= index < len(self.candidates) else None

    def edit_client_profile(self):
        target = self.current_target()
        if target is None or self.thread is not None:
            return
        installation = self.candidates[self.installations.currentIndex()]
        current = get_profile(installation.client_root)
        value, accepted = QInputDialog.getText(self, 'WoW-Interface-Profil',
            'Interface-Nummer aus dem Spiel (/dump select(4, GetBuildInfo())):',
            text=current.interface if current else '')
        if not accepted:
            return
        try:
            profile = save_profile(installation.client_root, value)
        except (ValueError, OSError) as exc:
            QMessageBox.warning(self, 'Profil nicht gespeichert', str(exc))
            return
        info = compatibility('JaegerRP', profile)
        self.status.setText(f'Interface-Profil gespeichert: {profile.interface} ({profile.client_type}). {info}. Keine TOC verändert.')

    def preview_selected_toc(self):
        root = self.current_target()
        row = self.table.currentRow()
        if root is None or self.thread is not None or row < 0:
            return
        name = self.table.item(row, 0).text()
        profile = get_profile(self.candidates[self.installations.currentIndex()].client_root)
        if profile is None:
            QMessageBox.information(self, 'TOC-Vorschau', 'Bitte zuerst das Interface-Profil speichern.')
            return
        toc_path = root / name / (name + '.toc')
        try:
            from wow_detection import _linked
            if _linked(toc_path) or _linked(toc_path.parent):
                raise ValueError('Verknüpfte AddOn-Dateien werden nicht gelesen.')
            original = toc_path.read_text(encoding='utf-8-sig')
            # Explicit approval here produces a string for display only, never a file write.
            updated = preview_toc(original, profile.interface, compatible=True)
        except (OSError, UnicodeError, ValueError) as exc:
            QMessageBox.warning(self, 'TOC-Vorschau', str(exc))
            return
        old_line = interface_line(original) or '?'
        new_line = interface_line(updated) or '?'
        QMessageBox.information(self, 'TOC-Vorschau, keine Installation',
            f'{name}\nAktuell: {old_line}\nVorgeschlagen: {new_line}\n\n'
            f'Kompatibilität: {compatibility(name, profile)}\n\n'
            'Dies ist nur eine Zeichenfolgen-Vorschau. Keine Datei wurde verändert. '
            'Ohne bestätigte Kompatibilität darf kein automatisches Update erfolgen.')

    def selected_staged(self):
        row = self.table.currentRow()
        if not 0 <= row < self.table.rowCount():
            return None
        item = self.table.item(row, 0)
        return self.staged_packages.get(item.text()) if item else None

    def install_selected(self):
        package = self.selected_staged()
        target = self.current_target()
        if self.thread is not None or package is None or target is None:
            return
        profile = get_profile(self.candidates[self.installations.currentIndex()].client_root)
        if profile is None:
            QMessageBox.warning(self, "Interface-Profil fehlt",
                "Bitte zuerst das Interface-Profil der WoW-Installation speichern.")
            return
        warning = compatibility(package.name, profile)
        try:
            plan = preview_safe_install(package.name, package.directory, target, profile)
        except Exception as exc:
            QMessageBox.warning(self, "Installation nicht möglich", str(exc))
            return
        if not plan.new_files and not plan.toc_changed:
            details = (
                f"Für {package.name} gibt es derzeit keine gefahrlos anwendbaren Änderungen.\n\n"
                f"Neue Dateien: 0\n"
                f"TOC-Interface bereits passend: {profile.interface}\n"
                f"Abweichende vorhandene Dateien (geschützt): {len(plan.protected)}\n\n"
                "Bereits vorhandene Programm- und Textdateien werden aus Sicherheitsgründen "
                "nicht automatisch überschrieben. Eine neue GitHub-Version kann deshalb "
                "vorliegen, obwohl hier kein sicheres Update möglich ist."
            )
            QMessageBox.information(self, "Keine Änderungen notwendig", details)
            self.status.setText(f"{package.name}: keine sicheren Änderungen; vorhandene Dateien geschützt.")
            return
        summary = (
            f"AddOn: {package.name}\n"
            f"Ziel: {target / package.name}\n"
            f"Interface-Profil: {profile.interface}\n\n"
            "Geplante Änderungen\n"
            f"  • Neue Dateien: {len(plan.new_files)}\n"
            f"  • Geschützte abweichende Dateien: {len(plan.protected)}\n"
            f"  • Interface-Zeile der TOC anpassen: {'Ja' if plan.toc_changed else 'Nein'}\n\n"
            "Bestandsschutz\n"
            "  • Bestehende RP-Texte und sonstige Dateien bleiben erhalten.\n"
            "  • Nur die Interface-Zeile der TOC darf angepasst werden.\n"
            "  • Der bisherige AddOn-Ordner wird vorab gesichert.\n\n"
            f"Kompatibilität: {warning}\n"
            "Eine passende Interface-Nummer garantiert keine WoW-API-Kompatibilität.\n"
            "Bitte nur fortfahren, wenn du die Installation mit diesem Client testen möchtest."
        )
        dialog = QMessageBox(self)
        dialog.setWindowTitle("AddOn-Installation prüfen")
        dialog.setIcon(QMessageBox.Warning)
        dialog.setText(f"Installation von {package.name} bestätigen?")
        dialog.setInformativeText(summary)
        dialog.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        dialog.setDefaultButton(QMessageBox.No)
        dialog.button(QMessageBox.Yes).setText("Installieren")
        dialog.button(QMessageBox.No).setText("Abbrechen")
        dialog.setMinimumWidth(630)
        if dialog.exec() != QMessageBox.Yes:
            return
        self._start("install", staging_target=(plan, profile))

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
        self._operation = operation
        self.thread = QThread(self)
        self.worker = UserScanWorker(operation, target, self.channel.currentData(), name,
                                     staging_target)
        self.worker.moveToThread(self.thread)
        self.thread.started.connect(self.worker.run)
        self.worker.done.connect(self._on_done)
        self.worker.failed.connect(self._failed)
        self.worker.done.connect(self.thread.quit)
        self.worker.failed.connect(self.thread.quit)
        self.thread.finished.connect(self.worker.deleteLater)
        self.thread.finished.connect(self._cleanup)
        self.thread.start()

    @Slot(object)
    def _on_done(self, results):
        self._done(self._operation, results)

    def _done(self, operation, results):
        if operation == "discover":
            self.staged_packages.clear()
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
            self.staged_packages[results.name] = results
            self.status.setText(f"Paket vorbereitet: {results.directory}")
            QMessageBox.information(self, "Paket geprüft und bereitgestellt",
                f"{results.name} {results.version} wurde ohne Installation vorbereitet.\n"
                f"Commit: {results.commit}\nSHA-256 (Archiv): {results.archive_sha256}\n"
                f"Dateien: {results.files}\nZiel: {results.directory}")
        elif operation == "install":
            backup_path = Path(results)
            self.status.setText("AddOn installiert. Sicherung erstellt.")
            dialog = QMessageBox(self)
            dialog.setWindowTitle("Installation erfolgreich")
            dialog.setIcon(QMessageBox.Information)
            dialog.setText("Das AddOn wurde erfolgreich installiert.")
            dialog.setInformativeText(
                "Der vorherige AddOn-Stand wurde gesichert.\n"
                "Du kannst ihn bei Bedarf über die Backup-Wiederherstellung zurückholen.\n\n"
                f"Sicherung: {backup_path.name}"
            )
            dialog.setDetailedText(str(backup_path))
            open_button = dialog.addButton("Backup-Ordner öffnen", QMessageBox.ActionRole)
            dialog.addButton("Schließen", QMessageBox.AcceptRole)
            dialog.exec()
            if dialog.clickedButton() is open_button:
                from PySide6.QtCore import QUrl
                from PySide6.QtGui import QDesktopServices
                QDesktopServices.openUrl(QUrl.fromLocalFile(str(backup_path)))
        else:
            for i, row in enumerate(results):
                if i < self.table.rowCount():
                    self.table.setItem(i, 3, QTableWidgetItem(row.available or "—"))
                    self.table.setItem(i, 4, QTableWidgetItem(row.status + ": " + row.detail))
            self.status.setText("GitHub-Versionsvergleich abgeschlossen. Keine Installation möglich.")
        if operation == "discover" and self.candidates:
            self._scan_after_cleanup = True

    @Slot(str)
    def _failed(self, message):
        self.status.setText("Prüfung fehlgeschlagen: " + message)

    def _cleanup(self):
        if self.thread:
            self.thread.deleteLater()
        self.thread = None
        self.worker = None
        self._operation = None
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
