from argparse import ArgumentParser
from argparse import _ArgumentGroup as ArgGroup

from rich_argparse import RichHelpFormatter

from msdk_py.common.display import cout

from . import __prog__, __version__
from .commands import COMMANDS


def add_parser_help(parser: ArgumentParser | ArgGroup) -> None:
    parser.add_argument(
        "-h",
        "--help",
        action="help",
        help="Show program/command help message and exit",
    )


def fmt_subcmd_usage(cmd: str, *, has_pos_args: bool = False) -> str:
    pos_arg_str = " \\[args]" if has_pos_args else ""
    return f"[prog]{cmd}[/] [cyan]\\[options]{pos_arg_str}[/]"


def mkparser() -> ArgumentParser:
    help_fmter = lambda prog: RichHelpFormatter(prog, indent_increment=2, console=cout)  # noqa: E731
    parser = ArgumentParser(
        prog="msdk-py",
        description="CLI tool for Maxim SDK project management.",
        formatter_class=help_fmter,
        add_help=False,
    )

    parser.add_argument(
        "-V",
        "--version",
        action="version",
        version=f"[bold cyan]%(prog)s[/] [green]v{__version__}[/]",
        help="Show program's version number and exit",
    )

    # argparse is probably one of the worst stdlib modules to ever exist
    global_opts = parser.add_argument_group("Global Options")
    add_parser_help(global_opts)
    global_opts.add_argument("-q", "--quiet", action="store_true", help="Suppress command output")

    subparsers = parser.add_subparsers(dest="command", required=True, title="Commands", metavar="<command>")
    for cmd_t in COMMANDS:
        cmd = cmd_t()
        cmd_parser = subparsers.add_parser(
            cmd.name,
            help=cmd.help,
            formatter_class=help_fmter,
            usage=fmt_subcmd_usage(f"{__prog__} {cmd.name}", has_pos_args=cmd.has_pos_args),
            add_help=False,
            aliases=cmd.aliases or (),
        )
        add_parser_help(cmd_parser)
        cmd.configure_parser(cmd_parser)
        cmd_parser.set_defaults(run_cmd=cmd.execute)

    return parser
