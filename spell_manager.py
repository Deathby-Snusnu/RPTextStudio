"""Safe, project-local spell-to-RP-key mapping for macro generation.

The mapping is editor metadata, not a runtime hook or automatic cast tracker.
"""
from __future__ import annotations
import json
import re
from pathlib import Path
from project_paths import metadata_path, addons_root
from lua_text import ParseError, decode_string, lex

FILENAME = '.rptextstudio-spells.json'
COMMANDS = {'HexerRP': '/wrp', 'PaladinRP': '/prp', 'JaegerRP': '/jrp', 'DruidenRP': '/drp'}
SLASH_PATTERN = re.compile(r"^\s*SLASH_([A-Z0-9_]+)1\s*=\s*[\"'](/[-a-z0-9]+)[\"']", re.M)
KEY_PATTERN = re.compile(r'^[A-Z][A-Z0-9_]*


def _has_handler_assignment(content: str, handler: str) -> bool:
    try:
        tokens = lex(content)
    except ParseError:
        return False
    for index in range(len(tokens) - 4):
        target = tokens[index:index + 5]
        if ([token.value for token in target[:2]] == ["SlashCmdList", "["]
                and target[2].kind == "string"
                and target[3].value == "]"
                and target[4].value == "="
                and decode_string(target[2].value) == handler
                and (index == 0 or tokens[index - 1].value not in {".", ":"})):
            return True
    return False


def candidate_keys(files: dict, addon: str) -> list[str]:
    """Find spell-capable RP keys in all supported class addons.

    The parser paths are relative to the Lua assignment (without `addon`):
    localeData.deDE.texts.SHADOW_BOLT.ziel, or
    localeData.deDE.Abilities.LAYONHANDS.ziel.
    Ambient collections are deliberately excluded from spell macros. The
    result is not a complete list of runtime keys; unsupported addons return
    an empty list. Paladin GreaterBlessings base keys are exposed with the
    GREATER_ prefix required by the runtime command.
    """
    result = set()
    paladin_sources = {"Abilities", "Blessings", "GreaterBlessings", "Auras", "Seals"}
    for path, pools in files.items():
        path = Path(path)
        if (path.parent.parent.name != "locales"
                or path.parent.parent.parent.name != addon
                or path.suffix.lower() != ".lua"):
            continue
        for tokens in pools:
            parts = tuple(tokens)
            if len(parts) < 4:
                continue
            if (path.name in ("Classes.lua", "RaceClass.lua")
                    and parts[-1] in ("ziel", "gruppe")):
                result.add(parts[-2])
            if addon == "PaladinRP":
                if (len(parts) >= 5 and "localeData" in parts
                        and any(section in parts for section in paladin_sources)
                        and path.stem in paladin_sources
                        and parts[-1] in ("ziel", "gruppe")):
                    key = parts[-2]
                    if path.stem == "GreaterBlessings" and not key.startswith("GREATER_"):
                        key = "GREATER_" + key
                    result.add(key)
                elif (path.name == "Racial.lua"
                      and any(part.casefold() == "racial" for part in parts)
                      and len(parts) >= 5):
                    result.add(parts[-2] if parts[-1] in ("ziel", "gruppe") else parts[-1])
            elif path.name == "Texts.lua" and (
                    "texts" in parts or "Texts" in parts) and parts[-1] in ("ziel", "gruppe"):
                result.add(parts[-2])
            elif (path.name == "Racial.lua"
                  and any(part.casefold() == "racial" for part in parts)):
                # Race-specific spell pool: Racial.Dwarf.MIGHT = {"..."}
                if len(parts) >= 5:
                    result.add(parts[-2] if parts[-1] in ("ziel", "gruppe") else parts[-1])
    return sorted(key for key in result if KEY_PATTERN.fullmatch(key))


def validate_entry(addon: str, spell: str, key: str, known_keys: list[str], commands=None):
    """Validate an addon, spell name, and known RP key or raise ValueError.

    This checks the macro format, not whether the spell exists in the client.
    """
    if addon not in (commands if commands is not None else COMMANDS):
        raise ValueError('Für dieses AddOn wurde kein registrierter RP-Slash-Befehl gefunden.')
    if not spell or '\n' in spell or '\r' in spell or spell.startswith('/'):
        raise ValueError('Ungültiger Zaubername (keine Zeilenumbrüche oder Slash-Befehle).')
    if not KEY_PATTERN.fullmatch(key):
        raise ValueError('Ungültiger RP-Schlüssel.')
    if key not in known_keys:
        raise ValueError(f'RP-Schlüssel {key} fehlt in den geladenen Textpools.')
    if key in NON_CASTABLE_KEYS.get(addon, set()):
        raise ValueError(f'RP-Schlüssel {key} ist passiv oder nicht eigenständig wirkbar. Nur /krp als Erzähltext verwenden.')


def make_macro(addon: str, spell: str, key: str, known_keys: list[str], commands=None) -> str:
    """Return a validated cast-and-RP macro without modifying the game."""
    validate_entry(addon, spell, key, known_keys, commands)
    # Macro uses the current client-language spell name. The mapping does not
    # claim any implicit cast detection or guaranteed protected-chat behavior.
    return f'#showtooltip {spell}\n/cast {spell}\n{(commands if commands is not None else COMMANDS)[addon]} {key.lower()}'


def load_mappings(root: Path) -> list[dict[str,str]]:
    """Read project spell mappings, or return an empty list if absent.

    Malformed data or an unsupported schema raises ValueError.
    """
    p = metadata_path(root, FILENAME)
    if not p.exists():
        return []
    data = json.loads(p.read_text(encoding='utf-8'))
    if not isinstance(data, dict) or data.get('schema') != 1 or not isinstance(data.get('mappings'), list):
        raise ValueError('Unbekanntes Spell-Mapping-Format.')
    rows = data['mappings']
    if any(not isinstance(row, dict) or not all(isinstance(row.get(k), str) for k in ('addon','spell','key')) for row in rows):
        raise ValueError('Ungültige Einträge in Spell-Mappings.')
    return rows


def save_mappings(root: Path, rows: list[dict[str,str]]) -> None:
    """Write supplied project mappings, backing up an existing changed file.

    The caller is responsible for validating the rows before saving.
    """
    p = metadata_path(root, FILENAME, write=True)
    payload = json.dumps({'schema': 1, 'mappings': rows}, indent=2, ensure_ascii=False) + '\n'
    if p.exists() and p.read_text(encoding='utf-8') == payload:
        return
    if p.exists():
        backup = p.with_suffix(p.suffix + '.bak')
        backup.write_bytes(p.read_bytes())
    tmp = p.with_name(p.name + '.tmp')
    tmp.write_text(payload, encoding='utf-8')
    tmp.replace(p)
def discover_commands(root: Path, files: dict | None = None) -> dict[str, str]:
    """Discover real /slash commands only from installed project Lua sources.

    A candidate must register the matching SlashCmdList handler. Never infer
    commands from a name or allow arbitrary user-defined macro statements.
    """
    found = {}
    directory = addons_root(Path(root))
    addons = {p.parent.parent.parent.name for p in (files or {})
              if Path(p).parent.parent.name == "locales"}
    for addon in sorted(addons):
        base = directory / addon
        candidates = [base / "core" / "Commands.lua", base / (addon + ".lua")]
        for path in candidates:
            if not path.is_file():
                continue
            try:
                content = path.read_text(encoding="utf-8-sig")
            except (OSError, UnicodeError):
                continue
            for match in SLASH_PATTERN.finditer(content):
                if _has_handler_assignment(content, match.group(1)):
                    found[addon] = match.group(2)
                    break
            if addon in found:
                break
    return found

)
# RP-only keys are not independently castable WoW actions.
NON_CASTABLE_KEYS = {"KriegerRP": {"TACTICAL_MASTERY", "DEVASTATE"}}


