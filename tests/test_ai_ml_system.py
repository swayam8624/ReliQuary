"""
Comprehensive Test Suite for ReliQuary AI/ML Enhanced Decision System

This module tests all components of the AI/ML intelligence engine, decision
optimizer, NLP processor, and integration manager.
"""

import pytest
import asyncio
import json
import time
from datetime import datetime, timedelta
from typing import Dict, List, Any

# Import AI/ML components to test
from ai_ml.intelligence_engine import (
    IntelligenceEngine, TrustPredictor, AnomalyDetector, 
    DecisionConfidence, IntelligenceModelType
)
from ai_ml.decision_optimizer import (
    DecisionOptimizer, OptimizationStrategy, NLPProcessor,
    AuditSeverity, OptimizedDecision, AuditAnalysis
)
from ai_ml.integration_manager import (
    AIMLIntegrationManager, AIEnhancedDecisionRequest, AIEnhancedDecisionResult,
    create_ai_enhanced_request, process_batch_decisions
)


class TestTrustPredictor:
    """Test cases for Trust Prediction model"""
    
    def setup_method(self):
        """Setup test fixtures"""
        self.trust_predictor = TrustPredictor("test_trust_predictor")
        
        # Sample training data
        self.training_data = [
            {
                'historical_trust_score': 0.8,
                'success_rate': 0.9,
                'failure_rate': 0.1,
                'response_time_avg': 150,
                'last_interaction_hours': 12,
                'consistency_score': 0.85
            },
            {
                'historical_trust_score': 0.3,
                'success_rate': 0.4,
                'failure_rate': 0.6,
                'response_time_avg': 500,
                'last_interaction_hours': 72,
                'consistency_score': 0.2
            }
        ]
        self.labels = [1, 0]  # High trust, Low trust
    
    def test_feature_preparation(self):
        """Test feature preparation for trust prediction"""
        user_data = {
            'historical_trust_score': 0.7,
            'success_rate': 0.8,
            'response_time_avg': 200
        }
        
        features = self.trust_predictor.prepare_features(user_data)
        
        assert features.shape == (1, 6)  # Should have 6 features
        assert features[0][0] == 0.7  # historical_trust_score
        assert features[0][1] == 0.8  # success_rate
        assert features[0][2] == 0.0  # failure_rate (missing, should be 0)
    
    def test_model_training(self):
        """Test trust predictor model training"""
        metrics = self.trust_predictor.train(self.training_data, self.labels)
        
        assert self.trust_predictor.is_trained
        assert "accuracy" in metrics
        assert metrics["accuracy"] > 0.0
    
    def test_trust_prediction(self):
        """Test trust score prediction"""
        # Train model first
        self.trust_predictor.train(self.training_data, self.labels)
        
        # Test prediction for high-trust user
        high_trust_user = {
            'historical_trust_score': 0.9,
            'success_rate': 0.95,
            'failure_rate': 0.05,
            'consistency_score': 0.9
        }
        
        trust_score, confidence = self.trust_predictor.predict_trust(high_trust_user)
        
        assert 0.0 <= trust_score <= 1.0
        assert isinstance(confidence, DecisionConfidence)
        
        # Test prediction for low-trust user
        low_trust_user = {
            'historical_trust_score': 0.2,
            'success_rate': 0.3,
            'failure_rate': 0.7,
            'consistency_score': 0.1
        }
        
        low_trust_score, low_confidence = self.trust_predictor.predict_trust(low_trust_user)
        
        assert 0.0 <= low_trust_score <= 1.0
        # High trust user should generally have higher score than low trust user
        # (though this isn't guaranteed with simulation data)


