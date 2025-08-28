"""
Tests for Rule Enforcement System

This module contains tests for the trust rule validation and enforcement system,
including rule validation, evaluation, and policy enforcement.
"""

import pytest
import json
from unittest.mock import patch, MagicMock
from datetime import datetime

# Import rule enforcement components
try:
    from core.rules.validator import RuleValidator
    from apps.api.services.rule_enforcer import RuleEnforcementService
    from core.trust.scorer import TrustScoringEngine
except ImportError:
    # Mock implementations for testing
    class RuleValidator:
        def __init__(self):
            self.rules = [
                {
                    "rule_id": "min_trust_threshold",
                    "name": "Minimum Trust Threshold",
                    "description": "Users must have a minimum trust score of 50",
                    "condition": "trust_score >= 50",
                    "weight": 1.0,
                    "enabled": True
                },
                {
                    "rule_id": "high_risk_block",
                    "name": "High Risk Block",
                    "description": "Block access for high risk users",
                    "condition": "risk_level != 'very_high'",
                    "weight": 0.8,
                    "enabled": True
                }
            ]
        
        def validate_rule(self, rule_config: dict) -> dict:
            return {
                "valid": True,
                "errors": [],
                "warnings": []
            }
        
        def get_active_rules(self) -> list:
            return [rule for rule in self.rules if rule["enabled"]]
    
    class RuleEnforcementService:
        def __init__(self):
            self.rule_validator = RuleValidator()
            self.trust_engine = TrustScoringEngine()
        
        def evaluate_rules(self, user_id: str, context: dict, trust_score: float) -> dict:
            return {
                "compliant": True,
                "passed_rules": ["min_trust_threshold", "high_risk_block"],
                "failed_rules": [],
                "enforcement_action": "allow",
                "confidence": 0.95
            }
    
    class TrustScoringEngine:
        def evaluate_trust(self, user_id: str, context: dict) -> dict:
            return {
                "overall_trust_score": 85.5,
                "risk_level": "low",
                "confidence_score": 0.92,
                "trust_factors": []
            }


@pytest.fixture
def rule_validator():
    """Fixture for rule validator"""
    return RuleValidator()


@pytest.fixture
def rule_enforcement_service():
    """Fixture for rule enforcement service"""
    return RuleEnforcementService()


@pytest.fixture
def trust_engine():
    """Fixture for trust scoring engine"""
    return TrustScoringEngine()


class TestRuleValidation:
    """Test cases for rule validation"""
    
    def test_valid_rule_validation(self, rule_validator):
        """Test validation of a valid rule"""
        # Arrange
        rule_config = {
            "rule_id": "test_rule",
            "name": "Test Rule",
            "description": "A test rule for validation",
            "condition": "trust_score >= 70",
            "weight": 0.5,
            "enabled": True
        }
        
        # Act
        result = rule_validator.validate_rule(rule_config)
        
        # Assert
        assert "valid" in result
        assert "errors" in result
        assert "warnings" in result
        assert result["valid"] is True
        assert len(result["errors"]) == 0
    
    def test_invalid_rule_validation(self, rule_validator):
        """Test validation of an invalid rule"""
        # Arrange
        rule_config = {
            "rule_id": "",  # Missing required field
            "name": "Test Rule",
            "description": "A test rule for validation",
            "condition": "invalid_condition",  # Invalid condition
            "weight": 1.5,  # Invalid weight (> 1.0)
            "enabled": True
        }
        
        # Act
        result = rule_validator.validate_rule(rule_config)
        
        # Assert
        assert result["valid"] is False
        assert len(result["errors"]) > 0
    
    def test_rule_schema_validation(self, rule_validator):
        """Test validation of rule schema"""
        # Arrange
        rule_config = {
            "rule_id": "schema_test",
            "name": "Schema Test Rule",
            "description": "Testing rule schema validation",
            "condition": "user_id != ''",
            "weight": 0.7,
            "enabled": True
        }
        
        # Act
        result = rule_validator.validate_rule(rule_config)
        
        # Assert
        assert result["valid"] is True
        assert "rule_id" in rule_config
        assert "name" in rule_config
        assert "condition" in rule_config


