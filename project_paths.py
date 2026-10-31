"""Resolve collection, unpacked runtime and legacy editor project layouts."""
from pathlib import Path


def project_root(root: Path) -> Path:
    """Resolve a collection root from its addons directory, when applicable."""
    root = root.resolve()
    if root.name.lower() == "addons" and (root.parent / "apps").is_dir():
        return root.parent
    return root


def addons_root(root: Path) -> Path:
    """Return a nested addons directory if present, otherwise the project root."""
    root = project_root(root)
    nested = root / "addons"
    return nested if nested.is_dir() else root


def metadata_path(root: Path, filename: str, *, write: bool = False) -> Path:
    """Resolve project metadata under data, with a legacy-root read fallback.

    For writes, create the data directory and always return its target path.
    For reads, return the legacy root file only if no data file exists.
    """
    root = project_root(root)
    target = root / "data" / filename
    if write:
        target.parent.mkdir(parents=True, exist_ok=True)
    elif not target.exists() and (root / filename).is_file():
        return root / filename
    return target


def manual_path() -> Path:
    """Return a bundled manual or the expected shared manual path.

    The shared path is returned even if the manual does not exist.
    """
    app = Path(__file__).resolve().parent
    bundled = app / "HANDBUCH.md"
    if bundled.is_file():
        return bundled
    return app.parent.parent / "docs" / "RPTextStudio" / "HANDBUCH.md"
