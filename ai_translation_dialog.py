"""Review-first OpenAI translation dialog. API key stays in memory."""
from __future__ import annotations
import os
from PySide6.QtCore import QThread, Signal
from PySide6.QtWidgets import (QDialog,QVBoxLayout,QFormLayout,QLineEdit,QPlainTextEdit,
    QLabel,QPushButton,QHBoxLayout,QMessageBox,QCheckBox)
from ai_translation import translate, inspect_translation

class Worker(QThread):
    translated = Signal(dict)
    failed = Signal(str)
    def __init__(self, source, config):
        super().__init__()
        self.source, self.config = source, config
    def run(self):
        try:
            self.translated.emit({lang: translate(self.source, lang, **self.config)
                                  for lang in ("enUS","frFR")})
        except Exception as exc:
            self.failed.emit(str(exc))

class TranslationDialog(QDialog):
    def __init__(self, parent, source, addon, race, on_accept):
        super().__init__(parent)
        self.setWindowTitle("KI-Übersetzungen prüfen")
        self.resize(770,620)
        self.source, self.addon, self.on_accept = source, addon, on_accept
        self.worker = None
        layout=QVBoxLayout(self)
        layout.addWidget(QLabel("Deutsch (Original, unveränderlich)"))
        original=QPlainTextEdit(source);original.setReadOnly(True);original.setMaximumHeight(85)
        layout.addWidget(original)
        form=QFormLayout()
        self.api_key=QLineEdit(os.environ.get("OPENAI_API_KEY",""))
        self.api_key.setEchoMode(QLineEdit.Password)
        self.api_key.setToolTip("Nur für diese Sitzung. Alternativ OPENAI_API_KEY als Umgebungsvariable.")
        self.model=QLineEdit("gpt-5-mini")
        self.race=QLineEdit(race)
        self.style=QLineEdit()
        self.style.setPlaceholderText("z. B. gnomisch, ironisch, wissenschaftlich")
        for title, widget in (("OpenAI API-Key",self.api_key),("Modell",self.model),
                              ("Rasse",self.race),("Charakterstil",self.style)):
            form.addRow(title,widget)
        layout.addLayout(form)
        self.texts={};self.approvals={}
        for lang in ("enUS","frFR"):
            box=QCheckBox(lang+" nach Prüfung freigeben")
            layout.addWidget(box)
            edit=QPlainTextEdit()
            edit.setPlaceholderText("KI-Vorschlag kann vor der Freigabe geändert werden")
            edit.setMaximumHeight(105)
            layout.addWidget(edit)
            self.texts[lang]=edit;self.approvals[lang]=box
        self.message=QLabel("API-Anfrage nur nach Klick auf „Vorschläge erzeugen“. Kosten möglich.")
        self.message.setWordWrap(True)
        layout.addWidget(self.message)
        row=QHBoxLayout()
        self.generate=QPushButton("Vorschläge erzeugen")
        self.generate.clicked.connect(self.request)
        row.addWidget(self.generate)
        approve=QPushButton("Freigegebene übernehmen")
        approve.clicked.connect(self.apply)
        row.addWidget(approve)
        close=QPushButton("Schließen");close.clicked.connect(self.reject);row.addWidget(close)
        layout.addLayout(row)

    def request(self):
        if self.worker and self.worker.isRunning():return
        if not self.api_key.text().strip():
            QMessageBox.warning(self,"API-Key fehlt","OPENAI_API_KEY setzen oder Schlüssel eingeben.")
            return
        self.generate.setEnabled(False)
        config=dict(api_key=self.api_key.text(),model=self.model.text(),addon=self.addon,
                    race=self.race.text(),character_style=self.style.text())
        self.worker=Worker(self.source,config)
        self.worker.translated.connect(self.show_results)
        self.worker.failed.connect(self.show_error)
        self.worker.finished.connect(lambda:self.generate.setEnabled(True))
        self.worker.start()

    def show_results(self, results):
        for lang,result in results.items():
            self.texts[lang].setPlainText(result)
            self.approvals[lang].setChecked(False)
        self.message.setText("Vorschläge erhalten: bitte kontrollieren, bearbeiten und einzeln freigeben.")

    def show_error(self, message):
        self.message.setText(message)
        QMessageBox.warning(self,"OpenAI-Fehler",message)

    def apply(self):
        if self.worker and self.worker.isRunning():
            QMessageBox.information(self,"Anfrage läuft","Der laufende API-Aufruf muss zunächst enden.")
            return
        selected={lang:edit.toPlainText() for lang,edit in self.texts.items()
                  if self.approvals[lang].isChecked()}
        if not selected:
            QMessageBox.information(self,"Keine Freigabe","Mindestens eine Sprache auswählen.")
            return
        for lang,value in selected.items():
            problems=inspect_translation(self.source,value)
            if problems:
                QMessageBox.warning(self,lang+" ungültig","\n".join(problems));return
        if self.on_accept(selected):
            self.accept()

    def reject(self):
        if self.worker and self.worker.isRunning():
            QMessageBox.information(self,"Anfrage läuft","Der laufende API-Aufruf muss zunächst enden.")
            return
        super().reject()