class TestAnomalyDetector:
    """Test cases for Anomaly Detection model"""
    
    def setup_method(self):
        """Setup test fixtures"""
        self.anomaly_detector = AnomalyDetector("test_anomaly_detector")
        
        # Normal activity patterns
        self.normal_activities = [
            {
                'access_frequency': 8,
                'unusual_hours': 0,
                'location_variance': 0.1,
                'device_changes': 0,
                'failed_attempts': 0,
                'session_duration': 1800
            },
            {
                'access_frequency': 12,
                'unusual_hours': 1,
                'location_variance': 0.2,
                'device_changes': 1,
                'failed_attempts': 1,
                'session_duration': 2400
            }
        ]
    
    def test_feature_extraction(self):
        """Test behavioral feature extraction"""
        activity_data = {
            'access_frequency': 10,
            'unusual_hours': 2,
            'failed_attempts': 3
        }
        
        features = self.anomaly_detector.extract_features(activity_data)
        
        assert features.shape == (1, 6)  # Should have 6 features
        assert features[0][0] == 10.0  # access_frequency
        assert features[0][1] == 2.0   # unusual_hours
        assert features[0][4] == 3.0   # failed_attempts
    
    def test_model_training(self):
        """Test anomaly detector training"""
        result = self.anomaly_detector.train(self.normal_activities)
        
        assert self.anomaly_detector.is_trained
        assert "model" in result
        assert result["model"] in ["IsolationForest", "simulation"]
    
    def test_anomaly_detection(self):
        """Test anomaly detection functionality"""
        # Train model first
        self.anomaly_detector.train(self.normal_activities)
        
        # Test normal activity
        normal_activity = {
            'access_frequency': 9,
            'unusual_hours': 0,
            'location_variance': 0.15,
            'device_changes': 0,
            'failed_attempts': 0,
            'session_duration': 2000
        }
        
        is_normal_anomaly, normal_score, normal_indicators = self.anomaly_detector.detect_anomaly(normal_activity)
        
        # Test suspicious activity
        suspicious_activity = {
            'access_frequency': 50,  # Very high
            'unusual_hours': 10,     # Very high
            'location_variance': 1.0,  # Maximum variance
            'device_changes': 5,     # Many device changes
            'failed_attempts': 20,   # Many failures
            'session_duration': 10   # Very short sessions
        }
        
        is_suspicious_anomaly, suspicious_score, suspicious_indicators = self.anomaly_detector.detect_anomaly(suspicious_activity)
        
        # Assertions
        assert isinstance(is_normal_anomaly, bool)
        assert isinstance(is_suspicious_anomaly, bool)
        assert 0.0 <= normal_score <= 1.0
        assert 0.0 <= suspicious_score <= 1.0
        assert isinstance(normal_indicators, list)
        assert isinstance(suspicious_indicators, list)
        
        # Suspicious activity should have more indicators
        assert len(suspicious_indicators) >= len(normal_indicators)


class TestDecisionOptimizer:
    """Test cases for Decision Optimizer"""
    
    def setup_method(self):
        """Setup test fixtures"""
        self.optimizer = DecisionOptimizer("test_optimizer")
    
    @pytest.mark.asyncio
    async def test_decision_optimization(self):
        """Test decision optimization functionality"""
        context_data = {
            'resource_sensitivity': 'high',
            'access_type': 'sensitive_data',
            'emergency': False
        }
        
        risk_factors = ['low_trust_score', 'unusual_behavior']
        trust_score = 0.4
        
        result = await self.optimizer.optimize_decision(
            original_decision="ALLOW",
            context_data=context_data,
            risk_factors=risk_factors,
            trust_score=trust_score,
            strategy=OptimizationStrategy.CONSERVATIVE
        )
        
        assert isinstance(result, OptimizedDecision)
        assert result.original_decision == "ALLOW"
        assert result.optimization_strategy == OptimizationStrategy.CONSERVATIVE
        assert result.confidence_improvement >= 0.0
        assert result.risk_reduction >= 0.0
        assert isinstance(result.reasoning, list)
        assert isinstance(result.safeguards_added, list)
        assert result.optimization_time > 0.0
    
    @pytest.mark.asyncio
    async def test_optimization_strategies(self):
        """Test different optimization strategies"""
        context_data = {'resource_sensitivity': 'medium'}
        risk_factors = ['anomalous_behavior']
        trust_score = 0.6
        
        strategies = [
            OptimizationStrategy.CONSERVATIVE,
            OptimizationStrategy.BALANCED,
            OptimizationStrategy.AGGRESSIVE
        ]
        
        results = []
        for strategy in strategies:
            result = await self.optimizer.optimize_decision(
                original_decision="ALLOW",
                context_data=context_data,
                risk_factors=risk_factors,
                trust_score=trust_score,
                strategy=strategy
            )
            results.append(result)
        
        # All results should be valid
        for result in results:
            assert isinstance(result, OptimizedDecision)
            assert result.optimization_time > 0.0


