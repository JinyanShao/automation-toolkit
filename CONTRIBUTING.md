# Contributing

Contributions should keep each tool focused, safe, documented, and independently testable.

## Development Setup

Clone the repository and install the File Organizer development dependencies:

```bash
git clone https://github.com/JinyanShao/automation-toolkit.git
cd automation-toolkit/file-organizer
python3 -m pip install -e '.[dev]'
```

## Quality Checks

Run all checks from `file-organizer/` before opening a pull request:

```bash
python3 -m ruff check src tests
python3 -m ruff format --check src tests
python3 -m pytest --cov=file_organizer --cov-report=term-missing --cov-fail-under=85
```

## Change Guidelines

- Keep runtime dependencies minimal and justify any new dependency.
- Preserve the rule that existing destination files are never overwritten.
- Add or update tests whenever behavior changes.
- Update the relevant README and changelog when user-facing behavior changes.
- Do not create directories for planned tools before a working implementation exists.
- Keep changes scoped so they can be reviewed and reverted independently.

## Commit Messages

Use concise Conventional Commits for new work. Examples:

```text
test: add CLI and edge-case coverage
ci: add coverage and formatting checks
docs: finalize file organizer documentation
```

Existing history does not need to be rewritten.

## Pull Requests

Describe what changed, why it changed, and how it was validated. Keep unrelated changes in separate pull requests and ensure all applicable checks pass before merging.
