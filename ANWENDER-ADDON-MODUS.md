# Anwender-Modus für RP-AddOns

Unter **AddOns → Anwender: Installierte AddOns prüfen…** kann RPTextStudio die installierten RP-AddOns ohne ein geöffnetes Entwicklungsprojekt anzeigen.

## Funktionen

- Suche nach gespeicherten und bekannten WoW-Installationen im Hintergrund.
- Bestätigte Clients auswählbar; Anzeige lokaler TOC-Versionen und
  Interface-Nummern der sieben AddOns im mitgelieferten Katalog, einschließlich MagierRP.
- Öffentliche GitHub-Versionen lassen sich ohne Anmeldung prüfen; `GH_TOKEN`
  oder `GITHUB_TOKEN` sind optional. Für private Repositories kann vorhandene
  Authentifizierung über `GH_TOKEN` oder `GITHUB_TOKEN` verwendet werden.
- Die Versionsprüfung verändert keine WoW- oder Projektdateien. Antworten der
  GitHub-API können jedoch in einem lokalen Cache unter
  `%LOCALAPPDATA%\RPTextStudio\github_api_cache.json` gespeichert werden
  (ohne `LOCALAPPDATA` unter `~/.cache/rptextstudio/`). Paketdownload und
  Installation sind separate, ausdrücklich gestartete Aktionen mit Vorschau;
  siehe [sichere Installation](SAFE-GITHUB-INSTALL.md).
- **AddOn herunterladen und prüfen…** legt ein geprüftes Paket außerhalb von
  WoW bereit. **Geprüftes Paket installieren…** schreibt erst nach Vorschau
  und ausdrücklicher Bestätigung in die ausgewählte WoW-Installation.
- **Ausgewähltes AddOn aktualisieren…** führt von einem Download zur
  geschützten Vorschau. Abweichende vorhandene Dateien werden nur bei
  ausdrücklicher Einzelauswahl ersetzt.
- Fehlende bekannte AddOns lassen sich auswählen, gemeinsam vorbereiten und
  nach einer gemeinsamen Vorschau installieren; siehe
  [Erstinstallation](FIRST-INSTALL-RP-ADDONS.md).
- Die Auswahl weiterer WoW-Pfade erfolgt weiterhin über Projekt → WoW-Installation suchen; danach den Anwenderdialog erneut öffnen.

## Entwicklerfunktionen

Unter **AddOns → Entwickler: Lokale AddOns installieren…** bleibt der bestehende Installer mit expliziter Entwicklungsprojekt-Quelle und Vorschau erhalten.

## Grenzen und Tests

Der Modus verwendet den mitgelieferten Katalog; beliebige Repositories
werden nicht aus lokalen Ordnernamen abgeleitet. Ein vorbereitetes Paket ist
keine Kompatibilitätszusage. Die Versionsprüfung und das Staging ersetzen
keinen Windows- oder Ingame-Test.

Der Versionsvergleich unterstützt nur numerische, punktgetrennte Angaben.
SemVer-Zusätze wie `-rc.1` oder `+build.1` werden nicht ausgewertet: Bei einem
Versionsvergleich lautet der Status **Unvergleichbar**, bei solchen stabilen
Release-Tags **Kein Release / nicht verfügbar**.

Bei direkter Nutzung von `inspect_installed` oder `check_installed` aus
[user_addon_manager.py](user_addon_manager.py) müssen übergebene AddOn-Namen
den eindeutigen IDs des mitgelieferten vertrauenswürdigen Katalogs entsprechen.
Unbekannte IDs, Pfadbestandteile und doppelte Einträge werden abgelehnt.

Der ältere Entwickler-Versionsdialog zeigt noch Hinweise auf sechs private
Repositories und `gh auth login`. Die aktuellen HTTP-Abfragen benötigen für
öffentliche Repositories keine GitHub-CLI; für authentifizierte Zugriffe
werden `GH_TOKEN` oder `GITHUB_TOKEN` verwendet.


## Updates bei abweichender TOC-Interface-Nummer

Die Versionsprüfung vergleicht Versionsnummern unabhängig von der `## Interface`-Zeile.
Eine Abweichung wird zusätzlich als Hinweis angezeigt und verhindert nicht,
dass ein vorhandenes AddOn zur Aktualisierung ausgewählt wird.
Bei der Installation bleiben Paketprüfung, Änderungsvorschau, Bestandsschutz,
Backup und ausdrückliche Bestätigung erforderlich. Das gespeicherte
Interface-Profil des **tatsächlich ausgewählten WoW-Clients** wird für die
TOC-Anpassung verwendet. Eine Änderung dieser Metadaten beweist keine
Laufzeitkompatibilität mit beliebigen anderen WoW-Versionen.