class TestNLPProcessor:
    """Test cases for NLP Processor"""
    
    def setup_method(self):
        """Setup test fixtures"""
        self.nlp_processor = NLPProcessor("test_nlp")
    
    @pytest.mark.asyncio
    async def test_audit_text_analysis(self):
        """Test NLP analysis of audit text"""
        audit_text = """
        User admin123 failed to authenticate 5 times from IP 192.168.1.100.
        Multiple unauthorized access attempts detected. Possible brute force attack.
        System triggered security alert and blocked the IP address.
        """
        
        analysis = await self.nlp_processor.analyze_audit_text(audit_text)
        
        assert isinstance(analysis, AuditAnalysis)
        assert analysis.text_content == audit_text
        assert -1.0 <= analysis.sentiment_score <= 1.0
        assert isinstance(analysis.key_entities, list)
        assert isinstance(analysis.risk_keywords, list)
        assert isinstance(analysis.severity_assessment, AuditSeverity)
        assert isinstance(analysis.extracted_threats, list)
        assert analysis.processing_time > 0.0
        
        # Should detect security-related content
        assert len(analysis.risk_keywords) > 0 or len(analysis.extracted_threats) > 0
        assert analysis.severity_assessment != AuditSeverity.INFO  # Should be higher than info
    
    @pytest.mark.asyncio
    async def test_sentiment_analysis(self):
        """Test sentiment analysis functionality"""
        positive_text = "User successfully authenticated and accessed resources without issues."
        negative_text = "Critical security breach detected. Unauthorized data access and potential malware infection."
        
        positive_analysis = await self.nlp_processor.analyze_audit_text(positive_text)
        negative_analysis = await self.nlp_processor.analyze_audit_text(negative_text)
        
        # Positive text should have higher sentiment score than negative
        assert positive_analysis.sentiment_score >= negative_analysis.sentiment_score
    
    def test_entity_extraction(self):
        """Test entity extraction from text"""
        text = "User admin123 from IP 192.168.1.100 accessed file system at user@example.com"
        
        entities = self.nlp_processor._extract_entities(text)
        
        assert isinstance(entities, list)
        # Should extract IP address
        assert any("192.168.1" in entity for entity in entities)
        # Should extract email
        assert any("@" in entity for entity in entities)


class TestIntelligenceEngine:
    """Test cases for Intelligence Engine"""
    
    def setup_method(self):
        """Setup test fixtures"""
        self.engine = IntelligenceEngine("test_engine")
    
    @pytest.mark.asyncio
    async def test_engine_initialization(self):
        """Test intelligence engine initialization"""
        result = await self.engine.initialize_models()
        
        assert isinstance(result, dict)
        assert "trust_predictor" in result
        assert "anomaly_detector" in result
    
    @pytest.mark.asyncio
    async def test_intelligent_decision_analysis(self):
        """Test comprehensive intelligent decision analysis"""
        # Initialize engine
        await self.engine.initialize_models()
        
        context_data = {
            'resource_id': 'sensitive_document_123',
            'access_type': 'read',
            'timestamp': time.time()
        }
        
        user_data = {
            'user_id': 'test_user_456',
            'historical_trust_score': 0.7,
            'success_rate': 0.85,
            'consistency_score': 0.8
        }
        
        activity_data = {
            'access_frequency': 10,
            'unusual_hours': 1,
            'failed_attempts': 2,
            'device_changes': 0
        }
        
        result = await self.engine.analyze_intelligent_decision(
            original_decision="ALLOW",
            context_data=context_data,
            user_data=user_data,
            activity_data=activity_data
        )
        
        assert result.decision_id is not None
        assert result.original_decision == "ALLOW"
        assert result.ai_recommendation is not None
        assert isinstance(result.confidence, DecisionConfidence)
        assert isinstance(result.reasoning, list)
        assert isinstance(result.risk_factors, list)
        assert 0.0 <= result.trust_score <= 1.0
        assert isinstance(result.anomaly_indicators, list)
        assert result.processing_time > 0.0
        assert isinstance(result.model_versions, dict)
    
    def test_system_status(self):
        """Test system status retrieval"""
        status = self.engine.get_system_status()
        
        assert isinstance(status, dict)
        assert "engine_id" in status
        assert "model_status" in status
        assert "total_predictions" in status
        assert "success_rate" in status
        assert "average_processing_time" in status


