# RP Text Studio 0.1.10 – Bedienungsanleitung

[Editor-Übersicht und Installation](README.md) · [Changelog](CHANGELOG.md) ·
[Sammlungsübersicht](../README.md)

## Schnellstart

1. Python installieren; bisher dokumentiert sind 3.11–3.13, ohne nachgewiesene vollständige Testmatrix. **`Start.bat`** erstellt bei Bedarf `.venv`, aktiviert sie, prüft/installiert bei jedem Start `requirements.txt` und öffnet den Editor.
2. Alternativ nach der [manuellen Einrichtung](README.md#installation-windows) im Editor-Ordner mit `.\.venv\Scripts\python.exe main.py` starten. Das vermeidet den pip-Aufruf des Starters und ist bei bereits installierten Abhängigkeiten auch für Offline-Arbeit geeignet.
3. **Projektordner öffnen** oder **ZIP als Projekt entpacken** auswählen. Für ZIP-Import einen leeren Arbeitsordner wählen.
4. Oben AddOn und Navigationssprache wählen, links einen Textpool anklicken.
5. In der mittleren Textliste eine Zeile wählen und rechts oder im Sprachvergleich bearbeiten.
6. **Alles prüfen** ausführen und anschließend **Änderungen speichern** drücken.

## Oberfläche

- **Projektordner öffnen:** Öffnet ein bereits entpacktes Projekt mit den AddOn-Unterordnern.
- **ZIP als Projekt entpacken:** Entpackt ein AddOn-Archiv in einen Arbeitsordner. Die Original-ZIP wird nicht bearbeitet.
- **Änderungen speichern:** Aktualisiert geänderte Lua-Textlisten. Vor jeder tatsächlich geschriebenen Datei entsteht eine `.bak`-Datei.
- **Alles prüfen:** Sucht nach leeren Texten, einseitigen `*`-Markierungen und unbekannten `%`-Platzhaltern. Dies ist kein vollständiger Lua- oder Spieltest.
- **Addon:** Begrenzt die Textpool-Liste auf ein AddOn.
- **Sprache:** Wählt die Navigationssprache; der Sprachvergleich zeigt trotzdem alle drei Sprachen.
- **Textart:** Filtert auf `Texts.lua`, `Racial.lua` oder `Ambient.lua`. **Alle Textarten** zeigt zusätzlich andere Kategorien, beispielsweise Paladin-Segen und soziale RPChatMod-Texte.
- **Rasse:** Filtert auf eine bestimmte Rasse aus `Racial.lua`. Bei ausgewählter Rasse erscheinen nur entsprechende Rassentextpools.
- **Suche:** Filtert Textpools anhand von Key und Textinhalt der Navigationssprache.
- **Textpool-Baum:** AddOn > Datei > Schlüssel/Kategorie.
- **Textliste:** Alle Varianten des ausgewählten Pools. Ein Klick wählt die aktive Zeilennummer.
- **Neu / Duplizieren / Entfernen / ↑ / ↓:** Verändert nur die Varianten im aktuell gewählten Sprachpool.
- **Text bearbeiten:** Bearbeitet die aktuell gewählte Zeile in der Navigationssprache.
- **Vorschau:** Veranschaulicht `/say` beziehungsweise `/me` mit beispielhaften Namen.
- **Sprachvergleich:** Drei Felder für `deDE`, `enUS`, `frFR` zeigen dieselbe Textkategorie, aber ausdrücklich ausgewählte Varianten. Andere Sprachen erhalten ohne gespeicherte Verknüpfung keine automatische Variantenauswahl. Im Dropdown wählen oder in der betreffenden Navigationssprache über **Neu** eine Variante ergänzen.

### Übersetzungsgruppen (verbessert in 0.1.9)

1. **Projekt öffnen** und einen Textpool (z. B. `SHADOW_BOLT/ziel`) auswählen.
2. In der Textliste einen **Ausgangstext** anklicken. Dessen Sprache ist bereits vorausgewählt.
3. In den Dropdowns von `deDE`, `enUS`, `frFR` die passenden Varianten auswählen. Die Dropdowns zeigen jeweils **Nummer und Textanfang**. Sobald du eine Variante auswählst, steht **genau dieser Text** im Editor darunter. „Keine Auswahl“ lässt eine Sprache aus.
4. **Diese Texte verknüpfen** klicken. Mindestens zwei Sprachen müssen ausgewählt sein. Ein Text, der bereits in einer anderen Gruppe vorkommt, wird nicht stillschweigend neu verknüpft.
5. **Gespeicherte Verknüpfung anzeigen** aktiviert die Anzeige der tatsächlich verbundenen Varianten beim Wechsel des Ausgangstexts.
6. **Änderungen speichern** sichert die Zuordnungen im Projektordner.

**Wichtig:** Der Sprach-Editor bearbeitet immer exakt die Variante aus dem Dropdown darüber. Eine Auswahl ist **keine automatische Übersetzung**. „Zuordnung lösen“ löscht ausschließlich die Verbindung, nicht die RP-Texte.

Gespeichert wird separat in `.rptextstudio-translations.json`; die Lua-Dateien enthalten weiterhin ausschließlich ihre bisherigen RP-Texte. Es werden keine neuen Übersetzungen erfunden. Wenn Sätze oder ihre Position verändert werden, lässt sich eine Verknüpfung nur wiederfinden, wenn die Textreferenz eindeutig ist. Backups werden beim Speichern angelegt.

### Wichtig zum Sprachvergleich

Die RP-Texte in den Sprachen sind alternative Zufallsvarianten, **keine garantiert paarweise übersetzten Sätze**. Gleiche Zeilennummer bedeutet daher nicht automatisch gleiche Bedeutung. Der Vergleich dient der Sichtkontrolle und schnellen Bearbeitung. Eine automatische Übersetzung oder Synchronisierung findet nicht statt.

## RP-Konventionen

- `Ein Satz.`: gesprochener Text, in der Vorschau `/say`; im Spiel gilt der konfigurierte Kanal.
- `*hebt die Hand.*`: Handlung, später `/me`.
- `%s`: vom AddOn aufgelöster Name, beispielsweise Ziel oder Begleiter. `%p`: Dämonenname in HexerRP. Der Editor akzeptiert außerdem `%%` und zeigt es als Prozentzeichen; die AddOns ersetzen dies nicht allgemein. Vorschau und tatsächliche Laufzeitersetzung können deshalb abweichen.
- Normale Textbearbeitungen werden vorgemerkt und erst über **Änderungen speichern** geschrieben. Schlüsselanlage und die Manager haben eigene Schreibvorgänge; beim Bestätigen der Schlüsselanlage werden die Lua-Strukturen bereits geschrieben.

## Sichere Arbeitsweise

- Original-ZIP aufbewahren und nur in einem eigenen Arbeitsordner bearbeiten.
- Nach dem Speichern eine Stichprobe im Spiel durchführen. Der Editor startet WoW nicht und überprüft keinen aktiven AddOn-Client.
- Lua-Sicherungen heißen beispielsweise `Texts.lua.<Zeitstempel>.bak`; JSON-Sicherungen tragen zusätzlich `.bak`. Für eine Wiederherstellung den Editor schließen, die aktuelle Fassung separat sichern und die gewünschte Sicherung unter dem ursprünglichen Dateinamen zurückkopieren.
- Bei ungespeicherten Änderungen erscheint vor Projektwechsel oder Schließen eine Rückfrage.

## Einschränkungen

- Bearbeitet ausschließlich statische String-Listen in `*/locales/{deDE,enUS,frFR}/*.lua`, außer `Expansion.lua`.
- Keine Bearbeitung ausführbarer Lua-Logik oder dynamischer Texttabellen. Neue Schlüssel sind über den gesonderten Dialog in unterstützten bestehenden Tabellen möglich; neue Sprachdateien und TOC-Einträge werden nicht erstellt.
- Beim Ändern einer Liste können Kommentare **innerhalb der Liste** verloren gehen. Code und Kommentare außerhalb der bearbeiteten Liste bleiben erhalten.
- Keine Garantie, dass Textvarianten verschiedener Sprachen dieselbe Reihenfolge oder Anzahl besitzen. Deshalb gibt es explizite Zuordnungen. Die Anwendung übersetzt Texte nicht automatisch.
- Kein `.exe`, keine Live-Verbindung zu WoW, keine automatische Übersetzung.
- Pytest-Tests ersetzen keinen GUI-Test auf Windows und keinen Ingame-Test.
- **Alles prüfen** kontrolliert nicht vollständig die Chatgrenze von 255 Bytes nach Ersetzung, die Kanalverfügbarkeit oder die Erkennung neuer Schlüssel im AddOn.

## Hilfe und Hinweise

- **F1:** Öffnet diese Anleitung im Programm.
- **Hilfe > Bedienungsanleitung:** Öffnet dieselbe Anleitung.
- Mit dem Mauszeiger über Schaltflächen und Eingabefeldern erscheinen kurze Tooltips.

## Fehlersuche

- **`ModuleNotFoundError: PySide6`**: Im Editor-Ordner `.\.venv\Scripts\python.exe -m pip install -r requirements.txt` ausführen; fehlt die Umgebung, zuerst die [Installation](README.md#installation-windows) durchführen.
- **Keine bearbeitbaren Locale-Textpools gefunden**: Prüfen, ob der gewählte Ordner AddOn-Unterordner mit `locales/deDE`, `locales/enUS` oder `locales/frFR` enthält.
- **Sprachfeld deaktiviert**: Es fehlt der entsprechende Sprachpool oder im Dropdown ist keine Variante ausgewählt.
- **Nicht im Spiel sichtbar**: Sicherstellen, dass die gespeicherten AddOns in den verwendeten Client-AddOns-Ordner kopiert wurden und der Client neu geladen wurde.

## Rassentexte in HexerRP

Die Rassenfilter sind reine Navigationsfilter und ändern nicht die aktive Spielerrasse. Wähle **HexerRP**, die Textart **Rassen (Racial.lua)** und z. B. **Gnome**, um die entsprechenden Texte zu bearbeiten. Für allgemeine Varianten zunächst **Alle Rassen** und **Allgemein (Texts.lua)** wählen. Fehlende oder unbrauchbare Zauber-Rassenkombinationen fallen in HexerRP auf allgemeinere Pools zurück. Neue Schlüssel lassen sich über den folgenden Dialog anlegen.

## Neue Rassen-, Klassen- und Zauberschlüssel (Version 0.1.6)

1. AddOn-Projekt öffnen und gegebenenfalls bisherige Änderungen speichern.
2. Oben **Neuen Schlüssel anlegen** wählen.
3. AddOn und die gewünschte Struktur auswählen: **Rasse**, **Klasse**, **Rasse + Klasse** oder **Allgemein**.
4. Je nach Struktur die *internen* Rassen-/Klassenbezeichner und den neuen Zauberschlüssel eingeben. Erlaubt sind Buchstaben, Zahlen und Unterstriche; die Bezeichnung muss mit einem Buchstaben oder Unterstrich beginnen. Groß-/Kleinschreibung beachten.
5. Nach dem Erstellen den neuen Schlüssel über die Suche auswählen und die Platzhaltertexte in Deutsch, Englisch und Französisch ersetzen.
6. Mit **Alles prüfen** validieren und Änderungen speichern.

**Dateischemata:** Manche AddOns verwenden `SCHLUESSEL = {"Text"}`, andere `SCHLUESSEL = {ziel = {...}, gruppe = {...}}`. Der Editor orientiert sich an den vorhandenen Textpools. Fehlende `Classes.lua`- oder `RaceClass.lua`-Dateien werden bewusst nicht frei erfunden; der Dialog meldet die fehlende Vorlage.

**Ingame-Verhalten:** Ein neuer Textschlüssel erzeugt keine automatische
Zaubererkennung. Die Klassen-AddOns werden manuell per Slash-Befehl oder
`TryText` aufgerufen. Ob der neue Schlüssel nutzbar ist, hängt von der
vorhandenen Poolauswahl ab; ein Eintrag im Editorregister allein genügt
nicht. Neue Rassen-/Klassen-IDs müssen zur Erkennung im AddOn passen.
Der Texteditor ändert keine Core-Handler oder TOCs.

**Sicherheit:** Neue Schlüssel werden vor dem Schreiben in temporären Dateikopien getestet; für vorhandene Sprachdateien werden Sicherungen erstellt. Bei Schreibfehlern sollte man die vorhandenen `.bak`-Dateien prüfen, bevor ein weiterer Versuch erfolgt. Mehrere zusammenhängende Dateioperationen sind derzeit nicht atomar.

## Zauber-Manager (0.1.7)

Über **Zauber-Manager** lassen sich vorhandene RP-Schlüssel für die AddOns
HexerRP, PaladinRP, JaegerRP und DruidenRP mit einem WoW-Zaubernamen verknüpfen.
Die Vorschläge stammen aus geladenen `Texts.lua`, `Racial.lua`, `Classes.lua`
und `RaceClass.lua`. Andere Dateien wie `Blessings.lua` werden nicht generell
ausgewertet; die Liste ist keine vollständige Übersicht aller Laufzeitschlüssel.

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

## Rassen- und Klassen-Manager (0.1.8)

1. Ein entpacktes AddOn-Projekt öffnen und die Schaltfläche **Rassen-/Klassen-Manager** betätigen.
2. **Rasse** oder **Klasse** wählen, einen eindeutigen Lua-Schlüssel und einen Anzeigenamen angeben.
3. Den **RP-Sprachstil** als redaktionelle Beschreibung eintragen. Beispiel: `NightElf`, Anzeigename `Nachtelf`, Stil `Naturverbunden, geheimnisvoll, traditionsbewusst`.
4. Standardmäßig **Nur im Register** wählen. Dann entsteht ausschließlich `.rptextstudio-races-classes.json` im Projektordner.
5. Optional ein AddOn auswählen: Wenn dort vorhandene `locales/deDE|enUS|frFR/Racial.lua` bzw. `Classes.lua` bearbeitbare Tabellen besitzen, wird ein neuer Zweig für die ID mit dem ersten Textschlüssel (Vorgabe `RP_GREETING`) angelegt. Jeder Ziel-Lua-Datei wird davor ein Zeitstempel-Backup erstellt.
6. Den neuen Textpool über die gewohnte Auswahl öffnen, Platzhaltertext ersetzen und speichern.

**Wichtige Grenzen:** Das Register ist nur eine Verwaltung für den Editor. Es erweitert weder WoW Forever um neue spielbare Rassen/Klassen noch die im AddOn zur Laufzeit erkannten Rassen-IDs. Die internen IDs müssen exakt zur jeweiligen AddOn-Logik bzw. den WoW-Rassenkennungen passen, einschließlich Groß-/Kleinschreibung. `NightElf` ist ein Beispiel und wird *nicht* automatisch als gültige Kennung des Clients nachgewiesen. Bestehende AddOn-Core-Dateien werden nicht umgeschrieben. Es werden nur bereits vorhandene, statisch erkennbare Texttabellen unterstützt; fehlende oder mehrdeutige Dateistrukturen werden abgelehnt. Für einen neuen Zauber ist ggf. eine Registrierung im AddOn-Handler weiterhin nötig. Der Dialog verwaltet aktuell das **Anlegen**, nicht das Umbenennen oder Löschen vorhandener Profile. Sprachstil-Beschreibungen erzeugen keine automatischen Übersetzungen. JSON-Profil und Lua-Dateien werden separat gespeichert; bei einem seltenen Schreibfehler kann eine manuelle Wiederherstellung aus `.bak` nötig sein.


## Automatischer Windows-Start

- `Start.bat` verwendet das eigene `.venv` neben `main.py` und verändert keine global installierten Python-Pakete.
- Existiert noch keine Umgebung, erstellt das Skript sie über `py -3 -m venv`, alternativ `python -m venv`.
- Danach wird `Scripts\activate.bat` aufgerufen. `python -m pip install -r requirements.txt` überprüft bei jedem Start den Paketstand; bereits erfüllte Anforderungen müssen nicht erneut installiert werden.
- `start_windows.bat` ist aus Kompatibilitätsgründen weiterhin nutzbar.
- Bei Fehlern stoppt das Skript und zeigt die Meldung bis zum Tastendruck an.
- Für eine neue Umgebung den Editor schließen, die bisherige `.venv` zunächst unter anderem Namen aufbewahren und `Start.bat` erneut starten. Der Starter wählt über `py -3` eine verfügbare Python-3-Version, ohne den dokumentierten Bereich zu erzwingen.
- Die Startanzeige nennt noch `0.1.9`; die Anwendung selbst verwendet `0.1.10`.

### Fehlerbehebung: „kein Textpool“ in Englisch/Französisch

In Version 0.1.9 lag ein Fehler beim sprachübergreifenden Vergleich verschachtelter `localeData`-Schlüssel vor. Version 0.1.10 korrigiert die Zuordnung. Bestehende Übersetzungszuordnungen werden beim Laden auf sprachunabhängige Poolkennungen umgestellt. Speichere das Projekt anschließend, um die migrierte Zuordnung dauerhaft in der JSON-Datei zu sichern.

## Projektregister mitnehmen

Die Dateien `.rptextstudio-translations.json`, `.rptextstudio-spells.json` und
`.rptextstudio-races-classes.json` liegen im geöffneten Projektordner.
Sie enthalten Editor-Metadaten und werden nicht von WoW geladen.
Das [Verpackungsskript](../VERPACKUNG.md) schließt solche Punktdateien aus.
Für die Weiterarbeit in einem neuen Projektordner die benötigten Register
deshalb separat mitnehmen. Gespeicherte Lua-Textänderungen sind davon unabhängig.

## Tests und Modulübersicht

Python-Tests mit **pytest** aus dem vollständigen Quellprojekt ausführen.
Einrichtung und genaue Befehle stehen unter [Tests](README.md#tests);
eine Modulübersicht steht unter [Module](README.md#module).
Nach GUI-Änderungen oder Textpflege zusätzlich Öffnen, Variantenwahl,
Verknüpfen/Lösen, Speichern und Wiederöffnen an einer Projektkopie prüfen.
Anschließend die betroffenen AddOns im passenden WoW-Client testen.
