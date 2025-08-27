"""
FastAPI Integration for ReliQuary Multi-Agent Consensus System

This module provides FastAPI endpoints for orchestrating multi-agent consensus
decisions, managing agent workflows, and coordinating threshold cryptography
operations in the ReliQuary system.
"""

import asyncio
import json
import logging
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union
from pydantic import BaseModel, Field
from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

# Import agent system components
from agents.orchestrator import (
    DecisionOrchestrator, 
    DecisionType, 
    DecisionStatus,
    OrchestrationResult
)
from agents.workflow import (
    AgentWorkflowCoordinator,
    WorkflowState,
    WorkflowPhase,
    WorkflowMessage,
    MessageType
)
from agents.consensus import DistributedConsensusManager
from agents.crypto.threshold import (
    EnhancedThresholdCryptography,
    ThresholdScheme,
    SecretShare,
    ReconstructionResult
)

# Authentication and authorization
from auth.auth_manager import AuthManager
from auth.rbac_manager import RBACManager, Permission
from core.vault_api import get_current_user


# Security
security = HTTPBearer()
logger = logging.getLogger("agent_api")


# Pydantic models for API
class AgentDecisionRequest(BaseModel):
    """Request for agent decision orchestration"""
    decision_type: str = Field(..., description="Type of decision to orchestrate")
    requestor_id: str = Field(..., description="ID of the requesting entity")
    context_data: Dict[str, Any] = Field(..., description="Context data for the decision")
    priority: int = Field(5, ge=1, le=10, description="Priority level (1=highest, 10=lowest)")
    timeout_seconds: Optional[float] = Field(60.0, description="Timeout for the decision")
    required_agents: Optional[List[str]] = Field(None, description="Specific agents required")


class AgentDecisionResponse(BaseModel):
    """Response from agent decision orchestration"""
    request_id: str
    final_decision: str
    consensus_confidence: float
    participating_agents: List[str]
    execution_time: float
    status: str
    timestamp: str


class WorkflowStartRequest(BaseModel):
    """Request to start an agent workflow"""
    workflow_type: str = Field(..., description="Type of workflow to execute")
    initial_context: Dict[str, Any] = Field(..., description="Initial context data")
    participating_agents: Optional[List[str]] = Field(None, description="Agents to participate")


class WorkflowStatusResponse(BaseModel):
    """Response with workflow status"""
    request_id: str
    workflow_phase: str
    progress: float
    participating_agents: List[str]
    messages_count: int
    created_at: str
    updated_at: str


class ThresholdSchemeRequest(BaseModel):
    """Request to create a threshold cryptography scheme"""
    scheme_type: str = Field(..., description="Type of threshold scheme")
    threshold: int = Field(..., ge=1, description="Minimum parties needed")
    total_parties: int = Field(..., ge=1, description="Total number of parties")
    party_ids: Optional[List[int]] = Field(None, description="Specific party IDs")
    enable_verification: bool = Field(True, description="Enable verifiable sharing")


class SecretSharingRequest(BaseModel):
    """Request to share a secret"""
    scheme_id: str = Field(..., description="ID of the threshold scheme")
    secret_value: int = Field(..., description="Secret value to share")
    dealer_id: Optional[int] = Field(None, description="ID of the dealing party")


class SecretReconstructionRequest(BaseModel):
    """Request to reconstruct a secret"""
    scheme_id: str = Field(..., description="ID of the threshold scheme")
    shares: Dict[str, Dict[str, Any]] = Field(..., description="Shares for reconstruction")
    verify_shares: bool = Field(True, description="Whether to verify share validity")


class AgentRegistrationRequest(BaseModel):
    """Request to register an agent"""
    agent_id: str = Field(..., description="Unique agent identifier")
    agent_type: str = Field(..., description="Type of agent")
    capabilities: List[str] = Field(..., description="Agent capabilities")
    network_agents: List[str] = Field(..., description="Network agent list")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata")


class SystemStatusResponse(BaseModel):
    """System status response"""
    orchestrator_status: Dict[str, Any]
    workflow_status: Dict[str, Any]
    consensus_status: Dict[str, Any]
    threshold_crypto_status: Dict[str, Any]
    active_agents: List[str]
    system_health: str
    uptime_seconds: float


