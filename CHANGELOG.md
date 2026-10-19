## 0.1.8 (Startskript-Aktualisierung)
- `Start.bat` richtet `.venv` bei Bedarf ein, aktiviert sie, prüft/installiert `requirements.txt` und startet die Anwendung.
- `start_windows.bat` bleibt als Alias erhalten.
- README und Handbuch um Einrichtung und Fehlersuche erweitert.

## 0.1.5 - 2026-10-19

- Filter fuer Textart und Rasse sowie Tooltip-Ergaenzungen.
- Anleitung fuer HexerRP-Rassentexte erweitert.

# Changelog

## 0.1.4 (2026-10-18)

- Explizite Übersetzungsgruppen für beliebige Zeilenindizes in drei Sprachen.
- Separates, versioniertes JSON-Speicherformat mit optionalem Backup.
- Verknüpfungsanzeige, Zuordnen und Lösen; neue Tooltips und Hilfe.
- Keine automatische Übersetzung oder semantische Vermutung.

# Changelog

## 0.1.3 (2026-10-18)

- Bearbeitbarer dreispaltiger Vergleich deDE/enUS/frFR pro Textzeile.
- Integrierte Hilfe mit F1, Menü und Tooltips.
- README aktualisiert und ausführliches HANDBUCH.md ergänzt.
- Keine Veränderung der konservativen Lua-Speicherlogik aus 0.1.2.

## 0.1.2

- Kompatibilitätsanpassung und Speichern nur bei echten Änderungen.

## 0.1.6 - 2026-10-19
- Dialog zum Anlegen neuer Rassen-, Klassen-, Rassen-Klassen- und allgemeiner Text-/Zauberschlüssel.
- Neue Schlüssel in den vorhandenen DE/EN/FR-Lua-Textdateien, mit Prüfung gegen doppelte und ungültige Namen.
- Unterstützt direkte Textlisten und `ziel`/`gruppe`-Tabellen anhand des bestehenden Dateischemas.
- Testlauf an temporären Kopien, Sicherungen vor Schreibvorgängen, neu geladene Textpools nach Erstellung.
- Tooltips, README und Handbuch erweitert.

## 0.1.7
- Zauber-Manager mit vorhandenen RP-Schlüsseln, Zuordnung lokalisierter Zaubernamen und Makro-Vorschau.
- Projektbezogene JSON-Speicherung samt Backup, Hilfetexte und Tests.
- Keine automatische Cast-/Spell-ID-Erkennung oder Änderung an AddOn-Core-Dateien.

## 0.1.8 · 2026-10-19
- Rassen- und Klassen-Manager mit Name, ID, Sprachstil und Projektregister.
- Optionale Lua-Textzweige in vorhandenen Racial.lua / Classes.lua, mit Vorabprüfung und Backups.
- Tooltips, Hilfetexte, Dokumentation und zusätzliche Unit-Tests.
- Keine Änderung der AddOn-Laufzeit oder der vom Spiel unterstützten Rassen/Klassen.
