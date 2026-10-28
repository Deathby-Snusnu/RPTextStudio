"""Extended MagierRP text catalog with class-neutral stable keys."""
SPELL_KEYS = ["FIREBALL","FROSTBOLT","ARCANE_MISSILES","FIRE_BLAST","PYROBLAST","FLAMESTRIKE","SCORCH","BLIZZARD","FROST_NOVA","CONE_OF_COLD","ICE_BARRIER","ICE_BLOCK","ARCANE_EXPLOSION","COUNTERSPELL","POLYMORPH","BLINK","SLOW_FALL","EVOCATION","ARCANE_INTELLECT","ARCANE_BRILLIANCE","MANA_SHIELD","CONJURE_FOOD","CONJURE_WATER","CREATE_MANA_GEM","PORTAL","TELEPORT","REMOVE_LESSER_CURSE","DETECT_MAGIC"]
SPELL_DATA = {
    "deDE": {
        "FIREBALL": {"name": "Feuerball", "ziel": ["Euch wird gleich warm, %s.","*wirkt Feuerball auf %s.*"], "gruppe": ["Euch wird gleich warm.","*konzentriert sich und entfesselt Feuerball.*"]},
        "FROSTBOLT": {"name": "Frostblitz", "ziel": ["Ein frostiger Gruß, %s.","*wirkt Frostblitz auf %s.*"], "gruppe": ["Ein frostiger Gruß.","*konzentriert sich und entfesselt Frostblitz.*"]},
        "ARCANE_MISSILES": {"name": "Arkane Geschosse", "ziel": ["Arkane Kräfte finden Euch, %s.","*wirkt Arkane Geschosse auf %s.*"], "gruppe": ["Arkane Kräfte finden Euch.","*konzentriert sich und entfesselt Arkane Geschosse.*"]},
        "FIRE_BLAST": {"name": "Feuerschlag", "ziel": ["Ein Funke genügt, %s!","*wirkt Feuerschlag auf %s.*"], "gruppe": ["Ein Funke genügt!","*konzentriert sich und entfesselt Feuerschlag.*"]},
        "PYROBLAST": {"name": "Pyroschlag", "ziel": ["Zeit für ein richtiges Feuerwerk, %s!","*wirkt Pyroschlag auf %s.*"], "gruppe": ["Zeit für ein richtiges Feuerwerk!","*konzentriert sich und entfesselt Pyroschlag.*"]},
        "FLAMESTRIKE": {"name": "Flammenstoß", "ziel": ["Der Boden selbst wird brennen!","*wirkt Flammenstoß auf %s.*"], "gruppe": ["Der Boden selbst wird brennen!","*konzentriert sich und entfesselt Flammenstoß.*"]},
        "SCORCH": {"name": "Versengen", "ziel": ["Nur ein kleiner Vorgeschmack, %s.","*wirkt Versengen auf %s.*"], "gruppe": ["Nur ein kleiner Vorgeschmack.","*konzentriert sich und entfesselt Versengen.*"]},
        "BLIZZARD": {"name": "Blizzard", "ziel": ["Der Winter kennt keine Gnade!","*wirkt Blizzard auf %s.*"], "gruppe": ["Der Winter kennt keine Gnade!","*konzentriert sich und entfesselt Blizzard.*"]},
        "FROST_NOVA": {"name": "Frostnova", "ziel": ["Keinen Schritt weiter, %s!","*wirkt Frostnova auf %s.*"], "gruppe": ["Keinen Schritt weiter!","*konzentriert sich und entfesselt Frostnova.*"]},
        "CONE_OF_COLD": {"name": "Kältekegel", "ziel": ["Ein Hauch des Nordens!","*wirkt Kältekegel auf %s.*"], "gruppe": ["Ein Hauch des Nordens!","*konzentriert sich und entfesselt Kältekegel.*"]},
        "ICE_BARRIER": {"name": "Eisbarriere", "ziel": [], "gruppe": ["Kälte ist mein Schild.","*konzentriert sich und entfesselt Eisbarriere.*"]},
        "ICE_BLOCK": {"name": "Eisblock", "ziel": [], "gruppe": ["Ich bin kurz nicht zu sprechen.","*konzentriert sich und entfesselt Eisblock.*"]},
        "ARCANE_EXPLOSION": {"name": "Arkane Explosion", "ziel": ["Abstand halten, die Magie wird unruhig!","*wirkt Arkane Explosion auf %s.*"], "gruppe": ["Abstand halten, die Magie wird unruhig!","*konzentriert sich und entfesselt Arkane Explosion.*"]},
        "COUNTERSPELL": {"name": "Gegenzauber", "ziel": ["Eure Worte enden hier, %s!","*wirkt Gegenzauber auf %s.*"], "gruppe": ["Eure Worte enden hier!","*konzentriert sich und entfesselt Gegenzauber.*"]},
        "POLYMORPH": {"name": "Verwandlung", "ziel": ["Ein wenig Wolle steht Euch gut, %s.","*wirkt Verwandlung auf %s.*"], "gruppe": ["Ein wenig Wolle steht Euch gut.","*konzentriert sich und entfesselt Verwandlung.*"]},
        "BLINK": {"name": "Blinzeln", "ziel": [], "gruppe": ["Einen Augenblick, ich bin gleich woanders.","*konzentriert sich und entfesselt Blinzeln.*"]},
        "SLOW_FALL": {"name": "Langsamer Fall", "ziel": ["Die Schwerkraft kann heute warten.","*wirkt Langsamer Fall auf %s.*"], "gruppe": ["Die Schwerkraft kann heute warten.","*konzentriert sich und entfesselt Langsamer Fall.*"]},
        "EVOCATION": {"name": "Hervorrufung", "ziel": [], "gruppe": ["Einen Moment, ich sammle meine Gedanken und mein Mana.","*konzentriert sich und entfesselt Hervorrufung.*"]},
        "ARCANE_INTELLECT": {"name": "Arkane Intelligenz", "ziel": ["Ein klarer Geist ist die beste Waffe, %s.","*wirkt Arkane Intelligenz auf %s.*"], "gruppe": ["Ein klarer Geist ist die beste Waffe.","*konzentriert sich und entfesselt Arkane Intelligenz.*"]},
        "ARCANE_BRILLIANCE": {"name": "Arkane Brillanz", "ziel": ["Mögen unsere Gedanken heller leuchten!","*wirkt Arkane Brillanz auf %s.*"], "gruppe": ["Mögen unsere Gedanken heller leuchten!","*konzentriert sich und entfesselt Arkane Brillanz.*"]},
        "MANA_SHIELD": {"name": "Manaschild", "ziel": [], "gruppe": ["Mana zu Schutz, Gedanken zu Stahl.","*konzentriert sich und entfesselt Manaschild.*"]},
        "CONJURE_FOOD": {"name": "Essen herbeizaubern", "ziel": [], "gruppe": ["Ein bisschen Magie gegen den Hunger.","*konzentriert sich und entfesselt Essen herbeizaubern.*"]},
        "CONJURE_WATER": {"name": "Wasser herbeizaubern", "ziel": [], "gruppe": ["Frisches Wasser aus reiner Magie.","*konzentriert sich und entfesselt Wasser herbeizaubern.*"]},
        "CREATE_MANA_GEM": {"name": "Manastein erschaffen", "ziel": [], "gruppe": ["Ein kleiner Vorrat für große Not.","*konzentriert sich und entfesselt Manastein erschaffen.*"]},
        "PORTAL": {"name": "Portal", "ziel": [], "gruppe": ["Bitte beim Durchgang keine Gliedmaßen verlieren.","*konzentriert sich und entfesselt Portal.*"]},
        "TELEPORT": {"name": "Teleportieren", "ziel": [], "gruppe": ["Ich nehme die Abkürzung durch das Raumgefüge.","*konzentriert sich und entfesselt Teleportieren.*"]},
        "REMOVE_LESSER_CURSE": {"name": "Geringen Fluch aufheben", "ziel": ["Der Fluch hat hier nichts verloren, %s.","*wirkt Geringen Fluch aufheben auf %s.*"], "gruppe": ["Der Fluch hat hier nichts verloren.","*konzentriert sich und entfesselt Geringen Fluch aufheben.*"]},
        "DETECT_MAGIC": {"name": "Magie entdecken", "ziel": ["Mal sehen, welche Geheimnisse Ihr tragt, %s.","*wirkt Magie entdecken auf %s.*"], "gruppe": ["Mal sehen, welche Geheimnisse Ihr tragt.","*konzentriert sich und entfesselt Magie entdecken.*"]},
    },
    "enUS": {
        "FIREBALL": {"name": "Fireball", "ziel": ["Feel the heat, %s.","*casts Fireball on %s.*"], "gruppe": ["Feel the heat.","*conjures Fireball.*"]},
        "FROSTBOLT": {"name": "Frostbolt", "ziel": ["A chilly greeting, %s.","*casts Frostbolt on %s.*"], "gruppe": ["A chilly greeting.","*conjures Frostbolt.*"]},
        "ARCANE_MISSILES": {"name": "Arcane Missiles", "ziel": ["Arcane energies seek you, %s.","*casts Arcane Missiles on %s.*"], "gruppe": ["Arcane energies seek you.","*conjures Arcane Missiles.*"]},
        "FIRE_BLAST": {"name": "Fire Blast", "ziel": ["One spark will do, %s!","*casts Fire Blast on %s.*"], "gruppe": ["One spark will do!","*conjures Fire Blast.*"]},
        "PYROBLAST": {"name": "Pyroblast", "ziel": ["Time for a proper firestorm, %s!","*casts Pyroblast on %s.*"], "gruppe": ["Time for a proper firestorm!","*conjures Pyroblast.*"]},
        "FLAMESTRIKE": {"name": "Flamestrike", "ziel": ["The ground itself shall burn!","*casts Flamestrike on %s.*"], "gruppe": ["The ground itself shall burn!","*conjures Flamestrike.*"]},
        "SCORCH": {"name": "Scorch", "ziel": ["Just a taste of fire, %s.","*casts Scorch on %s.*"], "gruppe": ["Just a taste of fire.","*conjures Scorch.*"]},
        "BLIZZARD": {"name": "Blizzard", "ziel": ["Winter shows no mercy!","*casts Blizzard on %s.*"], "gruppe": ["Winter shows no mercy!","*conjures Blizzard.*"]},
        "FROST_NOVA": {"name": "Frost Nova", "ziel": ["Not another step, %s!","*casts Frost Nova on %s.*"], "gruppe": ["Not another step!","*conjures Frost Nova.*"]},
        "CONE_OF_COLD": {"name": "Cone of Cold", "ziel": ["A breath of the north!","*casts Cone of Cold on %s.*"], "gruppe": ["A breath of the north!","*conjures Cone of Cold.*"]},
        "ICE_BARRIER": {"name": "Ice Barrier", "ziel": [], "gruppe": ["Cold is my shield.","*conjures Ice Barrier.*"]},
        "ICE_BLOCK": {"name": "Ice Block", "ziel": [], "gruppe": ["I am briefly unavailable.","*conjures Ice Block.*"]},
        "ARCANE_EXPLOSION": {"name": "Arcane Explosion", "ziel": ["Stand back, the magic is restless!","*casts Arcane Explosion on %s.*"], "gruppe": ["Stand back, the magic is restless!","*conjures Arcane Explosion.*"]},
        "COUNTERSPELL": {"name": "Counterspell", "ziel": ["Your incantation ends here, %s!","*casts Counterspell on %s.*"], "gruppe": ["Your incantation ends here!","*conjures Counterspell.*"]},
        "POLYMORPH": {"name": "Polymorph", "ziel": ["A little wool suits you, %s.","*casts Polymorph on %s.*"], "gruppe": ["A little wool suits you.","*conjures Polymorph.*"]},
        "BLINK": {"name": "Blink", "ziel": [], "gruppe": ["Just a moment, I will be elsewhere.","*conjures Blink.*"]},
        "SLOW_FALL": {"name": "Slow Fall", "ziel": ["Gravity can wait today.","*casts Slow Fall on %s.*"], "gruppe": ["Gravity can wait today.","*conjures Slow Fall.*"]},
        "EVOCATION": {"name": "Evocation", "ziel": [], "gruppe": ["A moment to gather my thoughts and mana.","*conjures Evocation.*"]},
        "ARCANE_INTELLECT": {"name": "Arcane Intellect", "ziel": ["A sharp mind is your finest weapon, %s.","*casts Arcane Intellect on %s.*"], "gruppe": ["A sharp mind is your finest weapon.","*conjures Arcane Intellect.*"]},
        "ARCANE_BRILLIANCE": {"name": "Arcane Brilliance", "ziel": ["May our minds shine brighter!","*casts Arcane Brilliance on %s.*"], "gruppe": ["May our minds shine brighter!","*conjures Arcane Brilliance.*"]},
        "MANA_SHIELD": {"name": "Mana Shield", "ziel": [], "gruppe": ["Mana into shelter, thought into steel.","*conjures Mana Shield.*"]},
        "CONJURE_FOOD": {"name": "Conjure Food", "ziel": [], "gruppe": ["A little magic against hunger.","*conjures Conjure Food.*"]},
        "CONJURE_WATER": {"name": "Conjure Water", "ziel": [], "gruppe": ["Fresh water, drawn from pure magic.","*conjures Conjure Water.*"]},
        "CREATE_MANA_GEM": {"name": "Conjure Mana Gem", "ziel": [], "gruppe": ["A little reserve for dire moments.","*conjures Conjure Mana Gem.*"]},
        "PORTAL": {"name": "Portal", "ziel": [], "gruppe": ["Mind your limbs when stepping through.","*conjures Portal.*"]},
        "TELEPORT": {"name": "Teleport", "ziel": [], "gruppe": ["I shall take the shortcut through space.","*conjures Teleport.*"]},
        "REMOVE_LESSER_CURSE": {"name": "Remove Lesser Curse", "ziel": ["This curse has no place here, %s.","*casts Remove Lesser Curse on %s.*"], "gruppe": ["This curse has no place here.","*conjures Remove Lesser Curse.*"]},
        "DETECT_MAGIC": {"name": "Detect Magic", "ziel": ["Let us see what secrets you carry, %s.","*casts Detect Magic on %s.*"], "gruppe": ["Let us see what secrets you carry.","*conjures Detect Magic.*"]},
    },
    "frFR": {
        "FIREBALL": {"name": "Boule de feu", "ziel": ["Sentez la chaleur, %s !","*lance Boule de feu on %s.*"], "gruppe": ["Sentez la chaleur !","*conjures Boule de feu.*"]},
        "FROSTBOLT": {"name": "Éclair de givre", "ziel": ["Un salut glacé, %s !","*lance Éclair de givre on %s.*"], "gruppe": ["Un salut glacé !","*conjures Éclair de givre.*"]},
        "ARCANE_MISSILES": {"name": "Projectiles des Arcanes", "ziel": ["Les énergies arcaniques vous cherchent, %s !","*lance Projectiles des Arcanes on %s.*"], "gruppe": ["Les énergies arcaniques vous cherchent !","*conjures Projectiles des Arcanes.*"]},
        "FIRE_BLAST": {"name": "Trait de feu", "ziel": ["Une étincelle suffit, %s !","*lance Trait de feu on %s.*"], "gruppe": ["Une étincelle suffit !","*conjures Trait de feu.*"]},
        "PYROBLAST": {"name": "Explosion pyrotechnique", "ziel": ["Place au grand brasier, %s !","*lance Explosion pyrotechnique on %s.*"], "gruppe": ["Place au grand brasier !","*conjures Explosion pyrotechnique.*"]},
        "FLAMESTRIKE": {"name": "Choc de flammes", "ziel": ["Le sol lui-même brûlera !","*lance Choc de flammes on %s.*"], "gruppe": ["Le sol lui-même brûlera !","*conjures Choc de flammes.*"]},
        "SCORCH": {"name": "Brûlure", "ziel": ["Un avant-goût du feu, %s.","*lance Brûlure on %s.*"], "gruppe": ["Un avant-goût du feu.","*conjures Brûlure.*"]},
        "BLIZZARD": {"name": "Blizzard", "ziel": ["L'hiver est sans pitié !","*lance Blizzard on %s.*"], "gruppe": ["L'hiver est sans pitié !","*conjures Blizzard.*"]},
        "FROST_NOVA": {"name": "Nova de givre", "ziel": ["Pas un pas de plus, %s !","*lance Nova de givre on %s.*"], "gruppe": ["Pas un pas de plus !","*conjures Nova de givre.*"]},
        "CONE_OF_COLD": {"name": "Cône de froid", "ziel": ["Un souffle du nord !","*lance Cône de froid on %s.*"], "gruppe": ["Un souffle du nord !","*conjures Cône de froid.*"]},
        "ICE_BARRIER": {"name": "Barrière de glace", "ziel": [], "gruppe": ["Le froid est mon bouclier.","*conjures Barrière de glace.*"]},
        "ICE_BLOCK": {"name": "Bloc de glace", "ziel": [], "gruppe": ["Je suis momentanément indisponible.","*conjures Bloc de glace.*"]},
        "ARCANE_EXPLOSION": {"name": "Explosion des Arcanes", "ziel": ["Reculez, la magie s'agite !","*lance Explosion des Arcanes on %s.*"], "gruppe": ["Reculez, la magie s'agite !","*conjures Explosion des Arcanes.*"]},
        "COUNTERSPELL": {"name": "Contresort", "ziel": ["Votre incantation s'arrête ici, %s !","*lance Contresort on %s.*"], "gruppe": ["Votre incantation s'arrête ici !","*conjures Contresort.*"]},
        "POLYMORPH": {"name": "Métamorphose", "ziel": ["Un peu de laine vous va bien, %s.","*lance Métamorphose on %s.*"], "gruppe": ["Un peu de laine vous va bien.","*conjures Métamorphose.*"]},
        "BLINK": {"name": "Transfert", "ziel": [], "gruppe": ["Un instant, je serai ailleurs.","*conjures Transfert.*"]},
        "SLOW_FALL": {"name": "Chute lente", "ziel": ["La gravité attendra aujourd'hui.","*lance Chute lente on %s.*"], "gruppe": ["La gravité attendra aujourd'hui.","*conjures Chute lente.*"]},
        "EVOCATION": {"name": "Évocation", "ziel": [], "gruppe": ["Un instant pour rassembler mes pensées et mon mana.","*conjures Évocation.*"]},
        "ARCANE_INTELLECT": {"name": "Intelligence des Arcanes", "ziel": ["Un esprit vif est votre meilleure arme, %s.","*lance Intelligence des Arcanes on %s.*"], "gruppe": ["Un esprit vif est votre meilleure arme.","*conjures Intelligence des Arcanes.*"]},
        "ARCANE_BRILLIANCE": {"name": "Illumination des Arcanes", "ziel": ["Que nos esprits brillent davantage !","*lance Illumination des Arcanes on %s.*"], "gruppe": ["Que nos esprits brillent davantage !","*conjures Illumination des Arcanes.*"]},
        "MANA_SHIELD": {"name": "Bouclier de mana", "ziel": [], "gruppe": ["Le mana me protège, la pensée devient acier.","*conjures Bouclier de mana.*"]},
        "CONJURE_FOOD": {"name": "Invocation de nourriture", "ziel": [], "gruppe": ["Un peu de magie contre la faim.","*conjures Invocation de nourriture.*"]},
        "CONJURE_WATER": {"name": "Invocation d'eau", "ziel": [], "gruppe": ["De l'eau fraîche, née de la magie.","*conjures Invocation d'eau.*"]},
        "CREATE_MANA_GEM": {"name": "Invocation d'une gemme de mana", "ziel": [], "gruppe": ["Une petite réserve pour les urgences.","*conjures Invocation d'une gemme de mana.*"]},
        "PORTAL": {"name": "Portail", "ziel": [], "gruppe": ["Attention à vos membres en traversant.","*conjures Portail.*"]},
        "TELEPORT": {"name": "Téléportation", "ziel": [], "gruppe": ["Je prends un raccourci à travers l'espace.","*conjures Téléportation.*"]},
        "REMOVE_LESSER_CURSE": {"name": "Délivrance de la malédiction mineure", "ziel": ["Cette malédiction n'a pas sa place ici, %s.","*lance Délivrance de la malédiction mineure on %s.*"], "gruppe": ["Cette malédiction n'a pas sa place ici.","*conjures Délivrance de la malédiction mineure.*"]},
        "DETECT_MAGIC": {"name": "Détection de la magie", "ziel": ["Voyons quels secrets vous portez, %s.","*lance Détection de la magie on %s.*"], "gruppe": ["Voyons quels secrets vous portez.","*conjures Détection de la magie.*"]},
    },
}
FRIENDLY_KEYS = ["ARCANE_INTELLECT","ARCANE_BRILLIANCE","SLOW_FALL","REMOVE_LESSER_CURSE"]
SELF_KEYS = ["ICE_BARRIER","ICE_BLOCK","BLINK","EVOCATION","MANA_SHIELD","CONJURE_FOOD","CONJURE_WATER","CREATE_MANA_GEM","PORTAL","TELEPORT"]

