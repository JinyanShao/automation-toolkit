"""Scanning, planning, and moving operations for the file organizer."""

from __future__ import annotations

import errno
import os
import sys
from dataclasses import dataclass
from enum import Enum
from pathlib import Path

from .classifiers import Rule, classify_file, parse_rule
from .exceptions import (
    ClassificationError,
    InvalidConflictStrategyError,
    InvalidDirectoryError,
)


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
        raise InvalidConflictStrategyError(value) from exc


@dataclass(frozen=True)
class MovePlan:
    """A planned source-to-destination file operation."""

    source: Path
    destination: Path
    conflict: bool = False
    same_object: bool = False


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
        raise InvalidDirectoryError.missing(resolved)
    if not resolved.is_dir():
        raise InvalidDirectoryError.not_directory(resolved)
    return resolved


def scan_files(directory: Path) -> list[Path]:
    """Return visible, top-level, non-symlink regular files in deterministic order."""
    return sorted(
        (
            path
            for path in directory.iterdir()
            if not path.name.startswith(".") and not path.is_symlink() and path.is_file()
        ),
        key=lambda path: path.name.casefold(),
    )


def _normalized_path(path: Path) -> str:
    return str(path).casefold()


def _existing_destination(destination: Path) -> Path | None:
    """Return an exact or case-insensitive existing destination."""
    if destination.parent.is_symlink():
        return None
    if destination.exists():
        return destination
    if not destination.parent.is_dir():
        return None
    expected_name = destination.name.casefold()
    return next(
        (path for path in destination.parent.iterdir() if path.name.casefold() == expected_name),
        None,
    )


def _same_file(source: Path, destination: Path) -> bool:
    try:
        return source.samefile(destination)
    except OSError:
        return False


def _print_error(message: str) -> None:
    print(message, file=sys.stderr)


def _move_without_overwrite(source: Path, destination: Path) -> None:
    """Create the destination atomically, then remove the source name.

    Directory descriptors and O_NOFOLLOW pin the category directory on POSIX.
    The path-based fallback retains atomic no-replace file creation on platforms
    without dir_fd support and rejects a category directory that is already a link.
    """
    source_directory = source.parent.resolve(strict=True)
    destination_root = destination.parent.parent.resolve(strict=True)
    if source_directory != destination_root:
        raise OSError(
            errno.EPERM, "destination must be a direct category directory", str(destination)
        )

    directory_flags = os.O_RDONLY | getattr(os, "O_DIRECTORY", 0)
    no_follow = getattr(os, "O_NOFOLLOW", 0)
    supports_directory_descriptors = (
        os.name == "posix"
        and no_follow
        and os.open in os.supports_dir_fd
        and os.mkdir in os.supports_dir_fd
        and os.link in os.supports_dir_fd
        and os.unlink in os.supports_dir_fd
        and os.link in os.supports_follow_symlinks
    )

    if supports_directory_descriptors:
        source_fd = os.open(source_directory, directory_flags | no_follow)
        try:
            try:
                os.mkdir(destination.parent.name, dir_fd=source_fd)
            except FileExistsError:
                pass

            destination_fd = os.open(
                destination.parent.name,
                directory_flags | no_follow,
                dir_fd=source_fd,
            )
            try:
                os.link(
                    source.name,
                    destination.name,
                    src_dir_fd=source_fd,
                    dst_dir_fd=destination_fd,
                    follow_symlinks=False,
                )
                os.unlink(source.name, dir_fd=source_fd)
            finally:
                os.close(destination_fd)
        finally:
            os.close(source_fd)
        return

    destination_directory = destination.parent
    if destination_directory.is_symlink():
        raise OSError(
            errno.ELOOP,
            "symbolic-link category directories are not supported",
            str(destination_directory),
        )
    destination_directory.mkdir(parents=True, exist_ok=True)
    if destination_directory.is_symlink():
        raise OSError(
            errno.ELOOP,
            "symbolic-link category directories are not supported",
            str(destination_directory),
        )
    if destination_directory.resolve(strict=True).parent != source_directory:
        raise OSError(
            errno.EPERM, "destination escaped the selected directory", str(destination_directory)
        )

    os.link(source, destination, follow_symlinks=False)
    source.unlink()


def _renamed_destination(destination: Path, reserved: set[str]) -> Path:
    """Find the first available numbered name without touching the filesystem."""
    counter = 1
    while True:
        candidate = destination.with_name(f"{destination.stem} ({counter}){destination.suffix}")
        if _existing_destination(candidate) is None and _normalized_path(candidate) not in reserved:
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
        try:
            category = classify_file(source, selected_rule)
        except OSError as exc:
            raise ClassificationError(source, exc) from exc

        destination = source.parent / category / source.name
        normalized_destination = _normalized_path(destination)
        existing_destination = _existing_destination(destination)
        same_object = existing_destination is not None and _same_file(source, existing_destination)
        has_conflict = existing_destination is not None or normalized_destination in reserved

        if has_conflict and not same_object and selected_strategy is ConflictStrategy.RENAME:
            destination = _renamed_destination(destination, reserved)

        plans.append(MovePlan(source, destination, has_conflict, same_object))
        if not same_object and not (has_conflict and selected_strategy is ConflictStrategy.SKIP):
            reserved.add(_normalized_path(destination))

    return plans


def move_files(
    plans: list[MovePlan],
    *,
    dry_run: bool = False,
    conflict_strategy: ConflictStrategy | str = ConflictStrategy.SKIP,
    output=print,
    error_output=_print_error,
) -> OrganizeResult:
    """Execute or preview a move plan and return a result summary."""
    selected_strategy = parse_conflict_strategy(conflict_strategy)
    moved = skipped = failed = 0

    for plan in plans:
        if plan.same_object:
            output(f"SKIP     {plan.source.name} (source and destination are the same file)")
            skipped += 1
            continue

        if plan.conflict and selected_strategy is ConflictStrategy.SKIP:
            output(f"SKIP     {plan.source.name} -> {plan.destination} (already exists)")
            skipped += 1
            continue

        action = "WOULD MOVE" if dry_run else "MOVE"
        output(f"{action:<10} {plan.source.name} -> {plan.destination}")
        if dry_run:
            continue

        try:
            _move_without_overwrite(plan.source, plan.destination)
            moved += 1
        except FileExistsError:
            output(f"SKIP     {plan.source.name} (destination appeared during run)")
            skipped += 1
        except OSError as exc:
            error_output(f"ERROR    {plan.source.name}: {exc}")
            failed += 1

    return OrganizeResult(len(plans), moved, skipped, failed)


def organize(
    directory: Path,
    rule: Rule | str = Rule.TYPE,
    *,
    dry_run: bool = False,
    conflict_strategy: ConflictStrategy | str = ConflictStrategy.SKIP,
    output=print,
    error_output=_print_error,
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
        error_output=error_output,
    )
