class MsdkError(Exception):
    """Base exception for all msdk-py errors.

    If raised directly, more than likely, something on your side went wrong.
    """


class ValidationError(MsdkError):
    """Input validation errors."""
