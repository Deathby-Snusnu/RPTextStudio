"""Remove an explicitly selected RP key from literal Lua tables only.

No Lua code is evaluated. Removal is restricted to keyed table entries whose
complete descendant text pools match the selected spell/action branch.
"""
from __future__ import annotations
from pathlib import Path
import re
import shutil
from datetime import datetime
from lua_text import lex, parse_pools, ParseError
from key_creation import find_table


def spell_path(pool_path: tuple[str, ...]) -> tuple[str, ...]:
    if len(pool_path) < 4:
        raise ValueError('Kein loeschbarer Zauberschluessel ausgewaehlt.')
    if pool_path[-1] in ('ziel', 'gruppe'):
        if len(pool_path) < 5:
            raise ValueError('Kein eigenstaendiger Zauberzweig.')
        return pool_path[:-1]
    return pool_path


def prepare_deletion(src: str, parent_path: tuple[str,...], spell: str) -> tuple[str,int]:
    """Return modified source and count of removed leaf pools, without writing."""
    if not re.fullmatch(r'[A-Za-z_][A-Za-z0-9_]*', spell):
        raise ValueError('Ungueltiger Schluessel.')
    ts=lex(src)
    opener,closer=find_table(src,parent_path+(spell,))
    parent_open,parent_close=find_table(src,parent_path)
    # Locate the direct table assignment before its opening brace.
    oi=next(i for i,t in enumerate(ts) if t.start==opener.start)
    pi=next(i for i,t in enumerate(ts) if t.start==parent_open.start)
    ci=next(i for i,t in enumerate(ts) if t.start==parent_close.start)
    if not(pi<oi<ci):raise ValueError('Schluessel liegt nicht unter dem erwarteten Elternzweig.')
    if oi>=2 and ts[oi-1].value=='=' and ts[oi-2].kind=='ident' and ts[oi-2].value==spell:
        start=ts[oi-2].start
    elif oi>=4 and ts[oi-1].value=='=' and ts[oi-2].value==']' and ts[oi-4].value=='[':
        start=ts[oi-4].start
    else:raise ValueError('Schluessel ist kein direktes Lua-Tabellenfeld.')
    # Include optional following comma, preserve surrounding sibling tables.
    close_i=next(i for i,t in enumerate(ts) if t.start==closer.start)
    end=closer.end
    if close_i+1<len(ts) and ts[close_i+1].value in (',',';'):
        end=ts[close_i+1].end
    before=parse_pools(src)
    target=parent_path+(spell,)
    removed={k for k in before if k[:len(target)]==target}
    if not removed:raise ValueError('Kein eigenstaendiger Textpool unter diesem Schluessel gefunden.')
    result=src[:start]+src[end:]
    after=parse_pools(result)
    if set(after)!=set(before)-removed:
        raise ValueError('Schutzpruefung: Weitere Textpools waeren betroffen.')
    if any(k in after for k in removed):raise ValueError('Schluessel wurde nicht vollstaendig entfernt.')
    return result,len(removed)


def delete_from_files(targets: list[tuple[Path,tuple[str,...],str]]) -> int:
    """Preflight every file, then back up all originals before writing."""
    patches=[]
    for path,parent,spell in targets:
        with path.open('r',encoding='utf-8',newline='') as f:src=f.read()
        result,count=prepare_deletion(src,parent,spell)
        patches.append((path,src,result,count))
    # Safety: each planned modification has a backup before any write.
    stamp=datetime.now().strftime('%Y%m%d-%H%M%S-%f')
    for path,_,_,_ in patches:
        shutil.copy2(path,path.with_suffix(path.suffix+'.'+stamp+'.bak'))
    for path,_,result,_ in patches:
        with path.open('w',encoding='utf-8',newline='') as f:f.write(result)
    return sum(p[3] for p in patches)
