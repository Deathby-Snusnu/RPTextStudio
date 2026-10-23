"""Preview-first atomic generation of a new MagierRP project."""
from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path
import re
import shutil
import tempfile
from addon_project_templates import source_files
from addon_registry import discover, load_registry, register
from project_paths import project_root

VERSION = re.compile(r"^\d+(?:\.\d+){1,3}$")
LANGS = ("deDE", "enUS", "frFR")


@dataclass(frozen=True)
class AddonProjectSpec:
    addon_id: str = "MagierRP"
    title: str = "Magier RP"
    addon_type: str = "class"
    class_token: str = "MAGE"
    locales: tuple[str, ...] = LANGS
    version: str = "0.1.0"
    interface: int = 16001


@dataclass(frozen=True)
class GenerationPlan:
    addon_path: Path
    files_to_create: tuple[str, ...]
    registry_changes: tuple[str, ...]
    warnings: tuple[str, ...]


def _validate(root: Path, spec: AddonProjectSpec):
    if spec.addon_id != "MagierRP" or spec.class_token != "MAGE" or spec.addon_type != "class":
        raise ValueError("Diese erste Generatorvorlage unterstützt nur MagierRP / MAGE.")
    if not spec.title.strip() or "\n" in spec.title or "\r" in spec.title:
        raise ValueError("Ungültiger Projekttitel.")
    if len(set(spec.locales)) != len(spec.locales) or tuple(spec.locales) != LANGS:
        raise ValueError("MagierRP benötigt deDE, enUS und frFR.")
    if not VERSION.fullmatch(spec.version) or not isinstance(spec.interface, int) or not 10000 <= spec.interface <= 999999:
        raise ValueError("Ungültige Version oder Interface-Nummer.")
    root = project_root(Path(root))
    folder = root / "addons"
    if not folder.is_dir() or folder.is_symlink():
        raise ValueError("Bitte die bestehende RPAddOns-Projektwurzel mit addons/ öffnen.")
    path = folder / spec.addon_id
    if path.exists() or path.is_symlink():
        raise FileExistsError("MagierRP existiert bereits; nichts wird überschrieben.")
    if spec.addon_id in discover(root):
        raise FileExistsError("MagierRP ist bereits vorhanden.")
    registered = load_registry(root)
    if any(x["id"].casefold() == spec.addon_id.casefold() for x in registered["addons"]):
        raise ValueError("MagierRP ist bereits registriert.")
    return root, path


def _entry(spec: AddonProjectSpec) -> dict:
    return {"id": spec.addon_id, "title": spec.title, "type": spec.addon_type,
            "class_token": spec.class_token, "toc": spec.addon_id + ".toc",
            "version": spec.version, "locales": list(spec.locales),
            "repository": None, "enabled": True}


def preview_project(root: Path, spec: AddonProjectSpec) -> GenerationPlan:
    _, path = _validate(root, spec)
    files = source_files(spec.addon_id, spec.title, spec.locales, spec.version, spec.interface)
    return GenerationPlan(path, tuple(sorted(files)), ("addons.json: MagierRP hinzufügen",),
                          ("GitHub-Repository wird nicht automatisch angelegt.",))


def generate_project(root: Path, spec: AddonProjectSpec, approved_plan: GenerationPlan) -> Path:
    plan = preview_project(root, spec)
    if plan != approved_plan:
        raise ValueError("Die Vorschau ist veraltet und muss erneuert werden.")
    root = project_root(Path(root))
    files = source_files(spec.addon_id, spec.title, spec.locales, spec.version, spec.interface)
    stage = Path(tempfile.mkdtemp(prefix=".magierrp-stage-", dir=root / "addons"))
    dest = plan.addon_path
    created = False
    try:
        for rel, content in files.items():
            target = stage / rel
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(content, encoding="utf-8")
        # Verify every TOC reference resolves to an actual generated file.
        toc = files[spec.addon_id + ".toc"]
        for line in toc.splitlines():
            if line and not line.startswith("#"):
                relative = line.replace("\\", "/")
                if relative not in files:
                    raise ValueError("TOC verweist auf fehlende Datei: " + relative)
        if dest.exists() or dest.is_symlink():
            raise FileExistsError("Zielverzeichnis wurde inzwischen erstellt.")
        stage.rename(dest)
        created = True
        register(root, _entry(spec))
        return dest
    except Exception:
        if created:
            shutil.rmtree(dest)
        raise
    finally:
        if stage.exists():
            shutil.rmtree(stage)
