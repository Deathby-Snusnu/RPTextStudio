"""Safe, project-local spell-to-RP-key mapping for macro generation.

The mapping is editor metadata, not a runtime hook or automatic cast tracker.
"""
from __future__ import annotations
import json
import re
from pathlib import Path
from project_paths import metadata_path

FILENAME = '.rptextstudio-spells.json'
COMMANDS = {'HexerRP': '/wrp', 'PaladinRP': '/prp', 'JaegerRP': '/jrp', 'DruidenRP': '/drp'}
KEY_PATTERN = re.compile(r'^[A-Z][A-Z0-9_]*$')


def candidate_keys(files: dict, addon: str) -> list[str]:
    """Discover actual spell keys from localized literal RP pools.

    PaladinRP stores its spells across Abilities, Blessings, GreaterBlessings,
    Auras and Seals, not in Texts.lua. Ambient pools are not spell commands.
    """
    keys = set()
    spell_files = {"Abilities.lua", "Blessings.lua", "GreaterBlessings.lua",
                   "Auras.lua", "Seals.lua"}
    for path, pools in files.items():
        if addon not in path.parts:
            continue
        for parts in pools:
            if addon == "PaladinRP":
                if path.name in spell_files and "localeData" in parts:
                    # addon.localeData.deDE.Abilities.LAYONHANDS.ziel
                    if len(parts) >= 5 and parts[-1] in ("ziel", "gruppe"):
                        keys.add(parts[-2])
                elif path.name == "Racial.lua" and len(parts) >= 5:
                    # localeData.deDE.Racial.Dwarf.MIGHT is a fallback,
                    # not a new spell; it still contributes its spell token.
                    keys.add(parts[-1])
            elif path.name == "Texts.lua" and len(parts) >= 4:
                keys.add(parts[3])
            elif path.name == "Racial.lua" and len(parts) >= 5:
                keys.add(parts[4])
            elif path.name in ("Classes.lua", "RaceClass.lua") and len(parts) >= 5:
                keys.add(parts[-2] if parts[-1] in ("ziel", "gruppe") else parts[-1])
    return sorted(key for key in keys if KEY_PATTERN.fullmatch(key))


def validate_entry(addon: str, spell: str, key: str, known_keys: list[str]):
    if addon not in COMMANDS:
        raise ValueError('Für dieses AddOn ist kein sicherer RP-Makrobefehl hinterlegt.')
    if not spell or '\n' in spell or '\r' in spell or spell.startswith('/'):
        raise ValueError('Ungültiger Zaubername (keine Zeilenumbrüche oder Slash-Befehle).')
    if not KEY_PATTERN.fullmatch(key):
        raise ValueError('Ungültiger RP-Schlüssel.')
    if key not in known_keys:
        raise ValueError(f'RP-Schlüssel {key} fehlt in den geladenen Textpools.')


def make_macro(addon: str, spell: str, key: str, known_keys: list[str]) -> str:
    validate_entry(addon, spell, key, known_keys)
    # Macro uses the current client-language spell name. The mapping does not
    # claim any implicit cast detection or guaranteed protected-chat behavior.
    return f'#showtooltip {spell}\n/cast {spell}\n{COMMANDS[addon]} {key.lower()}'


def load_mappings(root: Path) -> list[dict[str,str]]:
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
