"""Safe, project-local spell-to-RP-key mapping for macro generation.

The mapping is editor metadata, not a runtime hook or automatic cast tracker.
"""
from __future__ import annotations
import json
import re
from pathlib import Path
from project_paths import metadata_path, addons_root

FILENAME = '.rptextstudio-spells.json'
COMMANDS = {'HexerRP': '/wrp', 'PaladinRP': '/prp', 'JaegerRP': '/jrp', 'DruidenRP': '/drp'}
SLASH_PATTERN = re.compile(r'^\\s*SLASH_([A-Z0-9_]+)1\\s*=\\s*["\\'](/[-a-z0-9]+)["\\']', re.M)
KEY_PATTERN = re.compile(r'^[A-Z][A-Z0-9_]*$')


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
                if ('SlashCmdList["' + match.group(1) + '"]') in content or (
                        "SlashCmdList['" + match.group(1) + "']") in content:
                    found[addon] = match.group(2)
                    break
            if addon in found:
                break
    return found


