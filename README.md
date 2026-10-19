# RP Text Studio 0.1.9

Python-/PySide6-Desktopeditor für die RP-Textpools der AddOns **RPChatMod, HexerRP, PaladinRP, JaegerRP und DruidenRP**.

## Installation (Windows)

**Empfohlen:** `Start.bat` doppelklicken. Das Skript erstellt bei Bedarf `.venv`, aktiviert die Umgebung, installiert bzw. prüft `requirements.txt` mit pip und startet `main.py`. Bei weiteren Starts wird `.venv` wiederverwendet. `start_windows.bat` ruft denselben Starter auf. Python 3.11 bis 3.13 muss bereits installiert sein und über den Python Launcher `py` oder `python` erreichbar sein. Bei einem Fehler bleibt das Fenster zur Diagnose geöffnet.


```powershell
py -m pip install -r requirements.txt
py main.py
```

Alternativ `Start.bat` verwenden. `start_windows.bat` ist ein kompatibler Alias. Vorausgesetzt wird Python 3.11–3.13.

## Einstieg

1. Über **Projektordner öffnen** die AddOn-Sammlung laden oder über **ZIP als Projekt entpacken** eine ZIP in einen leeren Arbeitsordner importieren.
2. AddOn und Navigationssprache auswählen, im Textpool-Baum einen Eintrag und danach eine Textzeile markieren.
3. Rechts den Text bearbeiten oder unten Deutsch, Englisch und Französisch parallel vergleichen/bearbeiten.
4. **Alles prüfen**, dann **Änderungen speichern**. Der Editor legt Sicherungen als `.bak` an.

**Hilfe:** Über das Menü **Hilfe > Bedienungsanleitung** oder **F1** wird `HANDBUCH.md` im Programm angezeigt. Kurze Hinweise erscheinen als Tooltips an den Bedienelementen.

## Übersetzungszuordnung (überarbeitet in 0.1.9)

- Explizite Übersetzungsgruppen für unterschiedliche Zeilenpositionen in deDE/enUS/frFR.
- „Gespeicherte Verknüpfung anzeigen“ nutzt ausschließlich bestätigte Zuordnungen, keine automatischen Vermutungen.
- Textvarianten per Dropdown mit sofortiger Vorschau auswählen und dann „Diese Texte verknüpfen“ anklicken.
- Mit „Zuordnung lösen“ die Gruppe entfernen, ohne den RP-Text zu löschen.
- Zuordnungen werden getrennt in `.rptextstudio-translations.json` im Projektordner gespeichert. Lua-Dateien bleiben kompatibel.
- Alte oder nicht mehr eindeutig auffindbare Referenzen gelten als nicht zugeordnet, statt falsche Übersetzungen anzuzeigen.

## Version 0.1.3

- Dreispaltige, bearbeitbare Ansicht für `deDE`, `enUS`, `frFR` zum ausgewählten Textpool und Zeilenindex.
- Keine automatische Zuordnung von Übersetzungen: Zufallsvarianten können je Sprache unterschiedlich sortiert sein. Fehlende Zeilen bleiben im Vergleich deaktiviert.
- Integrierte Hilfe (F1), Tooltips, erweitertes Handbuch.
- Vorhandene Funktionen für Bearbeitung, Suche, Prüfung, Sicherung und selektives Speichern bleiben erhalten.

## Textformat und Grenzen

- `*Handlung*` kennzeichnet `/me`; gewöhnlicher Text `/say`.
- `%s` = Ziel, `%p` = Begleiter/Dämon.
- Nur wörtliche Stringlisten in `*/locales/{deDE,enUS,frFR}/*.lua` werden bearbeitet. `Expansion.lua`, Core/Config/TOC sowie dynamische Lua-Ausdrücke bleiben ausgenommen.
- Bei Änderungen einer Stringliste gehen Kommentare **innerhalb** der Liste möglicherweise verloren. Nicht bearbeitete Listen und übrige Dateibereiche werden beibehalten.
- **Alles prüfen** ersetzt keinen vollständigen Lua-Syntaxtest und keinen Spieltest.
- Kein fertiges Windows-EXE und keine automatische Übersetzung.

Detaillierte Arbeitsschritte, Einschränkungen und Fehlerbehebung stehen in [HANDBUCH.md](HANDBUCH.md).

## Tests

Im Ordner `RPTextStudio` mit der projektlokalen Python-Umgebung ausführen.
Voraussetzung ist, dass `pytest` in dieser Umgebung installiert ist; es ist
nicht in den Laufzeitabhängigkeiten aus `requirements.txt` enthalten.

```powershell
.\.venv\Scripts\python.exe -m pytest tests -v
```

Pytest kann die vorhandenen `unittest.TestCase`-Tests ohne Umschreiben ausführen.
Die Parser-/Speichertests und Python-Kompilierung können automatisiert ausgeführt werden. Die GUI ist auf einem Windows-System mit installiertem PySide6 zu testen.

### Neu in 0.1.5

Textart- und Rassenfilter zur getrennten Pflege allgemeiner Texte, Rassentexte und Ambient-Pools. Passend zu HexerRP 0.3.0.

## Version 0.1.6: Schlüsselverwaltung