# Additional Classic/Forever candidate keys. Talent spells and client-specific
# additions are data entries only; availability is not assumed at runtime.
ADDITIONAL_MAGE_SPELLS = ["DAMPEN_MAGIC","AMPLIFY_MAGIC","FROST_ARMOR","ICE_ARMOR","MAGE_ARMOR","FIRE_WARD","FROST_WARD","ARCANE_BLAST","ARCANE_WRATH","ARCANE_POWER","PRESENCE_OF_MIND","BLAST_WAVE","COMBUSTION","FROSTFIRE_BOLT","FELFIRE","ICE_LANCE","FROST_BLAST","COLD_SNAP","CONJURE_MANA_AGATE","CONJURE_MANA_JADE","CONJURE_MANA_CITRINE","CONJURE_MANA_RUBY","POLYMORPH_COW","COMPREHEND_SCROLL","STUDY","TELEPORT_STORMWIND","PORTAL_STORMWIND","TELEPORT_IRONFORGE","PORTAL_IRONFORGE","TELEPORT_DARNASSUS","PORTAL_DARNASSUS","TELEPORT_DALARAN","PORTAL_DALARAN","TELEPORT_ORGRIMMAR","PORTAL_ORGRIMMAR","TELEPORT_UNDERCITY","PORTAL_UNDERCITY","TELEPORT_THUNDER_BLUFF","PORTAL_THUNDER_BLUFF"]
_additional = [["DAMPEN_MAGIC","Magie dämpfen","Dampen Magic","Atténuation de la magie","Magische Strömungen werden leiser."],["AMPLIFY_MAGIC","Magie verstärken","Amplify Magic","Amplification de la magie","Mehr Magie, mehr Möglichkeiten."],["FROST_ARMOR","Frostrüstung","Frost Armor","Armure de givre","Ein frostiger Mantel steht mir gut."],["ICE_ARMOR","Eisrüstung","Ice Armor","Armure de glace","Ein Schutzpanzer aus klirrendem Eis."],["MAGE_ARMOR","Magische Rüstung","Mage Armor","Armure du mage","Mein Geist ist mein bester Panzer."],["FIRE_WARD","Feuerzauberschutz","Fire Ward","Gardien de feu","Feuer soll mich nicht verzehren."],["FROST_WARD","Frostzauberschutz","Frost Ward","Gardien de givre","Die Kälte gehorcht mir."],["ARCANE_BLAST","Arkanbeschuss","Arcane Blast","Déflagration des arcanes","Arkane Energie bricht hervor!"],["ARCANE_WRATH","Arkaner Zorn","Arcane Wrath","Courroux des arcanes","Die arkanen Ströme antworten auf meinen Zorn."],["ARCANE_POWER","Arkane Macht","Arcane Power","Pouvoir des arcanes","Mehr Macht, doch zu welchem Preis?"],["PRESENCE_OF_MIND","Geistesgegenwart","Presence of Mind","Présence spirituelle","Ein Gedanke genügt."],["BLAST_WAVE","Druckwelle","Blast Wave","Vague explosive","Ein Sturm aus Feuer und Wucht!"],["COMBUSTION","Verbrennung","Combustion","Combustion","Die Glut erwacht."],["FROSTFIRE_BOLT","Frostfeuerblitz","Frostfire Bolt","Éclair de givrefeu","Feuer und Eis im selben Atemzug!"],["FELFIRE","Teufelsfeuer","Felfire","Gangrefeu","Diese Flamme hat einen düsteren Ursprung."],["ICE_LANCE","Eislanze","Ice Lance","Lance de glace","Ein Splitter genügt."],["FROST_BLAST","Frostschlag","Frost Blast","Explosion de givre","Der Frost findet seinen Weg."],["COLD_SNAP","Kälteeinbruch","Cold Snap","Morsure du froid","Der Winter kehrt zurück."],["CONJURE_MANA_AGATE","Manaachat herbeizaubern","Conjure Mana Agate","Invocation d'agate de mana","Ein kleiner arkaner Vorrat."],["CONJURE_MANA_JADE","Manajadestein herbeizaubern","Conjure Mana Jade","Invocation de jade de mana","Ein bisschen Mana für später."],["CONJURE_MANA_CITRINE","Manacitrin herbeizaubern","Conjure Mana Citrine","Invocation de citrine de mana","Dieser Stein bewahrt meine Reserven."],["CONJURE_MANA_RUBY","Manarubin herbeizaubern","Conjure Mana Ruby","Invocation de rubis de mana","Eine kostbare Reserve für den Notfall."],["POLYMORPH_COW","Verwandlung: Kuh","Polymorph: Cow","Métamorphose : vache","Ein Muh ist auch eine Antwort."],["COMPREHEND_SCROLL","Schriftrolle verstehen","Comprehend Scroll","Compréhension du parchemin","Die Zeichen ergeben langsam Sinn."],["STUDY","Studieren","Study","Étude","Wissen ist Macht, Geduld ist der Schlüssel."],["TELEPORT_STORMWIND","Teleport: STORMWIND","Teleport: STORMWIND","Téléportation : STORMWIND","Eine Abkürzung nach STORMWIND."],["PORTAL_STORMWIND","Portal: STORMWIND","Portal: STORMWIND","Portail : STORMWIND","Der Weg nach STORMWIND ist offen."],["TELEPORT_IRONFORGE","Teleport: IRONFORGE","Teleport: IRONFORGE","Téléportation : IRONFORGE","Eine Abkürzung nach IRONFORGE."],["PORTAL_IRONFORGE","Portal: IRONFORGE","Portal: IRONFORGE","Portail : IRONFORGE","Der Weg nach IRONFORGE ist offen."],["TELEPORT_DARNASSUS","Teleport: DARNASSUS","Teleport: DARNASSUS","Téléportation : DARNASSUS","Eine Abkürzung nach DARNASSUS."],["PORTAL_DARNASSUS","Portal: DARNASSUS","Portal: DARNASSUS","Portail : DARNASSUS","Der Weg nach DARNASSUS ist offen."],["TELEPORT_DALARAN","Teleport: DALARAN","Teleport: DALARAN","Téléportation : DALARAN","Eine Abkürzung nach DALARAN."],["PORTAL_DALARAN","Portal: DALARAN","Portal: DALARAN","Portail : DALARAN","Der Weg nach DALARAN ist offen."],["TELEPORT_ORGRIMMAR","Teleport: ORGRIMMAR","Teleport: ORGRIMMAR","Téléportation : ORGRIMMAR","Eine Abkürzung nach ORGRIMMAR."],["PORTAL_ORGRIMMAR","Portal: ORGRIMMAR","Portal: ORGRIMMAR","Portail : ORGRIMMAR","Der Weg nach ORGRIMMAR ist offen."],["TELEPORT_UNDERCITY","Teleport: UNDERCITY","Teleport: UNDERCITY","Téléportation : UNDERCITY","Eine Abkürzung nach UNDERCITY."],["PORTAL_UNDERCITY","Portal: UNDERCITY","Portal: UNDERCITY","Portail : UNDERCITY","Der Weg nach UNDERCITY ist offen."],["TELEPORT_THUNDER_BLUFF","Teleport: THUNDER_BLUFF","Teleport: THUNDER_BLUFF","Téléportation : THUNDER_BLUFF","Eine Abkürzung nach THUNDER_BLUFF."],["PORTAL_THUNDER_BLUFF","Portal: THUNDER_BLUFF","Portal: THUNDER_BLUFF","Portail : THUNDER_BLUFF","Der Weg nach THUNDER_BLUFF ist offen."]]
_self_additional = {"FROST_ARMOR","ICE_ARMOR","MAGE_ARMOR","FIRE_WARD","FROST_WARD","ARCANE_POWER","PRESENCE_OF_MIND","COMBUSTION","COLD_SNAP","CONJURE_MANA_AGATE","CONJURE_MANA_JADE","CONJURE_MANA_CITRINE","CONJURE_MANA_RUBY","COMPREHEND_SCROLL","STUDY","TELEPORT_STORMWIND","PORTAL_STORMWIND","TELEPORT_IRONFORGE","PORTAL_IRONFORGE","TELEPORT_DARNASSUS","PORTAL_DARNASSUS","TELEPORT_DALARAN","PORTAL_DALARAN","TELEPORT_ORGRIMMAR","PORTAL_ORGRIMMAR","TELEPORT_UNDERCITY","PORTAL_UNDERCITY","TELEPORT_THUNDER_BLUFF","PORTAL_THUNDER_BLUFF"}
for key, de, en, fr, phrase in _additional:
    SPELL_KEYS.append(key)
    if key in _self_additional:
        SELF_KEYS.append(key)
    for lang, label in (("deDE", de), ("enUS", en), ("frFR", fr)):
        spoken = phrase if lang == "deDE" else (f"Arcane forces shape {label}." if lang == "enUS" else f"Les arcanes façonnent {label}.")
        emote = f"*{label}: die Magie nimmt Gestalt an.*" if lang == "deDE" else (f"*channels {label}.*" if lang == "enUS" else f"*canalise {label}.*")
        SPELL_DATA[lang][key] = {"name": label, "ziel": [] if key in _self_additional else [spoken + " %s", emote[:-2] + " %s.*"], "gruppe": [spoken, emote]}

