from __future__ import annotations

import json
import shutil
from pathlib import Path

from msdk_py.common.error import MsdkError, ValidationError
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
    ensure_exists(template_dir / "Makefile", "template [file]Makefile[/]")
    ensure_exists(template_dir / "main.c", "template [file]main.c[/]")
    ensure_exists(template_dir / "project.mk", "template [file]project.mk[/]")

    return template_dir


def _rename_old_if_exists(path: Path) -> None:
    """Rename path if it already exists.

    Args:
        path: Path to rename
    """

    if path.exists():
        path.rename(path.with_suffix(".old"))


def _copy_template_files(
    template_dir: Path,
    output_dir: Path,
    *,
    target: str,
    bsp: str,
    include_vscode: bool,
    is_cwd: bool,
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

    Raises:
        ValidationError: If example does not exist
    """

    if not is_cwd:
        output_dir.mkdir(parents=True)

    # Create file or update mod time for msdk-py marker file (for later locating project dir)
    (output_dir / ".msdk-py-proj").touch()

    tem_srcs = (template_dir / f for f in ("Makefile", "main.c", "project.mk"))
    out_dests = (output_dir / f for f in ("Makefile", "src/main.c", "project.mk"))

    (output_dir / "src").mkdir(exist_ok=True)

    for tem_src, out_dest in zip(tem_srcs, out_dests, strict=True):
        if is_cwd:
            _rename_old_if_exists(out_dest)
        shutil.copy2(tem_src, out_dest)

    (output_dir / "include").mkdir(exist_ok=True)

    out_p_mk = output_dir / "project.mk"
    out_p_mk_lines = out_p_mk.read_text().splitlines()[:-1]  # Exclude "# Add your config here!" line
    aline = out_p_mk_lines.append
    aline(f"PROJECT={output_dir.name}")
    aline(f"BOARD={bsp}")
    aline(f"TARGET={target}\n")
    aline("# Add any additional configs here!\n")
    out_p_mk.write_text("\n".join(out_p_mk_lines))

    if include_vscode:
        vscode_src = template_dir / ".vscode"
        vscout_out = output_dir / ".vscode"
        shutil.copytree(vscode_src, vscout_out)


def _update_vscode_bsp(vscode_dir: Path, bsp: str) -> None:
    """Update board (bsp) field in `.vscode/settings.json`.

    Args:
        vscode_dir: Path to `.vscode` directory
        board: Board to update (e.g., 'EvKit_V1')

    Raises:
        ValidationError: If settings file does not exist
    """

    settings_file = vscode_dir / "settings.json"
    ensure_exists(settings_file, "template [file].vscode/settings.json[/]")

    with settings_file.open() as f:
        settings = json.load(f)

    settings["board"] = bsp

    with settings_file.open("w") as f:
        json.dump(settings, f, indent=4)


def gen_proj(
    maxim_path: Path,
    output_dir: Path,
    target: str,
    bsp: str,
    template: str,
    *,
    include_vscode: bool,
    include_readme: bool,
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

    Raises:
        ValidationError: If example does not exist
        MsdkError: Arbitrary OS/IO error
    """
    is_cwd = output_dir.resolve() == Path.cwd()

    try:
        template_dir = _ensure_template_files_exist(maxim_path, target, template)
        _copy_template_files(
            template_dir,
            output_dir,
            include_vscode=include_vscode,
            target=target,
            bsp=bsp,
            is_cwd=is_cwd,
        )

        if include_vscode:
            _update_vscode_bsp(output_dir / ".vscode", bsp)

        if include_readme:
            (output_dir / "README.md").write_text(f"# {output_dir.name}\n")

    except OSError as e:
        if output_dir.exists():
            shutil.rmtree(output_dir)
        raise MsdkError(e) from e
    except ValidationError:
        if output_dir.exists():
            shutil.rmtree(output_dir)
        raise
