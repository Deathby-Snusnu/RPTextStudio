"""Generate source-identified metadata and the matching Inno preprocessor version."""
import argparse
import json
from pathlib import Path
import subprocess
from datetime import datetime, timezone
from app_build_info import APP_VERSION

ROOT = Path(__file__).resolve().parent


def prepare(root: Path = ROOT) -> dict:
    check = subprocess.run(["git", "status", "--porcelain", "--untracked-files=no", "--", ":/",
                            ":(exclude)build_info.json", ":(exclude)build_version.issinc"], cwd=root,
                           check=True, capture_output=True, text=True, timeout=15)
    # Generated metadata from a previous build may be tracked and dirty.
    # Only these two reproducible output files are exempted; source edits still abort.
    if check.stdout.strip():
        raise RuntimeError("Build abgebrochen: Git-Arbeitskopie enthält nicht committete Änderungen.")
    head = subprocess.run(["git", "rev-parse", "HEAD"], cwd=root, check=True,
                          capture_output=True, text=True, timeout=15).stdout.strip().lower()
    if len(head) != 40 or any(c not in "0123456789abcdef" for c in head):
        raise RuntimeError("Ungültige Git-Commit-ID.")
    metadata = {"version": APP_VERSION, "commit": head,
                "built_at_utc": datetime.now(timezone.utc).isoformat()}
    (root / "build_info.json").write_text(json.dumps(metadata, indent=2) + "\n", encoding="utf-8")
    (root / "build_version.issinc").write_text(f'#define AppVersion "{APP_VERSION}"\n', encoding="utf-8")
    return metadata


if __name__ == "__main__":
    print(prepare())
