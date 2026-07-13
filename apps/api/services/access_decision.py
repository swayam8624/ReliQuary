"""Trust-gated access decisions for ReliQuary vault contents."""

from __future__ import annotations

import json
import os
import uuid
from collections import deque
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Deque, Dict, List, Literal, Optional


Sensitivity = Literal["public", "private", "sensitive", "secret", "sealed"]
Decision = Literal["allow", "redact", "deny"]
VisibleResult = Literal["full", "metadata_only", "existence_only", "none"]


SENSITIVITY_THRESHOLDS: Dict[Sensitivity, int] = {
    "public": 0,
    "private": 50,
    "sensitive": 75,
    "secret": 90,
    "sealed": 101,
}


@dataclass
class AccessSubject:
    user_id: str
    device_verified: bool = False
    local_session: bool = False
    biometric_verified: bool = False
    remote_address: str = "127.0.0.1"
    user_agent: str = "reliquary-local-client"


@dataclass
class AccessResource:
    vault_id: str
    owner_id: str
    name: str
    sensitivity: Sensitivity = "private"
    resource_type: str = "secret"
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class AccessDecisionRecord:
    event_id: str
    timestamp: str
    decision: Decision
    visible_result: VisibleResult
    trust_score: int
    required_score: int
    sensitivity: Sensitivity
    subject_user_id: str
    owner_id: str
    vault_id: str
    resource_name: str
    resource_type: str
    reasons: List[str]
    audit_label: str


class AccessEventStore:
    """In-memory event queue plus JSONL audit output for visualizers."""

    def __init__(self, max_events: int = 250):
        self._events: Deque[AccessDecisionRecord] = deque(maxlen=max_events)
        self._log_path = Path(os.environ.get("RELIQUARY_ACCESS_EVENT_LOG", "logs/access_events.jsonl"))

    def append(self, event: AccessDecisionRecord) -> None:
        self._events.appendleft(event)
        try:
            self._log_path.parent.mkdir(parents=True, exist_ok=True)
            with self._log_path.open("a", encoding="utf-8") as handle:
                handle.write(json.dumps(asdict(event), sort_keys=True) + "\n")
        except OSError:
            pass

    def list_events(self, limit: int = 50) -> List[AccessDecisionRecord]:
        return list(self._events)[: max(1, min(limit, self._events.maxlen or limit))]


access_event_store = AccessEventStore()


class AccessDecisionEngine:
    """Evaluate what a caller can see for a vault resource."""

    def evaluate(
        self,
        subject: AccessSubject,
        resource: AccessResource,
        trust_score: int,
        requested_detail: str = "value",
    ) -> AccessDecisionRecord:
        normalized_score = max(0, min(100, int(trust_score)))
        required_score = SENSITIVITY_THRESHOLDS[resource.sensitivity]
        reasons: List[str] = []

        if resource.sensitivity == "sealed":
            reasons.append("sealed resources never reveal direct values")

        if subject.user_id != resource.owner_id and resource.sensitivity != "public":
            reasons.append("requesting user is not the vault owner")
            normalized_score = min(normalized_score, 40)

        if self._is_remote(subject.remote_address) and not subject.local_session:
            reasons.append("remote origin without local trusted session")
            normalized_score = max(0, normalized_score - 20)

        if resource.sensitivity in {"sensitive", "secret", "sealed"} and not subject.device_verified:
            reasons.append("device is not verified")
            normalized_score = max(0, normalized_score - 15)

        if resource.sensitivity in {"secret", "sealed"} and not subject.biometric_verified:
            reasons.append("biometric or explicit high-trust confirmation missing")
            normalized_score = max(0, normalized_score - 10)

        if normalized_score >= required_score and resource.sensitivity != "sealed":
            decision: Decision = "allow"
            visible_result: VisibleResult = "full"
            if not reasons:
                reasons.append("trust threshold met")
        elif normalized_score >= max(0, required_score - 25) or resource.sensitivity in {"public", "private"}:
            decision = "redact"
            visible_result = "metadata_only" if requested_detail in {"value", "path"} else "existence_only"
            reasons.append("trust below full reveal threshold")
        else:
            decision = "deny"
            visible_result = "none"
            reasons.append("trust below minimum disclosure threshold")

        record = AccessDecisionRecord(
            event_id=f"access_{uuid.uuid4().hex[:16]}",
            timestamp=datetime.now(timezone.utc).isoformat(),
            decision=decision,
            visible_result=visible_result,
            trust_score=normalized_score,
            required_score=required_score,
            sensitivity=resource.sensitivity,
            subject_user_id=subject.user_id,
            owner_id=resource.owner_id,
            vault_id=resource.vault_id,
            resource_name=resource.name,
            resource_type=resource.resource_type,
            reasons=reasons,
            audit_label=f"{decision}:{resource.sensitivity}:{resource.resource_type}",
        )
        access_event_store.append(record)
        return record

    @staticmethod
    def _is_remote(remote_address: str) -> bool:
        host = remote_address.split(":")[0].strip().lower()
        return host not in {"", "127.0.0.1", "localhost", "::1"}
