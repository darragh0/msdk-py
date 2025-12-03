from __future__ import annotations

import json
import shutil
import subprocess as subproc
from pathlib import Path

from msdk_py.common.error import CannotProceedError, MissingToolError, MsdkError, ValidationError
from msdk_py.common.toml_config import write_project_config
from msdk_py.common.utils import dir_is_empty
from msdk_py.common.validation import ensure_exists


def _ensure_template_files_exist(maxim_path: Path, target: str, template: str) -> Path:
    """Ensure template (example) directory exists and has the required files.

    Args:
        maxim_path: Path to MaximSDK installation
        target: Target to validate (e.g., 'MAX32655')
        template: Template to validate (e.g., 'Hello_World')

    Returns:
        Path: Path to template directory

    Raises:
        ValidationError: If template does not exist
    """

    all_templates_dir = maxim_path / "Examples" / target
    template_dir = maxim_path / "Examples" / target / template

    ensure_exists(template_dir, f"template [path]{template}[/] for [value]{target}[/]", check4similar=all_templates_dir)
    ensure_exists(template_dir / "Makefile", "template [path]Makefile[/]")
    ensure_exists(template_dir / "main.c", "template [path]main.c[/]")
    ensure_exists(template_dir / "project.mk", "template [path]project.mk[/]")

    return template_dir


def _copy_template_files(
    template_dir: Path,
    output_dir: Path,
    *,
    target: str,
    bsp: str,
    include_vscode: bool,
    is_cwd: bool,
    with_git: bool,
) -> None:
    """Copy files from template (example) directory to output directory.

    Args:
        template_dir: Path to template directory
        output_dir: Path to output directory

    Keyword Arguments:
        target: Target (e.g., 'MAX32655')
        bsp: Board support package to use (e.g., 'EvKit_V1')
        include_vscode: Include VSCode configuration
        is_cwd: Template files to be copied to current directory
        with_git: Whether to add `.gitkeep` file to new `/include` dir

    Raises:
        ValidationError: If example does not exist
    """

    if not is_cwd:
        output_dir.mkdir(parents=True)

    inc_out = output_dir / "include"
    src_out = output_dir / "src"
    inc_out.mkdir(exist_ok=True)
    src_out.mkdir(exist_ok=True)

    tem_srcs = (template_dir / f for f in ("Makefile", "main.c", "project.mk"))
    out_dests = (output_dir / f for f in ("Makefile", "src/main.c", "project.mk"))

    project_mk_copied = False
    for tem_src, out_dest in zip(tem_srcs, out_dests, strict=True):
        if not out_dest.exists():
            shutil.copy2(tem_src, out_dest)
            if out_dest.name == "project.mk":
                project_mk_copied = True

    # check if with git and also if inc_out is empty
    if with_git and dir_is_empty(inc_out):
        (inc_out / ".gitkeep").touch()

    if project_mk_copied:
        mk_out = output_dir / "project.mk"
        mk_out_lines = mk_out.read_text().splitlines()[:-1]  # Exclude "# Add your config here!" line
        mk_out_lines.extend(
            [
                f"PROJECT={output_dir.resolve().name}",
                f"BOARD={bsp}",
                f"TARGET={target}\n",
                "# Add any additional configs here!\n",
            ]
        )
        mk_out.write_text("\n".join(mk_out_lines))

    if include_vscode:
        vscode_src = template_dir / ".vscode"
        vscout_out = output_dir / ".vscode"
        if not vscout_out.exists():
            shutil.copytree(vscode_src, vscout_out)
            _update_vscode_bsp(vscout_out, bsp)

    # Generate TOML config from template's VSCode settings
    settings_path = template_dir / ".vscode" / "settings.json"
    if settings_path.exists():
        with settings_path.open() as f:
            settings = json.load(f)

        write_project_config(
            output_dir=output_dir,
            target=target,
            board=bsp,
            project_name=output_dir.resolve().name,
            settings_json=settings,
        )


