"""
Agent Orchestration Service for ReliQuary API.
This service is responsible for invoking the multi-agent quorum and receiving their consensus decision.
"""

import json
import logging
import asyncio
import warnings
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, asdict
from datetime import datetime
from enum import Enum

def _load_agent_components():
    try:
        from langchain_core._api.deprecation import LangChainPendingDeprecationWarning

        warnings.filters = [
            filter_entry
            for filter_entry in warnings.filters
            if not (
                filter_entry[0] == "default"
                and filter_entry[2] is LangChainPendingDeprecationWarning
            )
        ]
        warnings.simplefilter("ignore", LangChainPendingDeprecationWarning, append=False)
        from agents.decision_orchestrator import DecisionOrchestrator
        from agents.graph import AgentGraph
        from agents.agent_foundation import AgentRole

        return DecisionOrchestrator, AgentGraph, AgentRole
    except ImportError:
        class DecisionOrchestrator:
            async def make_decision(self, context: Dict[str, Any], user_id: str, resource_path: str) -> Dict[str, Any]:
                context_data = context.get("context_data", {})
                trust_score = float(context_data.get("trust_score", context_data.get("confidence_score", 0.0)))
                device_verified = bool(context_data.get("device_verified", context_data.get("verified", False)))
                high_risk = context_data.get("risk_level") in {"high", "very_high"}
                strict_vote = "approved" if trust_score >= 90 and device_verified and not high_risk else "denied"
                neutral_vote = "approved" if trust_score >= 60 and not high_risk else "denied"
                permissive_vote = "approved" if trust_score >= 40 else "denied"
                votes = {
                    "strict": strict_vote,
                    "neutral": neutral_vote,
                    "permissive": permissive_vote,
                    "watchdog": "denied" if high_risk else neutral_vote,
                }
                approvals = sum(1 for vote in votes.values() if vote == "approved")
                decision = "approved" if approvals >= 3 else "denied"
                return {
                    "decision": decision,
                    "confidence": approvals / len(votes),
                    "agents_consulted": ["neutral", "permissive", "strict"],
                    "detailed_votes": votes,
                    "risk_assessment": {
                        "trust_score": trust_score,
                        "device_verified": device_verified,
                        "high_risk": high_risk,
                    },
                    "reasoning": "Deterministic local quorum evaluated trust, device verification, and risk level.",
                    "timestamp": datetime.now().isoformat()
                }

        class AgentRole(Enum):
            NEUTRAL = "neutral"
            PERMISSIVE = "permissive"
            STRICT = "strict"
            WATCHDOG = "watchdog"

        class AgentGraph:
            def __init__(self, agent_ids=None, agent_roles=None):
                self.agent_ids = agent_ids or []
                self.agent_roles = agent_roles or {}

        return DecisionOrchestrator, AgentGraph, AgentRole


class DecisionType(Enum):
    """Types of decisions that can be made by the agent quorum"""
    ACCESS_REQUEST = "access_request"
    GOVERNANCE_DECISION = "governance_decision"
    EMERGENCY_RESPONSE = "emergency_response"
    SECURITY_VALIDATION = "security_validation"


@dataclass
class AgentRequest:
    """Request for agent consensus"""
    request_id: str
    decision_type: DecisionType
    user_id: str
    resource_path: str
    context_data: Dict[str, Any]
    priority: int = 5
    timeout_seconds: int = 30
    required_agents: Optional[List[str]] = None
    metadata: Optional[Dict[str, Any]] = None


@dataclass
class AgentResponse:
    """Response from agent consensus"""
    request_id: str
    decision: str
    confidence_score: float
    participating_agents: List[str]
    consensus_time_ms: float
    detailed_votes: Dict[str, Any]
    risk_assessment: Dict[str, Any]
    timestamp: datetime
    success: bool


