"""flash -- Flash MSDK project to device using GDB and OpenOCD."""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING, override

from msdk_py.commands.base import BaseCommand
from msdk_py.common.build import build_project
from msdk_py.common.display import cout
from msdk_py.common.error import ValidationError
from msdk_py.common.toml_config import load_flash_config
from msdk_py.common.utils import find_maxim_toolchain, get_ocd_bin, run_trusted_cmd
from msdk_py.common.validation import ensure_proj_dir, validate_maxim_path

if TYPE_CHECKING:
    from argparse import ArgumentParser, Namespace

    from msdk_py.common.toml_config import FlashConfig


def _validate_build_file(path: Path, file_type: str) -> None:
    """Validate that a build artifact exists.

    Args:
        path: Path to file
        file_type: Description (e.g., "program", "symbol")

    Raises:
        ValidationError: If file doesn't exist
    """
    if not path.exists():
        msg = (
            f"{file_type} file not found: [path]{path}[/]\n\n"
            "[tip]tip:[/] run [var]msdk build[/] first or use "
            "[var]msdk flash[/] without [var]--skip-build[/]"
        )
        raise ValidationError(msg)


def _flash_device(config: FlashConfig, *, run: bool = False) -> None:
    """Flash (and optionally run) device using GDB.

    Args:
        config: Flash configuration
        run: If True, use flash_m4_run (resume), else flash_m4 (halt)

    Raises:
        ValidationError: If program or symbol file not found
        CannotProceedError: If GDB command fails
    """
    # Validate build artifacts exist
    program_path = Path.cwd() / "build" / config.program_file
    symbol_path = Path.cwd() / "build" / config.symbol_file

    _validate_build_file(program_path, "program")
    _validate_build_file(symbol_path, "symbol")

    # Build GDB command
    gdb_func = "flash_m4_run" if run else "flash_m4"

    cmd = [
        "arm-none-eabi-gdb",
        f"--cd={Path.cwd()}",
        f"--se={program_path}",
        f"--symbols={symbol_path}",
        f"-x={config.gdb_script}",
        f"--ex={gdb_func} {config.ocd_path} {config.interface_file} {config.target_file}",
        "--batch",
    ]

    # Get toolchain and run
    maxim_path = validate_maxim_path()
    toolchain_bin = str(find_maxim_toolchain(maxim_path))
    ocd_bin = str(get_ocd_bin(config.ocd_path))

    action = "flashing and running" if run else "flashing"
    cout(f"[success]•[/] {action} [proj]{config.project_name}[/]...")
    run_trusted_cmd(cmd, add2path=[toolchain_bin, ocd_bin])


class FlashCommand(BaseCommand):
    """Build & flash project to device."""

    name = "flash"
    help = "Build & flash project to device."
    aliases = ("f",)

    @override
    def configure_parser(self, parser: ArgumentParser) -> None:
        parser.add_argument(
            "--skip-build",
            action="store_true",
            help="Skip build step, flash existing binary",
        )

    @override
    def execute(self, args: Namespace) -> None:
        ensure_proj_dir()

        if not args.skip_build:
            build_project()

        config = load_flash_config()
        _flash_device(config)
