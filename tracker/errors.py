class BaseTrackerException(Exception):
    """Core tackers exceptions."""


class AppendOutOfScopeError(BaseTrackerException):
    """`append` must be called either by `success_dict` or `error_dict` methods."""


class InvalidFlagError(BaseTrackerException):
    """`create_csv` passed flag not recognized."""
