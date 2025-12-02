# Contributing to msdk-py

I've organized the project so that adding new commands is trivial. Feel free to contribute additional commands, just open a PR!

> [!NOTE]
> If you do contribute, add your name (and optionally email) to `authors` in [pyproject.toml](./pyproject.toml)

## Development Prerequisites

Ensure python 3.12+ is installed.

## Development Setup

Setup environment & install dependencies:

```bash
command -v uv >/dev/null && uv sync && . .venv/bin/activate ||
  python3 -m venv .venv && . .venv/bin/activate && pip install -e .
```

## Code Style

- Follow PEP8 as much as possible
- Use 3.12+ type hints on function signatures, class attributes, constants, etc.
- Use [`ruff`](https://github.com/charliermarsh/ruff) for linting (`ruff check`) & formatting (`ruff format`)
- Keep functions short & simple
- Document classes & non-trivial functions
- Use comments seldomly

## Project Structure

```
src/msdk_py/
├── __main__.py            # Program entry point
├── cli.py                 # Top-level CLI argument parser config
│
├── commands/              # Command implementations
│   ├── base.py            # Base command interface
│   └── init/              # `init` command
│       └── ...
│
└── common/               # Shared utilities
    ├── display.py        # Console output styles, etc.
    ├── error.py          # Custom exceptions
    ├── types.py          # Common type definitions
    └── validation.py     # Validation helpers
```

## Adding Commands

1. Create command directory under `src/msdk_py/commands/`
2. Implement `BaseCommand` protocol
3. Add command to `COMMANDS` in `src/commands/__init__.py`

```python
COMMANDS: Final[list[type[BaseCommand]]] = [InitCommand, ..., >>> YOUR NEW CLASS <<<]
```

## Commit Conventions

Use [conventional commit](https://www.conventionalcommits.org/en/v1.0.0/) format:

```
<type>(<scope>): <subject>

[optional body]
```

Common types: `feat`, `fix`, `docs`, `chore`

Keep subject line ≤50 chars, imperative mood, no period.
