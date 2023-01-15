import json
import inspect
import logging
import numpy as np
import pandas as pd
import typing as t
from tracker.errors import AppendOutOfScopeError
from tracker.abstract.interface import AbstractTrackerInterface


class BaseTracker(AbstractTrackerInterface):
    """Nominative class to watch module's execution to provide reports around it."""

    def __init__(self, cols: t.Sequence[str]):
        super().__init__(cols)
        self.df['success'] = bool
        self.errors_array = np.array([])
        self.successes_array = np.array([])

    @property
    def errors(self) -> int:
        """Get entries flagged as errors count."""
        return int(self.errors_df.shape[0])

    @property
    def successes(self) -> int:
        """Get entries flagged as successes count."""
        return int(self.successes_df.shape[0])

    @property
    def status(self) -> t.Tuple[int, int]:
        """Split the entries into the error and success groups."""
        return self.errors, self.successes

    @property
    def errors_df(self) -> pd.DataFrame:
        """Get the entries which are flagged as error."""
        filter_by = (self.df['success'].isnull()) | (self.df['success'] == False)
        return self.df.loc[filter_by]

    @property
    def successes_df(self) -> pd.DataFrame:
        """Get the entries which are flagged as success."""
        filter_by = (self.df['success'].notnull()) & (self.df['success'] != False)
        return self.df.loc[filter_by]

    def summarize_errors(self) -> None:
        """Sum up all entries flagged as errors into an array by using dict data type."""
        self.errors_array = np.array([])
        errors_df = self.errors_df
        if not errors_df.empty:
            errors_df.apply(self.error_dict, axis=1)

    def summarize_successes(self) -> None:
        """Sum up all entries flagged as successes into an array by using dict data type."""
        self.successes_array = np.array([])
        successes_df = self.successes_df
        if not successes_df.empty:
            successes_df.apply(self.success_dict, axis=1)

    def summarize(
        self,
        summarize_status: t.Optional[bool] = True,
        summarize_errors: t.Optional[bool] = True,
        summarize_successes: t.Optional[bool] = False,
    ) -> str:
        """Sum up the global tracker's status and generate a JSON content from it.

        Parameters
        ------
        summarize_status: indicates whether errors/successes count must be displayed in JSON.
        summarize_errors: indicates whether errors array must be displayed in JSON.
        summarize_successes: indicates whether successes array must be displayed in JSON.
        """
        summary = {}
        if summarize_status:
            status = self.status
            summary.update({'errors': status[0], 'successes': status[1]})
        if summarize_errors:
            self.summarize_errors()
            summary['failed'] = self.errors_array.tolist()
        if summarize_successes:
            self.summarize_successes()
            summary['succeded'] = self.successes_array.tolist()
        return json.dumps(summary, indent=4)

    def log_summary(self, logger: logging.Logger, **kwargs) -> None:
        """Display tracker's summary through a log upon informational level.

        Parameters
        ------
        logger: built-in Python util to display/record messages during module's flow.
        """
        logger.info(self.summarize(**kwargs))

    def append_dict(self, __dict: t.Dict[str, t.Any]) -> None:
        """Insert a self custom map to be displayed into summary depending on the caller source.

        Each dictionary object is inserted into an array depending on the caller source stack. This
        is meant to be invoked either by `error_dict` or `success_dict` methods, otherwise throwing
        an exception.

        The populated arrays are used afterwards to generate reports using a JSON notation.

        Parameters
        ------
        __dict: map holding error/success information to be appended into the correct arrays.
        """
        caller = inspect.stack()[1][3]
        if caller == 'error_dict':
            self.errors_array = np.append(__dict, self.errors_array)
        elif caller == 'success_dict':
            self.successes_array = np.append(__dict, self.successes_array)
        else:
            raise AppendOutOfScopeError

    def transform(self, **kwargs) -> t.Dict[t.Any, t.Any]:
        """Overridden."""
        return kwargs

    def add_snapshot(self, **kwargs) -> None:
        """Record a given block execution output."""
        row = self.transform(**kwargs)
        self.df.loc[len(self.df)] = row
