"""
Watchdog Agent Node for ReliQuary Multi-Agent Consensus System

The Watchdog Agent specializes in anomaly detection, threat monitoring, and
security surveillance. It focuses on identifying suspicious patterns, behavioral
anomalies, and potential security breaches that other agents might miss.
"""

import logging
import time
import statistics
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
from collections import defaultdict, deque

# LangGraph and LangChain imports
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage
from langchain_core.runnables import RunnableLambda
from langgraph.graph import StateGraph, END

# ReliQuary imports
from ..agent_foundation import BaseAgent, AgentCapabilities, AgentRole
from .neutral_agent import DecisionConfidence, NeutralDecisionState


class ThreatLevel(Enum):
    """Threat severity levels"""
    NONE = "none"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class WatchdogDecisionState(NeutralDecisionState):
    """State object for watchdog agent decision process"""
    anomalies: List[str] = None
    threat_level: ThreatLevel = ThreatLevel.NONE
    behavioral_analysis: Dict[str, Any] = None
    pattern_deviations: List[str] = None
    security_alerts: List[str] = None
    monitoring_flags: List[str] = None
    anomaly_score: float = 0.0
    
    def __post_init__(self):
        super().__post_init__()
        if self.anomalies is None:
            self.anomalies = []
        if self.behavioral_analysis is None:
            self.behavioral_analysis = {}
        if self.pattern_deviations is None:
            self.pattern_deviations = []
        if self.security_alerts is None:
            self.security_alerts = []
        if self.monitoring_flags is None:
            self.monitoring_flags = []


