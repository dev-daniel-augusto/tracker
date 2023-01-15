import json
import tracker


def populate(tracker: tracker.BaseTracker) -> None:
    """Create tracker's entries for testing purposes."""
    tracker.add_snapshot(status=200, content=json.dumps({'message': 'All fetched.'}))
    tracker.add_snapshot(status=401, content=json.dumps({'message': 'Not authorized.'}))
    tracker.add_snapshot(status=403, content=json.dumps({'message': 'Authorizization not found.'}))
    tracker.add_snapshot(status=500, content=json.dumps({'message': 'Internal Server Error.'}))
