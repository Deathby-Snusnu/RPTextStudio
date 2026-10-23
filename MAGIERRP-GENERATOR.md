# MagierRP-Projektgenerator (Entwicklungsstand)

Menü: **Projekt → Neues Klassen-AddOn erstellen…** nach Öffnen der RPAddOns-Projektwurzel.

Der Generator erstellt das neue **addons/MagierRP/** aus Vorlagen mit:

- MagierRP.toc (Interface-Nummer und Startversion konfigurierbar)
- Core: Database, Text, Chat, Cooldown, Commands
- Konfiguration und Initialisierung
- deDE, enUS, frFR mit FIREBALL, FROSTBOLT, ARCANE_MISSILES und jeweils ziel/gruppe
- README, CHANGELOG und einfachem Lua-Smoke-Test
- dynamischem Registry-Eintrag in **addons.json** an der Projektwurzel

Vor dem Anlegen: vollständige Dateivorschau. Danach nur Erstellung, wenn Ziel noch nicht existiert. Ein GitHub-Repository wird **nicht** automatisch erstellt. Für die spätere Update-Prüfung kann der Registry-Eintrag nach Einrichtung eines eigenen GitHub-Repositories ergänzt werden.

## Grenzen

Diese erste Vorlage unterstützt nur MagierRP/MAGE. Die generierten Lua-Texte werden ausschließlich über /mrp oder /magierrp ausgegeben. Kein automatisches Reagieren auf Zauberereignisse. In der Entwicklungsphase Tests lokal ausführen und den AddOn-Start in WoW Forever separat prüfen.

Die Registry entdeckt gültige lokale AddOns anhand eines Ordners mit gleichnamiger .toc. Neu gefundene AddOns können ausdrücklich ins Register übernommen werden; es wird kein fremdes Repository allein aus einem Ordnernamen abgeleitet.

Testaufruf: `python -m unittest discover -s tests -p 'test_addon_project_generator.py'`.
