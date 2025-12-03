"""TOML configuration handling for msdk-py projects."""

from __future__ import annotations

import tomllib
from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING

import tomli_w

from msdk_py.common.error import CannotProceedError, ValidationError
from msdk_py.common.validation import validate_maxim_path

if TYPE_CHECKING:
    from typing import Any


@dataclass
class FlashConfig:
    """Flash configuration from TOML."""

    target: str
    board: str
    project_name: str
    program_file: str
    symbol_file: str
    interface_file: str
    target_file: str
    gdb_script: Path
    ocd_path: Path


def _validate_toml_sections(data: dict[str, Any]) -> None:
    """Validate required sections exist in TOML data.

    Args:
        data: TOML data dictionary

    Raises:
        ValidationError: If required sections missing
    """
    required_sections = ["project", "flash"]
    for section in required_sections:
        if section not in data:
            msg = f"missing required section in [path]msdk-proj.toml[/]: [{section}]"
            raise ValidationError(msg)


def _validate_toml_fields(data: dict[str, Any]) -> None:
    """Validate required fields exist in TOML data.

    Args:
        data: TOML data dictionary

    Raises:
        ValidationError: If required fields missing
    """
    required_fields = {
        "project": ["target", "board", "name"],
        "flash": ["program_file", "symbol_file", "interface_file", "target_file", "gdb_script"],
    }

    for section, fields in required_fields.items():
        section_data = data[section]
        for field in fields:
            if field not in section_data or not section_data[field]:
                msg = f"missing required field in [path]msdk-proj.toml[/]: [{section}].{field}"
                raise ValidationError(msg)


def _resolve_ocd_path(paths: dict[str, Any]) -> Path:
    """Resolve OpenOCD path from TOML or MAXIM_PATH.

    Args:
        paths: Paths section from TOML

    Returns:
        Path: Resolved OpenOCD path

    Raises:
        ValidationError: If OpenOCD path not found
    """
    ocd_path_str = paths.get("ocd_path", "")
    if ocd_path_str:
        ocd_path = Path(ocd_path_str)
    else:
        maxim_path = validate_maxim_path()
        ocd_path = maxim_path / "Tools" / "OpenOCD"

    if not ocd_path.exists():
        msg = (
            f"OpenOCD tools directory not found: [path]{ocd_path}[/]\n\n"
            "[tip]tip:[/] ensure [var]MAXIM_PATH[/] is set correctly and points to a valid MaximSDK installation"
        )
        raise ValidationError(msg)

    return ocd_path


def load_flash_config() -> FlashConfig:
    """Load and validate flash config from msdk-proj.toml in cwd.

    Returns:
        FlashConfig: Validated flash configuration

    Raises:
        ValidationError: If TOML missing, invalid, or required fields missing
    """
    toml_path = Path.cwd() / "msdk-proj.toml"

    # Validate TOML exists
    if not toml_path.exists():
        msg = (
            "project configuration not found: [path]msdk-proj.toml[/]\n\n"
            "[tip]tip:[/] run [var]msdk init . --allow-cwd[/] to reinitialize project configuration"
        )
        raise ValidationError(msg)

    # Parse TOML
    try:
        with toml_path.open("rb") as f:
            data = tomllib.load(f)
    except tomllib.TOMLDecodeError as e:
        msg = (
            f"invalid project configuration: [path]msdk-proj.toml[/]\n  {e}\n\n"
            "[tip]tip:[/] check TOML syntax or regenerate with [var]msdk init . --allow-cwd[/]"
        )
        raise ValidationError(msg) from e

    # Validate structure
    _validate_toml_sections(data)
    _validate_toml_fields(data)

    # Extract sections
    project = data["project"]
    flash = data["flash"]
    paths = data.get("paths", {})

    # Resolve GDB script path
    gdb_script = Path.cwd() / flash["gdb_script"]
    if not gdb_script.exists():
        msg = (
            f"GDB flash script not found: [path]{gdb_script}[/]\n\n"
            "[tip]tip:[/] this file should have been copied during [var]msdk init[/]\n"
            f"  you can find it in [path]$MAXIM_PATH/Examples/{project['target']}/{{TEMPLATE}}/.vscode/flash.gdb[/]"
        )
        raise ValidationError(msg)

    # Resolve OCD path
    ocd_path = _resolve_ocd_path(paths)

    return FlashConfig(
        target=project["target"],
        board=project["board"],
        project_name=project["name"],
        program_file=flash["program_file"],
        symbol_file=flash["symbol_file"],
        interface_file=flash["interface_file"],
        target_file=flash["target_file"],
        gdb_script=gdb_script,
        ocd_path=ocd_path,
    )


def extract_flash_config_from_vscode(settings: dict[str, Any], project_name: str) -> dict[str, str]:
    """Extract and resolve flash-related fields from VSCode settings.json.

    Args:
        settings: VSCode settings dictionary
        project_name: Project name to use for variable resolution

    Returns:
        dict: Extracted flash configuration values
    """
    # Resolve ${config:project_name} references
    program_file = settings.get("program_file", f"{project_name}.elf")
    program_file = program_file.replace("${config:project_name}", project_name)

    # Resolve ${config:program_file} references in symbol_file
    symbol_file = settings.get("symbol_file", program_file)
    symbol_file = symbol_file.replace("${config:program_file}", program_file)
    symbol_file = symbol_file.replace("${config:project_name}", project_name)

    return {
        "target": settings.get("target", ""),
        "board": settings.get("board", ""),
        "program_file": program_file,
        "symbol_file": symbol_file,
        "interface_file": settings.get("M4_OCD_interface_file", "cmsis-dap.cfg"),
        "target_file": settings.get("M4_OCD_target_file", ""),
    }


def write_project_config(
    output_dir: Path,
    target: str,
    board: str,
    project_name: str,
    settings_json: dict[str, Any],
) -> None:
    """Generate msdk-proj.toml from VSCode settings during init.

    Args:
        output_dir: Project output directory
        target: Target device (e.g., 'MAX32655')
        board: Board/BSP name (e.g., 'EvKit_V1')
        project_name: Project name
        settings_json: VSCode settings.json content
    """
    flash_config = extract_flash_config_from_vscode(settings_json, project_name)

    toml_data = {
        "project": {
            "target": target,
            "board": board,
            "name": project_name,
        },
        "flash": {
            "program_file": flash_config["program_file"],
            "symbol_file": flash_config["symbol_file"],
            "interface_file": flash_config["interface_file"],
            "target_file": flash_config["target_file"],
            "gdb_script": ".vscode/flash.gdb",
        },
        "paths": {
            "ocd_path": "",  # Empty means auto-detect from MAXIM_PATH
        },
    }

    toml_path = output_dir / "msdk-proj.toml"

    # Check if config already exists (prevents re-initialization)
    if toml_path.exists():
        msg = (
            "cannot initialize project: [path]msdk-proj.toml[/] already exists\n\n"
            "[tip]tip:[/] this directory is already an MSDK project"
        )
        raise CannotProceedError(msg)

    with toml_path.open("wb") as f:
        tomli_w.dump(toml_data, f)
