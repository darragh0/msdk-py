"""init -- create MSDK project"""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING, override

from msdk_py.commands.base import BaseCommand
from msdk_py.commands.init.validation import validate_bsp, validate_proj_name, validate_target
from msdk_py.common.display import cout
from msdk_py.common.validation import validate_maxim_path

from .defaults import DEFAULT_BSP, DEFAULT_TEMPLATE
from .generate import gen_proj

if TYPE_CHECKING:
    from argparse import ArgumentParser, Namespace


class InitCommand(BaseCommand):
    """Initialize MSDK project from SDK example."""

    name = "init"
    help = "Initialize new MSDK project"
    aliases = ("new",)

    @override
    def configure_parser(self, parser: ArgumentParser) -> None:
        arg = parser.add_argument
        arg("project_name", help="Name of the project to create")

        target_help = "Target board ([italic]MAX32655, MAX32690[/], ...)"
        arg("-t", "--target", required=True, help=target_help, metavar="TGT")

        bsp_help = f"Board support package (default: [italic]{DEFAULT_BSP}[/])"
        arg("-b", "--bsp", help=bsp_help, default=DEFAULT_BSP, metavar="BSP")

        template_help = (
            "Template (example) name from SDK (e.g., [italic]Hello_World, "
            f"GPIO, I2C[/]) (default: [italic]{DEFAULT_TEMPLATE})[/]"
        )
        arg("--template", help=template_help, default=DEFAULT_TEMPLATE, metavar="TEM")

        arg("--no-vscode", action="store_false", help="Don't include VSCode configuration", dest="include_vscode")
        arg("--no-readme", action="store_false", help="Don't create [file]README.md[/]", dest="include_readme")
        arg("--no-git", action="store_false", help="Don't initialize git repository", dest="init_git")
        arg(
            "--reinit-git",
            action="store_true",
            help="Reinitialize existing git repository if it exists",
            dest="reinit_git",
        )
        arg(
            "--allow-cwd",
            action="store_true",
            help="Allow project to be created in current directory",
            dest="allow_cwd",
        )

    @override
    def execute(self, args: Namespace) -> None:
        target = args.target.upper()
        if target.isdigit():
            target = f"MAX{target}"

        maxim_path = validate_maxim_path()
        validate_target(target, maxim_path)
        validate_bsp(target, args.bsp, maxim_path)

        proj_name = args.project_name.strip()
        validate_proj_name(proj_name, Path.cwd(), allow_cwd=args.allow_cwd)

        proj_dir = Path.cwd() / proj_name
        gen_proj(
            maxim_path=maxim_path,
            output_dir=proj_dir,
            target=target,
            bsp=args.bsp,
            template=args.template,
            include_vscode=args.include_vscode,
            include_readme=args.include_readme,
            init_git=args.init_git,
            reinit_git=args.reinit_git,
        )

        cout(f"Initialized project [proj]{args.project_name}[/] at [path]{proj_dir}[/]")
