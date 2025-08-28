"""
ReliQuary AI/ML Enhanced Decision System

This package provides advanced AI/ML capabilities for intelligent decision-making,
behavioral pattern analysis, trust prediction, anomaly detection, and automated
threat response in the ReliQuary multi-agent system.

Components:
- IntelligenceEngine: Core AI/ML intelligence for decision enhancement
- TrustPredictor: Machine learning model for trust score prediction
- AnomalyDetector: Behavioral anomaly detection system
- DecisionOptimizer: AI-driven decision optimization engine
- NLPProcessor: Natural language processing for audit analysis
- AIMLIntegrationManager: Integration layer with ReliQuary agents
"""

from .intelligence_engine import (
    IntelligenceEngine,
    TrustPredictor, 
    AnomalyDetector,
    IntelligenceModelType,
    DecisionConfidence,
    IntelligentDecision
)

from .decision_optimizer import (
    DecisionOptimizer,
    NLPProcessor,
    OptimizationStrategy,
    AuditSeverity,
    OptimizedDecision,
    AuditAnalysis
)

from .integration_manager import (
    AIMLIntegrationManager,
    AIEnhancedDecisionRequest,
    AIEnhancedDecisionResult,
    create_ai_enhanced_request,
    process_batch_decisions
)

__version__ = "1.0.0"
__author__ = "ReliQuary AI/ML Team"

# Package metadata
__all__ = [
    # Core Intelligence Components
    "IntelligenceEngine",
    "TrustPredictor",
    "AnomalyDetector",
    
    # Decision Optimization
    "DecisionOptimizer", 
    "NLPProcessor",
    
    # Integration Layer
    "AIMLIntegrationManager",
    "AIEnhancedDecisionRequest",
    "AIEnhancedDecisionResult",
    
    # Utility Functions
    "create_ai_enhanced_request",
    "process_batch_decisions",
    
    # Enums and Data Classes
    "IntelligenceModelType",
    "DecisionConfidence",
    "OptimizationStrategy",
    "AuditSeverity",
    "IntelligentDecision",
    "OptimizedDecision",
    "AuditAnalysis"
]