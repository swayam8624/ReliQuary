"""
Permissive Agent Node for ReliQuary Multi-Agent Consensus System

The Permissive Agent favors granting access while maintaining security standards.
It represents a user-friendly perspective that emphasizes usability and accessibility
while still respecting critical security boundaries.
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
from .neutral_agent import DecisionConfidence, NeutralDecisionState


@dataclass
class PermissiveDecisionState(NeutralDecisionState):
    """State object for permissive agent decision process"""
    usability_factors: List[str] = None
    user_experience_score: float = 0.0
    flexibility_applied: List[str] = None
    
    def __post_init__(self):
        super().__post_init__()
        if self.usability_factors is None:
            self.usability_factors = []
        if self.flexibility_applied is None:
            self.flexibility_applied = []


class PermissiveAgent(BaseAgent):
    """
    Permissive Agent implementation for user-friendly decision-making.
    
    The Permissive Agent evaluates access requests with a bias toward granting
    access, emphasizing user experience and productivity while maintaining
    essential security safeguards.
    """
    
    def __init__(self, agent_id: str, network_agents: List[str]):
        """
        Initialize the Permissive Agent.
        
        Args:
            agent_id: Unique identifier for this agent
            network_agents: List of all agent IDs in the network
        """
        capabilities = AgentCapabilities(
            roles=[AgentRole.COORDINATOR],
            max_concurrent_tasks=15,  # Higher capacity for user-friendly service
            supported_verification_types=["device", "location", "timestamp", "pattern"],
            trust_scoring_enabled=True,
            consensus_participation=True,
            specializations=["user_experience", "permissive_evaluation"]
        )
        
        super().__init__(agent_id, capabilities)
        
        self.network_agents = network_agents
        
        # Permissive-oriented decision weights (favor access)
        self.decision_weights = {
            "trust_score": 0.25,
            "context_verification": 0.2,
            "historical_behavior": 0.25,  # Higher weight on good history
            "user_experience": 0.2,      # Unique to permissive agent
            "risk_assessment": 0.1       # Lower weight on risk
        }
        
        # More lenient thresholds
        self.allow_threshold = 0.4   # Lower threshold for allowing
        self.deny_threshold = 0.2    # Much lower threshold for denying
        self.critical_risk_threshold = 0.8  # Only deny if risk is very high
        
        # Initialize LangGraph workflow
        self._build_decision_graph()
        
        self.logger = logging.getLogger(f"permissive_agent.{self.agent_id}")
    
    def _build_decision_graph(self):
        """Build the LangGraph decision workflow for permissive agent"""
        workflow = StateGraph(PermissiveDecisionState)
        
        # Add nodes
        workflow.add_node("initialize", self._initialize_decision)
        workflow.add_node("analyze_context", self._analyze_context)
        workflow.add_node("evaluate_trust", self._evaluate_trust)
        workflow.add_node("assess_usability", self._assess_usability)
        workflow.add_node("apply_flexibility", self._apply_flexibility)
        workflow.add_node("check_critical_risks", self._check_critical_risks)
        workflow.add_node("make_decision", self._make_decision)
        workflow.add_node("finalize", self._finalize_decision)
        
        # Define the flow
        workflow.set_entry_point("initialize")
        workflow.add_edge("initialize", "analyze_context")
        workflow.add_edge("analyze_context", "evaluate_trust")
        workflow.add_edge("evaluate_trust", "assess_usability")
        workflow.add_edge("assess_usability", "apply_flexibility")
        workflow.add_edge("apply_flexibility", "check_critical_risks")
        workflow.add_edge("check_critical_risks", "make_decision")
        workflow.add_edge("make_decision", "finalize")
        workflow.add_edge("finalize", END)
        
        self.decision_graph = workflow.compile()
    
    async def evaluate_access_request(self, 
                                    request_id: str,
                                    context_data: Dict[str, Any],
                                    trust_score: float,
                                    history: List[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Evaluate an access request using the permissive agent logic.
        
        Args:
            request_id: Unique identifier for the request
            context_data: Context information for the request
            trust_score: Current trust score for the user
            history: Historical decision data
            
        Returns:
            Dictionary containing the decision and reasoning
        """
        # Initialize state
        initial_state = PermissiveDecisionState(
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
                "usability_factors": result.usability_factors,
                "flexibility_applied": result.flexibility_applied,
                "user_experience_score": result.user_experience_score,
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
    
    def _initialize_decision(self, state: PermissiveDecisionState) -> PermissiveDecisionState:
        """Initialize the decision process with permissive mindset"""
        state.current_step = "initialize"
        state.reasoning.append("Starting permissive agent evaluation")
        state.reasoning.append("Approach: Favor access while maintaining security")
        
        # Start with higher confidence for permissive approach
        state.confidence = DecisionConfidence.MEDIUM
        
        return state
    
    def _analyze_context(self, state: PermissiveDecisionState) -> PermissiveDecisionState:
        """Analyze context with permissive interpretation"""
        state.current_step = "analyze_context"
        
        context = state.context_data
        verified_factors = 0
        total_factors = 0
        
        # Device verification (more lenient interpretation)
        if "device_verified" in context:
            total_factors += 1
            if context["device_verified"]:
                verified_factors += 1
                state.access_factors.append("Device verified")
            else:
                # Permissive: Don't treat as major risk if only device fails
                state.reasoning.append("Device not verified, but not critical")
        
        # Location verification (flexible)
        if "location_verified" in context:
            total_factors += 1
            if context["location_verified"]:
                verified_factors += 1
                state.access_factors.append("Location verified")
            else:
                # Check if location is just new, not necessarily suspicious
                state.usability_factors.append("New location - user mobility")
        
        # Timestamp verification (lenient)
        if "timestamp_verified" in context:
            total_factors += 1
            if context["timestamp_verified"]:
                verified_factors += 1
                state.access_factors.append("Timestamp valid")
            else:
                # Permissive: Minor timestamp issues shouldn't block access
                state.usability_factors.append("Minor timestamp variance")
        
        # Pattern verification (understanding)
        if "pattern_verified" in context:
            total_factors += 1
            if context["pattern_verified"]:
                verified_factors += 1
                state.access_factors.append("Behavioral pattern normal")
            else:
                # Permissive: Patterns can change legitimately
                state.usability_factors.append("Pattern variation - user adaptation")
        
        # Calculate context score with permissive bias
        context_score = (verified_factors / total_factors) if total_factors > 0 else 0.7
        # Boost score slightly for permissive approach
        context_score = min(1.0, context_score + 0.1)
        
        state.reasoning.append(f"Context verification score: {context_score:.2f} (permissive adjustment)")
        
        return state
    
    def _evaluate_trust(self, state: PermissiveDecisionState) -> PermissiveDecisionState:
        """Evaluate trust score with optimistic interpretation"""
        state.current_step = "evaluate_trust"
        
        trust_score = state.trust_score
        
        if trust_score >= 70:  # Lower threshold than neutral
            state.access_factors.append("Good trust score")
            state.confidence = DecisionConfidence.HIGH
        elif trust_score >= 50:  # More lenient
            state.access_factors.append("Acceptable trust score")
            state.confidence = DecisionConfidence.MEDIUM
        elif trust_score >= 30:  # Give benefit of doubt
            state.usability_factors.append("Building trust score")
            state.confidence = DecisionConfidence.MEDIUM
        else:
            state.risk_factors.append("Low trust score needs attention")
            state.confidence = DecisionConfidence.LOW
        
        state.reasoning.append(f"Trust score evaluation: {trust_score} (permissive interpretation)")
        
        return state
    
    def _assess_usability(self, state: PermissiveDecisionState) -> PermissiveDecisionState:
        """Assess user experience and usability factors"""
        state.current_step = "assess_usability"
        
        context = state.context_data
        ux_score = 0
        
        # Check for productivity indicators
        session_duration = context.get("session_duration", 1800)
        if session_duration > 300:  # Active session
            ux_score += 20
            state.usability_factors.append("Active work session")
        
        # Reasonable access frequency
        access_freq = context.get("access_frequency", 1)
        if 1 <= access_freq <= 5:  # Normal frequency
            ux_score += 15
            state.usability_factors.append("Normal access frequency")
        
        # Typing patterns (human-like)
        kpm = context.get("keystrokes_per_minute", 60)
        if 20 <= kpm <= 150:  # Human typing range
            ux_score += 15
            state.usability_factors.append("Human-like interaction")
        
        # Time of access (work hours boost)
        current_hour = int(time.time() % 86400 / 3600)
        if 8 <= current_hour <= 18:  # Extended work hours
            ux_score += 10
            state.usability_factors.append("Work hours access")
        
        # Historical success rate
        if state.decision_history:
            recent_success = sum(1 for d in state.decision_history[-5:] 
                               if d.get("decision") == "allow")
            if recent_success >= 3:
                ux_score += 20
                state.usability_factors.append("Good access history")
        
        state.user_experience_score = ux_score
        state.reasoning.append(f"User experience score: {ux_score}")
        
        return state
    
    def _apply_flexibility(self, state: PermissiveDecisionState) -> PermissiveDecisionState:
        """Apply permissive flexibility rules"""
        state.current_step = "apply_flexibility"
        
        # Apply flexibility based on context
        if len(state.access_factors) >= 2:
            state.flexibility_applied.append("Multiple verification factors passed")
        
        if state.trust_score >= 40:
            state.flexibility_applied.append("Minimum trust threshold met")
        
        if state.user_experience_score >= 40:
            state.flexibility_applied.append("Good user experience indicators")
        
        # Historical behavior flexibility
        if state.decision_history:
            recent_denials = sum(1 for d in state.decision_history[-3:] 
                               if d.get("decision") == "deny")
            if recent_denials == 0:
                state.flexibility_applied.append("No recent access issues")
        
        # Emergency access considerations (simplified)
        if "emergency" in str(state.context_data).lower():
            state.flexibility_applied.append("Emergency access consideration")
            state.usability_factors.append("Emergency context detected")
        
        state.reasoning.append(f"Flexibility rules applied: {len(state.flexibility_applied)}")
        
        return state
    
    def _check_critical_risks(self, state: PermissiveDecisionState) -> PermissiveDecisionState:
        """Check for critical risks that would override permissive approach"""
        state.current_step = "check_critical_risks"
        
        critical_risks = []
        
        # Check for definitive security violations
        if state.trust_score < 20:
            critical_risks.append("Extremely low trust score")
        
        # Multiple verification failures
        context = state.context_data
        verification_failures = 0
        for check in ["device_verified", "location_verified", "timestamp_verified", "pattern_verified"]:
            if check in context and not context[check]:
                verification_failures += 1
        
        if verification_failures >= 3:
            critical_risks.append("Multiple verification failures")
        
        # Suspicious activity patterns
        if context.get("access_frequency", 1) > 20:
            critical_risks.append("Excessive access frequency")
        
        if context.get("keystrokes_per_minute", 60) > 300:
            critical_risks.append("Non-human interaction pattern")
        
        # Historical red flags
        if state.decision_history:
            recent_denials = sum(1 for d in state.decision_history[-5:] 
                               if d.get("decision") == "deny")
            if recent_denials >= 4:
                critical_risks.append("Pattern of access denials")
        
        if critical_risks:
            state.risk_factors.extend(critical_risks)
            state.reasoning.append(f"Critical risks identified: {len(critical_risks)}")
        else:
            state.reasoning.append("No critical risks identified")
        
        return state
    
    def _make_decision(self, state: PermissiveDecisionState) -> PermissiveDecisionState:
        """Make the final access decision with permissive bias"""
        state.current_step = "make_decision"
        
        # Calculate decision score with permissive weights
        trust_factor = state.trust_score / 100
        access_bonus = len(state.access_factors) * 0.15  # Higher bonus
        usability_bonus = state.user_experience_score / 100 * 0.2
        flexibility_bonus = len(state.flexibility_applied) * 0.1
        risk_penalty = len(state.risk_factors) * 0.05  # Lower penalty
        
        final_score = trust_factor + access_bonus + usability_bonus + flexibility_bonus - risk_penalty
        
        # Check for critical risk override
        critical_risk_count = sum(1 for risk in state.risk_factors 
                                if "critical" in risk.lower() or "extreme" in risk.lower())
        
        if critical_risk_count > 0 and final_score < self.critical_risk_threshold:
            state.final_decision = "deny"
            state.reasoning.append(f"Decision: DENY due to critical risks (score: {final_score:.2f})")
        elif final_score >= self.allow_threshold:
            state.final_decision = "allow"
            state.reasoning.append(f"Decision: ALLOW (score: {final_score:.2f})")
        elif final_score > self.deny_threshold:
            # Permissive: When in doubt, allow with conditions
            state.final_decision = "allow"
            state.reasoning.append(f"Decision: ALLOW with monitoring (score: {final_score:.2f})")
            state.usability_factors.append("Granted with enhanced monitoring")
        else:
            state.final_decision = "deny"
            state.reasoning.append(f"Decision: DENY (score too low: {final_score:.2f})")
        
        return state
    
    def _finalize_decision(self, state: PermissiveDecisionState) -> PermissiveDecisionState:
        """Finalize the decision with permissive summary"""
        state.current_step = "finalize"
        
        # Add decision summary
        state.reasoning.append(f"Final decision: {state.final_decision.upper()}")
        state.reasoning.append(f"Confidence level: {state.confidence.value}")
        state.reasoning.append(f"Access factors: {len(state.access_factors)}")
        state.reasoning.append(f"Usability factors: {len(state.usability_factors)}")
        state.reasoning.append(f"Flexibility applied: {len(state.flexibility_applied)}")
        state.reasoning.append(f"Risk factors: {len(state.risk_factors)}")
        state.reasoning.append(f"User experience score: {state.user_experience_score}")
        
        self.logger.info(f"Permissive agent decision for {state.request_id}: {state.final_decision}")
        
        return state
    
    def get_agent_status(self) -> Dict[str, Any]:
        """Get current agent status and configuration"""
        base_status = super().get_agent_status()
        base_status.update({
            "agent_type": "permissive",
            "decision_weights": self.decision_weights,
            "allow_threshold": self.allow_threshold,
            "deny_threshold": self.deny_threshold,
            "critical_risk_threshold": self.critical_risk_threshold,
            "network_agents": len(self.network_agents),
            "approach": "user_friendly_with_security"
        })
        return base_status