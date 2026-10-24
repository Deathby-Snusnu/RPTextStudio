"""Read-only three-way Lua RP text merge report.

Usage:
  python preview_rp_text_merge.py BASELINE.lua LOCAL.lua NEW_REPO.lua

This command does not modify any files.
"""
from __future__ import annotations
import argparse
from pathlib import Path
from rp_text_merge import preview_text_merge


def main() -> int:
    parser = argparse.ArgumentParser(description="Vorschau: Neue Repo-RP-Texte integrieren")
    parser.add_argument("baseline", type=Path, help="Original-Textdatei der vorherigen Repo-Version")
    parser.add_argument("local", type=Path, help="Lokal angepasste Textdatei")
    parser.add_argument("upstream", type=Path, help="Neue Textdatei aus dem Repository")
    args = parser.parse_args()
    baseline = args.baseline.read_text(encoding="utf-8-sig")
    local = args.local.read_text(encoding="utf-8-sig")
    upstream = args.upstream.read_text(encoding="utf-8-sig")
    preview = preview_text_merge(baseline, local, upstream)
    for pool in preview.pools:
        if pool.status == "Unverändert":
            continue
        print(f"[{pool.status}] {' / '.join(pool.path)}: {pool.reason}")
        for text in pool.additions:
            print(f"  + {text}")
    print(f"\n{preview.additions} neue Texte; {preview.conflicts} ungeklärte Listen.")
    print("Nur Vorschau: Es wurden keine Dateien verändert.")
    return 2 if preview.conflicts else 0


if __name__ == "__main__":
    raise SystemExit(main())
