import subprocess as sproc
import threading
from os import environ
from pathlib import Path
from typing import TextIO

from rich.console import Console
from rich.text import Text

from msdk_py.common.error import CannotProceedError, MissingToolError
from msdk_py.common.validation import ensure_exists

from .display import cout

console = Console()


def dir_is_empty(path: Path) -> bool:
    """Check if a directory is empty.

    Args:
        path: Directory to check

    Returns:
        True if directory is empty else False
    """
    return any(path.iterdir())


def find_maxim_toolchain(maxim_path: Path) -> Path:
    """Auto-detect MaximSDK ARM GCC toolchain path.

    Args:
        maxim_path: Path to MaximSDK installation

    Returns:
        Path to toolchain bin directory, or None if not found

    Raises:
        MissingToolError: If toolchain (or missing toolchain versions) not found
    """

    gnu_tools = maxim_path / "Tools" / "GNUTools"
    ensure_exists(gnu_tools, "MaximSDK toolchain directory", path_type="dir")

    versions = [d for d in gnu_tools.iterdir() if d.is_dir() and d.name[0].isdigit()]
    if not versions:
        msg = f"cannot find any MaximSDK toolchain versions in [path]{gnu_tools}[/]"
        raise MissingToolError(msg)

    # Sort by version -- latest last (simple lexicographic works for most cases)
    versions.sort(key=lambda p: [int(x) for x in p.name.split(".")])
    toolchain_bin = versions[-1] / "bin"

    ensure_exists(toolchain_bin, "MaximSDK toolchain bin directory", path_type="dir")
    return toolchain_bin


def _out_stream(pipe: TextIO, style: str) -> None:
    for line in iter(pipe.readline, ""):
        cout(Text("  |  " + line.rstrip(), style=style))
    pipe.close()


def run_trusted_cmd(cmd: list[str], *, add2path: list[str] | None = None) -> None:
    """Run a (trusted) command, redirecting stdout & stderr to the console

    Args:
        cmd: Command to run

    Optional Keyword Args:
        add2path: Optional additional PATH entries

    Raises
        CannotProceedError: If the command fails (exits with non-zero error code)
    """
    env: dict[str, str] | None
    if add2path is not None:
        env = environ.copy()
        env["PATH"] = f"{':'.join(add2path)}:{env['PATH']}"  # Matches left-to-right, so add to left
    else:
        env = None

    cout(f"[success]Running command:[/] [bright_white]{' '.join(cmd)}[/]\n[dim]  |[/]")

    proc = sproc.Popen(cmd, stdout=sproc.PIPE, stderr=sproc.PIPE, text=True, env=env)  # noqa: S603

    t_out = threading.Thread(target=_out_stream, args=(proc.stdout, "dim"))
    t_err = threading.Thread(target=_out_stream, args=(proc.stderr, "dim red"))

    t_out.start()
    t_err.start()
    t_out.join()
    t_err.join()

    cout("  [dim]|[/]")
    if (errno := proc.wait()) != 0:
        msg = f"command returned non-zero exit code: {errno}"
        raise CannotProceedError(msg)

    cout("[success]Command succeeded[/]")
