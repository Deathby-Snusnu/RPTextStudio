"""Read-only GitHub version checks for RP Text Studio.

A newer repository commit does not imply a released update. Public repositories
can be queried without a token; private access uses GH_TOKEN or GITHUB_TOKEN.
The shared REST client does not use GitHub CLI authentication. No package
downloads or installation are performed in this module, but API responses
can be stored in the user's local cache.
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import base64
import json
import os
import re
import subprocess
from subprocess_windows import hidden_subprocess_kwargs
import urllib.error
import urllib.parse
import urllib.request

from addon_manager import known_addons
from addon_registry import discover, load_registry

OWNER = "Deathby-Snusnu"
VERSION_RE = re.compile(r"^\s*##\s*Version\s*:\s*(.*?)\s*$", re.I | re.M)
INTERFACE_RE = re.compile(r"^\s*##\s*Interface\s*:\s*(.*?)\s*$", re.I | re.M)
NUMERIC_VERSION = re.compile(r"^\d+(?:\.\d+)*$")
MAX_RESPONSE = 2 * 1024 * 1024


@dataclass(frozen=True)
class VersionCheck:
    """Describe a comparison; development commit_sha may be a TOC blob SHA."""

    name: str
    installed: str | None
    available: str | None
    source: str
    status: str
    detail: str
    release_url: str | None = None
    commit_sha: str | None = None


class GitHubCheckError(RuntimeError):
    """Report a guarded GitHub request or response failure."""

    pass


def parse_toc(text: str) -> tuple[str | None, str | None]:
    """Return the first TOC version and interface values, if present."""
    version = VERSION_RE.search(text)
    interface = INTERFACE_RE.search(text)
    return (version.group(1).strip() if version else None,
            interface.group(1).strip() if interface else None)


def compare_versions(installed: str, available: str) -> int | None:
    """Compare numeric versions; return None if either version is unsupported.

    Returns -1 for newer available, 0 for equal, and 1 for older available.
    """
    if not NUMERIC_VERSION.fullmatch(installed) or not NUMERIC_VERSION.fullmatch(available):
        return None
    a = tuple(map(int, installed.split(".")))
    b = tuple(map(int, available.split(".")))
    width = max(len(a), len(b))
    a += (0,) * (width - len(a))
    b += (0,) * (width - len(b))
    return (a > b) - (a < b)


def _api(path: str) -> object:
    """Shared guarded REST access used by version checks and staging."""
    from github_request_manager import get_json, RequestGuardError
    try:
        return get_json(path)
    except RequestGuardError as exc:
        raise GitHubCheckError(str(exc)) from exc


def _release(name: str) -> tuple[str, str | None, str]:
    data = _api(f"/repos/{OWNER}/{name}/releases/latest")
    if not isinstance(data, dict) or data.get("draft") or data.get("prerelease"):
        raise GitHubCheckError("Kein gültiger stabiler Release.")
    tag = data.get("tag_name", "")
    version = str(tag).removeprefix("v")
    if not NUMERIC_VERSION.fullmatch(version):
        raise GitHubCheckError("Release-Tag ist keine numerische Version.")
    url = data.get("html_url")
    if not isinstance(url, str) or not url.startswith(f"https://github.com/{OWNER}/{name}/releases/"):
        url = None
    return version, url, str(tag)


def _release_interface(name: str, tag: str) -> str | None:
    path = urllib.parse.quote(f"{name}.toc", safe="")
    ref = urllib.parse.quote(tag, safe="")
    toc = _api(f"/repos/{OWNER}/{name}/contents/{path}?ref={ref}")
    if not isinstance(toc, dict) or toc.get("encoding") != "base64":
        raise GitHubCheckError("TOC-Inhalt konnte nicht gelesen werden.")
    try:
        raw = base64.b64decode(toc["content"], validate=False).decode("utf-8-sig")
    except (KeyError, ValueError, UnicodeError) as exc:
        raise GitHubCheckError("Ungültige TOC-Daten.") from exc
    _, interface = parse_toc(raw)
    return interface


def _development(name: str) -> tuple[str | None, str | None, str | None]:
    repo = _api(f"/repos/{OWNER}/{name}")
    if not isinstance(repo, dict):
        raise GitHubCheckError("Ungültige Repository-Antwort.")
    branch = repo.get("default_branch")
    if not isinstance(branch, str) or not re.fullmatch(r"[\w./-]{1,128}", branch):
        raise GitHubCheckError("Ungültiger Hauptbranch.")
    path = urllib.parse.quote(f"{name}.toc", safe="")
    ref = urllib.parse.quote(branch, safe="")
    toc = _api(f"/repos/{OWNER}/{name}/contents/{path}?ref={ref}")
    if not isinstance(toc, dict) or toc.get("encoding") != "base64":
        raise GitHubCheckError("TOC-Inhalt konnte nicht gelesen werden.")
    try:
        raw = base64.b64decode(toc["content"], validate=False).decode("utf-8-sig")
    except (KeyError, ValueError, UnicodeError) as exc:
        raise GitHubCheckError("Ungültige TOC-Daten.") from exc
    version, interface = parse_toc(raw)
    sha = toc.get("sha")  # file blob SHA; not a repository commit
    return version, interface, sha if isinstance(sha, str) else None


def _resolve_repository(name: str, project: Path | None) -> str | None:
    if project is None:
        if name not in known_addons():
            raise ValueError("Unbekanntes AddOn ohne Projektregister.")
        return name
    projects = discover(project)
    if name not in projects:
        raise ValueError("Nicht bekanntes lokales AddOn.")
    for item in load_registry(project)["addons"]:
        if item["id"] == name:
            repository = item.get("repository")
            if repository is None:
                return None
            if repository != f"{OWNER}/{name}":
                raise ValueError("GitHub-Zuordnung ist nicht für diese Quelle freigegeben.")
            return name
    # Legacy six projects retain their historical allowlisted mapping.
    return name if name in known_addons() else None


def check_addon(name: str, target: Path, channel: str = "stable", *, project: Path | None = None) -> VersionCheck:
    """Compare local TOC metadata with a release or development version.

    ``target`` contains addon directories. If ``project`` is supplied, its
    registry controls repository association; otherwise the catalog is used.
    An unassociated addon is reported without a GitHub query. Invalid channels
    or repository associations raise ValueError; request failures are
    represented in the returned status.
    """
    if channel not in ("stable", "development"):
        raise ValueError("Ungültiger Update-Kanal.")
    repo_name = _resolve_repository(name, project)
    path = Path(target) / name / f"{name}.toc"
    try:
        local_version, local_interface = parse_toc(path.read_text(encoding="utf-8-sig"))
    except FileNotFoundError:
        local_version = local_interface = None
    except (OSError, UnicodeError) as exc:
        return VersionCheck(name, None, None, channel, "Fehler", str(exc))
    if repo_name is None:
        return VersionCheck(name, local_version, None, channel, "Nicht zugeordnet",
                            "Kein bestätigtes GitHub-Repository registriert.")
    try:
        if channel == "stable":
            try:
                available, url, tag = _release(repo_name)
            except GitHubCheckError as exc:
                # 404 on releases/latest is expected for repos with no releases.
                return VersionCheck(name, local_version, None, channel,
                                    "Kein Release / nicht verfügbar", str(exc))
            try:
                remote_interface = _release_interface(repo_name, tag)
            except GitHubCheckError as exc:
                return VersionCheck(name, local_version, None, channel, "Nicht prüfbar", str(exc))
            sha = None
        else:
            available, remote_interface, sha = _development(repo_name)
            url = None
    except GitHubCheckError as exc:
        return VersionCheck(name, local_version, None, channel, "Nicht prüfbar", str(exc))
    if not available:
        status, detail = "Nicht prüfbar", "GitHub-Version fehlt."
    elif local_version is None and path.is_file():
        status, detail = "Nicht prüfbar", "Lokale TOC-Datei enthält keine Versionsnummer."
    elif local_version is None:
        status, detail = "Nicht installiert", "Lokale TOC-Datei fehlt."
    elif remote_interface and local_interface and remote_interface != local_interface:
        status, detail = "Kompatibilität prüfen", f"Interface {local_interface} vs. {remote_interface}."
    else:
        cmp = compare_versions(local_version, available)
        status = {-1: "Neuer Quellstand", 0: "Versionsgleich", 1: "Lokal neuer", None: "Unvergleichbar"}[cmp]
        detail = ("Nur Versionsnummern geprüft; Dateiintegrität und Installierbarkeit "
                  "sind nicht bestätigt.")
    return VersionCheck(name, local_version, available, channel, status, detail, url, sha)


def check_all(target: Path, names=None, channel="stable", *, project: Path | None = None) -> tuple[VersionCheck, ...]:
    """Compare selected addon IDs, or all catalog IDs when names is None."""
    if names is None:
        names = known_addons()
    return tuple(check_addon(name, target, channel, project=project) for name in names)
