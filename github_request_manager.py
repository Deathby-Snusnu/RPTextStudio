"""Bounded, shared GitHub REST client for version checks and package staging.

Reads public repositories without credentials; uses optional GH_TOKEN/GITHUB_TOKEN.
One serialized request path, persistent bounded TTL/negative caching, conditional
requests, and fail-closed rate-limit cooldown shared by all callers.
"""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import tempfile
import threading
import time
import urllib.error
import urllib.request
from email.utils import parsedate_to_datetime
from datetime import datetime, timezone

MAX_BYTES = 2 * 1024 * 1024
CACHE_TTL = 30 * 60
NOT_FOUND_TTL = 60 * 60
MIN_GAP = 1.0
MAX_CACHE_RECORDS = 100
_LOCK = threading.RLock()
_NEXT_CALL = 0.0
_BLOCK_UNTIL = 0.0
_LAST_LIMIT = None
_LAST_REMAINING = None
_MEMORY = {}


class RequestGuardError(RuntimeError):
    pass


def _store_path():
    root = os.environ.get("LOCALAPPDATA")
    if root:
        return Path(root) / "RPTextStudio" / "github_api_cache.json"
    return Path.home() / ".cache" / "rptextstudio" / "github_api_cache.json"


def _identity(token):
    # A token is never persisted. Distinguish anonymous and authorized cache.
    return "authenticated:" + hashlib.sha256(token.encode()).hexdigest()[:16] if token else "anonymous"


def _load():
    global _MEMORY
    if _MEMORY:
        return
    try:
        raw = _store_path().read_bytes()
        if len(raw) <= MAX_BYTES:
            data = json.loads(raw)
            if isinstance(data, dict) and data.get("schema") == 1:
                _MEMORY = data.get("entries", {}) if isinstance(data.get("entries"), dict) else {}
    except (OSError, ValueError, TypeError):
        pass


def _save():
    try:
        destination = _store_path()
        destination.parent.mkdir(parents=True, exist_ok=True)
        items = sorted(_MEMORY.items(), key=lambda x: x[1].get("stored", 0), reverse=True)[:MAX_CACHE_RECORDS]
        payload = json.dumps({"schema": 1, "entries": dict(items)}, ensure_ascii=False).encode("utf-8")
        if len(payload) > MAX_BYTES:
            return
        fd, tmp = tempfile.mkstemp(dir=destination.parent, prefix=".github-", suffix=".tmp")
        try:
            with os.fdopen(fd, "wb") as stream:
                stream.write(payload)
            os.replace(tmp, destination)
        finally:
            if os.path.exists(tmp):
                os.unlink(tmp)
    except OSError:
        pass  # An unwritable cache must not break ordinary usage.


def _delay(headers, now):
    retry = headers.get("Retry-After")
    if retry:
        try:
            return now + max(60, min(float(retry), 3600))
        except (TypeError, ValueError):
            try:
                parsed = parsedate_to_datetime(retry)
                return now + max(60, min((parsed - datetime.now(timezone.utc)).total_seconds(), 3600))
            except (TypeError, ValueError, OverflowError):
                pass
    reset = headers.get("X-RateLimit-Reset")
    if reset:
        try:
            return max(now + 60, min(float(reset) + 5, now + 3600))
        except (TypeError, ValueError):
            pass
    return now + 120


def _headers(response):
    global _LAST_LIMIT, _LAST_REMAINING
    headers = response.headers
    try:
        _LAST_LIMIT = int(headers.get("X-RateLimit-Limit"))
        _LAST_REMAINING = int(headers.get("X-RateLimit-Remaining"))
    except (ValueError, TypeError):
        pass


def status():
    with _LOCK:
        _load()
        now = time.time()
        return {"remaining": _LAST_REMAINING, "limit": _LAST_LIMIT,
                "blocked_seconds": max(0, int(_BLOCK_UNTIL - now)),
                "cached": sum(1 for v in _MEMORY.values() if v.get("expires", 0) > now),
                "path": str(_store_path())}


def get_json(path):
    """Fetch one allowlisted GitHub REST path, without retry storms."""
    global _NEXT_CALL, _BLOCK_UNTIL
    if not path.startswith("/repos/Deathby-Snusnu/") or "://" in path or "\n" in path:
        raise RequestGuardError("Unzulässige GitHub-Adresse.")
    token = (os.environ.get("GH_TOKEN") or os.environ.get("GITHUB_TOKEN") or "").strip()
    key = _identity(token) + ":" + path
    with _LOCK:
        now = time.time()
        _load()
        cached = _MEMORY.get(key, {})
        if cached.get("expires", 0) > now:
            if cached.get("not_found"):
                raise RequestGuardError("Repository oder Release nicht öffentlich verfügbar (Cache).")
            return cached["value"]
        if now < _BLOCK_UNTIL:
            raise RequestGuardError("GitHub-API-Limit erreicht. Erneut in %d Sekunden versuchen." % int(_BLOCK_UNTIL-now+1))
        wait = max(0, _NEXT_CALL - time.monotonic())
        if wait:
            time.sleep(wait)
        _NEXT_CALL = time.monotonic() + MIN_GAP
        headers = {"Accept": "application/vnd.github+json",
                   "User-Agent": "RPTextStudio-GitHubGuard"}
        if token:
            headers["Authorization"] = "Bearer " + token
        if cached.get("etag"):
            headers["If-None-Match"] = cached["etag"]
        request = urllib.request.Request("https://api.github.com" + path, headers=headers)
        try:
            with urllib.request.urlopen(request, timeout=12) as response:
                _headers(response)
                data = response.read(MAX_BYTES + 1)
                if len(data) > MAX_BYTES:
                    raise RequestGuardError("GitHub-Antwort zu groß.")
                value = json.loads(data)
                _MEMORY[key] = {"value": value, "etag": response.headers.get("ETag"),
                                "stored": now, "expires": now + CACHE_TTL}
                _save()
                return value
        except urllib.error.HTTPError as exc:
            _headers(exc)
            if exc.code == 304 and "value" in cached:
                cached["expires"] = now + CACHE_TTL
                cached["stored"] = now
                _save()
                return cached["value"]
            remaining = exc.headers.get("X-RateLimit-Remaining")
            if exc.code in (403, 429):
                _BLOCK_UNTIL = _delay(exc.headers, now)
                raise RequestGuardError("GitHub-API-Limit erreicht; weitere Abfragen pausiert.") from exc
            if exc.code == 404:
                _MEMORY[key] = {"not_found": True, "stored": now, "expires": now + NOT_FOUND_TTL}
                _save()
                raise RequestGuardError("Repository oder Release nicht öffentlich verfügbar.") from exc
            if exc.code in (401, 403):
                raise RequestGuardError("GitHub-Zugriff verweigert oder API-Limit erreicht.") from exc
            raise RequestGuardError("GitHub-HTTP-Fehler: %s" % exc.code) from exc
        except (urllib.error.URLError, TimeoutError, OSError) as exc:
            raise RequestGuardError("GitHub-Zugriff fehlgeschlagen: %s" % exc) from exc
        except (ValueError, UnicodeError) as exc:
            raise RequestGuardError("Ungültige GitHub-Antwort.") from exc
