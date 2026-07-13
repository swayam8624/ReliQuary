"""
Agent API endpoints for ReliQuary.
"""

import logging
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status

from apps.api.schemas.agent import (
    AgentCapabilities,
    AgentDecisionRequest,
    AgentDecisionResponse,
    AgentHeartbeatRequest,
    AgentHeartbeatResponse,
    AgentInfo,
    AgentListResponse,
    AgentMetrics,
    AgentRegistrationRequest,
    AgentRegistrationResponse,
    AgentRole,
    AgentStatus,
)
from apps.api.services.agent_orchestrator import (
    AgentOrchestrator,
    AgentRequest,
    DecisionType,
    get_agent_orchestrator,
)
from apps.api.services.agent_registry import AgentRegistry

router = APIRouter(prefix="/agents", tags=["agents"])
logger = logging.getLogger(__name__)

_agent_registry = None


async def get_orchestrator() -> AgentOrchestrator:
    return get_agent_orchestrator()


async def get_registry() -> AgentRegistry:
    global _agent_registry
    if _agent_registry is None:
        _agent_registry = AgentRegistry()
    return _agent_registry


def _agent_info_from_record(record: dict) -> AgentInfo:
    return AgentInfo(
        agent_id=record["agent_id"],
        role=AgentRole(record["role"]),
        status=AgentStatus(record["status"]),
        capabilities=AgentCapabilities(**record["capabilities"]),
        metrics=AgentMetrics(**record.get("metrics", {})),
        last_heartbeat=datetime.fromisoformat(record["last_heartbeat"]),
        version=record["version"],
    )


@router.post("/register", response_model=AgentRegistrationResponse)
async def register_agent(
    request: AgentRegistrationRequest,
    registry: AgentRegistry = Depends(get_registry),
):
    """Register or update an agent in the local registry."""
    try:
        registry.upsert_agent(
            {
                "agent_id": request.agent_id,
                "role": request.role.value,
                "status": AgentStatus.ACTIVE.value,
                "capabilities": request.capabilities.model_dump(mode="json"),
                "metrics": AgentMetrics().model_dump(mode="json"),
                "version": request.version,
            }
        )
        return AgentRegistrationResponse(
            success=True,
            agent_id=request.agent_id,
            message="Agent registered successfully",
        )
    except Exception as e:
        logger.error("Agent registration failed: %s", e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Agent registration failed: {str(e)}",
        )


@router.post("/heartbeat", response_model=AgentHeartbeatResponse)
async def agent_heartbeat(
    request: AgentHeartbeatRequest,
    registry: AgentRegistry = Depends(get_registry),
):
    """Persist heartbeat status and metrics for a registered agent."""
    try:
        record = registry.heartbeat(
            request.agent_id,
            request.status.value,
            request.metrics.model_dump(mode="json"),
        )
        if record is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Agent '{request.agent_id}' is not registered",
            )
        return AgentHeartbeatResponse(
            success=True,
            agent_id=request.agent_id,
            next_heartbeat_interval=30,
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Agent heartbeat failed: %s", e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Agent heartbeat failed: {str(e)}",
        )


@router.post("/decision", response_model=AgentDecisionResponse)
async def request_agent_decision(
    request: AgentDecisionRequest,
    orchestrator: AgentOrchestrator = Depends(get_orchestrator),
):
    """Request a decision from the agent quorum."""
    try:
        agent_request = AgentRequest(
            request_id=request.request_id,
            decision_type=DecisionType.ACCESS_REQUEST,
            user_id=request.agent_id,
            resource_path="api/decision",
            context_data={**request.context_data, "trust_score": request.trust_score},
            timeout_seconds=request.timeout,
        )
        agent_response = await orchestrator.request_consensus(agent_request)
        return AgentDecisionResponse(
            request_id=agent_response.request_id,
            agent_id=request.agent_id,
            decision=agent_response.decision,
            confidence=agent_response.confidence_score,
            reasoning=[f"Decision made by {len(agent_response.participating_agents)} agents"],
            processing_time=agent_response.consensus_time_ms / 1000.0,
        )
    except Exception as e:
        logger.error("Agent decision request failed: %s", e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Agent decision request failed: {str(e)}",
        )


@router.get("/{agent_id}", response_model=AgentInfo)
async def get_agent_info(
    agent_id: str,
    registry: AgentRegistry = Depends(get_registry),
):
    """Get information about a registered agent."""
    try:
        record = registry.get(agent_id)
        if record is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Agent '{agent_id}' is not registered",
            )
        return _agent_info_from_record(record)
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to retrieve agent info: %s", e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve agent info: {str(e)}",
        )


@router.get("/", response_model=AgentListResponse)
async def list_agents(
    registry: AgentRegistry = Depends(get_registry),
):
    """List registered agents."""
    try:
        agents = [_agent_info_from_record(record) for record in registry.list()]
        return AgentListResponse(agents=agents, total_count=len(agents))
    except Exception as e:
        logger.error("Failed to list agents: %s", e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list agents: {str(e)}",
        )
