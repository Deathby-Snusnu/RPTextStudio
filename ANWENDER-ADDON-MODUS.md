# Anwender-Modus für RP-AddOns

Unter **AddOns → Anwender: Installierte AddOns prüfen…** kann RPTextStudio die installierten RP-AddOns ohne ein geöffnetes Entwicklungsprojekt anzeigen.

## Funktionen

- Suche nach gespeicherten und bekannten WoW-Installationen im Hintergrund.
- Bestätigte Clients auswählbar; Anzeige lokaler .toc-Versionen und Interface-Nummern der sechs bekannten RP-AddOns.
- GitHub-Abfrage für stabile Releases oder Entwicklungsstände über bereits vorhandene GitHub-CLI-Authentifizierung beziehungsweise GH_TOKEN.
- Kein Download, kein Austausch von Dateien, keine Installation und kein Schreibzugriff auf WoW.
- Die Auswahl weiterer WoW-Pfade erfolgt weiterhin über Projekt → WoW-Installation suchen; danach den Anwenderdialog erneut öffnen.

## Entwicklerfunktionen

Unter **AddOns → Entwickler: Lokale AddOns installieren…** bleibt der bestehende Installer mit expliziter Entwicklungsprojekt-Quelle und Vorschau erhalten.

## Grenzen und Tests

Dieser erste Anwender-Modus kennt die sechs bestehenden RP-AddOns. Frei konfigurierbare Repository-Listen und überprüfte GitHub-Updatepakete gehören noch nicht dazu. Die GUI- und Windows-Praxistests müssen vor der Freigabe durchgeführt werden. Die Python-Testdatei ist hinzugefügt, wurde hier aber noch nicht ausgeführt.