class WatchdogAgent(BaseAgent):
    """
    Watchdog Agent implementation for threat monitoring and anomaly detection.
    
    The Watchdog Agent continuously monitors access patterns, behavioral anomalies,
    and security indicators to detect potential threats and suspicious activities.
    """
    
    def __init__(self, agent_id: str, network_agents: List[str]):
        """
        Initialize the Watchdog Agent.
        
        Args:
            agent_id: Unique identifier for this agent
            network_agents: List of all agent IDs in the network
        """
        capabilities = AgentCapabilities(
            roles=[AgentRole.MONITOR],
            max_concurrent_tasks=20,  # High capacity for monitoring
            supported_verification_types=["device", "location", "timestamp", "pattern", "anomaly"],
            trust_scoring_enabled=True,
            consensus_participation=True,
            specializations=["anomaly_detection", "threat_monitoring", "behavioral_analysis"]
        )
        
        super().__init__(agent_id, capabilities)
        
        self.network_agents = network_agents
        
        # Monitoring-oriented decision weights
        self.decision_weights = {
            "anomaly_detection": 0.3,     # Primary focus
            "behavioral_analysis": 0.25,  # Behavior patterns
            "threat_assessment": 0.2,     # Threat evaluation
            "trust_score": 0.15,          # Lower weight on trust
            "context_verification": 0.1   # Context as supporting evidence
        }
        
        # Watchdog-specific thresholds
        self.anomaly_threshold = 0.3    # Threshold for anomaly detection
        self.threat_threshold = 0.5     # Threshold for threat classification
        self.critical_threshold = 0.8   # Threshold for critical threats
        
        # Behavioral baseline tracking
        self.user_baselines: Dict[str, Dict[str, Any]] = {}
        self.global_patterns: Dict[str, deque] = defaultdict(lambda: deque(maxlen=100))
        
        # Initialize LangGraph workflow
        self._build_decision_graph()
        
        self.logger = logging.getLogger(f"watchdog_agent.{self.agent_id}")
    
    def _build_decision_graph(self):
        """Build the LangGraph decision workflow for watchdog agent"""
        workflow = StateGraph(WatchdogDecisionState)
        
        # Add nodes
        workflow.add_node("initialize", self._initialize_monitoring)
        workflow.add_node("collect_baseline", self._collect_baseline)
        workflow.add_node("detect_anomalies", self._detect_anomalies)
        workflow.add_node("analyze_behavior", self._analyze_behavior)
        workflow.add_node("assess_threats", self._assess_threats)
        workflow.add_node("pattern_analysis", self._pattern_analysis)
        workflow.add_node("security_correlation", self._security_correlation)
        workflow.add_node("make_decision", self._make_decision)
        workflow.add_node("finalize", self._finalize_decision)
        
        # Define the flow
        workflow.set_entry_point("initialize")
        workflow.add_edge("initialize", "collect_baseline")
        workflow.add_edge("collect_baseline", "detect_anomalies")
        workflow.add_edge("detect_anomalies", "analyze_behavior")
        workflow.add_edge("analyze_behavior", "assess_threats")
        workflow.add_edge("assess_threats", "pattern_analysis")
        workflow.add_edge("pattern_analysis", "security_correlation")
        workflow.add_edge("security_correlation", "make_decision")
        workflow.add_edge("make_decision", "finalize")
        workflow.add_edge("finalize", END)
        
        self.decision_graph = workflow.compile()
    
    async def evaluate_access_request(self, 
                                    request_id: str,
                                    context_data: Dict[str, Any],
                                    trust_score: float,
                                    history: List[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Evaluate an access request using the watchdog agent logic.
        
        Args:
            request_id: Unique identifier for the request
            context_data: Context information for the request
            trust_score: Current trust score for the user
            history: Historical decision data
            
        Returns:
            Dictionary containing the decision and reasoning
        """
        # Initialize state
        initial_state = WatchdogDecisionState(
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
                "anomalies": result.anomalies,
                "threat_level": result.threat_level.value,
                "behavioral_analysis": result.behavioral_analysis,
                "pattern_deviations": result.pattern_deviations,
                "security_alerts": result.security_alerts,
                "monitoring_flags": result.monitoring_flags,
                "anomaly_score": result.anomaly_score,
                "timestamp": time.time()
            }
            
        except Exception as e:
            self.logger.error(f"Decision evaluation failed: {e}")
            self.metrics.failed_verifications += 1
            return {
                "agent_id": self.agent_id,
                "decision": "deny",
                "confidence": "high",  # High confidence in denying on monitoring failure
                "reasoning": [f"Monitoring system error - security protocol: {str(e)}"],
                "threat_level": "high",
                "timestamp": time.time()
            }
    
    def _initialize_monitoring(self, state: WatchdogDecisionState) -> WatchdogDecisionState:
        """Initialize the monitoring and anomaly detection process"""
        state.current_step = "initialize"
        state.reasoning.append("Starting watchdog agent monitoring")
        state.reasoning.append("Focus: Anomaly detection and threat monitoring")
        
        # Initialize behavioral analysis structure
        state.behavioral_analysis = {
            "typing_pattern": {},
            "access_pattern": {},
            "session_behavior": {},
            "temporal_analysis": {}
        }
        
        # Start with medium confidence for monitoring
        state.confidence = DecisionConfidence.MEDIUM
        
        return state
    
    def _collect_baseline(self, state: WatchdogDecisionState) -> WatchdogDecisionState:
        """Collect and update behavioral baselines"""
        state.current_step = "collect_baseline"
        
        context = state.context_data
        user_id = context.get("user_id", "unknown")
        
        # Initialize user baseline if not exists
        if user_id not in self.user_baselines:
            self.user_baselines[user_id] = {
                "typing_speeds": deque(maxlen=20),
                "session_durations": deque(maxlen=15),
                "access_frequencies": deque(maxlen=10),
                "access_times": deque(maxlen=30),
                "last_updated": time.time()
            }
        
        baseline = self.user_baselines[user_id]
        
        # Update baselines with current data
        if "keystrokes_per_minute" in context:
            baseline["typing_speeds"].append(context["keystrokes_per_minute"])
        
        if "session_duration" in context:
            baseline["session_durations"].append(context["session_duration"])
        
        if "access_frequency" in context:
            baseline["access_frequencies"].append(context["access_frequency"])
        
        # Record access time
        current_hour = int(time.time() % 86400 / 3600)
        baseline["access_times"].append(current_hour)
        baseline["last_updated"] = time.time()
        
        state.reasoning.append(f"Baseline updated for user {user_id}")
        
        return state
    
    def _detect_anomalies(self, state: WatchdogDecisionState) -> WatchdogDecisionState:
        """Detect behavioral and statistical anomalies"""
        state.current_step = "detect_anomalies"
        
        context = state.context_data
        user_id = context.get("user_id", "unknown")
        anomaly_score = 0
        
        if user_id in self.user_baselines:
            baseline = self.user_baselines[user_id]
            
            # Typing speed anomaly detection
            if "keystrokes_per_minute" in context and baseline["typing_speeds"]:
                current_speed = context["keystrokes_per_minute"]
                speeds = list(baseline["typing_speeds"])
                
                if len(speeds) >= 3:
                    mean_speed = statistics.mean(speeds)
                    stdev_speed = statistics.stdev(speeds) if len(speeds) > 1 else 10
                    
                    z_score = abs(current_speed - mean_speed) / max(stdev_speed, 5)
                    if z_score > 2.5:
                        state.anomalies.append(f"Unusual typing speed: {current_speed} (baseline: {mean_speed:.1f})")
                        anomaly_score += 0.3
                    elif z_score > 1.5:
                        state.monitoring_flags.append("Typing speed variation detected")
                        anomaly_score += 0.1
            
            # Session duration anomaly detection
            if "session_duration" in context and baseline["session_durations"]:
                current_duration = context["session_duration"]
                durations = list(baseline["session_durations"])
                
                if len(durations) >= 3:
                    mean_duration = statistics.mean(durations)
                    
                    # Very short or very long sessions are suspicious
                    if current_duration < mean_duration * 0.1:
                        state.anomalies.append("Unusually short session duration")
                        anomaly_score += 0.4
                    elif current_duration > mean_duration * 5:
                        state.anomalies.append("Unusually long session duration")
                        anomaly_score += 0.2
            
            # Access frequency anomaly detection
            if "access_frequency" in context and baseline["access_frequencies"]:
                current_freq = context["access_frequency"]
                frequencies = list(baseline["access_frequencies"])
                
                if frequencies:
                    max_freq = max(frequencies)
                    if current_freq > max_freq * 3:
                        state.anomalies.append("Extremely high access frequency")
                        anomaly_score += 0.5
                    elif current_freq > max_freq * 2:
                        state.monitoring_flags.append("High access frequency")
                        anomaly_score += 0.2
            
            # Temporal access pattern anomaly
            if baseline["access_times"]:
                current_hour = int(time.time() % 86400 / 3600)
                access_times = list(baseline["access_times"])
                
                # Check if current access is outside normal hours
                normal_hours = set(access_times)
                if current_hour not in normal_hours and len(normal_hours) >= 5:
                    state.anomalies.append(f"Access outside normal hours: {current_hour}")
                    anomaly_score += 0.3
        
        # Global anomaly detection
        self._detect_global_anomalies(state, context)
        
        state.anomaly_score = anomaly_score
        state.reasoning.append(f"Anomaly detection completed: score {anomaly_score:.2f}")
        
        return state
    
    def _detect_global_anomalies(self, state: WatchdogDecisionState, context: Dict[str, Any]):
        """Detect anomalies against global patterns"""
        # Check against global typing speed patterns
        if "keystrokes_per_minute" in context:
            speed = context["keystrokes_per_minute"]
            self.global_patterns["typing_speeds"].append(speed)
            
            if len(self.global_patterns["typing_speeds"]) >= 10:
                global_speeds = list(self.global_patterns["typing_speeds"])
                global_mean = statistics.mean(global_speeds)
                
                if speed > global_mean * 4 or speed < global_mean * 0.1:
                    state.anomalies.append("Extreme deviation from global typing patterns")
        
        # Check for impossible human behavior
        if "keystrokes_per_minute" in context:
            kpm = context["keystrokes_per_minute"]
            if kpm > 500 or kpm < 1:
                state.anomalies.append("Impossible human typing speed")
                state.security_alerts.append("Bot-like behavior detected")
    
    def _analyze_behavior(self, state: WatchdogDecisionState) -> WatchdogDecisionState:
        """Analyze behavioral patterns for consistency"""
        state.current_step = "analyze_behavior"
        
        context = state.context_data
        
        # Typing pattern analysis
        kpm = context.get("keystrokes_per_minute", 60)
        session_duration = context.get("session_duration", 1800)
        
        state.behavioral_analysis["typing_pattern"] = {
            "speed": kpm,
            "consistency": "normal",  # Simplified
            "human_like": 10 <= kpm <= 200
        }
        
        if not state.behavioral_analysis["typing_pattern"]["human_like"]:
            state.pattern_deviations.append("Non-human typing pattern")
        
        # Access pattern analysis
        access_freq = context.get("access_frequency", 1)
        state.behavioral_analysis["access_pattern"] = {
            "frequency": access_freq,
            "normal_range": 1 <= access_freq <= 10,
            "burst_activity": access_freq > 15
        }
        
        if state.behavioral_analysis["access_pattern"]["burst_activity"]:
            state.pattern_deviations.append("Burst access activity detected")
        
        # Session behavior analysis
        state.behavioral_analysis["session_behavior"] = {
            "duration": session_duration,
            "reasonable": 60 <= session_duration <= 14400,
            "suspicious_short": session_duration < 30,
            "suspicious_long": session_duration > 28800
        }
        
        if state.behavioral_analysis["session_behavior"]["suspicious_short"]:
            state.pattern_deviations.append("Suspiciously short session")
        elif state.behavioral_analysis["session_behavior"]["suspicious_long"]:
            state.pattern_deviations.append("Unusually long session")
        
        # Temporal analysis
        current_hour = int(time.time() % 86400 / 3600)
        state.behavioral_analysis["temporal_analysis"] = {
            "access_hour": current_hour,
            "business_hours": 9 <= current_hour <= 17,
            "off_hours": current_hour < 6 or current_hour > 22
        }
        
        if state.behavioral_analysis["temporal_analysis"]["off_hours"]:
            state.monitoring_flags.append("Off-hours access")
        
        state.reasoning.append(f"Behavioral analysis: {len(state.pattern_deviations)} deviations")
        
        return state
    
    def _assess_threats(self, state: WatchdogDecisionState) -> WatchdogDecisionState:
        """Assess threat level based on anomalies and patterns"""
        state.current_step = "assess_threats"
        
        threat_score = 0
        
        # Anomaly-based threat assessment
        if state.anomaly_score > 0.7:
            threat_score += 0.5
            state.security_alerts.append("High anomaly score detected")
        elif state.anomaly_score > 0.4:
            threat_score += 0.3
        
        # Pattern deviation assessment
        if len(state.pattern_deviations) >= 3:
            threat_score += 0.4
            state.security_alerts.append("Multiple pattern deviations")
        elif len(state.pattern_deviations) >= 2:
            threat_score += 0.2
        
        # Trust score correlation
        if state.trust_score < 30:
            threat_score += 0.3
            state.security_alerts.append("Low trust score correlation")
        
        # Historical threat indicators
        if state.decision_history:
            recent_denials = sum(1 for d in state.decision_history[-5:] 
                               if d.get("decision") == "deny")
            if recent_denials >= 3:
                threat_score += 0.2
                state.security_alerts.append("Pattern of recent denials")
        
        # Determine threat level
        if threat_score >= 0.8:
            state.threat_level = ThreatLevel.CRITICAL
        elif threat_score >= 0.6:
            state.threat_level = ThreatLevel.HIGH
        elif threat_score >= 0.4:
            state.threat_level = ThreatLevel.MEDIUM
        elif threat_score >= 0.2:
            state.threat_level = ThreatLevel.LOW
        else:
            state.threat_level = ThreatLevel.NONE
        
        state.reasoning.append(f"Threat assessment: {state.threat_level.value} (score: {threat_score:.2f})")
        
        return state
    
    def _pattern_analysis(self, state: WatchdogDecisionState) -> WatchdogDecisionState:
        """Analyze patterns across multiple dimensions"""
        state.current_step = "pattern_analysis"
        
        # Cross-correlation analysis
        correlations = []
        
        # Check trust score vs anomaly correlation
        if state.trust_score < 50 and state.anomaly_score > 0.3:
            correlations.append("Low trust correlates with high anomalies")
        
        # Check verification vs behavior correlation
        context = state.context_data
        failed_verifications = sum(1 for check in ["device_verified", "location_verified", "timestamp_verified"] 
                                 if not context.get(check, True))
        
        if failed_verifications >= 2 and len(state.pattern_deviations) >= 2:
            correlations.append("Verification failures correlate with behavior anomalies")
        
        if correlations:
            state.security_alerts.extend(correlations)
            state.reasoning.append(f"Pattern correlations found: {len(correlations)}")
        
        return state
    
    def _security_correlation(self, state: WatchdogDecisionState) -> WatchdogDecisionState:
        """Correlate security indicators for final assessment"""
        state.current_step = "security_correlation"
        
        # Calculate final security correlation score
        security_factors = {
            "anomalies": len(state.anomalies) * 0.2,
            "pattern_deviations": len(state.pattern_deviations) * 0.15,
            "security_alerts": len(state.security_alerts) * 0.25,
            "threat_level_numeric": {
                ThreatLevel.NONE: 0,
                ThreatLevel.LOW: 0.2,
                ThreatLevel.MEDIUM: 0.4,
                ThreatLevel.HIGH: 0.6,
                ThreatLevel.CRITICAL: 0.8
            }[state.threat_level]
        }
        
        total_security_concern = sum(security_factors.values())
        
        if total_security_concern >= 0.8:
            state.confidence = DecisionConfidence.VERY_HIGH
        elif total_security_concern >= 0.6:
            state.confidence = DecisionConfidence.HIGH
        elif total_security_concern >= 0.4:
            state.confidence = DecisionConfidence.MEDIUM
        else:
            state.confidence = DecisionConfidence.LOW
        
        state.reasoning.append(f"Security correlation score: {total_security_concern:.2f}")
        
        return state
    
    def _make_decision(self, state: WatchdogDecisionState) -> WatchdogDecisionState:
        """Make watchdog decision based on monitoring results"""
        state.current_step = "make_decision"
        
        # Critical threat override
        if state.threat_level == ThreatLevel.CRITICAL:
            state.final_decision = "deny"
            state.reasoning.append("Decision: DENY due to critical threat level")
            return state
        
        # High anomaly score override
        if state.anomaly_score >= 0.7:
            state.final_decision = "deny"
            state.reasoning.append(f"Decision: DENY due to high anomaly score: {state.anomaly_score:.2f}")
            return state
        
        # Multiple security alerts
        if len(state.security_alerts) >= 3:
            state.final_decision = "deny"
            state.reasoning.append("Decision: DENY due to multiple security alerts")
            return state
        
        # Calculate watchdog decision score
        base_trust = state.trust_score / 100
        anomaly_penalty = state.anomaly_score
        pattern_penalty = len(state.pattern_deviations) * 0.1
        alert_penalty = len(state.security_alerts) * 0.15
        
        watchdog_score = base_trust - anomaly_penalty - pattern_penalty - alert_penalty
        
        # Apply watchdog-specific thresholds
        if watchdog_score >= 0.6:
            state.final_decision = "allow"
            state.reasoning.append(f"Decision: ALLOW (monitoring score: {watchdog_score:.2f})")
        elif watchdog_score >= 0.3:
            state.final_decision = "allow"
            state.reasoning.append(f"Decision: ALLOW with enhanced monitoring (score: {watchdog_score:.2f})")
            state.monitoring_flags.append("Enhanced monitoring recommended")
        else:
            state.final_decision = "deny"
            state.reasoning.append(f"Decision: DENY (monitoring concerns, score: {watchdog_score:.2f})")
        
        return state
    
    def _finalize_decision(self, state: WatchdogDecisionState) -> WatchdogDecisionState:
        """Finalize watchdog decision with monitoring summary"""
        state.current_step = "finalize"
        
        # Add comprehensive monitoring summary
        state.reasoning.append(f"Final decision: {state.final_decision.upper()}")
        state.reasoning.append(f"Confidence level: {state.confidence.value}")
        state.reasoning.append(f"Threat level: {state.threat_level.value}")
        state.reasoning.append(f"Anomaly score: {state.anomaly_score:.2f}")
        state.reasoning.append(f"Anomalies detected: {len(state.anomalies)}")
        state.reasoning.append(f"Pattern deviations: {len(state.pattern_deviations)}")
        state.reasoning.append(f"Security alerts: {len(state.security_alerts)}")
        state.reasoning.append(f"Monitoring flags: {len(state.monitoring_flags)}")
        
        # Log monitoring results
        self.logger.info(f"Watchdog decision for {state.request_id}: {state.final_decision}")
        if state.security_alerts:
            self.logger.warning(f"Security alerts: {state.security_alerts}")
        if state.anomalies:
            self.logger.warning(f"Anomalies detected: {state.anomalies}")
        
        return state
    
    def get_agent_status(self) -> Dict[str, Any]:
        """Get current agent status and monitoring metrics"""
        base_status = super().get_agent_status()
        base_status.update({
            "agent_type": "watchdog",
            "decision_weights": self.decision_weights,
            "anomaly_threshold": self.anomaly_threshold,
            "threat_threshold": self.threat_threshold,
            "critical_threshold": self.critical_threshold,
            "monitored_users": len(self.user_baselines),
            "global_patterns_size": len(self.global_patterns),
            "network_agents": len(self.network_agents),
            "approach": "threat_monitoring_anomaly_detection"
        })
        return base_status