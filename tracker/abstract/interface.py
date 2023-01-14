import logging
import pandas as pd
import typing as t
from abc import ABC, abstractmethod


class AbstractTrackerInterface(ABC):

    def __init__(self, cols: t.Sequence[str]) -> None: self.df = pd.DataFrame(columns=cols)
    def __str__(self) -> str: return f'Tracker<[{self.df.shape[0]}:{self.errors}|{self.successes}]>'
    @abstractmethod
    def transform(self, **kwargs) -> t.Dict[t.Any, t.Any]: ...
    @property
    def errors(self) -> int: ...
    @property
    def successes(self) -> int: ...
    @property
    def status(self) -> t.Tuple[int, int]: ...
    @property
    def errors_df(self) -> pd.DataFrame: ...
    @property
    def successes_df(self) -> pd.DataFrame: ...
    def error_dict(self) -> None: raise NotImplementedError
    def success_dict(self) -> None: raise NotImplementedError
    def summarize_errors(self) -> None: ...
    def summarize_successes(self) -> None: ...
    def summarize(self) -> str: ...
    def log_summary(self, logger: logging.Logger, **kwargs) -> None: ...
    def append_dict(self, __dict: t.Dict[str, t.Any]) -> None: ...
    def add_snapshot(self, **kwargs) -> None: ...
