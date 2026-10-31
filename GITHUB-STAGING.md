# GitHub-Pakete sicher vorbereiten (Staging)

Im Anwender-Modus **AddOns → Anwender: Installierte AddOns prüfen…** einen
Eintrag markieren und **AddOn herunterladen und prüfen…** wählen.

Die Funktion ermittelt über die GitHub API eine stabile Release-Tag-Version
oder den Standardbranch, löst die Referenz zu einem Commit-SHA auf, lädt das
zugehörige GitHub-ZIP-Archiv und prüft es vor dem Entpacken. Öffentliche
Repositories funktionieren ohne Anmeldung; `GH_TOKEN` oder `GITHUB_TOKEN`
können optional gesetzt werden. Für private Repositories ist ein gültiges
`GH_TOKEN` oder `GITHUB_TOKEN` erforderlich.

## Prüfungen

- Zulässige Repositories: Einträge des geprüften lokalen AddOn-Katalogs unter
  Deathby-Snusnu. Der mitgelieferte Katalog enthält sieben AddOns einschließlich
  MagierRP; neue Quellen benötigen eine entsprechende Katalogfreigabe.
- Maximal 64 MiB Archivgröße, 256 MiB Runtime-Inhalte und 10.000 Dateien.
- Abweisung von Pfad-Traversal, absoluten Pfaden, symbolischen Links und doppelten Namen.
- Nur bekannte Runtime-Dateiendungen; Entwicklungsordner werden ausgeschlossen.
- Dateien ohne zugelassene Runtime-Endung, darunter `LICENSE` und `NOTICE`,
  werden beim Staging nicht übernommen. Lizenz- und Rechtehinweise für eine
  Weitergabe müssen deshalb gesondert geprüft und bereitgestellt werden.
- Die gleichnamige TOC-Datei und alle daraus referenzierten Runtime-Dateien müssen vorhanden sein.
- Eine stabile Release-Version muss exakt zur Version im TOC passen.
- Anzeige von Commit-SHA und SHA-256-Hash des geladenen Archivs.
- Das Paket wird nur in einen noch nicht existierenden Staging-Ordner
  außerhalb des WoW-AddOns-Pfads entpackt; das übergeordnete Verzeichnis
  muss bereits existieren.

## Wichtig

Der SHA-256-Hash dient der lokalen Nachvollziehbarkeit der tatsächlich geladenen ZIP-Bytes. Er ist **keine unabhängige Signatur oder kryptografische Herkunftsbestätigung**. Das Vertrauen beruht auf TLS, GitHub API, dem zugeordneten Repository und dem aufgelösten Commit.

Das Staging ist **keine Installationsfreigabe**. Der Staging-Schritt selbst
installiert nichts und prüft keine signierten Manifeste. Für die getrennte,
ausdrücklich bestätigte Installation siehe
[sichere Installation](SAFE-GITHUB-INSTALL.md). Der vollständige Windows-
Abnahmestand ist hier nicht belegt und muss vor einer Produktivfreigabe
gesondert geprüft werden.

## Tests

Im RPTextStudio-Quellverzeichnis:
`python -m unittest discover -s tests -p test_github_staging.py -v`

Vor Freigabe sind unter Windows reale Paketdownloads, gesetzte Tokens für
private Repositories, Netzwerkausfälle und der PySide6-Dialog-Lebenszyklus
zu testen.
