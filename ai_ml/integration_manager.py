"""
AI/ML Integration Layer for ReliQuary Multi-Agent System

This module integrates the AI/ML intelligence engine with the existing ReliQuary
multi-agent consensus system, providing intelligent decision enhancement and
behavioral analysis capabilities.
"""

import asyncio
import json
import time
import logging
import hashlib
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional, Any, Union
from dataclasses import dataclass, asdict

# Import ReliQuary components
try:
    from agents.orchestrator import DecisionOrchestrator, DecisionType, DecisionStatus
    from agents.consensus import DistributedConsensusManager
    from agents.workflow import AgentWorkflowCoordinator
    AGENTS_AVAILABLE = True
except ImportError:
    AGENTS_AVAILABLE = False
    logging.warning("Agent modules not available - using simulation mode")

# Import AI/ML components
from ai_ml.intelligence_engine import (
    IntelligenceEngine, IntelligentDecision, DecisionConfidence
)
from ai_ml.decision_optimizer import (
    DecisionOptimizer, OptimizedDecision, OptimizationStrategy,
    NLPProcessor, AuditAnalysis, AuditSeverity
)


@dataclass
class AIEnhancedDecisionRequest:
    """Request for AI-enhanced decision processing"""
    request_id: str
    original_decision_type: str
    context_data: Dict[str, Any]
    user_data: Dict[str, Any]
    activity_data: Dict[str, Any]
    optimization_strategy: OptimizationStrategy
    enable_nlp_analysis: bool = True
    audit_text: Optional[str] = None


@dataclass
class AIEnhancedDecisionResult:
    """Result of AI-enhanced decision processing"""
    request_id: str
    original_decision: str
    intelligent_decision: IntelligentDecision
    optimized_decision: OptimizedDecision
    audit_analysis: Optional[AuditAnalysis]
    final_recommendation: str
    confidence_score: float
    risk_mitigation_score: float
    processing_metrics: Dict[str, float]
    timestamp: datetime


