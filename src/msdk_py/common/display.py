from __future__ import annotations

import sys
from typing import TYPE_CHECKING, Any, Unpack

from rich.console import Console as RichConsole
from rich.theme import Theme
from rich_argparse import RichHelpFormatter

if TYPE_CHECKING:
    from .types import RichConsolePrintKwargs

# Custom styles for -h/--help
RichHelpFormatter.styles.update(
    {
        "argparse.args": "cyan",
        "argparse.groups": "green bold",
        "argparse.metavar": "dim cyan",
        "argparse.prog": "cyan bold",
        "argparse.custom": "cyan",
    },
)


# Custom rich tags
_APP_THEME = Theme(
    {
        "success": "bright_green",
        "error": "bold bright_red",
        "path": "cyan",
        "var": "cyan",
        "tip": "bold bright_green",
        "note": "bold bright_yellow",
        "proj": "cyan bold",
        "value": "cyan",
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
