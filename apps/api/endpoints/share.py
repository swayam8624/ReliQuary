"""Cross-device share links for ReliQuary secrets."""

from __future__ import annotations

from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field

from apps.api.endpoints.vault import get_vault_manager
from apps.api.services.share_links import share_link_store
from vaults.manager import VaultManager


router = APIRouter(prefix="/share", tags=["share"])


class ShareCreateRequest(BaseModel):
    vault_id: str = Field(..., min_length=1)
    secret_name: str = Field(..., min_length=1)
    created_by: str = Field(..., min_length=1)
    ttl_minutes: int = Field(default=60, ge=1, le=1440)
    max_views: int = Field(default=1, ge=1, le=25)
    share_password: Optional[str] = Field(default=None, min_length=8, max_length=512)


class ShareCreateResponse(BaseModel):
    token: str
    share_url: str
    expires_at: datetime
    max_views: int


class ShareOpenRequest(BaseModel):
    share_password: Optional[str] = Field(default=None, min_length=8, max_length=512)
    access_password: Optional[str] = Field(default=None, min_length=8, max_length=512)


class ShareOpenResponse(BaseModel):
    vault_id: str
    secret_name: str
    secret_value: str
    metadata: dict
    remaining_views: int


@router.post("/create", response_model=ShareCreateResponse)
async def create_share_link(
    request: ShareCreateRequest,
    vault_manager: VaultManager = Depends(get_vault_manager),
):
    if not vault_manager.get_vault(request.vault_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Vault not found")
    link = share_link_store.create(
        vault_id=request.vault_id,
        secret_name=request.secret_name,
        created_by=request.created_by,
        ttl_minutes=request.ttl_minutes,
        max_views=request.max_views,
        share_password=request.share_password,
    )
    return ShareCreateResponse(
        token=link.token,
        share_url=f"/share/{link.token}",
        expires_at=datetime.fromisoformat(link.expires_at),
        max_views=link.max_views,
    )


@router.post("/{token}", response_model=ShareOpenResponse)
async def open_share_link(
    token: str,
    request: ShareOpenRequest,
    vault_manager: VaultManager = Depends(get_vault_manager),
):
    try:
        link = share_link_store.consume(token, share_password=request.share_password)
        secret = vault_manager.retrieve_secret(
            link.vault_id,
            link.secret_name,
            access_password=request.access_password,
        )
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(exc)) from exc
    return ShareOpenResponse(
        vault_id=link.vault_id,
        secret_name=link.secret_name,
        secret_value=secret.secret_value,
        metadata=secret.metadata,
        remaining_views=max(0, link.max_views - link.view_count),
    )
