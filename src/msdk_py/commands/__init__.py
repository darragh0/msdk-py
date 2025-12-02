from __future__ import annotations

from typing import TYPE_CHECKING, Final

from .init import InitCommand

if TYPE_CHECKING:
    from .init import BaseCommand


COMMANDS: Final[list[type[BaseCommand]]] = [InitCommand]

__all__ = ["COMMANDS"]
