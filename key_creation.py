"""Conservative insertion of new literal Lua text keys, without running Lua."""
from pathlib import Path
import re
import shutil
from datetime import datetime
from lua_text import lex, parse_pools, encode_string, ParseError

IDENT=re.compile(r'^[A-Za-z_][A-Za-z0-9_]*$')

def ensure_key(value):
    """Check identifier syntax and return the value; reserved words are not checked."""
    if not IDENT.fullmatch(value):
        raise ValueError(f'Ungueltiger Lua-Schluessel: {value!r}. Nur Buchstaben, Zahlen und _; keine fuehrende Zahl.')
    return value

def find_table(src, path):
    """Return (open token, close token) of the literal table at an assignment path.

    Traversal is restricted to a root addon.* assignment and immediate keyed child
    tables. It never follows expressions or edits executable Lua logic.
    """
    ts=lex(src)
    roots=[]
    for i,t in enumerate(ts):
        if t.value!='addon' or t.kind!='ident':continue
        j=i+1; fields=[]
        while j+1<len(ts) and ts[j].value=='.' and ts[j+1].kind=='ident':
            fields.append(ts[j+1].value);j+=2
        if j+1<len(ts) and ts[j].value=='=' and ts[j+1].value=='{':
            roots.append((tuple(fields), j+1))
    matches=[(root,idx) for root,idx in roots if tuple(path[:len(root)])==root]
    if not matches:raise ValueError(f'Keine passende addon-Tabelle fuer {path}')
    root,start=max(matches,key=lambda x:len(x[0]))
    def closing(i):
        depth=0
        for j in range(i,len(ts)):
            if ts[j].value=='{':depth+=1
            if ts[j].value=='}':
                depth-=1
                if depth==0:return j
        raise ParseError('Unclosed table')
    idx=start
    for field in path[len(root):]:
        end=closing(idx);found=None
        j=idx+1
        while j<end:
            name=None;v=None
            if j+2<end and ts[j].kind=='ident' and ts[j+1].value=='=':
                name=ts[j].value;v=j+2
            elif j+4<end and ts[j].value=='[' and ts[j+1].kind=='string' and ts[j+2].value==']' and ts[j+3].value=='=':
                from lua_text import decode_string
                name=decode_string(ts[j+1].value);v=j+4
            if name==field and v is not None and ts[v].value=='{':
                found=v;break
            # Move past nested tables rather than matching descendant names.
            if v is not None and v<end and ts[v].value=='{':j=closing(v)+1
            elif ts[j].value=='{':j=closing(j)+1
            else:j+=1
        if found is None:raise ValueError(f'Parent-Schluessel fehlt: {field}')
        idx=found
    return ts[idx],ts[closing(idx)]

def new_spell(path:Path, parent:tuple[str,...], branches:tuple[str,...], spell:str, text='Neuer RP-Text', backup=True, direct=False):
    """Insert missing ancestors and a new spell in a literal Lua table.

    The caller selects the root parent; an existing spell table is rejected. Unless
    ``direct`` is true, the new key contains separate ``ziel`` and ``gruppe``
    pools. The modified source is parsed before writing, and ``backup`` creates
    a timestamped sibling backup. Returns the new key path.
    """
    for x in (*branches,spell):ensure_key(x)
    if not branches and not spell:raise ValueError('Schluessel fehlt')
    with path.open('r',encoding='utf-8',newline='') as f:src=f.read()
    base=parent
    missing=list(branches)+( [spell] )
    # Walk existing intermediate branches, but spell itself must be new.
    for part in branches:
        try:find_table(src,base+(part,))
        except ValueError:break
        base=base+(part,)
        missing.pop(0)
    if not missing or (base+tuple(missing))==base:raise ValueError('Schluessel existiert bereits')
    if not missing[:-1]:
        try:find_table(src,base+(spell,))
        except ValueError:pass
        else:raise ValueError(f'Schluessel {spell} existiert bereits')
    opener,closer=find_table(src,base)
    nl='\r\n' if '\r\n' in src else '\n'
    line=src.rfind('\n',0,opener.start)+1
    indentation=re.match(r'[ \t]*',src[line:opener.start]).group()
    # Every newly added branch is indented one level.
    lines=[];depth=1
    for part in missing:
        lines.append('    '*depth + f'{part} = {{');depth+=1
    if direct:
        lines.append('    '*depth + encode_string(text)+',')
    else:
        for pool in ('ziel','gruppe'):
            lines.append('    '*depth + f'{pool} = {{ {encode_string(text)}, }},')
    for _ in missing:
        depth-=1;lines.append('    '*depth+'},')
    inserted=nl+nl.join(indentation+line for line in lines)+nl+indentation
    modified=src[:closer.start]+inserted+src[closer.start:]
    original=set(parse_pools(src));parsed=parse_pools(modified)
    final=parent+tuple(branches)+(spell,)
    expected=[final] if direct else [final+('ziel',),final+('gruppe',)]
    if any(x not in parsed for x in expected):
        raise ValueError(f'Neue Textpools konnten nicht gelesen werden: {final}')
    if not original.issubset(parsed):raise ValueError('Vorhandene Textpools gingen verloren')
    if modified==src:raise ValueError('Keine Aenderung')
    if backup:
        shutil.copy2(path,path.with_suffix(path.suffix+'.'+datetime.now().strftime('%Y%m%d-%H%M%S-%f')+'.bak'))
    with path.open('w',encoding='utf-8',newline='') as f:f.write(modified)
    return final
