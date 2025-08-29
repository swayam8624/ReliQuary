# agents/agent_foundation.py

import json
import time
import uuid
import hashlib
import asyncio
from pathlib import Path
from typing import Dict, Any, List, Optional, Callable, Set
from dataclasses import dataclass, asdict
from enum import Enum
import logging
from datetime import datetime
import threading
from concurrent.futures import ThreadPoolExecutor

# Import our core components
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '../'))

from core.merkle_logging.writer import MerkleLogWriter
from zk.context_manager import ContextVerificationManager, ContextVerificationResult
from zk.trust_engine import TrustScoringEngine, TrustEvaluation

class AgentRole(Enum):
    """Agent roles in the multi-agent system"""
    VALIDATOR = "validator"           # Validates context and trust scores
    CONSENSUS = "consensus"           # Participates in consensus algorithms
    MONITOR = "monitor"              # Monitors system health and anomalies
    COORDINATOR = "coordinator"      # Coordinates multi-agent operations
    SPECIALIST = "specialist"        # Specialized domain-specific validation
    NEUTRAL = "neutral"              # Neutral decision-making agent
    PERMISSIVE = "permissive"        # Permissive decision-making agent
    STRICT = "strict"                # Strict decision-making agent
    WATCHDOG = "watchdog"            # Watchdog monitoring agent

class AgentStatus(Enum):
    """Agent operational status"""
    INITIALIZING = "initializing"
    ACTIVE = "active"
    IDLE = "idle"
    BUSY = "busy"
    ERROR = "error"
    OFFLINE = "offline"

class MessageType(Enum):
    """Inter-agent message types"""
    VERIFICATION_REQUEST = "verification_request"
    VERIFICATION_RESPONSE = "verification_response"
    CONSENSUS_PROPOSAL = "consensus_proposal"
    CONSENSUS_VOTE = "consensus_vote"
    HEALTH_CHECK = "health_check"
    COORDINATION = "coordination"
    ALERT = "alert"

@dataclass
class AgentMessage:
    """Message structure for inter-agent communication"""
    message_id: str
    sender_id: str
    recipient_id: Optional[str]  # None for broadcast
    message_type: MessageType
    payload: Dict[str, Any]
    timestamp: int
    signature: Optional[str] = None
    priority: int = 0  # 0=normal, 1=high, 2=critical

@dataclass
class AgentCapabilities:
    """Agent capabilities and configuration"""
    roles: List[AgentRole]
    max_concurrent_tasks: int
    supported_verification_types: List[str]
    trust_scoring_enabled: bool
    consensus_participation: bool
    specializations: List[str]

@dataclass
class AgentMetrics:
    """Agent performance and health metrics"""
    total_tasks_processed: int = 0
    successful_verifications: int = 0
    failed_verifications: int = 0
    average_response_time: float = 0.0
    current_load: float = 0.0
    uptime_seconds: int = 0
    last_health_check: int = 0

