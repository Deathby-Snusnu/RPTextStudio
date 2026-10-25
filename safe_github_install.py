"""Conservative install of a verified GitHub staging directory.

Existing files are retained byte-for-byte, except for the explicitly approved
TOC Interface line. New runtime files are copied. A full folder backup is kept.
No automatic merge or overwrite of existing Lua, text, XML or assets.
"""
from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path
from hashlib import sha256
import json
from datetime import datetime, timezone
import os
import shutil
import tempfile
import uuid

from addon_manager import ADDONS, _files, _hash, _linked, InstallError
from wow_detection import inspect_client
from wow_client_profiles import preview_toc, ClientProfile

@dataclass(frozen=True)
class SafePlan:
    name: str
    target: Path
    source: Path
    interface: str
    new_files: tuple[str, ...]
    protected: tuple[str, ...]
    toc_changed: bool
    source_hashes: tuple[tuple[str, str], ...]
    target_hashes: tuple[tuple[str, str], ...]
    # Explicit, individually reviewed exceptions to the default file protection.
    approved_overwrites: tuple[str, ...] = ()

def _validate(name: str, staged: Path, target: Path, profile: ClientProfile):
    if name not in ADDONS:
        raise InstallError("Unbekanntes RP-AddOn.")
    if target.name.casefold() != "addons" or target.parent.name.casefold() != "interface":
        raise InstallError("Ziel muss Interface/AddOns sein.")
    installation = inspect_client(target.parent.parent)
    if installation is None or not installation.verified or installation.client_root.resolve() != profile.client_root.resolve():
        raise InstallError("Ausgewählte WoW-Installation nicht bestätigt.")
    if any(_linked(p) for p in (target, *target.parents, staged, *staged.parents)):
        raise InstallError("Verknüpfte Verzeichnisse sind nicht zulässig.")
    if not staged.is_dir() or staged.resolve() == target.resolve() or target.resolve() in staged.resolve().parents:
        raise InstallError("Unsicherer Staging-Ordner.")
    if (target / name).exists() and not (target / name).is_dir():
        raise InstallError("Ziel ist kein AddOn-Verzeichnis.")

def _casefold_index(files: dict[str, Path]) -> dict[str, str]:
    result = {}
    for rel in files:
        key = rel.casefold()
        if key in result:
            raise InstallError("Mehrere Dateien unterscheiden sich nur durch Groß-/Kleinschreibung.")
        result[key] = rel
    return result

def preview_safe_install(name: str, staged: Path, target: Path, profile: ClientProfile,
                         *, approved_overwrites: tuple[str, ...] = ()) -> SafePlan:
    staged, target = Path(staged).absolute(), Path(target).absolute()
    _validate(name, staged, target, profile)
    src = _files(staged, runtime=True)
    dest = target / name
    old = _files(dest, runtime=False) if dest.exists() else {}
    toc = name + ".toc"
    if toc not in src:
        raise InstallError("Gleichnamige TOC fehlt im Staging.")
    _casefold_index(src)
    old_names = _casefold_index(old)
    old_toc = old_names.get(toc.casefold())
    upstream = src[toc].read_text(encoding="utf-8-sig")
    preview_toc(upstream, profile.interface, compatible=True)
    if old_toc is not None:
        # Validate that the existing TOC is parseable before preparing any changes.
        preview_toc(old[old_toc].read_text(encoding="utf-8-sig"), profile.interface, compatible=True)
    new = tuple(sorted(k for k in src if k.casefold() not in old_names))
    protected = tuple(sorted(
        k for k in src
        if k.casefold() in old_names
        and not k.casefold().endswith(".toc")
        and _hash(src[k]) != _hash(old[old_names[k.casefold()]])
    ))
    # A file may only be replaced if it was actually reported as protected
    # in THIS snapshot. TOC and new/unchanged files are never user-selectable.
    selected = tuple(sorted(set(approved_overwrites)))
    if len(selected) != len(approved_overwrites) or any(rel not in protected for rel in selected):
        raise InstallError("Ungültige Auswahl geschützter Dateien.")
    current_toc = old[old_toc].read_text(encoding="utf-8-sig") if old_toc is not None else upstream
    adapted = preview_toc(current_toc, profile.interface, compatible=True)
    return SafePlan(name, target, staged, profile.interface, new, protected,
                    adapted != current_toc,
                    tuple(sorted((k, _hash(v)) for k, v in src.items())),
                    tuple(sorted((k, _hash(v)) for k, v in old.items())),
                    selected)

