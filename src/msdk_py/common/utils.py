from pathlib import Path

from .error import ValidationError


def ensure_proj_dir() -> None:
    """
    Ensure cwd is the project directory (with `.msdk-py-proj` marker file).

    Raises:
        ValidationError: If cwd is not the project directory
    """

    cwd = Path.cwd()
    if not (cwd / ".msdk-py-proj").is_file():
        msg = (
            f"current directory is not a msdk-py project directory: [path]{cwd}[/]\n\n"
            "[tip]tip:[/] run [command]msdk init[/] to create a new project in the current directory"
        )
        raise ValidationError(msg)
