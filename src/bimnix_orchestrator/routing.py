from __future__ import annotations

from .models import PipelineState


STATE_OWNER = {
    PipelineState.KNOWLEDGE_TECHNICAL_EVENT: "chatgpt",
    PipelineState.EVIDENCE: "notebooklm",
    PipelineState.SOURCE_CREDIT_VERIFICATION: "chatgpt",
    PipelineState.CONTENT_CANDIDATE: "deepseek",
    PipelineState.EDITORIAL_DECISION: "chatgpt",
    PipelineState.MEDIA: "gemini",
    PipelineState.QC: "claude",
    PipelineState.PUBLISH_GATE: "chatgpt",
    PipelineState.PUBLISHED: "meta_instagram",
    PipelineState.INSIGHTS: "chatgpt",
    PipelineState.LEARNING_LOOP: "chatgpt",
}


CAPABILITY_REQUIRED = {
    PipelineState.EVIDENCE: ("notebooklm", "source_grounded_retrieval"),
    PipelineState.CONTENT_CANDIDATE: ("deepseek", "batch_copy_generation"),
    PipelineState.MEDIA: ("gemini", "media_generation"),
    PipelineState.QC: ("claude", "bim_technical_review"),
}
