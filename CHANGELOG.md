# Changelog

All notable changes to this project are documented in this file.

The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and releases use [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2026-07-17

### Added

- File Organizer command-line interface with type, size, and modification-year rules.
- Dry-run previews that do not create directories or move files.
- Explicit `skip` and `rename` conflict strategies without file overwrites.
- Safe top-level scanning that ignores hidden files, symbolic links, and subdirectories.
- Clear stdout and stderr behavior with stable exit codes.
- Packaging metadata and a `file-organizer` console command.

### Quality

- Automated tests for CLI behavior, classifiers, conflicts, and filesystem edge cases.
- Ruff linting and formatting checks.
- An 85% minimum coverage requirement.
- GitHub Actions validation on Ubuntu, macOS, and Windows with Python 3.10 and 3.14.

[1.0.0]: https://github.com/JinyanShao/automation-toolkit/releases/tag/v1.0.0
