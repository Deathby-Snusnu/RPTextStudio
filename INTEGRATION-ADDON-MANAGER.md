# Integration: dynamische AddOn-Verwaltung

Dieser Branch kombiniert die Installer- und WoW-Erkennung (PR #10), GitHub-Prüfung (PR #11) und MagierRP-Generator (PR #12).

## Ablauf

1. RPAddOns-Projektwurzel in RP Text Studio öffnen.
2. Projekt → Neues Klassen-AddOn erstellen: erzeugt addons/MagierRP und registriert es in addons.json.
3. Projekt → AddOn-Installer / Updates: erkennt alle lokalen AddOn-Ordner mit gleichnamiger TOC dynamisch.
4. Vorschau prüfen, Ziel auswählen, Backup und lokale Installation explizit bestätigen.
5. GitHub-Updates prüfen: ausschließlich Versionsprüfung, keine Downloads.

## Herkunftssicherung

Neue AddOns ohne bestätigte GitHub-Zuordnung werden als Nicht zugeordnet angezeigt. Die sechs bisherigen Repositories haben eine Legacy-Zuordnung bei vorhandener lokaler Quelle. Für neue Projekte wird nur eine explizite Zuordnung Deathby-Snusnu/<AddOn-ID> akzeptiert. Andere Repositories werden nicht stillschweigend kontaktiert.

## Tests

python -m unittest discover -s tests

Zusätzlich sind die Lua-Ladefolge und die Sicherungs-/Wiederherstellungswege unter Windows und WoW Forever mit einem Testverzeichnis zu prüfen. Keine produktive Freigabe vor erfolgreichen Tests.
