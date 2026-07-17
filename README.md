# Automation Toolkit

[![Tests](https://github.com/JinyanShao/automation-toolkit/actions/workflows/file-organizer-ci.yml/badge.svg)](https://github.com/JinyanShao/automation-toolkit/actions/workflows/file-organizer-ci.yml)
[![Python](https://img.shields.io/badge/python-3.10%20%7C%203.14-blue.svg)](file-organizer/pyproject.toml)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Coverage threshold](https://img.shields.io/badge/coverage-85%25_minimum-brightgreen.svg)](file-organizer/pyproject.toml)

Practical Python command-line tools for safe file management and repeatable workflow automation.

## Core Features

- Safe, non-recursive file organization by type, size, or modification year
- Dry-run previews before any directory is created or file is moved
- Explicit filename conflict handling without overwriting existing content
- Cross-platform tests on Ubuntu, macOS, and Windows

## Quick Example

```bash
cd file-organizer
python3 -m pip install -e .
file-organizer ~/Downloads --dry-run
```

## Current Tool

### File Organizer

[File Organizer](file-organizer/) safely organizes the visible, top-level files in a selected directory.

Current capabilities include:

- Organizing files by type, size, or modification year
- Previewing planned changes with `--dry-run`
- Skipping hidden files, symbolic links, and all subdirectories
- Creating destination directories automatically
- Handling filename conflicts with explicit `skip` and `rename` strategies
- Preventing existing files from being overwritten
- Reporting planned, moved, skipped, and failed operations clearly

See the [File Organizer documentation](file-organizer/README.md) for installation, usage, and development instructions.

## Project Structure

This tree shows only files and directories that currently exist:

```text
automation-toolkit/
├── .github/
│   └── workflows/
│       └── file-organizer-ci.yml
├── file-organizer/
│   ├── src/
│   │   └── file_organizer/
│   ├── tests/
│   ├── README.md
│   └── pyproject.toml
├── .editorconfig
├── .gitignore
├── CHANGELOG.md
├── CONTRIBUTING.md
├── LICENSE
└── README.md
```

Important paths:

- [.github/workflows/](.github/workflows/) contains continuous-integration workflows.
- [file-organizer/](file-organizer/) contains the current command-line tool.
- [file-organizer/src/file_organizer/](file-organizer/src/file_organizer/) contains its Python package.
- [file-organizer/tests/](file-organizer/tests/) contains its pytest suite.
- [file-organizer/pyproject.toml](file-organizer/pyproject.toml) defines packaging and development dependencies.
- [.editorconfig](.editorconfig) defines shared editor formatting defaults.
- [.gitignore](.gitignore) defines generated files excluded from version control.
- [CHANGELOG.md](CHANGELOG.md) records notable release changes.
- [CONTRIBUTING.md](CONTRIBUTING.md) explains the contribution workflow and quality checks.
- [LICENSE](LICENSE) contains the MIT License.

Each tool is maintained in its own directory with dedicated documentation, tests, and dependency information.

## Getting Started

Clone the repository:

```bash
git clone https://github.com/JinyanShao/automation-toolkit.git
cd automation-toolkit
```

Open the current tool and install its development dependencies:

```bash
cd file-organizer
python3 -m pip install -e '.[dev]'
```

Preview an organization run before changing any files:

```bash
file-organizer ~/Downloads --dry-run
```

## Development Principles

- Clear and focused responsibilities
- Simple command-line interfaces
- Safe file and data handling
- Readable and maintainable Python code
- Useful error messages and operation summaries
- Minimal runtime dependencies
- Automated tests and cross-platform validation
- Documentation for installation and usage

## Quality Checks

Run the checks from [file-organizer/](file-organizer/):

```bash
python3 -m ruff check src tests
python3 -m ruff format --check src tests
python3 -m pytest --cov=file_organizer --cov-report=term-missing --cov-fail-under=85
```

The [GitHub Actions workflow](.github/workflows/file-organizer-ci.yml) runs linting, formatting, tests, and the 85% coverage gate on Linux, macOS, and Windows.

## Roadmap

- Continue stabilizing File Organizer across supported platforms.
- Define and develop Log Analyzer as the next practical tool.
- Consider CSV Cleaner after its workflow and interface are clearly specified.

Planned tools remain roadmap items until working implementations exist.

## Technology

- Python 3.10+
- Python standard library
- `argparse` command-line interfaces
- `pathlib` file-system operations
- pytest and Ruff for quality checks
- GitHub Actions for cross-platform validation

## License

This project is licensed under the [MIT License](LICENSE).

## Author

Developed by Jinyan Shao.
