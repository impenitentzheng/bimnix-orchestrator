from __future__ import annotations

import json
import sqlite3
from pathlib import Path

from .models import Event, EventType, PipelineState


SCHEMA = """
CREATE TABLE IF NOT EXISTS events (
  id TEXT PRIMARY KEY,
  parent_id TEXT,
  created_at TEXT NOT NULL,
  event_type TEXT NOT NULL,
  state TEXT NOT NULL,
  route_to TEXT,
  exception_reason TEXT,
  payload_json TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_events_parent ON events(parent_id);
CREATE INDEX IF NOT EXISTS idx_events_state ON events(state);
"""


class EventBus:
    def __init__(self, db_path: Path) -> None:
        self.db_path = db_path

    def init(self) -> None:
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        with sqlite3.connect(self.db_path) as conn:
            conn.executescript(SCHEMA)

    def append(self, event: Event) -> None:
        self.init()
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                """
                INSERT INTO events
                (id, parent_id, created_at, event_type, state, route_to, exception_reason, payload_json)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    event.id,
                    event.parent_id,
                    event.created_at,
                    event.event_type,
                    event.state,
                    event.route_to,
                    event.exception_reason,
                    json.dumps(event.payload, ensure_ascii=False, sort_keys=True),
                ),
            )

    def latest(self, root_id: str) -> Event | None:
        self.init()
        ids = {root_id}
        latest_event = None
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            while ids:
                placeholders = ",".join("?" for _ in ids)
                rows = conn.execute(
                    f"SELECT * FROM events WHERE id IN ({placeholders}) OR parent_id IN ({placeholders}) ORDER BY created_at",
                    tuple(ids) + tuple(ids),
                ).fetchall()
                new_ids = {row["id"] for row in rows} - ids
                if rows:
                    latest_event = self._row_to_event(rows[-1])
                if not new_ids:
                    break
                ids |= new_ids
        return latest_event

    def list_recent(self, limit: int = 20) -> list[Event]:
        self.init()
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            rows = conn.execute("SELECT * FROM events ORDER BY created_at DESC LIMIT ?", (limit,)).fetchall()
            return [self._row_to_event(row) for row in rows]

    @staticmethod
    def _row_to_event(row: sqlite3.Row) -> Event:
        return Event(
            id=row["id"],
            parent_id=row["parent_id"],
            created_at=row["created_at"],
            event_type=EventType(row["event_type"]),
            state=PipelineState(row["state"]),
            route_to=row["route_to"],
            exception_reason=row["exception_reason"],
            payload=json.loads(row["payload_json"]),
        )
