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
BANKS["enUS"] = {"FIRE":["Fire has always been an honest negotiator.","*spins a ribbon of amber sparks.*"],"FROST":["Even the air holds its breath.","*draws a ring of tiny ice crystals.*"],"ARCANE":["The equation is elegant. The consequences less so.","*aligns several violet glyphs.*"],"POLYMORPH":["A woollier appearance might suit you.","*sketches the outline of a sheep.*"],"PORTAL":["Please keep your limbs inside the portal.","*double-checks the destination coordinates.*"],"TELEPORT":["The shortest route may bend through space.","*folds a map into a glowing speck.*"],"CONJURE":["A respectable meal is high magic too.","*shakes sparks from a sleeve.*"],"WARD":["Caution is an art, not a weakness.","*draws a shimmering protective circle.*"],"BUFF":["A keen mind is a useful gift.","*passes on a softly shining glyph.*"],"UTILITY":["There is a formula for almost everything.","*turns to the right page of a spellbook.*"]}
BANKS["frFR"] = {"FIRE":["Le feu est un négociateur sincère.","*fait danser des étincelles ambrées.*"],"FROST":["Même l'air retient son souffle.","*dessine un cercle de cristaux de glace.*"],"ARCANE":["L'équation est élégante. Les conséquences, moins.","*aligne des glyphes violets.*"],"POLYMORPH":["Un peu de laine vous irait bien.","*esquisse la silhouette d'un mouton.*"],"PORTAL":["Gardez vos membres à l'intérieur du portail.","*vérifie deux fois les coordonnées.*"],"TELEPORT":["Le plus court chemin traverse parfois l'espace.","*plie une carte en une étincelle.*"],"CONJURE":["Un bon repas relève aussi de la haute magie.","*secoue des étincelles de sa manche.*"],"WARD":["La prudence est un art, pas une faiblesse.","*trace un cercle protecteur scintillant.*"],"BUFF":["Un esprit vif est un beau cadeau.","*transmet un glyphe lumineux.*"],"UTILITY":["Il existe une formule pour presque tout.","*ouvre un grimoire à la bonne page.*"]}
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
