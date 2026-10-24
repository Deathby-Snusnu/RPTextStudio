# GitHub-Pakete sicher vorbereiten (Staging)

Im Anwender-Modus **AddOns → Anwender: Installierte AddOns prüfen…** einen Eintrag markieren und **Paket prüfen und bereitstellen…** wählen.

Die Funktion ermittelt über GitHub API eine stabile Release-Tag-Version oder den Standardbranch, löst die Referenz zu einem Commit-SHA auf, lädt das zugehörige GitHub-ZIP-Archiv authentifiziert über `gh auth token` oder GH_TOKEN/GITHUB_TOKEN und prüft es vor dem Entpacken.

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

Das Staging ist **keine Installationsfreigabe**. Es gibt noch keine automatische Installation aus dem Paket, keine Freigabe über signierte Manifeste und keine Übertragung in WoW-AddOns. Die Funktion ist für den Windows-Test vorgesehen und verbleibt bis dahin als Draft.

## Tests

`python -m unittest discover -s tests -p test_github_staging.py -v`

Vor Freigabe sind unter Windows die GitHub-CLI-Anmeldung, reale private Repo-ZIP-Dateien, Netzwerkausfälle und PySide6-Dialog-Lebenszyklus zu testen.
