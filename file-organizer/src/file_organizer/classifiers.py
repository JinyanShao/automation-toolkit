"""Pure functions for mapping files to destination folder names."""

from __future__ import annotations

from datetime import datetime
from enum import Enum
from pathlib import Path

from .exceptions import InvalidRuleError

FILE_TYPE_MAP: dict[str, set[str]] = {
    "Images": {".bmp", ".gif", ".jpeg", ".jpg", ".png", ".tiff", ".webp"},
    "Videos": {".avi", ".flv", ".mkv", ".mov", ".mp4", ".wmv"},
    "Documents": {
        ".doc",
        ".docx",
        ".pdf",
        ".ppt",
        ".pptx",
        ".rtf",
        ".txt",
        ".xls",
        ".xlsx",
    },
    "Archives": {".7z", ".gz", ".rar", ".tar", ".zip"},
    "Audio": {".aac", ".flac", ".mp3", ".wav"},
    "Code": {".c", ".cpp", ".css", ".html", ".java", ".js", ".php", ".py"},
}

ONE_MIB = 1024 * 1024
TEN_MIB = 10 * ONE_MIB


class Rule(str, Enum):
    """Supported file classification rules."""

    TYPE = "type"
    SIZE = "size"
    YEAR = "year"

    def __str__(self) -> str:
        return self.value


def parse_rule(value: Rule | str) -> Rule:
    """Return a validated classification rule."""
    try:
        return Rule(value)
    except ValueError as exc:
        raise InvalidRuleError(value) from exc


def classify_by_type(path: Path) -> str:
    """Classify a file by its case-insensitive suffix."""
    suffix = path.suffix.lower()
    return next(
        (category for category, suffixes in FILE_TYPE_MAP.items() if suffix in suffixes),
        "Others",
    )


def classify_by_size(path: Path) -> str:
    """Classify a file into stable binary-size ranges."""
    size = path.stat().st_size
    if size < ONE_MIB:
        return "Small (<1MiB)"
    if size < TEN_MIB:
        return "Medium (1-10MiB)"
    return "Large (>=10MiB)"


def classify_by_year(path: Path) -> str:
    """Classify a file by its local modification year."""
    return str(datetime.fromtimestamp(path.stat().st_mtime).year)


def classify_file(path: Path, rule: Rule | str) -> str:
    """Apply a named classification rule to a file."""
    classifiers = {
        Rule.TYPE: classify_by_type,
        Rule.SIZE: classify_by_size,
        Rule.YEAR: classify_by_year,
    }
    return classifiers[parse_rule(rule)](path)
