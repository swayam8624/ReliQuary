"""Trust-gated access API for vault resources."""

from __future__ import annotations

import asyncio
import json
from dataclasses import asdict
from datetime import datetime
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field

from apps.api.endpoints.vault import get_vault_manager
from apps.api.services.access_decision import (
    AccessDecisionEngine,
    AccessDecisionRecord,
    AccessResource,
    AccessSubject,
    Sensitivity,
    access_event_store,
)
from vaults.manager import VaultManager


router = APIRouter(prefix="/access", tags=["access"])


class AccessSubjectRequest(BaseModel):
    user_id: str = Field(..., min_length=1, max_length=100)
    device_verified: bool = False
    local_session: bool = False
    biometric_verified: bool = False
    remote_address: str = "127.0.0.1"
    user_agent: str = "reliquary-local-client"


class AccessEvaluateRequest(BaseModel):
    vault_id: str = Field(..., min_length=1)
    resource_name: str = Field(..., min_length=1, max_length=140)
    resource_type: str = Field(default="secret", max_length=50)
    sensitivity: Sensitivity = "private"
    requested_detail: str = Field(default="value", max_length=40)
    trust_score: int = Field(default=50, ge=0, le=100)
    subject: AccessSubjectRequest
    metadata: Optional[Dict[str, Any]] = None


class AccessDecisionResponse(BaseModel):
    event_id: str
    timestamp: datetime
    decision: str
    visible_result: str
    trust_score: int
    required_score: int
    sensitivity: str
    subject_user_id: str
    owner_id: str
    vault_id: str
    resource_name: str
    resource_type: str
    reasons: List[str]
    audit_label: str
    revealed_value: Optional[str] = None
    revealed_metadata: Optional[Dict[str, Any]] = None


class AccessEventsResponse(BaseModel):
    events: List[AccessDecisionResponse]


def get_access_engine() -> AccessDecisionEngine:
    return AccessDecisionEngine()


def _record_to_response(
    record: AccessDecisionRecord,
    revealed_value: Optional[str] = None,
    revealed_metadata: Optional[Dict[str, Any]] = None,
) -> AccessDecisionResponse:
    payload = asdict(record)
    payload["revealed_value"] = revealed_value
    payload["revealed_metadata"] = revealed_metadata
    return AccessDecisionResponse(**payload)


def _resource_from_vault(vault_manager: VaultManager, request: AccessEvaluateRequest) -> AccessResource:
    vault = vault_manager.get_vault(request.vault_id)
    if not vault:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Vault not found")
    return AccessResource(
        vault_id=request.vault_id,
        owner_id=vault.owner_id or vault.metadata.owner_did,
        name=request.resource_name,
        sensitivity=request.sensitivity,
        resource_type=request.resource_type,
        metadata=request.metadata or {},
    )


@router.post("/evaluate", response_model=AccessDecisionResponse)
async def evaluate_access(
    request: AccessEvaluateRequest,
    vault_manager: VaultManager = Depends(get_vault_manager),
    engine: AccessDecisionEngine = Depends(get_access_engine),
):
    """Evaluate whether a caller should see a resource."""
    resource = _resource_from_vault(vault_manager, request)
    record = engine.evaluate(
        subject=AccessSubject(**request.subject.model_dump()),
        resource=resource,
        trust_score=request.trust_score,
        requested_detail=request.requested_detail,
    )
    metadata = resource.metadata if record.visible_result in {"full", "metadata_only", "existence_only"} else None
    return _record_to_response(record, revealed_metadata=metadata)


@router.post("/request-secret", response_model=AccessDecisionResponse)
async def request_secret(
    request: AccessEvaluateRequest,
    vault_manager: VaultManager = Depends(get_vault_manager),
    engine: AccessDecisionEngine = Depends(get_access_engine),
):
    """Request a secret through the trust gate."""
    resource = _resource_from_vault(vault_manager, request)
    record = engine.evaluate(
        subject=AccessSubject(**request.subject.model_dump()),
        resource=resource,
        trust_score=request.trust_score,
        requested_detail=request.requested_detail,
    )

    revealed_value = None
    revealed_metadata = {"resource_name": request.resource_name, "resource_type": request.resource_type}
    if record.decision == "allow":
        try:
            secret = vault_manager.retrieve_secret(request.vault_id, request.resource_name)
        except ValueError as exc:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
        revealed_value = secret.secret_value
        revealed_metadata.update(secret.metadata or {})
    elif record.decision == "redact":
        revealed_metadata["redacted"] = True
    else:
        revealed_metadata = None

    return _record_to_response(record, revealed_value=revealed_value, revealed_metadata=revealed_metadata)


@router.get("/events", response_model=AccessEventsResponse)
async def list_access_events(limit: int = 50):
    """Return recent access decision events for dashboards and visualizers."""
    return AccessEventsResponse(events=[_record_to_response(event) for event in access_event_store.list_events(limit)])


@router.get("/stream")
async def stream_access_events(limit: int = 25):
    """SSE stream of recent access events.

    This intentionally replays recent events every few seconds so a visualizer can
    be started after a demo flow and still receive useful state.
    """

    async def event_generator():
        while True:
            events = [asdict(event) for event in access_event_store.list_events(limit)]
            yield f"event: access\n"
            yield f"data: {json.dumps({'events': events})}\n\n"
            await asyncio.sleep(2.0)

    return StreamingResponse(event_generator(), media_type="text/event-stream")
