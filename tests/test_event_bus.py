import unittest

from bimnix_orchestrator.event_bus import EventBus
from bimnix_orchestrator.models import Event, EventType, PipelineState


class EventBusTests(unittest.TestCase):
    def test_event_bus_appends_and_lists_events(self):
        from tempfile import TemporaryDirectory
        from pathlib import Path

        with TemporaryDirectory(ignore_cleanup_errors=True) as temp_dir:
            bus = EventBus(Path(temp_dir) / "events.sqlite3")
            event = Event(
                event_type=EventType.SOCIAL_PIPELINE,
                state=PipelineState.KNOWLEDGE_TECHNICAL_EVENT,
                payload={"title": "A", "sources": ["s"]},
            )

            bus.append(event)
            events = bus.list_recent()

        self.assertEqual(len(events), 1)
        self.assertEqual(events[0].id, event.id)
        self.assertEqual(events[0].payload["title"], "A")


if __name__ == "__main__":
    unittest.main()
