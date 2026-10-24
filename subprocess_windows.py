"""Windows subprocess flags for GUI applications (also safe on Linux/macOS)."""
from __future__ import annotations
import os
import subprocess


def hidden_subprocess_kwargs() -> dict:
    """Prevent spawned console commands from flashing a terminal window."""
    if os.name != "nt":
        return {}
    startup = subprocess.STARTUPINFO()
    startup.dwFlags |= subprocess.STARTF_USESHOWWINDOW
    startup.wShowWindow = subprocess.SW_HIDE
    return {
        "startupinfo": startup,
        "creationflags": subprocess.CREATE_NO_WINDOW,
    }
