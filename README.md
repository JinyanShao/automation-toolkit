# Automation Toolkit

Small Python command-line utilities for repeatable file-processing tasks.

## Tools

### File Organizer

Organizes visible, top-level files by type, size, or modification year without overwriting existing files.

Usage:

```bash
file-organizer DIRECTORY [--rule type|size|year] [--dry-run] [--conflict skip|rename]
```

Example:

```text
before/
├── photo.jpg
├── report.pdf
└── notes.txt

after/
├── Documents/
│   ├── notes.txt
│   └── report.pdf
└── Images/
    └── photo.jpg
```

See the [File Organizer README](file-organizer/README.md) for the full command reference.

## Installation

Requires Python 3.10 or newer.

```bash
git clone https://github.com/JinyanShao/automation-toolkit.git
cd automation-toolkit/file-organizer
python3 -m pip install -e .
```

## Usage

```bash
# Preview type-based organization
file-organizer ~/Downloads --dry-run

# Organize by file size
file-organizer ~/Downloads --rule size

# Organize by year and rename collisions
file-organizer ~/Downloads --rule year --conflict rename
```

## Behavior

- Only visible files in the selected directory are processed; subdirectories, hidden files, and symbolic links are ignored.
- The default rule is `type`, and the default collision strategy is `skip`.
- `--dry-run` prints the planned moves without creating directories or moving files.
- `--conflict rename` keeps both files by adding a number to the incoming filename.
- Existing files are never overwritten.
- Invalid input and planning errors return exit code `2`; failed moves return exit code `1`.

## Tests

From `file-organizer/`, run:

```bash
python3 -m pip install -e '.[dev]'
python3 -m pytest --cov=file_organizer --cov-fail-under=85
```

## Planned tools

- Log Analyzer
- CSV Cleaner

Licensed under the [MIT License](LICENSE).
