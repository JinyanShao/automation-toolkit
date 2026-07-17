"""Scanning, planning, and moving operations for the file organizer."""

from __future__ import annotations

import shutil
from dataclasses import dataclass
from enum import Enum
from pathlib import Path

from .classifiers import Rule, classify_file, parse_rule
from .exceptions import InvalidDirectoryError


class ConflictStrategy(str, Enum):
    """Supported behaviors when a destination filename already exists."""

    SKIP = "skip"
    RENAME = "rename"

    def __str__(self) -> str:
        return self.value


def parse_conflict_strategy(value: ConflictStrategy | str) -> ConflictStrategy:
    """Return a validated conflict strategy."""
    try:
        return ConflictStrategy(value)
    except ValueError as exc:
        raise ValueError(f"Unsupported conflict strategy: {value}") from exc


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


def _normalized_path(path: Path) -> str:
    return str(path).casefold()


def _destination_exists(destination: Path) -> bool:
    """Check for exact and case-insensitive filename conflicts."""
    if destination.exists():
        return True
    if not destination.parent.is_dir():
        return False
    expected_name = destination.name.casefold()
    return any(path.name.casefold() == expected_name for path in destination.parent.iterdir())


def _renamed_destination(destination: Path, reserved: set[str]) -> Path:
    """Find the first available numbered name without touching the filesystem."""
    counter = 1
    while True:
        candidate = destination.with_name(
            f"{destination.stem} ({counter}){destination.suffix}"
        )
        if not _destination_exists(candidate) and _normalized_path(candidate) not in reserved:
            return candidate
        counter += 1


def plan_moves(
    files: list[Path],
    rule: Rule | str,
    conflict_strategy: ConflictStrategy | str = ConflictStrategy.SKIP,
) -> list[MovePlan]:
    """Build a complete move plan, resolving conflicts before execution."""
    selected_rule = parse_rule(rule)
    selected_strategy = parse_conflict_strategy(conflict_strategy)
    plans: list[MovePlan] = []
    reserved: set[str] = set()

    for source in files:
        destination = source.parent / classify_file(source, selected_rule) / source.name
        normalized_destination = _normalized_path(destination)
        has_conflict = _destination_exists(destination) or normalized_destination in reserved

        if has_conflict and selected_strategy is ConflictStrategy.RENAME:
            destination = _renamed_destination(destination, reserved)

        plans.append(MovePlan(source, destination, has_conflict))
        if not (has_conflict and selected_strategy is ConflictStrategy.SKIP):
            reserved.add(_normalized_path(destination))

    return plans


def move_files(
    plans: list[MovePlan],
    *,
    dry_run: bool = False,
    conflict_strategy: ConflictStrategy | str = ConflictStrategy.SKIP,
    output=print,
) -> OrganizeResult:
    """Execute or preview a move plan and return a result summary."""
    selected_strategy = parse_conflict_strategy(conflict_strategy)
    moved = skipped = failed = 0

    for plan in plans:
        if plan.conflict and selected_strategy is ConflictStrategy.SKIP:
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
            if _destination_exists(plan.destination):
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
    rule: Rule | str = Rule.TYPE,
    *,
    dry_run: bool = False,
    conflict_strategy: ConflictStrategy | str = ConflictStrategy.SKIP,
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
