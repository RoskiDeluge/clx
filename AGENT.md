# Gemini Code Assistant Guide

This document provides a guide for the Gemini code assistant to effectively understand and contribute to the `cbot-cli` project.

## Project Overview

`cbot-cli` is a command-line interface (CLI) tool written in Python that allows users to interact with various large language models (LLMs). It supports local models via Ollama (e.g., Llama 3.2, DeepSeek) and cloud-based models via the OpenAI API.

The key features include:
- **Model Selection:** Users can switch between different LLMs using command-line flags.
- **General Questions:** A mode for asking general knowledge questions.
- **Command Shortcuts:** Users can save and execute shell commands as named shortcuts.
- **Clipboard Integration:** Option to copy the generated command to the clipboard instead of executing it.
- **Agent Mode:** A persistent, stateful chat mode that remembers conversation history across sessions.
- **Local Caching:** Uses a local SQLite database to cache questions and responses for efficiency.

## Core Technologies

- **Language:** Python 3
- **LLM Integration:**
    - `requests` library for interacting with the Ollama API.
    - `openai` library for the OpenAI API.
- **CLI Framework:** `argparse` for parsing command-line arguments.
- **Database:** `sqlite3` for local caching of conversations.
- **Packaging:** `setuptools` (configured via `pyproject.toml` and `setup.py`).

## Project Structure

-   `cbot/`: Main source code directory.
    -   `cbot_cli.py`: Core application logic, including argument parsing, API interaction, and database management.
    -   `__main__.py`: Entry point for running the CLI, which calls the main function in `cbot_cli.py`.
-   `pyproject.toml`: Defines project metadata, dependencies, and the `cbot-cli` script entry point.
-   `requirements.txt`: Lists Python dependencies.
-   `README.md`: User-facing documentation.
-   `~/.cbot_cache`: Location of the SQLite database for caching.

## Development Workflow

### Setup

1.  **Clone the repository.**
2.  **Install in editable mode:**
    ```bash
    pip install -e .
    ```
    This makes the `cbot-cli` command available in the shell and reflects code changes immediately.

### Running the CLI

The primary entry point is the `cbot-cli` command.

**Examples:**
-   Ask a general question with the default model:
    ```bash
    cbot-cli -g "What is the capital of France?"
    ```
-   Get a shell command and execute it:
    ```bash
    cbot-cli "list all files in the current directory"
    ```
-   Use a specific model (e.g., OpenAI):
    ```bash
    cbot-cli -oa -g "Explain the theory of relativity"
    ```
-   Save a command shortcut:
    ```bash
    cbot-cli -s list_py "ls *.py"
    ```
-   Execute a saved shortcut:
    ```bash
    cbot-cli -x list_py
    ```

### Modifying Code

-   The main logic is in `cbot/cbot_cli.py`.
-   The `main()` function in this file is the primary entry point that orchestrates the application's behavior based on the parsed arguments.
-   Dependencies are managed in `pyproject.toml` and mirrored in `requirements.txt`.

When making changes, ensure they align with the existing structure and conventions. The tool should remain a simple, efficient CLI application.