class BaseAgent:
    """
    Base agent class for the multi-agent system.
    
    This provides the foundation for distributed agents that can:
    - Perform context verification and trust scoring
    - Participate in consensus algorithms
    - Communicate with other agents
    - Monitor system health and performance
    - Coordinate distributed operations
    """
    
    def __init__(self, agent_id: str, capabilities: AgentCapabilities, data_path: str = None):
        """
        Initialize the base agent.
        
        Args:
            agent_id: Unique agent identifier
            capabilities: Agent capabilities and configuration
            data_path: Path for agent data storage
        """
        self.agent_id = agent_id
        self.capabilities = capabilities
        self.status = AgentStatus.INITIALIZING
        self.metrics = AgentMetrics()
        
        # Initialize data path
        if data_path is None:
            data_path = Path(__file__).parent / "agent_data"
        self.data_path = Path(data_path)
        self.data_path.mkdir(exist_ok=True)
        
        # Initialize logging
        self.logger = logging.getLogger(f"agent_{agent_id}")
        
        # Initialize audit logging
        try:
            self.audit_logger = MerkleLogWriter(f"logs/agent_{agent_id}.log")
        except Exception as e:
            self.logger.warning(f"Could not initialize audit logging: {e}")
            self.audit_logger = None
        
        # Initialize message queues
        self.inbox: asyncio.Queue = asyncio.Queue()
        self.outbox: asyncio.Queue = asyncio.Queue()
        
        # Initialize agent registry
        self.known_agents: Dict[str, Dict[str, Any]] = {}
        
        # Initialize task executor
        self.executor = ThreadPoolExecutor(max_workers=capabilities.max_concurrent_tasks)
        
        # Initialize ZK components if needed
        self.context_manager: Optional[ContextVerificationManager] = None
        self.trust_engine: Optional[TrustScoringEngine] = None
        
        if any(role in [AgentRole.VALIDATOR, AgentRole.SPECIALIST] for role in capabilities.roles):
            self.context_manager = ContextVerificationManager()
        
        if capabilities.trust_scoring_enabled:
            self.trust_engine = TrustScoringEngine()
        
        # Start time for uptime calculation
        self.start_time = time.time()
        
        # Agent lifecycle
        self.running = False
        self.shutdown_event = threading.Event()
        
        self.logger.info(f"Agent {agent_id} initialized with roles: {[r.value for r in capabilities.roles]}")
    
    async def start(self):
        """Start the agent and begin processing."""
        self.status = AgentStatus.ACTIVE
        self.running = True
        
        # Log agent startup
        if self.audit_logger:
            self.audit_logger.add_entry({
                "event": "agent_startup",
                "agent_id": self.agent_id,
                "roles": [r.value for r in self.capabilities.roles],
                "timestamp": int(time.time())
            })
        
        # Start background tasks
        await asyncio.gather(
            self._message_processor(),
            self._health_monitor(),
            self._metrics_updater()
        )
    
    async def stop(self):
        """Stop the agent gracefully."""
        self.running = False
        self.shutdown_event.set()
        self.status = AgentStatus.OFFLINE
        
        # Cleanup resources
        self.executor.shutdown(wait=True)
        
        # Log agent shutdown
        if self.audit_logger:
            self.audit_logger.add_entry({
                "event": "agent_shutdown",
                "agent_id": self.agent_id,
                "uptime": int(time.time() - self.start_time),
                "tasks_processed": self.metrics.total_tasks_processed,
                "timestamp": int(time.time())
            })
        
        self.logger.info(f"Agent {self.agent_id} stopped")
    
    async def send_message(self, message: AgentMessage):
        """Send a message to another agent or broadcast."""
        try:
            # Sign the message
            message.signature = self._sign_message(message)
            
            # Add to outbox
            await self.outbox.put(message)
            
            self.logger.debug(f"Message sent: {message.message_type.value} to {message.recipient_id or 'broadcast'}")
            
        except Exception as e:
            self.logger.error(f"Failed to send message: {e}")
    
    async def handle_verification_request(self, message: AgentMessage) -> Dict[str, Any]:
        """Handle context verification request."""
        try:
            if not self.context_manager:
                return {"error": "Context verification not available on this agent"}
            
            # Extract verification request from message payload
            verification_data = message.payload.get("verification_request")
            if not verification_data:
                return {"error": "No verification request data provided"}
            
            # Perform verification (simplified for foundation)
            # In Phase 4, this will use the full context verification system
            result = {
                "verified": True,  # Placeholder
                "trust_score": 85,  # Placeholder
                "agent_id": self.agent_id,
                "processing_time": 0.5,
                "timestamp": int(time.time())
            }
            
            # Update metrics
            self.metrics.successful_verifications += 1
            self.metrics.total_tasks_processed += 1
            
            return result
            
        except Exception as e:
            self.logger.error(f"Verification request failed: {e}")
            self.metrics.failed_verifications += 1
            return {"error": str(e)}
    
    async def handle_consensus_proposal(self, message: AgentMessage) -> Dict[str, Any]:
        """Handle consensus proposal from another agent."""
        try:
            if not self.capabilities.consensus_participation:
                return {"error": "Consensus participation not enabled"}
            
            proposal = message.payload.get("proposal")
            if not proposal:
                return {"error": "No proposal data provided"}
            
            # Evaluate proposal (simplified for foundation)
            # In Phase 4, this will implement full consensus algorithms
            vote = {
                "proposal_id": proposal.get("proposal_id"),
                "vote": "approve",  # Placeholder decision logic
                "agent_id": self.agent_id,
                "reasoning": "Proposal meets basic criteria",
                "timestamp": int(time.time())
            }
            
            # Send vote response
            response_message = AgentMessage(
                message_id=str(uuid.uuid4()),
                sender_id=self.agent_id,
                recipient_id=message.sender_id,
                message_type=MessageType.CONSENSUS_VOTE,
                payload={"vote": vote},
                timestamp=int(time.time())
            )
            
            await self.send_message(response_message)
            
            return vote
            
        except Exception as e:
            self.logger.error(f"Consensus proposal handling failed: {e}")
            return {"error": str(e)}
    
    async def perform_health_check(self) -> Dict[str, Any]:
        """Perform agent health check."""
        try:
            current_time = int(time.time())
            
            # Calculate current metrics
            uptime = current_time - self.start_time
            current_load = self._calculate_current_load()
            
            health_data = {
                "agent_id": self.agent_id,
                "status": self.status.value,
                "uptime": uptime,
                "current_load": current_load,
                "total_tasks": self.metrics.total_tasks_processed,
                "success_rate": self._calculate_success_rate(),
                "capabilities": [r.value for r in self.capabilities.roles],
                "timestamp": current_time
            }
            
            # Update metrics
            self.metrics.uptime_seconds = uptime
            self.metrics.current_load = current_load
            self.metrics.last_health_check = current_time
            
            return health_data
            
        except Exception as e:
            self.logger.error(f"Health check failed: {e}")
            return {"agent_id": self.agent_id, "status": "error", "error": str(e)}
    
    def register_agent(self, agent_id: str, agent_info: Dict[str, Any]):
        """Register another agent in the network."""
        self.known_agents[agent_id] = agent_info
        self.logger.info(f"Registered agent: {agent_id}")
    
    def get_network_status(self) -> Dict[str, Any]:
        """Get status of the agent network."""
        return {
            "total_agents": len(self.known_agents) + 1,  # +1 for self
            "known_agents": list(self.known_agents.keys()),
            "network_health": "healthy" if len(self.known_agents) > 0 else "isolated",
            "last_updated": int(time.time())
        }
    
    async def _message_processor(self):
        """Process incoming messages."""
        while self.running:
            try:
                # Check for incoming messages
                if not self.inbox.empty():
                    message = await self.inbox.get()
                    await self._handle_message(message)
                
                # Brief pause to prevent busy waiting
                await asyncio.sleep(0.1)
                
            except Exception as e:
                self.logger.error(f"Message processing error: {e}")
    
    async def _handle_message(self, message: AgentMessage):
        """Handle a specific message based on its type."""
        try:
            # Verify message signature
            if not self._verify_message_signature(message):
                self.logger.warning(f"Invalid message signature from {message.sender_id}")
                return
            
            response_data = None
            
            if message.message_type == MessageType.VERIFICATION_REQUEST:
                response_data = await self.handle_verification_request(message)
                response_type = MessageType.VERIFICATION_RESPONSE
                
            elif message.message_type == MessageType.CONSENSUS_PROPOSAL:
                response_data = await self.handle_consensus_proposal(message)
                response_type = MessageType.CONSENSUS_VOTE
                
            elif message.message_type == MessageType.HEALTH_CHECK:
                response_data = await self.perform_health_check()
                response_type = MessageType.HEALTH_CHECK
                
            # Send response if needed
            if response_data and message.sender_id:
                response_message = AgentMessage(
                    message_id=str(uuid.uuid4()),
                    sender_id=self.agent_id,
                    recipient_id=message.sender_id,
                    message_type=response_type,
                    payload=response_data,
                    timestamp=int(time.time())
                )
                await self.send_message(response_message)
            
        except Exception as e:
            self.logger.error(f"Message handling error: {e}")
    
    async def _health_monitor(self):
        """Monitor agent health and performance."""
        while self.running:
            try:
                # Perform periodic health check
                await self.perform_health_check()
                
                # Update status based on current conditions
                if self.metrics.current_load > 0.9:
                    self.status = AgentStatus.BUSY
                elif self.metrics.current_load < 0.1:
                    self.status = AgentStatus.IDLE
                else:
                    self.status = AgentStatus.ACTIVE
                
                # Sleep for health check interval
                await asyncio.sleep(30)  # 30 seconds
                
            except Exception as e:
                self.logger.error(f"Health monitoring error: {e}")
                self.status = AgentStatus.ERROR
    
    async def _metrics_updater(self):
        """Update performance metrics."""
        while self.running:
            try:
                # Update average response time
                # This is a placeholder - in Phase 4, this will track actual response times
                self.metrics.average_response_time = 0.5  # Placeholder
                
                # Sleep for metrics update interval
                await asyncio.sleep(10)  # 10 seconds
                
            except Exception as e:
                self.logger.error(f"Metrics update error: {e}")
    
    def _calculate_current_load(self) -> float:
        """Calculate current agent load (0.0 to 1.0)."""
        # Simplified calculation based on active tasks
        # In Phase 4, this will consider actual CPU, memory, and task queue
        active_threads = threading.active_count()
        max_threads = self.capabilities.max_concurrent_tasks
        return min(active_threads / max_threads, 1.0)
    
    def _calculate_success_rate(self) -> float:
        """Calculate verification success rate."""
        total = self.metrics.successful_verifications + self.metrics.failed_verifications
        if total == 0:
            return 1.0
        return self.metrics.successful_verifications / total
    
    def _sign_message(self, message: AgentMessage) -> str:
        """Sign a message for authenticity (simplified)."""
        # Simplified signing - in Phase 4, this will use proper cryptographic signatures
        message_data = f"{message.sender_id}{message.message_type.value}{message.timestamp}"
        return hashlib.sha256(message_data.encode()).hexdigest()
    
    def _verify_message_signature(self, message: AgentMessage) -> bool:
        """Verify message signature (simplified)."""
        # Simplified verification - in Phase 4, this will use proper cryptographic verification
        expected_signature = self._sign_message(message)
        return message.signature == expected_signature

