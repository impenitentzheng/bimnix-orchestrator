from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import StrEnum
from typing import Any
from uuid import uuid4


class PipelineState(StrEnum):
    KNOWLEDGE_TECHNICAL_EVENT = "KNOWLEDGE_TECHNICAL_EVENT"
    EVIDENCE = "EVIDENCE"
    SOURCE_CREDIT_VERIFICATION = "SOURCE_CREDIT_VERIFICATION"
    CONTENT_CANDIDATE = "CONTENT_CANDIDATE"
    EDITORIAL_DECISION = "EDITORIAL_DECISION"
    MEDIA = "MEDIA"
    QC = "QC"
    PUBLISH_GATE = "PUBLISH_GATE"
    PUBLISHED = "PUBLISHED"
    INSIGHTS = "INSIGHTS"
    LEARNING_LOOP = "LEARNING_LOOP"
    CLAIM_REQUIRES_APPROVAL = "CLAIM_REQUIRES_APPROVAL"
    COPYRIGHT_RISK = "COPYRIGHT_RISK"
    BUSINESS_DM = "BUSINESS_DM"
    TECHNICAL_RESULT_UNVERIFIED = "TECHNICAL_RESULT_UNVERIFIED"
    PUBLISHING_FAILED = "PUBLISHING_FAILED"


class EventType(StrEnum):
    SOCIAL_PIPELINE = "SOCIAL_PIPELINE"
    OWNER_EXCEPTION = "OWNER_EXCEPTION"
    PIPELINE_AUDIT = "PIPELINE_AUDIT"


@dataclass(frozen=True)
class Event:
    event_type: EventType
    state: PipelineState
    payload: dict[str, Any]
    id: str = field(default_factory=lambda: str(uuid4()))
    parent_id: str | None = None
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    route_to: str | None = None
    exception_reason: str | None = None


@dataclass(frozen=True)
class Transition:
    next_state: PipelineState
    route_to: str
    payload_patch: dict[str, Any] = field(default_factory=dict)
    exception_reason: str | None = None
