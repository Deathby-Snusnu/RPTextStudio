"""Per-installation WoW interface profiles and safe, preview-only TOC adaptation."""
from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path
import json
import os
import re
from wow_detection import inspect_client
from wow_installations import settings_path

INTERFACE_RE = re.compile(r"^(\s*##\s*Interface\s*:\s*)([^\r\n]*)(\r?\n|$)", re.I | re.M)
VALID_INTERFACE = re.compile(r"^[1-9][0-9]{3,6}$")
# Verified compatibility remains opt-in. These are not compatibility claims for other clients.
TESTED_COMPATIBILITY = {name: {"forever"} for name in (
    "JaegerRP", "DruidenRP", "HexerRP", "PaladinRP", "RPChatMod", "RPControlCenter"
)}


@dataclass(frozen=True)
class ClientProfile:
    client_root: Path
    client_type: str
    interface: str
    source: str


def profile_path() -> Path:
    return settings_path().with_name("client_profiles.json")


def _key(path: Path) -> str:
    return os.path.normcase(str(Path(path).absolute())).casefold()


def _load(path: Path) -> dict:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        if data.get("schema") == 1 and isinstance(data.get("profiles"), dict):
            return data["profiles"]
    except (OSError, ValueError, TypeError, AttributeError):
        pass
    return {}


def get_profile(root: Path, path: Path | None = None) -> ClientProfile | None:
    detected = inspect_client(root, "profile")
    if detected is None:
        return None
    raw = _load(path or profile_path()).get(_key(detected.client_root))
    if not isinstance(raw, dict) or not VALID_INTERFACE.fullmatch(str(raw.get("interface", ""))):
        return None
    return ClientProfile(detected.client_root, detected.client_type,
                         str(raw["interface"]), str(raw.get("source", "manual")))


def save_profile(root: Path, interface: str, path: Path | None = None) -> ClientProfile:
    detected = inspect_client(root, "profile")
    if detected is None or not detected.verified:
        raise ValueError("Nur bestätigte WoW-Installationen erlauben ein Interface-Profil.")
    if not VALID_INTERFACE.fullmatch(str(interface)):
        raise ValueError("Interface muss eine vier- bis siebenstellige positive Nummer sein.")
    file = path or profile_path()
    profiles = _load(file)
    profiles[_key(detected.client_root)] = {"interface": str(interface), "source": "manual"}
    file.parent.mkdir(parents=True, exist_ok=True)
    tmp = file.with_suffix(".tmp")
    tmp.write_text(json.dumps({"schema": 1, "profiles": profiles}, indent=2), encoding="utf-8")
    tmp.replace(file)
    return ClientProfile(detected.client_root, detected.client_type, str(interface), "manual")


def compatibility(addon: str, profile: ClientProfile) -> str:
    if profile.client_type == "custom":
        return "Manuell prüfen: Custom-Client, nicht automatisch als Forever bestätigt"
    if profile.client_type not in TESTED_COMPATIBILITY.get(addon, set()):
        return "Nicht als kompatibel bestätigt"
    return "Kompatibilität deklariert"


def preview_toc(toc: str, interface: str, *, compatible: bool = False) -> str:
    """Return adapted content without writing; compatibility must be explicitly approved."""
    if not compatible:
        raise ValueError("Keine bestätigte Kompatibilität; TOC wird nicht angepasst.")
    if not VALID_INTERFACE.fullmatch(str(interface)):
        raise ValueError("Ungültige Interface-Nummer.")
    matches = list(INTERFACE_RE.finditer(toc))
    if len(matches) != 1:
        raise ValueError("TOC muss genau eine Interface-Zeile enthalten.")
    match = matches[0]
    return toc[:match.start(2)] + str(interface) + toc[match.end(2):]
