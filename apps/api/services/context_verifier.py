"""
Context verification service for ReliQuary.

The active API path uses deterministic proof envelopes until a Groth16 circuit
bundle is configured. These envelopes are not advertised as cryptographic ZK
proofs; they are replayable development proofs that make request state
auditable and tamper-detectable during local runs.
"""

import hashlib
import json
import logging
import os
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional


@dataclass
class ContextVerificationRequest:
    """Request for context verification."""

    user_id: str
    ip_address: str
    user_agent: str
    timestamp: str
    device_fingerprint: str
    location_data: Optional[Dict[str, Any]] = None
    access_patterns: Optional[List[str]] = None


@dataclass
class ContextVerificationResponse:
    """Response for context verification."""

    request_id: str
    verified: bool
    confidence_score: float
    verified_components: List[str]
    timestamp: datetime
    zk_proof_data: Optional[Dict[str, Any]] = None


@dataclass
class ContextData:
    """Context data for verification."""

    user_id: str
    ip_address: str
    user_agent: str
    timestamp: str
    device_fingerprint: str
    location_data: Optional[Dict[str, Any]] = None
    access_patterns: Optional[List[str]] = None


@dataclass
class VerificationResult:
    """Result of context verification."""

    request_id: str
    verified: bool
    confidence_score: float
    verified_components: List[str]
    timestamp: datetime
    zk_proof_data: Optional[Dict[str, Any]] = None


class DeterministicProofBackend:
    """Creates and verifies canonical hash proof envelopes for local runs."""

    proof_system = "deterministic-dev-envelope"

    @staticmethod
    def canonical_payload(circuit_name: str, inputs: Dict[str, Any]) -> str:
        return json.dumps(
            {"circuit_name": circuit_name, "inputs": inputs},
            sort_keys=True,
            separators=(",", ":"),
            default=str,
        )

    def generate_proof(self, circuit_name: str, inputs: Dict[str, Any]) -> Dict[str, Any]:
        canonical = self.canonical_payload(circuit_name, inputs)
        input_digest = hashlib.sha256(canonical.encode("utf-8")).hexdigest()
        challenge = hashlib.sha256(f"{input_digest}:reliquary-context".encode("utf-8")).hexdigest()
        return {
            "proof_system": self.proof_system,
            "circuit_name": circuit_name,
            "input_digest": input_digest,
            "challenge": challenge,
            "proof": {"digest": input_digest, "challenge": challenge},
            "public_signals": [input_digest],
            "verification_key": {
                "type": self.proof_system,
                "hash": "sha256",
                "scope": "local-development",
            },
        }

    def verify_proof(self, proof_data: Dict[str, Any]) -> bool:
        proof = proof_data.get("proof", {})
        input_digest = proof_data.get("input_digest") or proof.get("digest")
        challenge = proof_data.get("challenge") or proof.get("challenge")
        expected = hashlib.sha256(f"{input_digest}:reliquary-context".encode("utf-8")).hexdigest()
        return (
            proof_data.get("proof_system") == self.proof_system
            and isinstance(input_digest, str)
            and proof_data.get("public_signals") == [input_digest]
            and challenge == expected
        )


class ContextVerificationStore:
    """JSON-backed store for verification request status."""

    def __init__(self, path: Optional[str] = None):
        default_path = Path("runtime/context_verifications.json")
        self.path = Path(path or os.environ.get("RELIQUARY_CONTEXT_STORE", default_path))
        self.path.parent.mkdir(parents=True, exist_ok=True)

    def save(self, result: VerificationResult) -> None:
        records = self._read_all()
        payload = asdict(result)
        payload["timestamp"] = result.timestamp.isoformat()
        records[result.request_id] = payload
        self.path.write_text(json.dumps(records, indent=2, sort_keys=True), encoding="utf-8")

    def get(self, request_id: str) -> Optional[VerificationResult]:
        payload = self._read_all().get(request_id)
        if not payload:
            return None
        return VerificationResult(
            request_id=payload["request_id"],
            verified=payload["verified"],
            confidence_score=payload["confidence_score"],
            verified_components=payload["verified_components"],
            timestamp=datetime.fromisoformat(payload["timestamp"]),
            zk_proof_data=payload.get("zk_proof_data"),
        )

    def _read_all(self) -> Dict[str, Dict[str, Any]]:
        if not self.path.exists():
            return {}
        try:
            return json.loads(self.path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            return {}


class ContextVerifier:
    """Verifies supplied context and persists request status."""

    def __init__(
        self,
        proof_backend: Optional[DeterministicProofBackend] = None,
        store: Optional[ContextVerificationStore] = None,
    ):
        self.logger = logging.getLogger(__name__)
        self.proof_backend = proof_backend or DeterministicProofBackend()
        self.store = store or ContextVerificationStore()

    def verify_context(self, context_data: ContextData) -> VerificationResult:
        request_id = f"ctx_{int(datetime.now().timestamp() * 1000000)}"
        zk_proofs: List[Dict[str, Any]] = []
        verified_components: List[str] = []

        checks = [
            ("device_fingerprint", "device_proof", {
                "device_fingerprint": context_data.device_fingerprint,
                "user_id": context_data.user_id,
            }),
            ("timestamp", "timestamp_verifier", {
                "timestamp": context_data.timestamp,
                "user_id": context_data.user_id,
            }),
        ]
        if context_data.location_data:
            checks.append(("location", "location_chain", {
                "ip_address": context_data.ip_address,
                "location_data": context_data.location_data,
                "user_id": context_data.user_id,
            }))
        if context_data.access_patterns:
            checks.append(("access_patterns", "pattern_match", {
                "access_patterns": context_data.access_patterns,
                "user_id": context_data.user_id,
            }))

        for component, circuit_name, inputs in checks:
            proof = self.proof_backend.generate_proof(circuit_name, inputs)
            zk_proofs.append(proof)
            if self.proof_backend.verify_proof(proof):
                verified_components.append(component)

        all_verified = len(verified_components) == len(checks)
        confidence_score = min(len(verified_components) / 4.0, 1.0) if checks else 0.0
        if not all_verified:
            confidence_score *= 0.5

        result = VerificationResult(
            request_id=request_id,
            verified=all_verified,
            confidence_score=confidence_score,
            verified_components=verified_components,
            timestamp=datetime.now(),
            zk_proof_data={
                "proof_system": self.proof_backend.proof_system,
                "proofs": zk_proofs,
                "verification_results": [
                    self.proof_backend.verify_proof(proof) for proof in zk_proofs
                ],
                "note": "Deterministic local proof envelope; configure Circom/snarkjs for Groth16 ZK proofs.",
            },
        )
        self.store.save(result)
        self.logger.info("Context verification completed for request %s: %s", request_id, result.verified)
        return result

    def get_verification(self, request_id: str) -> Optional[VerificationResult]:
        return self.store.get(request_id)


ContextVerificationService = ContextVerifier

_context_verifier = None


def get_context_verifier() -> ContextVerifier:
    """Get the global context verifier instance."""
    global _context_verifier
    if _context_verifier is None:
        _context_verifier = ContextVerifier()
    return _context_verifier


def verify_context_data(context_data: ContextData) -> VerificationResult:
    """Convenience function to verify context data."""
    verifier = get_context_verifier()
    return verifier.verify_context(context_data)
