import sys
import traceback

from .cli import mkparser
from .common.display import cerr, set_quiet_mode
from .common.error import CannotProceedError, MissingToolError, MsdkError, ValidationError


def main() -> None:
    parser = mkparser()
    args = parser.parse_args()

    if args.quiet:
        set_quiet_mode(True)

    try:
        args.run_cmd(args)
    except (ValidationError, CannotProceedError, MissingToolError) as e:
        cerr(str(e), exit_code=1)
    except MsdkError as e:
        cerr(str(e))
        if input("See traceback? (y/n): ").strip().lower() == "y":
            cerr(traceback.format_exc())
        sys.exit(2)
    except KeyboardInterrupt:
        sys.exit(130)
    else:
        sys.exit(0)


if __name__ == "__main__":
    main()
