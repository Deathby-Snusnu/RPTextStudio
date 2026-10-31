"""Read-only, bounded Windows World of Warcraft installation discovery.

Only a validated candidate may be offered to the installer; discovery never writes.
Battle.net metadata is treated as a hint, not a trusted source of paths.
"""
from __future__ import annotations

from dataclasses import dataclass, replace
from pathlib import Path
from collections import deque
import os
import re
import stat

CLIENT_DIRS = {
    "_retail_": "retail",
    "_classic_": "classic",
    "_classic_era_": "classic_era",
    "_anniversary_": "anniversary",
    "_ptr_": "ptr",
    "_xptr_": "ptr",
    "_beta_": "beta",
}
EXE_NAMES = {"wow.exe", "wowclassic.exe", "wowclassicera.exe", "wowt.exe",
             "wow-64.exe", "wowclassic-64.exe"}
WOW_NAMES = {"world of warcraft", "wow", "wow forever", "wow-forever", "wowforever"}
MAX_DIRECTORY_VISITS = 20000
MAX_DIRECTORY_ENTRIES = 200000
MAX_DEPTH = 4


@dataclass(frozen=True)
class WoWInstallation:
    """Describe a detected client, its evidence, confidence, and target path."""

    client_root: Path
    addons_path: Path
    client_type: str
    display_name: str
    confidence: str
    reasons: tuple[str, ...]
    sources: tuple[str, ...]
    verified: bool


def _linked(path: Path) -> bool:
    try:
        details = path.lstat()
    except OSError:
        return False
    reparse_point = getattr(stat, "FILE_ATTRIBUTE_REPARSE_POINT", 0x400)
    return stat.S_ISLNK(details.st_mode) or bool(
        getattr(details, "st_file_attributes", 0) & reparse_point
    )


def _usable_dir(path: Path) -> bool:
    try:
        return path.is_dir() and not _linked(path)
    except OSError:
        return False


def _children(folder: Path):
    try:
        return list(folder.iterdir())
    except (OSError, PermissionError):
        return []


def _normalize_hint(path: Path) -> Path:
    """Accept client root, game collection, Interface or Interface/AddOns."""
    path = Path(path).expanduser().absolute()
    if path.name.lower() == "addons" and path.parent.name.lower() == "interface":
        return path.parent.parent
    if path.name.lower() == "interface":
        return path.parent
    return path


def _candidate_roots(path: Path) -> list[Path]:
    path = _normalize_hint(path)
    if not _local_root(path):
        return []
    results = [path]
    if _usable_dir(path):
        results.extend(p for p in _children(path)
                       if _usable_dir(p) and p.name.lower() in CLIENT_DIRS)
    return results


def inspect_client(path: Path, source: str = "scan") -> WoWInstallation | None:
    """Inspect one local candidate without creating or changing files.

    A plausible candidate may be returned without ``verified``; automatic
    verification requires high confidence. Linked and network paths are not
    accepted. A verified installation is not an addon compatibility claim.
    """
    root = _normalize_hint(path)
    if not _local_root(root):
        return None
    if not _usable_dir(root):
        return None
    if any(_linked(p) for p in (root, *root.parents)):
        return None
    interface = root / "Interface"
    addons = interface / "AddOns"
    exe = any(p.is_file() and not _linked(p) and
              (p.name.casefold() in EXE_NAMES or
               bool(re.fullmatch(r"wow(?:classic\w*)?(?:-64)?\.exe", p.name, re.I)))
              for p in _children(root))
    has_interface = _usable_dir(interface)
    has_addons = _usable_dir(addons)
    has_wtf = _usable_dir(root / "WTF")
    known_dir = root.name.lower() in CLIENT_DIRS
    # Require game executable or two independent structural signals plus client naming.
    likely_name = known_dir or ("wow" in root.name.lower() or
                               "warcraft" in root.name.lower())
    plausible = exe or (likely_name and has_interface and has_wtf)
    if not plausible:
        return None
    # A writable target may not yet exist; never create it during detection.
    if (_linked(interface) or _linked(addons) or
            (interface.exists() and not has_interface) or
            (addons.exists() and not has_addons)):
        return None
    reasons = []
    if exe:
        reasons.append("WoW-Programmdatei gefunden")
    if known_dir:
        reasons.append("Bekannter Clientordner")
    if has_interface:
        reasons.append("Interface-Verzeichnis vorhanden")
    if has_wtf:
        reasons.append("WTF-Verzeichnis vorhanden")
    if has_addons:
        reasons.append("AddOns-Verzeichnis vorhanden")
    kind = CLIENT_DIRS.get(root.name.lower(), "custom")
    high = exe and has_interface and (has_wtf or known_dir)
    medium = exe or (has_interface and has_wtf)
    confidence = "hoch" if high else "mittel" if medium else "niedrig"
    # Only high confidence is automatically verified; others need manual confirmation.
    return WoWInstallation(root, addons, kind,
                           root.name, confidence, tuple(reasons), (source,), high)


def _identity(path: Path) -> str:
    return os.path.normcase(os.path.realpath(str(path))).casefold()


