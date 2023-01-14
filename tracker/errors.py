class BaseTrackerException(Exception):
    """Core tackers exceptions."""


class AppendOutOfScope(BaseTrackerException):
    """`append` must be called either by `success_dict` or `error_dict` methods."""