class AgentCoordinator:
    """
    Coordinates multiple agents in the system.
    
    This class manages agent discovery, task distribution,
    consensus coordination, and network health monitoring.
    """
    
    def __init__(self):
        self.agents: Dict[str, BaseAgent] = {}
        self.logger = logging.getLogger("agent_coordinator")
        
        # Initialize audit logging
        try:
            self.audit_logger = MerkleLogWriter("logs/agent_coordinator.log")
        except Exception as e:
            self.logger.warning(f"Could not initialize audit logging: {e}")
            self.audit_logger = None
    
    def register_agent(self, agent: BaseAgent):
        """Register an agent with the coordinator."""
        self.agents[agent.agent_id] = agent
        
        # Update all agents about the new agent
        agent_info = {
            "agent_id": agent.agent_id,
            "roles": [r.value for r in agent.capabilities.roles],
            "capabilities": asdict(agent.capabilities),
            "status": agent.status.value
        }
        
        for other_agent in self.agents.values():
            if other_agent.agent_id != agent.agent_id:
                other_agent.register_agent(agent.agent_id, agent_info)
        
        self.logger.info(f"Registered agent: {agent.agent_id}")
        
        if self.audit_logger:
            self.audit_logger.add_entry({
                "event": "agent_registered",
                "agent_id": agent.agent_id,
                "total_agents": len(self.agents),
                "timestamp": int(time.time())
            })
    
    def get_agents_by_role(self, role: AgentRole) -> List[BaseAgent]:
        """Get all agents with a specific role."""
        return [agent for agent in self.agents.values() if role in agent.capabilities.roles]
    
    def get_system_status(self) -> Dict[str, Any]:
        """Get overall system status."""
        agent_statuses = {}
        total_tasks = 0
        average_load = 0.0
        
        for agent in self.agents.values():
            agent_statuses[agent.agent_id] = {
                "status": agent.status.value,
                "load": agent.metrics.current_load,
                "tasks": agent.metrics.total_tasks_processed
            }
            total_tasks += agent.metrics.total_tasks_processed
            average_load += agent.metrics.current_load
        
        if len(self.agents) > 0:
            average_load /= len(self.agents)
        
        return {
            "total_agents": len(self.agents),
            "agent_statuses": agent_statuses,
            "total_tasks_processed": total_tasks,
            "average_system_load": average_load,
            "system_health": "healthy" if average_load < 0.8 else "high_load",
            "timestamp": int(time.time())
        }

