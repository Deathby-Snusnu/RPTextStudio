"""Validated creation of Race/Class profiles and spell keys for workspace UI.

Every supported locale is dry-run before original Lua files are changed.
"""
from __future__ import annotations
from pathlib import Path
from tempfile import TemporaryDirectory

from key_creation import new_spell, ensure_key
from race_class_manager import validate_profile, discover_targets, load_registry, register, add_lua_profile
from lua_text import parse_pools

FILES = ("Texts.lua", "Racial.lua", "Classes.lua", "RaceClass.lua")
def plan_spell(root: Path, addon: str, mode: int, race: str, klass: str, spell: str):
    if mode not in range(4):
        raise ValueError("Ungültiger Textstruktur-Typ.")
    ensure_key(spell)
    branches = ((race,) if mode in (1,3) else ()) + ((klass,) if mode in (2,3) else ())
    for branch in branches:
        ensure_key(branch)
    filename = FILES[mode]
    targets = []
    for lang in ("deDE","enUS","frFR"):
        p = root / addon / "locales" / lang / filename
        if not p.is_file():
            continue
        pools = parse_pools(p.read_text(encoding="utf-8-sig"))
        roots = {k[:3] for k in pools if len(k) >= 4 and k[:2] == ("localeData",lang)}
        if len(roots) != 1:
            raise ValueError(f"Keine eindeutige Root-Tabelle: {p}")
        base = next(iter(roots))
        samples = [k for k in pools if k[:3] == base]
        direct = not any(k[-1] in ("ziel","gruppe") for k in samples)
        targets.append((p,base,direct))
    if not targets:
        raise ValueError(f"Keine {filename}-Sprachdatei in {addon} gefunden.")
    with TemporaryDirectory() as directory:
        for i,(path,base,direct) in enumerate(targets):
            clone = Path(directory) / f"{i}.lua"
            clone.write_bytes(path.read_bytes())
            new_spell(clone,base,branches,spell,backup=False,direct=direct)
    return targets,branches

def create_spell(root: Path, addon: str, mode: int, race: str, klass: str, spell: str):
    targets, branches = plan_spell(root,addon,mode,race,klass,spell)
    for path,base,direct in targets:
        new_spell(path,base,branches,spell,backup=True,direct=direct)
    return len(targets)

def plan_profile(root:Path, addon:str,kind:str,key:str,name:str,style:str,with_lua:bool):
    validate_profile(kind,key,name,style)
    registry=load_registry(root)
    bucket=registry["races" if kind=="race" else "classes"]
    if key in bucket:
        raise ValueError(f"{key} ist bereits im Register.")
    if not with_lua:
        return []
    targets=discover_targets(root,addon,kind)
    if not targets:
        raise ValueError(f"{addon} besitzt keine unterstützte Rassen-/Klassen-Datei.")
    with TemporaryDirectory() as directory:
        for i,(path,base,direct) in enumerate(targets):
            clone=Path(directory)/f"{i}.lua"
            clone.write_bytes(path.read_bytes())
            new_spell(clone,base,(key,),"RP_GREETING",backup=False,direct=direct)
    return targets

def create_profile(root:Path, addon:str,kind:str,key:str,name:str,style:str,with_lua:bool):
    targets=plan_profile(root,addon,kind,key,name,style,with_lua)
    if targets:
        add_lua_profile(root,addon,kind,key)
    register(root,kind,key,name,style,[addon] if with_lua else [])
    return len(targets)
