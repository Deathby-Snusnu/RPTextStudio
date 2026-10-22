# Changelog

## [0.1.15] – Integrierter Arbeitsassistent

- F2 öffnet einen breiten Arbeitsdialog mit Schrittliste links und Editor rechts.
- Deutsches Original bearbeiten, Übersetzungen manuell oder mit OpenAI vorbereiten und einzeln freigeben.
- Gesamtvorschau und Validierung vor dem expliziten Speichern mit Backups.
- Alter Navigations-Wizard bleibt separat erreichbar.
- Tests und Handbuch ergänzt; neue Schlüssel weiterhin über die bestehenden Manager.



## [0.1.14] – Geführter Workflow-Assistent

- Optionaler Wizard unter Hilfe → Workflow-Assistent (F2).
- Vier geführte Einstiege: Text bearbeiten, Zauber ergänzen, KI-Übersetzung, Projektprüfung.
- Kontextprüfung auf geöffnetes Projekt, gewählten Textpool und deDE-Ausgangszeile.
- Keine automatischen Schreibvorgänge oder API-Aufrufe; vorhandene Werkzeuge bleiben zuständig.
- Dokumentation und Tests der Voraussetzungen ergänzt.



## [0.1.13] – Klassische Desktopnavigation

- Menüleiste Datei / Bearbeiten / Projekt / Übersetzungen / Ansicht / Hilfe.
- Kompakte Symbolleiste für oft verwendete Aktionen und einheitliche Tastenkürzel.
- Dauerhafte Statusfelder für Projekt, Navigationssprache, Textauswahl und offene Änderungen.
- Bestehende Bearbeitungsfunktionen erhalten; Workflow-Assistent folgt später.
- Dokumentation entsprechend ergänzt.



### Unreleased: OpenAI-RP-Übersetzungen

- Optionaler OpenAI-Responses-API-Übersetzer für deutsche RP-Texte nach `enUS` und `frFR`.
- Manuelle Prüfung und Freigabe pro Zielsprache; sichere Verknüpfung mit den vorhandenen Übersetzungsgruppen.
- Schutz für RP-Platzhalter und `/me`-Markierungen, API-Schlüssel nur im Speicher.
- Offline-Mock-Tests sowie ergänzte Anleitung.


Die dokumentierte Historie wird nach Versionen geordnet. Undatierte
Versionen erhalten kein nachträglich angenommenes Release-Datum.

## [Unreleased]

### Windows-Paket

- `build_exe.bat` erstellt mit PyInstaller eine einzelne Windows-EXE samt Python, Qt und eingebettetem Handbuch.
- Build-Abhängigkeiten separat in `requirements-build.txt`; Projektdateien und Backups bleiben extern bearbeitbar.
- Windows-Starter bevorzugen eine vorhandene EXE und benötigen dann keine Python-Installation.

### Dokumentation

- README und Handbuch auf den Anwendungsstand 0.1.10 abgestimmt.
- Projektlokale Installation, pytest-Aufruf, Variantenwahl, Manager-Grenzen,
  Modulaufgaben und getrennte Projektregister dokumentiert.
- Historische Funktionsbeschreibungen von der aktuellen Bedienung getrennt.

## [0.1.10]

### Behoben

- Sprachvergleich: Sprachsegment in Lua-Pool-Schlüsseln wird beim Zugriff auf
  DE/EN/FR korrekt angepasst.
- Übersetzungsgruppen erhalten sprachübergreifende IDs; bestehende JSON-IDs
  werden beim Laden migriert.
- Speichern in fremden Sprachspalten verwendet nun den richtigen Lua-Schlüssel.

## [0.1.9] - 2026-10-19

### Geändert

- Sprachvarianten per Dropdown mit Textvorschau statt Zeilennummern wählen.
- Korrektur: Die Sprach-Editoren bearbeiten jetzt tatsächlich die
  ausgewählte Variante.
- Explizite Sprachwahl, Mindestanzahl zwei Sprachen, Konfliktprüfung vor Änderung.
- Hilfe, README und Startskript aktualisiert.

