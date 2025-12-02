from sys import exit as sexit

from .cli import mkparser
from .common.display import cerr
from .common.error import MsdkError


def main() -> None:
    parser = mkparser()
    args = parser.parse_args()

    try:
        args.run_cmd(args)
    except MsdkError as e:
        cerr(str(e), exit_code=1)
    except KeyboardInterrupt:
        sexit(130)
    else:
        sexit(0)


if __name__ == "__main__":
    main()
