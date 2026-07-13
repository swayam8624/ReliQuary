"""Persistent local agent registry for the API."""

import json
import os
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Dict, List, Optional


class AgentRegistry:
    """JSON-backed registry for registered agents and heartbeats."""

    def __init__(self, path: Optional[str] = None):
        default_path = Path("runtime/agents.json")
        self.path = Path(path or os.environ.get("RELIQUARY_AGENT_REGISTRY", default_path))
        self.path.parent.mkdir(parents=True, exist_ok=True)

    def upsert_agent(self, agent: Dict[str, Any]) -> Dict[str, Any]:
        agents = self._read_all()
        now = datetime.now(UTC).isoformat()
        existing = agents.get(agent["agent_id"], {})
        record = {
            **existing,
            **agent,
            "status": agent.get("status", existing.get("status", "active")),
            "metrics": agent.get("metrics", existing.get("metrics", {})),
            "registered_at": existing.get("registered_at", now),
            "last_heartbeat": agent.get("last_heartbeat", existing.get("last_heartbeat", now)),
        }
        agents[agent["agent_id"]] = record
        self._write_all(agents)
        return record

    def heartbeat(self, agent_id: str, status: str, metrics: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        agents = self._read_all()
        if agent_id not in agents:
            return None
        agents[agent_id]["status"] = status
        agents[agent_id]["metrics"] = metrics
        agents[agent_id]["last_heartbeat"] = datetime.now(UTC).isoformat()
        self._write_all(agents)
        return agents[agent_id]

    def get(self, agent_id: str) -> Optional[Dict[str, Any]]:
        return self._read_all().get(agent_id)

    def list(self) -> List[Dict[str, Any]]:
        return list(self._read_all().values())

    def _read_all(self) -> Dict[str, Dict[str, Any]]:
        if not self.path.exists():
            return {}
        try:
            return json.loads(self.path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            return {}

    def _write_all(self, agents: Dict[str, Dict[str, Any]]) -> None:
        self.path.write_text(json.dumps(agents, indent=2, sort_keys=True), encoding="utf-8")
