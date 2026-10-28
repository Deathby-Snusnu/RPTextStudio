"""Thematic speech and emote banks for mage spell families."""
BANKS = {"deDE": {
  "FIRE": [
    "Flammen sind ehrlicher als viele Verhandlungen.",
    "*entfacht eine Spirale bernsteinfarbener Funken.*",
    "Ich hoffe, Ihr mögt es knusprig.",
    "*zeichnet ein glühendes Siegel in die Luft.*"
  ],
  "FROST": [
    "Ruhe. Selbst die Luft hält jetzt den Atem an.",
    "*zieht einen Reif aus Eiskristallen durch die Luft.*",
    "Kälte belohnt jene, die Geduld haben.",
    "*lässt eine Schneeflocke auf der Hand wachsen.*"
  ],
  "ARCANE": [
    "Die Gleichung ist elegant. Die Folgen weniger.",
    "*ordnet schwebende Glyphen in einer exakten Reihe.*",
    "Magie ist Mathematik mit schlechterer Fehlerbehandlung.",
    "*spannt einen Faden aus violettem Licht.*"
  ],
  "POLYMORPH": [
    "Ein wenig Wolle würde Euch gut stehen.",
    "*überlegt kurz, ob Hörner besser wären.*",
    "Keine Sorge. Das ist meistens reversibel.",
    "*skizziert die Umrisse eines Schafes.*"
  ],
  "PORTAL": [
    "Bitte die Gliedmaßen innerhalb des Portals behalten.",
    "*prüft zweimal die Zielkoordinaten.*",
    "Reisekosten: etwas Mana und volles Vertrauen.",
    "*öffnet einen schimmernden Durchgang.*"
  ],
  "TELEPORT": [
    "Der kürzeste Weg ist gelegentlich sehr indirekt.",
    "*faltet eine Landkarte zu einem glühenden Punkt.*",
    "Falls ich verschwinde, waren es die Koordinaten.",
    "*prüft die Sterne und schließt die Augen.*"
  ],
  "CONJURE": [
    "Etwas Essbares ist auch eine Form hoher Magie.",
    "*schüttelt ein paar Funken aus dem Ärmel.*",
    "Hoffentlich ist die Rezeptur diesmal nicht zu süß.",
    "*prüft das frisch herbeigezauberte Ergebnis.*"
  ],
  "WARD": [
    "Vorsicht ist eine Kunst, keine Schwäche.",
    "*zieht einen leuchtenden Kreis um die Schultern.*",
    "Besser geschützt als überrascht.",
    "*prüft die Kanten eines schimmernden Schutzzaubers.*"
  ],
  "BUFF": [
    "Ein klarer Geist wirkt Wunder, ganz ohne Wunder.",
    "*legt zwei Finger an die Stirn.*",
    "Wissen ist der angenehmste aller Vorteile.",
    "*überträgt eine sanft leuchtende Glyphe.*"
  ],
  "UTILITY": [
    "Es gibt für alles eine Formel. Meistens.",
    "*schlägt die passende Seite seines Zauberbuchs auf.*",
    "Magie hilft auch bei kleinen Schwierigkeiten.",
    "*zeichnet ein unscheinbares Symbol.*"
  ]
}}
def theme_for(key):
    if key.startswith("PORTAL"): return "PORTAL"
    if key.startswith("TELEPORT") or key in ("BLINK", "SLOW_FALL"): return "TELEPORT"
    if key.startswith("POLYMORPH"): return "POLYMORPH"
    if key.startswith("CONJURE") or key.startswith("CREATE_MANA"): return "CONJURE"
    if key in ("ARCANE_INTELLECT", "ARCANE_BRILLIANCE", "AMPLIFY_MAGIC", "DAMPEN_MAGIC"): return "BUFF"
    if any(part in key for part in ("ARMOR", "WARD", "BARRIER", "SHIELD", "ICE_BLOCK")): return "WARD"
    if key in ("FIREBALL", "FIRE_BLAST", "PYROBLAST", "FLAMESTRIKE", "SCORCH", "BLAST_WAVE", "COMBUSTION", "FELFIRE"): return "FIRE"
    if key in ("FROSTBOLT", "BLIZZARD", "FROST_NOVA", "CONE_OF_COLD", "ICE_LANCE", "COLD_SNAP", "FROST_BLAST"): return "FROST"
    if key.startswith("ARCANE") or key in ("PRESENCE_OF_MIND", "EVOCATION", "COUNTERSPELL"): return "ARCANE"
    return "UTILITY"
