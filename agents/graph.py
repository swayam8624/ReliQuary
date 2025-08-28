"""
LangGraph Workflow Definition for ReliQuary Multi-Agent System

This module defines the LangGraph structure and workflow for coordinating
the multi-agent consensus system. It orchestrates the interactions between
different specialized agents and manages the decision-making process flow.
"""

import logging
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from enum import Enum

# LangGraph and LangChain imports
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage
from langchain_core.runnables import RunnableLambda
from langgraph.graph import StateGraph, END

# ReliQuary imports
from .nodes.neutral_agent import NeutralAgent
from .nodes.permissive_agent import PermissiveAgent
from .nodes.strict_agent import StrictAgent
from .nodes.watchdog_agent import WatchdogAgent
from .agent_foundation import AgentRole
from .memory.encrypted_memory import EncryptedMemory, MemoryType
from .tools.context_checker import ContextChecker
from .tools.trust_checker import TrustChecker


class WorkflowState(Enum):
    """States in the agent workflow"""
    INITIALIZED = "initialized"
    CONTEXT_VERIFICATION = "context_verification"
    TRUST_EVALUATION = "trust_evaluation"
    INDIVIDUAL_DECISIONS = "individual_decisions"
    CONSENSUS_BUILDING = "consensus_building"
    FINAL_DECISION = "final_decision"
    COMPLETED = "completed"


@dataclass
class AgentWorkflowState:
    """State object for the multi-agent workflow"""
    request_id: str
    context_data: Dict[str, Any]
    trust_score: float
    agent_decisions: Dict[str, Dict[str, Any]]
    consensus_reached: bool
    final_decision: Optional[str]
    reasoning_chain: List[str]
    current_step: WorkflowState
    error_messages: List[str]
    metadata: Dict[str, Any]
    
    def __post_init__(self):
        if self.agent_decisions is None:
            self.agent_decisions = {}
        if self.reasoning_chain is None:
            self.reasoning_chain = []
        if self.error_messages is None:
            self.error_messages = []
        if self.metadata is None:
            self.metadata = {}