def install_safe(plan: SafePlan, profile: ClientProfile) -> Path:
    """Apply previously approved exact plan, then return persistent backup path."""
    if preview_safe_install(plan.name, plan.source, plan.target, profile,
                            approved_overwrites=plan.approved_overwrites) != plan:
        raise InstallError("Dateien oder Installationsprofil wurden seit der Vorschau geändert.")
    if not plan.new_files and not plan.toc_changed and not plan.approved_overwrites:
        raise InstallError("Keine sicheren Änderungen vorhanden.")
    target = plan.target
    dest = target / plan.name
    backups = target / ".addon-backups"
    if _linked(backups):
        raise InstallError("Unsicheres Backup-Verzeichnis.")
    token = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ") + "-" + uuid.uuid4().hex[:10]
    backup = backups / token
    target.mkdir(parents=True, exist_ok=True)
    # Prepare beside target. Existing files are all preserved, including unknown formats.
    target.mkdir(parents=True, exist_ok=True)
    work = Path(tempfile.mkdtemp(prefix=".rpstudio-safe-", dir=target))
    ready = work / plan.name
    moved = False
    deployed = False
    manifest = {
        "timestamp": token, "names": [plan.name],
        "previously_installed": [plan.name] if dest.exists() else [],
        "status": "installing",
    }

    def write_manifest() -> None:
        temporary_manifest = backup / ".manifest.json.tmp"
        temporary_manifest.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
        temporary_manifest.replace(backup / "manifest.json")

    try:
        if dest.exists():
            shutil.copytree(dest, ready, symlinks=False)
        else:
            ready.mkdir()
        incoming = _files(plan.source, runtime=True)
        for rel in plan.new_files:
            output = ready / rel
            output.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(incoming[rel], output)
            if _hash(output) != dict(plan.source_hashes)[rel]:
                raise InstallError("Kopierprüfung fehlgeschlagen: " + rel)
        # The existing filename's spelling is preserved for case-insensitive
        # Windows volumes. Every explicit replacement is verified byte-for-byte.
        ready_names = _casefold_index(_files(ready, runtime=False))
        for rel in plan.approved_overwrites:
            old_rel = ready_names.get(rel.casefold())
            if old_rel is None:
                raise InstallError("Freigegebene Datei fehlt bei der Vorbereitung: " + rel)
            output = ready / old_rel
            shutil.copy2(incoming[rel], output)
            if _hash(output) != dict(plan.source_hashes)[rel]:
                raise InstallError("Kopierprüfung fehlgeschlagen: " + rel)
        toc_rel = next(
            (rel for rel, _ in plan.target_hashes if rel.casefold() == (plan.name + ".toc").casefold()),
            plan.name + ".toc",
        )
        toc = ready / toc_rel
        original_bytes = toc.read_bytes()
        has_bom = original_bytes.startswith(b"\xef\xbb\xbf")
        original = original_bytes.decode("utf-8-sig")
        changed = preview_toc(original, plan.interface, compatible=True)
        if changed != original:
            toc.write_bytes((b"\xef\xbb\xbf" if has_bom else b"") + changed.encode("utf-8"))
        if preview_safe_install(plan.name, plan.source, target, profile,
                                approved_overwrites=plan.approved_overwrites) != plan:
            raise InstallError("Dateien während der Vorbereitung geändert.")
        backup.mkdir(parents=True, exist_ok=False)
        write_manifest()
        if dest.exists():
            dest.rename(backup / plan.name)
            moved = True
        ready.rename(dest)
        deployed = True
        manifest["status"] = "complete"
        write_manifest()
        return backup
    except Exception:
        if deployed and dest.exists():
            shutil.rmtree(dest)
        if moved and (backup / plan.name).exists():
            (backup / plan.name).rename(dest)
        shutil.rmtree(backup, ignore_errors=True)
        raise
    finally:
        shutil.rmtree(work, ignore_errors=True)
