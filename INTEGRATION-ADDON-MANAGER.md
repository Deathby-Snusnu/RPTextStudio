# Integration: dynamische AddOn-Verwaltung

Diese Übersicht beschreibt die integrierten AddOn-Verwaltungsfunktionen.

## Ablauf

1. RPAddOns-Projektwurzel in RP Text Studio öffnen.
2. Projekt → Neues Klassen-AddOn erstellen: erzeugt `addons/MagierRP` nach
   Vorschau und registriert es in `addons.json`.
3. AddOns → Anwender: Installierte AddOns prüfen… öffnet die Verwaltung für
   bestätigte WoW-Installationen und die sechs bekannten RP-AddOns.
4. **GitHub-Versionen prüfen** liest Release-/Branch-Metadaten. **AddOn
   herunterladen und prüfen…** stellt ein validiertes Paket außerhalb von WoW
   bereit; die getrennte Installationsaktion benötigt eine Vorschau und
   ausdrückliche Bestätigung.
5. Fehlende bekannte AddOns können gesammelt vorbereitet und anschließend mit
   gemeinsamer Vorschau installiert werden.

## Herkunftssicherung

Neue AddOns ohne bestätigte GitHub-Zuordnung werden als nicht zugeordnet
angezeigt. Für neue Projekte wird nur eine explizite Zuordnung
`Deathby-Snusnu/<AddOn-ID>` akzeptiert. Andere Repositories werden nicht
still und automatisch kontaktiert.

## Tests

python -m unittest discover -s tests

Zusätzlich sind die Lua-Ladefolge und die Sicherungs-/Wiederherstellungswege unter Windows und WoW Forever mit einem Testverzeichnis zu prüfen. Keine produktive Freigabe vor erfolgreichen Tests.
