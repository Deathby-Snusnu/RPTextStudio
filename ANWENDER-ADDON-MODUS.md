# Anwender-Modus für RP-AddOns

Unter **AddOns → Anwender: Installierte AddOns prüfen…** kann RPTextStudio die installierten RP-AddOns ohne ein geöffnetes Entwicklungsprojekt anzeigen.

## Funktionen

- Suche nach gespeicherten und bekannten WoW-Installationen im Hintergrund.
- Bestätigte Clients auswählbar; Anzeige lokaler .toc-Versionen und Interface-Nummern der sechs bekannten RP-AddOns.
- Öffentliche GitHub-Versionen lassen sich ohne Anmeldung prüfen; `GH_TOKEN`
  oder `GITHUB_TOKEN` sind optional. Für private Repositories kann vorhandene
  Authentifizierung über `GH_TOKEN` oder `GITHUB_TOKEN` verwendet werden.
- Die reine Versionsprüfung verändert keine Dateien. Paketdownload und
  Installation sind separate, ausdrücklich gestartete Aktionen mit Vorschau;
  siehe [sichere Installation](SAFE-GITHUB-INSTALL.md).
- **AddOn herunterladen und prüfen…** legt ein geprüftes Paket außerhalb von
  WoW bereit. **Geprüftes Paket installieren…** schreibt erst nach Vorschau
  und ausdrücklicher Bestätigung in die ausgewählte WoW-Installation.
- Fehlende bekannte AddOns lassen sich gemeinsam vorbereiten und nach einer
  gemeinsamen Vorschau installieren; siehe
  [Erstinstallation](FIRST-INSTALL-RP-ADDONS.md).
- Die Auswahl weiterer WoW-Pfade erfolgt weiterhin über Projekt → WoW-Installation suchen; danach den Anwenderdialog erneut öffnen.

## Entwicklerfunktionen

Unter **AddOns → Entwickler: Lokale AddOns installieren…** bleibt der bestehende Installer mit expliziter Entwicklungsprojekt-Quelle und Vorschau erhalten.

## Grenzen und Tests

Der Modus kennt die sechs registrierten RP-AddOns; beliebige Repositories
werden nicht aus lokalen Ordnernamen abgeleitet. Ein vorbereitetes Paket ist
keine Kompatibilitätszusage. Die Versionsprüfung und das Staging ersetzen
keinen Windows- oder Ingame-Test.
