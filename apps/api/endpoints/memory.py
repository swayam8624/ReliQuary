"""Permissioned local memory retrieval API."""

from __future__ import annotations

from typing import List

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field

from apps.api.endpoints.access import AccessSubjectRequest
from apps.api.services.access_decision import AccessSubject, Sensitivity
from apps.api.services.local_retrieval import LocalFolderConnector, retrieval_catalog


router = APIRouter(prefix="/memory", tags=["memory"])


class IndexLocalFolderRequest(BaseModel):
    root_path: str = Field(..., min_length=1)
    vault_id: str = Field(..., min_length=1)
    owner_id: str = Field(..., min_length=1)
    sensitivity: Sensitivity = "private"
    max_files: int = Field(default=250, ge=1, le=5000)


class IndexLocalFolderResponse(BaseModel):
    indexed_count: int
    connector: str


class MemoryQueryRequest(BaseModel):
    query: str = Field(..., min_length=1)
    subject: AccessSubjectRequest
    trust_score: int = Field(default=50, ge=0, le=100)
    limit: int = Field(default=10, ge=1, le=50)


class MemoryQueryResponse(BaseModel):
    query: str
    results: List[dict]


@router.post("/index/local-folder", response_model=IndexLocalFolderResponse)
async def index_local_folder(request: IndexLocalFolderRequest):
    """Index a user-selected local folder as permissioned memory metadata."""
    try:
        entries = LocalFolderConnector().scan(
            root_path=request.root_path,
            vault_id=request.vault_id,
            owner_id=request.owner_id,
            sensitivity=request.sensitivity,
            max_files=request.max_files,
        )
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    retrieval_catalog.add_entries(entries)
    return IndexLocalFolderResponse(indexed_count=len(entries), connector="local-folder")


@router.post("/query", response_model=MemoryQueryResponse)
async def query_memory(request: MemoryQueryRequest):
    """Search indexed local memory and reveal paths only when policy allows."""
    results = retrieval_catalog.query_with_policy(
        query=request.query,
        subject=AccessSubject(**request.subject.model_dump()),
        trust_score=request.trust_score,
        limit=request.limit,
    )
    return MemoryQueryResponse(query=request.query, results=results)
