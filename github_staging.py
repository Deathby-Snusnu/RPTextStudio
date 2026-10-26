"""Authenticated, bounded GitHub archive staging. Never modifies WoW installations.

The chosen GitHub ref is resolved to a commit before downloading. The resulting
ZIP is checked for path traversal, links, duplicate paths, oversized content and
missing TOC references. Only runtime files are staged.
"""
from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
from pathlib import Path, PurePosixPath
from urllib.request import Request, build_opener, HTTPRedirectHandler
from urllib.error import URLError
import json
import os
import re
import shutil
import stat
import subprocess
import tempfile
import zipfile

from addon_manager import known_addons, RUNTIME_SUFFIXES, SKIP_DIRS
from github_updates import OWNER, _api, parse_toc
from subprocess_windows import hidden_subprocess_kwargs

MAX_ARCHIVE = 64 * 1024 * 1024
MAX_UNPACKED = 256 * 1024 * 1024
MAX_FILES = 10000
SHA = re.compile(r"^[a-f0-9]{40}$")
VERSION = re.compile(r"^\d+(?:\.\d+){1,3}$")


class DownloadError(RuntimeError):
    pass


@dataclass(frozen=True)
class StagedAddon:
    name: str
    channel: str
    version: str
    interface: str
    commit: str
    files: int
    archive_sha256: str
    directory: Path


def _token() -> str:
    token = os.environ.get("GH_TOKEN") or os.environ.get("GITHUB_TOKEN")
    if token:
        return token.strip()
    try:
        result = subprocess.run(["gh", "auth", "token", "--hostname", "github.com"],
                                capture_output=True, text=True, timeout=15, check=False,
                                **hidden_subprocess_kwargs())
    except (OSError, subprocess.TimeoutExpired) as exc:
        raise DownloadError("GitHub CLI / Anmeldung nicht verfügbar.") from exc
    if result.returncode or not result.stdout.strip():
        raise DownloadError("Bitte zuerst 'gh auth login' ausführen.")
    return result.stdout.strip()


