from __future__ import annotations

import sys
from typing import TYPE_CHECKING, Any, Unpack

from rich.console import Console as RichConsole
from rich.theme import Theme
from rich_argparse import RichHelpFormatter

if TYPE_CHECKING:
    from .types import RichConsolePrintKwargs

# Quiet mode state
_QUIET_MODE = False


def set_quiet_mode(enabled: bool) -> None:  # noqa: FBT001
    """Enable or disable quiet mode (suppresses subprocess output)."""
    _QUIET_MODE = enabled


def is_quiet_mode() -> bool:
    """Check if quiet mode is enabled."""
    return _QUIET_MODE


# Custom styles for -h/--help
RichHelpFormatter.styles.update(
    {
        "argparse.args": "cyan",
        "argparse.groups": "green bold",
        "argparse.metavar": "dim cyan",
        "argparse.usage": "dim cyan",
        "argparse.prog": "cyan bold",
        "argparse.custom": "cyan",
    },
)

RichHelpFormatter.usage_markup = True


# Custom rich tags
_APP_THEME = Theme(
    {
        "success": "bright_green bold",
        "error": "bold bright_red",
        "path": "cyan",
        "var": "cyan",
        "tip": "bold bright_green",
        "note": "bold bright_yellow",
        "proj": "cyan bold",
        "value": "cyan",
        "prog": "cyan bold",
    },
)


class _Console(RichConsole):
    """Console wrapper for rich library."""

    def __call__(
        self,
        *objects: Any,  # noqa: ANN401
        **kwargs: Unpack[RichConsolePrintKwargs],
    ) -> None:
        self.print(*objects, **kwargs)


class _ErrConsole(RichConsole):
    """Console wrapper for rich library."""

    def __call__(
        self,
        *objects: Any,  # noqa: ANN401
        exit_code: int | None = None,
        **kwargs: Unpack[RichConsolePrintKwargs],
    ) -> None:
        self.print("[error]error:[/]", *objects, **kwargs)
        if exit_code is not None:
            sys.exit(exit_code)


cout = _Console(theme=_APP_THEME)
cerr = _ErrConsole(stderr=True, theme=_APP_THEME)
