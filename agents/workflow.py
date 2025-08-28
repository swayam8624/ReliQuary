"""
LangGraph Workflow for ReliQuary Multi-Agent State Management

This module implements comprehensive workflow management using LangGraph
for coordinating agent states, message passing, and decision orchestration
in the ReliQuary multi-agent system.
"""

import asyncio
import json
import logging
import time
from typing import Dict, List, Any, Optional, Union, Callable
from dataclasses import dataclass, asdict
from enum import Enum
import uuid
from datetime import datetime

try:
    from langgraph.graph import StateGraph, END, START
    from langgraph.graph.message import AnyMessage, add_messages
    from langgraph.prebuilt import ToolNode
    from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, SystemMessage
    from pydantic import BaseModel, Field
except ImportError:
    # Fallback for development without LangGraph
    logging.warning("LangGraph not available, using fallback implementations")
    
    class StateGraph:
        def __init__(self, state_schema): 
            self.state_schema = state_schema
            self.nodes = {}
            self.edges = {}
            
        def add_node(self, name, func): 
            self.nodes[name] = func
            
        def add_edge(self, from_node, to_node): 
            if from_node not in self.edges:
                self.edges[from_node] = []
            self.edges[from_node].append(to_node)
            
        def add_conditional_edges(self, from_node, condition, mapping): 
            self.edges[from_node] = {"condition": condition, "mapping": mapping}
            
        def compile(self): 
            return WorkflowGraph(self.nodes, self.edges, self.state_schema)
    
    class BaseMessage:
        def __init__(self, content, **kwargs):
            self.content = content
            for k, v in kwargs.items():
                setattr(self, k, v)
    
    class HumanMessage(BaseMessage): pass
    class AIMessage(BaseMessage): pass
    class SystemMessage(BaseMessage): pass
    
    END = "__END__"
    START = "__START__"


class WorkflowPhase(Enum):
    """Phases in the agent workflow"""
    INITIALIZATION = "initialization"
    CONTEXT_ANALYSIS = "context_analysis"
    AGENT_EVALUATION = "agent_evaluation"
    CONSENSUS_BUILDING = "consensus_building"
    DECISION_FINALIZATION = "decision_finalization"
    EXECUTION = "execution"
    AUDIT_LOGGING = "audit_logging"
    COMPLETION = "completion"


class AgentRole(Enum):
    """Roles agents can play in workflows"""
    COORDINATOR = "coordinator"
    EVALUATOR = "evaluator"
    VALIDATOR = "validator"
    MONITOR = "monitor"
    EXECUTOR = "executor"


class MessageType(Enum):
    """Types of messages in the workflow"""
    REQUEST = "request"
    RESPONSE = "response"
    NOTIFICATION = "notification"
    STATUS_UPDATE = "status_update"
    ERROR = "error"
    CONSENSUS_VOTE = "consensus_vote"
    AUDIT_LOG = "audit_log"


