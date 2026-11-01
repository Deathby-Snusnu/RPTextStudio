# Changelog

Die dokumentierte Historie wird nach Versionen geordnet. Undatierte
Versionen erhalten kein nachträglich angenommenes Release-Datum.

## Aktueller Quellstand: APP_VERSION 1.0.0 (unveröffentlicht)

- KriegerRP als vertrauenswürdige `WARRIOR`-Klassenquelle `Deathby-Snusnu/KriegerRP` in den AddOn-Katalog aufgenommen.
- Der bestehende geschützte Download-, Prüf- und Bestandschutz-Ablauf gilt nach dem Merge des KriegerRP-Repositories auch für das neue AddOn. Katalog-Regressionstest hinzugefügt.
- Der Makro-Generator lehnt passive oder nicht eigenständig wirkbare KriegerRP-Schlüssel wie `TACTICAL_MASTERY` und `DEVASTATE` ausdrücklich ab.

GitHub veröffentlichte zuletzt `v0.2.2` am 28.10.2026. Der Quellstand
dieses Tags und der veröffentlichte Installer weisen intern noch `0.2.1`
aus. Vorhandene Build-Metadaten und Installer bleiben bis zu einem neuen
Build dem älteren Stand zugeordnet.

- Der mitgelieferte AddOn-Katalog enthält MagierRP neben den sechs bisherigen
  AddOns. Fehlende AddOns werden im Anwenderdialog ausdrücklich ausgewählt.
- Titel und Info-Dialog verwenden dieselbe Quellversion.
- Der Paladin-Zauber-Manager bildet GreaterBlessings-Basisschlüssel auf die
  benötigten `GREATER_`-Aufrufschlüssel ab.
- Die lokale AddOn-Übersicht und Versionsprüfung akzeptieren nur eindeutige
  AddOn-IDs aus dem vertrauenswürdigen Katalog.
- Abweichende bestehende Dateien bleiben beim GitHub-Update standardmäßig
  geschützt und können einzeln zur Ersetzung freigegeben werden.
- Der Zauber-Manager berücksichtigt unterstützte Paladin-Segen, Auren,
  Siegel und Fähigkeiten und bildet große Segen auf passende `GREATER_`-
  Aufrufschlüssel ab. MagierRP ist kein Makro-Manager-Ziel.
- Der EXE-Build ermittelt Version und Commit-ID und verlangt eine
  Git-Arbeitskopie ohne Änderungen an verfolgten Dateien.
- Nach `v0.2.2` wurde MagierRP in den vertrauenswürdigen AddOn-Katalog
  aufgenommen; der AddOn-Generator wurde entfernt und seine Magier-
  Textquellen werden im MagierRP-Projekt gepflegt.
- GitHub-API-Anfragen laufen über einen gemeinsamen Request-Manager mit
  Cache, Warteschlange und Rate-Limit-Wiederholungen.
- README, Handbuch und Feature-Anleitungen an den aktuellen Quellstand
  angepasst; historische Einträge bleiben erhalten.

## [0.2.2] - 2026-10-28

### AddOn-Verwaltung

- Geführte Updates bestehender AddOns mit Vorschau und Bestandsschutz
  ergänzt.

### MagierRP

- MagierRP-Unterstützung mit 28 Zaubern, drei Sprachen und dem Befehl
  `/mrp list` ergänzt.

## [0.2.1] - 2026-10-27

### Windows-Paket

- Windows-Build und Installer verwenden nachvollziehbare Versions- und
  Commit-Metadaten; die Build-Vorbereitung und Installationsprüfung wurden
  erweitert.

## [0.2.0] - 2026-10-26

### AddOn-Verwaltung

- Anwenderdialog für erkannte WoW-Installationen, lokale AddOn-Versionen,
  Interface-Profile und GitHub-Versionsprüfungen erweitert.
- Unterstützte AddOns werden anhand eines gepflegten Katalogs gefunden und
  mit ihren Anzeigenamen dargestellt; interne AddOn-IDs bleiben für Aktionen
  maßgeblich.
- Öffentliche GitHub-Repositories können ohne Token geprüft und bereitgestellt
  werden; optionale `GH_TOKEN`- und `GITHUB_TOKEN`-Variablen ermöglichen
  authentifizierte Zugriffe.
- Release-Metadaten und Archive öffentlicher Repositories werden direkt über
  HTTPS abgerufen. Dafür sind weder GitHub-CLI noch Konto erforderlich;
  Downloads werden vor der Installationsvorschau temporär bereitgestellt.
