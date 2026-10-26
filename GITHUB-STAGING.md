# GitHub-Pakete sicher vorbereiten (Staging)

Im Anwender-Modus **AddOns → Anwender: Installierte AddOns prüfen…** einen Eintrag markieren und **Paket prüfen und bereitstellen…** wählen.

Die Funktion ermittelt über die GitHub API eine stabile Release-Tag-Version
oder den Standardbranch, löst die Referenz zu einem Commit-SHA auf, lädt das
zugehörige GitHub-ZIP-Archiv und prüft es vor dem Entpacken. Öffentliche
Repositories funktionieren ohne Anmeldung; `GH_TOKEN` oder `GITHUB_TOKEN`
können optional gesetzt werden. Für private Repositories ist ein gültiges
`GH_TOKEN` oder `GITHUB_TOKEN` erforderlich.

## Prüfungen

- Zulässige Repositories: die sechs vorhandenen RP-AddOns unter Deathby-Snusnu; neue AddOns benötigen ein explizites eigenes Freigabekonzept.
- Maximal 64 MiB Archivgröße, 256 MiB Runtime-Inhalte und 10.000 Dateien.
- Abweisung von Pfad-Traversal, absoluten Pfaden, symbolischen Links und doppelten Namen.
- Nur bekannte Runtime-Dateiendungen; Entwicklungsordner werden ausgeschlossen.
- Die gleichnamige TOC-Datei und alle daraus referenzierten Runtime-Dateien müssen vorhanden sein.
- Eine stabile Release-Version muss exakt zur Version im TOC passen.
- Anzeige von Commit-SHA und SHA-256-Hash des geladenen Archivs.
- Das Paket wird nur in einen neuen, leeren Staging-Ordner außerhalb des WoW-AddOns-Pfads entpackt.

## Wichtig

Der SHA-256-Hash dient der lokalen Nachvollziehbarkeit der tatsächlich geladenen ZIP-Bytes. Er ist **keine unabhängige Signatur oder kryptografische Herkunftsbestätigung**. Das Vertrauen beruht auf TLS, GitHub API, dem authentifizierten Repository und dem aufgelösten Commit.

Das Staging ist **keine Installationsfreigabe**. Der Staging-Schritt selbst
installiert nichts und prüft keine signierten Manifeste. Für die getrennte,
ausdrücklich bestätigte Installation siehe
[sichere Installation](SAFE-GITHUB-INSTALL.md). Der vollständige Windows-
Abnahmetest steht noch aus; bis dahin ist die Funktion nicht für eine
Produktivfreigabe vorgesehen.

## Tests

`python -m unittest discover -s tests -p test_github_staging.py -v`

Vor Freigabe sind unter Windows reale Paketdownloads, gesetzte Tokens für
private Repositories, Netzwerkausfälle und der PySide6-Dialog-Lebenszyklus
zu testen.
