from argparse import ArgumentParser

from rich_argparse import RichHelpFormatter

from . import __version__
from .commands import COMMANDS


def add_help(parser: ArgumentParser) -> None:
    parser.add_argument(
        "-h",
        "--help",
        action="help",
        help="Show this help message and exit",
    )


def mkparser() -> ArgumentParser:
    parser = ArgumentParser(
        prog="msdk-py",
        description="CLI tool for Maxim MSDK project management",
        formatter_class=RichHelpFormatter,
        add_help=False,
    )

    add_help(parser)

    parser.add_argument(
        "-V",
        "--version",
        action="version",
        version=f"[bold cyan]%(prog)s[/] [green]{__version__}[/]",
        help="Show program's version number and exit",
    )

    subparsers = parser.add_subparsers(dest="command", required=True, title="Commands")
    for cmd_t in COMMANDS:
        cmd = cmd_t()
        cmd_parser = subparsers.add_parser(
            cmd.name,
            help=cmd.help,
            formatter_class=RichHelpFormatter,
            add_help=False,
            aliases=cmd.aliases or (),
        )
        add_help(cmd_parser)
        cmd.configure_parser(cmd_parser)
        cmd_parser.set_defaults(run_cmd=cmd.execute)

    return parser
