"""Audit log reader backed by the Merkle log writer."""

import hashlib
import os
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from core.merkle_logging.writer import MerkleLogWriter


class AuditStore:
    """Read and verify API audit entries from a local Merkle log."""

    def __init__(self, path: Optional[str] = None):
        default_path = Path("logs/api.log")
        self.path = str(path or os.environ.get("RELIQUARY_AUDIT_LOG", default_path))
        self.writer = MerkleLogWriter(self.path)

    def events(
        self,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        level: Optional[str] = None,
        source: Optional[str] = None,
        user_id: Optional[str] = None,
        limit: int = 100,
        offset: int = 0,
    ) -> List[Dict[str, Any]]:
        records = [self._normalise(index, entry.data) for index, entry in enumerate(self.writer._entries_cache)]
        filtered = []
        for record in records:
            timestamp = datetime.fromisoformat(record["timestamp"].replace("Z", ""))
            if start_time and timestamp < start_time:
                continue
            if end_time and timestamp > end_time:
                continue
            if level and record["level"].lower() != level.lower():
                continue
            if source and record["source"] != source:
                continue
            if user_id and record.get("user_id") != user_id:
                continue
            filtered.append(record)
        return filtered[offset: offset + limit]

    def get_event(self, event_id: str) -> Optional[Dict[str, Any]]:
        for record in self.events(limit=10000):
            if record["event_id"] == event_id:
                return record
        return None

    def verify_range(self, start_event_id: str, end_event_id: str) -> Dict[str, Any]:
        events = self.events(limit=10000)
        ids = [event["event_id"] for event in events]
        if start_event_id not in ids or end_event_id not in ids:
            return {"verified": False, "hash": "", "message": "One or both audit event IDs were not found."}
        start_index = ids.index(start_event_id)
        end_index = ids.index(end_event_id)
        if start_index > end_index:
            start_index, end_index = end_index, start_index
        selected = events[start_index: end_index + 1]
        digest = hashlib.sha256(
            "|".join(event["event_id"] for event in selected).encode("utf-8")
        ).hexdigest()
        return {
            "verified": self.writer.verify_log_integrity(),
            "hash": digest,
            "message": "Audit range is present and the Merkle log integrity check passed."
            if self.writer.verify_log_integrity()
            else "Audit range is present but the Merkle log integrity check failed.",
        }

    def summary(
        self,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        level: Optional[str] = None,
    ) -> Dict[str, Any]:
        events = self.events(start_time=start_time, end_time=end_time, level=level, limit=10000)
        by_level: Dict[str, int] = {}
        by_source: Dict[str, int] = {}
        users = set()
        for event in events:
            by_level[event["level"]] = by_level.get(event["level"], 0) + 1
            by_source[event["source"]] = by_source.get(event["source"], 0) + 1
            if event.get("user_id"):
                users.add(event["user_id"])
        return {
            "total_events": len(events),
            "events_by_level": by_level,
            "events_by_source": by_source,
            "unique_users": len(users),
            "integrity_verified": self.writer.verify_log_integrity(),
            "merkle_root": self.writer.merkle_root.hex() if self.writer.merkle_root else None,
            "time_range": {
                "start": start_time.isoformat() if start_time else None,
                "end": end_time.isoformat() if end_time else None,
            },
        }

    @staticmethod
    def _normalise(index: int, data: Dict[str, Any]) -> Dict[str, Any]:
        timestamp = data.get("timestamp") or datetime.now(UTC).isoformat()
        action = data.get("action") or data.get("event") or "unknown"
        event_id = data.get("event_id") or hashlib.sha256(
            f"{index}:{timestamp}:{action}".encode("utf-8")
        ).hexdigest()[:24]
        return {
            "event_id": event_id,
            "timestamp": timestamp,
            "level": str(data.get("level", data.get("status", "info"))).upper(),
            "source": data.get("source", "api"),
            "action": action,
            "user_id": data.get("user_id"),
            "resource_id": data.get("resource_id") or data.get("vault_id"),
            "details": data,
            "ip_address": data.get("ip_address"),
        }