class AIMLIntegrationManager:
    """Manager for integrating AI/ML capabilities with ReliQuary agents"""
    
    def __init__(self, integration_id: str = "aiml_integration_v1"):
        self.integration_id = integration_id
        self.logger = logging.getLogger(f"aiml_integration.{integration_id}")
        
        # Initialize AI/ML components
        self.intelligence_engine = IntelligenceEngine()
        self.decision_optimizer = DecisionOptimizer()
        self.nlp_processor = NLPProcessor()
        
        # Initialize agent connections
        self.orchestrator = None
        self.consensus_manager = None
        self.workflow_coordinator = None
        
        # Processing metrics
        self.total_requests = 0
        self.successful_enhancements = 0
        self.average_processing_time = 0.0
        self.enhancement_effectiveness = 0.0
        
        # Decision cache for performance
        self.decision_cache = {}
        self.cache_ttl = 300  # 5 minutes
        
        self.logger.info(f"AI/ML Integration Manager {integration_id} initialized")
    
    async def initialize(self, training_data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Initialize the AI/ML integration system"""
        try:
            # Initialize intelligence engine
            intelligence_status = await self.intelligence_engine.initialize_models(training_data)
            
            # Connect to agent systems if available
            if AGENTS_AVAILABLE:
                try:
                    self.orchestrator = DecisionOrchestrator(
                        orchestrator_id="aiml_orchestrator",
                        agent_network=["neutral_agent", "permissive_agent", "strict_agent", "watchdog_agent"]
                    )
                    
                    self.consensus_manager = DistributedConsensusManager(
                        agent_id="aiml_consensus",
                        agent_network=["neutral_agent", "permissive_agent", "strict_agent", "watchdog_agent"]
                    )
                    
                    self.workflow_coordinator = AgentWorkflowCoordinator(
                        coordinator_id="aiml_workflow"
                    )
                    
                    self.logger.info("Connected to ReliQuary agent systems")
                except Exception as e:
                    self.logger.warning(f"Agent system connection failed: {e}")
            
            return {
                "integration_id": self.integration_id,
                "intelligence_engine": intelligence_status,
                "agent_systems_connected": AGENTS_AVAILABLE and self.orchestrator is not None,
                "initialization_time": datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"AI/ML integration initialization failed: {e}")
            raise
    
    async def process_ai_enhanced_decision(self, request: AIEnhancedDecisionRequest) -> AIEnhancedDecisionResult:
        """Process a decision request with AI/ML enhancement"""
        start_time = time.time()
        self.total_requests += 1
        
        try:
            # Check cache first
            cache_key = self._generate_cache_key(request)
            cached_result = self._get_cached_result(cache_key)
            if cached_result:
                return cached_result
            
            # Get base decision from agent orchestrator
            original_decision = await self._get_base_decision(request)
            
            # Apply AI intelligence analysis
            intelligent_decision = await self.intelligence_engine.analyze_intelligent_decision(
                original_decision=original_decision,
                context_data=request.context_data,
                user_data=request.user_data,
                activity_data=request.activity_data
            )
            
            # Apply decision optimization
            optimized_decision = await self.decision_optimizer.optimize_decision(
                original_decision=intelligent_decision.ai_recommendation,
                context_data=request.context_data,
                risk_factors=intelligent_decision.risk_factors,
                trust_score=intelligent_decision.trust_score,
                strategy=request.optimization_strategy
            )
            
            # Perform NLP analysis if requested and text provided
            audit_analysis = None
            if request.enable_nlp_analysis and request.audit_text:
                audit_analysis = await self.nlp_processor.analyze_audit_text(
                    text_content=request.audit_text,
                    content_type="decision_context"
                )
            
            # Generate final recommendation
            final_recommendation = self._generate_final_recommendation(
                intelligent_decision, optimized_decision, audit_analysis
            )
            
            # Calculate metrics
            confidence_score = self._calculate_overall_confidence(
                intelligent_decision, optimized_decision, audit_analysis
            )
            
            risk_mitigation_score = self._calculate_risk_mitigation(
                intelligent_decision, optimized_decision
            )
            
            processing_time = time.time() - start_time
            
            # Create result
            result = AIEnhancedDecisionResult(
                request_id=request.request_id,
                original_decision=original_decision,
                intelligent_decision=intelligent_decision,
                optimized_decision=optimized_decision,
                audit_analysis=audit_analysis,
                final_recommendation=final_recommendation,
                confidence_score=confidence_score,
                risk_mitigation_score=risk_mitigation_score,
                processing_metrics={
                    "total_processing_time": processing_time,
                    "intelligence_time": intelligent_decision.processing_time,
                    "optimization_time": optimized_decision.optimization_time,
                    "nlp_time": audit_analysis.processing_time if audit_analysis else 0.0
                },
                timestamp=datetime.now()
            )
            
            # Cache result
            self._cache_result(cache_key, result)
            
            # Update metrics
            self.successful_enhancements += 1
            self._update_performance_metrics(processing_time, confidence_score, risk_mitigation_score)
            
            return result
            
        except Exception as e:
            self.logger.error(f"AI-enhanced decision processing failed: {e}")
            processing_time = time.time() - start_time
            
            # Return fallback result
            return AIEnhancedDecisionResult(
                request_id=request.request_id,
                original_decision="MANUAL_REVIEW_REQUIRED",
                intelligent_decision=IntelligentDecision(
                    decision_id=f"error_{int(time.time())}",
                    original_decision="ERROR",
                    ai_recommendation="MANUAL_REVIEW_REQUIRED",
                    confidence=DecisionConfidence.VERY_LOW,
                    reasoning=[f"AI processing failed: {str(e)}"],
                    risk_factors=["AI_PROCESSING_ERROR"],
                    trust_score=0.0,
                    anomaly_indicators=[],
                    processing_time=processing_time,
                    model_versions={}
                ),
                optimized_decision=OptimizedDecision(
                    original_decision="ERROR",
                    optimized_decision="MANUAL_REVIEW_REQUIRED",
                    optimization_strategy=request.optimization_strategy,
                    confidence_improvement=0.0,
                    risk_reduction=0.0,
                    reasoning=["Fallback due to AI processing error"],
                    safeguards_added=["manual_review", "error_logging"],
                    performance_impact="high",
                    optimization_time=0.0
                ),
                audit_analysis=None,
                final_recommendation="MANUAL_REVIEW_REQUIRED",
                confidence_score=0.0,
                risk_mitigation_score=0.0,
                processing_metrics={"error_time": processing_time},
                timestamp=datetime.now()
            )
    
    async def _get_base_decision(self, request: AIEnhancedDecisionRequest) -> str:
        """Get base decision from agent orchestrator"""
        if not AGENTS_AVAILABLE or not self.orchestrator:
            # Simulation mode - simple rule-based decision
            trust_score = request.user_data.get('trust_score', 0.5)
            failed_attempts = request.activity_data.get('failed_attempts', 0)
            
            if failed_attempts > 5 or trust_score < 0.3:
                return "DENY"
            elif trust_score > 0.8 and failed_attempts == 0:
                return "ALLOW"
            else:
                return "ALLOW_WITH_MONITORING"
        
        try:
            # Convert decision type
            decision_type = DecisionType.ACCESS_REQUEST
            if "governance" in request.original_decision_type.lower():
                decision_type = DecisionType.GOVERNANCE_PROPOSAL
            elif "emergency" in request.original_decision_type.lower():
                decision_type = DecisionType.EMERGENCY_OVERRIDE
            
            # Orchestrate decision
            result = await self.orchestrator.orchestrate_decision(
                decision_type=decision_type,
                requestor_id=request.user_data.get('user_id', 'unknown'),
                context_data=request.context_data,
                priority=5,
                timeout_seconds=30.0
            )
            
            return result.final_decision
            
        except Exception as e:
            self.logger.error(f"Base decision orchestration failed: {e}")
            return "MANUAL_REVIEW_REQUIRED"
    
    def _generate_final_recommendation(self, 
                                     intelligent_decision: IntelligentDecision,
                                     optimized_decision: OptimizedDecision,
                                     audit_analysis: Optional[AuditAnalysis]) -> str:
        """Generate final recommendation combining all AI analyses"""
        # Start with optimized decision
        base_recommendation = optimized_decision.optimized_decision
        
        # Consider audit analysis if available
        if audit_analysis:
            if audit_analysis.severity_assessment in [AuditSeverity.CRITICAL, AuditSeverity.HIGH]:
                # High severity audit findings override permissive decisions
                if "ALLOW" in base_recommendation:
                    base_recommendation = "DENY_DUE_TO_AUDIT_FINDINGS"
            
            elif audit_analysis.severity_assessment == AuditSeverity.MEDIUM:
                # Medium severity adds monitoring
                if base_recommendation == "ALLOW":
                    base_recommendation = "ALLOW_WITH_ENHANCED_MONITORING"
        
        # Consider confidence levels
        if intelligent_decision.confidence == DecisionConfidence.VERY_LOW:
            if "ALLOW" in base_recommendation:
                base_recommendation = "ALLOW_WITH_MANUAL_VERIFICATION"
        
        # Consider risk factors
        if len(intelligent_decision.risk_factors) > 3:
            if "ALLOW" in base_recommendation:
                base_recommendation = "ALLOW_WITH_STRICT_SAFEGUARDS"
        
        return base_recommendation
    
    def _calculate_overall_confidence(self, 
                                    intelligent_decision: IntelligentDecision,
                                    optimized_decision: OptimizedDecision,
                                    audit_analysis: Optional[AuditAnalysis]) -> float:
        """Calculate overall confidence score"""
        confidence_values = {
            DecisionConfidence.VERY_LOW: 0.1,
            DecisionConfidence.LOW: 0.3,
            DecisionConfidence.MEDIUM: 0.5,
            DecisionConfidence.HIGH: 0.7,
            DecisionConfidence.VERY_HIGH: 0.9
        }
        
        base_confidence = confidence_values[intelligent_decision.confidence]
        
        # Adjust for optimization confidence improvement
        optimization_boost = optimized_decision.confidence_improvement * 0.2
        
        # Adjust for audit analysis confidence
        audit_adjustment = 0.0
        if audit_analysis:
            audit_adjustment = audit_analysis.confidence * 0.1
        
        total_confidence = base_confidence + optimization_boost + audit_adjustment
        return min(1.0, total_confidence)
    
    def _calculate_risk_mitigation(self, 
                                 intelligent_decision: IntelligentDecision,
                                 optimized_decision: OptimizedDecision) -> float:
        """Calculate risk mitigation score"""
        base_risk_reduction = optimized_decision.risk_reduction
        
        # Adjust for safeguards
        safeguard_benefit = len(optimized_decision.safeguards_added) * 0.1
        
        # Adjust for anomaly detection
        anomaly_penalty = len(intelligent_decision.anomaly_indicators) * 0.05
        
        total_mitigation = base_risk_reduction + safeguard_benefit - anomaly_penalty
        return max(0.0, min(1.0, total_mitigation))
    
    def _generate_cache_key(self, request: AIEnhancedDecisionRequest) -> str:
        """Generate cache key for decision request"""
        key_data = {
            "decision_type": request.original_decision_type,
            "user_id": request.user_data.get('user_id', 'unknown'),
            "resource": request.context_data.get('resource_id', 'unknown'),
            "strategy": request.optimization_strategy.value
        }
        return hashlib.md5(json.dumps(key_data, sort_keys=True).encode()).hexdigest()
    
    def _get_cached_result(self, cache_key: str) -> Optional[AIEnhancedDecisionResult]:
        """Get cached result if available and not expired"""
        if cache_key in self.decision_cache:
            cached_data = self.decision_cache[cache_key]
            if time.time() - cached_data['timestamp'] < self.cache_ttl:
                return cached_data['result']
            else:
                # Clean expired cache entry
                del self.decision_cache[cache_key]
        return None
    
    def _cache_result(self, cache_key: str, result: AIEnhancedDecisionResult):
        """Cache decision result"""
        self.decision_cache[cache_key] = {
            'result': result,
            'timestamp': time.time()
        }
        
        # Clean old cache entries periodically
        if len(self.decision_cache) > 1000:
            current_time = time.time()
            expired_keys = [
                key for key, data in self.decision_cache.items()
                if current_time - data['timestamp'] > self.cache_ttl
            ]
            for key in expired_keys:
                del self.decision_cache[key]
    
    def _update_performance_metrics(self, processing_time: float, 
                                  confidence_score: float, risk_mitigation_score: float):
        """Update performance metrics"""
        # Update average processing time
        total_time = self.average_processing_time * (self.total_requests - 1) + processing_time
        self.average_processing_time = total_time / self.total_requests
        
        # Update enhancement effectiveness
        enhancement_score = (confidence_score + risk_mitigation_score) / 2
        total_effectiveness = self.enhancement_effectiveness * (self.successful_enhancements - 1) + enhancement_score
        self.enhancement_effectiveness = total_effectiveness / self.successful_enhancements
    
    async def get_system_status(self) -> Dict[str, Any]:
        """Get comprehensive system status"""
        intelligence_status = self.intelligence_engine.get_system_status()
        
        return {
            "integration_id": self.integration_id,
            "total_requests": self.total_requests,
            "successful_enhancements": self.successful_enhancements,
            "success_rate": self.successful_enhancements / max(1, self.total_requests),
            "average_processing_time": self.average_processing_time,
            "enhancement_effectiveness": self.enhancement_effectiveness,
            "cache_size": len(self.decision_cache),
            "agent_systems_connected": AGENTS_AVAILABLE and self.orchestrator is not None,
            "intelligence_engine": intelligence_status,
            "components_status": {
                "decision_optimizer": True,
                "nlp_processor": True,
                "cache_system": True
            }
        }
    
    async def analyze_decision_patterns(self, time_period_hours: int = 24) -> Dict[str, Any]:
        """Analyze decision patterns over a time period"""
        # This would analyze historical decision data
        # For now, return current metrics
        return {
            "analysis_period_hours": time_period_hours,
            "total_decisions_analyzed": self.total_requests,
            "average_confidence": self.enhancement_effectiveness,
            "common_optimization_strategies": ["balanced", "conservative"],
            "top_risk_factors": ["low_trust_score", "anomalous_behavior"],
            "improvement_suggestions": [
                "Increase training data for better trust prediction",
                "Enhance anomaly detection sensitivity",
                "Optimize decision caching strategy"
            ]
        }
    
    async def retrain_models(self, new_training_data: Dict[str, Any]) -> Dict[str, Any]:
        """Retrain AI/ML models with new data"""
        try:
            # Retrain intelligence engine
            retraining_results = await self.intelligence_engine.initialize_models(new_training_data)
            
            self.logger.info(f"Models retrained successfully: {retraining_results}")
            
            # Clear cache to ensure fresh predictions
            self.decision_cache.clear()
            
            return {
                "retrain_status": "success",
                "retrain_results": retraining_results,
                "cache_cleared": True,
                "retrain_timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Model retraining failed: {e}")
            return {
                "retrain_status": "failed",
                "error": str(e),
                "retrain_timestamp": datetime.now().isoformat()
            }


# Utility functions
def create_ai_enhanced_request(decision_type: str,
                             user_id: str,
                             context_data: Dict[str, Any],
                             user_data: Dict[str, Any],
                             activity_data: Dict[str, Any],
                             strategy: OptimizationStrategy = OptimizationStrategy.BALANCED,
                             audit_text: Optional[str] = None) -> AIEnhancedDecisionRequest:
    """Create an AI-enhanced decision request"""
    return AIEnhancedDecisionRequest(
        request_id=f"ai_request_{int(time.time())}_{hash(user_id) % 10000}",
        original_decision_type=decision_type,
        context_data=context_data,
        user_data=user_data,
        activity_data=activity_data,
        optimization_strategy=strategy,
        enable_nlp_analysis=audit_text is not None,
        audit_text=audit_text
    )


async def process_batch_decisions(integration_manager: AIMLIntegrationManager,
                                requests: List[AIEnhancedDecisionRequest]) -> List[AIEnhancedDecisionResult]:
    """Process multiple decision requests in batch"""
    tasks = [
        integration_manager.process_ai_enhanced_decision(request)
        for request in requests
    ]
    
    results = await asyncio.gather(*tasks, return_exceptions=True)
    
    # Handle any exceptions
    processed_results = []
    for i, result in enumerate(results):
        if isinstance(result, Exception):
            logging.error(f"Batch decision {i} failed: {result}")
            # Create error result
            error_result = AIEnhancedDecisionResult(
                request_id=requests[i].request_id,
                original_decision="ERROR",
                intelligent_decision=None,
                optimized_decision=None,
                audit_analysis=None,
                final_recommendation="MANUAL_REVIEW_REQUIRED",
                confidence_score=0.0,
                risk_mitigation_score=0.0,
                processing_metrics={"error": str(result)},
                timestamp=datetime.now()
            )
            processed_results.append(error_result)
        else:
            processed_results.append(result)
    
    return processed_results