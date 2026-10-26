"""First-install workflow for absent RP addons only.

All packages are staged and checked before a single addon is installed. Existing
addon folders are never touched. On partial failure previous new installations
are rolled back using their recorded manifests.
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import shutil
import tempfile

from addon_manager import known_addons, _linked, rollback, InstallError
from github_staging import stage
from safe_github_install import preview_safe_install, install_safe, SafePlan
from wow_client_profiles import ClientProfile
from wow_detection import inspect_client


@dataclass(frozen=True)
class MissingBatch:
    target: Path
    profile: ClientProfile
    channel: str
    scratch: Path
    plans: tuple[SafePlan, ...]


def missing_names(target: Path) -> tuple[str, ...]:
    """Only absent known addon directories may participate in a first install."""
    target = Path(target).absolute()
    if target.name.casefold() != "addons" or target.parent.name.casefold() != "interface":
        raise InstallError("Ziel muss Interface/AddOns sein.")
    if not target.is_dir() or any(_linked(p) for p in (target, *target.parents)):
        raise InstallError("Bitte eine bestätigte WoW-Installation mit Interface/AddOns wählen.")
    names_on_disk = {p.name.casefold() for p in target.iterdir()}
    return tuple(name for name in known_addons() if name.casefold() not in names_on_disk)


def prepare_missing(target: Path, profile: ClientProfile, channel: str = "stable",
                    names: tuple[str, ...] | None = None) -> MissingBatch:
    target = Path(target).absolute()
    installation = inspect_client(target.parent.parent)
    if installation is None or not installation.verified or installation.client_root.resolve() != profile.client_root.resolve():
        raise InstallError("WoW-Installation oder Interface-Profil ungültig.")
    available = missing_names(target)
    if names is None:
        names = available
    if not names or len(names) != len(set(names)) or any(name not in available for name in names):
        raise InstallError("Bitte mindestens ein noch nicht installiertes, bekanntes RP-AddOn auswählen.")
    if not names:
        raise InstallError("Alle bekannten RP-AddOns sind bereits vorhanden.")
    scratch = Path(tempfile.mkdtemp(prefix="rptextstudio-first-install-"))
    try:
        plans = []
        for name in names:
            destination = scratch / name
            stage(name, channel, destination)
            plan = preview_safe_install(name, destination, target, profile)
            if plan.protected or plan.target_hashes or not plan.new_files:
                raise InstallError(f"Kein sicherer Neuinstallationsplan für {name}.")
            plans.append(plan)
        return MissingBatch(target, profile, channel, scratch, tuple(plans))
    except Exception:
        shutil.rmtree(scratch, ignore_errors=True)
        raise


def install_missing(batch: MissingBatch) -> tuple[Path, ...]:
    """Commit approved batch; best-effort rollback if a later installation fails."""
    if not batch.plans:
        raise InstallError("Keine AddOns zur Installation.")
    if any(name not in missing_names(batch.target) for name in (plan.name for plan in batch.plans)):
        raise InstallError("AddOn-Bestand wurde seit der Vorschau verändert.")
    for plan in batch.plans:
        if preview_safe_install(plan.name, plan.source, batch.target, batch.profile) != plan:
            raise InstallError(f"Installationsvorschau für {plan.name} ist nicht mehr aktuell.")
    backups = []
    try:
        for plan in batch.plans:
            # Protect against concurrent creation of an addon during installation.
            if (batch.target / plan.name).exists():
                raise InstallError(f"{plan.name} wurde inzwischen installiert.")
            backups.append(install_safe(plan, batch.profile))
        return tuple(backups)
    except Exception as cause:
        failures = []
        for backup in reversed(backups):
            try:
                rollback(batch.target, backup)
            except Exception as exc:
                failures.append(str(exc))
        if failures:
            raise InstallError("Installation fehlgeschlagen. Automatische Wiederherstellung "
                "unvollständig, Sicherungen nicht löschen: " + "; ".join(failures)) from cause
        raise InstallError("Installation fehlgeschlagen; zuvor angelegte AddOns wurden "
                           "zurückgenommen: " + str(cause)) from cause


def discard_missing(batch: MissingBatch) -> None:
    shutil.rmtree(batch.scratch, ignore_errors=True)
