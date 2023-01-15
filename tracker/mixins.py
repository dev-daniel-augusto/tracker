import typing as t
from datetime import datetime
from functools import wraps
from tracker.constants import flags
from tracker.errors import InvalidFlagError
from tracker.abstract.interface import AbstractTrackerInterface


class CSVMixin(AbstractTrackerInterface):
    """Adds a functionality of creating .csv files from trackers' scopes."""

    def create_csv(self, path: str, flag: int, **kwargs) -> None:
        """Generate a .csv file from errors df, successes df or entire df.

        Parameters
        ------
        path: local where the file will be created on OS.
        flag: indicates which tracker's DataFrame are going to be used to generate the CSV.

        Exemples
        ------
        class Tracker(BaseTracker, CSVMixin):

            def __init__(self):
                super().__init__(('col_1', 'col_2'))

        >>> tracker = Tracker()
        >>> tracker.create_csv(path='all.csv', flag=flags.ALL)
        >>> tracker.create_csv(path='errors.csv', flag=flags.ONLY_ERRORS)
        >>> tracker.create_csv(path='successes.csv', flag=flags.SUCCESSES)
        """
        if flag == flags.ALL:
            self.df.to_csv(path, index=False, **kwargs)
        elif flag == flags.ONLY_ERRORS:
            self.errors_df.to_csv(path, index=False, **kwargs)
        elif flag == flags.ONLY_SUCCESSES:
            self.successes_df.to_csv(path, index=False, **kwargs)
        else:
            raise InvalidFlagError(f'Flag {flag} is not accepted.')


class TimeMixin(AbstractTrackerInterface):
    """Auto-add timing while adding tracker's entries.

    Exemples
    ------
    class Tracker(BaseTracker, TimeMixin):

        def __init__(self):
            super().__init__(('col_1', 'col_2'))
            self.df['time'] = datetime

    >>> tracker = Tracker()
    >>> tracker.add_snapshot(col_1='col_1_value', col_2='col_2_value', success=False)
    >>> tracker.df

        col_1        col_2        success   time
    0   col_1_value  col_2_value  False     2023-01-14 08:30:30.480553
    """

    def __init_subclass__(cls) -> None:
        cls.transform = cls.add_time(cls.transform)

    def add_time(
        transform: t.Callable[[t.Dict[str, t.Any]], t.Dict[str, t.Any]],
    ) -> t.Callable[..., t.Dict[str, t.Any]]:
        """Wrap `AbstractTrackerInterface.transform` to include a timing feature.

        Parameters
        ------
        transform: `AbstractTrackerInterface.transform` callable.
        """
        @wraps(transform)
        def time_decorator(self, *args, **kwargs) -> t.Dict[str, t.Any]:
            """Fill DataFrame's entries time column with the current time following the ISO 8601."""
            kwargs = transform(self, *args, **kwargs)
            kwargs['time'] = str(datetime.now())
            return kwargs
        return time_decorator