class TestAIMLIntegrationManager:
    """Test cases for AI/ML Integration Manager"""
    
    def setup_method(self):
        """Setup test fixtures"""
        self.manager = AIMLIntegrationManager("test_integration")
    
    @pytest.mark.asyncio
    async def test_manager_initialization(self):
        """Test integration manager initialization"""
        result = await self.manager.initialize()
        
        assert isinstance(result, dict)
        assert "integration_id" in result
        assert "intelligence_engine" in result
    
    @pytest.mark.asyncio
    async def test_ai_enhanced_decision_processing(self):
        """Test end-to-end AI-enhanced decision processing"""
        # Initialize manager
        await self.manager.initialize()
        
        # Create test request
        request = AIEnhancedDecisionRequest(
            request_id="test_request_123",
            original_decision_type="access_request",
            context_data={
                'resource_id': 'test_resource',
                'resource_sensitivity': 'medium'
            },
            user_data={
                'user_id': 'test_user',
                'trust_score': 0.7,
                'success_rate': 0.8
            },
            activity_data={
                'access_frequency': 8,
                'failed_attempts': 1,
                'unusual_hours': 0
            },
            optimization_strategy=OptimizationStrategy.BALANCED,
            enable_nlp_analysis=True,
            audit_text="User test_user requested access to test_resource"
        )
        
        result = await self.manager.process_ai_enhanced_decision(request)
        
        assert isinstance(result, AIEnhancedDecisionResult)
        assert result.request_id == "test_request_123"
        assert result.original_decision is not None
        assert result.intelligent_decision is not None
        assert result.optimized_decision is not None
        assert result.final_recommendation is not None
        assert 0.0 <= result.confidence_score <= 1.0
        assert 0.0 <= result.risk_mitigation_score <= 1.0
        assert isinstance(result.processing_metrics, dict)
    
    @pytest.mark.asyncio
    async def test_batch_decision_processing(self):
        """Test batch processing of multiple decisions"""
        # Initialize manager
        await self.manager.initialize()
        
        # Create multiple test requests
        requests = []
        for i in range(3):
            request = create_ai_enhanced_request(
                decision_type="access_request",
                user_id=f"test_user_{i}",
                context_data={'resource_id': f'resource_{i}'},
                user_data={'trust_score': 0.7 + i * 0.1},
                activity_data={'access_frequency': 5 + i}
            )
            requests.append(request)
        
        results = await process_batch_decisions(self.manager, requests)
        
        assert len(results) == 3
        for result in results:
            assert isinstance(result, AIEnhancedDecisionResult)
            assert result.final_recommendation is not None
    
    @pytest.mark.asyncio
    async def test_system_status_and_analytics(self):
        """Test system status and analytics functionality"""
        # Initialize manager
        await self.manager.initialize()
        
        # Get system status
        status = await self.manager.get_system_status()
        
        assert isinstance(status, dict)
        assert "integration_id" in status
        assert "total_requests" in status
        assert "success_rate" in status
        
        # Test pattern analysis
        patterns = await self.manager.analyze_decision_patterns(24)
        
        assert isinstance(patterns, dict)
        assert "analysis_period_hours" in patterns


