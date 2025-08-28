"""
Agent API Endpoints for ReliQuary

This module defines the FastAPI routes for agent-related operations
including agent registration, status updates, and decision requests.
"""

from typing import List, Optional
from fastapi import APIRouter, HTTPException, Depends, status
from pydantic import BaseModel
import logging

from ..schemas.agent import (
    AgentInfo, 
    AgentRegistrationRequest, 
    AgentRegistrationResponse,
    AgentHeartbeatRequest,
    AgentHeartbeatResponse,
    AgentDecisionRequest,
    AgentDecisionResponse,
    AgentListResponse
)
from ..services.agent_orchestrator import (
    AgentOrchestrator,
    AgentRequest,
    DecisionType,
    get_agent_orchestrator
)

# Create router
router = APIRouter(prefix="/agents", tags=["agents"])

# Initialize logger
logger = logging.getLogger(__name__)

# Dependency injection for agent orchestrator
async def get_orchestrator() -> AgentOrchestrator:
    return get_agent_orchestrator()


@router.post("/register", response_model=AgentRegistrationResponse)
async def register_agent(
    request: AgentRegistrationRequest,
    orchestrator: AgentOrchestrator = Depends(get_orchestrator)
):
    """
    Register a new agent in the system.
    
    Args:
        request: Agent registration request data
        
    Returns:
        AgentRegistrationResponse with registration status
    """
    try:
        # In a real implementation, this would register the agent
        # For now, we'll simulate successful registration
        logger.info(f"Registering agent {request.agent_id}")
        
        return AgentRegistrationResponse(
            success=True,
            agent_id=request.agent_id,
            message="Agent registered successfully"
        )
    except Exception as e:
        logger.error(f"Agent registration failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Agent registration failed: {str(e)}"
        )


@router.post("/heartbeat", response_model=AgentHeartbeatResponse)
async def agent_heartbeat(
    request: AgentHeartbeatRequest,
    orchestrator: AgentOrchestrator = Depends(get_orchestrator)
):
    """
    Receive heartbeat from an agent.
    
    Args:
        request: Agent heartbeat data
        
    Returns:
        AgentHeartbeatResponse with heartbeat status
    """
    try:
        # In a real implementation, this would update agent status
        # For now, we'll simulate successful heartbeat
        logger.info(f"Received heartbeat from agent {request.agent_id}")
        
        return AgentHeartbeatResponse(
            success=True,
            agent_id=request.agent_id,
            next_heartbeat_interval=30
        )
    except Exception as e:
        logger.error(f"Agent heartbeat failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Agent heartbeat failed: {str(e)}"
        )


@router.post("/decision", response_model=AgentDecisionResponse)
async def request_agent_decision(
    request: AgentDecisionRequest,
    orchestrator: AgentOrchestrator = Depends(get_orchestrator)
):
    """
    Request a decision from the agent quorum.
    
    Args:
        request: Agent decision request data
        
    Returns:
        AgentDecisionResponse with decision result
    """
    try:
        # Create agent request
        agent_request = AgentRequest(
            request_id=request.request_id,
            decision_type=DecisionType.ACCESS_REQUEST,
            user_id=request.agent_id,
            resource_path="api/decision",
            context_data=request.context_data,
            timeout_seconds=request.timeout
        )
        
        # Request consensus
        agent_response = await orchestrator.request_consensus(agent_request)
        
        return AgentDecisionResponse(
            request_id=agent_response.request_id,
            agent_id=request.agent_id,
            decision=agent_response.decision,
            confidence=agent_response.confidence_score,
            reasoning=[f"Decision made by {len(agent_response.participating_agents)} agents"],
            processing_time=agent_response.consensus_time_ms / 1000.0
        )
    except Exception as e:
        logger.error(f"Agent decision request failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Agent decision request failed: {str(e)}"
        )


@router.get("/{agent_id}", response_model=AgentInfo)
async def get_agent_info(
    agent_id: str,
    orchestrator: AgentOrchestrator = Depends(get_orchestrator)
):
    """
    Get information about a specific agent.
    
    Args:
        agent_id: ID of the agent to retrieve
        
    Returns:
        AgentInfo with agent details
    """
    try:
        # In a real implementation, this would retrieve agent info
        # For now, we'll simulate agent info
        from datetime import datetime
        from ...apps.api.schemas.agent import AgentRole, AgentStatus, AgentCapabilities, AgentMetrics
        
        agent_info = AgentInfo(
            agent_id=agent_id,
            role=AgentRole.NEUTRAL,
            status=AgentStatus.ACTIVE,
            capabilities=AgentCapabilities(
                roles=[AgentRole.NEUTRAL],
                max_concurrent_tasks=10,
                supported_verification_types=["device", "timestamp"],
                trust_scoring_enabled=True,
                consensus_participation=True,
                specializations=["general"]
            ),
            metrics=AgentMetrics(
                total_tasks_processed=0,
                successful_verifications=0,
                failed_verifications=0,
                average_response_time=0.0,
                current_load=0,
                uptime=0.0
            ),
            last_heartbeat=datetime.utcnow(),
            version="1.0.0"
        )
        
        return agent_info
    except Exception as e:
        logger.error(f"Failed to retrieve agent info: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve agent info: {str(e)}"
        )


@router.get("/", response_model=AgentListResponse)
async def list_agents(
    orchestrator: AgentOrchestrator = Depends(get_orchestrator)
):
    """
    List all agents in the system.
    
    Returns:
        AgentListResponse with list of agents
    """
    try:
        # In a real implementation, this would list all agents
        # For now, we'll simulate a list of agents
        from datetime import datetime
        from ...apps.api.schemas.agent import AgentRole, AgentStatus, AgentCapabilities, AgentMetrics
        
        agents = [
            AgentInfo(
                agent_id="neutral_001",
                role=AgentRole.NEUTRAL,
                status=AgentStatus.ACTIVE,
                capabilities=AgentCapabilities(
                    roles=[AgentRole.NEUTRAL],
                    max_concurrent_tasks=10,
                    supported_verification_types=["device", "timestamp"],
                    trust_scoring_enabled=True,
                    consensus_participation=True,
                    specializations=["general"]
                ),
                metrics=AgentMetrics(
                    total_tasks_processed=100,
                    successful_verifications=95,
                    failed_verifications=5,
                    average_response_time=0.5,
                    current_load=2,
                    uptime=3600.0
                ),
                last_heartbeat=datetime.utcnow(),
                version="1.0.0"
            ),
            AgentInfo(
                agent_id="permissive_001",
                role=AgentRole.PERMISSIVE,
                status=AgentStatus.ACTIVE,
                capabilities=AgentCapabilities(
                    roles=[AgentRole.PERMISSIVE],
                    max_concurrent_tasks=15,
                    supported_verification_types=["device", "timestamp", "pattern"],
                    trust_scoring_enabled=True,
                    consensus_participation=True,
                    specializations=["access"]
                ),
                metrics=AgentMetrics(
                    total_tasks_processed=150,
                    successful_verifications=140,
                    failed_verifications=10,
                    average_response_time=0.3,
                    current_load=1,
                    uptime=3600.0
                ),
                last_heartbeat=datetime.utcnow(),
                version="1.0.0"
            )
        ]
        
        return AgentListResponse(
            agents=agents,
            total_count=len(agents)
        )
    except Exception as e:
        logger.error(f"Failed to list agents: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list agents: {str(e)}"
        )