class AgentOrchestrator:
    """Service for orchestrating multi-agent consensus decisions"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        DecisionOrchestrator, AgentGraph, AgentRole = _load_agent_components()
        self.decision_orchestrator = DecisionOrchestrator()
        # Initialize AgentGraph with default agents and roles
        agent_ids = ["neutral", "permissive", "strict", "watchdog"]
        agent_roles = {
            "neutral": AgentRole.NEUTRAL,
            "permissive": AgentRole.PERMISSIVE,
            "strict": AgentRole.STRICT,
            "watchdog": AgentRole.WATCHDOG
        }
        self.agent_graph = AgentGraph(agent_ids, agent_roles)
        self.consensus_status: Dict[str, Dict[str, Any]] = {}
    
    async def request_consensus(self, request: AgentRequest) -> AgentResponse:
        """
        Request consensus from the multi-agent quorum.
        
        Args:
            request: Agent request for consensus
            
        Returns:
            Agent response with consensus decision
        """
        start_time = datetime.now()
        self.consensus_status[request.request_id] = {
            "request_id": request.request_id,
            "status": "running",
            "progress": 10,
            "timestamp": start_time.isoformat()
        }
        
        try:
            # Prepare context for decision making
            context = {
                "decision_type": request.decision_type.value,
                "context_data": request.context_data,
                "priority": request.priority,
                "required_agents": request.required_agents,
                "metadata": request.metadata or {}
            }
            
            # Make decision using the orchestrator
            decision_result = await self.decision_orchestrator.make_decision(
                context=context,
                user_id=request.user_id,
                resource_path=request.resource_path
            )
            
            # Calculate consensus time
            end_time = datetime.now()
            consensus_time_ms = (end_time - start_time).total_seconds() * 1000
            
            # Create agent response
            response = AgentResponse(
                request_id=request.request_id,
                decision=decision_result.get("decision", "undecided"),
                confidence_score=decision_result.get("confidence", 0.0),
                participating_agents=decision_result.get("agents_consulted", []),
                consensus_time_ms=consensus_time_ms,
                detailed_votes=decision_result.get("detailed_votes", {}),
                risk_assessment=decision_result.get("risk_assessment", {}),
                timestamp=end_time,
                success=decision_result.get("decision") is not None
            )
            
            self.logger.info(f"Agent consensus completed for request {request.request_id}: {response.decision}")
            self.consensus_status[request.request_id] = {
                "request_id": request.request_id,
                "status": "completed" if response.success else "failed",
                "progress": 100,
                "decision": response.decision,
                "timestamp": end_time.isoformat()
            }
            return response
            
        except Exception as e:
            self.logger.error(f"Agent consensus failed for request {request.request_id}: {str(e)}")
            
            # Calculate consensus time even for failed requests
            end_time = datetime.now()
            consensus_time_ms = (end_time - start_time).total_seconds() * 1000
            
            response = AgentResponse(
                request_id=request.request_id,
                decision="error",
                confidence_score=0.0,
                participating_agents=[],
                consensus_time_ms=consensus_time_ms,
                detailed_votes={},
                risk_assessment={},
                timestamp=end_time,
                success=False
            )
            self.consensus_status[request.request_id] = {
                "request_id": request.request_id,
                "status": "failed",
                "progress": 100,
                "decision": "error",
                "timestamp": end_time.isoformat()
            }
            return response
    
    async def get_consensus_status(self, request_id: str) -> Dict[str, Any]:
        """
        Get the status of a consensus request.
        
        Args:
            request_id: ID of the consensus request
            
        Returns:
            Status information for the request
        """
        return self.consensus_status.get(
            request_id,
            {
                "request_id": request_id,
                "status": "not_found",
                "progress": 0,
                "timestamp": datetime.now().isoformat()
            }
        )
    
    async def cancel_consensus(self, request_id: str) -> bool:
        """
        Cancel an ongoing consensus request.
        
        Args:
            request_id: ID of the consensus request to cancel
            
        Returns:
            True if cancellation was successful, False otherwise
        """
        status = self.consensus_status.get(request_id)
        if not status or status.get("status") != "running":
            return False
        status.update({
            "status": "cancelled",
            "progress": 100,
            "timestamp": datetime.now().isoformat()
        })
        self.logger.info(f"Canceled consensus request {request_id}")
        return True


@dataclass
class OrchestrationRequest:
    """Request for agent orchestration"""
    request_id: str
    user_id: str
    resource_path: str
    context_data: Dict[str, Any]
    priority: int = 5
    timeout_seconds: int = 30
    required_agents: Optional[List[str]] = None
    metadata: Optional[Dict[str, Any]] = None


@dataclass
class OrchestrationResponse:
    """Response from agent orchestration"""
    request_id: str
    decision: str
    confidence_score: float
    participating_agents: List[str]
    consensus_time_ms: float
    detailed_votes: Dict[str, Any]
    risk_assessment: Dict[str, Any]
    timestamp: datetime
    success: bool


class AgentOrchestrationService:
    """Service for orchestrating multi-agent consensus decisions"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.agent_orchestrator = AgentOrchestrator()
    
    async def process_orchestration_request(self, request: OrchestrationRequest) -> OrchestrationResponse:
        """
        Process an orchestration request using the agent orchestrator.
        
        Args:
            request: Orchestration request
            
        Returns:
            Orchestration response with consensus decision
        """
        # Convert OrchestrationRequest to AgentRequest
        agent_request = AgentRequest(
            request_id=request.request_id,
            decision_type=DecisionType.ACCESS_REQUEST,
            user_id=request.user_id,
            resource_path=request.resource_path,
            context_data=request.context_data,
            priority=request.priority,
            timeout_seconds=request.timeout_seconds,
            required_agents=request.required_agents,
            metadata=request.metadata
        )
        
        # Get response from agent orchestrator
        agent_response = await self.agent_orchestrator.request_consensus(agent_request)
        
        # Convert AgentResponse to OrchestrationResponse
        orchestration_response = OrchestrationResponse(
            request_id=agent_response.request_id,
            decision=agent_response.decision,
            confidence_score=agent_response.confidence_score,
            participating_agents=agent_response.participating_agents,
            consensus_time_ms=agent_response.consensus_time_ms,
            detailed_votes=agent_response.detailed_votes,
            risk_assessment=agent_response.risk_assessment,
            timestamp=agent_response.timestamp,
            success=agent_response.success
        )
        
        return orchestration_response
    
    async def get_request_status(self, request_id: str) -> Dict[str, Any]:
        """Get the status of an orchestration request."""
        return await self.agent_orchestrator.get_consensus_status(request_id)
    
    async def cancel_request(self, request_id: str) -> bool:
        """Cancel an orchestration request."""
        return await self.agent_orchestrator.cancel_consensus(request_id)


# Global agent orchestrator instance
_agent_orchestrator = None


def get_agent_orchestrator() -> AgentOrchestrator:
    """Get the global agent orchestrator instance"""
    global _agent_orchestrator
    if _agent_orchestrator is None:
        _agent_orchestrator = AgentOrchestrator()
    return _agent_orchestrator


async def request_agent_consensus(request: AgentRequest) -> AgentResponse:
    """Convenience function to request agent consensus"""
    orchestrator = get_agent_orchestrator()
    return await orchestrator.request_consensus(request)


async def get_consensus_status(request_id: str) -> Dict[str, Any]:
    """Convenience function to get consensus status"""
    orchestrator = get_agent_orchestrator()
    return await orchestrator.get_consensus_status(request_id)


async def cancel_consensus(request_id: str) -> bool:
    """Convenience function to cancel consensus"""
    orchestrator = get_agent_orchestrator()
    return await orchestrator.cancel_consensus(request_id)
