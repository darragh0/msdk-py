from __future__ import annotations

from typing import TYPE_CHECKING, Annotated, Literal, TypedDict

if TYPE_CHECKING:
    from rich.console import JustifyMethod, OverflowMethod
    from rich.style import Style


class RichConsolePrintKwargs(TypedDict, total=False):
    """Typed keyword arguments for rich.console.print()."""

    sep: str
    end: str
    style: str | Style | None
    justify: JustifyMethod | None
    overflow: OverflowMethod | None
    no_wrap: bool | None
    emoji: bool | None
    markup: bool | None
    highlight: bool | None
    width: int | None
    height: int | None
    crop: bool
    soft_wrap: bool | None
    new_line_start: bool


PathType = Annotated[Literal["file", "dir"], "Type of a path"]
