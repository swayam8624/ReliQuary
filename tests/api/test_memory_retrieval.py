from pathlib import Path

from fastapi.testclient import TestClient

from apps.api.endpoints import memory as memory_endpoint
from apps.api.services.local_retrieval import RetrievalCatalog
from apps.api.main import app


def test_local_memory_query_reveals_path_only_when_trusted(tmp_path, monkeypatch):
    catalog_path = tmp_path / "catalog.json"
    monkeypatch.setattr(memory_endpoint, "retrieval_catalog", RetrievalCatalog(str(catalog_path)))

    docs = tmp_path / "docs"
    docs.mkdir()
    target = docs / "passport_scan.txt"
    target.write_text("placeholder", encoding="utf-8")

    client = TestClient(app)
    index_response = client.post(
        "/memory/index/local-folder",
        json={
            "root_path": str(docs),
            "vault_id": "vault-local-1",
            "owner_id": "alice",
            "sensitivity": "secret",
        },
    )
    assert index_response.status_code == 200
    assert index_response.json()["indexed_count"] == 1

    allowed = client.post(
        "/memory/query",
        json={
            "query": "passport",
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
    assert allowed.status_code == 200
    assert allowed.json()["results"][0]["decision"] == "allow"
    assert allowed.json()["results"][0]["path"] == str(target)

    denied = client.post(
        "/memory/query",
        json={
            "query": "passport",
            "trust_score": 20,
            "subject": {
                "user_id": "mallory",
                "device_verified": False,
                "local_session": False,
                "remote_address": "203.0.113.44",
            },
        },
    )
    assert denied.status_code == 200
    assert denied.json()["results"][0]["decision"] == "deny"
    assert "path" not in denied.json()["results"][0]
