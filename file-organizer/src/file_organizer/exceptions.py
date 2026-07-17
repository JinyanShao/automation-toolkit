"""Application-specific exceptions."""


class FileOrganizerError(Exception):
    """Base exception for expected file-organizer failures."""


class InvalidDirectoryError(FileOrganizerError):
    """Raised when the requested source directory cannot be used."""
