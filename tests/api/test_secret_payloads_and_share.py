import sys
from pathlib import Path

from fastapi.testclient import TestClient

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from apps.api.endpoints import vault as vault_endpoint
from apps.api.services import share_links
from apps.api.services.share_links import ShareLinkStore
from apps.api.main import app


def _fresh_client(tmp_path, monkeypatch):
    vault_endpoint._vault_manager = None
    monkeypatch.setattr(share_links, "share_link_store", ShareLinkStore(str(tmp_path / "shares.json")))
    import apps.api.endpoints.share as share_endpoint

    monkeypatch.setattr(share_endpoint, "share_link_store", share_links.share_link_store)
    client = TestClient(app)
    vault = client.post(
        "/vaults/",
        json={"name": "payload-vault", "description": "payload test", "owner_id": "alice"},
    ).json()
    return client, vault["vault_id"]


def test_secret_specific_password_is_required(tmp_path, monkeypatch):
    client, vault_id = _fresh_client(tmp_path, monkeypatch)

    stored = client.post(
        f"/vaults/secrets?vault_id={vault_id}",
        json={
            "secret_name": "phone-pin",
            "secret_value": "123456",
            "access_password": "specific-password",
        },
    )
    assert stored.status_code == 201
    assert stored.json()["metadata"]["password_required"] is True

    denied = client.post(
        "/access/request-secret",
        json={
            "vault_id": vault_id,
            "resource_name": "phone-pin",
            "sensitivity": "secret",
            "trust_score": 99,
            "subject": {
                "user_id": "alice",
                "device_verified": True,
                "local_session": True,
                "biometric_verified": True,
            },
        },
    )
    assert denied.status_code == 403

    allowed = client.post(
        "/access/request-secret",
        json={
            "vault_id": vault_id,
            "resource_name": "phone-pin",
            "sensitivity": "secret",
            "trust_score": 99,
            "access_password": "specific-password",
            "subject": {
                "user_id": "alice",
                "device_verified": True,
                "local_session": True,
                "biometric_verified": True,
            },
        },
    )
    assert allowed.status_code == 200
    assert allowed.json()["revealed_value"] == "123456"


def test_file_secret_and_share_link_flow(tmp_path, monkeypatch):
    client, vault_id = _fresh_client(tmp_path, monkeypatch)
    secret_file = tmp_path / "recovery-code.txt"
    secret_file.write_text("RECOVERY-CODE-001", encoding="utf-8")

    stored = client.post(
        f"/vaults/secrets/file?vault_id={vault_id}",
        json={
            "secret_name": "recovery-file",
            "path": str(secret_file),
            "sensitivity": "secret",
            "access_password": "file-password",
        },
    )
    assert stored.status_code == 201
    assert stored.json()["metadata"]["secret_kind"] == "file"

    share = client.post(
        "/share/create",
        json={
            "vault_id": vault_id,
            "secret_name": "recovery-file",
            "created_by": "alice",
            "ttl_minutes": 30,
            "max_views": 1,
            "share_password": "share-pass",
        },
    )
    assert share.status_code == 200
    token = share.json()["token"]

    opened = client.post(
        f"/share/{token}",
        json={"share_password": "share-pass", "access_password": "file-password"},
    )
    assert opened.status_code == 200
    assert opened.json()["metadata"]["file_name"] == "recovery-code.txt"
    assert opened.json()["remaining_views"] == 0

    second = client.post(
        f"/share/{token}",
        json={"share_password": "share-pass", "access_password": "file-password"},
    )
    assert second.status_code == 403
