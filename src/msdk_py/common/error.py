class MsdkError(Exception):
    """Base exception for all msdk-py errors."""


class ValidationError(MsdkError):
    """Input validation errors."""
