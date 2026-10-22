"""Integrated, review-first translation workspace with left-hand step navigation.

Nothing touches Lua or the translation-link file before the final confirmation.
API generation is optional; human-edited translations follow the same checks.
"""
from __future__ import annotations
import json
import os
from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QDialog, QWidget, QHBoxLayout, QVBoxLayout, QFormLayout, QListWidget,
    QStackedWidget, QComboBox, QLabel, QPlainTextEdit, QLineEdit, QPushButton,
    QCheckBox, QMessageBox, QGroupBox, QSplitter,
)
from ai_translation import inspect_translation
from ai_translation_dialog import Worker
from translation_links import LANGS, pool_id, reference, resolve
from workspace_structures import plan_spell, create_spell, plan_profile, create_profile

STEPS = ("Text auswählen", "Original bearbeiten", "Übersetzen", "Prüfen & speichern", "Strukturen anlegen")

def draft_issues(source: str, translations: dict[str, str]) -> list[str]:
    import re
    issues = []
    if not source.strip():
        issues.append("Deutscher Ausgangstext fehlt.")
    if source.startswith("*") != source.endswith("*"):
        issues.append("deDE: Ungleiche Emote-Markierungen *...*.")
    if "%" in re.sub(r"%(?:%|s|p)", "", source):
        issues.append("deDE: Ungültiger %-Platzhalter.")
    for lang, value in translations.items():
        issues.extend(f"{lang}: {message}" for message in inspect_translation(source, value))
    return issues