## [0.1.8] - 2026-10-19

### Hinzugefügt

- Rassen- und Klassen-Manager mit Name, ID, Sprachstil und Projektregister.
- Optionale Lua-Textzweige in vorhandenen `Racial.lua`- und `Classes.lua`-Dateien,
  mit Vorabprüfung und Backups.
- Tooltips, Hilfetexte, Dokumentation und zusätzliche Tests.
- Keine Änderung der AddOn-Laufzeit oder der vom Spiel unterstützten Rassen/Klassen.

### Geändert

- `Start.bat` richtet `.venv` bei Bedarf ein, aktiviert sie,
  prüft/installiert `requirements.txt` und startet die Anwendung.
- `start_windows.bat` bleibt als Alias erhalten.
- README und Handbuch um Einrichtung und Fehlersuche erweitert.

## [0.1.7]

### Hinzugefügt

- Zauber-Manager mit vorhandenen RP-Schlüsseln, Zuordnung lokalisierter
  Zaubernamen und Makro-Vorschau.
- Projektbezogene JSON-Speicherung samt Backup, Hilfetexte und Tests.
- Keine automatische Cast-/Spell-ID-Erkennung oder Änderung an AddOn-Core-Dateien.

## [0.1.6] - 2026-10-19

### Hinzugefügt

- Dialog zum Anlegen neuer Rassen-, Klassen-, Rassen-Klassen- und allgemeiner
  Text-/Zauberschlüssel.
- Neue Schlüssel in den vorhandenen DE/EN/FR-Lua-Textdateien, mit Prüfung
  gegen doppelte und ungültige Namen.
- Unterstützt direkte Textlisten und `ziel`/`gruppe`-Tabellen anhand des bestehenden Dateischemas.
- Testlauf an temporären Kopien, Sicherungen vor Schreibvorgängen, neu geladene Textpools nach Erstellung.
- Tooltips, README und Handbuch erweitert.

## [0.1.5] - 2026-10-19

### Hinzugefügt

- Filter für Textart und Rasse sowie Tooltip-Ergänzungen.
- Anleitung für HexerRP-Rassentexte erweitert.

## [0.1.4] - 2026-10-18

### Hinzugefügt

- Explizite Übersetzungsgruppen für beliebige Zeilenindizes in drei Sprachen.
- Separates, versioniertes JSON-Speicherformat mit optionalem Backup.
- Verknüpfungsanzeige, Zuordnen und Lösen; neue Tooltips und Hilfe.
- Keine automatische Übersetzung oder semantische Vermutung.

## [0.1.3] - 2026-10-18

### Hinzugefügt

- Bearbeitbarer dreispaltiger Vergleich deDE/enUS/frFR pro Textzeile.
- Integrierte Hilfe mit F1, Menü und Tooltips.
- README aktualisiert und ausführliches HANDBUCH.md ergänzt.
- Keine Veränderung der konservativen Lua-Speicherlogik aus 0.1.2.

## [0.1.2]

### Geändert

- Kompatibilitätsanpassung und Speichern nur bei echten Änderungen.

## Ambient-Texte (Version 0.1.11)

Neu: `Ambient.lua` und `AmbientRacial.lua` in JaegerRP, PaladinRP und DruidenRP. Die Textverwaltung erkennt die Tabellen als Textpools. Waehle die Textart und bei rassenspezifischen Kategorien die Rasse. Alle Textaenderungen muessen wie bisher gespeichert werden. `*Handlungen*` werden zu `/me`.

## 0.1.12
- Kontextbezogenes **Schlüssel löschen** mit Vorschau für alle vorhandenen Sprachen, Sicherheitsdialog und Backups.
- Entfernt den vollständigen ausgewählten RP-Schlüssel, bewahrt Geschwister- und Elternzweige.
- Mehrdateien-Vorabprüfung und Regressionstests für alle fünf RP-AddOn-Strukturen.
- Handbuch, README und Tooltips ergänzt.
