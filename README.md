# RP Text Studio 1.0.0 (Quellstand, unveröffentlicht)

![RP Text Studio – Texte gestalten. Welten erzählen.](assets/rp_text_studio_logo.svg)

Python-/PySide6-Desktopeditor für statische RP-Textpools, unter anderem von
**RPChatMod, HexerRP, PaladinRP, JaegerRP, DruidenRP und MagierRP**.
RPControlCenter enthält keine entsprechenden Textpools.

## Dokumentation

[Sammlungsübersicht](https://github.com/Deathby-Snusnu/RPAddOns/blob/main/README.md) · [Bedienungsanleitung](https://github.com/Deathby-Snusnu/RPAddOns/blob/main/docs/RPTextStudio/HANDBUCH.md) ·
[Changelog](CHANGELOG.md) · [Verpackung](https://github.com/Deathby-Snusnu/RPAddOns/blob/main/docs/VERPACKUNG.md)

Weitere Anleitungen: [Anwender-Modus](ANWENDER-ADDON-MODUS.md),
[Erstinstallation](FIRST-INSTALL-RP-ADDONS.md),
[sichere Updates](SAFE-GITHUB-INSTALL.md), [GitHub-Staging](GITHUB-STAGING.md),
[Client-Profile](WOW-CLIENT-PROFILE.md), [Text-Merge-Vorschau](RP-TEXT-MERGE.md)
und [Windows-Installer](WINDOWS-INSTALLER.md).

Der Editor liegt unter `apps\RPTextStudio`, die sieben AddOns des aktuellen
Arbeitsstands unter `addons`.
Beim Öffnen sind sowohl der Projektstamm als auch dessen `addons`-Ordner
möglich. Entpackte Installations-ZIPs mit direkten AddOn-Unterordnern bleiben
unterstützt. Die drei Text-, Zauber- und Profilregister werden im jeweiligen
Projekt unter `data` gespeichert. Ihre älteren Fassungen direkt im
Projektstamm werden weiterhin gelesen, solange keine neuere Fassung in
`data` existiert; beim Speichern entsteht die kanonische Datei in `data`,
ohne das Original zu entfernen. Das optionale AddOn-Register `addons.json`
liegt dagegen im Projektstamm und ist vom mitgelieferten Katalog getrennt.
Vorhandene EXEs wurden beim Umzug erhalten, aber nicht neu gebaut.
Für den aktuellen Quellstand Python direkt verwenden oder die EXE neu bauen.
Die oben verlinkten gemeinsamen Handbücher liegen außerhalb des
Editor-Repositories und setzen den vollständigen Sammlungs-Checkout voraus;
sie stehen auch im
[Sammlungsrepository](https://github.com/Deathby-Snusnu/RPAddOns).
Ein einzelner Editor-Checkout benötigt für den EXE-Build ein `HANDBUCH.md`
neben dem Build-Skript oder das Handbuch an der gemeinsamen Projektposition.

## Windows-Setup

Ein Windows-Setup mit Startmenü, optionaler Desktopverknüpfung und
Deinstallation lässt sich mit `build_installer.bat` erzeugen. Dazu werden
Python, Git und Inno Setup 6 benötigt. Das Paket wird unter `installer-dist/`
abgelegt und installiert ausschließlich den Editor, keine WoW-AddOns.
Build-Voraussetzungen und manuelle Abnahmeschritte stehen in
[WINDOWS-INSTALLER.md](WINDOWS-INSTALLER.md). Ein aktueller Windows-Abnahmestand
oder eine Installer-Freigabe wird dadurch nicht belegt.

## Installation (Windows)

**Ohne Python auf dem Zielrechner:** Mit `build_exe.bat` lässt sich auf einem
Windows-Rechner mit Python eine einzelne `dist\RPTextStudio.exe` erstellen.
Sie enthält Python, Qt und das Handbuch und kann ohne die Python-Ordnerstruktur
weitergegeben werden. Die bearbeiteten AddOn-Dateien bleiben separat und
werden über **Projektordner öffnen** geladen.
Der Build benötigt außerdem Git und eine Arbeitskopie ohne Änderungen an
verfolgten Dateien. Build-Anleitung, Schreibrechte und Hinweise zur Weitergabe:
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
Die Versionskonstante in [app_build_info.py](app_build_info.py) deklariert
`1.0.0`; Fenstertitel und Info-Dialog verwenden diese gemeinsame
unveröffentlichte Quellversion. Dies ist keine Aussage über einen Release.
Die dokumentierte Historie steht im [Changelog](CHANGELOG.md).

## Einstieg

1. Über **Projektordner öffnen** die AddOn-Sammlung laden oder über **ZIP als Projekt entpacken** eine ZIP in einen leeren Arbeitsordner importieren.
2. AddOn und Navigationssprache auswählen, im Textpool-Baum einen Eintrag und danach eine Textzeile markieren.
3. Rechts den Text bearbeiten oder unten Deutsch, Englisch und Französisch parallel vergleichen/bearbeiten.
4. **Alles prüfen**, dann **Änderungen speichern**. Der Editor legt Sicherungen als `.bak` an.

**Hilfe:** Über das Menü **Hilfe > Bedienungsanleitung** oder **F1** wird das [Handbuch](https://github.com/Deathby-Snusnu/RPAddOns/blob/main/docs/RPTextStudio/HANDBUCH.md) im Programm angezeigt. Beim EXE-Build wird es eingebettet. Kurze Hinweise erscheinen als Tooltips an den Bedienelementen.

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
- Windows-EXE über `build_exe.bat` selbst erstellbar. Optionale
  KI-Übersetzungsvorschläge erfordern eine ausdrückliche Prüfung und Freigabe;
  es gibt keine unbeaufsichtigte Stapelverarbeitung.

Detaillierte Arbeitsschritte, Einschränkungen und Fehlerbehebung stehen im [Handbuch](https://github.com/Deathby-Snusnu/RPAddOns/blob/main/docs/RPTextStudio/HANDBUCH.md).

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
`Classes.lua` und `RaceClass.lua` ermittelte Schlüssel. Für PaladinRP werden
zusätzlich unterstützte Pools aus `Abilities.lua`, `Blessings.lua`,
`GreaterBlessings.lua`, `Auras.lua` und `Seals.lua` berücksichtigt.
Ambient-Pools und MagierRP sind nicht Bestandteil dieses Makro-Managers;
die Vorschläge sind keine vollständige Laufzeit-Schlüsselliste.

Bei PaladinRP liegen große Segen in `GreaterBlessings.lua` beispielsweise
unter `MIGHT`. Der Manager bietet dafür den Laufzeitschlüssel `GREATER_MIGHT`
an und erzeugt `/prp greater_might`. Die verfügbaren Aufrufe mit
`/prp list` überprüfen.

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

**Kein Runtime-Patch:** Das Programm macht keine Rassen/Klassen spielbar und passt die Rassen-/Klassen-Erkennung im AddOn nicht automatisch an. ID-Schreibweise und Core-Handler müssen gesondert geprüft werden. Details siehe [Handbuch](https://github.com/Deathby-Snusnu/RPAddOns/blob/main/docs/RPTextStudio/HANDBUCH.md).

## Projektdateien und Sicherungen

| Datei | Inhalt | Wirkung im Spiel |
| --- | --- | --- |
| `data\.rptextstudio-translations.json` | Explizite Übersetzungsgruppen | Keine |
| `data\.rptextstudio-spells.json` | Zauber-/Schlüsselzuordnungen für Makros | Erst durch Nutzung des erzeugten Makros |
| `data\.rptextstudio-races-classes.json` | Redaktionelle Rassen-/Klassenprofile | Keine; optionale Lua-Zweige sind separat |
| `addons.json` im Projektstamm | Optionale lokale AddOn- und Repository-Zuordnungen | Keine |

Bei Auswahl von `addons` im vollständigen Quellprojekt wird der übergeordnete
Projektstamm verwendet. Installationspakete lassen diese Register aus; bei
einem Projektumzug den gesamten `data`-Ordner und gegebenenfalls die
`addons.json` mitnehmen. Lua-Sicherungen liegen neben der jeweiligen Datei
und tragen einen Zeitstempel vor `.bak`. Beim Überschreiben des Übersetzungs-
oder Zauberregisters entsteht eine JSON-Sicherung mit zusätzlichem `.bak`.
Das Rassen-/Klassenregister und `addons.json` erhalten beim Speichern keine
solche automatische Sicherung; vor Änderungen bei Bedarf selbst sichern.
Zusammenhängende Änderungen über mehrere Dateien sind nicht atomar.

## Module

| Modul | Zuständigkeit |
| --- | --- |
| [main.py](main.py) | Editoroberfläche, Projekt-/ZIP-Öffnen, Filter, Sprachvergleich, Menüs und Arbeitsassistent |
| [project_paths.py](project_paths.py) | Projekt-/AddOn-Wurzeln, Metadaten- und Handbuchpfade |
| [lua_text.py](lua_text.py) | Statischer Lua-Listenparser, Validierung, gezieltes Schreiben und Sicherungen |
| `key_creation.py`, `key_deletion.py` | Neue Schlüssel anlegen bzw. ausgewählte Textschlüssel sicher entfernen |
| [translation_links.py](translation_links.py) | Sprachübergreifende Poolkennungen, Textreferenzen und JSON-Speicherung |
| [spell_manager.py](spell_manager.py) | Schlüsselvorschläge, Makroerzeugung und Zuordnungsregister |
| [race_class_manager.py](race_class_manager.py) | Profilregister und optionale Lua-Textzweige |
| `addon_manager.py`, `user_addon_manager.py` | AddOn-Erkennung, Vorschau und sichere Installations-/Updateoperationen |
| `github_updates.py`, `github_staging.py`, `safe_github_install.py` | Versionsprüfung, validiertes Paket-Staging und bestätigte Installation |
| `wow_detection.py`, `wow_client_profiles.py` | WoW-Installationen erkennen und Interface-Profile verwalten |
| `addon_registry.py` | Vorhandene AddOn-Projekte erkennen und lokal registrieren |
| `ai_translation.py`, `workspace_wizard.py`, `workflow_wizard.py` | Geprüfte Übersetzungsvorschläge und geführte Arbeitsabläufe |

## Lizenz

Der Editor steht laut [LICENSE](LICENSE) unter **MPL-2.0**.
Die Lizenz der bearbeiteten RP-Texte wird dadurch nicht geändert; für die
AddOn-Textdaten gelten die jeweiligen Lizenz- und SPDX-Hinweise.

## Ambient-Texte (Version 0.1.11)

Neu: `Ambient.lua` und `AmbientRacial.lua` in JaegerRP, PaladinRP und DruidenRP. Die Textverwaltung erkennt die Tabellen als Textpools. Waehle die Textart und bei rassenspezifischen Kategorien die Rasse. Alle Textaenderungen muessen wie bisher gespeichert werden. `*Handlungen*` werden zu `/me`.

### Falsch angelegte Schlüssel entfernen (0.1.12)

Gewünschten Textpool auswählen und **Schlüssel löschen** anklicken. Vor dem Löschen wird die Liste der betroffenen Sprachdateien gezeigt und eine Bestätigung verlangt. Es werden nur die Texte des gewählten Schlüssels (inklusive `ziel`/`gruppe`), nicht der übergeordnete Rassen-/Klassenzweig gelöscht. Alle geänderten Lua-Dateien erhalten ein `.bak`-Backup. Makro- und Übersetzungsmetadaten bei Bedarf separat prüfen. Siehe [Handbuch](https://github.com/Deathby-Snusnu/RPAddOns/blob/main/docs/RPTextStudio/HANDBUCH.md).

## KI-Übersetzung mit OpenAI

Im Sprachvergleich einen **deutschen** Text auswählen und **KI-Übersetzung …** anklicken. In dem Dialog einen eigenen OpenAI API-Key eingeben oder `OPENAI_API_KEY` als Umgebungsvariable setzen; Modell und RP-Stil können angepasst werden. Erst **Vorschläge erzeugen** sendet Originaltext, AddOn, Rasse und Stil über die OpenAI Responses API an den Dienst (API-Nutzung kann Kosten verursachen).

Die Vorschläge für `enUS` und `frFR` werden zunächst nur angezeigt. Sie können korrigiert und **einzeln freigegeben** werden. Der Editor prüft dabei `%s`, `%p`, `%%`, `*...*` und Zeilenumbrüche. Erst nach Freigabe werden Varianten in die vorhandenen Sprachpools übernommen und dem deutschen Text zugeordnet. Bestehende Sprachvarianten werden **nicht überschrieben**. Abschließend **Änderungen speichern** wählen, um Lua-Änderungen und Übersetzungsverknüpfungen mit Backups zu sichern.

**Sicherheit und Grenzen:** API-Schlüssel werden nicht in Projektdateien gespeichert. Es gibt keine automatische Stapelverarbeitung. Zielsprach-Textpools müssen schon existieren. Ein vorhandener Übersetzungslink wird nicht automatisch geändert. Die automatisierten API-Tests nutzen Mocks; eine aktuelle Abnahme mit echtem Online-Dienst und Windows-GUI ist hier nicht belegt.

## Klassische Menüführung (0.1.13)

Die Anwendung nutzt die Menüleiste **Datei, Bearbeiten, Projekt, AddOns,
Übersetzungen, Ansicht, Hilfe** und eine kompakte Standardsymbolleiste.
Die wichtigsten Kürzel: **Strg+O** Projekt öffnen, **Strg+S** speichern,
**Strg+N** Text hinzufügen, **Strg+D** duplizieren, **Strg+F** Suche
fokussieren, **F7** Projekt prüfen, **F1** Handbuch und **F2**
Arbeitsassistent.

Unten zeigt die dauerhafte Statusleiste Projekt, Navigationssprache, ausgewählte Textzeile und ungespeicherte Textpool-/Verknüpfungsänderungen. Die bisherigen Texteditoren, Sprachvergleiche und Prüfungen bleiben erhalten.

## Geführter Workflow-Assistent (0.1.14)

Über **Hilfe → Einfacher Assistent…** startet der frühere dreistufige
Navigationsassistent. Er bietet **Text bearbeiten**, **Zauber ergänzen**,
**KI-Übersetzung** und **Projekt prüfen**. Der Dialog beschreibt die
Voraussetzungen und öffnet nach **Fertigstellen** das jeweilige Werkzeug.
Er schreibt keine Dateien und sendet keine API-Anfragen selbstständig.
**F2** öffnet stattdessen den nachfolgend beschriebenen Arbeitsassistenten.

Der Assistent in 0.1.14 war eine geführte Navigation. Der spätere
Arbeitsassistent mit Entwurf, Prüfung und Speichern ist unter 0.1.15
beschrieben; die Anlage neuer Strukturen kam in 0.1.16 hinzu.

## Arbeitsassistent mit Schrittnavigation (0.1.15)

Der neue **große Arbeitsassistent** startet über **Hilfe → Arbeitsassistent…** oder **F2**. Links befinden sich die Schritte **Text auswählen**, **Original bearbeiten**, **Übersetzen**, **Prüfen & speichern**. Rechts bleibt der jeweilige Editor sichtbar; die Eingaben werden zwischen den Schritten als Entwurf erhalten.

1. Projekt laden und vorhandene Änderungen speichern.
2. Assistent aufrufen, deutschen Textpool und Ausgangszeile auswählen.
3. Original bearbeiten, bei Bedarf OpenAI-Vorschläge für `enUS` und `frFR` erzeugen und einzeln freigeben.
4. Prüfbericht lesen und **Prüfen und speichern** bestätigen. Erst dann werden Lua-Dateien und Übersetzungsverknüpfungen über die vorhandene Speicherlogik geschrieben (mit Backups).

Ohne API-Schlüssel können Übersetzungen manuell eingetragen werden. Fehlerhafte `%s`/`%p`/`%%`-Platzhalter oder Emote-Markierungen werden nicht übernommen. Bereits bestehende Links werden nicht ersetzt. Zielsprachpools müssen vorhanden sein. Der frühere einfache Navigationsassistent steht über **Hilfe → Einfacher Assistent…** weiterhin zur Verfügung.

Die Neuanlage von Zauber- und Rassenstrukturen gehörte noch nicht zu 0.1.15;
sie ist im folgenden Abschnitt für 0.1.16 beschrieben. Ein Windows-GUI-Test
ist weiterhin erforderlich.

## Arbeitsassistent: neue Strukturen anlegen (0.1.16)

Der mit **F2** erreichbare große Arbeitsassistent enthält zusätzlich **Strukturen anlegen**. Hier lassen sich neue **allgemeine, rassen- und klassenbezogene Zauberschlüssel** oder **Rassen-/Klassenprofile** vorbereiten. Ein Profil kann wahlweise nur das Projektregister erweitern oder zusätzlich vorhandene unterstützte `Racial.lua`-/`Classes.lua`-Sprachdateien ergänzen.

Die Vorschau prüft Kennungen, vorhandene Dateien, eindeutige Lua-Root-Strukturen und doppelte Einträge auf temporären Kopien. Erst **Struktur prüfen und anlegen** plus eine weitere Bestätigung verändern Dateien; Lua-Dateien erhalten Backups. Danach wird das Projekt neu geladen, damit neue Schlüssel im Texteditor sichtbar sind.

**Grenzen:** Neue Schlüssel sind reine RP-Textdaten. Die Zauber- oder Rassenerkennung im laufenden WoW-AddOn wird dadurch nicht automatisch erweitert. Für vorhandene Texte und Übersetzungen gelten weiterhin die getrennten Schritte **Text auswählen → Bearbeiten → Übersetzen → Prüfen & speichern**.

## Eigenständige Klassen-AddOns

Klassen-AddOns wie MagierRP werden in ihren eigenen GitHub-Repositories entwickelt.
RP Text Studio erzeugt keine neuen AddOn-Quellcodeprojekte mehr. Bestehende
RP-AddOns lassen sich weiterhin öffnen, bearbeiten, übersetzen, prüfen,
installieren und aktualisieren. Die lokale AddOn-Erkennung über `.toc`
und `addons.json` bleibt erhalten.

### KriegerRP im GitHub-Katalog

`KriegerRP` gehört mit der Klassenkennung `WARRIOR` und dem
Quell-Repository [Deathby-Snusnu/KriegerRP](https://github.com/Deathby-Snusnu/KriegerRP)
zum geschützten AddOn-Katalog (Änderung in
[PR #44](https://github.com/Deathby-Snusnu/RPTextStudio/pull/44)).
Bei bestätigter Installation werden dieselben Download-, Prüf- und
Bestandsschutz-Regeln wie bei anderen AddOns verwendet.
Die enthaltenen Texte können nach deDE, enUS und frFR getrennt
bearbeitet werden. Die enthaltenen /krp-Schlüssel sind im
Projektquellcode definiert; passive Schlüssel wie `TACTICAL_MASTERY`
dürfen nicht als aktiv wirkbare Zauber gemappt werden.

Die Erstversion wird in
[KriegerRP PR #1](https://github.com/Deathby-Snusnu/KriegerRP/pull/1)
entwickelt. Bis zu deren Merge kann der GitHub-Updater im `main`-Branch
noch keinen vollständigen KriegerRP-Release beziehen.
