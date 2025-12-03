"""Shared build logic for MSDK projects."""

from __future__ import annotations

from typing import TYPE_CHECKING

from msdk_py.common.utils import find_maxim_toolchain, run_trusted_cmd
from msdk_py.common.validation import ensure_proj_dir, validate_maxim_path

if TYPE_CHECKING:
    from pathlib import Path


def build_project(
    project_name: str | None = None,
    *,
    check_modified: bool = False,
    elf_path: Path | None = None,
) -> bool:
    """Build MSDK project.

    Args:
        project_name: Optional project name override (for PROJECT= in make)

    Keyword Args:
        check_modified: If True, check if .elf was modified
        elf_path: Path to .elf file to check (required if check_modified=True)

    Returns:
        bool: True if check_modified=True and .elf was modified, else False

    Raises:
        ValidationError: If not in project directory or invalid project name
        MissingToolError: If toolchain not found
        CannotProceedError: If build fails
    """
    ensure_proj_dir()
    maxim_path = validate_maxim_path()

    # Get mtime before build if checking for modifications
    mtime_before = 0.0
    if check_modified and elf_path is not None:
        mtime_before = elf_path.stat().st_mtime if elf_path.exists() else 0.0

    # Build project string for make
    project_str = (
        ""  # Excluded -- make falls back to whatever is in project.mk
        if project_name is None or project_name.strip() == "."
        else f" PROJECT={project_name}"
    )

    cmd = ["make", "-r", "-j", "8", "--output-sync=target", "--no-print-directory", project_str]
    toolchain_bin = str(find_maxim_toolchain(maxim_path))
    run_trusted_cmd(cmd, add2path=[toolchain_bin])

    # Check if elf was modified
    if check_modified and elf_path is not None:
        if not elf_path.exists():
            return False
        mtime_after = elf_path.stat().st_mtime
        return mtime_after > mtime_before

    return False
