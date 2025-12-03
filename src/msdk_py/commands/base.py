from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, ClassVar

if TYPE_CHECKING:
    from argparse import ArgumentParser, Namespace


class BaseCommand(ABC):
    """ABC defining the interface for msdk-py commands.

    Commands must implement this to be registered with the CLI.

    Attributes:
        name: The name of the command
        help: Help text for the command
        aliases: Optional tuple of alias names
    """

    __slots__ = ()

    name: ClassVar[str]
    help: ClassVar[str]
    aliases: ClassVar[tuple[str, ...] | None] = None
    has_pos_args: ClassVar[bool] = False

    @abstractmethod
    def configure_parser(self, parser: ArgumentParser) -> None:
        """Configure the argument parser for this command.

        Args:
            parser: ArgumentParser instance to configure with command-specific arguments
        """
        ...

    @abstractmethod
    def execute(self, args: Namespace) -> None:
        """Execute (run) the command.

        Args:
            args: Parsed command-line arguments

        Raises:
            MsdkError: If the command fails
        """
        ...
