"""Conservative parser/editor for literal RP text lists in Lua.

Never evaluates Lua. Saves only modified literal list interiors, preserving the
rest of the file byte-for-byte (as UTF-8 text).
"""
from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path
import re
import shutil
from datetime import datetime

@dataclass
class Token:
    """Represent a Lua token with its source-text offsets."""

    kind: str
    value: str
    start: int
    end: int

@dataclass
class Pool:
    """Represent a parsed literal text list and its enclosing source tokens."""

    path: tuple[str, ...]
    opener: Token
    closer: Token
    entries: list[str]
    indent: str

class ParseError(Exception): pass

def lex(src: str) -> list[Token]:
    """Tokenize supported Lua syntax without evaluating it."""
    out = []
    n = len(src)
    i = 0
    while i < n:
        ch = src[i]
        if ch.isspace():
            i += 1; continue
        if src.startswith('--', i):
            if i + 2 < n and src[i+2] == '[':
                m = re.match(r'\[(=*)\[', src[i+2:])
                if m:
                    term = ']' + m.group(1) + ']'
                    j = src.find(term, i + 2 + len(m.group()))
                    if j < 0: raise ParseError('Unclosed long comment')
                    i = j + len(term); continue
            j = src.find('\n', i)
            i = n if j < 0 else j+1
            continue
        if ch in '\"\'':
            start = i; quote = ch; i += 1
            while i < n:
                if src[i] == '\\': i += 2; continue
                if src[i] == quote: i += 1; break
                i += 1
            else: raise ParseError(f'Unclosed string at character {start}')
            out.append(Token('string', src[start:i], start, i)); continue
        if ch == '[':
            m = re.match(r'\[(=*)\[',src[i:])
            if m:
                term = ']' + m.group(1) + ']'
                j = src.find(term, i+len(m.group()))
                if j < 0: raise ParseError('Unclosed long string')
                end=j+len(term)
                out.append(Token('other',src[i:end],i,end)); i=end; continue
        if ch.isalpha() or ch == '_':
            start=i; i+=1
            while i<n and (src[i].isalnum() or src[i]=='_'):i+=1
            out.append(Token('ident',src[start:i],start,i)); continue
        out.append(Token('symbol',ch,i,i+1)); i+=1
    return out

def decode_string(raw: str) -> str:
    """Decode common escapes in a quoted Lua string literal."""
    # Lua string escapes: handle common escapes without interpreting unsafe code.
    body = raw[1:-1]
    d = {'n':'\n','r':'\r','t':'\t','a':'\a','b':'\b','f':'\f','v':'\v','\\':'\\','\"':'\"',"'":"'"}
    def sub(m):
        s=m.group(1)
        if s.isdigit(): return chr(int(s)) if int(s)<=255 else m.group()
        return d.get(s,'\\'+s)
    return re.sub(r'\\(\d{1,3}|.)',sub,body,flags=re.S)

def encode_string(s: str) -> str:
    """Encode text as a double-quoted Lua string literal."""
    return '"' + (s.replace('\\','\\\\').replace('"','\\"').replace('\n','\\n').replace('\r','\\r').replace('\t','\\t')) + '"'

