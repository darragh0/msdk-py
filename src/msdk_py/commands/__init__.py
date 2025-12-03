from __future__ import annotations

from typing import TYPE_CHECKING, Final

from .build import BuildCommand
from .clean import CleanCommand
from .clean_periph import CleanPeriphCommand
from .flash import FlashCommand
from .init import InitCommand
from .run import RunCommand

if TYPE_CHECKING:
    from .init import BaseCommand


COMMANDS: Final[list[type[BaseCommand]]] = [
    InitCommand,
    BuildCommand,
    CleanCommand,
    CleanPeriphCommand,
    FlashCommand,
    RunCommand,
]

__all__ = ["COMMANDS"]
