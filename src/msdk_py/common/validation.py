from __future__ import annotations

from os import environ
from pathlib import Path
from typing import TYPE_CHECKING

from .error import ValidationError

if TYPE_CHECKING:
    from .types import PathType


def ensure_exists(
    path: Path,
    description: str,
    *,
    path_type: PathType | None = None,
    check4similar: Path | None = None,
) -> None:
    """Ensure path exists.

    Args:
        path: Path to validate
        description: Short description of path to validate

    Optional Keyword Args:
        path_type: Type of path to validate ("file" | "dir")
        check4similar: Path to check for similarly-named paths (for adding tip to error message)

    Raises:
        ValidationError: If path does not exist
    """
    pred, label = (
        (Path.is_dir, "directory")
        if path_type == "dir"
        else (Path.is_file, "file")
        if path_type == "file"
        else (lambda _: True, None)
    )

    exists = path.exists()
    if exists and pred(path):
        return

    msg = (
        f"{description} not found: [path]{path}[/]"
        if not exists
        else f"{description} is not a {label}: [path]{path}[/]"
    )

    if check4similar is not None:
        for d in check4similar.iterdir():
            if pred(d):
                dir_lower = d.name.lower()
                path_lower = path.name.lower()

                if dir_lower == path_lower or dir_lower in path_lower or path_lower in dir_lower:
                    msg += f"\n\n[tip]tip:[/] did you mean [path]{d.name}[/]?"
                    # break at first similar
                    break

    raise ValidationError(msg)


def ensure_env_var(var_name: str, *, tip: str | None = None) -> str:
    """Ensure environment variable is set.

    Args:
        var_name: Name of environment variable to validate

    Optional Keyword Args:
        tip: Tip/hint to display if variable is not set

    Returns:
        str: Value of environment variable

    Raises:
        ValidationError: If environment variable is not set
    """

    value = environ.get(var_name)
    if value is None:
        msg = f"[var]{var_name}[/] environment variable not set"
        if tip is not None:
            msg += f"\n\n[tip]tip:[/] {tip}"
        raise ValidationError(msg)

    return value


def validate_maxim_path() -> Path:
    """Validate MAXIM_PATH environment variable.

    Returns:
        Path: Path to MaximSDK installation

    Raises:
        ValidationError: If MAXIM_PATH is not set
    """

    env_tip = (
        "set it to your MaximSDK installation directory (ideally in [file].bashrc[/] or [file].zshrc[/])\n"
        "  E.g. -> 'export MAXIM_PATH=\"$HOME/MaximSDK\"' >> [path]$HOME/.bashrc[/] "
        "&& [magenta]source[/] [path]$HOME/.bashrc[/]"
    )

    maxpath = Path(ensure_env_var("MAXIM_PATH", tip=env_tip))
    ensure_exists(maxpath, "[var]MAXIM_PATH[/]", path_type="dir")

    try:
        ensure_exists(maxpath / "Examples", "Examples directory", path_type="dir")
    except ValidationError as e:
        msg = f"[note]note:[/] [var]MAXIM_PATH[/] does not appear to be a valid MaximSDK installation\n\n{e}"
        raise ValidationError(msg) from e

    return maxpath
