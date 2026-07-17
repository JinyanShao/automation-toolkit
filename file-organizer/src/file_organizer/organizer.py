"""Scanning, planning, and moving operations for the file organizer."""

from __future__ import annotations

import shutil
from dataclasses import dataclass
from pathlib import Path
from typing import Literal

from .classifiers import classify_file
from .exceptions import InvalidDirectoryError

ConflictStrategy = Literal["skip", "rename"]


@dataclass(frozen=True)
class MovePlan:
    """A planned source-to-destination file operation."""

    source: Path
    destination: Path
    conflict: bool = False


@dataclass(frozen=True)
class OrganizeResult:
    """Summary returned after an organization run."""

    planned: int
    moved: int
    skipped: int
    failed: int


def validate_directory(directory: Path) -> Path:
    """Resolve and validate the directory selected by the user."""
    resolved = directory.expanduser().resolve()
    if not resolved.exists():
        raise InvalidDirectoryError(f"Directory does not exist: {resolved}")
    if not resolved.is_dir():
        raise InvalidDirectoryError(f"Path is not a directory: {resolved}")
    return resolved


def scan_files(directory: Path) -> list[Path]:
    """Return visible, top-level regular files in deterministic order."""
    return sorted(
        (
            path
            for path in directory.iterdir()
            if path.is_file() and not path.name.startswith(".")
        ),
        key=lambda path: path.name.casefold(),
    )


def _renamed_destination(destination: Path, reserved: set[Path]) -> Path:
    """Find the first available numbered name without touching the filesystem."""
    counter = 1
    while True:
        candidate = destination.with_name(
            f"{destination.stem} ({counter}){destination.suffix}"
        )
        if not candidate.exists() and candidate not in reserved:
            return candidate
        counter += 1


def plan_moves(
    files: list[Path],
    rule: str,
    conflict_strategy: ConflictStrategy = "skip",
) -> list[MovePlan]:
    """Build a complete move plan, resolving conflicts before execution."""
    plans: list[MovePlan] = []
    reserved: set[Path] = set()

    for source in files:
        destination = source.parent / classify_file(source, rule) / source.name
        has_conflict = destination.exists() or destination in reserved

        if has_conflict and conflict_strategy == "rename":
            destination = _renamed_destination(destination, reserved)

        plans.append(MovePlan(source, destination, has_conflict))
        if not (has_conflict and conflict_strategy == "skip"):
            reserved.add(destination)

    return plans


def move_files(
    plans: list[MovePlan],
    *,
    dry_run: bool = False,
    conflict_strategy: ConflictStrategy = "skip",
    output=print,
) -> OrganizeResult:
    """Execute or preview a move plan and return a result summary."""
    moved = skipped = failed = 0

    for plan in plans:
        if plan.conflict and conflict_strategy == "skip":
            output(f"SKIP     {plan.source.name} -> {plan.destination} (already exists)")
            skipped += 1
            continue

        action = "WOULD MOVE" if dry_run else "MOVE"
        output(f"{action:<10} {plan.source.name} -> {plan.destination}")
        if dry_run:
            continue

        try:
            plan.destination.parent.mkdir(parents=True, exist_ok=True)
            # Recheck immediately before moving to prevent accidental overwrite.
            if plan.destination.exists():
                output(f"SKIP     {plan.source.name} (destination appeared during run)")
                skipped += 1
                continue
            shutil.move(str(plan.source), str(plan.destination))
            moved += 1
        except OSError as exc:
            output(f"ERROR    {plan.source.name}: {exc}")
            failed += 1

    return OrganizeResult(len(plans), moved, skipped, failed)


def organize(
    directory: Path,
    rule: str = "type",
    *,
    dry_run: bool = False,
    conflict_strategy: ConflictStrategy = "skip",
    output=print,
) -> OrganizeResult:
    """Validate, scan, classify, and organize a directory."""
    source_directory = validate_directory(directory)
    files = scan_files(source_directory)
    plans = plan_moves(files, rule, conflict_strategy)
    return move_files(
        plans,
        dry_run=dry_run,
        conflict_strategy=conflict_strategy,
        output=output,
    )
