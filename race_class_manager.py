"""Project-local race/class profiles and conservative Lua text branch creation.

The registry describes RP style and user-chosen identifiers. It does not create
new playable WoW races/classes or change runtime addon dispatch.
"""
from __future__ import annotations
import json
import os
from pathlib import Path
import re
import tempfile
from key_creation import ensure_key, new_spell
from lua_text import parse_pools
from project_paths import addons_root, metadata_path

REGISTRY = '.rptextstudio-races-classes.json'
KEYS = {'race':'races', 'class':'classes'}

def load_registry(root:Path)->dict:
    """Read project profiles or return an empty registry if none exists."""
    file=metadata_path(root, REGISTRY)
    if not file.exists():return {'version':1,'races':{},'classes':{}}
    raw=json.loads(file.read_text(encoding='utf-8'))
    if not isinstance(raw,dict) or not isinstance(raw.get('races'),dict) or not isinstance(raw.get('classes'),dict):
        raise ValueError('Ungültiges Rassen-/Klassenregister')
    return raw

def validate_profile(kind:str, key:str, display:str, style:str):
    """Validate the profile kind, identifier, display name, and text limits."""
    if kind not in KEYS:raise ValueError('Unbekannter Typ')
    ensure_key(key)
    if key.lower() in {'true','false','nil','function','end','local','return','if','then','else'}:
        raise ValueError('Reserviertes Lua-Wort')
    if not display.strip():raise ValueError('Anzeigename fehlt')
    if len(display)>100 or len(style)>3000:raise ValueError('Text zu lang')
    if any(c in key for c in '\r\n'):raise ValueError('Ungültige ID')

def register(root:Path,kind:str,key:str,display:str,style:str,addons:list[str]|None=None)->None:
    """Add a validated, unique profile to the project-local registry.

    The registry is replaced using a temporary file; no backup is created.
    """
    validate_profile(kind,key,display,style)
    obj=load_registry(root); bucket=obj[KEYS[kind]]
    if key in bucket:raise ValueError(f'{key} ist bereits registriert')
    bucket[key]={'name':display.strip(),'style':style.strip(),'addons':addons or []}
    target=metadata_path(root, REGISTRY, write=True)
    fd,temp=tempfile.mkstemp(dir=target.parent,prefix='.rpstudio-',suffix='.tmp')
    try:
        with os.fdopen(fd,'w',encoding='utf-8') as f:
            json.dump(obj,f,indent=2,ensure_ascii=False);f.write('\n')
        os.replace(temp,target)
    finally:
        if os.path.exists(temp):os.unlink(temp)

def discover_targets(root:Path,addon:str,kind:str):
    """Find existing literal locale structures for a validated race/class kind."""
    filename='Racial.lua' if kind=='race' else 'Classes.lua'
    targets=[]
    for locale in ('deDE','enUS','frFR'):
        p=addons_root(root)/addon/'locales'/locale/filename
        if not p.exists():continue
        pools=parse_pools(p.read_text(encoding='utf-8-sig'))
        roots={k[:3] for k in pools if len(k)>=4 and k[:2]==('localeData',locale)}
        if len(roots)!=1:raise ValueError(f'Root-Tabelle nicht eindeutig: {p}')
        base=next(iter(roots))
        samples=[k for k in pools if k[:3]==base]
        nested=any(k[-1] in ('ziel','gruppe') for k in samples)
        targets.append((p,base,not nested))
    return targets

def add_lua_profile(root:Path,addon:str,kind:str,key:str,seed_key:str='RP_GREETING'):
    """Create first usable text pool under a previously absent race/class branch.

    Dry-run every language before touching any original file, then back up
    each original before editing it. Returns the number of edited files.
    """
    validate_profile(kind,key,key,'')
    ensure_key(seed_key)
    targets=discover_targets(root,addon,kind)
    if not targets:raise ValueError(f'Keine unterstützten Textdateien für {addon}/{kind} vorhanden')
    for path,base,direct in targets:
        pools=parse_pools(path.read_text(encoding='utf-8-sig'))
        if any(k[:len(base)+1]==base+(key,) for k in pools):
            raise ValueError(f'Rasse/Klasse {key} existiert bereits in {path.name} ({path.parent.name})')
    with tempfile.TemporaryDirectory() as tmp:
        for i,(path,base,direct) in enumerate(targets):
            clone=Path(tmp)/f'{i}.lua';clone.write_bytes(path.read_bytes())
            new_spell(clone,base,(key,),seed_key,backup=False,direct=direct)
    for path,base,direct in targets:
        new_spell(path,base,(key,),seed_key,backup=True,direct=direct)
    return len(targets)
