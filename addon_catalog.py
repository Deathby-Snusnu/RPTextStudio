"""Verified, data-driven catalog for RP text add-ons.

Catalog data is untrusted input. Parsing does not download files, execute code,
or grant installation permission. The current bundled catalog allows only
explicitly trusted GitHub repositories from the publisher.
"""
from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path
import re

ADDON_ID = re.compile(r"^[A-Za-z][A-Za-z0-9_]{1,63}$")
REPOSITORY = re.compile(r"^[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+$")
MAX_CATALOG_BYTES = 512 * 1024
BUILTIN_PATH = Path(__file__).with_name("addon_catalog.json")


@dataclass(frozen=True)
class CatalogAddon:
    id: str
    title: str
    repository: str
    supported_clients: tuple[str, ...]
    classes: tuple[str, ...]
    description: str = ""


def parse_catalog(raw: bytes, *, trusted_owner: str = "Deathby-Snusnu") -> tuple[CatalogAddon, ...]:
    """Validate entries before presenting them to users.

    A catalog is a *discovery* source, not evidence that an addon is compatible.
    A client's compatibility must be checked independently before installing.
    """
    if len(raw) > MAX_CATALOG_BYTES:
        raise ValueError("AddOn-Katalog ist zu groß.")
    try:
        data = json.loads(raw.decode("utf-8"))
    except (UnicodeError, ValueError) as exc:
        raise ValueError("Ungültiges Katalogformat.") from exc
    if not isinstance(data, dict) or data.get("schema") != 1:
        raise ValueError("Nicht unterstützte Katalogversion.")
    entries = data.get("addons")
    if not isinstance(entries, list) or len(entries) > 256:
        raise ValueError("Ungültige Anzahl von AddOns.")
    result = []
    seen = set()
    for entry in entries:
        if not isinstance(entry, dict):
            raise ValueError("Ungültiger AddOn-Eintrag.")
        name, repo = entry.get("id"), entry.get("repository")
        title, description = entry.get("title"), entry.get("description", "")
        clients, classes = entry.get("supported_clients"), entry.get("classes", [])
        if not isinstance(name, str) or not ADDON_ID.fullmatch(name):
            raise ValueError("Ungültige AddOn-ID.")
        if name.casefold() in seen:
            raise ValueError("Doppelte AddOn-ID.")
        seen.add(name.casefold())
        if not isinstance(repo, str) or not REPOSITORY.fullmatch(repo):
            raise ValueError("Ungültiger Repository-Name.")
        owner, repository_name = repo.split("/", 1)
        if owner != trusted_owner or repository_name != name:
            raise ValueError("Repository ist für diesen Katalog nicht freigegeben.")
        if not isinstance(title, str) or not title.strip() or len(title) > 80:
            raise ValueError("Ungültiger Anzeigename.")
        if not isinstance(description, str) or len(description) > 300:
            raise ValueError("Ungültige Beschreibung.")
        if not isinstance(clients, list) or not all(
            isinstance(c, str) and re.fullmatch(r"[a-z0-9_-]{2,40}", c)
            for c in clients
        ) or len(set(clients)) != len(clients):
            raise ValueError("Ungültige Client-Angaben.")
        if not isinstance(classes, list) or len(classes) > 32 or not all(
            isinstance(c, str) and re.fullmatch(r"[A-Z_]{2,40}", c)
            for c in classes
        ):
            raise ValueError("Ungültige Klassenangaben.")
        result.append(CatalogAddon(name, title.strip(), repo, tuple(clients),
                                   tuple(classes), description))
    return tuple(result)


def load_catalog(path: Path | None = None) -> tuple[CatalogAddon, ...]:
    """Read-only catalog discovery. Does not touch WoW or initiate downloads."""
    catalog = BUILTIN_PATH if path is None else Path(path)
    if not catalog.is_file() or catalog.is_symlink():
        raise ValueError("Kein vertrauenswürdiger Katalog am angegebenen Pfad.")
    with catalog.open("rb") as stream:
        return parse_catalog(stream.read(MAX_CATALOG_BYTES + 1))


def catalog_ids(path: Path | None = None) -> tuple[str, ...]:
    return tuple(addon.id for addon in load_catalog(path))
