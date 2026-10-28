# MagierRP: Zauber und RP-Texte (erste Ausbaustufe)

MagierRP kann bereits durch den Projektgenerator von RP Text Studio erstellt
werden. Dieser PR erweitert die Generator-Vorlage um 28 strukturierte
Zauberschlüssel mit deutschen, englischen und französischen RP-Texten.

Die Texte unterscheiden gesprochene Sprüche (`/say`) von markierten
`*Emotes*` (`/me`). Jeder Schlüssel besitzt neutrale Gruppentexte;
Zieltexte verwenden `%s` für den Zielnamen.

## Bereiche

- Feuer: FIREBALL, FIRE_BLAST, PYROBLAST, FLAMESTRIKE, SCORCH
- Frost: FROSTBOLT, BLIZZARD, FROST_NOVA, CONE_OF_COLD, ICE_BARRIER, ICE_BLOCK
- Arkan: ARCANE_MISSILES, ARCANE_EXPLOSION, COUNTERSPELL, POLYMORPH
- Mobilität: BLINK, SLOW_FALL, TELEPORT, PORTAL
- Unterstützung: ARCANE_INTELLECT, ARCANE_BRILLIANCE, MANA_SHIELD,
  EVOCATION, REMOVE_LESSER_CURSE, DETECT_MAGIC
- Versorgung: CONJURE_FOOD, CONJURE_WATER, CREATE_MANA_GEM

## Bedienung im Spiel

- `/mrp help` zeigt die kurze Hilfe
- `/mrp list` zeigt sämtliche unterstützten Zauberschlüssel
- `/mrp FIREBALL`, `/mrp FROST_NOVA`, `/mrp POLYMORPH` geben zufällige
  Rollenspieltexte aus
- `/magierrp` ist ein Alias zu `/mrp`

Die Befehle erzeugen **Rollenspieltext**. Es wird dadurch kein Zauber gewirkt.
Die automatische Zuordnung zu echten Spellcasts sowie reichhaltige Ambient-,
Rassen- und Situationssysteme werden in weiteren Schritten ergänzt.

## Sicherheit und Kompatibilität

Der Generator überschreibt ein bereits vorhandenes MagierRP-Projekt nicht.
Die Vorlage verwendet die vorhandene `MAGE`-Klassenprüfung,
charaktergebundene Einstellungen, Chat-Ausgabe und den Cooldown.
Buffs für Freunde und Selbstzauber unterscheiden sich in der Zielauflösung.
Die Interface-Nummer 16001 ist ein vom Generator gewähltes Profil, kein Beweis
für die Kompatibilität mit anderen Classic+-Clients.

Noch kein öffentliches separates MagierRP-Repository und daher noch keine
automatische Bereitstellung im universellen GitHub-Katalog.
Nach Erzeugung und WoW-Live-Test kann das AddOn als eigenes Repository mit
Release veröffentlicht und im Katalog registriert werden.

## Test

`python -m pytest tests/test_extended_mage_catalog.py tests/test_addon_project_generator.py -v`

Danach in einer isolierten RPAddOns-Testwurzel MagierRP neu generieren und
im passenden WoW-Client `/mrp list` sowie einzelne Schlüssel testen.