# Additional spoken/emote variety, shared across each supported key and locale.
# Keep each pool non-empty even where no enemy target exists.
_GROUP_LINES = {
    "deDE": [
        "Die arkane Theorie sieht das jedenfalls so vor.",
        "*zieht mit zwei Fingern eine flüchtige Rune in die Luft.*",
        "Der letzte Versuch war weniger elegant.",
        "*murmelt eine Formel und verfolgt aufmerksam die aufsteigenden Funken.*",
    ],
    "enUS": [
        "At least, that is what the arcane theory predicts.",
        "*traces a fleeting rune in the air.*",
        "The last attempt was less elegant.",
        "*murmurs an incantation and watches the rising sparks.*",
    ],
    "frFR": [
        "Du moins, c'est ce que prévoit la théorie des arcanes.",
        "*trace une rune fugitive dans les airs.*",
        "La dernière tentative fut moins élégante.",
        "*murmure une formule en observant les étincelles.*",
    ],
}
_TARGET_LINES = {
    "deDE": ["%s, Ihr werdet noch von dieser Formel hören!", "*richtet eine sorgfältig gezogene Rune auf %s.*"],
    "enUS": ["%s, you will remember this formula!", "*aims a carefully traced rune at %s.*"],
    "frFR": ["%s, vous vous souviendrez de cette formule !", "*dirige une rune soigneusement tracée vers %s.*"],
}
for _language in ("deDE", "enUS", "frFR"):
    for _key in SPELL_KEYS:
        _record = SPELL_DATA[_language][_key]
        # Format with the translated spell name, retaining natural text/emote markers.
        _record["gruppe"].extend(_GROUP_LINES[_language])
        if _key not in SELF_KEYS:
            _record["ziel"].extend(_TARGET_LINES[_language])

