# CLAUDE.md - AI Assistant Guide for cbot-cli

This document provides comprehensive guidance for AI assistants (Claude, GPT-4, Gemini, etc.) working with the cbot-cli project.

## Project Overview

**cbot-cli** is a local-first command-line interface tool that enables natural language interaction with large language models (LLMs) for productivity and automation tasks. The tool is designed to help users generate shell commands, ask general questions, and maintain conversational context through an agent mode.

### Key Characteristics

- **Python-based CLI tool** distributed via PyPI
- **Local-first architecture** with SQLite caching
- **Multi-model support**: Ollama (Llama 3.2, DeepSeek) and OpenAI API
- **Persistent memory** for conversational context
- **Simple, lightweight design** with minimal dependencies

## Architecture

### Project Structure

```
cbot-cli/
├── cbot/
│   ├── __init__.py          # Package initialization
│   ├── __main__.py          # Entry point (calls run_cbot)
│   └── cbot_cli.py          # Core application logic (~430 lines)
├── pyproject.toml           # Modern Python packaging configuration
├── setup.py                 # Legacy setup file
├── requirements.txt         # Dependency list
├── README.md               # User documentation
├── AGENTS.md               # AI assistant guide (legacy)
└── LICENSE                 # MIT License
```

### Core Components

#### 1. Entry Point (`cbot/__main__.py`)
- Simple wrapper that calls `run_cbot(sys.argv)`
- Two CLI commands registered: `cbot` and `cbot-cli`

#### 2. Main Application (`cbot/cbot_cli.py`)

**Key Functions:**