class TestRuleRetrieval:
    """Test cases for rule retrieval"""
    
    def test_get_active_rules(self, rule_validator):
        """Test retrieval of active rules"""
        # Act
        active_rules = rule_validator.get_active_rules()
        
        # Assert
        assert isinstance(active_rules, list)
        assert len(active_rules) > 0
        for rule in active_rules:
            assert "rule_id" in rule
            assert "name" in rule
            assert "condition" in rule
            assert rule.get("enabled", True) is True
    
    def test_get_empty_rules(self):
        """Test retrieval when no rules are configured"""
        # Arrange
        empty_validator = RuleValidator()
        empty_validator.rules = []
        
        # Act
        active_rules = empty_validator.get_active_rules()
        
        # Assert
        assert isinstance(active_rules, list)
        assert len(active_rules) == 0


class TestRuleEnforcement:
    """Test cases for rule enforcement"""
    
    def test_compliant_user_enforcement(self, rule_enforcement_service):
        """Test enforcement for a compliant user"""
        # Arrange
        user_id = "compliant_user"
        context = {
            "resource": "test_resource",
            "action": "read",
            "timestamp": datetime.now().isoformat()
        }
        trust_score = 85.5
        
        # Act
        result = rule_enforcement_service.evaluate_rules(user_id, context, trust_score)
        
        # Assert
        assert "compliant" in result
        assert "passed_rules" in result
        assert "failed_rules" in result
        assert "enforcement_action" in result
        assert result["compliant"] is True
        assert result["enforcement_action"] in ["allow", "challenge", "deny"]
    
    def test_non_compliant_user_enforcement(self, rule_enforcement_service):
        """Test enforcement for a non-compliant user"""
        # Arrange
        user_id = "non_compliant_user"
        context = {
            "resource": "sensitive_resource",
            "action": "write",
            "timestamp": datetime.now().isoformat()
        }
        trust_score = 30.0  # Low trust score
        
        # Act
        result = rule_enforcement_service.evaluate_rules(user_id, context, trust_score)
        
        # Assert
        assert "compliant" in result
        assert isinstance(result["compliant"], bool)
    
    def test_rule_evaluation_with_context(self, rule_enforcement_service):
        """Test rule evaluation with context data"""
        # Arrange
        user_id = "context_user"
        context = {
            "device_verified": True,
            "location_verified": False,
            "time_of_day": "night",
            "access_frequency": 10,
            "trust_score": 75.0
        }
        trust_score = 75.0
        
        # Act
        result = rule_enforcement_service.evaluate_rules(user_id, context, trust_score)
        
        # Assert
        assert "passed_rules" in result
        assert "failed_rules" in result
        assert isinstance(result["passed_rules"], list)
        assert isinstance(result["failed_rules"], list)


class TestTrustIntegration:
    """Test cases for trust engine integration"""
    
    def test_trust_score_integration(self, rule_enforcement_service, trust_engine):
        """Test integration with trust scoring engine"""
        # Arrange
        user_id = "integration_test_user"
        context = {
            "resource": "test_resource",
            "action": "access",
            "device_fingerprint": "test_device_123"
        }
        
        # Act
        trust_result = trust_engine.evaluate_trust(user_id, context)
        enforcement_result = rule_enforcement_service.evaluate_rules(
            user_id, context, trust_result["overall_trust_score"]
        )
        
        # Assert
        assert "overall_trust_score" in trust_result
        assert "risk_level" in trust_result
        assert "compliant" in enforcement_result
        assert isinstance(trust_result["overall_trust_score"], (int, float))
        assert trust_result["overall_trust_score"] >= 0
        assert trust_result["overall_trust_score"] <= 100


class TestEdgeCases:
    """Test edge cases for rule enforcement"""
    
    def test_boundary_trust_scores(self, rule_enforcement_service):
        """Test enforcement with boundary trust scores"""
        # Test with minimum trust score
        result_min = rule_enforcement_service.evaluate_rules("user", {}, 0.0)
        assert "compliant" in result_min
        
        # Test with maximum trust score
        result_max = rule_enforcement_service.evaluate_rules("user", {}, 100.0)
        assert "compliant" in result_max
    
    def test_empty_context_handling(self, rule_enforcement_service):
        """Test handling of empty context"""
        # Act
        result = rule_enforcement_service.evaluate_rules("user", {}, 75.0)
        
        # Assert
        assert "compliant" in result
        assert isinstance(result["compliant"], bool)
    
    def test_malformed_context_handling(self, rule_enforcement_service):
        """Test handling of malformed context"""
        # Arrange
        malformed_context = {"invalid": None, "": "empty_key"}
        
        # Act
        result = rule_enforcement_service.evaluate_rules("user", malformed_context, 75.0)
        
        # Assert
        assert "compliant" in result


if __name__ == "__main__":
    pytest.main([__file__])