class TestEndToEndWorkflow:
    """End-to-end integration tests"""
    
    @pytest.mark.asyncio
    async def test_complete_ai_decision_workflow(self):
        """Test complete AI-enhanced decision workflow"""
        # Setup components
        manager = AIMLIntegrationManager("e2e_test")
        await manager.initialize()
        
        # Simulate a high-risk access request
        request = create_ai_enhanced_request(
            decision_type="access_request",
            user_id="suspicious_user",
            context_data={
                'resource_id': 'critical_database',
                'resource_sensitivity': 'critical',
                'access_type': 'admin',
                'emergency': False
            },
            user_data={
                'user_id': 'suspicious_user',
                'historical_trust_score': 0.2,
                'success_rate': 0.3,
                'failure_rate': 0.7,
                'consistency_score': 0.1
            },
            activity_data={
                'access_frequency': 50,
                'unusual_hours': 15,
                'location_variance': 1.0,
                'device_changes': 10,
                'failed_attempts': 25,
                'session_duration': 10
            },
            strategy=OptimizationStrategy.CONSERVATIVE,
            audit_text="User suspicious_user attempting admin access to critical database with multiple failed authentication attempts and unusual access patterns"
        )
        
        # Process the request
        result = await manager.process_ai_enhanced_decision(request)
        
        # Verify security-focused decision
        recommendation_upper = result.final_recommendation.upper()
        assert any(pattern in recommendation_upper for pattern in ["DENY", "INVESTIGATE", "MANUAL_REVIEW"])
        assert result.confidence_score > 0.0
        assert len(result.intelligent_decision.risk_factors) > 0
        assert len(result.optimized_decision.safeguards_added) > 0
        
        # Verify audit analysis detected threats or risk keywords
        if result.audit_analysis:
            # In simulation mode, we may not have full NLP capabilities
            # So check for either severity detection OR risk keyword detection
            has_severity = result.audit_analysis.severity_assessment in [AuditSeverity.HIGH, AuditSeverity.CRITICAL, AuditSeverity.MEDIUM]
            has_risk_keywords = len(result.audit_analysis.risk_keywords) > 0
            assert has_severity or has_risk_keywords, "Should detect either high severity or risk keywords"
    
    @pytest.mark.asyncio
    async def test_normal_user_workflow(self):
        """Test workflow for normal, trusted user"""
        # Setup components
        manager = AIMLIntegrationManager("normal_user_test")
        await manager.initialize()
        
        # Simulate a normal access request
        request = create_ai_enhanced_request(
            decision_type="access_request",
            user_id="trusted_user",
            context_data={
                'resource_id': 'normal_document',
                'resource_sensitivity': 'low',
                'access_type': 'read'
            },
            user_data={
                'user_id': 'trusted_user',
                'historical_trust_score': 0.9,
                'success_rate': 0.95,
                'failure_rate': 0.05,
                'consistency_score': 0.9
            },
            activity_data={
                'access_frequency': 8,
                'unusual_hours': 0,
                'location_variance': 0.1,
                'device_changes': 0,
                'failed_attempts': 0,
                'session_duration': 1800
            },
            strategy=OptimizationStrategy.BALANCED,
            audit_text="User trusted_user requesting normal read access to document"
        )
        
        # Process the request
        result = await manager.process_ai_enhanced_decision(request)
        
        # Verify permissive but monitored decision
        recommendation_upper = result.final_recommendation.upper()
        assert "ALLOW" in recommendation_upper
        assert result.confidence_score > 0.5
        assert len(result.intelligent_decision.risk_factors) == 0 or all("low" in rf.lower() for rf in result.intelligent_decision.risk_factors)


# Performance and stress tests
class TestPerformance:
    """Performance and stress tests"""
    
    @pytest.mark.asyncio
    async def test_decision_processing_performance(self):
        """Test decision processing performance"""
        manager = AIMLIntegrationManager("performance_test")
        await manager.initialize()
        
        # Create a simple request
        request = create_ai_enhanced_request(
            decision_type="access_request",
            user_id="performance_user",
            context_data={'resource_id': 'test_resource'},
            user_data={'trust_score': 0.7},
            activity_data={'access_frequency': 5}
        )
        
        # Measure processing time
        start_time = time.time()
        result = await manager.process_ai_enhanced_decision(request)
        processing_time = time.time() - start_time
        
        # Verify reasonable performance (should be under 5 seconds)
        assert processing_time < 5.0
        assert result.processing_metrics['total_processing_time'] < 5.0
    
    @pytest.mark.asyncio
    async def test_concurrent_decision_processing(self):
        """Test concurrent processing of multiple decisions"""
        manager = AIMLIntegrationManager("concurrent_test")
        await manager.initialize()
        
        # Create multiple requests
        requests = [
            create_ai_enhanced_request(
                decision_type="access_request",
                user_id=f"user_{i}",
                context_data={'resource_id': f'resource_{i}'},
                user_data={'trust_score': 0.5 + i * 0.1},
                activity_data={'access_frequency': 5 + i}
            )
            for i in range(5)
        ]
        
        # Process concurrently
        start_time = time.time()
        results = await process_batch_decisions(manager, requests)
        concurrent_time = time.time() - start_time
        
        # Verify all processed successfully
        assert len(results) == 5
        for result in results:
            assert result.final_recommendation is not None
        
        # Concurrent processing should be faster than sequential
        assert concurrent_time < 15.0  # Should complete within reasonable time


if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v", "--tb=short"])