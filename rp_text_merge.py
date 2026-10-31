"""Conservative three-way RP text-list merge preview.

No Lua execution, no disk writes. Uses the existing literal-list parser.
A prior upstream baseline is required to distinguish genuinely new upstream
texts from locally rewritten upstream texts.
"""
from __future__ import annotations
from dataclasses import dataclass
from lua_text import parse_pools, ParseError

@dataclass(frozen=True)
class PoolMerge:
    """Describe one local pool, proposed additions, and any conflict."""

    path: tuple[str, ...]
    status: str
    local: tuple[str, ...]
    additions: tuple[str, ...]
    result: tuple[str, ...]
    reason: str

@dataclass(frozen=True)
class MergePreview:
    """Collect pool-level results and safe proposed updates without writing."""

    pools: tuple[PoolMerge, ...]
    safe_updates: dict[tuple[str, ...], list[str]]

    @property
    def conflicts(self) -> int:
        """Return the number of pools requiring manual review."""
        return sum(p.status == "Konflikt" for p in self.pools)

    @property
    def additions(self) -> int:
        """Return the number of proposed new text entries."""
        return sum(len(p.additions) for p in self.pools)


def preview_text_merge(baseline_lua: str, local_lua: str, upstream_lua: str) -> MergePreview:
    """Merge only literal leaf pools already present locally.

    Known old upstream strings edited/deleted locally never reappear merely
    because upstream still has them. Newly added upstream strings are appended
    in upstream order. New or structurally changed keys must be reviewed manually.
    """
    rejected = set()
    old = parse_pools(baseline_lua, rejected_paths=rejected)
    local = parse_pools(local_lua, rejected_paths=rejected)
    new = parse_pools(upstream_lua, rejected_paths=rejected)
    previews = []
    updates = {}
    for key in sorted(set(old) | set(local) | set(new) | rejected):
        before = old.get(key)
        current = local.get(key)
        incoming = new.get(key)
        if key in rejected:
            existing = tuple(current.entries) if current else ()
            previews.append(PoolMerge(key, "Konflikt", existing, (), existing,
                "Textliste enthält nichtliterale Lua-Ausdrücke und muss manuell geprüft werden."))
            continue
        if not current:
            previews.append(PoolMerge(key, "Konflikt", (),
                (), (), "Textliste fehlt lokal oder ist nicht als reine Textliste lesbar."))
            continue
        existing = tuple(current.entries)
        if not before or not incoming:
            previews.append(PoolMerge(key, "Konflikt", existing, (), existing,
                "Kein gemeinsamer Ausgangsstand oder Liste im Repository entfernt."))
            continue
        old_set = set(before.entries)
        local_set = set(existing)
        # A string is new only if it was not present in the previous upstream version.
        additions = tuple(dict.fromkeys(s for s in incoming.entries
                                         if s not in old_set and s not in local_set))
        merged = existing + additions
        status = "Ergänzen" if additions else "Unverändert"
        previews.append(PoolMerge(key, status, existing, additions, merged,
            "Nur neue Repository-Texte ergänzt; lokale Texte unverändert."))
        if additions:
            updates[key] = list(merged)
    return MergePreview(tuple(previews), updates)
