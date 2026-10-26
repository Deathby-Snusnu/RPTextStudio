"""User mode: read-only WoW addon overview with background discovery and GitHub checks."""
from __future__ import annotations
from pathlib import Path
import tempfile
from uuid import uuid4
from PySide6.QtCore import QObject, QThread, Signal, Slot, Qt
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QComboBox, QPushButton,
    QTableWidget, QTableWidgetItem, QMessageBox, QFileDialog, QInputDialog,
    QDialogButtonBox, QListWidget, QListWidgetItem,
)
from addon_catalog import load_catalog
from wow_installations import load_paths
from wow_detection import discover_wow_installations, inspect_client
from user_addon_manager import inspect_installed, check_installed
from github_staging import stage
from safe_github_install import preview_safe_install, install_safe
from addon_manager import rollback
from batch_addon_install import prepare_missing, install_missing, discard_missing, missing_names
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
            elif self.operation == "prepare_missing":
                result = prepare_missing(self.target, self.staging_target, self.channel)
            elif self.operation == "install_missing":
                result = install_missing(self.staging_target)
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
        self.catalog = {entry.id: entry for entry in load_catalog()}
        self.staged_packages = {}
        self.missing_batch = None
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
        self.stage_button = QPushButton("AddOn herunterladen und prüfen…")
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
        self.missing_button = QPushButton('Alle fehlenden RP-AddOns vorbereiten…')
        self.missing_button.clicked.connect(self.handle_missing)
        actions.addWidget(self.missing_button)
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
        self.missing_button.setEnabled(not busy and self.current_target() is not None)

    def _selected_addon_id(self):
        item = self.table.item(self.table.currentRow(), 0)
        return (item.data(Qt.UserRole) or item.text()) if item else None

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
        info = 'Kompatibilität für jedes AddOn separat prüfen'
        self.status.setText(f'Interface-Profil gespeichert: {profile.interface} ({profile.client_type}). {info}. Keine TOC verändert.')

    def preview_selected_toc(self):
        root = self.current_target()
        row = self.table.currentRow()
        if root is None or self.thread is not None or row < 0:
            return
        name = self._selected_addon_id()
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

    def handle_missing(self):
        if self.thread is not None or self.current_target() is None:
            return
        if self.missing_batch is not None:
            batch = self.missing_batch
            if batch.target != self.current_target():
                discard_missing(batch)
                self.missing_batch = None
                self.missing_button.setText("Alle fehlenden RP-AddOns vorbereiten…")
                QMessageBox.warning(self, "WoW-Installation gewechselt",
                    "Die vorbereiteten Pakete gehörten zu einer anderen Installation. Bitte neu vorbereiten.")
                return
            names = ", ".join(plan.name for plan in batch.plans)
            summary = (
                f"WoW-Installation: {batch.target.parent.parent}\n"
                f"Interface-Nummer: {batch.profile.interface}\n"
                f"Kanal: {batch.channel}\n"
                f"Neue AddOns: {len(batch.plans)}\n\n"
                f"{names}\n\n"
                "Nur fehlende RP-AddOns werden installiert. Bereits vorhandene "
                "AddOn-Ordner und Benutzertexte bleiben unverändert. "
                "Die Installation erstellt Wiederherstellungsinformationen.\n\n"
                "Achtung: Eine angepasste Interface-Nummer garantiert keine "
                "funktionale WoW-API-Kompatibilität. Fortfahren nur für "
                "einen ausdrücklich gewünschten Test."
            )
            dialog = QMessageBox(self)
            dialog.setWindowTitle("Gemeinsame Erstinstallation bestätigen")
            dialog.setIcon(QMessageBox.Warning)
            dialog.setText("Alle vorbereiteten RP-AddOns installieren?")
            dialog.setInformativeText(summary)
            dialog.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
            dialog.setDefaultButton(QMessageBox.No)
            dialog.button(QMessageBox.Yes).setText("Installieren")
            dialog.button(QMessageBox.No).setText("Abbrechen")
            if dialog.exec() == QMessageBox.Yes:
                self._start("install_missing", staging_target=batch)
            return

        installation = self.candidates[self.installations.currentIndex()]
        profile = get_profile(installation.client_root)
        if profile is None:
            QMessageBox.information(self, "Interface-Profil fehlt",
                "Bitte zuerst unter 'Interface-Profil…' die Nummer des WoW-Clients speichern.")
            return
        try:
            names = missing_names(self.current_target())
        except Exception as exc:
            QMessageBox.warning(self, "Erstinstallation nicht möglich", str(exc))
            return
        if not names:
            QMessageBox.information(self, "Keine fehlenden AddOns",
                "Alle sechs bekannten RP-AddOns sind bereits vorhanden.")
            return
        if QMessageBox.question(self, "Fehlende RP-AddOns herunterladen",
            f"{len(names)} AddOns fehlen:\n" + "\n".join(names) +
            f"\n\nKanal: {self.channel.currentText()}\n"
            "Pakete werden zuerst außerhalb von WoW geladen und geprüft. "
            "Es wird jetzt noch nichts installiert.",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No) != QMessageBox.Yes:
            return
        self._start("prepare_missing", staging_target=profile)

    def selected_staged(self):
        row = self.table.currentRow()
        if not 0 <= row < self.table.rowCount():
            return None
        item = self.table.item(row, 0)
        return self.staged_packages.get(item.data(Qt.UserRole) or item.text()) if item else None

    def _choose_overwrites(self, plan):
        """Require affirmative per-file selection; unchecked means preserve."""
        dialog = QDialog(self)
        dialog.setWindowTitle("Geschützte Dateien gezielt aktualisieren")
        dialog.resize(690, 430)
        layout = QVBoxLayout(dialog)
        explanation = QLabel(
            f"GitHub unterscheidet sich bei {len(plan.protected)} vorhandenen Dateien.\n\n"
            "Alle Dateien bleiben standardmäßig geschützt. Markiere nur Dateien, "
            "deren lokale Fassung du bewusst durch die geprüfte GitHub-Fassung "
            "ersetzen möchtest. Eventuelle eigene Änderungen in diesen Dateien "
            "sind anschließend nur noch im automatischen Backup vorhanden.\n\n"
            "Ein vollständiges Backup wird vor der Änderung angelegt. "
            "Unmarkierte Dateien bleiben unverändert."
        )
        explanation.setWordWrap(True)
        layout.addWidget(explanation)
        choices = QListWidget(dialog)
        for name in plan.protected:
            item = QListWidgetItem(name, choices)
            item.setFlags(item.flags() | Qt.ItemIsUserCheckable)
            item.setCheckState(Qt.Unchecked)
        layout.addWidget(choices)
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel, parent=dialog)
        buttons.button(QDialogButtonBox.Ok).setText("Auswahl übernehmen")
        buttons.button(QDialogButtonBox.Cancel).setText("Abbrechen")
        buttons.accepted.connect(dialog.accept)
        buttons.rejected.connect(dialog.reject)
        layout.addWidget(buttons)
        if dialog.exec() != QDialog.Accepted:
            return None
        return tuple(
            sorted(choices.item(i).text() for i in range(choices.count())
                   if choices.item(i).checkState() == Qt.Checked)
        )

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
        if plan.protected:
            replacements = self._choose_overwrites(plan)
            if replacements is None:
                return
            if replacements:
                try:
                    approved_plan = preview_safe_install(
                        package.name, package.directory, target, profile,
                        approved_overwrites=replacements,
                    )
                except Exception as exc:
                    QMessageBox.warning(self, "Aktualisierung nicht möglich", str(exc))
                    return
                if (approved_plan.source_hashes != plan.source_hashes
                        or approved_plan.target_hashes != plan.target_hashes):
                    QMessageBox.warning(
                        self, "Vorschau veraltet",
                        "Dateien wurden während der Auswahl geändert. "
                        "Bitte die Vorschau neu starten.",
                    )
                    return
                plan = approved_plan
        if not plan.new_files and not plan.toc_changed and not plan.approved_overwrites:
            details = (
                f"Für {package.name} gibt es derzeit keine gefahrlos anwendbaren Änderungen.\n\n"
                f"Neue Dateien: 0\n"
                f"TOC-Interface bereits passend: {profile.interface}\n"
                f"Abweichende vorhandene Dateien (geschützt): {len(plan.protected)}\n\n"
                "Bereits vorhandene Programm- und Textdateien werden aus Sicherheitsgründen "
                "nicht automatisch überschrieben. Eine neue GitHub-Version kann deshalb "
                "vorliegen, obwohl hier kein sicheres Update möglich ist."
            )
            QMessageBox.information(self, "Keine Aktualisierung freigegeben", details)
            self.status.setText(f"{package.name}: keine sicheren Änderungen; vorhandene Dateien geschützt.")
            return
        summary = (
            f"AddOn: {package.name}\n"
            f"Ziel: {target / package.name}\n"
            f"Interface-Profil: {profile.interface}\n\n"
            "Geplante Änderungen\n"
            f"  • Neue Dateien: {len(plan.new_files)}\n"
            f"  • Geschützte abweichende Dateien: {len(plan.protected) - len(plan.approved_overwrites)}\n"
            f"  • Ausdrücklich freigegebene Ersetzungen: {len(plan.approved_overwrites)}\n"
            f"  • Interface-Zeile der TOC anpassen: {'Ja' if plan.toc_changed else 'Nein'}\n\n"
            "Bestandsschutz\n"
            "  • Nicht ausgewählte RP-Texte und sonstige Dateien bleiben erhalten.\n"
            "  • Ausgewählte vorhandene Dateien werden durch GitHub-Versionen ersetzt;\n"
            "    lokale Anpassungen dieser Dateien bleiben nur im Backup.\n"
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
        name = self._selected_addon_id()
        channel = self.channel.currentData()
        # Use a private temporary staging location, never a WoW directory.
        destination = Path(tempfile.gettempdir()) / ("rptextstudio-" + name + "-" + uuid4().hex)
        if QMessageBox.question(self, "AddOn sicher vorbereiten",
            f"{name} aus dem GitHub-Kanal {channel} herunterladen und prüfen?\\n\\n"
            "Das Paket wird in einem temporären Ordner vorbereitet. "
            "Deine WoW-AddOns bleiben bis zur ausdrücklichen Installationsbestätigung unverändert.") != QMessageBox.Yes:
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
            if self.missing_batch is not None:
                discard_missing(self.missing_batch)
                self.missing_batch = None
                self.missing_button.setText("Alle fehlenden RP-AddOns vorbereiten…")
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
                catalog_entry = self.catalog.get(entry.name)
                display_name = catalog_entry.title if catalog_entry else entry.name
                for j, value in enumerate((display_name, entry.version or "—", entry.interface or "—",
                                          "Noch nicht geprüft", entry.state)):
                    item = QTableWidgetItem(value)
                    if j == 0:
                        item.setData(Qt.UserRole, entry.name)
                        if catalog_entry:
                            item.setToolTip(catalog_entry.description or catalog_entry.repository)
                    self.table.setItem(i, j, item)
            self.status.setText("Lokale RP-AddOns eingelesen. Keine Änderungen vorgenommen.")
        elif operation == "prepare_missing":
            self.missing_batch = results
            self.missing_button.setText("Alle vorbereiteten RP-AddOns installieren…")
            self.status.setText(f"{len(results.plans)} RP-AddOns geprüft und bereitgestellt. Installation noch nicht gestartet.")
            QMessageBox.information(self, "Pakete bereit",
                f"{len(results.plans)} fehlende RP-AddOns wurden außerhalb von WoW heruntergeladen "
                "und geprüft. Mit 'Alle vorbereiteten RP-AddOns installieren…' kann die "
                "gemeinsame Installationsvorschau geöffnet werden.")
        elif operation == "install_missing":
            count = len(results)
            if self.missing_batch is not None:
                discard_missing(self.missing_batch)
                self.missing_batch = None
            self.missing_button.setText("Alle fehlenden RP-AddOns vorbereiten…")
            self.status.setText(f"{count} RP-AddOns installiert.")
            QMessageBox.information(self, "Erstinstallation abgeschlossen",
                f"{count} RP-AddOns wurden installiert. Vorhandene AddOns blieben unverändert. "
                "Wiederherstellungsdaten liegen im AddOns-Backup-Verzeichnis.")
            self._scan_after_cleanup = True
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
            dialog.addButton("Schließen", QMessageBox.RejectRole)
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
        if self.missing_batch is not None and self.missing_batch.target != self.current_target():
            discard_missing(self.missing_batch)
            self.missing_batch = None
            self.missing_button.setText("Alle fehlenden RP-AddOns vorbereiten…")
        self.table.setRowCount(0)
        if self.current_target() is not None:
            self._start("local")

    def reject(self):
        if self.thread is not None and self.thread.isRunning():
            self.status.setText("Laufende Suche wird abgeschlossen. Danach kann das Fenster geschlossen werden.")
            return
        if self.missing_batch is not None:
            discard_missing(self.missing_batch)
            self.missing_batch = None
        super().reject()
