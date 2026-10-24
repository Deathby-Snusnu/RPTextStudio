"""Safe local WoW AddOn installation with a reviewable diff and recoverable backups."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from hashlib import sha256
from pathlib import Path
import json
import os
import shutil
import tempfile
import uuid
from addon_registry import discover

ADDONS = ("DruidenRP", "HexerRP", "JaegerRP", "PaladinRP", "RPChatMod", "RPControlCenter")
RUNTIME_SUFFIXES = {".toc", ".lua", ".xml", ".blp", ".tga", ".dds", ".png", ".jpg",
                    ".jpeg", ".ogg", ".mp3", ".wav", ".ttf", ".otf"}
SKIP_DIRS = {".git", ".vscode", ".pytest_cache", "__pycache__", "tests", "tools",
             "docs", "build", "dist", ".venv", "venv"}
MAX_FILES = 10000
MAX_BYTES = 256 * 1024 * 1024


def _linked(path: Path) -> bool:
    import stat
    try:
        info = path.lstat()
    except FileNotFoundError:
        return False
    return stat.S_ISLNK(info.st_mode) or bool(
        getattr(info, "st_file_attributes", 0) & stat.FILE_ATTRIBUTE_REPARSE_POINT
    )


class InstallError(RuntimeError):
    pass


@dataclass(frozen=True)
class AddonChange:
    name: str
    added: tuple[str, ...]
    changed: tuple[str, ...]
    removed: tuple[str, ...]

    @property
    def is_changed(self) -> bool:
        return bool(self.added or self.changed or self.removed)


def _hash(path: Path) -> str:
    h = sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def _files(folder: Path, *, runtime: bool) -> dict[str, Path]:
    if _linked(folder) or not folder.is_dir():
        raise InstallError(f"Ungültiger AddOn-Ordner: {folder}")
    result = {}
    count = total = 0
    def fail_walk(exc: OSError) -> None:
        raise InstallError(f"AddOn-Verzeichnis kann nicht gelesen werden: {exc}") from exc

    for root, dirs, files in os.walk(folder, followlinks=False, onerror=fail_walk):
        here = Path(root)
        for directory in dirs:
            if _linked(here / directory):
                raise InstallError(f"Verknüpfung im AddOn: {here / directory}")
        dirs[:] = sorted(d for d in dirs if not runtime or d.lower() not in SKIP_DIRS)
        for filename in sorted(files):
            path = here / filename
            if _linked(path) or not path.is_file():
                raise InstallError(f"Ungültige Datei: {path}")
            rel = path.relative_to(folder).as_posix()
            if runtime and path.suffix.lower() not in RUNTIME_SUFFIXES:
                continue
            count += 1
            total += path.stat().st_size
            if count > MAX_FILES or total > MAX_BYTES:
                raise InstallError(f"AddOn überschreitet Größenlimit: {folder.name}")
            result[rel] = path
    return result


def _validate_target(target: Path, source: Path) -> Path:
    target = target.absolute()
    source = source.resolve()
    if target.name.casefold() != "addons" or target.parent.name.casefold() != "interface":
        raise InstallError("Ziel muss der WoW-Ordner Interface/AddOns sein.")
    for folder in (target, *target.parents):
        if _linked(folder):
            raise InstallError(f"Symbolischer Link/Junction nicht zulässig: {folder}")
    canonical = target.resolve()
    if canonical == source or canonical in source.parents or source in canonical.parents:
        raise InstallError("Entwicklungsordner darf nicht Installationsziel sein.")
    return target


def _validate_selection(source: Path, target: Path, names: tuple[str, ...]) -> None:
    known = discover(source)
    if not names or len(names) != len(set(names)) or any(n not in known for n in names):
        raise InstallError("Ungültige AddOn-Auswahl.")
    for name in names:
        folder = source / name
        if not (folder / (name + ".toc")).is_file():
            raise InstallError(f"TOC fehlt: {name}/{name}.toc")
        if (target / name).exists() and not (target / name).is_dir():
            raise InstallError(f"Ziel ist kein Verzeichnis: {target / name}")
        for candidate in (folder, target / name):
            if candidate.exists() and _linked(candidate):
                raise InstallError(f"Verknüpfung nicht zulässig: {candidate}")


def preview(source: Path, target: Path, names: tuple[str, ...] = ADDONS) -> tuple[AddonChange, ...]:
    source = Path(source).resolve()
    target = _validate_target(Path(target), source)
    _validate_selection(source, target, names)
    changes = []
    for name in names:
        src = _files(source / name, runtime=True)
        dst = _files(target / name, runtime=False) if (target / name).exists() else {}
        added = sorted(set(src) - set(dst))
        removed = sorted(set(dst) - set(src))
        changed = sorted(k for k in set(src) & set(dst) if _hash(src[k]) != _hash(dst[k]))
        changes.append(AddonChange(name, tuple(added), tuple(changed), tuple(removed)))
    return tuple(changes)


def install(source: Path, target: Path, names: tuple[str, ...] = ADDONS,
            *, approved: tuple[AddonChange, ...] | None = None) -> Path:
    """Apply only a reviewed plan. Backups remain under AddOns/.addon-backups."""
    source = Path(source).resolve()
    target = _validate_target(Path(target), source)
    plan = preview(source, target, names)
    if approved is None or plan != approved:
        raise InstallError("Vorschau ist nicht freigegeben oder hat sich geändert.")
    if not any(x.is_changed for x in plan):
        raise InstallError("Keine Änderungen zur Installation.")
    target.mkdir(parents=True, exist_ok=True)
    backups = target / ".addon-backups"
    if _linked(backups):
        raise InstallError("Unsicherer Backup-Ordner.")
    token = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ") + "-" + uuid.uuid4().hex[:10]
    stage = Path(tempfile.mkdtemp(prefix=".rpstudio-stage-", dir=target))
    backup = backups / token
    moved, deployed = [], []
    changed = [p for p in plan if p.is_changed]
    try:
        for item in changed:
            staged = stage / item.name
            staged.mkdir()
            for rel, path in _files(source / item.name, runtime=True).items():
                dest = staged / Path(rel)
                dest.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(path, dest)
                if _hash(path) != _hash(dest):
                    raise InstallError(f"Kopierprüfung fehlgeschlagen: {item.name}/{rel}")
        if preview(source, target, names) != approved:
            raise InstallError("Dateien haben sich während der Vorbereitung geändert.")
        backup.mkdir(parents=True, exist_ok=False)
        for item in changed:
            dest = target / item.name
            if dest.exists():
                dest.rename(backup / item.name)
                moved.append(item.name)
            (stage / item.name).rename(dest)
            deployed.append(item.name)
        manifest = {"timestamp": token, "names": [x.name for x in changed],
                    "previously_installed": moved}
        (backup / "manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
        return backup
    except Exception:
        for name in reversed(deployed):
            shutil.rmtree(target / name)
        for name in reversed(moved):
            (backup / name).rename(target / name)
        raise
    finally:
        shutil.rmtree(stage, ignore_errors=True)


def rollback(target: Path, backup: Path) -> None:
    """Restore a previous installation, keeping the replaced version separately."""
    target = Path(target).absolute()
    backup = Path(backup).absolute()
    if target.name.casefold() != "addons" or target.parent.name.casefold() != "interface":
        raise InstallError("Ungültiger Installationspfad.")
    if any(_linked(folder) for folder in (target, *target.parents)):
        raise InstallError("Unsicheres Installationsziel.")
    base = target / ".addon-backups"
    if backup.parent != base or _linked(backup) or _linked(base):
        raise InstallError("Sicherung liegt außerhalb des Backup-Verzeichnisses.")
    data = json.loads((backup / "manifest.json").read_text(encoding="utf-8"))
    names = data["names"]
    previous = set(data["previously_installed"])
    if any(n not in ADDONS for n in names):
        raise InstallError("Ungültiger Backup-Inhalt.")
    for name in names:
        if _linked(target / name) or _linked(backup / name):
            raise InstallError("Verknüpfte Verzeichnisse sind nicht zulässig.")
        if name in previous and not (backup / name).is_dir():
            raise InstallError(f"Sicherung fehlt: {name}")
    reverted = base / ("pre-rollback-" + uuid.uuid4().hex)
    reverted.mkdir(parents=True)
    moved_current, restored = [], []
    try:
        for name in names:
            if (target / name).exists():
                (target / name).rename(reverted / name)
                moved_current.append(name)
            if name in previous:
                (backup / name).rename(target / name)
                restored.append(name)
    except Exception:
        for name in reversed(restored):
            (target / name).rename(backup / name)
        for name in reversed(moved_current):
            (reverted / name).rename(target / name)
        raise
