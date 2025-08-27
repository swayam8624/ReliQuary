"""
Decision Orchestrator for Multi-Agent Consensus Coordination

This module implements the core orchestrator that coordinates decisions across
multiple specialized agents, manages consensus protocols, and ensures Byzantine
fault tolerance in the ReliQuary system.
"""

import asyncio
import json
import logging
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Set, Any, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
import uuid
from collections import defaultdict

from .consensus import DistributedConsensusManager, ConsensusPhase
from .nodes.neutral_agent import NeutralAgent
from .nodes.permissive_agent import PermissiveAgent
from .nodes.strict_agent import StrictAgent
from .nodes.watchdog_agent import WatchdogAgent
from .tools.context_checker import ContextChecker
from .tools.trust_checker import TrustChecker
from .tools.decrypt_tool import DecryptTool
from .memory.encrypted_memory import EncryptedMemorySystem, MemoryType


class DecisionType(Enum):
    """Types of decisions that can be orchestrated"""
    ACCESS_REQUEST = "access_request"
    POLICY_UPDATE = "policy_update"
    EMERGENCY_OVERRIDE = "emergency_override"
    TRUST_CALIBRATION = "trust_calibration"
    SYSTEM_MAINTENANCE = "system_maintenance"


class DecisionStatus(Enum):
    """Status of orchestrated decisions"""
    PENDING = "pending"
    EVALUATING = "evaluating"
    CONSENSUS_REACHED = "consensus_reached"
    CONSENSUS_FAILED = "consensus_failed"
    EXECUTED = "executed"
    FAILED = "failed"
    TIMEOUT = "timeout"


@dataclass
class DecisionRequest:
    """Structure for decision requests"""
    request_id: str
    decision_type: DecisionType
    requestor_id: str
    context_data: Dict[str, Any]
    priority: int  # 1 (highest) to 10 (lowest)
    timeout_seconds: float
    created_at: datetime
    metadata: Dict[str, Any]


@dataclass
class AgentDecision:
    """Individual agent's decision"""
    agent_id: str
    agent_type: str
    decision: str  # "allow" or "deny"
    confidence: float  # 0.0 to 1.0
    reasoning: str
    trust_score: float
    risk_assessment: Dict[str, Any]
    processing_time: float
    timestamp: datetime


@dataclass
class OrchestrationResult:
    """Final orchestration result"""
    request_id: str
    final_decision: str
    consensus_confidence: float
    participating_agents: List[str]
    agent_decisions: List[AgentDecision]
    consensus_metrics: Dict[str, Any]
    execution_time: float
    status: DecisionStatus
    timestamp: datetime