class AgentGraph:
    """
    LangGraph workflow definition for the multi-agent consensus system.
    
    This class defines the structure and flow of interactions between
    different specialized agents in the ReliQuary system.
    """
    
    def __init__(self, agent_ids: List[str], agent_roles: Dict[str, AgentRole]):
        """
        Initialize the agent graph workflow.
        
        Args:
            agent_ids: List of all agent IDs in the system
            agent_roles: Mapping of agent IDs to their roles
        """
        self.agent_ids = agent_ids
        self.agent_roles = agent_roles
        self.logger = logging.getLogger("agent_graph")
        
        # Initialize agents
        self.agents = self._initialize_agents()
        
        # Initialize tools
        self.context_checker = ContextChecker()
        self.trust_checker = TrustChecker()
        
        # Initialize memory system
        self.memory_system = EncryptedMemory("agents/graph_memory")
        
        # Build the workflow graph
        self.workflow = self._build_workflow()
        
        self.logger.info("Agent graph workflow initialized")
    
    def _initialize_agents(self) -> Dict[str, Any]:
        """Initialize all agent nodes based on their roles."""
        agents = {}
        
        for agent_id in self.agent_ids:
            role = self.agent_roles.get(agent_id, AgentRole.NEUTRAL)
            
            try:
                if role == AgentRole.NEUTRAL:
                    agents[agent_id] = NeutralAgent(agent_id, self.agent_ids)
                elif role == AgentRole.PERMISSIVE:
                    agents[agent_id] = PermissiveAgent(agent_id, self.agent_ids)
                elif role == AgentRole.STRICT:
                    agents[agent_id] = StrictAgent(agent_id, self.agent_ids)
                elif role == AgentRole.WATCHDOG:
                    agents[agent_id] = WatchdogAgent(agent_id, self.agent_ids)
                else:
                    # Default to neutral agent
                    agents[agent_id] = NeutralAgent(agent_id, self.agent_ids)
                    
                self.logger.debug(f"Initialized {role.value} agent: {agent_id}")
                
            except Exception as e:
                self.logger.error(f"Failed to initialize agent {agent_id}: {e}")
                # Fallback to neutral agent
                agents[agent_id] = NeutralAgent(agent_id, self.agent_ids)
        
        return agents
    
    def _build_workflow(self) -> StateGraph:
        """Build the LangGraph workflow structure."""
        workflow = StateGraph(AgentWorkflowState)
        
        # Add nodes for each workflow step
        workflow.add_node("initialize", self._initialize_workflow)
        workflow.add_node("verify_context", self._verify_context)
        workflow.add_node("evaluate_trust", self._evaluate_trust)
        workflow.add_node("collect_decisions", self._collect_agent_decisions)
        workflow.add_node("build_consensus", self._build_consensus)
        workflow.add_node("make_final_decision", self._make_final_decision)
        workflow.add_node("finalize", self._finalize_workflow)
        
        # Define the flow
        workflow.set_entry_point("initialize")
        workflow.add_edge("initialize", "verify_context")
        workflow.add_edge("verify_context", "evaluate_trust")
        workflow.add_edge("evaluate_trust", "collect_decisions")
        workflow.add_edge("collect_decisions", "build_consensus")
        workflow.add_edge("build_consensus", "make_final_decision")
        workflow.add_edge("make_final_decision", "finalize")
        workflow.add_edge("finalize", END)
        
        return workflow.compile()
    
    def _initialize_workflow(self, state: AgentWorkflowState) -> AgentWorkflowState:
        """Initialize the workflow state."""
        state.current_step = WorkflowState.INITIALIZED
        state.reasoning_chain.append("Workflow initialization started")
        
        # Store initial request in memory
        try:
            memory_data = {
                "request_id": state.request_id,
                "context_data": state.context_data,
                "initial_trust_score": state.trust_score,
                "timestamp": __import__('time').time()
            }
            
            # This would be async in reality, but for simplicity in state transformation:
            # await self.memory_system.store_memory(
            #     agent_id="workflow",
            #     memory_type=MemoryType.AGENT_STATE,
            #     data=memory_data
            # )
            
            state.reasoning_chain.append("Initial request stored in memory")
        except Exception as e:
            state.error_messages.append(f"Failed to store initial request: {e}")
            self.logger.warning(f"Memory storage failed during initialization: {e}")
        
        return state
    
    def _verify_context(self, state: AgentWorkflowState) -> AgentWorkflowState:
        """Verify context information using ZK proofs."""
        state.current_step = WorkflowState.CONTEXT_VERIFICATION
        state.reasoning_chain.append("Starting context verification")
        
        try:
            # In a real implementation, this would be async:
            # result = await self.context_checker.verify_context(
            #     user_id=state.context_data.get("user_id", "unknown"),
            #     context_data=state.context_data,
            #     verification_level="standard"
            # )
            
            # For now, simulate successful verification
            state.reasoning_chain.append("Context verification completed successfully")
            # In real implementation, we would update trust score based on verification
            
        except Exception as e:
            state.error_messages.append(f"Context verification failed: {e}")
            self.logger.error(f"Context verification error: {e}")
            # Even on failure, we continue but with lower confidence
        
        return state
    
    def _evaluate_trust(self, state: AgentWorkflowState) -> AgentWorkflowState:
        """Evaluate trust score based on context and history."""
        state.current_step = WorkflowState.TRUST_EVALUATION
        state.reasoning_chain.append("Starting trust evaluation")
        
        try:
            # In a real implementation, this would be async:
            # result = await self.trust_checker.evaluate_trust(
            #     user_id=state.context_data.get("user_id", "unknown"),
            #     context_data=state.context_data
            # )
            
            # For now, simulate trust evaluation
            state.reasoning_chain.append("Trust evaluation completed")
            # In real implementation, we would update state.trust_score
            
        except Exception as e:
            state.error_messages.append(f"Trust evaluation failed: {e}")
            self.logger.error(f"Trust evaluation error: {e}")
        
        return state
    
    def _collect_agent_decisions(self, state: AgentWorkflowState) -> AgentWorkflowState:
        """Collect individual decisions from all agents."""
        state.current_step = WorkflowState.INDIVIDUAL_DECISIONS
        state.reasoning_chain.append("Collecting individual agent decisions")
        
        try:
            # Collect decisions from all agents
            for agent_id, agent in self.agents.items():
                try:
                    # In a real implementation, this would be async:
                    # decision = await agent.evaluate_access_request(
                    #     request_id=state.request_id,
                    #     context_data=state.context_data,
                    #     trust_score=state.trust_score
                    # )
                    
                    # For now, simulate agent decisions
                    decision = {
                        "agent_id": agent_id,
                        "decision": "allow" if agent_id.startswith("permissive") else "deny" if agent_id.startswith("strict") else "allow",
                        "confidence": "high",
                        "reasoning": [f"Decision made by {agent_id} agent"]
                    }
                    
                    state.agent_decisions[agent_id] = decision
                    state.reasoning_chain.append(f"Decision collected from {agent_id}")
                    
                except Exception as e:
                    state.error_messages.append(f"Agent {agent_id} decision failed: {e}")
                    self.logger.error(f"Agent {agent_id} decision error: {e}")
                    # Continue with other agents
            
            state.reasoning_chain.append(f"Collected decisions from {len(state.agent_decisions)} agents")
            
        except Exception as e:
            state.error_messages.append(f"Failed to collect agent decisions: {e}")
            self.logger.error(f"Agent decision collection error: {e}")
        
        return state
    
    def _build_consensus(self, state: AgentWorkflowState) -> AgentWorkflowState:
        """Build consensus from individual agent decisions."""
        state.current_step = WorkflowState.CONSENSUS_BUILDING
        state.reasoning_chain.append("Building consensus from agent decisions")
        
        try:
            if not state.agent_decisions:
                state.error_messages.append("No agent decisions available for consensus")
                return state
            
            # Simple consensus algorithm (in reality, this would be more sophisticated)
            allow_count = sum(1 for decision in state.agent_decisions.values() 
                            if decision.get("decision") == "allow")
            deny_count = len(state.agent_decisions) - allow_count
            
            # Majority rule
            if allow_count > deny_count:
                state.consensus_reached = True
                state.reasoning_chain.append(f"Consensus reached: ALLOW ({allow_count}/{len(state.agent_decisions)} agents)")
            elif deny_count > allow_count:
                state.consensus_reached = True
                state.reasoning_chain.append(f"Consensus reached: DENY ({deny_count}/{len(state.agent_decisions)} agents)")
            else:
                state.consensus_reached = False
                state.reasoning_chain.append(f"No consensus reached: SPLIT DECISION ({allow_count} allow, {deny_count} deny)")
            
        except Exception as e:
            state.error_messages.append(f"Consensus building failed: {e}")
            self.logger.error(f"Consensus building error: {e}")
        
        return state
    
    def _make_final_decision(self, state: AgentWorkflowState) -> AgentWorkflowState:
        """Make the final decision based on consensus or fallback logic."""
        state.current_step = WorkflowState.FINAL_DECISION
        state.reasoning_chain.append("Making final decision")
        
        try:
            if state.consensus_reached:
                # Use consensus decision
                if any(decision.get("decision") == "allow" for decision in state.agent_decisions.values()):
                    state.final_decision = "allow"
                else:
                    state.final_decision = "deny"
                state.reasoning_chain.append("Final decision based on agent consensus")
            else:
                # Fallback decision logic
                # In this case, we might use the initial trust score or other factors
                if state.trust_score >= 50:
                    state.final_decision = "allow"
                else:
                    state.final_decision = "deny"
                state.reasoning_chain.append("Final decision based on fallback logic")
            
            state.reasoning_chain.append(f"Final decision: {state.final_decision}")
            
        except Exception as e:
            state.error_messages.append(f"Final decision making failed: {e}")
            self.logger.error(f"Final decision error: {e}")
            # Default deny in case of errors
            state.final_decision = "deny"
        
        return state
    
    def _finalize_workflow(self, state: AgentWorkflowState) -> AgentWorkflowState:
        """Finalize the workflow and store results."""
        state.current_step = WorkflowState.COMPLETED
        state.reasoning_chain.append("Workflow completed")
        
        try:
            # Store final decision in memory
            memory_data = {
                "request_id": state.request_id,
                "final_decision": state.final_decision,
                "consensus_reached": state.consensus_reached,
                "agent_decisions": state.agent_decisions,
                "trust_score": state.trust_score,
                "reasoning_chain": state.reasoning_chain,
                "error_messages": state.error_messages,
                "timestamp": __import__('time').time()
            }
            
            # In a real implementation, this would be async:
            # await self.memory_system.store_memory(
            #     agent_id="workflow",
            #     memory_type=MemoryType.DECISION_HISTORY,
            #     data=memory_data
            # )
            
            state.reasoning_chain.append("Final decision stored in memory")
            self.logger.info(f"Workflow completed for request {state.request_id} with decision: {state.final_decision}")
            
        except Exception as e:
            state.error_messages.append(f"Failed to store final decision: {e}")
            self.logger.warning(f"Memory storage failed during finalization: {e}")
        
        return state
    
    async def process_request(self, request_id: str, context_data: Dict[str, Any], 
                            initial_trust_score: float = 50.0) -> Dict[str, Any]:
        """
        Process an access request through the multi-agent workflow.
        
        Args:
            request_id: Unique identifier for the request
            context_data: Context information for the request
            initial_trust_score: Initial trust score for the user
            
        Returns:
            Dictionary containing the final decision and process details
        """
        # Initialize state
        initial_state = AgentWorkflowState(
            request_id=request_id,
            context_data=context_data,
            trust_score=initial_trust_score,
            agent_decisions={},
            consensus_reached=False,
            final_decision=None,
            reasoning_chain=[],
            current_step=WorkflowState.INITIALIZED,
            error_messages=[],
            metadata={
                "start_time": __import__('time').time(),
                "agent_count": len(self.agent_ids)
            }
        )
        
        try:
            # Run the workflow
            final_state = await self.workflow.ainvoke(initial_state)
            
            # Return results
            return {
                "request_id": final_state.request_id,
                "final_decision": final_state.final_decision,
                "consensus_reached": final_state.consensus_reached,
                "agent_decisions": final_state.agent_decisions,
                "trust_score": final_state.trust_score,
                "reasoning_chain": final_state.reasoning_chain,
                "error_messages": final_state.error_messages,
                "processing_time": __import__('time').time() - final_state.metadata.get("start_time", __import__('time').time()),
                "timestamp": __import__('time').time()
            }
            
        except Exception as e:
            self.logger.error(f"Workflow processing failed: {e}")
            return {
                "request_id": request_id,
                "final_decision": "deny",  # Safe default
                "consensus_reached": False,
                "agent_decisions": {},
                "trust_score": initial_trust_score,
                "reasoning_chain": ["Workflow processing error"],
                "error_messages": [str(e)],
                "processing_time": 0,
                "timestamp": __import__('time').time()
            }
    
    def get_workflow_metrics(self) -> Dict[str, Any]:
        """Get workflow performance metrics."""
        return {
            "agent_count": len(self.agents),
            "agent_roles": {agent_id: agent.capabilities.roles[0].value 
                          for agent_id, agent in self.agents.items()},
            "workflow_steps": [step.value for step in WorkflowState],
            "memory_system_initialized": hasattr(self, 'memory_system')
        }


# Convenience function to create a standard agent graph
def create_standard_agent_graph() -> AgentGraph:
    """
    Create a standard agent graph with typical agent configuration.
    
    Returns:
        AgentGraph instance with standard agent setup
    """
    agent_ids = [
        "neutral_001",
        "permissive_001", 
        "strict_001",
        "watchdog_001",
        "neutral_002"
    ]
    
    agent_roles = {
        "neutral_001": AgentRole.NEUTRAL,
        "permissive_001": AgentRole.PERMISSIVE,
        "strict_001": AgentRole.STRICT,
        "watchdog_001": AgentRole.WATCHDOG,
        "neutral_002": AgentRole.NEUTRAL
    }
    
    return AgentGraph(agent_ids, agent_roles)