# Distinctive German text pools per school and functional spell family.
from magier_voice_banks import BANKS, theme_for
for _language in ("deDE", "enUS", "frFR"):
    for _key in SPELL_KEYS:
        SPELL_DATA[_language][_key]["gruppe"].extend(BANKS[_language][theme_for(_key)])

# Handwritten, key-specific German variants complement thematic pools.
_KEY_VOICE_DE = {"FIREBALL":["Ein sauberer Feuerball braucht keinen zweiten Versuch.","*verdichtet eine glühende Kugel zwischen den Handflächen.*"],"PYROBLAST":["Dafür brauche ich einen Augenblick. Ihr dafür eine neue Frisur.","*sammelt mit sichtlicher Mühe eine gewaltige Flamme.*"],"FROST_NOVA":["Ihr bleibt genau hier. Die Kälte besteht darauf.","*lässt eisige Ranken über den Boden kriechen.*"],"BLIZZARD":["Der Wetterbericht hat sich soeben verschlechtert.","*ruft ein Wirbeln aus Schnee und scharfkantigem Eis herbei.*"],"ARCANE_MISSILES":["Eine Rune für jeden Fehler in Eurer Verteidigung.","*entlässt mehrere violette Lichtpfeile aus einer schwebenden Glyphe.*"],"COUNTERSPELL":["Ein schöner Zauber. Schade um die letzte Silbe.","*zerreißt die fremde Formel mit einer knappen Handbewegung.*"],"POLYMORPH":["Ich verspreche, die Verwandlung steht Euch ausgezeichnet.","*mustert sein Gegenüber wie ein Schneider mit sehr viel Fantasie.*"],"ICE_BLOCK":["Bitte nicht stören. Ich bin gerade tiefgekühlt.","*schließt sich in kristallklarem Eis ein.*"],"BLINK":["Ihr schaut in die falsche Richtung.","*verschwindet in einem kurzen Flimmern der Luft.*"],"ARCANE_INTELLECT":["Ein geschärfter Verstand wiegt mehr als ein ganzer Waffenschrank.","*setzt eine leuchtende Rune behutsam auf die Stirn.*"],"CONJURE_WATER":["Wasser ist die vernünftigste aller Beschwörungen.","*lässt perlende Tropfen zu einer Karaffe verschmelzen.*"],"CONJURE_FOOD":["Ein bisschen Brot hat schon manch heldenhafte Reise gerettet.","*zaubert mit einer Verbeugung einen kleinen Imbiss hervor.*"],"PORTAL":["Wer zuerst hindurchgeht, darf mir anschließend berichten.","*prüft misstrauisch die Farbe des Portalrandes.*"],"EVOCATION":["Geduld. Meine Reserven sind nicht unerschöpflich.","*zieht langsam arkane Ströme aus der Umgebung.*"]}
for _key, _lines in _KEY_VOICE_DE.items():
    if _key in SPELL_DATA["deDE"]:
        SPELL_DATA["deDE"][_key]["gruppe"].extend(_lines)
