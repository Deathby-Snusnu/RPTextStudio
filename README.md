# RP Text Studio 0.1.16

![RP Text Studio – Texte gestalten. Welten erzählen.](assets/rp_text_studio_logo.svg)

Python-/PySide6-Desktopeditor für die RP-Textpools der AddOns **RPChatMod, HexerRP, PaladinRP, JaegerRP und DruidenRP**.

## Dokumentation

[Sammlungsübersicht](../../README.md) · [Bedienungsanleitung](../../docs/RPTextStudio/HANDBUCH.md) ·
[Changelog](CHANGELOG.md) · [Verpackung](../../docs/VERPACKUNG.md)

Der Editor liegt unter `apps\RPTextStudio`, die sechs AddOns unter `addons`.
Beim Öffnen sind sowohl der Projektstamm als auch dessen `addons`-Ordner
möglich. Entpackte Installations-ZIPs mit direkten AddOn-Unterordnern bleiben
unterstützt. Editor-Register werden im jeweiligen Projekt unter `data` gespeichert.
Alte Register direkt im Projektstamm werden weiterhin gelesen, solange
keine neuere Fassung in `data` existiert; beim Speichern entsteht die
kanonische Datei in `data`, ohne das Original zu entfernen.
Vorhandene EXEs wurden beim Umzug erhalten, aber nicht neu gebaut.
Für den aktuellen Quellstand Python direkt verwenden oder die EXE neu bauen.

## Windows-Setup (neu, derzeit Draft)

Ein reguläres Windows-Setup mit Startmenü, optionaler Desktopverknüpfung und Deinstallation lässt sich mit `build_installer.bat` erzeugen. Dazu werden Python und Inno Setup 6 benötigt. Das Paket wird unter `installer-dist/` abgelegt. Die vorgesehene Setup-Version `0.2.0` ist bis zur Release-Freigabe vorläufig. Details und manuelle Abnahmeschritte stehen in [WINDOWS-INSTALLER.md](WINDOWS-INSTALLER.md). Das Setup installiert ausschließlich den Editor, keine WoW-AddOns. Der Build wurde bisher nicht auf Windows ausgeführt.

## Installation (Windows)

