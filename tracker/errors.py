class BaseTrackerException(Exception):
    """Core tackers exceptions."""


class AppendOutOfScopeError(BaseTrackerException):
    """Invalid caller source."""


class InvalidFlagError(BaseTrackerException):
    """Not recognized flag."""
