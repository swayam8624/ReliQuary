"""
Agent Schemas for ReliQuary FastAPI

This module defines Pydantic schemas for agent-related data structures
used in the FastAPI application.
"""

from typing import List, Dict, Any, Optional
from enum import Enum
from pydantic import BaseModel, Field
from datetime import datetime


class AgentRole(str, Enum):
    """Agent roles in the system"""
    NEUTRAL = "neutral"
    PERMISSIVE = "permissive"
    STRICT = "strict"
    WATCHDOG = "watchdog"
    COORDINATOR = "coordinator"


class AgentStatus(str, Enum):
    """Agent status values"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    BUSY = "busy"
    OFFLINE = "offline"
    ERROR = "error"


class AgentCapabilities(BaseModel):
    """Agent capabilities model"""
    roles: List[AgentRole] = Field(..., description="List of roles this agent can fulfill")
    max_concurrent_tasks: int = Field(..., description="Maximum concurrent tasks agent can handle")
    supported_verification_types: List[str] = Field(default_factory=list, description="Supported verification types")
    trust_scoring_enabled: bool = Field(default=False, description="Whether trust scoring is enabled")
    consensus_participation: bool = Field(default=False, description="Whether agent participates in consensus")
    specializations: List[str] = Field(default_factory=list, description="Agent specializations")


class AgentMetrics(BaseModel):
    """Agent performance metrics"""
    total_tasks_processed: int = Field(default=0, description="Total tasks processed")
    successful_verifications: int = Field(default=0, description="Successful verifications")
    failed_verifications: int = Field(default=0, description="Failed verifications")
    average_response_time: float = Field(default=0.0, description="Average response time in seconds")
    current_load: int = Field(default=0, description="Current task load")
    uptime: float = Field(default=0.0, description="Uptime in seconds")


class AgentInfo(BaseModel):
    """Agent information model"""
    agent_id: str = Field(..., description="Unique agent identifier")
    role: AgentRole = Field(..., description="Primary agent role")
    status: AgentStatus = Field(..., description="Current agent status")
    capabilities: AgentCapabilities = Field(..., description="Agent capabilities")
    metrics: AgentMetrics = Field(..., description="Agent performance metrics")
    last_heartbeat: datetime = Field(..., description="Last heartbeat timestamp")
    version: str = Field(..., description="Agent version")


class AgentRegistrationRequest(BaseModel):
    """Request model for agent registration"""
    agent_id: str = Field(..., description="Unique agent identifier")
    role: AgentRole = Field(..., description="Primary agent role")
    capabilities: AgentCapabilities = Field(..., description="Agent capabilities")
    version: str = Field(..., description="Agent version")


class AgentRegistrationResponse(BaseModel):
    """Response model for agent registration"""
    success: bool = Field(..., description="Whether registration was successful")
    agent_id: str = Field(..., description="Registered agent identifier")
    message: Optional[str] = Field(None, description="Additional message")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Response timestamp")


class AgentHeartbeatRequest(BaseModel):
    """Request model for agent heartbeat"""
    agent_id: str = Field(..., description="Agent identifier")
    status: AgentStatus = Field(..., description="Current agent status")
    metrics: AgentMetrics = Field(..., description="Current agent metrics")


class AgentHeartbeatResponse(BaseModel):
    """Response model for agent heartbeat"""
    success: bool = Field(..., description="Whether heartbeat was successful")
    agent_id: str = Field(..., description="Agent identifier")
    next_heartbeat_interval: int = Field(..., description="Recommended next heartbeat interval in seconds")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Response timestamp")


class AgentDecisionRequest(BaseModel):
    """Request model for agent decision"""
    request_id: str = Field(..., description="Unique request identifier")
    agent_id: str = Field(..., description="Agent identifier")
    context_data: Dict[str, Any] = Field(..., description="Context data for decision")
    trust_score: float = Field(..., description="Current trust score", ge=0.0, le=100.0)
    timeout: int = Field(default=30, description="Decision timeout in seconds")


class AgentDecisionResponse(BaseModel):
    """Response model for agent decision"""
    request_id: str = Field(..., description="Request identifier")
    agent_id: str = Field(..., description="Agent identifier")
    decision: str = Field(..., description="Decision result (allow/deny)")
    confidence: str = Field(..., description="Confidence level")
    reasoning: List[str] = Field(default_factory=list, description="Decision reasoning")
    processing_time: float = Field(..., description="Processing time in seconds")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Decision timestamp")


class AgentListResponse(BaseModel):
    """Response model for agent list"""
    agents: List[AgentInfo] = Field(..., description="List of agents")
    total_count: int = Field(..., description="Total number of agents")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Response timestamp")