# Global system components
orchestrator: Optional[DecisionOrchestrator] = None
workflow_coordinator: Optional[AgentWorkflowCoordinator] = None
consensus_manager: Optional[DistributedConsensusManager] = None
threshold_crypto: Optional[EnhancedThresholdCryptography] = None
auth_manager: Optional[AuthManager] = None
rbac_manager: Optional[RBACManager] = None

# System startup time
system_start_time = time.time()


def create_agent_orchestration_app() -> FastAPI:
    """Create and configure the FastAPI application for agent orchestration."""
    app = FastAPI(
        title="ReliQuary Multi-Agent Orchestration API",
        description="REST API for orchestrating multi-agent consensus decisions, workflows, and cryptographic operations",
        version="4.0.0",
        docs_url="/docs",
        redoc_url="/redoc"
    )
    
    # Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # Configure appropriately for production
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    return app


# Create the FastAPI app
app = create_agent_orchestration_app()


async def get_authenticated_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Get authenticated user from JWT token."""
    try:
        if auth_manager:
            user = await auth_manager.verify_token(credentials.credentials)
            if user:
                return user
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except Exception as e:
        logger.error(f"Authentication error: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication failed",
            headers={"WWW-Authenticate": "Bearer"},
        )


async def check_permission(user: Dict[str, Any], permission: Permission):
    """Check if user has required permission."""
    if rbac_manager:
        user_id = user.get("user_id")
        if not await rbac_manager.check_permission(user_id, permission):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Insufficient permissions: {permission.value} required"
            )


@app.on_event("startup")
async def startup_event():
    """Initialize system components on startup."""
    global orchestrator, workflow_coordinator, consensus_manager, threshold_crypto
    global auth_manager, rbac_manager
    
    try:
        logger.info("Initializing ReliQuary Multi-Agent Orchestration API...")
        
        # Initialize core components
        agent_network = ["neutral_agent", "permissive_agent", "strict_agent", "watchdog_agent"]
        
        orchestrator = DecisionOrchestrator(
            orchestrator_id="api_orchestrator",
            agent_network=agent_network
        )
        
        workflow_coordinator = AgentWorkflowCoordinator(
            coordinator_id="api_workflow_coordinator"
        )
        
        consensus_manager = DistributedConsensusManager(
            agent_id="api_consensus_manager",
            agent_network=agent_network
        )
        
        threshold_crypto = EnhancedThresholdCryptography(security_level=256)
        
        # Initialize authentication (if available)
        try:
            auth_manager = AuthManager()
            rbac_manager = RBACManager()
        except Exception as e:
            logger.warning(f"Authentication not available: {e}")
        
        logger.info("Multi-Agent Orchestration API initialized successfully")
        
    except Exception as e:
        logger.error(f"Failed to initialize API: {e}")
        raise


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "uptime_seconds": time.time() - system_start_time,
        "components": {
            "orchestrator": orchestrator is not None,
            "workflow_coordinator": workflow_coordinator is not None,
            "consensus_manager": consensus_manager is not None,
            "threshold_crypto": threshold_crypto is not None
        }
    }


@app.get("/status", response_model=SystemStatusResponse)
async def get_system_status(user: Dict[str, Any] = Depends(get_authenticated_user)):
    """Get comprehensive system status."""
    if rbac_manager:
        await check_permission(user, Permission.READ_SYSTEM_STATUS)
    
    try:
        orchestrator_status = orchestrator.get_orchestration_status() if orchestrator else {}
        workflow_status = workflow_coordinator.get_workflow_status() if workflow_coordinator else {}
        consensus_status = consensus_manager.get_consensus_status() if consensus_manager else {}
        threshold_status = threshold_crypto.get_system_metrics() if threshold_crypto else {}
        
        # Determine system health
        health_checks = [
            orchestrator is not None,
            workflow_coordinator is not None,
            consensus_manager is not None,
            threshold_crypto is not None
        ]
        
        if all(health_checks):
            system_health = "excellent"
        elif sum(health_checks) >= 3:
            system_health = "good"
        elif sum(health_checks) >= 2:
            system_health = "degraded"
        else:
            system_health = "critical"
        
        return SystemStatusResponse(
            orchestrator_status=orchestrator_status,
            workflow_status=workflow_status,
            consensus_status=consensus_status,
            threshold_crypto_status=threshold_status,
            active_agents=orchestrator_status.get("agents_available", []),
            system_health=system_health,
            uptime_seconds=time.time() - system_start_time
        )
        
    except Exception as e:
        logger.error(f"Failed to get system status: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve system status")


# Agent Decision Orchestration Endpoints
@app.post("/decisions/orchestrate", response_model=AgentDecisionResponse)
async def orchestrate_decision(
    request: AgentDecisionRequest,
    background_tasks: BackgroundTasks,
    user: Dict[str, Any] = Depends(get_authenticated_user)
):
    """Orchestrate a multi-agent consensus decision."""
    if rbac_manager:
        await check_permission(user, Permission.ORCHESTRATE_DECISIONS)
    
    if not orchestrator:
        raise HTTPException(status_code=503, detail="Orchestrator not available")
    
    try:
        # Convert string decision type to enum
        try:
            decision_type = DecisionType[request.decision_type.upper()]
        except KeyError:
            decision_type = DecisionType.ACCESS_REQUEST
        
        # Orchestrate the decision
        result = await orchestrator.orchestrate_decision(
            decision_type=decision_type,
            requestor_id=request.requestor_id,
            context_data=request.context_data,
            priority=request.priority,
            timeout_seconds=request.timeout_seconds
        )
        
        return AgentDecisionResponse(
            request_id=result.request_id,
            final_decision=result.final_decision,
            consensus_confidence=result.consensus_confidence,
            participating_agents=result.participating_agents,
            execution_time=result.execution_time,
            status=result.status.value,
            timestamp=result.timestamp.isoformat()
        )
        
    except Exception as e:
        logger.error(f"Decision orchestration failed: {e}")
        raise HTTPException(status_code=500, detail=f"Decision orchestration failed: {str(e)}")


@app.get("/decisions/{request_id}")
async def get_decision_status(
    request_id: str,
    user: Dict[str, Any] = Depends(get_authenticated_user)
):
    """Get the status of a decision request."""
    if rbac_manager:
        await check_permission(user, Permission.READ_DECISIONS)
    
    if not orchestrator:
        raise HTTPException(status_code=503, detail="Orchestrator not available")
    
    # Check completed decisions
    if request_id in orchestrator.completed_decisions:
        result = orchestrator.completed_decisions[request_id]
        return AgentDecisionResponse(
            request_id=result.request_id,
            final_decision=result.final_decision,
            consensus_confidence=result.consensus_confidence,
            participating_agents=result.participating_agents,
            execution_time=result.execution_time,
            status=result.status.value,
            timestamp=result.timestamp.isoformat()
        )
    
    # Check pending decisions
    if request_id in orchestrator.pending_decisions:
        return {
            "request_id": request_id,
            "status": "pending",
            "message": "Decision is being processed"
        }
    
    # Check active evaluations
    if request_id in orchestrator.active_evaluations:
        return {
            "request_id": request_id,
            "status": "evaluating",
            "message": "Decision is being evaluated by agents"
        }
    
    raise HTTPException(status_code=404, detail="Decision request not found")


@app.get("/decisions/history")
async def get_decision_history(
    limit: int = 100,
    user: Dict[str, Any] = Depends(get_authenticated_user)
):
    """Get decision history."""
    if rbac_manager:
        await check_permission(user, Permission.READ_DECISIONS)
    
    if not orchestrator:
        raise HTTPException(status_code=503, detail="Orchestrator not available")
    
    try:
        history = await orchestrator.get_decision_history(limit=limit)
        return {"history": history, "count": len(history)}
    except Exception as e:
        logger.error(f"Failed to get decision history: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve decision history")


# Workflow Management Endpoints
@app.post("/workflows/start", response_model=WorkflowStatusResponse)
async def start_workflow(
    request: WorkflowStartRequest,
    user: Dict[str, Any] = Depends(get_authenticated_user)
):
    """Start a new agent workflow."""
    if rbac_manager:
        await check_permission(user, Permission.MANAGE_WORKFLOWS)
    
    if not workflow_coordinator:
        raise HTTPException(status_code=503, detail="Workflow coordinator not available")
    
    try:
        # Generate request ID
        request_id = f"workflow_{int(time.time())}_{hash(request.workflow_type) % 10000}"
        
        # Start workflow
        result = await workflow_coordinator.start_workflow(
            request_id=request_id,
            workflow_type=request.workflow_type,
            initial_context=request.initial_context,
            participating_agents=request.participating_agents
        )
        
        # Calculate progress
        total_phases = len(WorkflowPhase)
        current_phase_index = list(WorkflowPhase).index(result.workflow_phase)
        progress = (current_phase_index + 1) / total_phases
        
        return WorkflowStatusResponse(
            request_id=result.request_id,
            workflow_phase=result.workflow_phase.value,
            progress=progress,
            participating_agents=result.metadata.get("participating_agents", []),
            messages_count=len(result.messages),
            created_at=result.created_at.isoformat(),
            updated_at=result.updated_at.isoformat()
        )
        
    except Exception as e:
        logger.error(f"Workflow start failed: {e}")
        raise HTTPException(status_code=500, detail=f"Workflow start failed: {str(e)}")


@app.get("/workflows/{request_id}")
async def get_workflow_status(
    request_id: str,
    user: Dict[str, Any] = Depends(get_authenticated_user)
):
    """Get workflow status."""
    if rbac_manager:
        await check_permission(user, Permission.READ_WORKFLOWS)
    
    if not workflow_coordinator:
        raise HTTPException(status_code=503, detail="Workflow coordinator not available")
    
    # Check workflow history
    if request_id in workflow_coordinator.workflow_history:
        result = workflow_coordinator.workflow_history[request_id]
        
        # Calculate progress
        total_phases = len(WorkflowPhase)
        current_phase_index = list(WorkflowPhase).index(result.workflow_phase)
        progress = (current_phase_index + 1) / total_phases
        
        return WorkflowStatusResponse(
            request_id=result.request_id,
            workflow_phase=result.workflow_phase.value,
            progress=progress,
            participating_agents=result.metadata.get("participating_agents", []),
            messages_count=len(result.messages),
            created_at=result.created_at.isoformat(),
            updated_at=result.updated_at.isoformat()
        )
    
    # Check active workflows
    if request_id in workflow_coordinator.active_workflows:
        return {
            "request_id": request_id,
            "status": "active",
            "message": "Workflow is currently executing"
        }
    
    raise HTTPException(status_code=404, detail="Workflow not found")


# Threshold Cryptography Endpoints
@app.post("/crypto/schemes")
async def create_threshold_scheme(
    request: ThresholdSchemeRequest,
    user: Dict[str, Any] = Depends(get_authenticated_user)
):
    """Create a new threshold cryptography scheme."""
    if rbac_manager:
        await check_permission(user, Permission.MANAGE_CRYPTO)
    
    if not threshold_crypto:
        raise HTTPException(status_code=503, detail="Threshold cryptography not available")
    
    try:
        # Convert string scheme type to enum
        try:
            scheme_type = ThresholdScheme[request.scheme_type.upper()]
        except KeyError:
            scheme_type = ThresholdScheme.SHAMIR_SECRET_SHARING
        
        # Create scheme
        scheme_id = threshold_crypto.create_scheme(
            scheme_type=scheme_type,
            threshold=request.threshold,
            total_parties=request.total_parties,
            party_ids=request.party_ids,
            enable_verification=request.enable_verification
        )
        
        # Get scheme info
        scheme_info = threshold_crypto.get_scheme_info(scheme_id)
        
        return {
            "scheme_id": scheme_id,
            "scheme_info": scheme_info,
            "message": "Threshold cryptography scheme created successfully"
        }
        
    except Exception as e:
        logger.error(f"Scheme creation failed: {e}")
        raise HTTPException(status_code=500, detail=f"Scheme creation failed: {str(e)}")


@app.post("/crypto/share")
async def share_secret(
    request: SecretSharingRequest,
    user: Dict[str, Any] = Depends(get_authenticated_user)
):
    """Share a secret using threshold cryptography."""
    if rbac_manager:
        await check_permission(user, Permission.MANAGE_CRYPTO)
    
    if not threshold_crypto:
        raise HTTPException(status_code=503, detail="Threshold cryptography not available")
    
    try:
        # Share the secret
        shares = threshold_crypto.share_secret(
            scheme_id=request.scheme_id,
            secret=request.secret_value,
            dealer_id=request.dealer_id
        )
        
        # Convert shares to serializable format
        shares_data = {}
        for party_id, share in shares.items():
            shares_data[str(party_id)] = share.to_dict()
        
        return {
            "scheme_id": request.scheme_id,
            "shares_generated": len(shares),
            "shares": shares_data,
            "message": "Secret shared successfully"
        }
        
    except Exception as e:
        logger.error(f"Secret sharing failed: {e}")
        raise HTTPException(status_code=500, detail=f"Secret sharing failed: {str(e)}")


@app.post("/crypto/reconstruct")
async def reconstruct_secret(
    request: SecretReconstructionRequest,
    user: Dict[str, Any] = Depends(get_authenticated_user)
):
    """Reconstruct a secret from threshold shares."""
    if rbac_manager:
        await check_permission(user, Permission.MANAGE_CRYPTO)
    
    if not threshold_crypto:
        raise HTTPException(status_code=503, detail="Threshold cryptography not available")
    
    try:
        # Convert share data back to SecretShare objects
        shares = {}
        for party_id_str, share_data in request.shares.items():
            party_id = int(party_id_str)
            shares[party_id] = SecretShare.from_dict(share_data)
        
        # Reconstruct the secret
        result = threshold_crypto.reconstruct_secret(
            scheme_id=request.scheme_id,
            shares=shares,
            verify_shares=request.verify_shares
        )
        
        return {
            "success": result.success,
            "reconstructed_secret": result.reconstructed_secret,
            "participating_shares": len(result.participating_shares),
            "validation_results": {str(k): v.value for k, v in result.validation_results.items()},
            "reconstruction_time": result.reconstruction_time,
            "error_message": result.error_message
        }
        
    except Exception as e:
        logger.error(f"Secret reconstruction failed: {e}")
        raise HTTPException(status_code=500, detail=f"Secret reconstruction failed: {str(e)}")


@app.get("/crypto/schemes/{scheme_id}")
async def get_scheme_info(
    scheme_id: str,
    user: Dict[str, Any] = Depends(get_authenticated_user)
):
    """Get information about a threshold scheme."""
    if rbac_manager:
        await check_permission(user, Permission.READ_CRYPTO)
    
    if not threshold_crypto:
        raise HTTPException(status_code=503, detail="Threshold cryptography not available")
    
    try:
        scheme_info = threshold_crypto.get_scheme_info(scheme_id)
        return scheme_info
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Failed to get scheme info: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve scheme information")


# Agent Management Endpoints
@app.post("/agents/register")
async def register_agent(
    request: AgentRegistrationRequest,
    user: Dict[str, Any] = Depends(get_authenticated_user)
):
    """Register a new agent with the system."""
    if rbac_manager:
        await check_permission(user, Permission.MANAGE_AGENTS)
    
    if not workflow_coordinator:
        raise HTTPException(status_code=503, detail="Workflow coordinator not available")
    
    try:
        # Register agent with workflow coordinator
        workflow_coordinator.register_agent(
            agent_id=request.agent_id,
            capabilities=request.capabilities,
            metadata=request.metadata
        )
        
        return {
            "agent_id": request.agent_id,
            "message": "Agent registered successfully",
            "capabilities": request.capabilities,
            "registered_at": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Agent registration failed: {e}")
        raise HTTPException(status_code=500, detail=f"Agent registration failed: {str(e)}")


@app.get("/agents")
async def list_agents(user: Dict[str, Any] = Depends(get_authenticated_user)):
    """List all registered agents."""
    if rbac_manager:
        await check_permission(user, Permission.READ_AGENTS)
    
    if not workflow_coordinator:
        raise HTTPException(status_code=503, detail="Workflow coordinator not available")
    
    try:
        agents = workflow_coordinator.registered_agents
        return {
            "agents": agents,
            "count": len(agents)
        }
    except Exception as e:
        logger.error(f"Failed to list agents: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve agent list")


# Emergency Override Endpoint
@app.post("/emergency/override/{request_id}")
async def emergency_override(
    request_id: str,
    override_decision: str,
    reason: str,
    user: Dict[str, Any] = Depends(get_authenticated_user)
):
    """Perform emergency override of a decision."""
    if rbac_manager:
        await check_permission(user, Permission.EMERGENCY_OVERRIDE)
    
    if not orchestrator:
        raise HTTPException(status_code=503, detail="Orchestrator not available")
    
    try:
        success = await orchestrator.emergency_override(
            request_id=request_id,
            override_decision=override_decision,
            reason=reason
        )
        
        if success:
            return {
                "request_id": request_id,
                "override_decision": override_decision,
                "reason": reason,
                "message": "Emergency override applied successfully",
                "timestamp": datetime.now().isoformat()
            }
        else:
            raise HTTPException(status_code=404, detail="Request not found or override failed")
            
    except Exception as e:
        logger.error(f"Emergency override failed: {e}")
        raise HTTPException(status_code=500, detail=f"Emergency override failed: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)