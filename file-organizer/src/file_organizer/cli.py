"""Command-line entry point."""

from __future__ import annotations

import argparse
from pathlib import Path

from .classifiers import RULES
from .exceptions import FileOrganizerError
from .organizer import organize


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="file-organizer",
        description="Organize visible files in a directory safely and predictably.",
    )
    parser.add_argument("directory", type=Path, help="directory whose top-level files are organized")
    parser.add_argument(
        "--rule",
        choices=RULES,
        default="type",
        help="classification rule (default: type)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="preview operations without creating folders or moving files",
    )
    parser.add_argument(
        "--conflict",
        choices=("skip", "rename"),
        default="skip",
        help="handle an existing destination by skipping or adding a number (default: skip)",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    mode = "DRY RUN" if args.dry_run else "RUN"
    print(f"[{mode}] directory={args.directory} rule={args.rule} conflict={args.conflict}")

    try:
        result = organize(
            args.directory,
            args.rule,
            dry_run=args.dry_run,
            conflict_strategy=args.conflict,
        )
    except (FileOrganizerError, OSError) as exc:
        print(f"ERROR: {exc}")
        return 2

    print(
        "Summary: "
        f"planned={result.planned} moved={result.moved} "
        f"skipped={result.skipped} failed={result.failed}"
    )
    return 1 if result.failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
