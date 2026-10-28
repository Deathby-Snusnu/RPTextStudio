"""Race-specific and neutral mage ambience, output as SAY or *EMOTE*."""
RACES = ("GNOME", "HUMAN", "HIGH_ELF", "BLOODELF", "NIGHTELF", "UNDEAD", "TROLL", "ORC", "DRAENEI", "DWARF")
THEMES = {
    "deDE": {
        "GNOME": ["Meine neueste Formel hat nur noch zwölf unbekannte Variablen.", "*kalibriert einen winzigen, summenden Arkandetektor.*", "Es gibt keine Fehlzündung. Nur unerwartete Forschungsergebnisse.", "*notiert eine Messreihe auf dem Ärmel seiner Robe.*", "Die Explosion lag innerhalb der statistischen Toleranz!"],
        "HUMAN": ["Disziplin ist die erste Lektion jeder Zauberschule.", "*prüft die saubere Linienführung einer arkanen Glyphe.*", "Macht ohne Beherrschung ist keine Kunst.", "*schließt das Zauberbuch mit bedächtiger Geste.*", "Auch ein Erzmagier beginnt jeden Morgen mit Grundlagen."],
        "HIGH_ELF": ["Die Leylinien bewahren Erinnerungen älter als jedes Königreich.", "*lauscht dem feinen Gesang arkaner Ströme.*", "Geduld ist die seltenste Gabe der jungen Völker.", "*glättet ehrfürchtig eine uralte Zauberseite.*", "Selbst Sterne verblassen vor dem Gedächtnis der Magie."],
        "BLOODELF": ["Arkanes Wirken verlangt Anmut und eine tadellose Haltung.", "*ordnet eine Reihe schimmernder Kristalle.*", "Präzision ist eine Form von Eleganz.", "*betrachtet kritisch die Symmetrie eines Zauberkreises.*", "Ein ungeschliffener Zauber ist eine Beleidigung für die Sinne."],
        "NIGHTELF": ["Selbst die Sterne flüstern von verborgener Magie.", "*beobachtet schweigend das Licht zwischen den Blättern.*", "Alte Macht verlangt noch ältere Vorsicht.", "*zeichnet ein silbriges Zeichen auf den Waldboden.*", "Der Wald vergisst keinen unbedachten Zauber."],
        "UNDEAD": ["Meine Hände sind kalt, doch die Formeln sitzen.", "*bläst Staub von einem verdächtig alten Folianten.*", "Manche Probleme überdauern sogar den Tod.", "*betrachtet einen schwebenden Funken mit trockenem Interesse.*", "Meine Konzentration ist seit dem letzten Atemzug bemerkenswert stabil."],
        "TROLL": ["Die Ahnen kennen mehr Wege der Macht als jedes Buch.", "*murmelt eine alte Formel und zeichnet ein Zeichen in den Staub.*", "Magie ohne Respekt vor den Geistern ist leer.", "*prüft sorgsam ein Bündel beschrifteter Talismane.*", "Lass die Ströme fließen, aber hör ihnen auch zu."],
        "ORC": ["Ein starker Wille lenkt selbst widerspenstige Magie.", "*presst die Finger zusammen, bis ein Funke aufspringt.*", "Ein guter Zauber braucht Mut und Verstand.", "*zieht mit einer entschlossenen Bewegung eine Rune.*", "Wer seine Kraft kennt, muss sie nicht verschwenden."],
        "DRAENEI": ["Das Licht der Sterne weist auch den arkanen Künsten den Weg.", "*betrachtet eine schwebende geometrische Figur.*", "Weisheit wächst aus Demut und Geduld.", "*ordnet die Linien eines leuchtenden Siegels.*", "Möge das Wissen uns dienen und niemals beherrschen."],
        "DWARF": ["Gute Magie hält mindestens so lange wie gutes Bier.", "*klopft skeptisch gegen einen summenden Zauberstein.*", "Hab schon instabilere Formeln gesehen. Und schlechteres Ale!", "*kritzelt eine Rune neben einen Bierfleck.*", "Ein ordentlicher Zauber muss auch einen Humpen überstehen."],
    },
    "enUS": {
        "GNOME": ["My calculations are almost entirely correct!", "*adjusts a humming arcane detector.*", "Unexpected explosions are simply new data."],
        "HUMAN": ["Discipline is the first lesson of magic.", "*straightens the lines of an arcane glyph.*", "Power without restraint is no art."],
        "HIGH_ELF": ["The ley lines remember ages long gone.", "*listens to the whisper of ancient magic.*", "Patience is rarer than power."],
        "BLOODELF": ["Precision is the purest elegance.", "*arranges glowing crystals with care.*", "A crude spell offends the senses."],
        "NIGHTELF": ["The stars remember every careless spell.", "*watches moonlight flicker between leaves.*", "Old power demands older wisdom."],
        "UNDEAD": ["My hands are cold, but my formulas remain sound.", "*dusts off an ancient spellbook.*", "Even death cannot interrupt a good study session."],
        "TROLL": ["The ancestors know paths no book contains.", "*traces an old symbol in the dust.*", "Listen to the spirits before you weave."],
        "ORC": ["A strong will bends stubborn magic.", "*draws a rune with a steady hand.*", "Strength means knowing when not to cast."],
        "DRAENEI": ["Wisdom grows from patience.", "*studies a floating constellation of runes.*", "Let knowledge guide us."],
        "DWARF": ["Good magic ought to survive a spilled ale.", "*taps a suspiciously humming mana stone.*", "I've seen worse formulas and worse beer."],
    },
    "frFR": {
        "GNOME": ["Mes calculs sont presque parfaitement exacts !", "*ajuste un détecteur arcanique bourdonnant.*", "Une explosion inattendue reste une découverte."],
        "HUMAN": ["La discipline est la première leçon de magie.", "*redresse les lignes d'un glyphe arcanique.*", "Le pouvoir sans maîtrise n'est pas un art."],
        "HIGH_ELF": ["Les lignes telluriques se souviennent des âges anciens.", "*écoute le murmure d'une magie antique.*", "La patience est plus rare que la puissance."],
        "BLOODELF": ["La précision est la plus pure élégance.", "*dispose soigneusement des cristaux lumineux.*", "Un sort grossier offense les sens."],
        "NIGHTELF": ["Les étoiles se souviennent de chaque sort imprudent.", "*observe la lumière de la lune dans les feuilles.*", "Une antique puissance exige de la sagesse."],
        "UNDEAD": ["Mes mains sont froides, mais mes formules sont intactes.", "*époussette un grimoire ancien.*", "Même la mort n'interrompt pas l'étude."],
        "TROLL": ["Les ancêtres connaissent des voies oubliées des livres.", "*trace un ancien signe dans la poussière.*", "Écoute les esprits avant d'agir."],
        "ORC": ["Une volonté forte maîtrise la magie rebelle.", "*dessine une rune d'un geste assuré.*", "La force sait aussi attendre."],
        "DRAENEI": ["La sagesse grandit avec la patience.", "*étudie une constellation de runes flottantes.*", "Que la connaissance nous guide."],
        "DWARF": ["Une bonne magie doit résister à la bière renversée.", "*tapote une pierre de mana suspecte.*", "J'ai connu de pires formules et de pires bières."],
    },
}
NEUTRAL = {
    "deDE": ["*blättert in einem abgegriffenen Zauberbuch.*", "Mana ist endlich. Meine Neugier leider nicht.", "*zieht einen schwebenden Funken aus der Luft.*", "Wer seine Formeln nicht kennt, sollte besser keine Portale öffnen.", "*prüft die Kreidelinien eines Zauberkreises.*", "Ich brauche nur noch eine letzte Berechnung. Vermutlich."],
    "enUS": ["*leafs through a battered spellbook.*", "Mana is finite. My curiosity is not.", "*plucks a glowing spark from the air.*", "One final calculation. Probably."],
    "frFR": ["*feuillette un grimoire usé.*", "Le mana est limité. Pas ma curiosité.", "*attrape une étincelle flottante.*", "Encore un dernier calcul. Probablement."],
}