class WorkspaceWizard(QDialog):
    def __init__(self, studio):
        super().__init__(studio)
        self.studio = studio
        self.setWindowTitle("RP Text Studio · Arbeitsassistent")
        self.resize(1050, 680)
        self.worker = None
        self.loading = False

        layout = QVBoxLayout(self)
        headline = QLabel("RP-Texte in einem Arbeitsgang bearbeiten und übersetzen")
        headline.setStyleSheet("font-size: 16px; font-weight: 600; padding: 4px;")
        layout.addWidget(headline)
        main = QSplitter(Qt.Horizontal, self)
        self.steps = QListWidget()
        self.steps.addItems(STEPS)
        self.steps.setMaximumWidth(225)
        self.steps.setToolTip("Links einen Arbeitsschritt auswählen. Alle Eingaben bleiben erhalten.")
        main.addWidget(self.steps)
        self.pages = QStackedWidget()
        main.addWidget(self.pages)
        main.setStretchFactor(1, 1)
        layout.addWidget(main, 1)

        self._selection_page()
        self._source_page()
        self._translations_page()
        self._review_page()
        self._structure_page()

        nav = QHBoxLayout()
        self.message = QLabel("Entwurf: Noch nichts gespeichert.")
        nav.addWidget(self.message, 1)
        self.back = QPushButton("Zurück")
        self.next = QPushButton("Weiter")
        self.finish = QPushButton("Prüfen und speichern")
        self.create_structure_button = QPushButton("Struktur prüfen und anlegen")
        cancel = QPushButton("Abbrechen")
        self.back.clicked.connect(lambda: self.steps.setCurrentRow(max(0, self.steps.currentRow()-1)))
        self.next.clicked.connect(lambda: self.steps.setCurrentRow(min(4, self.steps.currentRow()+1)))
        self.finish.clicked.connect(self.commit)
        self.create_structure_button.clicked.connect(self.create_structure)
        cancel.clicked.connect(self.reject)
        for button in (self.back, self.next, self.finish, self.create_structure_button, cancel):
            nav.addWidget(button)
        layout.addLayout(nav)
        self.steps.currentRowChanged.connect(self.switch_page)
        self.steps.setCurrentRow(0)
        self.populate_pools()

    def _page(self, title, explanation):
        page = QWidget()
        col = QVBoxLayout(page)
        col.addWidget(QLabel(f"<b>{title}</b>"))
        hint = QLabel(explanation)
        hint.setWordWrap(True)
        col.addWidget(hint)
        self.pages.addWidget(page)
        return col

    def _selection_page(self):
        col = self._page("1 · Textpool und Ausgangszeile",
                         "Wähle einen vorhandenen deutschen Textpool und eine Zeile. "
                         "Alle anderen Eingaben gehören anschließend genau zu diesem Ausgangstext.")
        form = QFormLayout()
        self.pool = QComboBox()
        self.pool.setToolTip("Vorhandene deDE-Textpools aller AddOns.")
        self.line = QComboBox()
        self.line.setToolTip("Zeile samt Textanfang wählen.")
        form.addRow("Textpool", self.pool)
        form.addRow("Ausgangstext", self.line)
        col.addLayout(form)
        self.pool.currentIndexChanged.connect(self.populate_lines)
        self.line.currentIndexChanged.connect(self.load_source)
        col.addStretch()

    def _source_page(self):
        col = self._page("2 · Deutschen Originaltext bearbeiten",
                         "Änderungen bleiben bis zur abschließenden Freigabe im Entwurf.")
        self.source = QPlainTextEdit()
        self.source.setPlaceholderText("Deutscher RP-Text")
        self.source.textChanged.connect(self.mark_preview_stale)
        col.addWidget(self.source, 1)
        col.addWidget(QLabel("Satz = /say · *Handlung* = /me · %s = Ziel · %p = Begleiter"))

    def _translations_page(self):
        col = self._page("3 · Englische und französische Texte",
                         "Übersetzungen können manuell eingetragen oder per OpenAI vorgeschlagen "
                         "werden. Jede Sprache wird vor der Übernahme einzeln freigegeben.")
        form = QFormLayout()
        self.api = QLineEdit(os.environ.get("OPENAI_API_KEY", ""))
        self.api.setEchoMode(QLineEdit.Password)
        self.api.setToolTip("Optional. Nur im Speicher, nicht in den AddOn-Dateien.")
        self.model = QLineEdit("gpt-5-mini")
        self.style = QLineEdit()
        self.style.setPlaceholderText("z. B. ironischer Gnom-Hexer, wissenschaftlich")
        form.addRow("API-Schlüssel", self.api)
        form.addRow("OpenAI-Modell", self.model)
        form.addRow("Charakterstil", self.style)
        col.addLayout(form)
        self.generate = QPushButton("Mit OpenAI Vorschläge erzeugen")
        self.generate.clicked.connect(self.generate_suggestions)
        col.addWidget(self.generate)
        self.translations = {}
        self.approve = {}
        for lang in ("enUS", "frFR"):
            group = QGroupBox(lang)
            inner = QVBoxLayout(group)
            editor = QPlainTextEdit()
            editor.setMaximumHeight(115)
            editor.setPlaceholderText(f"{lang}: Übersetzung oder KI-Vorschlag")
            inner.addWidget(editor)
            checked = QCheckBox("Diese Übersetzung freigeben")
            inner.addWidget(checked)
            self.translations[lang] = editor
            self.approve[lang] = checked
            col.addWidget(group)
        col.addStretch()

    def _review_page(self):
        col = self._page("4 · Übersicht und Freigabe",
                         "Prüfe die Änderung. Erst der Knopf „Prüfen und speichern“ "
                         "überträgt die Texte in das AddOn-Projekt.")
        self.review = QPlainTextEdit()
        self.review.setReadOnly(True)
        col.addWidget(self.review, 1)
        self.source.textChanged.connect(self.update_review)
        for editor in self.translations.values():
            editor.textChanged.connect(self.update_review)
        for checkbox in self.approve.values():
            checkbox.toggled.connect(self.update_review)

    def _structure_page(self):
        col = self._page("5 · Neue RP-Strukturen anlegen",
                         "Neue Zauber sowie Rassen- und Klassenprofile direkt hier vorbereiten. "
                         "Zuerst werden alle betroffenen Dateien geprüft; erst nach ausdrücklicher "
                         "Bestätigung werden Lua-Backups und Textzweige angelegt.")
        form = QFormLayout()
        self.structure_kind = QComboBox()
        self.structure_kind.addItems(("Zauberschlüssel", "Rassenprofil", "Klassenprofil"))
        self.structure_addon = QComboBox()
        self.structure_addon.addItems(sorted({p.parts[-4] for p in self.studio.files}))
        self.structure_mode = QComboBox()
        self.structure_mode.addItems(("Allgemein · Texts.lua", "Rasse · Racial.lua",
                                      "Klasse · Classes.lua", "Rasse + Klasse · RaceClass.lua"))
        self.structure_race = QLineEdit()
        self.structure_race.setPlaceholderText("z. B. Gnome oder NightElf")
        self.structure_class = QLineEdit()
        self.structure_class.setPlaceholderText("z. B. WARLOCK")
        self.structure_key = QLineEdit()
        self.structure_key.setPlaceholderText("z. B. SHADOW_BOLT oder NightElf")
        self.structure_name = QLineEdit()
        self.structure_name.setPlaceholderText("Anzeigename, z. B. Nachtelf")
        self.structure_style = QPlainTextEdit()
        self.structure_style.setPlaceholderText("Charaktertypischer RP-Sprachstil")
        self.structure_style.setMaximumHeight(85)
        self.structure_with_lua = QCheckBox("Passenden Lua-Textzweig erzeugen (RP_GREETING)")
        self.structure_with_lua.setChecked(True)
        for label,control in (
            ("Erstellen",self.structure_kind),("AddOn",self.structure_addon),
            ("Struktur",self.structure_mode),("Rassen-ID",self.structure_race),
            ("Klassen-ID",self.structure_class),("Neuer Schlüssel / ID",self.structure_key),
            ("Anzeigename",self.structure_name),("RP-Stil",self.structure_style),
        ):
            form.addRow(label,control)
        form.addRow(self.structure_with_lua)
        col.addLayout(form)
        self.structure_preview = QPlainTextEdit()
        self.structure_preview.setReadOnly(True)
        col.addWidget(self.structure_preview,1)
        for widget in (self.structure_kind,self.structure_addon,self.structure_mode):
            widget.currentIndexChanged.connect(self.update_structure_preview)
        for widget in (self.structure_race,self.structure_class,self.structure_key,self.structure_name):
            widget.textChanged.connect(self.update_structure_preview)
        self.structure_style.textChanged.connect(self.update_structure_preview)
        self.structure_with_lua.toggled.connect(self.update_structure_preview)
        self.structure_kind.currentIndexChanged.connect(self.sync_structure_fields)
        self.structure_mode.currentIndexChanged.connect(self.sync_structure_fields)
        self.sync_structure_fields()
        self.update_structure_preview()

    def sync_structure_fields(self,*_):
        spell=self.structure_kind.currentIndex()==0
        mode=self.structure_mode.currentIndex()
        self.structure_mode.setEnabled(spell)
        self.structure_race.setEnabled(spell and mode in (1,3))
        self.structure_class.setEnabled(spell and mode in (2,3))
        self.structure_name.setEnabled(not spell)
        self.structure_style.setEnabled(not spell)
        self.structure_with_lua.setEnabled(not spell)

    def plan_structure(self):
        root=self.studio.root
        addon=self.structure_addon.currentText()
        key=self.structure_key.text().strip()
        if self.structure_kind.currentIndex()==0:
            targets,branches=plan_spell(root,addon,self.structure_mode.currentIndex(),
                self.structure_race.text().strip(),self.structure_class.text().strip(),key)
            return (f"Neuer Schlüssel: {key}\nAddOn: {addon}\n"
                f"Eltern: {'/'.join(branches) or 'Allgemein'}\n"
                "Zielsprachen:\n"+'\n'.join(str(p.relative_to(root)) for p,_,_ in targets)+
                "\n\nDie AddOn-Logik erkennt neue Zauber NICHT automatisch.")
        kind="race" if self.structure_kind.currentIndex()==1 else "class"
        targets=plan_profile(root,addon,kind,key,self.structure_name.text(),
            self.structure_style.toPlainText(),self.structure_with_lua.isChecked())
        return (f"Neues {'Rassen' if kind=='race' else 'Klassen'}profil: {key}\n"
                f"Anzeigename: {self.structure_name.text()}\n"
                f"Sprachstil: {self.structure_style.toPlainText()}\n"
                "Geplante Lua-Dateien:\n"+
                ('\n'.join(str(p.relative_to(root)) for p,_,_ in targets) if targets else "(nur Projektregister)")+
                "\n\nEin Profil ändert nicht die Rassen-/Klassenerkennung des WoW-Clients.")

    def update_structure_preview(self,*_):
        if not hasattr(self,"structure_preview"): return
        try:
            self.structure_preview.setPlainText(self.plan_structure())
        except (OSError,ValueError) as error:
            self.structure_preview.setPlainText(f"Vorabprüfung: {error}")

    def create_structure(self):
        if self.worker and self.worker.isRunning():
            QMessageBox.warning(self,"Anfrage läuft","Bitte die Übersetzungsanfrage abschließen.")
            return
        try:
            preview=self.plan_structure()
            if self.studio.changes or self.studio.links_dirty:
                raise ValueError("Bitte zuerst offene Editor-Änderungen speichern.")
        except (OSError,ValueError) as error:
            QMessageBox.warning(self,"Vorabprüfung fehlgeschlagen",str(error))
            return
        response=QMessageBox.question(self,"Struktur wirklich anlegen?",
            preview+"\n\nJetzt mit Backups anlegen?",QMessageBox.Yes|QMessageBox.No,QMessageBox.No)
        if response!=QMessageBox.Yes:return
        try:
            addon=self.structure_addon.currentText()
            key=self.structure_key.text().strip()
            if self.structure_kind.currentIndex()==0:
                created=create_spell(self.studio.root,addon,self.structure_mode.currentIndex(),
                    self.structure_race.text().strip(),self.structure_class.text().strip(),key)
            else:
                kind="race" if self.structure_kind.currentIndex()==1 else "class"
                created=create_profile(self.studio.root,addon,kind,key,
                    self.structure_name.text(),self.structure_style.toPlainText(),
                    self.structure_with_lua.isChecked())
            self.studio.load(self.studio.root)
            QMessageBox.information(self,"Erstellt",
                f"Struktur angelegt. {created} Lua-Sprachdatei(en) bearbeitet.\n"
                "Bitte die neuen RP-Texte im Editor ergänzen.")
            self.accept()
        except (OSError,ValueError) as error:
            QMessageBox.critical(self,"Anlegen fehlgeschlagen",str(error))

    def populate_pools(self):
        studio = self.studio
        self.loading = True
        self.pool.clear()
        for path, pools in sorted(studio.files.items(), key=lambda kv: str(kv[0])):
            if path.parent.name != "deDE":
                continue
            for key in pools:
                label = f"{path.parts[-4]} / {path.name} / {' / '.join(key[2:])}"
                self.pool.addItem(label, (path, key))
        self.loading = False
        if studio.current and studio.current[0].parent.name == "deDE":
            for index in range(self.pool.count()):
                if self.pool.itemData(index) == studio.current:
                    self.pool.setCurrentIndex(index)
                    break
        self.populate_lines()

    def populate_lines(self):
        if self.loading:
            return
        data = self.pool.currentData()
        self.loading = True
        self.line.clear()
        if data:
            for index, value in enumerate(self.studio.get_entries(*data)):
                self.line.addItem(f"{index+1:02d} · {' '.join(value.split())[:100]}", index)
        self.loading = False
        if data == self.studio.current and self.studio.current_row >= 0:
            self.line.setCurrentIndex(self.studio.current_row)
        self.load_source()

    def load_source(self):
        if self.loading:
            return
        data = self.pool.currentData()
        row = self.line.currentData()
        if not data or row is None:
            self.source.clear()
            return
        self.source.blockSignals(True)
        self.source.setPlainText(self.studio.get_entries(*data)[row])
        self.source.blockSignals(False)
        for lang in self.translations:
            self.translations[lang].clear()
            self.approve[lang].setChecked(False)
        self.update_review()

    def selection(self):
        data = self.pool.currentData()
        row = self.line.currentData()
        if data is None or row is None:
            raise ValueError("Bitte einen deutschen Ausgangstext auswählen.")
        return data[0], data[1], row

    def target(self, source_path: Path, source_key: tuple, lang: str):
        target_path = source_path.parent.parent / lang / source_path.name
        key = list(source_key)
        if len(key) > 1 and key[0] == "localeData" and key[1] == "deDE":
            key[1] = lang
        result = tuple(key)
        if target_path not in self.studio.files or result not in self.studio.files[target_path]:
            raise ValueError(f"{lang}: Entsprechender Textpool fehlt.")
        return target_path, result

    def mark_preview_stale(self):
        for checkbox in self.approve.values():
            checkbox.setChecked(False)
        self.update_review()

    def update_review(self):
        if not hasattr(self, "review"):
            return
        try:
            path, key, row = self.selection()
            label = f"{path.parts[-4]} · {path.name} · {'/'.join(key)} · Zeile {row+1}"
        except ValueError:
            label = "Kein Ausgangstext gewählt"
        translations = {lang: ed.toPlainText() for lang, ed in self.translations.items()
                        if self.approve[lang].isChecked()}
        issues = draft_issues(self.source.toPlainText(), translations)
        lines = [label, "", "Deutsch:", self.source.toPlainText(), ""]
        for lang in ("enUS","frFR"):
            lines.extend((f"{lang} ({'freigegeben' if lang in translations else 'nicht freigegeben'}):",
                          self.translations[lang].toPlainText() or "(leer)", ""))
        lines.append("Prüfung: " + ("; ".join(issues) if issues else "keine Auffälligkeiten"))
        self.review.setPlainText("\n".join(lines))

    def switch_page(self, index):
        self.pages.setCurrentIndex(max(0,index))
        self.back.setEnabled(index > 0)
        self.next.setEnabled(index < 4)
        self.finish.setVisible(index == 3)
        self.create_structure_button.setVisible(index == 4)
        if index == 3:
            self.update_review()

    def generate_suggestions(self):
        if self.worker and self.worker.isRunning():
            return
        try:
            path, _, _ = self.selection()
        except ValueError as error:
            QMessageBox.warning(self, "Auswahl fehlt", str(error))
            return
        if not self.api.text().strip():
            QMessageBox.warning(self, "API-Schlüssel fehlt", "Bitte OpenAI-Schlüssel eintragen.")
            return
        locked_widgets = (
            self.generate, self.pool, self.line, self.source,
            *self.translations.values(), *self.approve.values(),
        )
        for widget in locked_widgets:
            widget.setEnabled(False)
        self.message.setText("OpenAI-Anfrage läuft …")
        self.worker = Worker(self.source.toPlainText(), dict(
            api_key=self.api.text(), model=self.model.text(),
            addon=path.parts[-4], race="", character_style=self.style.text()))
        self.worker.translated.connect(self.show_suggestions)
        self.worker.failed.connect(self.show_api_error)
        def request_finished():
            for widget in locked_widgets:
                widget.setEnabled(True)
        self.worker.finished.connect(request_finished)
        self.worker.start()

    def show_suggestions(self, translations):
        for lang, value in translations.items():
            self.translations[lang].setPlainText(value)
            self.approve[lang].setChecked(False)
        self.message.setText("KI-Vorschläge erhalten. Bitte prüfen und einzeln freigeben.")

    def show_api_error(self, error):
        self.message.setText("API-Fehler")
        QMessageBox.warning(self, "Übersetzung fehlgeschlagen", error)

    def commit(self):
        if self.worker and self.worker.isRunning():
            QMessageBox.warning(self, "Anfrage läuft", "Bitte die laufende API-Anfrage abschließen.")
            return
        try:
            path, key, row = self.selection()
            studio = self.studio
            original = list(studio.get_entries(path, key))
            if not 0 <= row < len(original):
                raise ValueError("Ausgangszeile existiert nicht mehr.")
            old_value = original[row]
            source = self.source.toPlainText()
            selected = {lang: ed.toPlainText() for lang, ed in self.translations.items()
                        if self.approve[lang].isChecked()}
            errors = draft_issues(source, selected)
            if errors:
                raise ValueError("\n".join(errors))
            pk = pool_id(str(path.relative_to(studio.root)), key)
            groups = studio.links.get(pk, [])
            if selected and any(resolve(original, group.get("deDE")) == row for group in groups):
                raise ValueError("Dieser Text hat bereits eine Übersetzungsgruppe. Bitte zuerst die vorhandene Verknüpfung prüfen.")
            planned = {}
            for lang, value in selected.items():
                other_path, other_key = self.target(path, key, lang)
                entries = list(studio.get_entries(other_path, other_key))
                matches = [i for i, text in enumerate(entries) if text == value]
                if len(matches) > 1:
                    raise ValueError(f"{lang}: Text ist mehrfach vorhanden und kann nicht eindeutig verknüpft werden.")
                idx = matches[0] if matches else len(entries)
                if not matches:
                    entries.append(value)
                if any(resolve(entries, group.get(lang)) == idx for group in groups):
                    raise ValueError(f"{lang}: Text ist bereits einer anderen Gruppe zugeordnet.")
                planned[lang] = (other_path, other_key, entries, idx)
            # All validations finished; stage into the existing editor model.
            if source != old_value:
                linked_groups = [
                    group for group in groups
                    if resolve(original, group.get("deDE")) == row
                ]
                original[row] = source
                for group in linked_groups:
                    group["deDE"] = reference(original, row)
                if linked_groups:
                    studio.links_dirty = True
                studio.changes.setdefault(path, {})[studio.locale_key(path, key)] = original
            if planned:
                group = {"deDE": reference(original, row)}
                for lang, (other_path, other_key, entries, idx) in planned.items():
                    if entries != studio.get_entries(other_path, other_key):
                        studio.changes.setdefault(other_path, {})[
                            studio.locale_key(other_path,other_key)] = entries
                    group[lang] = reference(entries,idx)
                studio.links.setdefault(pk, []).append(group)
                studio.links_dirty = True
            studio.update_status()
            if studio.save_all():
                QMessageBox.information(self, "Erfolgreich", "Texte und Verknüpfungen gespeichert.")
                self.accept()
        except (ValueError, OSError) as error:
            QMessageBox.warning(self, "Prüfung fehlgeschlagen", str(error))

    def reject(self):
        if self.worker and self.worker.isRunning():
            QMessageBox.information(self, "API-Anfrage läuft", "Bitte zunächst die laufende Anfrage abschließen.")
            return
        super().reject()