- `call_model(prompt, system_message, model, stream_to_stdout)` (line 72)
  - Handles both Ollama and OpenAI API calls
  - Supports streaming output for real-time responses
  - Uses OLLAMA_HOST environment variable (default: http://127.0.0.1:11434)

- `run_cbot(argv)` (line 154)
  - Main orchestration function
  - Handles argument parsing and mode selection
  - Manages model selection via flags

- `Agent` class (line 403)
  - Simple agent implementation with persistent memory
  - Maintains conversation history across sessions
  - Stores memory in SQLite database

**Database Functions:**
- `initDB()` - Creates three tables: questions, conversations, agent_memory
- `load_agent_memory()` - Retrieves conversation history
- `save_agent_memory_item()` - Persists conversation turns
- `clear_agent_memory()` - Resets agent memory

### Database Schema

Location: `~/.cbot_cache` (SQLite3)

**Tables:**

1. **questions** - Single Q&A caching
   - id (PRIMARY KEY)
   - question (TEXT)
   - answer (TEXT)
   - count (INTEGER) - tracks cache hits
   - timestamp (DATETIME)

2. **conversations** - Message history
   - id (PRIMARY KEY)
   - messages (TEXT) - JSON array of message objects
   - timestamp (DATETIME)

3. **agent_memory** - Agent mode persistence
   - id (PRIMARY KEY)
   - memory_item (TEXT)
   - timestamp (DATETIME)

## Command-Line Interface

### Model Selection Flags

Must appear BEFORE the question/command:

- `-l32` - Use Llama 3.2 (default)
- `-ds` - Use DeepSeek-R1
- `-oa` - Use OpenAI o4-mini

### Operation Modes

1. **Normal Mode** (default)
   - Generates shell commands for the detected OS
   - System message: "You are a command line translation tool for {platform}..."
   - Example: `cbot-cli "list all python files"`

2. **General Question Mode** (`-g`)
   - Generic question answering
   - System message: "You are a helpful assistant..."
   - Example: `cbot-cli -g "Who was the 45th president?"`

3. **Agent Mode** (`-a`)
   - Persistent conversational interface
   - Maintains memory across sessions
   - Commands: `exit` to quit, `clear` to reset memory
   - Example: `cbot-cli -a`

4. **Shortcut Mode** (`-s`)
   - Save commands with aliases
   - Format: `cbot-cli -s <name> "<command>"`
   - Example: `cbot-cli -s nap "pmset sleepnow"`

5. **History Mode** (`-m`)
   - Display last 10 conversation messages
   - Example: `cbot-cli -m`

### Execution Flags

- `-x` - Execute the generated command (blocks sudo)
- `-c` - Copy result to clipboard (uses pyperclip)
- `-h` - Display help information

## Technical Details

### Dependencies (pyproject.toml)

```toml
dependencies = [
    "requests",           # HTTP client for Ollama API
    "pyperclip",         # Clipboard integration
    "openai>=1.46.0,<2.0.0",  # OpenAI API client
    "python-dotenv"      # Environment variable management
]
```

### Platform Detection

The tool detects the operating system at runtime (line 307-313):
- `darwin` → "Mac"
- `win32` → "Windows"
- Other → "Linux"

This ensures platform-specific commands are generated correctly.

### Streaming Implementation

For Ollama models (line 92-136):
- Uses Server-Sent Events (SSE) via `requests.post(..., stream=True)`
- Streams tokens to stdout in real-time for better UX
- Collects full response for caching
- Handles JSON-encoded chunks with error recovery

For OpenAI (line 76-90):
- Uses OpenAI SDK's `client.responses.create()`
- No streaming (returns complete response)
- Includes rate limit error handling

### Caching Strategy

- Questions and answers are cached in SQLite
- Cache hits are marked with "💾 Cache Hit"
- Cache count increments on each hit (useful for analytics)
- Adding `?` to queries without one improves LLM performance
- History includes last 10 conversations for context

## Development Guidelines

### When Making Changes

1. **Code Style**
   - Follow existing conventions (functional style, global cache variable)
   - Keep the tool simple and lightweight
   - Maintain backward compatibility

2. **Database Migrations**
   - Use `CREATE TABLE IF NOT EXISTS` pattern
   - Don't break existing cache files
   - Consider migration path for schema changes

3. **Model Integration**
   - New models should use the existing flag pattern
   - Update model_name selection logic (line 162-174)
   - Test both streaming and non-streaming modes

4. **Error Handling**
   - Handle network timeouts gracefully
   - Provide clear error messages for API issues
   - Never expose API keys in error output

### Testing Workflow

```bash
# Install in development mode
pip install -e .

# Test different modes
cbot-cli -g "What is 2+2?"
cbot-cli "list files"
cbot-cli -a  # Test agent mode
cbot-cli -m  # View history

# Test model switching
cbot-cli -l32 -g "Hello"
cbot-cli -ds -g "Hello"
cbot-cli -oa -g "Hello"  # Requires OPENAI_API_KEY

# Test execution modes
cbot-cli -c "get current directory"  # Copies to clipboard
cbot-cli -x "print hello world"      # Executes (be careful!)
```

### Common Tasks

**Add a new model:**
1. Add flag to model selection (line 161-174)
2. Update `call_model()` if new API integration needed
3. Update README.md with new flag documentation

**Modify agent behavior:**
1. Edit Agent class (line 403-430)
2. Update system prompt (line 187)
3. Consider memory management and context window limits

**Change caching logic:**
1. Modify `checkQ()` and `insertQ()` functions
2. Update database schema if needed (line 39-63)
3. Test cache invalidation scenarios

## Important Considerations

### Security

- **Sudo protection**: The tool refuses to execute sudo commands (line 389-390)
- **API key handling**: Uses environment variables via python-dotenv
- **Local-first**: Sensitive data stays on user's machine
- **No telemetry**: No data sent to external services (except LLM APIs)

### Limitations

- Context window overflow not handled in agent mode (TODO at line 416)
- Single global cache connection (not thread-safe)
- No conversation branching or checkpointing
- Limited to 256 tokens for Ollama responses (line 99)

### Environment Variables

- `OPENAI_API_KEY` - Required for OpenAI models
- `OLLAMA_HOST` - Override Ollama endpoint (default: http://127.0.0.1:11434)

## Version Information

- Current version: 0.2.2 (pyproject.toml:7)
- Python requirement: >=3.7
- License: MIT (Copyright 2021 Greg Raiz)
- Maintainer: Roberto L. Delgado <roberto@delgadodev.xyz>

## Useful References

- Repository: https://github.com/roskideluge/cbot
- PyPI: https://pypi.org/project/cbot-cli/
- Ollama Models: https://ollama.com/search
- OpenAI API: https://platform.openai.com

## Key Files to Review

When working on the codebase, focus on:

1. `cbot/cbot_cli.py` - All core logic
2. `pyproject.toml` - Dependencies and metadata
3. `README.md` - User-facing documentation
4. `~/.cbot_cache` - Database location (created at runtime)

## Quick Tips for AI Assistants

- The codebase is intentionally simple (~430 lines of core logic)
- Prefer functional approach over OOP (except Agent class)
- Always test both Ollama and OpenAI code paths
- Cache invalidation happens via DELETE + INSERT pattern
- Agent mode is the most complex feature - handle with care
- Platform detection ensures cross-OS compatibility
- Streaming provides better UX but adds complexity
