"""clean -- Clean MSDK project build artifacts."""

from __future__ import annotations

from typing import TYPE_CHECKING, override

from msdk_py.commands.base import BaseCommand
from msdk_py.common.utils import run_trusted_cmd
from msdk_py.common.validation import ensure_proj_dir

if TYPE_CHECKING:
    from argparse import ArgumentParser, Namespace


class CleanCommand(BaseCommand):
    """Clean MSDK project build artifacts."""

    name = "clean"
    help = "Clean build artifacts"
    aliases = ("c",)

    @override
    def configure_parser(self, parser: ArgumentParser) -> None:
        _ = parser

    @override
    def execute(self, args: Namespace) -> None:
        _ = args
        ensure_proj_dir()
        run_trusted_cmd(["make", "clean"])
