"""Application-specific exceptions."""

from __future__ import annotations

from pathlib import Path


class FileOrganizerError(Exception):
    """Base exception for expected file-organizer failures."""


class InvalidDirectoryError(FileOrganizerError):
    """Raised when the requested source directory cannot be used."""

    @classmethod
    def missing(cls, path: Path) -> InvalidDirectoryError:
        return cls(f"Directory does not exist: {path}")

    @classmethod
    def not_directory(cls, path: Path) -> InvalidDirectoryError:
        return cls(f"Path is not a directory: {path}")


class ClassificationError(FileOrganizerError):
    """Raised when a file changes or becomes inaccessible during classification."""

    def __init__(self, path: Path, cause: OSError) -> None:
        super().__init__(f"Could not classify '{path}': {cause}")


class InvalidRuleError(FileOrganizerError, ValueError):
    """Raised when a classification rule is not supported."""

    def __init__(self, value: object) -> None:
        super().__init__(f"Unsupported organization rule: {value}")


class InvalidConflictStrategyError(FileOrganizerError, ValueError):
    """Raised when a conflict strategy is not supported."""

    def __init__(self, value: object) -> None:
        super().__init__(f"Unsupported conflict strategy: {value}")