@dataclass
class WorkflowState:
    """State container for LangGraph workflows"""
    request_id: str
    workflow_phase: WorkflowPhase
    messages: List[BaseMessage]
    agent_states: Dict[str, Dict[str, Any]]
    context_data: Dict[str, Any]
    decision_data: Dict[str, Any]
    consensus_data: Dict[str, Any]
    execution_results: Dict[str, Any]
    audit_trail: List[Dict[str, Any]]
    metadata: Dict[str, Any]
    created_at: datetime
    updated_at: datetime
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert state to dictionary for serialization"""
        return {
            "request_id": self.request_id,
            "workflow_phase": self.workflow_phase.value,
            "messages": [{"content": msg.content, "type": type(msg).__name__} for msg in self.messages],
            "agent_states": self.agent_states,
            "context_data": self.context_data,
            "decision_data": self.decision_data,
            "consensus_data": self.consensus_data,
            "execution_results": self.execution_results,
            "audit_trail": self.audit_trail,
            "metadata": self.metadata,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat()
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "WorkflowState":
        """Create state from dictionary"""
        messages = []
        for msg_data in data.get("messages", []):
            msg_type = msg_data.get("type", "BaseMessage")
            if msg_type == "HumanMessage":
                messages.append(HumanMessage(content=msg_data["content"]))
            elif msg_type == "AIMessage":
                messages.append(AIMessage(content=msg_data["content"]))
            elif msg_type == "SystemMessage":
                messages.append(SystemMessage(content=msg_data["content"]))
            else:
                messages.append(BaseMessage(content=msg_data["content"]))
        
        return cls(
            request_id=data["request_id"],
            workflow_phase=WorkflowPhase(data["workflow_phase"]),
            messages=messages,
            agent_states=data.get("agent_states", {}),
            context_data=data.get("context_data", {}),
            decision_data=data.get("decision_data", {}),
            consensus_data=data.get("consensus_data", {}),
            execution_results=data.get("execution_results", {}),
            audit_trail=data.get("audit_trail", []),
            metadata=data.get("metadata", {}),
            created_at=datetime.fromisoformat(data["created_at"]),
            updated_at=datetime.fromisoformat(data["updated_at"])
        )


@dataclass
class WorkflowMessage:
    """Message for inter-agent communication"""
    message_id: str
    sender_id: str
    recipient_id: Optional[str]
    message_type: MessageType
    content: Dict[str, Any]
    timestamp: datetime
    priority: int = 5
    requires_response: bool = False
    correlation_id: Optional[str] = None


class WorkflowGraph:
    """Fallback workflow graph implementation"""
    
    def __init__(self, nodes: Dict, edges: Dict, state_schema):
        self.nodes = nodes
        self.edges = edges
        self.state_schema = state_schema
        
    async def ainvoke(self, initial_state: Dict) -> Dict:
        """Execute the workflow graph"""
        current_state = initial_state.copy()
        current_node = "initialization"
        
        while current_node and current_node != END:
            if current_node in self.nodes:
                result = await self.nodes[current_node](current_state)
                current_state.update(result)
                
                # Determine next node
                if current_node in self.edges:
                    edge_config = self.edges[current_node]
                    if isinstance(edge_config, list):
                        current_node = edge_config[0] if edge_config else END
                    elif isinstance(edge_config, dict):
                        condition = edge_config.get("condition")
                        mapping = edge_config.get("mapping", {})
                        if condition:
                            next_key = condition(current_state)
                            current_node = mapping.get(next_key, END)
                        else:
                            current_node = END
                    else:
                        current_node = END
                else:
                    current_node = END
            else:
                break
                
        return current_state


class AgentWorkflowCoordinator:
    """
    Coordinates LangGraph workflows for multi-agent operations.
    """
    
    def __init__(self, coordinator_id: Optional[str] = None):
        """Initialize the workflow coordinator."""
        self.coordinator_id = coordinator_id or f"coordinator_{uuid.uuid4().hex[:8]}"
        self.logger = logging.getLogger(f"workflow.{self.coordinator_id}")
        
        # Workflow management
        self.active_workflows: Dict[str, Any] = {}
        self.workflow_history: Dict[str, WorkflowState] = {}
        self.message_queue: Dict[str, List[WorkflowMessage]] = {}
        
        # Agent registration
        self.registered_agents: Dict[str, Dict[str, Any]] = {}
        self.agent_capabilities: Dict[str, List[str]] = {}
        
        # Performance metrics
        self.total_workflows = 0
        self.successful_workflows = 0
        self.failed_workflows = 0
        self.average_workflow_time = 0.0
        
        # Create main workflow graph
        self.main_workflow = self._create_main_workflow()
        
        self.logger.info(f"Workflow coordinator {self.coordinator_id} initialized")
    
    def _create_main_workflow(self) -> Any:
        """Create the main LangGraph workflow for agent coordination."""
        
        # Define workflow state schema
        workflow = StateGraph(WorkflowState)
        
        # Add workflow nodes
        workflow.add_node("initialization", self._initialize_workflow)
        workflow.add_node("context_analysis", self._analyze_context)
        workflow.add_node("agent_evaluation", self._coordinate_agent_evaluation)
        workflow.add_node("consensus_building", self._build_consensus)
        workflow.add_node("decision_finalization", self._finalize_decision)
        workflow.add_node("execution", self._execute_decision)
        workflow.add_node("audit_logging", self._log_audit_trail)
        workflow.add_node("completion", self._complete_workflow)
        
        # Add workflow edges
        workflow.add_edge(START, "initialization")  # Add entrypoint from START
        workflow.add_edge("initialization", "context_analysis")
        workflow.add_edge("context_analysis", "agent_evaluation")
        workflow.add_edge("agent_evaluation", "consensus_building")
        workflow.add_edge("consensus_building", "decision_finalization")
        workflow.add_edge("decision_finalization", "execution")
        workflow.add_edge("execution", "audit_logging")
        workflow.add_edge("audit_logging", "completion")
        workflow.add_edge("completion", END)
        
        # Add conditional edges for error handling
        workflow.add_conditional_edges(
            "consensus_building",
            self._should_retry_consensus,
            {
                "retry": "agent_evaluation",
                "proceed": "decision_finalization",
                "fail": "audit_logging"
            }
        )
        
        return workflow.compile()
    
    async def start_workflow(self, 
                           request_id: str,
                           workflow_type: str,
                           initial_context: Dict[str, Any],
                           participating_agents: Optional[List[str]] = None) -> WorkflowState:
        """
        Start a new agent workflow.
        
        Args:
            request_id: Unique identifier for the request
            workflow_type: Type of workflow to execute
            initial_context: Initial context data
            participating_agents: List of agents to participate
            
        Returns:
            Final workflow state
        """
        start_time = time.time()
        self.total_workflows += 1
        
        try:
            # Create initial workflow state
            initial_state = WorkflowState(
                request_id=request_id,
                workflow_phase=WorkflowPhase.INITIALIZATION,
                messages=[SystemMessage(content=f"Starting {workflow_type} workflow")],
                agent_states={},
                context_data=initial_context,
                decision_data={},
                consensus_data={},
                execution_results={},
                audit_trail=[],
                metadata={
                    "workflow_type": workflow_type,
                    "participating_agents": participating_agents or [],
                    "coordinator_id": self.coordinator_id
                },
                created_at=datetime.now(),
                updated_at=datetime.now()
            )
            
            # Store active workflow
            self.active_workflows[request_id] = initial_state
            
            # Execute workflow
            final_state_dict = await self.main_workflow.ainvoke(initial_state.to_dict())
            final_state = WorkflowState.from_dict(final_state_dict)
            
            # Store completed workflow
            self.workflow_history[request_id] = final_state
            
            # Update metrics
            processing_time = time.time() - start_time
            self._update_workflow_metrics(processing_time, True)
            
            self.logger.info(f"Workflow {request_id} completed successfully in {processing_time:.2f}s")
            return final_state
            
        except Exception as e:
            self.logger.error(f"Workflow {request_id} failed: {e}")
            processing_time = time.time() - start_time
            self._update_workflow_metrics(processing_time, False)
            
            # Create error state
            error_state = WorkflowState(
                request_id=request_id,
                workflow_phase=WorkflowPhase.COMPLETION,
                messages=[AIMessage(content=f"Workflow failed: {str(e)}")],
                agent_states={},
                context_data=initial_context,
                decision_data={"error": str(e)},
                consensus_data={},
                execution_results={"success": False, "error": str(e)},
                audit_trail=[{"action": "workflow_error", "error": str(e), "timestamp": time.time()}],
                metadata={"workflow_type": workflow_type, "error": True},
                created_at=datetime.now(),
                updated_at=datetime.now()
            )
            
            self.workflow_history[request_id] = error_state
            return error_state
        finally:
            # Cleanup
            if request_id in self.active_workflows:
                del self.active_workflows[request_id]
    
    async def _initialize_workflow(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Initialize workflow phase."""
        self.logger.info(f"Initializing workflow {state['request_id']}")
        
        # Update state
        state["workflow_phase"] = WorkflowPhase.CONTEXT_ANALYSIS.value
        state["updated_at"] = datetime.now().isoformat()
        
        # Add initialization message
        init_message = AIMessage(content="Workflow initialized successfully")
        state["messages"].append({"content": init_message.content, "type": "AIMessage"})
        
        # Initialize agent states
        participating_agents = state.get("metadata", {}).get("participating_agents", [])
        for agent_id in participating_agents:
            state["agent_states"][agent_id] = {
                "status": "initialized",
                "role": AgentRole.EVALUATOR.value,
                "last_update": time.time()
            }
        
        # Add audit trail entry
        state["audit_trail"].append({
            "phase": "initialization",
            "action": "workflow_started",
            "timestamp": time.time(),
            "details": {"participating_agents": participating_agents}
        })
        
        return state
    
    async def _analyze_context(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze context phase."""
        self.logger.info(f"Analyzing context for workflow {state['request_id']}")
        
        # Update state
        state["workflow_phase"] = WorkflowPhase.AGENT_EVALUATION.value
        state["updated_at"] = datetime.now().isoformat()
        
        # Analyze context data
        context_data = state.get("context_data", {})
        
        # Perform context analysis
        analysis_results = {
            "context_completeness": self._assess_context_completeness(context_data),
            "risk_indicators": self._identify_risk_indicators(context_data),
            "trust_factors": self._extract_trust_factors(context_data),
            "complexity_score": self._calculate_complexity_score(context_data)
        }
        
        state["context_analysis"] = analysis_results
        
        # Add analysis message
        analysis_message = AIMessage(
            content=f"Context analysis completed. Complexity: {analysis_results['complexity_score']}"
        )
        state["messages"].append({"content": analysis_message.content, "type": "AIMessage"})
        
        # Add audit trail entry
        state["audit_trail"].append({
            "phase": "context_analysis",
            "action": "context_analyzed",
            "timestamp": time.time(),
            "details": analysis_results
        })
        
        return state
    
    async def _coordinate_agent_evaluation(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Coordinate agent evaluation phase."""
        self.logger.info(f"Coordinating agent evaluation for workflow {state['request_id']}")
        
        # Update state
        state["workflow_phase"] = WorkflowPhase.CONSENSUS_BUILDING.value
        state["updated_at"] = datetime.now().isoformat()
        
        # Get participating agents
        participating_agents = state.get("metadata", {}).get("participating_agents", [])
        
        # Simulate agent evaluations (in real implementation, this would coordinate with actual agents)
        evaluation_results = {}
        for agent_id in participating_agents:
            # Simulate evaluation
            evaluation_results[agent_id] = {
                "decision": "allow" if hash(agent_id + state["request_id"]) % 2 == 0 else "deny",
                "confidence": 0.75 + (hash(agent_id) % 25) / 100,
                "reasoning": f"Evaluation completed by {agent_id}",
                "processing_time": 0.5 + (hash(agent_id) % 10) / 10,
                "timestamp": time.time()
            }
            
            # Update agent state
            state["agent_states"][agent_id].update({
                "status": "evaluation_complete",
                "last_update": time.time(),
                "evaluation": evaluation_results[agent_id]
            })
        
        state["evaluation_results"] = evaluation_results
        
        # Add evaluation message
        eval_message = AIMessage(
            content=f"Agent evaluations completed. {len(evaluation_results)} agents participated."
        )
        state["messages"].append({"content": eval_message.content, "type": "AIMessage"})
        
        # Add audit trail entry
        state["audit_trail"].append({
            "phase": "agent_evaluation",
            "action": "evaluations_completed",
            "timestamp": time.time(),
            "details": {"agent_count": len(evaluation_results)}
        })
        
        return state
    
    async def _build_consensus(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Build consensus phase."""
        self.logger.info(f"Building consensus for workflow {state['request_id']}")
        
        # Update state
        state["workflow_phase"] = WorkflowPhase.DECISION_FINALIZATION.value
        state["updated_at"] = datetime.now().isoformat()
        
        # Get evaluation results
        evaluation_results = state.get("evaluation_results", {})
        
        # Calculate consensus
        allow_votes = sum(1 for result in evaluation_results.values() 
                         if result.get("decision") == "allow")
        deny_votes = sum(1 for result in evaluation_results.values() 
                        if result.get("decision") == "deny")
        
        total_confidence = sum(result.get("confidence", 0) 
                             for result in evaluation_results.values())
        average_confidence = total_confidence / max(len(evaluation_results), 1)
        
        # Determine consensus
        consensus_reached = abs(allow_votes - deny_votes) >= 1
        final_decision = "allow" if allow_votes > deny_votes else "deny"
        
        consensus_data = {
            "consensus_reached": consensus_reached,
            "final_decision": final_decision,
            "allow_votes": allow_votes,
            "deny_votes": deny_votes,
            "average_confidence": average_confidence,
            "consensus_confidence": average_confidence if consensus_reached else 0.0,
            "participating_agents": list(evaluation_results.keys())
        }
        
        state["consensus_data"] = consensus_data
        
        # Add consensus message
        consensus_message = AIMessage(
            content=f"Consensus {'reached' if consensus_reached else 'failed'}: {final_decision}"
        )
        state["messages"].append({"content": consensus_message.content, "type": "AIMessage"})
        
        # Add audit trail entry
        state["audit_trail"].append({
            "phase": "consensus_building",
            "action": "consensus_determined",
            "timestamp": time.time(),
            "details": consensus_data
        })
        
        return state
    
    async def _finalize_decision(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Finalize decision phase."""
        self.logger.info(f"Finalizing decision for workflow {state['request_id']}")
        
        # Update state
        state["workflow_phase"] = WorkflowPhase.EXECUTION.value
        state["updated_at"] = datetime.now().isoformat()
        
        # Get consensus data
        consensus_data = state.get("consensus_data", {})
        
        # Finalize decision
        decision_data = {
            "final_decision": consensus_data.get("final_decision", "deny"),
            "confidence": consensus_data.get("consensus_confidence", 0.0),
            "consensus_reached": consensus_data.get("consensus_reached", False),
            "decision_timestamp": time.time(),
            "decision_id": f"decision_{uuid.uuid4().hex[:8]}"
        }
        
        state["decision_data"] = decision_data
        
        # Add decision message
        decision_message = AIMessage(
            content=f"Decision finalized: {decision_data['final_decision']} (confidence: {decision_data['confidence']:.2f})"
        )
        state["messages"].append({"content": decision_message.content, "type": "AIMessage"})
        
        # Add audit trail entry
        state["audit_trail"].append({
            "phase": "decision_finalization",
            "action": "decision_finalized",
            "timestamp": time.time(),
            "details": decision_data
        })
        
        return state
    
    async def _execute_decision(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Execute decision phase."""
        self.logger.info(f"Executing decision for workflow {state['request_id']}")
        
        # Update state
        state["workflow_phase"] = WorkflowPhase.AUDIT_LOGGING.value
        state["updated_at"] = datetime.now().isoformat()
        
        # Get decision data
        decision_data = state.get("decision_data", {})
        
        # Execute decision (simulation)
        execution_results = {
            "success": True,
            "execution_time": time.time(),
            "action_taken": decision_data.get("final_decision", "deny"),
            "execution_id": f"exec_{uuid.uuid4().hex[:8]}"
        }
        
        state["execution_results"] = execution_results
        
        # Add execution message
        exec_message = AIMessage(
            content=f"Decision executed successfully: {execution_results['action_taken']}"
        )
        state["messages"].append({"content": exec_message.content, "type": "AIMessage"})
        
        # Add audit trail entry
        state["audit_trail"].append({
            "phase": "execution",
            "action": "decision_executed",
            "timestamp": time.time(),
            "details": execution_results
        })
        
        return state
    
    async def _log_audit_trail(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Log audit trail phase."""
        self.logger.info(f"Logging audit trail for workflow {state['request_id']}")
        
        # Update state
        state["workflow_phase"] = WorkflowPhase.COMPLETION.value
        state["updated_at"] = datetime.now().isoformat()
        
        # Finalize audit trail
        final_audit_entry = {
            "phase": "audit_logging",
            "action": "workflow_completed",
            "timestamp": time.time(),
            "details": {
                "total_phases": len(state["audit_trail"]),
                "workflow_duration": time.time() - datetime.fromisoformat(state["created_at"]).timestamp()
            }
        }
        
        state["audit_trail"].append(final_audit_entry)
        
        # Add completion message
        completion_message = AIMessage(
            content=f"Workflow completed. Audit trail logged with {len(state['audit_trail'])} entries."
        )
        state["messages"].append({"content": completion_message.content, "type": "AIMessage"})
        
        return state
    
    async def _complete_workflow(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Complete workflow phase."""
        self.logger.info(f"Completing workflow {state['request_id']}")
        
        # Final state update
        state["updated_at"] = datetime.now().isoformat()
        
        # Add final completion message
        final_message = AIMessage(content="Workflow completed successfully")
        state["messages"].append({"content": final_message.content, "type": "AIMessage"})
        
        return state
    
    def _should_retry_consensus(self, state: Dict[str, Any]) -> str:
        """Determine if consensus should be retried."""
        consensus_data = state.get("consensus_data", {})
        
        if not consensus_data.get("consensus_reached", False):
            # Check if we can retry
            retry_count = state.get("metadata", {}).get("retry_count", 0)
            if retry_count < 2:
                state["metadata"]["retry_count"] = retry_count + 1
                return "retry"
            else:
                return "fail"
        
        return "proceed"
    
    def _assess_context_completeness(self, context_data: Dict[str, Any]) -> float:
        """Assess how complete the context data is."""
        required_fields = ["user_id", "resource_id", "action"]
        optional_fields = ["location", "device_id", "timestamp"]
        
        required_score = sum(1 for field in required_fields if field in context_data) / len(required_fields)
        optional_score = sum(1 for field in optional_fields if field in context_data) / len(optional_fields)
        
        return (required_score * 0.8) + (optional_score * 0.2)
    
    def _identify_risk_indicators(self, context_data: Dict[str, Any]) -> List[str]:
        """Identify risk indicators in context data."""
        risk_indicators = []
        
        if context_data.get("location", "").startswith("unknown"):
            risk_indicators.append("Unknown location")
        
        if context_data.get("device_id", "").startswith("unregistered"):
            risk_indicators.append("Unregistered device")
        
        if "suspicious_activity" in context_data:
            risk_indicators.append("Suspicious activity detected")
        
        return risk_indicators
    
    def _extract_trust_factors(self, context_data: Dict[str, Any]) -> List[str]:
        """Extract trust factors from context data."""
        trust_factors = []
        
        if context_data.get("verified_device", False):
            trust_factors.append("Verified device")
        
        if context_data.get("known_location", False):
            trust_factors.append("Known location")
        
        if context_data.get("recent_activity", False):
            trust_factors.append("Recent legitimate activity")
        
        return trust_factors
    
    def _calculate_complexity_score(self, context_data: Dict[str, Any]) -> float:
        """Calculate complexity score for the context."""
        base_complexity = len(context_data) / 10.0
        
        # Adjust for specific complexity factors
        if "multi_factor_auth" in context_data:
            base_complexity += 0.2
        
        if "cross_domain_access" in context_data:
            base_complexity += 0.3
        
        return min(1.0, base_complexity)
    
    def _update_workflow_metrics(self, processing_time: float, success: bool):
        """Update workflow performance metrics."""
        if success:
            self.successful_workflows += 1
        else:
            self.failed_workflows += 1
        
        # Update average processing time
        total_time = self.average_workflow_time * (self.total_workflows - 1) + processing_time
        self.average_workflow_time = total_time / self.total_workflows
    
    def get_workflow_status(self) -> Dict[str, Any]:
        """Get current workflow coordinator status."""
        return {
            "coordinator_id": self.coordinator_id,
            "total_workflows": self.total_workflows,
            "successful_workflows": self.successful_workflows,
            "failed_workflows": self.failed_workflows,
            "success_rate": self.successful_workflows / max(self.total_workflows, 1),
            "average_workflow_time": self.average_workflow_time,
            "active_workflows": len(self.active_workflows),
            "registered_agents": len(self.registered_agents)
        }
    
    def register_agent(self, agent_id: str, capabilities: List[str], metadata: Optional[Dict[str, Any]] = None):
        """Register an agent with the workflow coordinator."""
        self.registered_agents[agent_id] = {
            "capabilities": capabilities,
            "metadata": metadata or {},
            "registered_at": datetime.now().isoformat(),
            "status": "active"
        }
        self.agent_capabilities[agent_id] = capabilities
        self.logger.info(f"Agent {agent_id} registered with capabilities: {capabilities}")
    
    async def send_message(self, message: WorkflowMessage):
        """Send a message to an agent or broadcast."""
        if message.recipient_id:
            # Direct message
            if message.recipient_id not in self.message_queue:
                self.message_queue[message.recipient_id] = []
            self.message_queue[message.recipient_id].append(message)
        else:
            # Broadcast message
            for agent_id in self.registered_agents.keys():
                if agent_id not in self.message_queue:
                    self.message_queue[agent_id] = []
                self.message_queue[agent_id].append(message)
    
    async def get_messages(self, agent_id: str) -> List[WorkflowMessage]:
        """Get pending messages for an agent."""
        messages = self.message_queue.get(agent_id, [])
        self.message_queue[agent_id] = []  # Clear after retrieval
        return messages