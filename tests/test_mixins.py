import pytest
import tracker as tk
from datetime import datetime
from os import remove
from os.path import exists
from tests.utils import populate


@pytest.fixture
def csv_tracker() -> tk.BaseTracker:
    """Initialize a BaseTracker instance with csv functionality."""
    class Tracker(tk.BaseTracker, tk.mixins.CSVMixin):

        def __init__(self) -> None:
            super().__init__(('status', 'content'))

    return Tracker()


@pytest.fixture
def time_tracker() -> tk.BaseTracker:
    """Initialize a populated BaseTracker instance with time functionality."""
    class Tracker(tk.BaseTracker, tk.mixins.TimeMixin):

        def __init__(self) -> None:
            super().__init__(('status', 'content'))
            self.df['time'] = datetime

        def transform(self, **kwargs) -> None:
            """Overridden."""
            if kwargs.get('status'):
                kwargs['success'] = True if 199 < kwargs['status'] < 300 else False
            return kwargs

    tracker = Tracker()
    populate(tracker)
    return tracker


class TestCSVMixin:
    """Carries CSVMixin class tests out."""

    def test_create_csv_all_flag(self, csv_tracker: tk.BaseTracker):
        """Check the create_csv upon all flag."""
        assert not exists('all.csv')
        csv_tracker.create_csv('all.csv', flag=tk.flags.ALL)
        assert exists('all.csv')
        remove('all.csv')

    def test_create_csv_errors_flag(self, csv_tracker: tk.BaseTracker):
        """Check the create_csv upon errors flag."""
        assert not exists('errors.csv')
        csv_tracker.create_csv('errors.csv', flag=tk.flags.ONLY_ERRORS)
        assert exists('errors.csv')
        remove('errors.csv')

    def test_create_csv_successes_flag(self, csv_tracker: tk.BaseTracker):
        """Check the create_csv successes flag."""
        assert not exists('successes.csv')
        csv_tracker.create_csv('successes.csv', flag=tk.flags.ONLY_SUCCESSES)
        assert exists('successes.csv')
        remove('successes.csv')

    def test_create_csv_invalid_flag(self, csv_tracker: tk.BaseTracker):
        """Check if an exception is raised over an invalid flag attempt."""
        with pytest.raises(tk.errors.InvalidFlagError):
            csv_tracker.create_csv('invalid_flag.csv', flag=-1)
        assert not exists('invalid_flag.csv')


class TestTimeMixin:
    """Carries TimeMixin class tests out."""

    def test_time_column(self, time_tracker: tk.BaseTracker):
        """Check if the time column is properly filled."""
        today = datetime.today().date().isoformat()
        assert time_tracker.df.loc[0, 'time'][:10] == today
