# File Organizer

A small, reliable command-line tool that organizes the visible, top-level files in a directory. It supports classification by file type, file size, or modification year and never overwrites an existing file.

## Safety behavior

- Only top-level regular files are scanned; subdirectories are never traversed.
- Hidden files (names beginning with `.`) are ignored.
- Destination directories are skipped naturally because directories are not scan candidates.
- `--dry-run` previews every planned move without creating directories or changing files.
- Existing destination files are skipped by default.
- `--conflict rename` preserves both files by choosing names such as `report (1).txt`.
- The destination is checked again immediately before each move to reduce overwrite risk.

## Requirements

- Python 3.10 or newer
- No runtime dependencies outside the Python standard library
- pytest 8 or newer for development and tests

## Installation

From this directory, install the command in editable mode:

```bash
python3 -m pip install -e .
```

To install the test dependency as well:

```bash
python3 -m pip install -e '.[dev]'
```

## Usage

Preview the default type-based organization first:

```bash
file-organizer ~/Downloads --dry-run
```

Apply the same changes:

```bash
file-organizer ~/Downloads
```

Choose another rule:

```bash
file-organizer ~/Downloads --rule size --dry-run
file-organizer ~/Downloads --rule year --dry-run
```

Keep both files when a destination name already exists:

```bash
file-organizer ~/Downloads --conflict rename
```

The complete interface is available with:

```bash
file-organizer --help
```

If the package is not installed, run it from the project directory with:

```bash
PYTHONPATH=src python3 -m file_organizer.cli ~/Downloads --dry-run
```

## Organization rules

| Rule | Destination examples |
| --- | --- |
| `type` | `Images`, `Documents`, `Code`, `Others` |
| `size` | `Small (<1MiB)`, `Medium (1-10MiB)`, `Large (>=10MiB)` |
| `year` | `2024`, `2025`, `2026` |

## Conflict strategies

| Strategy | Behavior |
| --- | --- |
| `skip` | Default. Leave the source and existing destination unchanged. |
| `rename` | Move the source using the first available numbered filename. |

No strategy overwrites an existing destination.

## Development

Run the test suite from this directory:

```bash
python3 -m pytest
```

The implementation is separated by responsibility:

```text
file-organizer/
├── src/file_organizer/
│   ├── __init__.py
│   ├── cli.py
│   ├── organizer.py
│   ├── classifiers.py
│   └── exceptions.py
├── tests/
│   ├── test_organizer.py
│   └── test_classifiers.py
├── README.md
└── pyproject.toml
```
