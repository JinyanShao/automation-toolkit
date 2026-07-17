# File Organizer

[![Tests](https://github.com/JinyanShao/automation-toolkit/actions/workflows/file-organizer-ci.yml/badge.svg)](https://github.com/JinyanShao/automation-toolkit/actions/workflows/file-organizer-ci.yml)
[![Coverage threshold](https://img.shields.io/badge/coverage-85%25_minimum-brightgreen.svg)](pyproject.toml)

A small, reliable command-line tool that organizes the visible, top-level files in a directory. It supports classification by file type, file size, or modification year and never overwrites an existing file.

## Safety behavior

- Only top-level regular files are scanned; subdirectories are never traversed.
- Hidden files (names beginning with `.`) are ignored.
- Symbolic links are ignored, even when they point to regular files.
- Destination directories are skipped naturally because directories are not scan candidates.
- `--dry-run` previews every planned move without creating directories or changing files.
- Existing destination files are skipped by default.
- `--conflict rename` preserves both files by choosing names such as `report (1).txt`.
- A source and destination that refer to the same file object are always skipped.
- The destination is checked again immediately before each move to reduce overwrite risk.
- Existing destination content is never overwritten by any conflict strategy.

## Reversibility

File Organizer does not keep an automatic recovery log and does not provide an undo command. Always run with `--dry-run` first, review the complete plan, and keep a backup when organizing important files. If a run is applied, reversing it requires moving the files back manually.

## Requirements

- Python 3.10 or newer
- No runtime dependencies outside the Python standard library
- pytest 8 or newer for tests
- pytest-cov for coverage checks
- Ruff for linting, complexity checks, and formatting

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

## Example Output

A dry run prints planned operations without changing the filesystem:

```text
[DRY RUN] directory=/Users/example/Downloads rule=type conflict=skip
WOULD MOVE photo.jpg -> /Users/example/Downloads/Images/photo.jpg
WOULD MOVE report.pdf -> /Users/example/Downloads/Documents/report.pdf
Summary: planned=2 moved=0 skipped=0 failed=0
```

Errors are written to stderr. Normal operations and the final summary are written to stdout.

## Before and After

Before running type-based organization:

```text
Downloads/
├── .notes.txt
├── photo.jpg
├── report.pdf
└── existing-folder/
```

After running `file-organizer ~/Downloads`:

```text
Downloads/
├── .notes.txt
├── Documents/
│   └── report.pdf
├── Images/
│   └── photo.jpg
└── existing-folder/
```

The hidden file and existing directory remain unchanged.

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

## Exit Codes

| Code | Meaning |
| --- | --- |
| `0` | The command completed without file-operation failures. A successful dry run also returns `0`. |
| `1` | At least one planned file move failed; other independent moves may have completed. |
| `2` | The command could not start or finish planning because of invalid input or an application-level filesystem error. |

## Limitations

- Organization is intentionally non-recursive; files inside subdirectories are not scanned.
- Hidden files and symbolic links are ignored.
- File-type classification uses the final suffix, so `archive.tar.gz` is classified from `.gz`.
- Year classification uses the file's modification year in the local timezone.
- Size thresholds use binary units: 1 MiB equals 1,048,576 bytes.
- Rules and file-type mappings are defined by the package and are not loaded from a user configuration file.
- Concurrent filesystem changes can cause a file to be skipped or reported as failed.
- The tool does not produce an operation report, recovery log, or automatic undo record.

## Development

Run the test suite with the same coverage gate used in CI:

```bash
python3 -m pytest --cov=file_organizer --cov-report=term-missing --cov-fail-under=85
```

Run Ruff against the package and tests:

```bash
python3 -m ruff check src tests
python3 -m ruff format --check src tests
```

The repository's [GitHub Actions workflow](../.github/workflows/file-organizer-ci.yml) runs linting, formatting, tests, and coverage checks on Linux, macOS, and Windows. It can also be started manually from the Actions tab.

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
│   ├── test_cli.py
│   ├── test_organizer.py
│   └── test_classifiers.py
├── README.md
└── pyproject.toml
```