def _has_handler_assignment(content: str, handler: str) -> bool:
    try:
        tokens = lex(content)
    except ParseError:
        return False
    for index in range(len(tokens) - 4):
        target = tokens[index:index + 5]
        if ([token.value for token in target[:2]] == ["SlashCmdList", "["]
                and target[2].kind == "string"
                and target[3].value == "]"
                and target[4].value == "="
                and decode_string(target[2].value) == handler
                and (index == 0 or tokens[index - 1].value not in {".", ":"})):
            return True
    return False


def candidate_keys(files: dict, addon: str) -> list[str]:
    """Find spell-capable RP keys in all supported class addons.

    The parser paths are relative to the Lua assignment (without `addon`):
    localeData.deDE.texts.SHADOW_BOLT.ziel, or
    localeData.deDE.Abilities.LAYONHANDS.ziel.
    Ambient collections are deliberately excluded from spell macros. The
    result is not a complete list of runtime keys; unsupported addons return
    an empty list. Paladin GreaterBlessings base keys are exposed with the
    GREATER_ prefix required by the runtime command.
    """
    result = set()
    paladin_sources = {"Abilities", "Blessings", "GreaterBlessings", "Auras", "Seals"}
    for path, pools in files.items():
        path = Path(path)
        if (path.parent.parent.name != "locales"
                or path.parent.parent.parent.name != addon
                or path.suffix.lower() != ".lua"):
            continue
        for tokens in pools:
            parts = tuple(tokens)
            if len(parts) < 4:
                continue
            if (path.name in ("Classes.lua", "RaceClass.lua")
                    and parts[-1] in ("ziel", "gruppe")):
                result.add(parts[-2])
            if addon == "PaladinRP":
                if (len(parts) >= 5 and "localeData" in parts
                        and any(section in parts for section in paladin_sources)
                        and path.stem in paladin_sources
                        and parts[-1] in ("ziel", "gruppe")):
                    key = parts[-2]
                    if path.stem == "GreaterBlessings" and not key.startswith("GREATER_"):
                        key = "GREATER_" + key
                    result.add(key)
                elif (path.name == "Racial.lua"
                      and any(part.casefold() == "racial" for part in parts)
                      and len(parts) >= 5):
                    result.add(parts[-2] if parts[-1] in ("ziel", "gruppe") else parts[-1])
            elif path.name == "Texts.lua" and (
                    "texts" in parts or "Texts" in parts) and parts[-1] in ("ziel", "gruppe"):
                result.add(parts[-2])
            elif (path.name == "Racial.lua"
                  and any(part.casefold() == "racial" for part in parts)):
                # Race-specific spell pool: Racial.Dwarf.MIGHT = {"..."}
                if len(parts) >= 5:
                    result.add(parts[-2] if parts[-1] in ("ziel", "gruppe") else parts[-1])
    return sorted(key for key in result if KEY_PATTERN.fullmatch(key))