- Geprüfte Pakete lassen sich nach Vorschau und ausdrücklicher Bestätigung
  installieren. Vorhandene Dateien bleiben standardmäßig geschützt; Sicherungen
  und Rücknahme bei Installationsfehlern sind Bestandteil des Ablaufs.
- Fehlende bekannte RP-AddOns können gesammelt vorbereitet und nach gemeinsamer
  Vorschau installiert werden.

### Windows-Paket

- `build_exe.bat` erstellt mit PyInstaller eine einzelne Windows-EXE samt
  Python, Qt und eingebettetem Handbuch.
- Build-Abhängigkeiten separat in `requirements-build.txt`; Projektdateien
  und Backups bleiben extern bearbeitbar.
- Im vollständigen Entwicklungsprojekt starten die Batch-Starter den
  aktuellen Python-Quellstand. Außerhalb davon bevorzugen sie eine vorhandene
  EXE.

### Dokumentation

- README und Handbuch auf den dokumentierten Anwendungsstand 0.2.0 abgestimmt.
- Projektlokale Installation, pytest-Aufruf, Variantenwahl, Manager-Grenzen,
  Modulaufgaben und getrennte Projektregister dokumentiert.
- Historische Funktionsbeschreibungen von der aktuellen Bedienung getrennt.

## [0.1.16] – Strukturen im Arbeitsassistenten

- Integrierter fünfter Schritt zum Erstellen von Rassen, Klassen und
  RP-Zauberschlüsseln.
- Vorschau, Validierung, Vorabtest auf Dateikopien und ausdrückliche
  Schreibfreigabe.
- Bestehende Schlüsselanlage und Rassen-/Klassenregistrierung wiederverwendet.
- Tests und Dokumentation ergänzt; AddOn-Spielerkennung bleibt unverändert.

## [0.1.15] – Integrierter Arbeitsassistent

- F2 öffnet einen breiten Arbeitsdialog mit Schrittliste links und Editor
  rechts.
- Deutsches Original bearbeiten, Übersetzungen manuell oder mit OpenAI
  vorbereiten und einzeln freigeben.
- Optionale RP-Übersetzung über die OpenAI Responses API mit Schutz für
  Platzhalter und `/me`-Markierungen; API-Schlüssel bleiben im Speicher.
- Gesamtvorschau und Validierung vor dem expliziten Speichern mit Backups.
- Alter Navigations-Wizard bleibt separat erreichbar.
- Tests und Handbuch ergänzt; neue Schlüssel weiterhin über die bestehenden
  Manager.

## [0.1.14] – Geführter Workflow-Assistent

- Optionaler Wizard unter Hilfe → Workflow-Assistent (F2).
- Vier geführte Einstiege: Text bearbeiten, Zauber ergänzen,
  KI-Übersetzung, Projektprüfung.
- Kontextprüfung auf geöffnetes Projekt, gewählten Textpool und
  deDE-Ausgangszeile.
- Keine automatischen Schreibvorgänge oder API-Aufrufe; vorhandene Werkzeuge
  bleiben zuständig.
- Dokumentation und Tests der Voraussetzungen ergänzt.

## [0.1.13] – Klassische Desktopnavigation

- Menüleiste Datei / Bearbeiten / Projekt / Übersetzungen / Ansicht / Hilfe.
- Kompakte Symbolleiste für oft verwendete Aktionen und einheitliche
  Tastenkürzel.
- Dauerhafte Statusfelder für Projekt, Navigationssprache, Textauswahl und
  offene Änderungen.
- Bestehende Bearbeitungsfunktionen erhalten; Workflow-Assistent folgt später.
- Dokumentation entsprechend ergänzt.

## [0.1.12]

- Kontextbezogenes **Schlüssel löschen** mit Vorschau für alle vorhandenen
  Sprachen, Sicherheitsdialog und Backups.
- Entfernt den vollständigen ausgewählten RP-Schlüssel, bewahrt Geschwister-
  und Elternzweige.
- Mehrdateien-Vorabprüfung und Regressionstests für alle fünf
  RP-AddOn-Strukturen.
- Handbuch, README und Tooltips ergänzt.

## [0.1.11]

- `Ambient.lua` und `AmbientRacial.lua` in JaegerRP, PaladinRP und DruidenRP
  ergänzt.
- Die Textverwaltung erkennt diese Tabellen als Textpools; rassenspezifische
  Pools lassen sich nach Textart und Rasse auswählen.
- `*Handlungen*` werden als `/me` ausgegeben.

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