Über **Neuen Schlüssel anlegen** lassen sich neue Zauber-/Aktionsschlüssel in bestehenden Lua-Texttabellen erzeugen:

- **Rasse** in `Racial.lua`, beispielsweise `Gnome / CURSE_RECKLESSNESS`.
- **Klasse** in `Classes.lua`, beispielsweise `WARLOCK / HELLO` (falls das AddOn diese Datei hat).
- **Rasse + Klasse** in `RaceClass.lua`, beispielsweise `Dwarf / PALADIN / HELLO` (falls vorhanden).
- **Allgemein** in `Texts.lua` (falls vorhanden).

Der Editor erstellt die Schlüssel in allen vorhandenen Sprachdateien dieser Art und prüft die Änderungen vorab an temporären Kopien. Bestehende Dateien werden vor jeder Änderung gesichert. Je nach vorhandenem Schema schreibt er entweder direkte Textlisten oder `ziel`/`gruppe`-Listen. Neu erzeugte Texte heißen zunächst `Neuer RP-Text` und sind vor Verwendung anzupassen.

**Wichtig:** Das Anlegen eines Schlüssels erzeugt **keine neue Zaubererkennung**. Ob der Schlüssel im Spiel aufgerufen wird, hängt von den vorhandenen Event-, Makro- und Spell-Mappings des betreffenden AddOns ab. Auch Rassen- und Klassen-IDs müssen den tatsächlich vom AddOn erwarteten IDs entsprechen. Bestehende Dateien und deren Strukturen werden nicht pauschal geändert.

## Zauber-Manager (0.1.7)

Über **Zauber-Manager** lassen sich vorhandene RP-Schlüssel für die AddOns
HexerRP, PaladinRP, JaegerRP und DruidenRP anzeigen und mit einem WoW-Zaubernamen
verknüpfen. Nur Schlüssel, die in geladenen Textlisten vorkommen, werden angeboten.

1. Projektordner mit AddOns öffnen.
2. **Zauber-Manager** anklicken und AddOn auswählen.
3. Den **exakten Zaubernamen in der Sprache des Spielclients** eingeben.
4. Den RP-Schlüssel wählen und **Zuordnung hinzufügen** klicken.
5. Das erzeugte Makro mit **Makro kopieren** in die Zwischenablage übernehmen
   und im Spiel im Makrofenster einfügen.
6. Über **Zuordnungen speichern** die Liste projektlokal ablegen.

**Wichtig:** Dies ist ein Makro-Assistent, **keine automatische Spell-ID-Erkennung**.
Die Speicherung in `.rptextstudio-spells.json` hat keinerlei Wirkung im Spiel, solange
nicht das entsprechende Makro benutzt wird. Die Core-Dateien der AddOns werden nicht
verändert. Ein Makro löst `/cast` und dann den RP-Slash-Befehl aus; die RP-Ausgabe
belegt **keinen erfolgreichen Zaubertreffer**. Chatbeschränkungen, Cooldowns und
Würfelchance gelten weiter. Bei veränderten Textschlüsseln die Zuordnung erneut prüfen.
Vor einem Überschreiben der Zuordnungsdatei entsteht `.bak`.

### Neu in 0.1.8: Rassen- und Klassen-Manager

Über **Rassen-/Klassen-Manager** neue redaktionelle Profile mit Anzeigenamen, interner ID und RP-Sprachstil anlegen. Beispiel: `Nachtelf` / `NightElf` / `Naturverbunden, geheimnisvoll, traditionsbewusst`. Das neue Projektregister `.rptextstudio-races-classes.json` hält diese Metadaten unabhängig von den WoW-Dateien. Optional wird in vorhandenen `Racial.lua` oder `Classes.lua` des gewählten AddOns in allen verfügbaren Sprachen ein neuer Textzweig mit `RP_GREETING` erstellt. Eingaben werden validiert; vor Lua-Änderungen erfolgen Testläufe auf temporären Kopien und Backups.

**Kein Runtime-Patch:** Das Programm macht keine Rassen/Klassen spielbar und passt die Rassen-/Klassen-Erkennung im AddOn nicht automatisch an. ID-Schreibweise und Core-Handler müssen gesondert geprüft werden. Details siehe `HANDBUCH.md`.

### Verbesserungen in 0.1.9

- Textauswahl erfolgt über Dropdowns mit Nummer und Satzanfang statt unklarer Nummernfelder.
- Die gewählte Variante erscheint sofort und ist genau die Variante, die in der jeweiligen Spalte bearbeitet wird.
- Andere Sprachen starten ohne Auswahl; keine versehentliche Verbindung gleicher Indizes.
- Verknüpfung erfordert mindestens zwei Sprachvarianten und lehnt Konflikte vollständig ab.
- Für die Lua-Dateien ändert sich nichts; gespeichert wird die Zuordnung separat.

### Sprachvergleich (ab 0.1.10)

Wähle links einen Textpool. Der Editor zeigt dieselbe Kategorie aus deDE, enUS und frFR an, auch wenn die zugrunde liegenden Lua-Schlüssel unterschiedliche Sprachteile enthalten. Wähle pro Sprache eine Variante im Dropdown und verbinde mindestens zwei Sprachen mit „Diese Texte verknüpfen“. Änderungen am Text werden stets im richtigen Sprachpool gespeichert.