def validate_entry(addon: str, spell: str, key: str, known_keys: list[str], commands=None):
    """Validate an addon, spell name, and known RP key or raise ValueError.

    This checks the macro format, not whether the spell exists in the client.
    """
    if addon not in (commands if commands is not None else COMMANDS):
        raise ValueError('Für dieses AddOn wurde kein registrierter RP-Slash-Befehl gefunden.')
    if not spell or '\n' in spell or '\r' in spell or spell.startswith('/'):
        raise ValueError('Ungültiger Zaubername (keine Zeilenumbrüche oder Slash-Befehle).')
    if not KEY_PATTERN.fullmatch(key):
        raise ValueError('Ungültiger RP-Schlüssel.')
    if key not in known_keys:
        raise ValueError(f'RP-Schlüssel {key} fehlt in den geladenen Textpools.')


def make_macro(addon: str, spell: str, key: str, known_keys: list[str], commands=None) -> str:
    """Return a validated cast-and-RP macro without modifying the game."""
    validate_entry(addon, spell, key, known_keys, commands)
    # Macro uses the current client-language spell name. The mapping does not
    # claim any implicit cast detection or guaranteed protected-chat behavior.
    return f'#showtooltip {spell}\n/cast {spell}\n{(commands if commands is not None else COMMANDS)[addon]} {key.lower()}'


def load_mappings(root: Path) -> list[dict[str,str]]:
    """Read project spell mappings, or return an empty list if absent.

    Malformed data or an unsupported schema raises ValueError.
    """
    p = metadata_path(root, FILENAME)
    if not p.exists():
        return []
    data = json.loads(p.read_text(encoding='utf-8'))
    if not isinstance(data, dict) or data.get('schema') != 1 or not isinstance(data.get('mappings'), list):
        raise ValueError('Unbekanntes Spell-Mapping-Format.')
    rows = data['mappings']
    if any(not isinstance(row, dict) or not all(isinstance(row.get(k), str) for k in ('addon','spell','key')) for row in rows):
        raise ValueError('Ungültige Einträge in Spell-Mappings.')
    return rows


def save_mappings(root: Path, rows: list[dict[str,str]]) -> None:
    """Write supplied project mappings, backing up an existing changed file.

    The caller is responsible for validating the rows before saving.
    """
    p = metadata_path(root, FILENAME, write=True)
    payload = json.dumps({'schema': 1, 'mappings': rows}, indent=2, ensure_ascii=False) + '\n'
    if p.exists() and p.read_text(encoding='utf-8') == payload:
        return
    if p.exists():
        backup = p.with_suffix(p.suffix + '.bak')
        backup.write_bytes(p.read_bytes())
    tmp = p.with_name(p.name + '.tmp')
    tmp.write_text(payload, encoding='utf-8')
    tmp.replace(p)
def discover_commands(root: Path, files: dict | None = None) -> dict[str, str]:
    """Discover real /slash commands only from installed project Lua sources.

    A candidate must register the matching SlashCmdList handler. Never infer
    commands from a name or allow arbitrary user-defined macro statements.
    """
    found = {}
    directory = addons_root(Path(root))
    addons = {p.parent.parent.parent.name for p in (files or {})
              if Path(p).parent.parent.name == "locales"}
    for addon in sorted(addons):
        base = directory / addon
        candidates = [base / "core" / "Commands.lua", base / (addon + ".lua")]
        for path in candidates:
            if not path.is_file():
                continue
            try:
                content = path.read_text(encoding="utf-8-sig")
            except (OSError, UnicodeError):
                continue
            for match in SLASH_PATTERN.finditer(content):
                if _has_handler_assignment(content, match.group(1)):
                    found[addon] = match.group(2)
                    break
            if addon in found:
                break
    return found

