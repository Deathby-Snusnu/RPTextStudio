"""Explicit multilingual text associations stored outside game Lua files.

A link points to the text and its last observed index. Resolving requires a
matching text, so changed lists cannot silently attach an unrelated translation.
"""
from __future__ import annotations
import json
from pathlib import Path
from project_paths import metadata_path

LANGS = ('deDE', 'enUS', 'frFR')
FILE_NAME = '.rptextstudio-translations.json'

def pool_id(relative_path: str, key: tuple[str, ...]) -> str:
    """Build a pool identity, normalizing a localeData language when present."""
    parts = Path(relative_path).parts
    if len(parts) < 4 or parts[-2] not in LANGS:
        raise ValueError('Unrecognized locale text path')
    normalized=list(key)
    if len(normalized)>1 and normalized[0]=='localeData' and normalized[1] in LANGS:
        normalized[1]='*'
    return json.dumps([parts[-4], parts[-1], normalized], ensure_ascii=False)

def resolve(entries: list[str], ref: dict | None) -> int | None:
    """Resolve a saved index and text, or a uniquely matching moved text.

    If the saved index no longer matches, missing or non-unique text returns None.
    """
    if not ref or not isinstance(ref.get('text'), str):
        return None
    text = ref['text']
    index = ref.get('index')
    if isinstance(index, int) and 0 <= index < len(entries) and entries[index] == text:
        return index
    matches = [i for i, value in enumerate(entries) if value == text]
    return matches[0] if len(matches) == 1 else None

def reference(entries: list[str], index: int) -> dict:
    """Capture an existing entry's index and text; reject out-of-range indices."""
    if not 0 <= index < len(entries):
        raise IndexError(index)
    return {'index': index, 'text': entries[index]}

def read_links(root: Path) -> dict:
    """Read and validate associations, normalizing legacy locale identifiers."""
    file = metadata_path(root, FILE_NAME)
    if not file.exists():
        return {}
    payload = json.loads(file.read_text(encoding='utf-8'))
    if not isinstance(payload, dict) or payload.get('version') != 1 or not isinstance(payload.get('pools'), dict):
        raise ValueError('Invalid translation association file')
    pools = payload['pools']
    for groups in pools.values():
        if not isinstance(groups, list):
            raise ValueError('Invalid translation groups')
        for group in groups:
            if not isinstance(group, dict) or not all(k in LANGS for k in group):
                raise ValueError('Invalid translation language')
    # Migrate version-1 identifiers that embedded a locale in the Lua key.
    # They previously split one translation pool into separate DE/EN/FR identities.
    normalized={}
    for identifier, groups in pools.items():
        try:
            addon, filename, key=json.loads(identifier)
            if isinstance(key,list) and len(key)>1 and key[0]=='localeData' and key[1] in LANGS:
                key[1]='*'
            identity=json.dumps([addon,filename,key],ensure_ascii=False)
        except (TypeError,ValueError,IndexError):
            identity=identifier
        target=normalized.setdefault(identity,[])
        for group in groups:
            if group not in target:target.append(group)
    return normalized

def write_links(root: Path, pools: dict) -> None:
    """Write changed associations and back up an existing registry first."""
    file = metadata_path(root, FILE_NAME, write=True)
    payload = {'version': 1, 'description': 'Explicit editor-only text associations; game Lua files are unaffected.', 'pools': pools}
    data = json.dumps(payload, indent=2, ensure_ascii=False) + '\n'
    if file.exists() and file.read_text(encoding='utf-8') == data:
        return
    if file.exists():
        import shutil
        shutil.copy2(file, file.with_suffix(file.suffix + '.bak'))
    temp = file.with_suffix(file.suffix + '.tmp')
    temp.write_text(data, encoding='utf-8')
    temp.replace(file)
