"""Read-only inspection of installed RP addons, independent of any project source."""
from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path
from addon_manager import known_addons
from github_updates import parse_toc, check_addon, VersionCheck
from wow_detection import inspect_client


@dataclass(frozen=True)
class InstalledAddon:
    name: str
    version: str | None
    interface: str | None
    state: str


def inspect_installed(addons: Path, names: tuple[str, ...] | None = None) -> tuple[InstalledAddon, ...]:
    """Read only known RP addons; never read/write arbitrary other AddOns."""
    root = Path(addons)
    if root.name.casefold() != "addons" or root.parent.name.casefold() != "interface":
        raise ValueError("Ungültiges Interface/AddOns-Verzeichnis.")
    if inspect_client(root.parent.parent, "installed-addons") is None:
        raise ValueError("Keine plausible WoW-Installation erkannt.")
    if names is None:
        names = known_addons()
    results = []
    from wow_detection import _linked

    for name in names:
        toc = root / name / (name + ".toc")
        try:
            if _linked(toc) or _linked(toc.parent):
                raise OSError("Verknüpfung statt regulärem AddOn")
            version, interface = parse_toc(toc.read_text(encoding="utf-8-sig"))
            state = "Installiert" if version else "Version fehlt"
        except FileNotFoundError:
            version = interface = None
            state = "Nicht installiert"
        except (OSError, UnicodeError) as exc:
            version = interface = None
            state = "Nicht lesbar: " + str(exc)
        results.append(InstalledAddon(name, version, interface, state))
    return tuple(results)


def check_installed(addons: Path, names: tuple[str, ...] | None = None,
                    channel: str = "stable") -> tuple[VersionCheck, ...]:
    """Version-only GitHub queries; no local developer project required."""
    installed = inspect_installed(addons, names)
    return tuple(
        VersionCheck(row.name, row.version, None, channel, "Fehler", row.state)
        if row.state.startswith("Nicht lesbar:")
        else check_addon(row.name, addons, channel)
        for row in installed
    )
