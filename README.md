Automation Toolkit

A collection of practical Python command-line tools designed to automate repetitive file-management and operational tasks.

The project focuses on building small, maintainable utilities that replace manual workflows with predictable and reusable automation.

Current Tool

File Organizer

A command-line utility that organizes files within a selected directory according to configurable criteria.

Current capabilities include:

- Organizing files by file type
- Organizing files by file size
- Creating destination directories automatically
- Handling unsupported or unexpected files safely
- Preventing common file-operation errors

See the file-organizer directory for usage instructions and implementation details.

Project Structure

automation-toolkit/
├── file-organizer/
├── csv-cleaner/
├── log-analyzer/
├── batch-renamer/
├── shared/
├── tests/
├── .github/
│   └── workflows/
├── pyproject.toml
├── .gitignore
├── LICENSE
└── README.md

Each tool is maintained in its own directory and includes dedicated documentation, usage examples, and dependency information where required.

Getting Started

Clone the repository:

git clone https://github.com/JinyanShao/automation-toolkit.git
cd automation-toolkit

Navigate to the tool you want to use and follow the instructions in its local README:

cd file-organizer

Development Principles

The tools in this repository are developed with the following principles:

- Clear and focused responsibilities
- Simple command-line interfaces
- Safe file and data handling
- Readable and maintainable Python code
- Useful error messages
- Minimal external dependencies
- Documentation for installation and usage

Planned Improvements

Future development may include:

- Dry-run support for previewing file operations
- Configurable organization rules
- Structured logging
- Automated tests
- Cross-platform validation
- Additional workflow-automation utilities

Features will be added only when they represent a practical and clearly defined automation use case.

Technology

- Python 3
- Python standard library
- Command-line interfaces
- File-system automation

License

This project is licensed under the MIT License.

Author

Developed by JinyanShao.