def _merge(results: list[WoWInstallation]) -> list[WoWInstallation]:
    merged = {}
    for item in results:
        key = _identity(item.client_root)
        if key not in merged:
            merged[key] = item
        else:
            prev = merged[key]
            best = item if (item.verified and not prev.verified) else prev
            merged[key] = replace(best, sources=tuple(dict.fromkeys(prev.sources + item.sources)))
    return sorted(merged.values(), key=lambda i: (not i.verified, i.client_type, str(i.client_root).casefold()))


def _windows_drive_type(path: Path) -> int:
    if os.name != "nt":
        return 3
    try:
        import ctypes
        return ctypes.windll.kernel32.GetDriveTypeW(str(Path(path).anchor))
    except (AttributeError, OSError):
        return 0


def _local_root(path: Path) -> bool:
    path = Path(path)
    if str(path).startswith(("\\\\", "//")):
        return False
    return _windows_drive_type(path) in (2, 3, 6)


def _local_drive_roots() -> tuple[Path, ...]:
    if os.name != "nt":
        return tuple(
            path for letter in "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
            if (path := Path(f"{letter}:\\")).exists()
        )
    return tuple(
        path for letter in "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
        if _windows_drive_type(path := Path(f"{letter}:\\")) in (2, 3, 6)
    )


def known_locations(env: dict[str, str] | None = None,
                    drives: tuple[Path, ...] | None = None) -> list[Path]:
    """Construct standard local installation hints without validating them."""
    env = os.environ if env is None else env
    bases = [Path(env[k]) for k in ("ProgramFiles(x86)", "ProgramFiles", "PUBLIC")
             if env.get(k)]
    if drives is None:
        drives = _local_drive_roots()
    candidates = []
    for base in (*bases, *drives):
        for rel in ("World of Warcraft", "Games/World of Warcraft",
                    "Games/WoW", "Games/WoW-Forever", "Spiele/World of Warcraft",
                    "Spiele/WoW", "WoW", "WoW-Forever"):
            candidates.append(base / rel)
    return candidates


def scan_selected_drives(drives: tuple[Path, ...], *,
                         max_depth: int = MAX_DEPTH,
                         max_visits: int = MAX_DIRECTORY_VISITS,
                         max_entries: int | None = None,
                         cancelled=None) -> list[Path]:
    """Opt-in bounded search: never traverse junctions, symlinks or network shares."""
    if (not 0 <= max_depth <= 8 or not 1 <= max_visits <= MAX_DIRECTORY_VISITS
            or (max_entries is not None
                and not 1 <= max_entries <= MAX_DIRECTORY_ENTRIES)):
        raise ValueError("Ungültige Suchgrenzen")
    found = []
    visited = 0
    entry_limit = max_entries or min(MAX_DIRECTORY_ENTRIES, max_visits * 10)
    queue = deque()
    for root in drives:
        if cancelled is not None and cancelled():
            break
        if len(queue) >= max_visits:
            break
        folder = Path(root).absolute()
        if _local_root(folder):
            queue.append((folder, 0))
    seen = set()
    entries_examined = 0
    while queue and visited < max_visits and entries_examined < entry_limit:
        if cancelled is not None and cancelled():
            break
        folder, depth = queue.popleft()
        if not _usable_dir(folder):
            continue
        identifier = _identity(folder)
        if identifier in seen:
            continue
        seen.add(identifier)
        visited += 1
        name = folder.name.casefold()
        if name in CLIENT_DIRS or "wow" in name or "warcraft" in name:
            found.append(folder)
        if depth >= max_depth:
            continue
        try:
            children = iter(folder.iterdir())
            while entries_examined < entry_limit and len(queue) < max_visits:
                if cancelled is not None and cancelled():
                    return found
                try:
                    child = next(children)
                except StopIteration:
                    break
                entries_examined += 1
                if _usable_dir(child):
                    queue.append((child, depth + 1))
        except (OSError, PermissionError):
            continue
    return found


def discover_wow_installations(saved_paths=(), *, custom_paths=(),
                               extra_roots=(), deep_scan=False,
                               drives=(), cancelled=None,
                               include_standard=True) -> list[WoWInstallation]:
    """Inspect supplied and optional standard hints, merging duplicate clients.

    A bounded drive search is used only when ``deep_scan`` and ``drives`` are
    supplied. Cancellation can return partial results; nothing is installed.
    """
    hints = [(Path(path), "gespeichert") for path in saved_paths]
    hints += [(Path(path), "manuell") for path in custom_paths]
    hints += [(Path(path), "Hinweis") for path in extra_roots]
    if include_standard:
        hints += [(p, "Standardpfad") for p in known_locations()]
    if deep_scan and drives:
        hints += [(p, "Erweiterte Suche")
                  for p in scan_selected_drives(tuple(map(Path, drives)), cancelled=cancelled)]
    found = []
    for path, source in hints:
        if cancelled is not None and cancelled():
            break
        for root in _candidate_roots(path):
            match = inspect_client(root, source)
            if match:
                found.append(match)
    return _merge(found)
