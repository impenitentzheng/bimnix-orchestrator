from __future__ import annotations

from .capabilities import CapabilityRegistry
from .models import Event, EventType, PipelineState, Transition
from .routing import CAPABILITY_REQUIRED, STATE_OWNER


EXCEPTION_STATES = {
    PipelineState.CLAIM_REQUIRES_APPROVAL,
    PipelineState.COPYRIGHT_RISK,
    PipelineState.BUSINESS_DM,
    PipelineState.TECHNICAL_RESULT_UNVERIFIED,
    PipelineState.PUBLISHING_FAILED,
}


class SocialPipeline:
    def __init__(self, capabilities: CapabilityRegistry) -> None:
        self.capabilities = capabilities

    def next(self, event: Event) -> Transition | None:
        if event.state in EXCEPTION_STATES or event.state == PipelineState.LEARNING_LOOP:
            return None

        if event.payload.get("inbound_kind") == "business_dm":
            return self._exception(PipelineState.BUSINESS_DM, "Potential sales/support DM needs owner response.")

        if event.state == PipelineState.KNOWLEDGE_TECHNICAL_EVENT:
            if not event.payload.get("sources"):
                return self._exception(PipelineState.CLAIM_REQUIRES_APPROVAL, "No source list attached to the claim.")
            return self._advance(PipelineState.EVIDENCE)

        if event.state == PipelineState.EVIDENCE:
            if not self._capability_ok(PipelineState.EVIDENCE):
                return self._exception(
                    PipelineState.TECHNICAL_RESULT_UNVERIFIED,
                    "NotebookLM/source-grounded retrieval capability is not verified.",
                )
            return self._advance(PipelineState.SOURCE_CREDIT_VERIFICATION)

        if event.state == PipelineState.SOURCE_CREDIT_VERIFICATION:
            if event.payload.get("copyright_status") == "risky":
                return self._exception(PipelineState.COPYRIGHT_RISK, "Source or media license needs review.")
            return self._advance(PipelineState.CONTENT_CANDIDATE, {"credit_checked": True})

        if event.state == PipelineState.CONTENT_CANDIDATE:
            if not self._capability_ok(PipelineState.CONTENT_CANDIDATE):
                patch = {"content_candidate": self._local_candidate(event.payload)}
                return self._advance(PipelineState.EDITORIAL_DECISION, patch)
            return self._advance(PipelineState.EDITORIAL_DECISION)

        if event.state == PipelineState.EDITORIAL_DECISION:
            decision = event.payload.get("editorial_decision", "needs_review")
            if decision != "approved":
                return self._exception(PipelineState.CLAIM_REQUIRES_APPROVAL, "Editorial decision is not approved.")
            return self._advance(PipelineState.MEDIA)

        if event.state == PipelineState.MEDIA:
            if not self._capability_ok(PipelineState.MEDIA):
                return self._advance(PipelineState.QC, {"media_plan": "Manual media required; Gemini capability unverified."})
            return self._advance(PipelineState.QC)

        if event.state == PipelineState.QC:
            if not self._capability_ok(PipelineState.QC):
                return self._exception(
                    PipelineState.TECHNICAL_RESULT_UNVERIFIED,
                    "Claude BIM technical review capability is not verified.",
                )
            return self._advance(PipelineState.PUBLISH_GATE)

        if event.state == PipelineState.PUBLISH_GATE:
            if not self.capabilities.integration_has("meta_instagram", "publish_instagram"):
                return self._exception(
                    PipelineState.PUBLISHING_FAILED,
                    "Official Meta/Instagram publishing capability is not verified.",
                )
            return self._advance(PipelineState.PUBLISHED)

        if event.state == PipelineState.PUBLISHED:
            return self._advance(PipelineState.INSIGHTS)

        if event.state == PipelineState.INSIGHTS:
            return self._advance(PipelineState.LEARNING_LOOP)

        return None

    def apply(self, event: Event, transition: Transition) -> Event:
        payload = dict(event.payload)
        payload.update(transition.payload_patch)
        return Event(
            event_type=EventType.SOCIAL_PIPELINE,
            state=transition.next_state,
            payload=payload,
            parent_id=event.id,
            route_to=transition.route_to,
            exception_reason=transition.exception_reason,
        )

    def _advance(self, state: PipelineState, patch: dict | None = None) -> Transition:
        return Transition(next_state=state, route_to=STATE_OWNER[state], payload_patch=patch or {})

    def _exception(self, state: PipelineState, reason: str) -> Transition:
        return Transition(next_state=state, route_to="owner", exception_reason=reason)

    def _capability_ok(self, state: PipelineState) -> bool:
        agent, capability = CAPABILITY_REQUIRED[state]
        return self.capabilities.agent_has(agent, capability)

    @staticmethod
    def _local_candidate(payload: dict) -> dict:
        title = payload.get("title", "BIMNIX technical note")
        claim = payload.get("claim", "A BIM workflow needs evidence before publication.")
        return {
            "caption_draft": f"{title}: {claim}",
            "format": "instagram_caption",
            "requires_editorial_approval": True,
        }
