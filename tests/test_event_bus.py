import unittest

from bimnix_orchestrator.event_bus import EventBus
from bimnix_orchestrator.models import Event, EventType, PipelineState
from bimnix_orchestrator.cli import _owner_queue


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

    def test_event_bus_lists_owner_queue_events(self):
        from tempfile import TemporaryDirectory
        from pathlib import Path

        with TemporaryDirectory(ignore_cleanup_errors=True) as temp_dir:
            bus = EventBus(Path(temp_dir) / "events.sqlite3")
            owner_event = Event(
                event_type=EventType.SOCIAL_PIPELINE,
                state=PipelineState.CLAIM_REQUIRES_APPROVAL,
                route_to="owner",
                payload={"title": "Needs approval"},
            )
            automated_event = Event(
                event_type=EventType.SOCIAL_PIPELINE,
                state=PipelineState.EVIDENCE,
                route_to="notebooklm",
                payload={"title": "Automated"},
            )

            bus.append(owner_event)
            bus.append(automated_event)
            events = bus.list_by_route("owner")

        self.assertEqual(len(events), 1)
        self.assertEqual(events[0].id, owner_event.id)

    def test_owner_queue_groups_events_with_next_action(self):
        event = Event(
            event_type=EventType.SOCIAL_PIPELINE,
            state=PipelineState.CLAIM_REQUIRES_APPROVAL,
            route_to="owner",
            exception_reason="No source list attached to the claim.",
            payload={"title": "Needs approval", "claim": "A claim"},
        )

        queue = _owner_queue([event])

        self.assertEqual(queue["total"], 1)
        self.assertIn("CLAIM_REQUIRES_APPROVAL", queue["groups"])
        item = queue["groups"]["CLAIM_REQUIRES_APPROVAL"][0]
        self.assertEqual(item["title"], "Needs approval")
        self.assertIn("Approve", item["next_owner_action"])


if __name__ == "__main__":
    unittest.main()
