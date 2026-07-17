# Automation Toolkit

A collection of practical Python command-line tools designed to replace repetitive file-management and operational workflows with predictable, reusable automation.

## Current Tool

### File Organizer

[File Organizer](file-organizer/) safely organizes the visible, top-level files in a selected directory.

Current capabilities include:

- Organizing files by type, size, or modification year
- Previewing planned changes with `--dry-run`
- Skipping hidden files and all subdirectories
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
├── .gitignore
├── LICENSE
└── README.md
```

Important paths:

- [.github/workflows/](.github/workflows/) contains continuous-integration workflows.
- [file-organizer/](file-organizer/) contains the current command-line tool.
- [file-organizer/src/file_organizer/](file-organizer/src/file_organizer/) contains its Python package.
- [file-organizer/tests/](file-organizer/tests/) contains its pytest suite.
- [file-organizer/pyproject.toml](file-organizer/pyproject.toml) defines packaging and development dependencies.
- [.gitignore](.gitignore) defines generated files excluded from version control.
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
python3 -m pytest
python3 -m ruff check src tests
```

The [GitHub Actions workflow](.github/workflows/file-organizer-ci.yml) runs these checks on Linux, macOS, and Windows.

## Roadmap

Planned work is listed here rather than represented as existing project structure:

1. Complete and stabilize File Organizer across supported platforms.
2. Add `log-analyzer` as the preferred second tool.
3. Consider `csv-cleaner` after a clear workflow and interface are defined.
4. Add `batch-renamer`, shared utilities, or repository-wide tests only when real reuse cases require them.

Features will be added only when they represent a practical and clearly defined automation use case.

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
