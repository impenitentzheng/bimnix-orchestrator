from __future__ import annotations

import argparse
import json
import logging
from collections import defaultdict
from pathlib import Path

from .capabilities import CapabilityRegistry
from .event_bus import EventBus
from .models import Event, EventType, PipelineState
from .pipeline import SocialPipeline


LOG = logging.getLogger("bimnix_orchestrator")


def main() -> None:
    parser = argparse.ArgumentParser(description="BIMNIX Orchestration Layer v1")
    parser.add_argument("--db", default="work/bimnix-events.sqlite3")
    parser.add_argument("--capabilities", default="config/capabilities.example.toml")
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("init-db")

    emit = sub.add_parser("emit-social-event")
    emit.add_argument("--title", required=True)
    emit.add_argument("--claim", required=True)
    emit.add_argument("--source", action="append", default=[])
    emit.add_argument("--copyright-status", default="unknown")
    emit.add_argument("--editorial-decision", default="needs_review")

    run = sub.add_parser("run-once")
    run.add_argument("event_id")

    owner_queue = sub.add_parser("owner-queue")
    owner_queue.add_argument("--limit", type=int, default=50)

    sub.add_parser("list-events")
    args = parser.parse_args()
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")

    bus = EventBus(Path(args.db))

    if args.command == "init-db":
        bus.init()
        print(f"Initialized event bus at {args.db}")
        return

    if args.command == "emit-social-event":
        event = Event(
            event_type=EventType.SOCIAL_PIPELINE,
            state=PipelineState.KNOWLEDGE_TECHNICAL_EVENT,
            route_to="chatgpt",
            payload={
                "title": args.title,
                "claim": args.claim,
                "sources": args.source,
                "copyright_status": args.copyright_status,
                "editorial_decision": args.editorial_decision,
            },
        )
        bus.append(event)
        LOG.info("created social event", extra={"event_id": event.id})
        print(json.dumps(_event_dict(event), ensure_ascii=False, indent=2))
        return

    if args.command == "run-once":
        latest = bus.latest(args.event_id)
        if latest is None:
            raise SystemExit(f"Event not found: {args.event_id}")
        pipeline = SocialPipeline(CapabilityRegistry.load(Path(args.capabilities)))
        transition = pipeline.next(latest)
        if transition is None:
            print(json.dumps({"status": "no_transition", "event": _event_dict(latest)}, ensure_ascii=False, indent=2))
            return
        new_event = pipeline.apply(latest, transition)
        bus.append(new_event)
        LOG.info("transitioned event", extra={"from": latest.state, "to": new_event.state})
        print(json.dumps(_event_dict(new_event), ensure_ascii=False, indent=2))
        return

    if args.command == "list-events":
        print(json.dumps([_event_dict(event) for event in bus.list_recent()], ensure_ascii=False, indent=2))
        return

    if args.command == "owner-queue":
        events = bus.list_by_route("owner", limit=args.limit)
        print(json.dumps(_owner_queue(events), ensure_ascii=False, indent=2))
        return


def _event_dict(event: Event) -> dict:
    return {
        "id": event.id,
        "parent_id": event.parent_id,
        "created_at": event.created_at,
        "event_type": event.event_type,
        "state": event.state,
        "route_to": event.route_to,
        "exception_reason": event.exception_reason,
        "payload": event.payload,
    }


def _owner_queue(events: list[Event]) -> dict:
    grouped = defaultdict(list)
    for event in events:
        grouped[event.state].append(
            {
                "id": event.id,
                "created_at": event.created_at,
                "reason": event.exception_reason,
                "title": event.payload.get("title"),
                "claim": event.payload.get("claim"),
                "next_owner_action": _owner_action(event.state),
            }
        )
    return {
        "route_to": "owner",
        "total": len(events),
        "groups": dict(grouped),
    }


def _owner_action(state: PipelineState) -> str:
    actions = {
        PipelineState.CLAIM_REQUIRES_APPROVAL: "Approve, reject, or rewrite the exact claim.",
        PipelineState.COPYRIGHT_RISK: "Confirm license, replace the asset, or reject the candidate.",
        PipelineState.BUSINESS_DM: "Reply personally or assign a sales/support follow-up.",
        PipelineState.TECHNICAL_RESULT_UNVERIFIED: "Attach verified evidence or send to BIM technical review.",
        PipelineState.PUBLISHING_FAILED: "Check publishing capability, account permissions, and retry policy.",
    }
    return actions.get(state, "Review and decide the next step.")


if __name__ == "__main__":
    main()
