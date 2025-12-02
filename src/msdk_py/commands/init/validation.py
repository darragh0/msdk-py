from __future__ import annotations

from typing import TYPE_CHECKING

from msdk_py.commands.init.defaults import DEFAULT_BSP
from msdk_py.common.error import ValidationError
from msdk_py.common.validation import ensure_conventional_path_name, ensure_exists

if TYPE_CHECKING:
    from pathlib import Path


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

    # If "32655" instead of "MAX32655"
    if target.isdigit():
        target = f"MAX{target}"

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

    # If "32655" instead of "MAX32655"
    if target.isdigit():
        target = f"MAX{target}"

    bsp_dir = target_bsp_dir / bsp
    try:
        ensure_exists(
            bsp_dir,
            f"board support package [path]{bsp}[/] for [value]{target}[/]",
            check4similar=None if bsp == DEFAULT_BSP else target_bsp_dir,
            path_type="dir",
        )
    except ValidationError as e:
        available = [d.name for d in target_bsp_dir.iterdir() if d.is_dir()]
        msg = f"{e}\n\n[note]note:[/] available BSPs: {', '.join(sorted(available))}"
        raise ValidationError(msg) from e


def validate_proj_name(name: str, parent_dir: Path, *, allow_cwd: bool) -> None:
    """Validate project name is valid and doesn't exist.

    Args:
        name (str): Project name to validate
        parent_dir (Path): Parent directory of project

    Keyword Arguments:
        allow_cwd: Allow project name to be current working directory (when name = ".")

    Raises:
        ValidationError: If project name is invalid or already exists
    """

    is_cwd = name.strip() == "."
    if not is_cwd:
        ensure_conventional_path_name(name, desc="project", is_dir=True)
    elif not allow_cwd:
        msg = (
            "cannot create project in: [value].[/]\n\n[note]note:[/] project name cannot "
            "be current working directory (use [var]--allow-cwd[/] to allow this)"
        )
        raise ValidationError(msg)
    else:
        return

    proj_path = parent_dir / name
    if proj_path.exists():
        msg = (
            f"directory already exists: [path]{proj_path}[/]\n\n"
            "[tip]tip:[/] choose a different name or remove the existing directory"
        )
        raise ValidationError(msg)