class _GitHubRedirect(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        redirected = super().redirect_request(req, fp, code, msg, headers, newurl)
        if redirected is None:
            return None
        # Never forward authentication to a host outside github.com and its archive CDN.
        from urllib.parse import urlsplit
        host = urlsplit(newurl).hostname
        if urlsplit(newurl).scheme != "https" or host not in ("api.github.com", "codeload.github.com"):
            raise DownloadError("Unzulässige GitHub-Weiterleitung.")
        if host != "api.github.com":
            redirected.remove_header("Authorization")
        return redirected


def _download(commit: str, name: str, output: Path) -> str:
    if not SHA.fullmatch(commit):
        raise DownloadError("Ungültiger Commit-SHA.")
    url = f"https://api.github.com/repos/{OWNER}/{name}/zipball/{commit}"
    request = Request(url, headers={
        "Authorization": "Bearer " + _token(),
        "Accept": "application/vnd.github+json",
        "User-Agent": "RPTextStudio-Staging",
    })
    h = sha256()
    size = 0
    try:
        with build_opener(_GitHubRedirect()).open(request, timeout=30) as response, output.open("wb") as stream:
            while True:
                chunk = response.read(1024 * 1024)
                if not chunk:
                    break
                size += len(chunk)
                if size > MAX_ARCHIVE:
                    raise DownloadError("GitHub-Paket überschreitet 64 MiB.")
                h.update(chunk)
                stream.write(chunk)
    except (URLError, TimeoutError, OSError) as exc:
        raise DownloadError(f"Archivabruf fehlgeschlagen: {exc}") from exc
    return h.hexdigest()


def _resolve(name: str, channel: str) -> tuple[str, str]:
    if name not in known_addons():
        raise DownloadError("Repository steht nicht auf der geprüften RP-AddOn-Liste.")
    if channel == "stable":
        release = _api(f"/repos/{OWNER}/{name}/releases/latest")
        if not isinstance(release, dict) or release.get("draft") or release.get("prerelease"):
            raise DownloadError("Kein stabiler Release vorhanden.")
        version = str(release.get("tag_name", "")).removeprefix("v")
        ref = str(release.get("tag_name", ""))
        if not VERSION.fullmatch(version):
            raise DownloadError("Release-Version ist ungültig.")
    elif channel == "development":
        repo = _api(f"/repos/{OWNER}/{name}")
        if not isinstance(repo, dict):
            raise DownloadError("Repository konnte nicht geprüft werden.")
        ref = repo.get("default_branch")
        if not isinstance(ref, str) or not re.fullmatch(r"[A-Za-z0-9._/-]{1,120}", ref):
            raise DownloadError("Ungültiger Git-Branch.")
        version = ""
    else:
        raise DownloadError("Unbekannter Update-Kanal.")
    from urllib.parse import quote
    commit_data = _api(f"/repos/{OWNER}/{name}/commits/{quote(ref, safe='')}")
    commit = commit_data.get("sha") if isinstance(commit_data, dict) else None
    if not isinstance(commit, str) or not SHA.fullmatch(commit):
        raise DownloadError("GitHub-Commit konnte nicht verifiziert werden.")
    return commit, version


def _validate_zip(archive: Path, name: str) -> tuple[dict[str, zipfile.ZipInfo], str, str]:
    selected: dict[str, zipfile.ZipInfo] = {}
    seen: set[str] = set()
    total = 0
    root_name = None
    with zipfile.ZipFile(archive) as zipfile_obj:
        for info in zipfile_obj.infolist():
            parts = PurePosixPath(info.filename).parts
            if not parts or any(p in ("", ".", "..") for p in parts) or "\\" in info.filename:
                raise DownloadError("Ungültiger Archivpfad.")
            if root_name is None:
                root_name = parts[0]
            if (parts[0] != root_name or info.filename.startswith("/")
                    or any(":" in part for part in parts)):
                raise DownloadError("Mehrere Archivwurzeln oder absoluter Pfad.")
            mode = (info.external_attr >> 16) & 0xFFFF
            if stat.S_ISLNK(mode):
                raise DownloadError("Symbolische Links sind nicht zulässig.")
            if info.is_dir():
                continue
            if mode and stat.S_IFMT(mode) not in (0, stat.S_IFREG):
                raise DownloadError("Nicht reguläre Archivdatei.")
            relative = parts[1:]
            if not relative:
                continue
            key = "/".join(relative)
            canonical = key.casefold()
            if canonical in seen:
                raise DownloadError("Doppelte oder uneindeutige Archivdatei.")
            seen.add(canonical)
            if any(p.lower() in SKIP_DIRS for p in relative[:-1]):
                continue
            if Path(key).suffix.lower() not in RUNTIME_SUFFIXES:
                continue
            total += info.file_size
            if len(selected) >= MAX_FILES or total > MAX_UNPACKED or info.file_size > MAX_UNPACKED:
                raise DownloadError("Entpackte Dateien überschreiten Sicherheitslimits.")
            selected[key] = info
        toc_key = name + ".toc"
        if toc_key not in selected:
            raise DownloadError("Gleichnamige TOC fehlt im Repository-Archiv.")
        raw_toc = zipfile_obj.read(selected[toc_key]).decode("utf-8-sig")
    version, interface = parse_toc(raw_toc)
    if not version or not VERSION.fullmatch(version) or not interface:
        raise DownloadError("TOC-Version oder Interface fehlt.")
    toc_entries = [line.strip().replace("\\", "/") for line in raw_toc.splitlines()
                   if line.strip() and not line.lstrip().startswith("#")]
    for entry in toc_entries:
        if entry not in selected:
            raise DownloadError(f"TOC verweist auf fehlende Runtime-Datei: {entry}")
    return selected, version, interface


def stage(name: str, channel: str, destination: Path) -> StagedAddon:
    """Stage new addon under an existing user-chosen empty directory.

    Nothing is installed. Stage may be discarded simply by deleting its output
    directory. Caller must not choose any WoW Interface/AddOns directory.
    """
    dest = Path(destination).absolute()
    if dest.exists() or dest.is_symlink():
        raise DownloadError("Ziel existiert bereits; Staging darf nichts überschreiben.")
    from wow_detection import CLIENT_DIRS
    if any(
        (p.name.casefold() == "addons" and p.parent.name.casefold() == "interface")
        or (p.name.casefold() == "interface"
            and p.parent.name.casefold() in (*CLIENT_DIRS, "_classic_ptr_"))
        for p in (dest, *dest.parents)
    ):
        raise DownloadError("Staging im WoW-Interface-Verzeichnis ist verboten.")
    from addon_manager import _linked
    if not dest.parent.is_dir() or any(_linked(p) for p in (dest.parent, *dest.parent.parents)):
        raise DownloadError("Ungültiges oder verknüpftes Staging-Ziel.")
    commit, release_version = _resolve(name, channel)
    with tempfile.TemporaryDirectory(prefix=".rpstudio-download-", dir=dest.parent) as temporary:
        archive = Path(temporary) / "download.zip"
        digest = _download(commit, name, archive)
        entries, version, interface = _validate_zip(archive, name)
        if release_version and version != release_version:
            raise DownloadError("Release-Tag und TOC-Version stimmen nicht überein.")
        out = Path(temporary) / "payload"
        out.mkdir()
        with zipfile.ZipFile(archive) as z:
            for rel, info in entries.items():
                path = out / rel
                path.parent.mkdir(parents=True, exist_ok=True)
                with z.open(info) as src, path.open("wb") as dst:
                    copied = 0
                    while True:
                        chunk = src.read(1024 * 1024)
                        if not chunk:
                            break
                        copied += len(chunk)
                        if copied > info.file_size or copied > MAX_UNPACKED:
                            raise DownloadError("Unzulässige Archivgröße beim Entpacken.")
                        dst.write(chunk)
                    if copied != info.file_size:
                        raise DownloadError("Archivinhalt ist unvollständig.")
        if dest.exists() or dest.is_symlink():
            raise DownloadError("Staging-Ziel wurde inzwischen erstellt.")
        out.rename(dest)
    return StagedAddon(name, channel, version, interface, commit, len(entries), digest, dest)
