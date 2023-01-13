class BaseTrackerError(Exception):
    """Core Trackers exceptions."""


class AppendOutOfScope(BaseException):
    """`append` must be called either by `success_dict` or `error_dict` methods."""
