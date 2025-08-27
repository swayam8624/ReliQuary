"""
Neutral Agent Node for ReliQuary Multi-Agent Consensus System

The Neutral Agent provides balanced, objective decision-making without bias toward
either permissive or restrictive access policies. It serves as a baseline evaluator
that considers all factors equally and provides consistent, rational decisions.
"""

import logging
import time
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from enum import Enum

# LangGraph and LangChain imports
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage
from langchain_core.runnables import RunnableLambda
from langgraph.graph import StateGraph, END

# ReliQuary imports
from ..agent_foundation import BaseAgent, AgentCapabilities, AgentRole
from ..consensus import DistributedConsensusManager


class DecisionConfidence(Enum):
    """Confidence levels for agent decisions"""
    VERY_LOW = "very_low"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    VERY_HIGH = "very_high"


@dataclass
class NeutralDecisionState:
    """State object for neutral agent decision process"""
    request_id: str
    context_data: Dict[str, Any]
    trust_score: float
    risk_factors: List[str]
    access_factors: List[str]
    decision_history: List[Dict[str, Any]]
    current_step: str = "initialize"
    confidence: DecisionConfidence = DecisionConfidence.MEDIUM
    reasoning: List[str] = None
    final_decision: Optional[str] = None
    
    def __post_init__(self):
        if self.reasoning is None:
            self.reasoning = []


