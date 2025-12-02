class MsdkError(Exception):
    """Base exception for all msdk-py errors.

    If raised directly, more than likely, something on your side went wrong.
    """


class ValidationError(MsdkError):
    """Input validation errors."""


class CannotProceedError(MsdkError):
    """Cannot proceed with operation."""


class MissingToolError(MsdkError):
    """Missing tool errors (e.g. `git`, `make`)."""
