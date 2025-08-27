"""
Strict Agent Node for ReliQuary Multi-Agent Consensus System

The Strict Agent emphasizes security above convenience, applying stringent
security policies and requiring high confidence levels before granting access.
It represents a security-first perspective that prioritizes protection over usability.
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
class StrictDecisionState(NeutralDecisionState):
    """State object for strict agent decision process"""
    security_violations: List[str] = None
    compliance_checks: List[str] = None
    threat_indicators: List[str] = None
    security_score: float = 0.0
    mandatory_requirements: List[str] = None
    
    def __post_init__(self):
        super().__post_init__()
        if self.security_violations is None:
            self.security_violations = []
        if self.compliance_checks is None:
            self.compliance_checks = []
        if self.threat_indicators is None:
            self.threat_indicators = []
        if self.mandatory_requirements is None:
            self.mandatory_requirements = []


class StrictAgent(BaseAgent):
    """
    Strict Agent implementation for security-focused decision-making.
    
    The Strict Agent evaluates access requests with a strong bias toward
    security, requiring multiple verification factors and high trust scores
    before granting access.
    """
    
    def __init__(self, agent_id: str, network_agents: List[str]):
        """
        Initialize the Strict Agent.
        
        Args:
            agent_id: Unique identifier for this agent
            network_agents: List of all agent IDs in the network
        """
        capabilities = AgentCapabilities(
            roles=[AgentRole.MONITOR],
            max_concurrent_tasks=8,  # Lower capacity for thorough analysis
            supported_verification_types=["device", "location", "timestamp", "pattern", "mfa"],
            trust_scoring_enabled=True,
            consensus_participation=True,
            specializations=["security_enforcement", "strict_evaluation"]
        )
        
        super().__init__(agent_id, capabilities)
        
        self.network_agents = network_agents
        
        # Security-oriented decision weights
        self.decision_weights = {
            "trust_score": 0.35,           # Higher weight on trust
            "context_verification": 0.3,   # Strong emphasis on verification
            "security_compliance": 0.2,    # Unique to strict agent
            "threat_assessment": 0.1,      # Threat detection
            "historical_behavior": 0.05    # Lower weight on history
        }
        
        # Strict thresholds
        self.allow_threshold = 0.8     # High threshold for allowing
        self.deny_threshold = 0.6      # High threshold for denying
        self.minimum_trust_score = 60  # Minimum trust required
        self.required_verifications = 3 # Minimum verifications needed
        
        # Initialize LangGraph workflow
        self._build_decision_graph()
        
        self.logger = logging.getLogger(f"strict_agent.{self.agent_id}")
    
    def _build_decision_graph(self):
        """Build the LangGraph decision workflow for strict agent"""
        workflow = StateGraph(StrictDecisionState)
        
        # Add nodes
        workflow.add_node("initialize", self._initialize_decision)
        workflow.add_node("verify_requirements", self._verify_requirements)
        workflow.add_node("analyze_context", self._analyze_context)
        workflow.add_node("evaluate_trust", self._evaluate_trust)
        workflow.add_node("assess_threats", self._assess_threats)
        workflow.add_node("check_compliance", self._check_compliance)
        workflow.add_node("security_audit", self._security_audit)
        workflow.add_node("make_decision", self._make_decision)
        workflow.add_node("finalize", self._finalize_decision)
        
        # Define the flow
        workflow.set_entry_point("initialize")
        workflow.add_edge("initialize", "verify_requirements")
        workflow.add_edge("verify_requirements", "analyze_context")
        workflow.add_edge("analyze_context", "evaluate_trust")
        workflow.add_edge("evaluate_trust", "assess_threats")
        workflow.add_edge("assess_threats", "check_compliance")
        workflow.add_edge("check_compliance", "security_audit")
        workflow.add_edge("security_audit", "make_decision")
        workflow.add_edge("make_decision", "finalize")
        workflow.add_edge("finalize", END)
        
        self.decision_graph = workflow.compile()
    
    async def evaluate_access_request(self, 
                                    request_id: str,
                                    context_data: Dict[str, Any],
                                    trust_score: float,
                                    history: List[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Evaluate an access request using the strict agent logic.
        
        Args:
            request_id: Unique identifier for the request
            context_data: Context information for the request
            trust_score: Current trust score for the user
            history: Historical decision data
            
        Returns:
            Dictionary containing the decision and reasoning
        """
        # Initialize state
        initial_state = StrictDecisionState(
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
                "security_violations": result.security_violations,
                "compliance_checks": result.compliance_checks,
                "threat_indicators": result.threat_indicators,
                "security_score": result.security_score,
                "mandatory_requirements": result.mandatory_requirements,
                "timestamp": time.time()
            }
            
        except Exception as e:
            self.logger.error(f"Decision evaluation failed: {e}")
            self.metrics.failed_verifications += 1
            return {
                "agent_id": self.agent_id,
                "decision": "deny",
                "confidence": "very_high",  # High confidence in denying on error
                "reasoning": [f"Evaluation error - security protocol engaged: {str(e)}"],
                "timestamp": time.time()
            }
    
    def _initialize_decision(self, state: StrictDecisionState) -> StrictDecisionState:
        """Initialize the decision process with strict security mindset"""
        state.current_step = "initialize"
        state.reasoning.append("Starting strict agent evaluation")
        state.reasoning.append("Approach: Security-first with stringent requirements")
        
        # Start with low confidence - must prove worthiness
        state.confidence = DecisionConfidence.LOW
        
        # Define mandatory requirements
        state.mandatory_requirements = [
            "Trust score >= 60",
            "At least 3 verification factors",
            "No critical security violations",
            "Compliance with security policies"
        ]
        
        return state
    
    def _verify_requirements(self, state: StrictDecisionState) -> StrictDecisionState:
        """Verify mandatory security requirements"""
        state.current_step = "verify_requirements"
        
        # Check minimum trust score
        if state.trust_score < self.minimum_trust_score:
            state.security_violations.append(f"Trust score {state.trust_score} below minimum {self.minimum_trust_score}")
        else:
            state.compliance_checks.append("Minimum trust score met")
        
        # Count verification factors
        context = state.context_data
        verified_count = 0
        total_checks = 0
        
        for check in ["device_verified", "location_verified", "timestamp_verified", "pattern_verified"]:
            if check in context:
                total_checks += 1
                if context[check]:
                    verified_count += 1
        
        if verified_count < self.required_verifications:
            state.security_violations.append(f"Only {verified_count}/{total_checks} verifications passed, minimum {self.required_verifications} required")
        else:
            state.compliance_checks.append(f"Sufficient verifications: {verified_count}/{total_checks}")
        
        # Check for required context data
        required_fields = ["device_verified", "timestamp_verified"]
        for field in required_fields:
            if field not in context:
                state.security_violations.append(f"Missing required field: {field}")
        
        state.reasoning.append(f"Mandatory requirements check: {len(state.security_violations)} violations found")
        
        return state
    
    def _analyze_context(self, state: StrictDecisionState) -> StrictDecisionState:
        """Analyze context with strict security interpretation"""
        state.current_step = "analyze_context"
        
        context = state.context_data
        security_score = 0
        max_security_score = 0
        
        # Device verification (critical requirement)
        if "device_verified" in context:
            max_security_score += 30
            if context["device_verified"]:
                security_score += 30
                state.access_factors.append("Device verified")
            else:
                state.security_violations.append("Device verification failed")
        
        # Location verification (high importance)
        if "location_verified" in context:
            max_security_score += 25
            if context["location_verified"]:
                security_score += 25
                state.access_factors.append("Location verified")
            else:
                state.threat_indicators.append("Unverified location access attempt")
        
        # Timestamp verification (medium importance)
        if "timestamp_verified" in context:
            max_security_score += 20
            if context["timestamp_verified"]:
                security_score += 20
                state.access_factors.append("Timestamp valid")
            else:
                state.security_violations.append("Invalid timestamp")
        
        # Pattern verification (behavioral analysis)
        if "pattern_verified" in context:
            max_security_score += 15
            if context["pattern_verified"]:
                security_score += 15
                state.access_factors.append("Behavioral pattern verified")
            else:
                state.threat_indicators.append("Anomalous behavioral pattern")
        
        # Multi-factor authentication (critical)
        if "mfa_verified" in context:
            max_security_score += 25
            if context["mfa_verified"]:
                security_score += 25
                state.access_factors.append("Multi-factor authentication verified")
            else:
                state.security_violations.append("Multi-factor authentication required")
        
        # Calculate security score
        state.security_score = (security_score / max_security_score) if max_security_score > 0 else 0
        state.reasoning.append(f"Security verification score: {state.security_score:.2f}")
        
        return state
    
    def _evaluate_trust(self, state: StrictDecisionState) -> StrictDecisionState:
        """Evaluate trust score with strict standards"""
        state.current_step = "evaluate_trust"
        
        trust_score = state.trust_score
        
        if trust_score >= 90:
            state.access_factors.append("Excellent trust score")
            state.confidence = DecisionConfidence.HIGH
        elif trust_score >= 80:
            state.access_factors.append("Good trust score")
            state.confidence = DecisionConfidence.MEDIUM
        elif trust_score >= 60:
            state.compliance_checks.append("Minimum trust score met")
            state.confidence = DecisionConfidence.LOW
        else:
            state.security_violations.append("Trust score below security threshold")
            state.confidence = DecisionConfidence.VERY_LOW
        
        # Check trust score stability
        if state.decision_history:
            recent_scores = [d.get("trust_score", 0) for d in state.decision_history[-5:]]
            if recent_scores:
                score_variance = max(recent_scores) - min(recent_scores)
                if score_variance > 20:
                    state.threat_indicators.append("High trust score variance")
                else:
                    state.compliance_checks.append("Stable trust score")
        
        state.reasoning.append(f"Trust evaluation: {trust_score} (strict standards applied)")
        
        return state
    
    def _assess_threats(self, state: StrictDecisionState) -> StrictDecisionState:
        """Assess potential security threats"""
        state.current_step = "assess_threats"
        
        context = state.context_data
        
        # Check for automated/bot-like behavior
        kpm = context.get("keystrokes_per_minute", 60)
        if kpm > 200 or kpm < 10:
            state.threat_indicators.append("Non-human typing pattern detected")
        
        # Check access frequency
        access_freq = context.get("access_frequency", 1)
        if access_freq > 15:
            state.threat_indicators.append("Excessive access frequency")
        elif access_freq > 8:
            state.risk_factors.append("High access frequency")
        
        # Check session duration
        session_duration = context.get("session_duration", 1800)
        if session_duration < 30:
            state.threat_indicators.append("Suspiciously short session")
        elif session_duration > 14400:  # 4 hours
            state.risk_factors.append("Unusually long session")
        
        # Check for off-hours access
        current_hour = int(time.time() % 86400 / 3600)
        if current_hour < 6 or current_hour > 22:
            state.threat_indicators.append("Off-hours access attempt")
        
        # Analyze historical patterns
        if state.decision_history:
            recent_denials = sum(1 for d in state.decision_history[-10:] 
                               if d.get("decision") == "deny")
            if recent_denials >= 5:
                state.threat_indicators.append("Pattern of recent access denials")
            elif recent_denials >= 3:
                state.risk_factors.append("Multiple recent access denials")
        
        state.reasoning.append(f"Threat assessment: {len(state.threat_indicators)} threats, {len(state.risk_factors)} risks")
        
        return state
    
    def _check_compliance(self, state: StrictDecisionState) -> StrictDecisionState:
        """Check security policy compliance"""
        state.current_step = "check_compliance"
        
        context = state.context_data
        
        # Business hours compliance
        current_hour = int(time.time() % 86400 / 3600)
        if 9 <= current_hour <= 17:
            state.compliance_checks.append("Access during business hours")
        else:
            state.risk_factors.append("Access outside standard business hours")
        
        # Geographic compliance (simplified)
        if context.get("location_verified", False):
            state.compliance_checks.append("Geographic compliance verified")
        else:
            state.security_violations.append("Geographic compliance not verified")
        
        # Device compliance
        if context.get("device_verified", False):
            state.compliance_checks.append("Device compliance verified")
        else:
            state.security_violations.append("Device compliance failed")
        
        # Data classification (if available)
        data_classification = context.get("data_classification", "unknown")
        if data_classification == "confidential" or data_classification == "secret":
            # Higher security requirements for sensitive data
            if state.trust_score < 80:
                state.security_violations.append("Insufficient trust for sensitive data access")
            if len(state.access_factors) < 4:
                state.security_violations.append("Insufficient verification for sensitive data")
        
        state.reasoning.append(f"Compliance check: {len(state.compliance_checks)} passed, {len(state.security_violations)} violations")
        
        return state
    
    def _security_audit(self, state: StrictDecisionState) -> StrictDecisionState:
        """Perform final security audit"""
        state.current_step = "security_audit"
        
        # Calculate overall security posture
        total_security_factors = (
            len(state.access_factors) + 
            len(state.compliance_checks)
        )
        
        total_security_risks = (
            len(state.security_violations) * 3 +  # Violations are critical
            len(state.threat_indicators) * 2 +   # Threats are serious
            len(state.risk_factors)              # Risks are moderate
        )
        
        security_ratio = total_security_factors / max(total_security_risks, 1)
        
        if security_ratio >= 2.0:
            state.reasoning.append("Security audit: STRONG security posture")
            state.confidence = DecisionConfidence.HIGH
        elif security_ratio >= 1.5:
            state.reasoning.append("Security audit: GOOD security posture")
            state.confidence = DecisionConfidence.MEDIUM
        elif security_ratio >= 1.0:
            state.reasoning.append("Security audit: ACCEPTABLE security posture")
            state.confidence = DecisionConfidence.LOW
        else:
            state.reasoning.append("Security audit: POOR security posture")
            state.confidence = DecisionConfidence.VERY_LOW
        
        # Final security score calculation
        base_score = state.security_score
        compliance_bonus = len(state.compliance_checks) * 0.05
        violation_penalty = len(state.security_violations) * 0.2
        threat_penalty = len(state.threat_indicators) * 0.15
        
        final_security_score = max(0, base_score + compliance_bonus - violation_penalty - threat_penalty)
        state.security_score = final_security_score
        
        state.reasoning.append(f"Final security score: {final_security_score:.2f}")
        
        return state
    
    def _make_decision(self, state: StrictDecisionState) -> StrictDecisionState:
        """Make the final access decision with strict security requirements"""
        state.current_step = "make_decision"
        
        # Immediate denial conditions
        if state.security_violations:
            state.final_decision = "deny"
            state.reasoning.append(f"Decision: DENY due to {len(state.security_violations)} security violations")
            return state
        
        if len(state.threat_indicators) >= 2:
            state.final_decision = "deny"
            state.reasoning.append(f"Decision: DENY due to multiple threat indicators")
            return state
        
        if state.trust_score < self.minimum_trust_score:
            state.final_decision = "deny"
            state.reasoning.append(f"Decision: DENY due to insufficient trust score")
            return state
        
        # Calculate weighted decision score
        trust_factor = state.trust_score / 100
        security_factor = state.security_score
        compliance_factor = len(state.compliance_checks) / max(len(state.mandatory_requirements), 1)
        access_factor = len(state.access_factors) * 0.1
        risk_penalty = (len(state.risk_factors) + len(state.threat_indicators)) * 0.1
        
        final_score = (
            trust_factor * self.decision_weights["trust_score"] +
            security_factor * self.decision_weights["context_verification"] +
            compliance_factor * self.decision_weights["security_compliance"] +
            access_factor - risk_penalty
        )
        
        # Apply strict thresholds
        if final_score >= self.allow_threshold:
            state.final_decision = "allow"
            state.reasoning.append(f"Decision: ALLOW (strict criteria met, score: {final_score:.2f})")
        else:
            state.final_decision = "deny"
            state.reasoning.append(f"Decision: DENY (strict criteria not met, score: {final_score:.2f})")
        
        return state
    
    def _finalize_decision(self, state: StrictDecisionState) -> StrictDecisionState:
        """Finalize the decision with strict security summary"""
        state.current_step = "finalize"
        
        # Add comprehensive decision summary
        state.reasoning.append(f"Final decision: {state.final_decision.upper()}")
        state.reasoning.append(f"Confidence level: {state.confidence.value}")
        state.reasoning.append(f"Security score: {state.security_score:.2f}")
        state.reasoning.append(f"Access factors: {len(state.access_factors)}")
        state.reasoning.append(f"Compliance checks passed: {len(state.compliance_checks)}")
        state.reasoning.append(f"Security violations: {len(state.security_violations)}")
        state.reasoning.append(f"Threat indicators: {len(state.threat_indicators)}")
        state.reasoning.append(f"Risk factors: {len(state.risk_factors)}")
        
        # Log security summary
        self.logger.info(f"Strict agent decision for {state.request_id}: {state.final_decision}")
        if state.security_violations:
            self.logger.warning(f"Security violations: {state.security_violations}")
        if state.threat_indicators:
            self.logger.warning(f"Threat indicators: {state.threat_indicators}")
        
        return state
    
    def get_agent_status(self) -> Dict[str, Any]:
        """Get current agent status and configuration"""
        base_status = super().get_agent_status()
        base_status.update({
            "agent_type": "strict",
            "decision_weights": self.decision_weights,
            "allow_threshold": self.allow_threshold,
            "deny_threshold": self.deny_threshold,
            "minimum_trust_score": self.minimum_trust_score,
            "required_verifications": self.required_verifications,
            "network_agents": len(self.network_agents),
            "approach": "security_first_strict_requirements"
        })
        return base_status