class NeutralAgent(BaseAgent):
    """
    Neutral Agent implementation for balanced decision-making.
    
    The Neutral Agent evaluates access requests using objective criteria,
    providing balanced decisions that serve as a baseline for consensus.
    It considers both security and usability factors equally.
    """
    
    def __init__(self, agent_id: str, network_agents: List[str]):
        """
        Initialize the Neutral Agent.
        
        Args:
            agent_id: Unique identifier for this agent
            network_agents: List of all agent IDs in the network
        """
        capabilities = AgentCapabilities(
            roles=[AgentRole.VALIDATOR],
            max_concurrent_tasks=10,
            supported_verification_types=["device", "location", "timestamp", "pattern"],
            trust_scoring_enabled=True,
            consensus_participation=True,
            specializations=["neutral_evaluation", "balanced_decisions"]
        )
        
        super().__init__(agent_id, capabilities)
        
        self.network_agents = network_agents
        self.decision_weights = {
            "trust_score": 0.3,
            "context_verification": 0.25,
            "historical_behavior": 0.2,
            "risk_assessment": 0.15,
            "compliance_factors": 0.1
        }
        
        # Decision thresholds
        self.allow_threshold = 0.6
        self.deny_threshold = 0.4
        
        # Initialize LangGraph workflow
        self._build_decision_graph()
        
        self.logger = logging.getLogger(f"neutral_agent.{self.agent_id}")
    
    def _build_decision_graph(self):
        """Build the LangGraph decision workflow"""
        workflow = StateGraph(NeutralDecisionState)
        
        # Add nodes
        workflow.add_node("initialize", self._initialize_decision)
        workflow.add_node("analyze_context", self._analyze_context)
        workflow.add_node("evaluate_trust", self._evaluate_trust)
        workflow.add_node("assess_risk", self._assess_risk)
        workflow.add_node("check_compliance", self._check_compliance)
        workflow.add_node("make_decision", self._make_decision)
        workflow.add_node("finalize", self._finalize_decision)
        
        # Define the flow
        workflow.set_entry_point("initialize")
        workflow.add_edge("initialize", "analyze_context")
        workflow.add_edge("analyze_context", "evaluate_trust")
        workflow.add_edge("evaluate_trust", "assess_risk")
        workflow.add_edge("assess_risk", "check_compliance")
        workflow.add_edge("check_compliance", "make_decision")
        workflow.add_edge("make_decision", "finalize")
        workflow.add_edge("finalize", END)
        
        self.decision_graph = workflow.compile()
    
    async def evaluate_access_request(self, 
                                    request_id: str,
                                    context_data: Dict[str, Any],
                                    trust_score: float,
                                    history: List[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Evaluate an access request using the neutral agent logic.
        
        Args:
            request_id: Unique identifier for the request
            context_data: Context information for the request
            trust_score: Current trust score for the user
            history: Historical decision data
            
        Returns:
            Dictionary containing the decision and reasoning
        """
        # Initialize state
        initial_state = NeutralDecisionState(
            request_id=request_id,
            context_data=context_data,
            trust_score=trust_score,
            risk_factors=[],
            access_factors=[],
            decision_history=history or []
        )
        
        try:
            # Run the decision graph
            result = await self.decision_graph.ainvoke(initial_state)
            
            # Update metrics
            self.metrics.total_tasks_processed += 1
            if result.final_decision == "allow":
                self.metrics.successful_verifications += 1
            
            return {
                "agent_id": self.agent_id,
                "decision": result.final_decision,
                "confidence": result.confidence.value,
                "trust_score": result.trust_score,
                "reasoning": result.reasoning,
                "risk_factors": result.risk_factors,
                "access_factors": result.access_factors,
                "timestamp": time.time()
            }
            
        except Exception as e:
            self.logger.error(f"Decision evaluation failed: {e}")
            self.metrics.failed_verifications += 1
            return {
                "agent_id": self.agent_id,
                "decision": "deny",
                "confidence": "very_low",
                "reasoning": [f"Evaluation error: {str(e)}"],
                "timestamp": time.time()
            }
    
    def _initialize_decision(self, state: NeutralDecisionState) -> NeutralDecisionState:
        """Initialize the decision process"""
        state.current_step = "initialize"
        state.reasoning.append("Starting neutral agent evaluation")
        
        # Basic validation
        if not state.context_data:
            state.reasoning.append("Warning: No context data provided")
            state.confidence = DecisionConfidence.LOW
        
        return state
    
    def _analyze_context(self, state: NeutralDecisionState) -> NeutralDecisionState:
        """Analyze context verification data"""
        state.current_step = "analyze_context"
        
        context = state.context_data
        score = 0
        max_score = 0
        
        # Device verification
        if "device_verified" in context:
            max_score += 25
            if context["device_verified"]:
                score += 25
                state.access_factors.append("Device verified")
            else:
                state.risk_factors.append("Device not verified")
        
        # Location verification
        if "location_verified" in context:
            max_score += 20
            if context["location_verified"]:
                score += 20
                state.access_factors.append("Location verified")
            else:
                state.risk_factors.append("Location suspicious")
        
        # Timestamp verification
        if "timestamp_verified" in context:
            max_score += 15
            if context["timestamp_verified"]:
                score += 15
                state.access_factors.append("Timestamp valid")
            else:
                state.risk_factors.append("Timestamp invalid")
        
        # Pattern verification
        if "pattern_verified" in context:
            max_score += 15
            if context["pattern_verified"]:
                score += 15
                state.access_factors.append("Behavioral pattern normal")
            else:
                state.risk_factors.append("Unusual behavioral pattern")
        
        # Calculate context score
        context_score = (score / max_score) if max_score > 0 else 0.5
        state.reasoning.append(f"Context verification score: {context_score:.2f}")
        
        return state
    
    def _evaluate_trust(self, state: NeutralDecisionState) -> NeutralDecisionState:
        """Evaluate trust score factors"""
        state.current_step = "evaluate_trust"
        
        trust_score = state.trust_score
        
        if trust_score >= 80:
            state.access_factors.append("High trust score")
            state.confidence = DecisionConfidence.HIGH
        elif trust_score >= 60:
            state.access_factors.append("Good trust score")
            state.confidence = DecisionConfidence.MEDIUM
        elif trust_score >= 40:
            state.risk_factors.append("Moderate trust score")
            state.confidence = DecisionConfidence.LOW
        else:
            state.risk_factors.append("Low trust score")
            state.confidence = DecisionConfidence.VERY_LOW
        
        state.reasoning.append(f"Trust score evaluation: {trust_score}")
        
        return state
    
    def _assess_risk(self, state: NeutralDecisionState) -> NeutralDecisionState:
        """Assess risk factors from context and history"""
        state.current_step = "assess_risk"
        
        context = state.context_data
        risk_score = 0
        
        # Check for anomalies
        if context.get("access_frequency", 1) > 10:
            risk_score += 20
            state.risk_factors.append("High access frequency")
        
        if context.get("session_duration", 1800) < 60:
            risk_score += 15
            state.risk_factors.append("Very short session duration")
        
        if context.get("keystrokes_per_minute", 60) > 200:
            risk_score += 25
            state.risk_factors.append("Unrealistic typing speed")
        
        # Historical risk factors
        recent_failures = sum(1 for decision in state.decision_history[-10:] 
                            if decision.get("decision") == "deny")
        if recent_failures > 3:
            risk_score += 30
            state.risk_factors.append("Recent access denials")
        
        state.reasoning.append(f"Risk assessment score: {risk_score}")
        
        return state
    
    def _check_compliance(self, state: NeutralDecisionState) -> NeutralDecisionState:
        """Check compliance and policy factors"""
        state.current_step = "check_compliance"
        
        context = state.context_data
        
        # Business hours check
        current_hour = int(time.time() % 86400 / 3600)
        if 9 <= current_hour <= 17:  # Business hours
            state.access_factors.append("Access during business hours")
        else:
            state.risk_factors.append("Access outside business hours")
        
        # Multi-factor authentication
        if context.get("mfa_verified", False):
            state.access_factors.append("Multi-factor authentication verified")
        else:
            state.risk_factors.append("No multi-factor authentication")
        
        state.reasoning.append("Compliance factors evaluated")
        
        return state
    
    def _make_decision(self, state: NeutralDecisionState) -> NeutralDecisionState:
        """Make the final access decision"""
        state.current_step = "make_decision"
        
        # Calculate decision score
        access_score = len(state.access_factors) * 0.1
        risk_penalty = len(state.risk_factors) * 0.08
        trust_factor = state.trust_score / 100
        
        final_score = trust_factor + access_score - risk_penalty
        
        # Make decision based on thresholds
        if final_score >= self.allow_threshold:
            state.final_decision = "allow"
            state.reasoning.append(f"Decision: ALLOW (score: {final_score:.2f})")
        elif final_score <= self.deny_threshold:
            state.final_decision = "deny"
            state.reasoning.append(f"Decision: DENY (score: {final_score:.2f})")
        else:
            # Neutral zone - err on side of security
            state.final_decision = "deny"
            state.reasoning.append(f"Decision: DENY (neutral zone, score: {final_score:.2f})")
        
        return state
    
    def _finalize_decision(self, state: NeutralDecisionState) -> NeutralDecisionState:
        """Finalize the decision and add summary"""
        state.current_step = "finalize"
        
        # Add decision summary
        state.reasoning.append(f"Final decision: {state.final_decision.upper()}")
        state.reasoning.append(f"Confidence level: {state.confidence.value}")
        state.reasoning.append(f"Access factors: {len(state.access_factors)}")
        state.reasoning.append(f"Risk factors: {len(state.risk_factors)}")
        
        self.logger.info(f"Neutral agent decision for {state.request_id}: {state.final_decision}")
        
        return state
    
    def get_agent_status(self) -> Dict[str, Any]:
        """Get current agent status and configuration"""
        base_status = super().get_agent_status()
        base_status.update({
            "agent_type": "neutral",
            "decision_weights": self.decision_weights,
            "allow_threshold": self.allow_threshold,
            "deny_threshold": self.deny_threshold,
            "network_agents": len(self.network_agents)
        })
        return base_status