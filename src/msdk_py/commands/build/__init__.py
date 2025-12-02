"""build -- Build MSDK project using MaximSDK GCC toolchain."""

from __future__ import annotations

from typing import TYPE_CHECKING, override

from msdk_py.commands.base import BaseCommand
from msdk_py.common.utils import find_maxim_toolchain, run_trusted_cmd
from msdk_py.common.validation import ensure_conventional_path_name, ensure_proj_dir, validate_maxim_path

if TYPE_CHECKING:
    from argparse import ArgumentParser, Namespace


class BuildCommand(BaseCommand):
    """Build MSDK project."""

    name = "build"
    help = "Build MSDK project"
    aliases = ("b",)

    @override
    def configure_parser(self, parser: ArgumentParser) -> None:
        out_help = "Output [italic].elf[/] file (default: [cyan]$PROJECT_NAME[/])"
        parser.add_argument("-o", "--out", help=out_help, default=None, metavar="OUT")

    @override
    def execute(self, args: Namespace) -> None:
        # TODO: Only support building projects in cwd for now -- update to support any valid proj dir
        ensure_proj_dir()
        maxim_path = validate_maxim_path()

        project_str: str
        if args.out is None or args.out.strip() != ".":
            project_str = ""  # Excluded -- make falls back to whatever is in project.mk
        else:
            ensure_conventional_path_name(args.out, desc="project", is_dir=True)
            project_str = f" PROJECT={args.out}"

        cmd = ["make", "-r", "-j", "8", "--output-sync=target", "--no-print-directory", project_str]
        toolchain_bin = str(find_maxim_toolchain(maxim_path))
        run_trusted_cmd(cmd, add2path=[toolchain_bin])
