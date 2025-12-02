from __future__ import annotations

from typing import TYPE_CHECKING, Final

from .build import BuildCommand
from .clean import CleanCommand
from .clean_periph import CleanPeriphCommand
from .init import InitCommand

if TYPE_CHECKING:
    from .init import BaseCommand


COMMANDS: Final[list[type[BaseCommand]]] = [InitCommand, BuildCommand, CleanCommand, CleanPeriphCommand]

__all__ = ["COMMANDS"]
