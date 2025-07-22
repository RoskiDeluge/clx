# Repository Guidelines for cbot-cli

This project provides a command line tool that interacts with local or remote text generation models. It is packaged as a normal Python project (PEP 517 / pyproject.toml) and exposes a console script named `cbot` or `cbot-cli`.

## Development Setup
1. Create a Python virtual environment and install the project in editable mode:
   ```bash
   python -m venv .venv
   source .venv/bin/activate
   pip install -e .
   ```
2. The CLI is then available via `cbot-cli`. You may run it with flags such as `-g` for general questions, `-x` to execute the response, and `-s` to save shortcuts (see README for details).
3. A local SQLite database (`~/.cbot_cache`) stores previous questions and responses.

## Code Style
- Follow [PEP 8](https://peps.python.org/pep-0008/) guidelines.
- Use 4 spaces for indentation.
- Keep functions short and well documented with comments where necessary.

## Testing
This repository does not include automated tests. If you add new functionality, consider adding tests using `unittest` or `pytest`. When tests exist, run them with:
```bash
pytest
```

## Commit Messages
Describe changes concisely. Reference affected modules or features when possible.

## Pull Request Notes
When creating pull requests, mention any manual steps required to verify functionality (e.g., running `cbot-cli -g "Who is the president?"`).
