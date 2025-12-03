"""build -- Build MSDK project using MaximSDK GCC toolchain."""

from __future__ import annotations

from typing import TYPE_CHECKING, override

from msdk_py.commands.base import BaseCommand
from msdk_py.common.build import build_project

if TYPE_CHECKING:
    from argparse import ArgumentParser, Namespace


class BuildCommand(BaseCommand):
    """Build MSDK project."""

    name = "build"
    help = "Build MSDK project."
    aliases = ("b",)

    @override
    def configure_parser(self, parser: ArgumentParser) -> None:
        out_help = "Output [italic].elf[/] file (default: [cyan]$PROJECT_NAME[/])"
        parser.add_argument("-o", "--out", help=out_help, default=None, metavar="OUT")

    @override
    def execute(self, args: Namespace) -> None:
        build_project(project_name=args.out)
