"""Read the declared app version and bundled build identity."""
from __future__ import annotations
import json
from pathlib import Path
import sys

APP_VERSION = "1.0.0"
INFO_FILE = Path(__file__).with_name("build_info.json")


def build_identity() -> str:
    """Return a bundled commit prefix or 'Quellcode' when unavailable."""
    if not getattr(sys, "frozen", False):
        return "Quellcode"
    try:
        info = json.loads(INFO_FILE.read_text(encoding="utf-8"))
        if info.get("version") != APP_VERSION:
            return "Quellcode"
        commit = info.get("commit")
        if isinstance(commit, str) and len(commit) == 40 and all(c in "0123456789abcdef" for c in commit):
            return commit[:12]
    except (OSError, ValueError, TypeError):
        pass
    return "Quellcode"


def window_title() -> str:
    """Format the declared version and available build identity for a title."""
    identity = build_identity()
    return f"RP Text Studio {APP_VERSION}" + (f" · {identity}" if identity != "Quellcode" else " · Quellcode")
