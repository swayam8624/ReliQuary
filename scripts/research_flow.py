#!/usr/bin/env python
"""Run the local ReliQuary research flow without starting a server.

This script exercises the FastAPI app in-process so a fresh clone can produce a
real result quickly: vault creation, context verification, trust evaluation, and
agent quorum decision.
"""

from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

from fastapi.testclient import TestClient

ROOT_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT_DIR))

from apps.api.main import app


def print_step(title: str, payload: dict) -> None:
    print(f"\n== {title} ==")
    print(json.dumps(payload, indent=2, default=str))


def main() -> None:
    client = TestClient(app)
    timestamp = datetime.now(timezone.utc).isoformat()

    vault_response = client.post(
        "/vaults/",
        json={
            "name": "research-vault",
            "description": "Local ReliQuary research flow",
            "owner_id": "alice",
        },
    )
    vault_response.raise_for_status()
    vault = vault_response.json()
    print_step("vault created", vault)

    context_response = client.post(
        "/context/verify",
        json={
            "user_id": "alice",
            "ip_address": "127.0.0.1",
            "user_agent": "reliquary-research-client/1.0",
            "timestamp": timestamp,
            "device_fingerprint": "local-device",
            "metadata": {"flow": "research_flow.py"},
        },
    )
    context_response.raise_for_status()
    context = context_response.json()
    print_step("context verified", context)

    trust_response = client.post(
        "/trust/evaluate",
        json={
            "request_id": "trust-local-1",
            "user_id": "alice",
            "context_data": {
                "verified": context["verified"],
                "confidence_score": context["confidence_score"],
            },
        },
    )
    trust_response.raise_for_status()
    trust = trust_response.json()
    print_step("trust evaluated", trust)

    agent_response = client.post(
        "/agents/decision",
        json={
            "request_id": "agent-local-1",
            "agent_id": "alice",
            "context_data": {
                "vault_id": vault["vault_id"],
                "context_verified": context["verified"],
                "context_confidence": context["confidence_score"],
                "trust_score": trust["evaluation"]["overall_trust_score"],
            },
            "trust_score": trust["evaluation"]["overall_trust_score"],
            "timeout": 10,
        },
    )
    agent_response.raise_for_status()
    print_step("agent quorum decision", agent_response.json())


if __name__ == "__main__":
    main()
