"""Read-only GitHub version checks for RP Text Studio.

A newer repository commit does not imply a released update. Private repositories
are accessed via GitHub CLI (gh auth login) or GITHUB_TOKEN / GH_TOKEN.
No package downloads or installation are performed in this module.
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import base64
import json
import os
import re
import subprocess
import urllib.error
import urllib.parse
import urllib.request

from addon_manager import ADDONS
from addon_registry import discover, load_registry

OWNER = "Deathby-Snusnu"
VERSION_RE = re.compile(r"^\s*##\s*Version\s*:\s*(.*?)\s*$", re.I | re.M)
INTERFACE_RE = re.compile(r"^\s*##\s*Interface\s*:\s*(.*?)\s*$", re.I | re.M)
NUMERIC_VERSION = re.compile(r"^\d+(?:\.\d+)*$")
MAX_RESPONSE = 2 * 1024 * 1024


@dataclass(frozen=True)
class VersionCheck:
    name: str
    installed: str | None
    available: str | None
    source: str
    status: str
    detail: str
    release_url: str | None = None
    commit_sha: str | None = None


class GitHubCheckError(RuntimeError):
    pass


def parse_toc(text: str) -> tuple[str | None, str | None]:
    version = VERSION_RE.search(text)
    interface = INTERFACE_RE.search(text)
    return (version.group(1).strip() if version else None,
            interface.group(1).strip() if interface else None)


def compare_versions(installed: str, available: str) -> int | None:
    """Return -1 for newer available, 0 for equal, 1 for older available."""
    if not NUMERIC_VERSION.fullmatch(installed) or not NUMERIC_VERSION.fullmatch(available):
        return None
    a = tuple(map(int, installed.split(".")))
    b = tuple(map(int, available.split(".")))
    width = max(len(a), len(b))
    a += (0,) * (width - len(a))
    b += (0,) * (width - len(b))
    return (a > b) - (a < b)


def _api(path: str) -> object:
    if not path.startswith("/repos/" + OWNER + "/"):
        raise GitHubCheckError("Unzulässige GitHub-Adresse.")
    endpoint = "https://api.github.com" + path
    token = os.environ.get("GH_TOKEN") or os.environ.get("GITHUB_TOKEN")
    if token:
        request = urllib.request.Request(endpoint, headers={
            "Authorization": "Bearer " + token,
            "Accept": "application/vnd.github+json",
            "User-Agent": "RPTextStudio-UpdateChecker",
        })
        try:
            with urllib.request.urlopen(request, timeout=12) as response:
                data = response.read(MAX_RESPONSE + 1)
        except (urllib.error.URLError, TimeoutError) as exc:
            raise GitHubCheckError(f"GitHub-Zugriff fehlgeschlagen: {exc}") from exc
        if len(data) > MAX_RESPONSE:
            raise GitHubCheckError("GitHub-Antwort zu groß.")
    else:
        # 'gh api' uses Windows GitHub CLI credential management for private repos.
        try:
            result = subprocess.run(["gh", "api", path, "-H",
                "Accept: application/vnd.github+json"], capture_output=True,
                text=True, timeout=15, check=False)
        except (OSError, subprocess.TimeoutExpired) as exc:
            raise GitHubCheckError("GitHub CLI fehlt oder antwortet nicht. "
                                   "Bitte 'gh auth login' ausführen oder GH_TOKEN setzen.") from exc
        if result.returncode:
            raise GitHubCheckError("GitHub-Zugriff fehlgeschlagen (Anmeldung/Rechte/Netzwerk prüfen).")
        data = result.stdout.encode("utf-8")
        if len(data) > MAX_RESPONSE:
            raise GitHubCheckError("GitHub-Antwort zu groß.")
    try:
        return json.loads(data)
    except (ValueError, UnicodeDecodeError) as exc:
        raise GitHubCheckError("Ungültige GitHub-Antwort.") from exc


def _release(name: str) -> tuple[str | None, str | None]:
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
    return version, url


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
        if name not in ADDONS:
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
    return name if name in ADDONS else None


def check_addon(name: str, target: Path, channel: str = "stable", *, project: Path | None = None) -> VersionCheck:
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
                available, url = _release(repo_name)
            except GitHubCheckError as exc:
                # 404 on releases/latest is expected for repos with no releases.
                return VersionCheck(name, local_version, None, channel,
                                    "Kein Release / nicht verfügbar", str(exc))
            remote_interface, sha = None, None
        else:
            available, remote_interface, sha = _development(repo_name)
            url = None
    except GitHubCheckError as exc:
        return VersionCheck(name, local_version, None, channel, "Nicht prüfbar", str(exc))
    if not available:
        status, detail = "Nicht prüfbar", "GitHub-Version fehlt."
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


def check_all(target: Path, names=ADDONS, channel="stable", *, project: Path | None = None) -> tuple[VersionCheck, ...]:
    return tuple(check_addon(name, target, channel, project=project) for name in names)
