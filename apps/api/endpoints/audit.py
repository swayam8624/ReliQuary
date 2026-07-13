"""
Audit API endpoints for ReliQuary.
"""

import logging
from datetime import UTC, datetime
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field

from apps.api.services.audit_store import AuditStore

router = APIRouter(prefix="/audit", tags=["audit"])
logger = logging.getLogger(__name__)

_audit_store = None


class AuditEvent(BaseModel):
    event_id: str
    timestamp: datetime
    level: str
    source: str
    action: str
    user_id: Optional[str] = None
    resource_id: Optional[str] = None
    details: Optional[Dict[str, Any]] = None
    ip_address: Optional[str] = None


class AuditLogResponse(BaseModel):
    """Response model for audit log retrieval."""

    events: List[AuditEvent]
    total_count: int
    limit: int
    offset: int
    timestamp: datetime = Field(default_factory=lambda: datetime.now(UTC))


class AuditVerificationRequest(BaseModel):
    """Request model for audit trail verification."""

    start_event_id: str
    end_event_id: str


class AuditVerificationResponse(BaseModel):
    """Response model for audit trail verification."""

    verified: bool
    verification_hash: str
    message: str
    timestamp: datetime = Field(default_factory=lambda: datetime.now(UTC))


async def get_audit_store() -> AuditStore:
    global _audit_store
    if _audit_store is None:
        _audit_store = AuditStore()
    return _audit_store


def _event_from_record(record: Dict[str, Any]) -> AuditEvent:
    return AuditEvent(
        event_id=record["event_id"],
        timestamp=datetime.fromisoformat(record["timestamp"].replace("Z", "")),
        level=record["level"],
        source=record["source"],
        action=record["action"],
        user_id=record.get("user_id"),
        resource_id=record.get("resource_id"),
        details=record.get("details"),
        ip_address=record.get("ip_address"),
    )


@router.get("/", response_model=AuditLogResponse)
async def get_audit_logs(
    start_time: Optional[datetime] = None,
    end_time: Optional[datetime] = None,
    level: Optional[str] = None,
    source: Optional[str] = None,
    user_id: Optional[str] = None,
    limit: int = Query(100, le=1000),
    offset: int = 0,
    audit_store: AuditStore = Depends(get_audit_store),
):
    """Retrieve audit logs with filtering options."""
    try:
        records = audit_store.events(
            start_time=start_time,
            end_time=end_time,
            level=level,
            source=source,
            user_id=user_id,
            limit=limit,
            offset=offset,
        )
        events = [_event_from_record(record) for record in records]
        return AuditLogResponse(
            events=events,
            total_count=len(events),
            limit=limit,
            offset=offset,
        )
    except Exception as e:
        logger.error("Failed to retrieve audit logs: %s", e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve audit logs: {str(e)}",
        )


@router.get("/events/{event_id}", response_model=AuditEvent)
async def get_audit_event(
    event_id: str,
    audit_store: AuditStore = Depends(get_audit_store),
):
    """Retrieve a specific audit event by ID."""
    try:
        record = audit_store.get_event(event_id)
        if record is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Audit event '{event_id}' was not found",
            )
        return _event_from_record(record)
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to retrieve audit event %s: %s", event_id, e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve audit event: {str(e)}",
        )


@router.post("/verify", response_model=AuditVerificationResponse)
async def verify_audit_trail(
    request: AuditVerificationRequest,
    audit_store: AuditStore = Depends(get_audit_store),
):
    """Verify that a requested audit event range exists in an intact Merkle log."""
    try:
        result = audit_store.verify_range(request.start_event_id, request.end_event_id)
        return AuditVerificationResponse(
            verified=result["verified"],
            verification_hash=result["hash"],
            message=result["message"],
        )
    except Exception as e:
        logger.error("Audit trail verification failed: %s", e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Audit trail verification failed: {str(e)}",
        )


@router.get("/summary")
async def get_audit_summary(
    start_time: Optional[datetime] = None,
    end_time: Optional[datetime] = None,
    level: Optional[str] = None,
    audit_store: AuditStore = Depends(get_audit_store),
):
    """Get a summary of real audit events in the Merkle log."""
    try:
        return audit_store.summary(start_time=start_time, end_time=end_time, level=level)
    except Exception as e:
        logger.error("Failed to generate audit summary: %s", e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate audit summary: {str(e)}",
        )
