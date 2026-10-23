"""Discovery and opt-in metadata for RP Text Studio projects."""
from __future__ import annotations
import json
import re
from pathlib import Path
from project_paths import addons_root, project_root

ID = re.compile(r"^[A-Za-z][A-Za-z0-9_]{1,63}$")
REPOSITORY = re.compile(r"^[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+$")
REGISTRY = "addons.json"


def discover(root: Path) -> dict[str, Path]:
    folder = addons_root(root)
    result = {}
    if not folder.is_dir():
        return result
    for candidate in folder.iterdir():
        if not candidate.is_dir() or candidate.is_symlink() or not ID.fullmatch(candidate.name):
            continue
        if (candidate / (candidate.name + ".toc")).is_file():
            result[candidate.name] = candidate
    return dict(sorted(result.items()))


def load_registry(root: Path) -> dict:
    path = project_root(root) / REGISTRY
    if not path.exists():
        return {"schema": 1, "addons": []}
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict) or data.get("schema") != 1 or not isinstance(data.get("addons"), list):
        raise ValueError("Ungültiges AddOn-Register.")
    ids = set()
    for item in data["addons"]:
        if not isinstance(item, dict) or not ID.fullmatch(str(item.get("id", ""))):
            raise ValueError("Ungültiger AddOn-Eintrag.")
        if item["id"].casefold() in ids:
            raise ValueError("Doppelter AddOn-Eintrag.")
        ids.add(item["id"].casefold())
        repository = item.get("repository")
        if repository is not None and not REPOSITORY.fullmatch(str(repository)):
            raise ValueError("Ungültiges Repository.")
    return data


def register(root: Path, entry: dict, *, persist=True) -> dict:
    """Add a validated local addon; never replace existing registrations."""
    name = entry.get("id", "")
    if not isinstance(name, str) or not ID.fullmatch(name):
        raise ValueError("Ungültige AddOn-ID.")
    if name not in discover(root):
        raise ValueError("AddOn besitzt keine gültige TOC im Quellordner.")
    repo = entry.get("repository")
    if repo is not None and (not isinstance(repo, str) or not REPOSITORY.fullmatch(repo)):
        raise ValueError("Ungültiges GitHub-Repository.")
    data = load_registry(root)
    if any(x["id"].casefold() == name.casefold() for x in data["addons"]):
        raise ValueError("AddOn ist bereits registriert.")
    data["addons"].append(dict(entry))
    data["addons"].sort(key=lambda a: a["id"].lower())
    if persist:
        path = project_root(root) / REGISTRY
        tmp = path.with_suffix(".json.tmp")
        tmp.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        tmp.replace(path)
    return data


def available(root: Path) -> list[dict]:
    """Registered entries with a valid local source, including future addons."""
    projects = discover(root)
    return [entry for entry in load_registry(root)["addons"] if entry["id"] in projects and entry.get("enabled", True)]
