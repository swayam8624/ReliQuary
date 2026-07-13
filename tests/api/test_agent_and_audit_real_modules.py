import sys
from pathlib import Path

from fastapi.testclient import TestClient

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from apps.api.endpoints import agent as agent_endpoint
from apps.api.endpoints import audit as audit_endpoint
from apps.api.main import app
from apps.api.services.agent_registry import AgentRegistry
from apps.api.services.audit_store import AuditStore


def test_agent_registry_drives_register_heartbeat_get_and_list(tmp_path):
    agent_endpoint._agent_registry = AgentRegistry(str(tmp_path / "agents.json"))
    client = TestClient(app)

    registration = client.post(
        "/agents/register",
        json={
            "agent_id": "strict-local",
            "role": "strict",
            "version": "1.0.0",
            "capabilities": {
                "roles": ["strict"],
                "max_concurrent_tasks": 3,
                "supported_verification_types": ["device"],
                "trust_scoring_enabled": True,
                "consensus_participation": True,
                "specializations": ["vault"],
            },
        },
    )
    assert registration.status_code == 200

    heartbeat = client.post(
        "/agents/heartbeat",
        json={
            "agent_id": "strict-local",
            "status": "busy",
            "metrics": {
                "total_tasks_processed": 2,
                "successful_verifications": 2,
                "failed_verifications": 0,
                "average_response_time": 0.2,
                "current_load": 1,
                "uptime": 12.0,
            },
        },
    )
    assert heartbeat.status_code == 200

    fetched = client.get("/agents/strict-local")
    assert fetched.status_code == 200
    assert fetched.json()["status"] == "busy"
    assert fetched.json()["metrics"]["total_tasks_processed"] == 2

    listed = client.get("/agents/")
    assert listed.status_code == 200
    assert listed.json()["total_count"] == 1

    missing = client.get("/agents/missing-agent")
    assert missing.status_code == 404


def test_audit_endpoints_read_and_verify_real_merkle_log(tmp_path):
    audit_endpoint._audit_store = AuditStore(str(tmp_path / "api.log"))
    audit_endpoint._audit_store.writer.add_entry(
        {
            "event_id": "evt-one",
            "level": "info",
            "source": "pytest",
            "action": "vault_create",
            "user_id": "alice",
        }
    )
    audit_endpoint._audit_store.writer.add_entry(
        {
            "event_id": "evt-two",
            "level": "warning",
            "source": "pytest",
            "action": "trust_denied",
            "user_id": "alice",
        }
    )
    client = TestClient(app)

    logs = client.get("/audit/?source=pytest")
    assert logs.status_code == 200
    assert logs.json()["total_count"] == 2

    event = client.get("/audit/events/evt-one")
    assert event.status_code == 200
    assert event.json()["action"] == "vault_create"

    verification = client.post(
        "/audit/verify",
        json={"start_event_id": "evt-one", "end_event_id": "evt-two"},
    )
    assert verification.status_code == 200
    assert verification.json()["verified"] is True
    assert verification.json()["verification_hash"]

    missing = client.get("/audit/events/does-not-exist")
    assert missing.status_code == 404

    summary = client.get("/audit/summary")
    assert summary.status_code == 200
    assert summary.json()["total_events"] == 2
    assert summary.json()["integrity_verified"] is True
