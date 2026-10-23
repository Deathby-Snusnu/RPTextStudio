"""Resolve collection, unpacked runtime and legacy editor project layouts."""
from pathlib import Path


def project_root(root: Path) -> Path:
    root = root.resolve()
    if root.name.lower() == "addons" and (root.parent / "apps").is_dir():
        return root.parent
    return root


def addons_root(root: Path) -> Path:
    root = project_root(root)
    nested = root / "addons"
    return nested if nested.is_dir() else root


def metadata_path(root: Path, filename: str, *, write: bool = False) -> Path:
    root = project_root(root)
    target = root / "data" / filename
    if write:
        target.parent.mkdir(parents=True, exist_ok=True)
    elif not target.exists() and (root / filename).is_file():
        return root / filename
    return target


def manual_path() -> Path:
    app = Path(__file__).resolve().parent
    bundled = app / "HANDBUCH.md"
    if bundled.is_file():
        return bundled
    return app.parent.parent / "docs" / "RPTextStudio" / "HANDBUCH.md"
