"""run -- Build, flash, and run MSDK project on device."""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING, override

from msdk_py.commands.base import BaseCommand
from msdk_py.commands.flash import _flash_device
from msdk_py.common.build import build_project
from msdk_py.common.toml_config import load_flash_config
from msdk_py.common.validation import ensure_proj_dir

if TYPE_CHECKING:
    from argparse import ArgumentParser, Namespace


class RunCommand(BaseCommand):
    """Build, flash, and run project on device."""

    name = "run"
    help = "Build, flash, and run project on device"
    aliases = ("r",)

    @override
    def configure_parser(self, parser: ArgumentParser) -> None:
        parser.add_argument(
            "--skip-build",
            action="store_true",
            help="Skip build step",
        )
        parser.add_argument(
            "--skip-flash",
            action="store_true",
            help="Skip flash step (only run)",
        )

    @override
    def execute(self, args: Namespace) -> None:
        ensure_proj_dir()

        config = load_flash_config()
        elf_path = Path.cwd() / "build" / config.program_file

        need_flash = not args.skip_flash

        if not args.skip_build:
            # Check if .elf was modified during build
            elf_modified = build_project(check_modified=True, elf_path=elf_path)
            if elf_modified:
                need_flash = True

        # Flash if needed (with halt)
        if need_flash:
            _flash_device(config, run=False)

        # Run (with resume)
        _flash_device(config, run=True)
