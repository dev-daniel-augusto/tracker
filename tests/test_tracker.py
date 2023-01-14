import json
import logging
import pandas as pd
import pytest
import tracker as tk
import typing as t
from pytest_mock import MockerFixture
from tests.utils import populate


@pytest.fixture
def tracker() -> tk.BaseTracker:
    """Initialize a specialized BaseTracker instance for testing purposes."""
    class Tracker(tk.BaseTracker):

        def __init__(self) -> None:
            super().__init__(('status', 'content'))

        def error_dict(self, entry: pd.Series) -> None:
            """Overridden."""
            error_dict = {'status': entry[0], 'error': entry[1]}
            self.append_dict(error_dict)

        def success_dict(self, entry: pd.Series) -> None:
            """Overridden."""
            success_dict = {'status': entry[0], 'message': 'Request filled with no errors.'}
            self.append_dict(success_dict)

        def transform(self, **kwargs) -> t.Dict[str, t.Any]:
            """Overridden."""
            if kwargs.get('status'):
                kwargs['success'] = True if 199 < kwargs['status'] < 300 else False
            return kwargs

        def _invalid_dict(self):
            """Call append_dict to raise an exception."""
            invalid_caller_dict = {'status': 0}
            self.append_dict(invalid_caller_dict)

    _tracker = Tracker()
    populate(_tracker)
    return _tracker


class TestBaseTracker:
    """Carries BaseTracker class tests out without specialization."""

    def test_transform(self, mocker: MockerFixture):
        """Check if transform method does not change anything due to no specialization."""
        _tracker = tk.BaseTracker(('status', 'content'))
        transform_spy = mocker.spy(_tracker, 'transform')
        add_snapshot_spy = mocker.spy(_tracker, 'add_snapshot')
        kwargs = {'status': 200, 'content': json.dumps({'message': 'All fetched.'})}
        _tracker.add_snapshot(**kwargs)
        transform_spy.assert_called_with(**kwargs)
        add_snapshot_spy.assert_called_with(**kwargs)


class TestTracker:
    """Carries BaseTracker class tests out with specialization."""

    def test_successes(self, tracker: tk.BaseTracker):
        """Check if successes property provides the correct number of entries flagged as success."""
        assert tracker.successes, 1

    def test_errors(self, tracker: tk.BaseTracker):
        """Check if errors property provides the correct number of entries flagged as error."""
        assert tracker.errors, 3

    def test_status(self, tracker: tk.BaseTracker):
        """Check if both errors and successes entries are properly aggregated."""
        assert tracker.status == (3, 1)

    def test_errors_df(self, tracker: tk.BaseTracker):
        """Check if builded DataFrame from errors entries."""
        errors_df = tracker.errors_df
        assert isinstance(errors_df, pd.DataFrame)
        assert errors_df.shape == (3, 3)

    def test_successes_df(self, tracker: tk.BaseTracker):
        """Check if builded DataFrame from successes entries."""
        successes_df = tracker.successes_df
        assert isinstance(successes_df, pd.DataFrame)
        assert successes_df.shape == (1, 3)

    def test_summarize_errors(self, tracker: tk.BaseTracker):
        """Check the array holding errors entries while invoking summarize_errors."""
        tracker.summarize_errors()
        assert len(tracker.errors_array) == 3
        expected_dict_1 = {'status': 500, 'error': '{"message": "Internal Server Error."}'}
        expected_dict_2 = {'status': 401, 'error': '{"message": "Not authorized."}'}
        assert tracker.errors_array[0] == expected_dict_1
        assert tracker.errors_array[-1] == expected_dict_2

    def test_summarize_successes(self, tracker: tk.BaseTracker):
        """Check the array holding errors entries while invoking summarize_successes."""
        tracker.summarize_successes()
        expected_dict = {'status': 200, 'message': 'Request filled with no errors.'}
        assert len(tracker.successes_array) == 1
        assert tracker.successes_array[0] == expected_dict

    def test_summarize(self, tracker: tk.BaseTracker):
        """Check the summary from tracker."""
        summary = json.loads(tracker.summarize(summarize_successes=True))
        arrays = (summary['failed'], summary['succeded'])
        assert summary['errors'] == 3
        assert summary['successes'] == 1
        assert len(summary['failed']) == 3
        assert len(summary['succeded']) == 1
        assert all(isinstance(array, list) for array in arrays)

    def test_log_summary(self, mocker: MockerFixture, tracker: tk.BaseTracker):
        """Check if the loggger's info is called while invoking the tracker's summary."""
        logger = logging.getLogger(__name__)
        logger_spy = mocker.spy(logger, 'info')
        tracker.log_summary(logger)
        logger_spy.assert_called_once()

    def test_append_dict_exception(self, tracker: tk.BaseTracker):
        """Check if an exception is raised when append_dict is wrongly called."""
        with pytest.raises(tk.errors.AppendOutOfScopeError):
            tracker._invalid_dict()
