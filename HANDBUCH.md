# RP Text Studio 0.1.16 – Bedienungsanleitung

[Editor-Übersicht und Installation](README.md) · [Changelog](CHANGELOG.md) ·
[Sammlungsübersicht](../README.md)

## Schnellstart

1. **Ohne Python:** Die erstellte `RPTextStudio.exe` doppelklicken. Sie enthält Python, Qt und dieses Handbuch. Nur die EXE wird zum Starten benötigt, keine Python-Quellordner. Zum Erstellen siehe [Windows-EXE bauen](#windows-exe-bauen).
2. Alternativ nach der [manuellen Einrichtung](README.md#installation-windows) im Editor-Ordner mit `.\.venv\Scripts\python.exe main.py` starten. Das vermeidet den pip-Aufruf des Starters und ist bei bereits installierten Abhängigkeiten auch für Offline-Arbeit geeignet.
3. **Projektordner öffnen** oder **ZIP als Projekt entpacken** auswählen. Für ZIP-Import einen leeren Arbeitsordner wählen.
4. Oben AddOn und Navigationssprache wählen, links einen Textpool anklicken.
5. In der mittleren Textliste eine Zeile wählen und rechts oder im Sprachvergleich bearbeiten.
6. **Alles prüfen** ausführen und anschließend **Änderungen speichern** drücken.

## Windows-EXE bauen

Nur auf dem **Build-Rechner** wird Python benötigt; bisher dokumentiert sind
Python 3.11–3.13, ohne vollständige Testmatrix. Im vollständigen Quellordner
`build_exe.bat` doppelklicken oder in PowerShell ausführen:

```powershell
.\build_exe.bat
```

Das Skript erstellt bei Bedarf `.venv` und installiert die Laufzeit- und
Build-Abhängigkeiten aus `requirements-build.txt` ausschließlich dort.
Zum Herunterladen der Pakete wird Internet benötigt. PyInstaller erstellt
anschließend `dist\RPTextStudio.exe` als einzelne Windows-GUI-Datei ohne
Konsolenfenster. `build` enthält nur Build-Zwischendateien.
Ein erneuter Build ersetzt die bisherige Ausgabe; eine laufende EXE vorher schließen.

Die EXE kann allein in einen anderen Ordner oder auf einen anderen kompatiblen
Windows-Rechner kopiert werden. Der Zielrechner benötigt weder Python noch
pip, `.venv`, PySide6 oder die Python-Quelldateien. Für Veröffentlichungen
die geltenden Lizenzhinweise für das Programm und seine Abhängigkeiten
zusätzlich beachten. Ein Build übernimmt die Architektur des verwendeten
Python-Interpreters; er ist kein plattformübergreifendes Installationspaket.

**Projektdateien bleiben extern:** Über **Projektordner öffnen** den Ordner
auswählen, der die AddOn-Unterordner enthält. Lua-Dateien, JSON-Register und
Backups werden wie bisher im gewählten Projekt gespeichert, nicht in der
EXE oder ihrem temporären Entpackordner. Dort sind Schreibrechte erforderlich.
Bei geschützten Installationsordnern besser mit einer beschreibbaren
Arbeitskopie arbeiten und die fertigen AddOns anschließend zurückkopieren.
Der Projektordner kann auch als Argument übergeben werden:

```powershell
.\dist\RPTextStudio.exe "D:\RP-Projekte\Meine AddOns"
```

`Start.bat` und sein Alias `start_windows.bat` bevorzugen eine
`RPTextStudio.exe` direkt im Editor-Ordner, danach `dist\RPTextStudio.exe`.
Nur ohne vorhandene EXE wird wie bisher Python verwendet und bei Bedarf
`.venv` eingerichtet. Für die Arbeit am Python-Quellcode nach einem Build
`.\.venv\Scripts\python.exe main.py` direkt ausführen.

Die Onefile-EXE entpackt ihre Laufzeit beim Start vorübergehend in den
Windows-Tempordner; der erste Start kann deshalb etwas dauern.
Die normale Textbearbeitung funktioniert offline. Die optionale
KI-Übersetzung benötigt weiterhin Internet und einen eigenen API-Schlüssel;
Schlüssel und Projektdateien werden nicht in den Build eingebettet.

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
- Keine Live-Verbindung zu WoW, keine automatische Übersetzung.
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

## Ambient-Texte (Version 0.1.11)

Neu: `Ambient.lua` und `AmbientRacial.lua` in JaegerRP, PaladinRP und DruidenRP. Die Textverwaltung erkennt die Tabellen als Textpools. Waehle die Textart und bei rassenspezifischen Kategorien die Rasse. Alle Textaenderungen muessen wie bisher gespeichert werden. `*Handlungen*` werden zu `/me`.

## Text-/Zauberschlüssel sicher löschen (ab 0.1.12)

1. Projekt öffnen und einen Textpool des zu entfernenden Schlüssels auswählen, beispielsweise `JaegerRP → Racial.lua → NightElf → SERPENT_STING → ziel`.
2. Auf **Schlüssel löschen** klicken. Der Editor ermittelt denselben Schlüssel in den vorhandenen Sprachdateien und zeigt die betroffenen Dateien und die Anzahl der Textpools an.
3. Vorschau sorgfältig prüfen und die Sicherheitsabfrage bestätigen.
4. Bei Bedarf die automatisch angelegten `*.bak`-Sicherungskopien zurückspielen.

Es wird **der gesamte ausgewählte Zauber-/Aktionsschlüssel** entfernt, also bei `ziel`/`gruppe` beide Listen; die Rassen- und Klassen-Elternzweige bleiben bestehen. Die Löschung betrifft keine anderen AddOns und keine gleichnamigen Schlüssel unter anderen Rassen. Ausstehende Änderungen werden vorher zur Speicherung angeboten. Bei Fehlern in der Vorabprüfung wird keine Sprachdatei geändert. Die vorhandenen Makro-Zuordnungen aus `.rptextstudio-spells.json` und Übersetzungsverknüpfungen werden **nicht** stillschweigend gelöscht; kontrolliere sie danach gesondert. Neue im Spiel geladene Schlüssel verschwinden nach einem `/reload` aus den dynamischen Listen.

**Achtung:** Lösche keine von der AddOn-Logik erwarteten Schlüssel, ohne ihre Verwendung zu prüfen. Die Funktion entfernt Texttabellen, nicht ausführbare Lua-Befehle.

## OpenAI-KI-Übersetzung (enUS, frFR)

1. Projekt öffnen und einen `deDE`-Textpool sowie die gewünschte Ausgangszeile markieren.
2. **KI-Übersetzung …** aufrufen.
3. API-Schlüssel nur für diese Sitzung eintragen (alternativ Umgebungsvariable `OPENAI_API_KEY`), Modell prüfen und optional Rasse sowie RP-Stil ergänzen.
4. **Vorschläge erzeugen** anklicken. Der Online-Aufruf ist optional und kann je nach API-Tarif Kosten auslösen.
5. Englischen und französischen Vorschlag lesen und bei Bedarf direkt korrigieren. Jede Sprache einzeln per Kontrollkästchen freigeben.
6. **Freigegebene übernehmen** wählt vorhandene identische Texte aus oder ergänzt neue Varianten und legt die explizite Übersetzungsgruppe an. Bereits bestehende Übersetzungsgruppen werden nicht überschrieben.
7. Im Hauptfenster **Änderungen speichern** nutzen. Erst dann werden die Lua-Textdateien auf dem Datenträger aktualisiert.

Die Validierung blockiert fehlende oder zusätzliche `%s`, `%p`, `%%`, fehlende Emote-Sternchen und Zeilenumbrüche. Es werden ausschließlich ausgewählte RP-Texte und Charakterhinweise an die API gesendet, niemals der ganze AddOn-Ordner. Der Schlüssel bleibt nur im Speicher, wird in der Eingabe maskiert und nicht in den Projektdaten abgelegt. API-Fehler werden ohne Serverantwort-Inhalt angezeigt. Wenn für die Zielsprache der Textpool fehlt, muss dieser zuerst angelegt werden. Dieser Branch wurde nicht gegen den echten Online-Dienst oder die Windows-GUI getestet.

## Menüleiste und Statusleiste (0.1.13)

**Datei:** Projektordner öffnen, ZIP importieren, Änderungen speichern, Beenden. **Bearbeiten:** neue Textzeile, Duplizieren, Entfernen und Suche. **Projekt:** Schlüssel anlegen/löschen, Zauber-Manager, Rassen-/Klassen-Manager und Prüfung. **Übersetzungen:** Verknüpfen, Lösen und OpenAI-Vorschläge. **Ansicht:** Suchfokus und Statusleiste ein-/ausblenden. **Hilfe:** Handbuch und Programmversion.

Die kompakte Symbolleiste enthält Öffnen, Speichern, Text hinzufügen, Prüfung und KI-Übersetzung. Häufige Tastenkürzel: Strg+O, Strg+S, Strg+N, Strg+D, Strg+F, F7 und F1. Nicht verfügbare Funktionen wie projektweites Rückgängig werden bewusst nicht als Menüaktionen angezeigt.

Die Statusleiste unten zeigt den Projektnamen, die Navigationssprache, die Textanzahl und Zeilenauswahl sowie ausstehende Änderungen. Bei offenen Änderungen steht zudem ein Sternchen im Fenstertitel. Meldungen zu Aktionen erscheinen weiterhin kurzzeitig links in der Statusleiste. Der geplante Workflow-Assistent folgt erst in einer späteren Version.

## Workflow-Assistent (F2)

Unter **Hilfe → Workflow-Assistent…** (oder **F2**) kannst du einen der Abläufe **Text bearbeiten**, **Zauber ergänzen**, **KI-Übersetzung** oder **Projekt prüfen** auswählen. **Weiter** zeigt die benötigten Vorbedingungen; **Zurück** ermöglicht die Änderung des Vorhabens. Mit **Fertigstellen** öffnet der Assistent die vorhandene Bearbeitungsfunktion beziehungsweise fokussiert den Texteditor. Fehlende Projekt-, Textpool- oder Zeilenauswahl werden ausdrücklich erklärt.

Vor der KI-Übersetzung muss eine deutsche Zeile aus `deDE` markiert sein. Dort bleiben Vorschau, Platzhalterkontrolle und manuelle Freigabe bestehen. Zum Abschluss **Änderungen speichern** wählen. Der Assistent speichert nichts automatisch, legt keine Schlüssel ungefragt an und sendet keine API-Anfrage selbstständig ab.

Diese erste Ausbaustufe ist eine geführte Navigation durch die bestehenden Werkzeuge; eine umfassende mehrstufige Projektanlage folgt später.

## Neuer integrierter Arbeitsassistent (F2)

Im Menü **Hilfe → Arbeitsassistent…** öffnet sich ein breiter Dialog mit Schritten links und Arbeitsfläche rechts. Der Assistent arbeitet derzeit mit **bestehenden deutschen Textpools**. Er übernimmt die ausgewählte Quelle, hält die Änderungen als Entwurf, bietet manuelle Übersetzungsfelder und optional OpenAI-Vorschläge an und zeigt zuletzt einen Prüfbericht.

In Schritt 1 Textpool und Zeile wählen; in Schritt 2 das deutsche Original bearbeiten; in Schritt 3 die Übersetzungen ergänzen oder über OpenAI vorschlagen lassen und jede gewünschte Zielsprache per Checkbox freigeben; in Schritt 4 ausdrücklich **Prüfen und speichern** betätigen. Vorher werden keine Dateien geschrieben. Bei Platzhalterfehlern oder konfliktierenden Verknüpfungen bleibt der Dialog offen. Für einheitliche Sicherung werden die bestehenden Speicherroutinen mit Backup verwendet.

Bereits offene ungespeicherte Änderungen müssen **vor** dem Start des Assistenten gesichert werden. Die bisherigen Manager für neue Zauber und Rassen bleiben erreichbar; neue Schlüssel kann diese erste integrierte Ansicht noch nicht selbst erzeugen. **Hilfe → Einfacher Assistent…** öffnet weiterhin den bisherigen Navigations-Wizard.

## Neue Zauber, Rassen und Klassen im Arbeitsassistenten

Öffne das Projekt, speichere offene Änderungen und starte **F2 → Strukturen anlegen**. Wähle zwischen **Zauberschlüssel**, **Rassenprofil** oder **Klassenprofil**. Für Zauberschlüssel bestimmst du AddOn, Speicherstruktur (Allgemein, Rasse, Klasse oder Rasse+Klasse), gegebenenfalls die zugehörigen IDs und den neuen Schlüssel. Für Profile gibst du ID, Anzeigename und Sprachstil ein; der optionale Haken erstellt auch einen ersten `RP_GREETING`-Zweig in vorhandenen Sprachdateien.

Die Vorschau zeigt alle geplanten Dateien und Fehler. Mit **Struktur prüfen und anlegen** folgt nochmals eine Bestätigung, erst dann werden bestehende Funktionen mit Backup verwendet. Anschließend lädt der Editor die veränderten Dateien neu. Die eigentlichen RP-Sprüche kannst du nun in den neuen Pools ergänzen. Die Funktion erzeugt **keine** neuen spielbaren WoW-Rassen oder Zauberhandler; die Client-IDs müssen zur tatsächlichen Spielumgebung passen.

Die Sprachzuordnung bleibt über `.rptextstudio-translations.json` und die bestehenden manuellen/ KI-Übersetzungsschritte möglich. Ein Abbruch vor der abschließenden Bestätigung verändert keine Projektdatei.