# Factory functions for creating specific agent types
def create_validator_agent(agent_id: str) -> BaseAgent:
    """Create a validation agent."""
    capabilities = AgentCapabilities(
        roles=[AgentRole.VALIDATOR],
        max_concurrent_tasks=5,
        supported_verification_types=["device", "timestamp", "location", "pattern"],
        trust_scoring_enabled=True,
        consensus_participation=True,
        specializations=["context_verification"]
    )
    return BaseAgent(agent_id, capabilities)

def create_consensus_agent(agent_id: str) -> BaseAgent:
    """Create a consensus agent."""
    capabilities = AgentCapabilities(
        roles=[AgentRole.CONSENSUS],
        max_concurrent_tasks=3,
        supported_verification_types=[],
        trust_scoring_enabled=False,
        consensus_participation=True,
        specializations=["consensus_algorithms"]
    )
    return BaseAgent(agent_id, capabilities)

def create_monitor_agent(agent_id: str) -> BaseAgent:
    """Create a monitoring agent."""
    capabilities = AgentCapabilities(
        roles=[AgentRole.MONITOR],
        max_concurrent_tasks=2,
        supported_verification_types=[],
        trust_scoring_enabled=False,
        consensus_participation=False,
        specializations=["health_monitoring", "anomaly_detection"]
    )
    return BaseAgent(agent_id, capabilities)

def create_coordinator_agent(agent_id: str) -> BaseAgent:
    """Create a coordinator agent."""
    capabilities = AgentCapabilities(
        roles=[AgentRole.COORDINATOR],
        max_concurrent_tasks=10,
        supported_verification_types=["device", "timestamp", "location", "pattern"],
        trust_scoring_enabled=True,
        consensus_participation=True,
        specializations=["coordination", "task_distribution"]
    )
    return BaseAgent(agent_id, capabilities)

# Export key classes and functions
__all__ = [
    "BaseAgent",
    "AgentCoordinator", 
    "AgentRole",
    "AgentStatus",
    "MessageType",
    "AgentMessage",
    "AgentCapabilities",
    "AgentMetrics",
    "create_validator_agent",
    "create_consensus_agent",
    "create_monitor_agent",
    "create_coordinator_agent"
]