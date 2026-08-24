from __future__ import annotations

import tomllib
from dataclasses import dataclass
from pathlib import Path


VERIFIED_STATUSES = {"verified", "verified_local", "manual"}


@dataclass(frozen=True)
class CapabilityRegistry:
    raw: dict

    @classmethod
    def load(cls, path: Path) -> "CapabilityRegistry":
        with path.open("rb") as handle:
            return cls(tomllib.load(handle))

    def agent_has(self, agent: str, capability: str) -> bool:
        item = self.raw.get("agents", {}).get(agent, {})
        return item.get("status") in VERIFIED_STATUSES and capability in item.get("capabilities", [])

    def integration_has(self, integration: str, capability: str) -> bool:
        item = self.raw.get("integrations", {}).get(integration, {})
        return item.get("status") in VERIFIED_STATUSES and capability in item.get("capabilities", [])

    def status(self, section: str, name: str) -> str:
        return self.raw.get(section, {}).get(name, {}).get("status", "missing")
