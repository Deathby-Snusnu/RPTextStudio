"""Lua sources for the MagierRP project skeleton."""
SPELLS = {
 "deDE": [("Feuerball","Ich hoffe, Ihr mögt es warm, %s.","*schleudert einen Feuerball auf %s.*","Ein Funke Magie!"),("Frostblitz","Ein frostiger Gruß, %s.","*wirft einen Frostblitz auf %s.*","Die Luft wird kälter."),("Arkane Geschosse","Arkane Grüße, %s.","*lenkt arkane Geschosse auf %s.*","Die Magie erwacht.")],
 "enUS": [("Fireball","I hope you like it warm, %s.","*hurls a fireball at %s.*","A spark of magic!"),("Frostbolt","A chilly greeting, %s.","*casts a frostbolt at %s.*","The air grows colder."),("Arcane Missiles","Arcane greetings, %s.","*guides arcane missiles toward %s.*","Magic awakens.")],
 "frFR": [("Boule de feu","J'espère que vous aimez la chaleur, %s.","*lance une boule de feu sur %s.*","Une étincelle de magie !"),("Éclair de givre","Un salut glacé, %s.","*lance un éclair de givre sur %s.*","L'air se refroidit."),("Projectiles des Arcanes","Salutations arcaniques, %s.","*dirige des projectiles arcaniques vers %s.*","La magie s'éveille.")]
}
KEYS = ("FIREBALL","FROSTBOLT","ARCANE_MISSILES")

def q(value: str) -> str:
    return '"' + value.replace("\\", "\\\\").replace('"', '\\"').replace("\n", "\\n") + '"'

def source_files(name: str, title: str, langs: tuple[str,...], version: str, interface: int) -> dict[str,str]:
    db = name + "_CharacterDB"
    toc = [f"## Interface: {interface}", f"## Title: {title}", f"## Version: {version}",
           f"## SavedVariablesPerCharacter: {db}", "", "config\\Settings.lua", "locales\\Init.lua"]
    for lang in langs:
        toc += [f"locales\\{lang}\\Texts.lua", f"locales\\{lang}\\Racial.lua"]
    toc += ["locales\\Finalize.lua", "core\\Database.lua", "core\\Text.lua",
            "core\\Chat.lua", "core\\Cooldown.lua", "core\\Commands.lua", name + ".lua", ""]
    files = {name + ".toc": "\n".join(toc)}
    files["config/Settings.lua"] = 'local _, addon = ...\naddon.defaults = { textChance = 100, cooldown = 0, outputLanguage = "deDE" }\n'
    files["locales/Init.lua"] = "local _, addon = ...\naddon.localeData = addon.localeData or {}\n" + "".join("addon.localeData."+l+" = {}\n" for l in langs)
    files["locales/Finalize.lua"] = "local _, addon = ...\naddon.availableLocales = { " + ", ".join(l+" = true" for l in langs) + " }\n"
    for lang in langs:
        rows = []
        for key, (spell, target, emote, group) in zip(KEYS, SPELLS[lang]):
            rows.append("    " + key + " = { name = " + q(spell) + ", ziel = { " +
                        q(target) + ", " + q(emote) + " }, gruppe = { " + q(group) + " } },")
        files[f"locales/{lang}/Texts.lua"] = ("local _, addon = ...\naddon.localeData." + lang +
                                            ".texts = {\n" + "\n".join(rows) + "\n}\n")
        files[f"locales/{lang}/Racial.lua"] = f"local _, addon = ...\naddon.localeData.{lang}.racial = {{}}\n"
    files["core/Database.lua"] = ('local _, addon = ...\nfunction addon.InitializeDatabase()\n' +
        '    if type(' + db + ') ~= "table" then ' + db + ' = {} end\n' +
        '    addon.db = ' + db + '\n' +
        '    for key, value in pairs(addon.defaults) do if addon.db[key] == nil then addon.db[key] = value end end\n' +
        '    if type(addon.db.textChance) ~= "number" or addon.db.textChance < 0 or addon.db.textChance > 100 then addon.db.textChance = 100 end\n' +
        '    if type(addon.db.cooldown) ~= "number" or addon.db.cooldown < 0 then addon.db.cooldown = 0 end\nend\n')
    files["core/Text.lua"] = """local _, addon = ...
function addon.BuildText(key)
    local lang = addon.db.outputLanguage
    if not addon.availableLocales[lang] then lang = "deDE" end
    local entries = addon.localeData[lang] and addon.localeData[lang].texts
    local entry = (entries and entries[key]) or (addon.localeData.deDE.texts and addon.localeData.deDE.texts[key])
    if type(entry) ~= "table" then return nil end
    local target = UnitExists("target") and UnitName("target") or nil
    local pool = target and entry.ziel or entry.gruppe
    if type(pool) ~= "table" or #pool == 0 then return nil end
    return pool[math.random(#pool)]:gsub("%%s", target or "")
end
"""
    files["core/Chat.lua"] = """local _, addon = ...
function addon.SendText(line)
    if type(line) ~= "string" or line == "" then return false end
    if line:sub(1,1) == "*" and line:sub(-1) == "*" then
        SendChatMessage(line:sub(2,-2), "EMOTE")
    else
        SendChatMessage(line, "SAY")
    end
    return true
end
"""
    files["core/Cooldown.lua"] = """local _, addon = ...
function addon.CooldownReady() return GetTime() >= (addon.nextTextTime or 0) end
function addon.StartCooldown() addon.nextTextTime = GetTime() + addon.db.cooldown end
"""
    files["core/Commands.lua"] = ('local _, addon = ...\n' +
        'SLASH_' + name.upper() + '1 = "/mrp"\n' +
        'SLASH_' + name.upper() + '2 = "/magierrp"\n' +
        'SlashCmdList["' + name.upper() + '"] = function(message)\n' +
        '    local key = (message or ""):match("^%s*(.-)%s*$"):upper()\n' +
        '    if key == "" or key == "HELP" then print("' + name + ': /mrp FIREBALL | FROSTBOLT | ARCANE_MISSILES"); return end\n' +
        '    addon.TryText(key)\nend\n')
    files[name + ".lua"] = ('local _, addon = ...\naddon.ready = false\n' +
        'function addon.TryText(key)\n' +
        '    if not addon.ready then return false end\n' +
        '    local _, class = UnitClass("player")\n' +
        '    if class ~= "MAGE" then print("' + name + ': nur für Magier."); return false end\n' +
        '    if not addon.CooldownReady() then return false end\n' +
        '    if math.random(100) > addon.db.textChance then return false end\n' +
        '    local line = addon.BuildText(key)\n' +
        '    if not line or not addon.SendText(line) then return false end\n' +
        '    addon.StartCooldown()\n    return true\nend\n' +
        'local frame = CreateFrame("Frame")\nframe:RegisterEvent("PLAYER_LOGIN")\n' +
        'frame:SetScript("OnEvent", function() addon.InitializeDatabase(); addon.ready = true end)\n')
    files["README.md"] = "# " + title + "\n\nKlassen-AddOn für MAGE. Hilfe: /mrp help.\n" + "Sprachen: " + ", ".join(langs) + ".\n"
    files["CHANGELOG.md"] = "# Changelog\n\n## " + version + "\n- Initiales Grundgerüst.\n"
    files["tests/test_addon.lua"] = """-- Lua smoke test, load TOC file list in the integration suite.
assert(type("MAGE") == "string")
"""
    return files