def _update_vscode_bsp(vscode_dir: Path, bsp: str) -> None:
    """Update board (bsp) field in `.vscode/settings.json`.

    Args:
        vscode_dir: Path to `.vscode` directory
        board: Board to update (e.g., 'EvKit_V1')

    Raises:
        ValidationError: If settings file does not exist
    """

    settings_file = vscode_dir / "settings.json"
    ensure_exists(settings_file, "template [path].vscode/settings.json[/]")

    with settings_file.open() as f:
        settings = json.load(f)

    settings["board"] = bsp

    with settings_file.open("w") as f:
        json.dump(settings, f, indent=4)


def _write_git_ignore(output_dir: Path, *, vscode: bool) -> None:
    """Write `.gitignore` file in output directory.

    Args:
        output_dir: Path to output directory

    Keyword Arguments:
        vscode: Whether to add VSCode dir to `.gitignore`
    """

    new_cont = f"build/\ncompile_flags.txt\n*.log\n*.old\n{'.vscode\n' if vscode else ''}"
    out_gitig = output_dir / ".gitignore"

    if out_gitig.is_dir():
        # Don't try to init anything cos the person's weird
        return

    cont = f"{'' if not out_gitig.is_file() else out_gitig.read_text()}\n{new_cont}"
    (output_dir / ".gitignore").write_text(cont)


def _init_git(output_dir: Path, *, is_cwd: bool) -> None:
    """Initialize git repository in output directory.

    Args:
        output_dir: Path to output directory

    Keyword Args:
        is_cwd: Whether output directory is current working directory

    Raises:
        MissingToolError: If git is not installed
        CannotProceedError: If git repository already exists
    """

    out_git = output_dir / ".git"
    if is_cwd and out_git.exists():
        return

    if out_git.is_file():
        msg = "cannot initialize git repository: invalid [path].git[/] file exists"
        raise CannotProceedError(msg)

    if out_git.is_dir():
        msg = "cannot initialize git repository: [path].git[/] directory exists"
        raise CannotProceedError(msg)

    if (gitpath := shutil.which("git")) is not None:
        try:
            _ = subproc.run(  # noqa: S603
                [gitpath, "init"],
                check=True,
                cwd=str(output_dir),
                capture_output=True,
            )
        except subproc.CalledProcessError as e:
            msg = "cannot initialize git repository: [var]git init[/] failed"
            raise CannotProceedError(msg) from e
    else:
        msg = "cannot initialize git repository: [var]git[/] is not installed"
        raise MissingToolError(msg)


def gen_proj(
    maxim_path: Path,
    output_dir: Path,
    target: str,
    bsp: str,
    template: str,
    *,
    include_vscode: bool,
    include_readme: bool,
    init_git: bool,
) -> None:
    """Generate project from MaximSDK example.

    Args:
        maxim_path: Path to MaximSDK installation
        output_dir: Path to output directory
        target: Target to validate (e.g., 'MAX32655')
        bsp: Board support package to use (e.g., 'EvKit_V1')
        template: Template (example) to validate (e.g., 'Hello_World')

    Keyword Arguments:
        include_vscode: Include VSCode configuration
        include_readme: Create README.md
        include_git: Initialize git repository

    Raises:
        ValidationError: If example does not exist
        MsdkError: Arbitrary OS/IO error
    """
    is_cwd = output_dir.resolve() == Path.cwd()
    cleanup_needed = False

    try:
        template_dir = _ensure_template_files_exist(maxim_path, target, template)
        _copy_template_files(
            template_dir,
            output_dir,
            include_vscode=include_vscode,
            target=target,
            bsp=bsp,
            is_cwd=is_cwd,
            with_git=init_git,
        )

        if include_readme:
            readme = output_dir / "README.md"
            if not readme.exists():
                readme.write_text(f"# {output_dir.resolve().name}\n")

        if init_git:
            _init_git(output_dir, is_cwd=is_cwd)
            _write_git_ignore(output_dir, vscode=include_vscode)

    except OSError as e:
        cleanup_needed = True
        raise MsdkError(e) from e
    except (ValidationError, CannotProceedError, MissingToolError):
        cleanup_needed = True
        raise
    else:
        cleanup_needed = False
    finally:
        if cleanup_needed and output_dir.exists() and not is_cwd:
            shutil.rmtree(output_dir)
