import sys
from pathlib import Path

from fastapi.testclient import TestClient

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from apps.api.endpoints import context as context_endpoint
from apps.api.endpoints import trust as trust_endpoint
from apps.api.main import app
from apps.api.services.context_verifier import ContextVerificationStore, ContextVerifier
from core.trust.scorer import TrustScoringEngine


def test_context_status_is_persisted_and_unknown_id_404(tmp_path, monkeypatch):
    store_path = tmp_path / "context.json"
    context_endpoint._context_verifier = ContextVerifier(
        store=ContextVerificationStore(str(store_path))
    )
    client = TestClient(app)

    response = client.post(
        "/context/verify",
        json={
            "user_id": "alice",
            "ip_address": "127.0.0.1",
            "user_agent": "pytest",
            "timestamp": "2026-07-13T00:00:00",
            "device_fingerprint": "device-1",
            "access_patterns": ["local-demo"],
        },
    )
    assert response.status_code == 200
    request_id = response.json()["request_id"]
    assert store_path.exists()

    stored = client.get(f"/context/verification/{request_id}")
    assert stored.status_code == 200
    assert stored.json()["request_id"] == request_id
    assert stored.json()["verified"] is True

    missing = client.get("/context/verification/ctx_missing")
    assert missing.status_code == 404


def test_deterministic_proof_verification_rejects_tampering():
    client = TestClient(app)
    generated = client.post(
        "/context/zk/generate",
        json={"circuit_name": "device_proof", "inputs": {"device": "mac"}},
    )
    assert generated.status_code == 200
    proof = generated.json()["proof"]

    valid = client.post("/context/zk/verify", json={"proof": proof})
    assert valid.status_code == 200
    assert valid.json()["valid"] is True

    proof["challenge"] = "tampered"
    invalid = client.post("/context/zk/verify", json={"proof": proof})
    assert invalid.status_code == 200
    assert invalid.json()["valid"] is False


def test_trust_profile_history_and_score_are_real_evaluations(tmp_path):
    trust_endpoint._trust_engine = TrustScoringEngine(history_path=str(tmp_path / "trust.json"))
    client = TestClient(app)

    payload = {
        "request_id": "trust-1",
        "user_id": "alice",
        "context_data": {
            "verified": True,
            "confidence_score": 0.92,
            "risk_assessment": {"risk_level": "low"},
        },
    }
    evaluation = client.post("/trust/evaluate", json=payload)
    assert evaluation.status_code == 200
    trust_score = evaluation.json()["evaluation"]["overall_trust_score"]
    assert trust_score > 0

    profile = client.get("/trust/profile/alice")
    assert profile.status_code == 200
    assert profile.json()["found"] is True
    assert profile.json()["profile"]["total_evaluations"] == 1
    assert profile.json()["profile"]["current_trust_score"] == trust_score

    history = client.post("/trust/history", json={"user_id": "alice", "limit": 10})
    assert history.status_code == 200
    assert history.json()["total_records"] == 1

    score = client.get("/trust/score/alice")
    assert score.status_code == 200
    assert score.json()["trust_score"] == trust_score

    missing = client.get("/trust/score/nobody")
    assert missing.status_code == 404
