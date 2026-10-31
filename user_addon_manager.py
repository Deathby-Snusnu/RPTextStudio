"""Inspect installed RP addons and check versions without a project checkout.

Inspection does not modify addon files. GitHub version checks can update the
local API cache managed by github_request_manager.
"""
from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path
from addon_manager import known_addons
from github_updates import parse_toc, check_addon, VersionCheck
from wow_detection import inspect_client


@dataclass(frozen=True)
class InstalledAddon:
    """Installed TOC metadata and the outcome of local inspection."""
    name: str
    version: str | None
    interface: str | None
    state: str


def _validated_names(names: tuple[str, ...] | None) -> tuple[str, ...]:
    """Restrict paths and GitHub lookups to IDs in the trusted addon catalog."""
    catalog = known_addons()
    allowed = frozenset(catalog)
    if names is None:
        return catalog
    if not isinstance(names, tuple) or any(
        not isinstance(name, str) or name not in allowed for name in names
    ):
        raise ValueError("Unbekannte oder ungültige AddOn-Auswahl.")
    if len(set(names)) != len(names):
        raise ValueError("AddOn-Auswahl enthält doppelte Einträge.")
    return names


def inspect_installed(addons: Path, names: tuple[str, ...] | None = None) -> tuple[InstalledAddon, ...]:
    """Inspect installed TOCs under a plausible Interface/AddOns directory.

    By default all catalog addons are examined. Caller-supplied names must
    match catalog IDs before they are used as filesystem path components.
    """
    names = _validated_names(names)
    root = Path(addons)
    if root.name.casefold() != "addons" or root.parent.name.casefold() != "interface":
        raise ValueError("Ungültiges Interface/AddOns-Verzeichnis.")
    if inspect_client(root.parent.parent, "installed-addons") is None:
        raise ValueError("Keine plausible WoW-Installation erkannt.")
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
    """Check installed addon versions against GitHub without a project checkout.

    Caller-supplied names are restricted to catalog IDs; the API client can
    write its cache.
    """
    installed = inspect_installed(addons, names)
    return tuple(
        VersionCheck(row.name, row.version, None, channel, "Fehler", row.state)
        if row.state.startswith("Nicht lesbar:")
        else check_addon(row.name, addons, channel)
        for row in installed
    )
