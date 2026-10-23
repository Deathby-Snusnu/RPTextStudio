"""Per-user remembered WoW installations; never stored in the source repository."""
from __future__ import annotations
from pathlib import Path
import json
import os
from wow_detection import WoWInstallation, discover_wow_installations

MAX_ENTRIES = 40


def settings_path(env: dict[str, str] | None = None) -> Path:
    env = os.environ if env is None else env
    base = env.get("LOCALAPPDATA")
    if base:
        return Path(base) / "RPTextStudio" / "installations.json"
    return Path.home() / ".rptextstudio" / "installations.json"


def load_paths(path: Path | None = None) -> list[Path]:
    file = Path(path) if path is not None else settings_path()
    try:
        obj = json.loads(file.read_text(encoding="utf-8"))
        if not isinstance(obj, dict) or obj.get("schema") != 1:
            return []
        raw = obj.get("paths", [])
        if not isinstance(raw, list):
            return []
        return [Path(v) for v in raw[:MAX_ENTRIES]
                if isinstance(v, str) and v.strip() and "\x00" not in v]
    except (FileNotFoundError, ValueError, OSError, UnicodeError):
        return []


def save_paths(paths, path: Path | None = None) -> None:
    file = Path(path) if path is not None else settings_path()
    unique = []
    seen = set()
    for candidate in paths:
        candidate = Path(candidate).absolute()
        normalized = os.path.normcase(str(candidate)).casefold()
        if normalized not in seen:
            seen.add(normalized)
            unique.append(str(candidate))
    if len(unique) > MAX_ENTRIES:
        raise ValueError("Zu viele gespeicherte Installationen.")
    file.parent.mkdir(parents=True, exist_ok=True)
    temporary = file.with_suffix(".tmp")
    temporary.write_text(json.dumps({"schema": 1, "paths": unique}, indent=2),
                         encoding="utf-8")
    temporary.replace(file)


def discover_saved(*, include_standard=True) -> list[WoWInstallation]:
    return discover_wow_installations(load_paths(), include_standard=include_standard)
