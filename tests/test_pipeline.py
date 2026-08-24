from pathlib import Path
import unittest

from bimnix_orchestrator.capabilities import CapabilityRegistry
from bimnix_orchestrator.models import Event, EventType, PipelineState
from bimnix_orchestrator.pipeline import SocialPipeline


def registry() -> CapabilityRegistry:
    return CapabilityRegistry.load(Path("config/capabilities.example.toml"))


class PipelineTests(unittest.TestCase):
    def test_claim_without_sources_requires_owner_approval(self):
        event = Event(
            event_type=EventType.SOCIAL_PIPELINE,
            state=PipelineState.KNOWLEDGE_TECHNICAL_EVENT,
            payload={"title": "Test", "claim": "Unverified claim", "sources": []},
        )

        transition = SocialPipeline(registry()).next(event)

        self.assertIsNotNone(transition)
        self.assertEqual(transition.next_state, PipelineState.CLAIM_REQUIRES_APPROVAL)
        self.assertEqual(transition.route_to, "owner")

    def test_unverified_notebooklm_stops_at_technical_unverified(self):
        event = Event(
            event_type=EventType.SOCIAL_PIPELINE,
            state=PipelineState.EVIDENCE,
            payload={"sources": ["https://example.com/source"]},
        )

        transition = SocialPipeline(registry()).next(event)

        self.assertIsNotNone(transition)
        self.assertEqual(transition.next_state, PipelineState.TECHNICAL_RESULT_UNVERIFIED)

    def test_unverified_deepseek_uses_local_candidate_fallback(self):
        event = Event(
            event_type=EventType.SOCIAL_PIPELINE,
            state=PipelineState.CONTENT_CANDIDATE,
            payload={"title": "Revit automation", "claim": "Automated checks reduce manual QA."},
        )

        transition = SocialPipeline(registry()).next(event)

        self.assertIsNotNone(transition)
        self.assertEqual(transition.next_state, PipelineState.EDITORIAL_DECISION)
        self.assertTrue(transition.payload_patch["content_candidate"]["requires_editorial_approval"])

    def test_publish_gate_requires_official_meta_capability(self):
        event = Event(
            event_type=EventType.SOCIAL_PIPELINE,
            state=PipelineState.PUBLISH_GATE,
            payload={"editorial_decision": "approved"},
        )

        transition = SocialPipeline(registry()).next(event)

        self.assertIsNotNone(transition)
        self.assertEqual(transition.next_state, PipelineState.PUBLISHING_FAILED)

    def test_business_dm_routes_to_owner(self):
        event = Event(
            event_type=EventType.SOCIAL_PIPELINE,
            state=PipelineState.KNOWLEDGE_TECHNICAL_EVENT,
            payload={"inbound_kind": "business_dm", "sources": ["crm"]},
        )

        transition = SocialPipeline(registry()).next(event)

        self.assertIsNotNone(transition)
        self.assertEqual(transition.next_state, PipelineState.BUSINESS_DM)
        self.assertEqual(transition.route_to, "owner")

    def test_copyright_risk_routes_to_owner(self):
        event = Event(
            event_type=EventType.SOCIAL_PIPELINE,
            state=PipelineState.SOURCE_CREDIT_VERIFICATION,
            payload={"copyright_status": "risky", "sources": ["licensed-image"]},
        )

        transition = SocialPipeline(registry()).next(event)

        self.assertIsNotNone(transition)
        self.assertEqual(transition.next_state, PipelineState.COPYRIGHT_RISK)
        self.assertEqual(transition.route_to, "owner")


if __name__ == "__main__":
    unittest.main()