**Ohne Python auf dem Zielrechner:** Mit `build_exe.bat` lässt sich auf einem
Windows-Rechner mit Python eine einzelne `dist\RPTextStudio.exe` erstellen.
Sie enthält Python, Qt und das Handbuch und kann ohne die Python-Ordnerstruktur
weitergegeben werden. Die bearbeiteten AddOn-Dateien bleiben separat und
werden über **Projektordner öffnen** geladen.
Build-Anleitung, Schreibrechte und Hinweise zur Weitergabe:
[Windows-EXE bauen](../../docs/RPTextStudio/HANDBUCH.md#windows-exe-bauen).
Im vollständigen Entwicklungsprojekt startet `Start.bat` immer den aktuellen
Python-Quellstand, damit eine alte EXE keine veralteten Pfade verwendet.
Außerhalb dieser Struktur bevorzugt der Starter eine vorhandene
`RPTextStudio.exe` im Editor-Ordner, danach `dist\RPTextStudio.exe`.

**Voraussetzungen:** Windows, Python und die Laufzeitabhängigkeit
`PySide6>=6.8,<7` aus [requirements.txt](requirements.txt). Der bisher
dokumentierte Python-Bereich ist 3.11–3.13; eine vollständig ausgeführte
Testmatrix für diese Versionen ist nicht nachgewiesen.

**Automatischer Python-Start:** [Start.bat](Start.bat) doppelklicken. Das Skript
verwendet im vollständigen Projekt die gemeinsame `.venv` im Projektstamm,
erstellt sie bei Bedarf und installiert `requirements.txt` nur bei fehlendem
PySide6. Außerhalb dieser Struktur wird eine lokale `.venv` verwendet.
Anschließend startet es `main.py`. [start_windows.bat](start_windows.bat)
ist ein Alias. Python muss über `py` oder `python` erreichbar sein.
`py -3` wählt die verfügbare Python-3-Installation, nicht ausdrücklich eine
Version aus dem oben genannten Bereich. Bei Fehlern bleibt das Fenster offen.

**Manuelle Einrichtung:** PowerShell im Projektstamm öffnen.
Beispiel mit installiertem Python 3.13:

```powershell
py -3.13 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r apps\RPTextStudio\requirements.txt
.\.venv\Scripts\python.exe apps\RPTextStudio\main.py .
```

Die Umgebung nur erstellen, wenn noch keine passende `.venv` existiert.
Bei bereits installierten Abhängigkeiten kann der letzte Befehl den Editor
ohne den pip-Schritt des Starters öffnen. Es wird keine Aktivierung der
Umgebung und keine Änderung der PowerShell-Ausführungsrichtlinie benötigt.
Der Anwendungsfenstertitel zeigt Version `0.1.13`. Das Startskript wurde in diesem UI-Branch nicht verändert.

## Einstieg

1. Über **Projektordner öffnen** die AddOn-Sammlung laden oder über **ZIP als Projekt entpacken** eine ZIP in einen leeren Arbeitsordner importieren.
2. AddOn und Navigationssprache auswählen, im Textpool-Baum einen Eintrag und danach eine Textzeile markieren.
3. Rechts den Text bearbeiten oder unten Deutsch, Englisch und Französisch parallel vergleichen/bearbeiten.
4. **Alles prüfen**, dann **Änderungen speichern**. Der Editor legt Sicherungen als `.bak` an.

**Hilfe:** Über das Menü **Hilfe > Bedienungsanleitung** oder **F1** wird das [Handbuch](../../docs/RPTextStudio/HANDBUCH.md) im Programm angezeigt. Beim EXE-Build wird es eingebettet. Kurze Hinweise erscheinen als Tooltips an den Bedienelementen.

## Übersetzungszuordnung

- Explizite Übersetzungsgruppen für unterschiedliche Zeilenpositionen in deDE/enUS/frFR.
- „Gespeicherte Verknüpfung anzeigen“ nutzt ausschließlich bestätigte Zuordnungen, keine automatischen Vermutungen.
- Textvarianten per Dropdown mit sofortiger Vorschau auswählen und dann „Diese Texte verknüpfen“ anklicken.
- Mit „Zuordnung lösen“ die Gruppe entfernen, ohne den RP-Text zu löschen.
- Zuordnungen werden getrennt in `data\.rptextstudio-translations.json` im Projekt gespeichert. Lua-Dateien bleiben kompatibel.
- Alte oder nicht mehr eindeutig auffindbare Referenzen gelten als nicht zugeordnet, statt falsche Übersetzungen anzuzeigen.

## Sprachvergleich

- Dreispaltige, bearbeitbare Ansicht für `deDE`, `enUS`, `frFR` zum ausgewählten Textpool.
- Varianten pro Sprache ausdrücklich über das Dropdown wählen; gleiche Zeilenindizes werden nicht automatisch verknüpft.
- Die Sprachsegmente der Lua-Schlüssel werden seit `0.1.10` beim Lesen und Speichern auf die jeweilige Sprache angepasst.
- Integrierte Hilfe (F1), Tooltips, erweitertes Handbuch.

## Textformat und Grenzen

- `*Handlung*` kennzeichnet `/me`; gewöhnlicher Text wird in der Vorschau als `/say` gezeigt. Im Spiel gilt der konfigurierte Sprachkanal.
- `%s` = aufgelöster Name, `%p` = Begleiter/Dämon in HexerRP. Die tatsächliche Ersetzung hängt vom AddOn ab.
- Nur wörtliche Stringlisten in `*/locales/{deDE,enUS,frFR}/*.lua` werden bearbeitet. `Expansion.lua`, Core/Config/TOC sowie dynamische Lua-Ausdrücke bleiben ausgenommen.
- Bei Änderungen einer Stringliste gehen Kommentare **innerhalb** der Liste möglicherweise verloren. Nicht bearbeitete Listen und übrige Dateibereiche werden beibehalten.
- **Alles prüfen** ersetzt keinen vollständigen Lua-Syntaxtest und keinen Spieltest.
- Windows-EXE über `build_exe.bat` selbst erstellbar; keine automatische Übersetzung.

Detaillierte Arbeitsschritte, Einschränkungen und Fehlerbehebung stehen im [Handbuch](../../docs/RPTextStudio/HANDBUCH.md).

## Tests

Im Projektstamm mit der gemeinsamen Python-Umgebung ausführen.
`pytest` ist eine zusätzliche Testabhängigkeit und nicht in den
Laufzeitabhängigkeiten aus `requirements.txt` enthalten. Bei Bedarf einmalig
in der projektlokalen Umgebung installieren:

```powershell
.\.venv\Scripts\python.exe -m pip install pytest
```

```powershell
.\.venv\Scripts\python.exe -m pytest apps\RPTextStudio\tests -v
```

Pytest führt auch die vorhandenen `unittest.TestCase`-Tests aus; die
Testimplementierung muss dafür nicht umgeschrieben werden. Die Tests decken
Parser/Speichern, Schlüsselverwaltung, Rassendateien, Sprachvergleich,
Übersetzungsgruppen und beide Manager ab. GUI-Interaktionen und das Verhalten
im WoW-Client sind zusätzlich manuell zu prüfen. Tests fehlen im Installations-ZIP.
Auf übersprungene Tests achten: Ein erfolgreicher pytest-Lauf bedeutet nicht,
dass jede GUI-/Sprachvergleichsprüfung tatsächlich ausgeführt wurde.

## Filter

Textart- und Rassenfilter trennen allgemeine Texte, Rassentexte und
Ambient-Pools. **Alle Textarten** zeigt auch andere Dateien, etwa
Paladin-Segen oder die sozialen RPChatMod-Kategorien. **Allgemein (Texts.lua)**
filtert dagegen ausschließlich auf Dateien dieses Namens.

## Schlüsselverwaltung

Über **Neuen Schlüssel anlegen** lassen sich neue Zauber-/Aktionsschlüssel in bestehenden Lua-Texttabellen erzeugen:

- **Rasse** in `Racial.lua`, beispielsweise `Gnome / CURSE_RECKLESSNESS`.
- **Klasse** in `Classes.lua`, beispielsweise `WARLOCK / HELLO` (falls das AddOn diese Datei hat).
- **Rasse + Klasse** in `RaceClass.lua`, beispielsweise `Dwarf / PALADIN / HELLO` (falls vorhanden).
- **Allgemein** in `Texts.lua` (falls vorhanden).

Der Editor erstellt die Schlüssel in allen vorhandenen Sprachdateien dieser Art und prüft die Änderungen vorab an temporären Kopien. Bestehende Dateien werden vor jeder Änderung gesichert. Je nach vorhandenem Schema schreibt er entweder direkte Textlisten oder `ziel`/`gruppe`-Listen. Neu erzeugte Texte heißen zunächst `Neuer RP-Text` und sind vor Verwendung anzupassen.
Die Strukturerstellung schreibt bereits beim Bestätigen des Dialogs in die
Lua-Dateien. Anschließende Textbearbeitungen werden erst mit
**Änderungen speichern** geschrieben.

**Wichtig:** Das Anlegen eines Schlüssels erzeugt **keine neue Zaubererkennung**.
Die Klassen-AddOns werden manuell per Slash-Befehl oder `TryText` aufgerufen.
Ob ein neuer Schlüssel nutzbar ist, hängt zusätzlich von der vorhandenen
Poolauswahl ab. Rassen- und Klassen-IDs müssen zu den vom AddOn erwarteten IDs
passen. Der Editor ändert weder Core-Handler noch TOCs und erzeugt keine
fehlenden Sprachdateien.

## Zauber-Manager

Über **Zauber-Manager** lassen sich vorhandene RP-Schlüssel für die AddOns
HexerRP, PaladinRP, JaegerRP und DruidenRP mit einem WoW-Zaubernamen
verknüpfen. Angeboten werden aus geladenen `Texts.lua`, `Racial.lua`,
`Classes.lua` und `RaceClass.lua` ermittelte Schlüssel. Andere Kategorien,
etwa reine Paladin-Segen aus `Blessings.lua`, werden derzeit nicht generell
erfasst; der Dialog ist keine vollständige Laufzeit-Schlüsselliste.

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

## Rassen- und Klassen-Manager

Über **Rassen-/Klassen-Manager** neue redaktionelle Profile mit Anzeigenamen, interner ID und RP-Sprachstil anlegen. Beispiel: `Nachtelf` / `NightElf` / `Naturverbunden, geheimnisvoll, traditionsbewusst`. Das neue Projektregister `.rptextstudio-races-classes.json` hält diese Metadaten unabhängig von den WoW-Dateien. Optional wird in vorhandenen `Racial.lua` oder `Classes.lua` des gewählten AddOns in allen verfügbaren Sprachen ein neuer Textzweig mit `RP_GREETING` erstellt. Eingaben werden validiert; vor Lua-Änderungen erfolgen Testläufe auf temporären Kopien und Backups.

**Kein Runtime-Patch:** Das Programm macht keine Rassen/Klassen spielbar und passt die Rassen-/Klassen-Erkennung im AddOn nicht automatisch an. ID-Schreibweise und Core-Handler müssen gesondert geprüft werden. Details siehe [Handbuch](../../docs/RPTextStudio/HANDBUCH.md).

## Projektdateien und Sicherungen

| Datei | Inhalt | Wirkung im Spiel |
| --- | --- | --- |
| `data\.rptextstudio-translations.json` | Explizite Übersetzungsgruppen | Keine |
| `data\.rptextstudio-spells.json` | Zauber-/Schlüsselzuordnungen für Makros | Erst durch Nutzung des erzeugten Makros |
| `data\.rptextstudio-races-classes.json` | Redaktionelle Rassen-/Klassenprofile | Keine; optionale Lua-Zweige sind separat |

Die Register liegen unter `data` im geöffneten Projekt, nicht zwingend neben dem
Editor. Bei Auswahl von `addons` im vollständigen Quellprojekt wird dafür
der übergeordnete Projektstamm verwendet. Installationspakete lassen diese
Register aus; bei einem Projektumzug den gesamten `data`-Ordner mitnehmen.
Lua-Sicherungen tragen einen Zeitstempel vor `.bak`; JSON-Sicherungen
verwenden den Namen der jeweiligen Datei mit zusätzlichem `.bak`.
Zusammenhängende Änderungen über mehrere Dateien sind nicht atomar.

## Module

| Modul | Zuständigkeit |
| --- | --- |
| [main.py](main.py) | GUI, Projekt-/ZIP-Öffnen, Filter, Sprachvergleich und Speichervorgänge |
| [project_paths.py](project_paths.py) | Projekt-/AddOn-Wurzeln, Metadaten- und Handbuchpfade |
| [lua_text.py](lua_text.py) | Statischer Lua-Listenparser, Validierung, gezieltes Schreiben und Sicherungen |
| [key_creation.py](key_creation.py) | Neue Schlüssel in bestehenden statischen Texttabellen |
| [translation_links.py](translation_links.py) | Sprachübergreifende Poolkennungen, Textreferenzen und JSON-Speicherung |
| [spell_manager.py](spell_manager.py) | Schlüsselvorschläge, Makroerzeugung und Zuordnungsregister |
| [race_class_manager.py](race_class_manager.py) | Profilregister und optionale Lua-Textzweige |

## Lizenz

Der Editor steht laut [LICENSE](LICENSE) unter **MPL-2.0**.
Die Lizenz der bearbeiteten RP-Texte wird dadurch nicht geändert; für die
AddOn-Textdaten gelten die jeweiligen Lizenz- und SPDX-Hinweise.

## Ambient-Texte (Version 0.1.11)

Neu: `Ambient.lua` und `AmbientRacial.lua` in JaegerRP, PaladinRP und DruidenRP. Die Textverwaltung erkennt die Tabellen als Textpools. Waehle die Textart und bei rassenspezifischen Kategorien die Rasse. Alle Textaenderungen muessen wie bisher gespeichert werden. `*Handlungen*` werden zu `/me`.

### Falsch angelegte Schlüssel entfernen (0.1.12)

Gewünschten Textpool auswählen und **Schlüssel löschen** anklicken. Vor dem Löschen wird die Liste der betroffenen Sprachdateien gezeigt und eine Bestätigung verlangt. Es werden nur die Texte des gewählten Schlüssels (inklusive `ziel`/`gruppe`), nicht der übergeordnete Rassen-/Klassenzweig gelöscht. Alle geänderten Lua-Dateien erhalten ein `.bak`-Backup. Makro- und Übersetzungsmetadaten bei Bedarf separat prüfen. Siehe `HANDBUCH.md`.

## KI-Übersetzung mit OpenAI (Feature-Branch)

Im Sprachvergleich einen **deutschen** Text auswählen und **KI-Übersetzung …** anklicken. In dem Dialog einen eigenen OpenAI API-Key eingeben oder `OPENAI_API_KEY` als Umgebungsvariable setzen; Modell und RP-Stil können angepasst werden. Erst **Vorschläge erzeugen** sendet Originaltext, AddOn, Rasse und Stil über die OpenAI Responses API an den Dienst (API-Nutzung kann Kosten verursachen).

Die Vorschläge für `enUS` und `frFR` werden zunächst nur angezeigt. Sie können korrigiert und **einzeln freigegeben** werden. Der Editor prüft dabei `%s`, `%p`, `%%`, `*...*` und Zeilenumbrüche. Erst nach Freigabe werden Varianten in die vorhandenen Sprachpools übernommen und dem deutschen Text zugeordnet. Bestehende Sprachvarianten werden **nicht überschrieben**. Abschließend **Änderungen speichern** wählen, um Lua-Änderungen und Übersetzungsverknüpfungen mit Backups zu sichern.

**Sicherheit und Grenzen:** API-Schlüssel werden nicht in Projektdateien gespeichert. Es gibt keine automatische Stapelverarbeitung. Zielsprach-Textpools müssen schon existieren. Ein vorhandener Übersetzungslink wird nicht automatisch geändert. Es fand noch kein echter API- oder Windows-GUI-Test statt; der API-Test nutzt ein Mock.

## Klassische Menüführung (0.1.13)

Die Anwendung nutzt jetzt die Menüleiste **Datei, Bearbeiten, Projekt, Übersetzungen, Ansicht, Hilfe** und eine kompakte Standardsymbolleiste. Die wichtigsten Kürzel: **Strg+O** Projekt öffnen, **Strg+S** speichern, **Strg+N** Text hinzufügen, **Strg+D** duplizieren, **Strg+F** Suche fokussieren, **F7** Projekt prüfen, **F1** Handbuch.

Unten zeigt die dauerhafte Statusleiste Projekt, Navigationssprache, ausgewählte Textzeile und ungespeicherte Textpool-/Verknüpfungsänderungen. Die bisherigen Texteditoren, Sprachvergleiche und Prüfungen bleiben erhalten. Der optionale Workflow-Assistent und eine projektweite Rückgängig-Funktion sind **nicht** Bestandteil dieser Version; sie sind für Folgeversionen vorgesehen.

## Geführter Workflow-Assistent (0.1.14)

Über **Hilfe → Workflow-Assistent…** oder **F2** startet ein dreistufiger Assistent. Er bietet **Text bearbeiten**, **Zauber ergänzen**, **KI-Übersetzung** und **Projekt prüfen**. Der Dialog beschreibt Voraussetzungen (geöffnetes Projekt, markierter Textpool, markierte Textzeile und bei KI-Übersetzung `deDE`). Nach **Fertigstellen** wird das entsprechende bestehende Werkzeug geöffnet. Es erfolgen **keine automatischen Schreibvorgänge** und **keine API-Anfragen**, bis du diese Aktionen im jeweiligen Werkzeug ausdrücklich auslöst.

Hinweis: Der Assistent ist bewusst eine geführte Navigation. Ein vollständig transaktionaler Mehrschritt-Assistent und die Rassen-/Klassen-Neuanlage innerhalb desselben Dialogs bleiben Folgeschritte.

## Arbeitsassistent mit Schrittnavigation (0.1.15)

Der neue **große Arbeitsassistent** startet über **Hilfe → Arbeitsassistent…** oder **F2**. Links befinden sich die Schritte **Text auswählen**, **Original bearbeiten**, **Übersetzen**, **Prüfen & speichern**. Rechts bleibt der jeweilige Editor sichtbar; die Eingaben werden zwischen den Schritten als Entwurf erhalten.

1. Projekt laden und vorhandene Änderungen speichern.
2. Assistent aufrufen, deutschen Textpool und Ausgangszeile auswählen.
3. Original bearbeiten, bei Bedarf OpenAI-Vorschläge für `enUS` und `frFR` erzeugen und einzeln freigeben.
4. Prüfbericht lesen und **Prüfen und speichern** bestätigen. Erst dann werden Lua-Dateien und Übersetzungsverknüpfungen über die vorhandene Speicherlogik geschrieben (mit Backups).

Ohne API-Schlüssel können Übersetzungen manuell eingetragen werden. Fehlerhafte `%s`/`%p`/`%%`-Platzhalter oder Emote-Markierungen werden nicht übernommen. Bereits bestehende Links werden nicht ersetzt. Zielsprachpools müssen vorhanden sein. Der frühere einfache Navigationsassistent steht über **Hilfe → Einfacher Assistent…** weiterhin zur Verfügung.

**Noch nicht enthalten:** Vollständig neue Zauber- und Rassenstrukturen innerhalb dieses Dialogs; diese werden bis auf Weiteres über die vorhandenen Manager angelegt. Ein Windows-GUI-Test ist noch erforderlich.

## Arbeitsassistent: neue Strukturen anlegen (0.1.16)

Der mit **F2** erreichbare große Arbeitsassistent enthält zusätzlich **Strukturen anlegen**. Hier lassen sich neue **allgemeine, rassen- und klassenbezogene Zauberschlüssel** oder **Rassen-/Klassenprofile** vorbereiten. Ein Profil kann wahlweise nur das Projektregister erweitern oder zusätzlich vorhandene unterstützte `Racial.lua`-/`Classes.lua`-Sprachdateien ergänzen.

Die Vorschau prüft Kennungen, vorhandene Dateien, eindeutige Lua-Root-Strukturen und doppelte Einträge auf temporären Kopien. Erst **Struktur prüfen und anlegen** plus eine weitere Bestätigung verändern Dateien; Lua-Dateien erhalten Backups. Danach wird das Projekt neu geladen, damit neue Schlüssel im Texteditor sichtbar sind.

**Grenzen:** Neue Schlüssel sind reine RP-Textdaten. Die Zauber- oder Rassenerkennung im laufenden WoW-AddOn wird dadurch nicht automatisch erweitert. Für vorhandene Texte und Übersetzungen gelten weiterhin die getrennten Schritte **Text auswählen → Bearbeiten → Übersetzen → Prüfen & speichern**.
