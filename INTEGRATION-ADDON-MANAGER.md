# Integration: dynamische AddOn-Verwaltung

Die Klassen-AddOns werden in eigenen GitHub-Repositories gepflegt.
RP Text Studio bearbeitet, erkennt, installiert und aktualisiert vorhandene
AddOns, erzeugt aber keine AddOn-Quellcodeprojekte.

## Ablauf

1. Vorhandene RPAddOns-Projektwurzel in RP Text Studio öffnen.
2. Bestehende AddOns werden über ihre gleichnamige TOC erkannt. Optional
   lassen sie sich mit dem unabhängigen `addon_registry.py` registrieren.
3. AddOns → Anwender: Installierte AddOns prüfen… öffnet die Verwaltung
   für bestätigte WoW-Installationen und den eingebauten AddOn-Katalog.
4. **GitHub-Versionen prüfen** liest Release-/Branch-Metadaten. **AddOn
   herunterladen und prüfen…** stellt ein validiertes Paket außerhalb
   von WoW bereit; die Installation benötigt eine Vorschau und
   ausdrückliche Bestätigung.
5. Fehlende bekannte AddOns können gesammelt vorbereitet und nach Vorschau
   installiert werden.

## Herkunftssicherung

Repository-Zuordnungen werden nicht allein aus Ordnernamen hergeleitet.
Externe Quellen bleiben durch die bestehende Vertrauensprüfung eingeschränkt.

## Tests

```powershell
python -m unittest discover -s tests
```

Zusätzlich Lua-Ladefolge und Backup/Rollback unter Windows und im WoW-Client prüfen.
