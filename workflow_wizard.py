"""Optional guided workflow for existing RP Text Studio actions.

The wizard navigates; existing editor operations remain responsible for changes.
No automatic writes, AI calls or key creation happen inside this wizard.
"""
from __future__ import annotations
from PySide6.QtWidgets import (QWizard,QWizardPage,QVBoxLayout,QLabel,
    QComboBox,QCheckBox,QMessageBox)

WORKFLOWS = {
    "edit": ("Text bearbeiten", "Textpool und Zeile auswählen, anschließend Text im Haupteditor bearbeiten.",
             "Änderungen prüfen und erst danach speichern."),
    "spell": ("Zauber ergänzen", "Einen vorhandenen AddOn-Textpool auswählen; anschließend einen neuen Schlüssel anlegen.",
              "Im Editor ziel- und gruppenbezogene Texte ergänzen und anschließend prüfen."),
    "translate": ("KI-Übersetzung", "Die Navigationssprache deDE und einen vorhandenen deutschen Text auswählen.",
                  "Vorschläge prüfen, einzeln freigeben und Änderungen ausdrücklich speichern."),
    "check": ("Projekt prüfen", "Die Textpools auf Platzhalter, leere Texte und Emotes prüfen.",
              "Prüfbericht lesen, Fehler korrigieren und anschließend speichern."),
}
def prerequisites(workflow: str, *, has_project: bool, has_pool: bool,
                  has_row: bool, locale: str) -> list[str]:
    issues=[]
    if not has_project: issues.append("Zuerst einen Projektordner oder eine AddOn-ZIP öffnen.")
    if workflow in ("edit","spell","translate") and not has_pool:
        issues.append("Zuerst einen Textpool im Projektbrowser markieren.")
    if workflow in ("edit","translate") and not has_row:
        issues.append("Zuerst eine Textzeile auswählen.")
    if workflow == "translate" and locale != "deDE":
        issues.append("Für KI-Übersetzungen die Navigationssprache deDE auswählen.")
    return issues

class WorkflowWizard(QWizard):
    def __init__(self,parent):
        super().__init__(parent)
        self.setWindowTitle("RP Workflow-Assistent")
        self.resize(650,390)
        self.setOption(QWizard.NoBackButtonOnStartPage)
        first=QWizardPage()
        first.setTitle("Was möchtest du tun?")
        v=QVBoxLayout(first)
        v.addWidget(QLabel("Wähle einen Arbeitsablauf. Der Assistent führt zu den bestehenden Werkzeugen."))
        self.choice=QComboBox()
        for key, value in WORKFLOWS.items(): self.choice.addItem(value[0],key)
        v.addWidget(self.choice)
        self.addPage(first)
        second=QWizardPage()
        second.setTitle("Vorbereitung")
        v=QVBoxLayout(second)
        self.instructions=QLabel()
        self.instructions.setWordWrap(True)
        v.addWidget(self.instructions)
        self.addPage(second)
        final=QWizardPage()
        final.setTitle("Bereit zum nächsten Schritt")
        v=QVBoxLayout(final)
        self.result_label=QLabel()
        self.result_label.setWordWrap(True)
        v.addWidget(self.result_label)
        v.addWidget(QLabel("Nach Fertigstellen öffnet sich das passende Werkzeug. Es wird nichts automatisch gespeichert."))
        self.addPage(final)
        self.currentIdChanged.connect(self.update_guidance)
        self.update_guidance()

    def update_guidance(self,*_):
        flow=self.choice.currentData()
        if flow not in WORKFLOWS:return
        _,intro,finish=WORKFLOWS[flow]
        issues=prerequisites(flow,has_project=self.parent().root is not None,
            has_pool=self.parent().current is not None,
            has_row=self.parent().current_row>=0,locale=self.parent().language.currentText())
        self.instructions.setText(intro+"\n\n"+
            ("Noch erforderlich:\n• "+"\n• ".join(issues) if issues else "Voraussetzungen erfüllt."))
        self.result_label.setText(finish+
            ("\n\nFehlende Voraussetzungen müssen zuvor im Hauptfenster erfüllt werden." if issues else ""))

    def selected_workflow(self):
        return self.choice.currentData()