class DecisionOrchestrator:
    """
    Core orchestrator for multi-agent consensus decisions.
    
    Coordinates specialized agents, manages consensus protocols, and ensures
    Byzantine fault tolerance for all access control decisions.
    """
    
    def __init__(self, 
                 orchestrator_id: Optional[str] = None,
                 agent_network: Optional[List[str]] = None):
        """
        Initialize the decision orchestrator.
        
        Args:
            orchestrator_id: Unique identifier for this orchestrator
            agent_network: List of agent IDs in the network
        """
        self.orchestrator_id = orchestrator_id or f"orchestrator_{uuid.uuid4().hex[:8]}"
        self.agent_network = agent_network or [
            "neutral_agent", "permissive_agent", "strict_agent", "watchdog_agent"
        ]
        
        # Initialize consensus manager
        self.consensus_manager = DistributedConsensusManager(
            agent_id=self.orchestrator_id,
            agent_network=self.agent_network
        )
        
        # Initialize specialized agents
        self.agents = {}
        self._initialize_agents()
        
        # Initialize tools
        self.context_checker = ContextChecker()
        self.trust_checker = TrustChecker()
        self.decrypt_tool = DecryptTool(agent_id=self.orchestrator_id)
        
        # Initialize memory system
        self.memory_system = EncryptedMemorySystem(f"orchestrator_{self.orchestrator_id}")
        
        # Decision tracking
        self.pending_decisions: Dict[str, DecisionRequest] = {}
        self.active_evaluations: Dict[str, Dict[str, Any]] = {}
        self.completed_decisions: Dict[str, OrchestrationResult] = {}
        
        # Performance metrics
        self.total_decisions = 0
        self.successful_decisions = 0
        self.failed_decisions = 0
        self.consensus_success_rate = 0.0
        self.average_processing_time = 0.0
        
        # Configuration
        self.max_concurrent_decisions = 10
        self.default_timeout = 60.0  # seconds
        self.consensus_threshold = 0.6  # Minimum confidence for consensus
        
        self.logger = logging.getLogger(f"orchestrator.{self.orchestrator_id}")
        self.logger.info(f"Decision orchestrator initialized with {len(self.agent_network)} agents")
    
    def _initialize_agents(self):
        """Initialize all specialized agent instances"""
        try:
            self.agents = {
                "neutral_agent": NeutralAgent("neutral_agent", self.agent_network),
                "permissive_agent": PermissiveAgent("permissive_agent", self.agent_network),
                "strict_agent": StrictAgent("strict_agent", self.agent_network),
                "watchdog_agent": WatchdogAgent("watchdog_agent", self.agent_network)
            }
            self.logger.info("All specialized agents initialized successfully")
        except Exception as e:
            self.logger.error(f"Failed to initialize agents: {e}")
            # Initialize with empty dict if agents fail to load
            self.agents = {}
    
    async def orchestrate_decision(self, 
                                 decision_type: DecisionType,
                                 requestor_id: str,
                                 context_data: Dict[str, Any],
                                 priority: int = 5,
                                 timeout_seconds: Optional[float] = None) -> OrchestrationResult:
        """
        Orchestrate a multi-agent decision with consensus.
        
        Args:
            decision_type: Type of decision to orchestrate
            requestor_id: ID of the entity requesting the decision
            context_data: Context data for the decision
            priority: Priority level (1-10, lower is higher priority)
            timeout_seconds: Custom timeout duration
            
        Returns:
            OrchestrationResult with final consensus decision
        """
        start_time = time.time()
        request_id = f"{decision_type.value}_{uuid.uuid4().hex[:8]}"
        
        # Check if we can handle more concurrent decisions
        if len(self.active_evaluations) >= self.max_concurrent_decisions:
            self.logger.warning(f"Max concurrent decisions reached, queuing request {request_id}")
            await self._queue_decision(request_id, decision_type, requestor_id, context_data, priority)
        
        # Create decision request
        decision_request = DecisionRequest(
            request_id=request_id,
            decision_type=decision_type,
            requestor_id=requestor_id,
            context_data=context_data,
            priority=priority,
            timeout_seconds=timeout_seconds or self.default_timeout,
            created_at=datetime.now(),
            metadata={}
        )
        
        self.pending_decisions[request_id] = decision_request
        self.total_decisions += 1
        
        try:
            # Start evaluation
            self.active_evaluations[request_id] = {
                "start_time": start_time,
                "status": DecisionStatus.EVALUATING,
                "agent_decisions": {}
            }
            
            # Perform multi-agent evaluation
            agent_decisions = await self._evaluate_with_agents(decision_request)
            
            # Run consensus protocol
            consensus_result = await self._run_consensus(request_id, agent_decisions, context_data)
            
            # Create final result
            result = await self._finalize_decision(
                decision_request, agent_decisions, consensus_result, start_time
            )
            
            # Store in memory
            await self._store_decision_memory(result)
            
            self.successful_decisions += 1
            self.logger.info(f"Decision {request_id} completed successfully: {result.final_decision}")
            
            return result
            
        except asyncio.TimeoutError:
            self.failed_decisions += 1
            result = self._create_timeout_result(decision_request, start_time)
            self.logger.warning(f"Decision {request_id} timed out")
            return result
            
        except Exception as e:
            self.failed_decisions += 1
            result = self._create_error_result(decision_request, str(e), start_time)
            self.logger.error(f"Decision {request_id} failed: {e}")
            return result
            
        finally:
            # Cleanup
            if request_id in self.active_evaluations:
                del self.active_evaluations[request_id]
            if request_id in self.pending_decisions:
                del self.pending_decisions[request_id]
            
            # Update metrics
            self._update_performance_metrics()
    
    async def _evaluate_with_agents(self, decision_request: DecisionRequest) -> List[AgentDecision]:
        """
        Evaluate decision request with all available agents.
        
        Args:
            decision_request: The decision request to evaluate
            
        Returns:
            List of agent decisions
        """
        agent_decisions = []
        evaluation_tasks = []
        
        # Create evaluation tasks for each agent
        for agent_id, agent in self.agents.items():
            task = self._evaluate_single_agent(agent_id, agent, decision_request)
            evaluation_tasks.append(task)
        
        # Execute evaluations in parallel with timeout
        try:
            results = await asyncio.wait_for(
                asyncio.gather(*evaluation_tasks, return_exceptions=True),
                timeout=decision_request.timeout_seconds * 0.8  # Reserve time for consensus
            )
            
            # Process results
            for i, result in enumerate(results):
                if isinstance(result, Exception):
                    agent_id = list(self.agents.keys())[i]
                    self.logger.warning(f"Agent {agent_id} evaluation failed: {result}")
                    # Create fallback decision
                    agent_decisions.append(self._create_fallback_decision(agent_id, str(result)))
                else:
                    agent_decisions.append(result)
                    
        except asyncio.TimeoutError:
            self.logger.error(f"Agent evaluation timeout for request {decision_request.request_id}")
            # Create fallback decisions for all agents
            for agent_id in self.agents.keys():
                agent_decisions.append(self._create_fallback_decision(agent_id, "evaluation_timeout"))
        
        return agent_decisions
    
    async def _evaluate_single_agent(self, 
                                   agent_id: str, 
                                   agent: Any, 
                                   decision_request: DecisionRequest) -> AgentDecision:
        """
        Evaluate decision with a single agent.
        
        Args:
            agent_id: ID of the agent
            agent: Agent instance
            decision_request: Decision request to evaluate
            
        Returns:
            AgentDecision from the agent
        """
        start_time = time.time()
        
        try:
            # Prepare evaluation context
            context_data = decision_request.context_data.copy()
            
            # Add contextual information
            context_data.update({
                "request_id": decision_request.request_id,
                "decision_type": decision_request.decision_type.value,
                "requestor_id": decision_request.requestor_id,
                "priority": decision_request.priority
            })
            
            # Get trust score
            trust_result = await self.trust_checker.evaluate_trust(
                user_id=decision_request.requestor_id,
                context_data=context_data
            )
            trust_score = trust_result.trust_score
            
            # Evaluate with agent
            if hasattr(agent, 'evaluate_access_request'):
                result = await agent.evaluate_access_request(
                    request_id=decision_request.request_id,
                    context_data=context_data,
                    trust_score=trust_score,
                    history=[]
                )
            else:
                # Fallback evaluation
                result = {
                    "decision": "deny",
                    "confidence": 0.5,
                    "reasoning": "Agent evaluation method not available",
                    "risk_factors": []
                }
            
            processing_time = time.time() - start_time
            
            return AgentDecision(
                agent_id=agent_id,
                agent_type=type(agent).__name__,
                decision=result.get("decision", "deny"),
                confidence=result.get("confidence", 0.5),
                reasoning=result.get("reasoning", "No reasoning provided"),
                trust_score=trust_score,
                risk_assessment=result.get("risk_factors", {}),
                processing_time=processing_time,
                timestamp=datetime.now()
            )
            
        except Exception as e:
            processing_time = time.time() - start_time
            self.logger.error(f"Agent {agent_id} evaluation error: {e}")
            
            return AgentDecision(
                agent_id=agent_id,
                agent_type=type(agent).__name__ if agent else "Unknown",
                decision="deny",
                confidence=0.0,
                reasoning=f"Evaluation error: {str(e)}",
                trust_score=0.0,
                risk_assessment={"error": str(e)},
                processing_time=processing_time,
                timestamp=datetime.now()
            )
    
    async def _run_consensus(self, 
                           request_id: str,
                           agent_decisions: List[AgentDecision],
                           context_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Run consensus protocol on agent decisions.
        
        Args:
            request_id: Request identifier
            agent_decisions: List of agent decisions
            context_data: Context data for the decision
            
        Returns:
            Consensus result
        """
        # Prepare agent decisions for consensus
        consensus_input = {}
        for decision in agent_decisions:
            consensus_input[decision.agent_id] = {
                "decision": decision.decision,
                "confidence": decision.confidence,
                "trust_score": decision.trust_score,
                "reasoning": decision.reasoning,
                "processing_time": decision.processing_time
            }
        
        # Run distributed consensus
        try:
            consensus_result = await self.consensus_manager.propose_access_decision(
                access_request_id=request_id,
                agent_decisions=consensus_input,
                context_data=context_data
            )
            
            return consensus_result
            
        except Exception as e:
            self.logger.error(f"Consensus failed for request {request_id}: {e}")
            return {
                "decision": "deny",
                "confidence": 0.0,
                "reason": f"consensus_error: {str(e)}"
            }
    
    async def _finalize_decision(self,
                               decision_request: DecisionRequest,
                               agent_decisions: List[AgentDecision],
                               consensus_result: Dict[str, Any],
                               start_time: float) -> OrchestrationResult:
        """
        Finalize the orchestrated decision.
        
        Args:
            decision_request: Original decision request
            agent_decisions: List of agent decisions
            consensus_result: Result from consensus protocol
            start_time: Start time for processing
            
        Returns:
            Final orchestration result
        """
        execution_time = time.time() - start_time
        
        # Determine final status
        if consensus_result.get("decision") in ["allow", "deny"]:
            status = DecisionStatus.CONSENSUS_REACHED
        else:
            status = DecisionStatus.CONSENSUS_FAILED
        
        # Get consensus metrics
        consensus_metrics = self.consensus_manager.get_consensus_status()
        
        result = OrchestrationResult(
            request_id=decision_request.request_id,
            final_decision=consensus_result.get("decision", "deny"),
            consensus_confidence=consensus_result.get("confidence", 0.0),
            participating_agents=[d.agent_id for d in agent_decisions],
            agent_decisions=agent_decisions,
            consensus_metrics=consensus_metrics,
            execution_time=execution_time,
            status=status,
            timestamp=datetime.now()
        )
        
        self.completed_decisions[decision_request.request_id] = result
        return result
    
    def _create_fallback_decision(self, agent_id: str, error_reason: str) -> AgentDecision:
        """Create a fallback decision when agent evaluation fails"""
        return AgentDecision(
            agent_id=agent_id,
            agent_type="Unknown",
            decision="deny",
            confidence=0.0,
            reasoning=f"Fallback decision due to: {error_reason}",
            trust_score=0.0,
            risk_assessment={"fallback": True, "error": error_reason},
            processing_time=0.0,
            timestamp=datetime.now()
        )
    
    def _create_timeout_result(self, decision_request: DecisionRequest, start_time: float) -> OrchestrationResult:
        """Create result for timed out decisions"""
        return OrchestrationResult(
            request_id=decision_request.request_id,
            final_decision="deny",
            consensus_confidence=0.0,
            participating_agents=[],
            agent_decisions=[],
            consensus_metrics={},
            execution_time=time.time() - start_time,
            status=DecisionStatus.TIMEOUT,
            timestamp=datetime.now()
        )
    
    def _create_error_result(self, decision_request: DecisionRequest, error: str, start_time: float) -> OrchestrationResult:
        """Create result for failed decisions"""
        return OrchestrationResult(
            request_id=decision_request.request_id,
            final_decision="deny",
            consensus_confidence=0.0,
            participating_agents=[],
            agent_decisions=[],
            consensus_metrics={"error": error},
            execution_time=time.time() - start_time,
            status=DecisionStatus.FAILED,
            timestamp=datetime.now()
        )
    
    async def _store_decision_memory(self, result: OrchestrationResult):
        """Store decision result in encrypted memory"""
        try:
            memory_data = {
                "request_id": result.request_id,
                "final_decision": result.final_decision,
                "consensus_confidence": result.consensus_confidence,
                "execution_time": result.execution_time,
                "status": result.status.value,
                "agent_count": len(result.participating_agents),
                "timestamp": result.timestamp.isoformat()
            }
            
            await self.memory_system.store_memory(
                agent_id=self.orchestrator_id,
                memory_type=MemoryType.DECISION_HISTORY,
                data=memory_data
            )
            
        except Exception as e:
            self.logger.error(f"Failed to store decision memory: {e}")
    
    async def _queue_decision(self, request_id: str, decision_type: DecisionType, 
                            requestor_id: str, context_data: Dict[str, Any], priority: int):
        """Queue decision when at capacity"""
        # For now, just wait and retry
        await asyncio.sleep(1.0)
    
    def _update_performance_metrics(self):
        """Update performance metrics"""
        if self.total_decisions > 0:
            self.consensus_success_rate = self.successful_decisions / self.total_decisions
        
        # Calculate average processing time from recent decisions
        recent_decisions = list(self.completed_decisions.values())[-10:]
        if recent_decisions:
            self.average_processing_time = sum(d.execution_time for d in recent_decisions) / len(recent_decisions)
    
    def get_orchestration_status(self) -> Dict[str, Any]:
        """Get current orchestration status and metrics"""
        return {
            "orchestrator_id": self.orchestrator_id,
            "agent_network": self.agent_network,
            "total_decisions": self.total_decisions,
            "successful_decisions": self.successful_decisions,
            "failed_decisions": self.failed_decisions,
            "consensus_success_rate": self.consensus_success_rate,
            "average_processing_time": self.average_processing_time,
            "pending_decisions": len(self.pending_decisions),
            "active_evaluations": len(self.active_evaluations),
            "completed_decisions": len(self.completed_decisions),
            "agents_available": list(self.agents.keys()),
            "consensus_metrics": self.consensus_manager.get_consensus_status()
        }
    
    async def get_decision_history(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Get recent decision history"""
        try:
            memories = await self.memory_system.retrieve_memories(
                agent_id=self.orchestrator_id,
                memory_type=MemoryType.DECISION_HISTORY,
                limit=limit
            )
            return [memory["data"] for memory in memories]
        except Exception as e:
            self.logger.error(f"Failed to retrieve decision history: {e}")
            return []
    
    async def emergency_override(self, request_id: str, override_decision: str, reason: str) -> bool:
        """
        Emergency override for critical situations.
        
        Args:
            request_id: Request to override
            override_decision: New decision ("allow" or "deny")
            reason: Reason for override
            
        Returns:
            True if override successful
        """
        try:
            if request_id in self.completed_decisions:
                original_result = self.completed_decisions[request_id]
                
                # Create override result
                override_result = OrchestrationResult(
                    request_id=f"{request_id}_override",
                    final_decision=override_decision,
                    consensus_confidence=1.0,
                    participating_agents=["emergency_override"],
                    agent_decisions=[],
                    consensus_metrics={"override_reason": reason},
                    execution_time=0.0,
                    status=DecisionStatus.EXECUTED,
                    timestamp=datetime.now()
                )
                
                self.completed_decisions[f"{request_id}_override"] = override_result
                
                # Store override memory
                await self._store_decision_memory(override_result)
                
                self.logger.warning(f"Emergency override applied to {request_id}: {override_decision} - {reason}")
                return True
            
            return False
            
        except Exception as e:
            self.logger.error(f"Emergency override failed: {e}")
            return False