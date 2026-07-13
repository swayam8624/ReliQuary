import sys
from pathlib import Path

from fastapi.testclient import TestClient

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from apps.api.endpoints import vault as vault_endpoint
from apps.api.main import app


def _client_with_fresh_vault():
    vault_endpoint._vault_manager = None
    client = TestClient(app)
    vault = client.post(
        "/vaults/",
        json={"name": "brain-vault", "description": "trust demo", "owner_id": "alice"},
    ).json()
    client.post(
        f"/vaults/secrets?vault_id={vault['vault_id']}",
        json={
            "secret_name": "apple-password-note",
            "secret_value": "high-value-secret",
            "metadata": {"category": "credential"},
        },
    )
    return client, vault["vault_id"]


def test_access_allows_high_trust_owner_secret_request():
    client, vault_id = _client_with_fresh_vault()

    response = client.post(
        "/access/request-secret",
        json={
            "vault_id": vault_id,
            "resource_name": "apple-password-note",
            "sensitivity": "secret",
            "trust_score": 99,
            "subject": {
                "user_id": "alice",
                "device_verified": True,
                "local_session": True,
                "biometric_verified": True,
                "remote_address": "127.0.0.1",
            },
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert body["decision"] == "allow"
    assert body["visible_result"] == "full"
    assert body["revealed_value"] == "high-value-secret"


def test_access_denies_low_trust_remote_secret_request():
    client, vault_id = _client_with_fresh_vault()

    response = client.post(
        "/access/request-secret",
        json={
            "vault_id": vault_id,
            "resource_name": "apple-password-note",
            "sensitivity": "secret",
            "trust_score": 55,
            "subject": {
                "user_id": "mallory",
                "device_verified": False,
                "local_session": False,
                "biometric_verified": False,
                "remote_address": "203.0.113.10",
            },
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert body["decision"] == "deny"
    assert body["visible_result"] == "none"
    assert body["revealed_value"] is None
    assert any("not the vault owner" in reason for reason in body["reasons"])


def test_access_redacts_near_threshold_sensitive_request():
    client, vault_id = _client_with_fresh_vault()

    response = client.post(
        "/access/evaluate",
        json={
            "vault_id": vault_id,
            "resource_name": "work-file-path",
            "resource_type": "file_path",
            "sensitivity": "sensitive",
            "trust_score": 68,
            "subject": {
                "user_id": "alice",
                "device_verified": True,
                "local_session": True,
                "biometric_verified": False,
                "remote_address": "127.0.0.1",
            },
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert body["decision"] == "redact"
    assert body["visible_result"] == "metadata_only"


def test_access_events_are_available_for_visualizers():
    client, vault_id = _client_with_fresh_vault()
    client.post(
        "/access/evaluate",
        json={
            "vault_id": vault_id,
            "resource_name": "public-readme",
            "resource_type": "file_path",
            "sensitivity": "public",
            "trust_score": 5,
            "subject": {"user_id": "guest"},
        },
    )

    response = client.get("/access/events")

    assert response.status_code == 200
    assert response.json()["events"]