def parse_pools(src: str, *, rejected_paths: set[tuple[str,...]] | None = None) -> dict[tuple[str,...],Pool]:
    """Find nonempty literal leaf lists in addon table assignments.

    Paths omit the leading ``addon``. When supplied, ``rejected_paths`` is
    updated for nonliteral leaf lists that contain string entries; Lua is
    never executed.
    """
    ts=lex(src); pools={}; n=len(ts)
    def table(idx: int, path: tuple[str,...]):
        opener=ts[idx]; idx+=1; entries=[]; children=False; is_literal=True
        while idx<n and ts[idx].value != '}':
            if ts[idx].value in {',',';'}:idx+=1;continue
            key=None
            if idx+1<n and ts[idx].kind=='ident' and ts[idx+1].value=='=':
                key=ts[idx].value;idx+=2
            elif idx+3<n and ts[idx].value=='[' and ts[idx+1].kind=='string' and ts[idx+2].value==']' and ts[idx+3].value=='=':
                key=decode_string(ts[idx+1].value);idx+=4
            if idx>=n:break
            if ts[idx].value=='{':
                children=True
                idx=table(idx,path+((key or f'#{len(entries)}'),))
            elif ts[idx].kind=='string' and key is None:
                entries.append(decode_string(ts[idx].value));idx+=1
            else:
                is_literal=False
                # Skip expressions up to top-level delimiter/closing brace.
                depth=0
                while idx<n:
                    v=ts[idx].value
                    if depth==0 and v in {',',';','}'}:break
                    if v in {'(','[','{'}:depth+=1
                    elif v in {')',']','}'}:depth=max(0,depth-1)
                    idx+=1
            if idx<n and ts[idx].value in {',',';'}:idx+=1
        if idx>=n:raise ParseError('Unclosed Lua table')
        closer=ts[idx]
        # Only accept literal leaf lists, never arbitrary Lua expressions.
        if entries and not children and is_literal:
            line=src.rfind('\n',0,opener.start)+1
            indent=re.match(r'[ \t]*',src[line:opener.start]).group()
            pools[path]=Pool(path,opener,closer,entries,indent)
        elif entries and not children and rejected_paths is not None:
            rejected_paths.add(path)
        return idx+1
    # Look for top-level literal assignment addon.localeData.<locale>.<name> = {
    # or other addon.* assignment, but never expansion scripts.
    for i,t in enumerate(ts):
        if t.kind!='ident' or t.value!='addon':continue
        j=i+1; fields=[]
        while j+1<n and ts[j].value=='.' and ts[j+1].kind=='ident':
            fields.append(ts[j+1].value);j+=2
        if j+1<n and ts[j].value=='=' and ts[j+1].value=='{':
            table(j+1,tuple(fields))
    return pools

def render_pool(pool:Pool,entries:list[str],newline:str='\n') -> str:
    """Render replacement list contents using the pool's indentation."""
    indent=pool.indent+'    '
    return (newline + ''.join(indent+encode_string(s)+','+newline for s in entries) + pool.indent)

def update_file(path:Path,updates:dict[tuple[str,...],list[str]], backup=True):
    """Validate and write changed literal pools, optionally backing up the file.

    Raises ValueError for missing pools, invalid text, or failed round-tripping.
    Returns True when written and None when the requested contents are unchanged.
    """
    with path.open('r',encoding='utf-8',newline='') as f:src=f.read()
    pools=parse_pools(src)
    missing=set(updates)-set(pools)
    if missing:raise ValueError(f'Pools not found: {missing}')
    nl='\r\n' if '\r\n' in src else '\n'
    patches=[]
    for key,entries in updates.items():
        pool=pools[key]
        if entries == pool.entries:
            continue  # No-op edits must preserve original Lua bytes and formatting.
        if not entries: raise ValueError(f'Pool {key} cannot be empty')
        for e in entries:
            if not isinstance(e,str) or not e.strip():raise ValueError(f'Empty text in {key}')
            if e.startswith('*') != e.endswith('*'):raise ValueError(f'Unbalanced emote stars in {key}: {e}')
            if '%' in re.sub(r'%(?:%|s|p)', '', e):raise ValueError(f'Invalid placeholder in {key}: {e}')
        patches.append((pool.opener.end,pool.closer.start,render_pool(pool,entries,nl)))
    dst=src
    for a,b,replacement in sorted(patches,reverse=True):dst=dst[:a]+replacement+dst[b:]
    # Always reparse before writing
    check=parse_pools(dst)
    for k,v in updates.items():
        if k not in check or check[k].entries!=v:raise ValueError(f'Round-trip failed: {k}')
    if dst==src:return None
    if backup:
        backup_name=path.with_suffix(path.suffix+'.'+datetime.now().strftime('%Y%m%d-%H%M%S-%f')+'.bak')
        shutil.copy2(path,backup_name)
    with path.open('w',encoding='utf-8',newline='') as f:f.write(dst)
    return True

def validate_file(path:Path):
    """Return parsed pools and text-format problems, not a full Lua syntax check."""
    with path.open(encoding='utf-8',newline='') as f:src=f.read()
    pools=parse_pools(src); problems=[]
    for key,pool in pools.items():
        for i,s in enumerate(pool.entries,1):
            if not s.strip():problems.append((key,i,'Empty text'))
            if s.startswith('*') != s.endswith('*'):problems.append((key,i,'Unbalanced *...*'))
            if '%' in re.sub(r'%(?:%|s|p)', '', s):problems.append((key,i,'Unsupported % placeholder'))
    return pools,problems
