from __future__ import annotations

from pathlib import Path

from msdk_py.commands.init.defaults import DEFAULT_BSP
from msdk_py.common.error import ValidationError
from msdk_py.common.utils import normalize_target
from msdk_py.common.validation import ensure_exists


def validate_target(target: str, maxim_path: Path) -> None:
    """Validate target exists in Examples directory.

    Args:
        target (str): Target to validate
        maxim_path (Path): Path to MaximSDK installation

    Raises:
        ValidationError: If target does not exist in Examples directory
    """

    examples_dir = maxim_path / "Examples"
    ensure_exists(examples_dir, "MaximSDK Examples directory", path_type="dir")

    target = normalize_target(target)
    target_dir = examples_dir / target
    if not target_dir.exists():
        available = [d.name for d in examples_dir.iterdir() if d.is_dir()]
        msg = (
            f"target [error]{target}[/] not found in [path]$MAXIM_PATH/Examples/[/]\n\n"
            f"[note]note:[/] available targets: {', '.join(sorted(available))}"
        )
        raise ValidationError(msg)


def validate_bsp(target: str, bsp: str, maxim_path: Path) -> None:
    """Validate board support package directory exists.

    Args:
        target (str): Target to validate
        bsp (str): Board support package to validate
        maxim_path (Path): Path to MaximSDK installation

    Raises:
        ValidationError: If board support package directory does not exist
    """

    base_bsp_dir = maxim_path / "Libraries" / "Boards"
    ensure_exists(base_bsp_dir, "MaximSDK BSP libraries directory", path_type="dir")

    target_bsp_dir = maxim_path / "Libraries" / "Boards" / target
    ensure_exists(target_bsp_dir, f"MaximSDK BSP libraries directory for [value]{target}[/]", path_type="dir")

    bsp_dir = target_bsp_dir / bsp
    check4similar = target_bsp_dir if bsp != DEFAULT_BSP else None
    try:
        ensure_exists(
            bsp_dir,
            f"board support package [path]{bsp}[/] for [value]{target}[/]",
            check4similar=check4similar,
            path_type="dir",
        )
    except ValidationError as e:
        available = [d.name for d in target_bsp_dir.iterdir() if d.is_dir()]
        msg = f"{e}\n\n[note]note:[/] available BSPs: {', '.join(sorted(available))}"
        raise ValidationError(msg) from e


def validate_proj_name(name: str, parent_dir: Path) -> None:
    """Validate project name is valid and doesn't already exist.

    Args:
        name: Project basename
        parent_dir: Parent directory for project

    Raises:
        ValidationError: If project name is invalid or already exists
    """
    # Check if empty
    if not name or name.strip() == "":
        msg = "project name cannot be empty"
        raise ValidationError(msg)

    # Check if parent exists
    if not parent_dir.exists():
        msg = (
            f"parent directory does not exist: [path]{parent_dir}[/]\n\n"
            "[tip]tip:[/] create parent directories first or use a different path"
        )
        raise ValidationError(msg)

    # Check if project already exists
    proj_path = parent_dir / name

    if proj_path.exists() and proj_path.is_file():
        msg = (
            f"[path]{proj_path}[/] is a file, not a directory\n\n"
            "[tip]tip:[/] choose a different name"
        )
        raise ValidationError(msg)

    # Allow existing directories (including cwd)
    # The project config file check will catch re-initialization attempts
