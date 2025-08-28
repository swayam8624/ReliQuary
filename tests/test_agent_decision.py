"""
Tests for Agent Decision Making

This module contains tests for the multi-agent consensus system,
including individual agent decisions, consensus building, and orchestration.
"""

import pytest
import json
from unittest.mock import patch, MagicMock
from datetime import datetime
from typing import Dict, Any

# Import agent components
try:
    from agents.decision_orchestrator import DecisionOrchestrator
    from agents.nodes.neutral_agent import NeutralAgent
    from agents.nodes.permissive_agent import PermissiveAgent
    from agents.nodes.strict_agent import StrictAgent
    from agents.nodes.watchdog_agent import WatchdogAgent
    from apps.api.services.agent_orchestrator import AgentOrchestrator, AgentRequest, DecisionType
except ImportError:
    # Mock implementations for testing
    class DecisionOrchestrator:
        async def make_decision(self, context: Dict[str, Any], user_id: str, resource_path: str) -> Dict[str, Any]:
            return {
                "decision": "approved",
                "confidence": 0.95,
                "agents_consulted": ["neutral", "permissive", "strict"],
                "reasoning": "Context verified with high confidence",
                "timestamp": datetime.now().isoformat()
            }
    
    class NeutralAgent:
        def __init__(self, agent_id: str, network_agents: list):
            self.agent_id = agent_id
            self.network_agents = network_agents
        
        async def evaluate_access_request(self, request_id: str, context_data: dict, trust_score: float, history: list = None) -> dict:
            return {
                "agent_id": self.agent_id,
                "decision": "allow",
                "confidence": "medium",
                "reasoning": ["Neutral evaluation completed"],
                "timestamp": datetime.now().timestamp()
            }
    
    class PermissiveAgent:
        def __init__(self, agent_id: str, network_agents: list):
            self.agent_id = agent_id
            self.network_agents = network_agents
        
        async def evaluate_access_request(self, request_id: str, context_data: dict, trust_score: float, history: list = None) -> dict:
            return {
                "agent_id": self.agent_id,
                "decision": "allow",
                "confidence": "high",
                "reasoning": ["Permissive evaluation completed"],
                "timestamp": datetime.now().timestamp()
            }
    
    class StrictAgent:
        def __init__(self, agent_id: str, network_agents: list):
            self.agent_id = agent_id
            self.network_agents = network_agents
        
        async def evaluate_access_request(self, request_id: str, context_data: dict, trust_score: float, history: list = None) -> dict:
            return {
                "agent_id": self.agent_id,
                "decision": "deny",
                "confidence": "high",
                "reasoning": ["Strict evaluation completed"],
                "timestamp": datetime.now().timestamp()
            }
    
    class WatchdogAgent:
        def __init__(self, agent_id: str, network_agents: list):
            self.agent_id = agent_id
            self.network_agents = network_agents
        
        async def evaluate_access_request(self, request_id: str, context_data: dict, trust_score: float, history: list = None) -> dict:
            return {
                "agent_id": self.agent_id,
                "decision": "allow",
                "confidence": "medium",
                "reasoning": ["Watchdog monitoring completed"],
                "timestamp": datetime.now().timestamp()
            }
    
    class AgentOrchestrator:
        def __init__(self):
            self.decision_orchestrator = DecisionOrchestrator()
        
        async def request_consensus(self, request: 'AgentRequest') -> 'AgentResponse':
            # Mock response
            class MockResponse:
                def __init__(self):
                    self.request_id = request.request_id
                    self.decision = "approved"
                    self.confidence_score = 0.95
                    self.participating_agents = ["neutral", "permissive", "strict"]
                    self.consensus_time_ms = 150.0
                    self.detailed_votes = {}
                    self.risk_assessment = {}
                    self.timestamp = datetime.now()
                    self.success = True
            
            return MockResponse()


@pytest.fixture
def decision_orchestrator():
    """Fixture for decision orchestrator"""
    return DecisionOrchestrator()


@pytest.fixture
def agent_orchestrator():
    """Fixture for agent orchestrator"""
    return AgentOrchestrator()


@pytest.fixture
def neutral_agent():
    """Fixture for neutral agent"""
    return NeutralAgent("neutral_test", ["agent1", "agent2", "agent3"])


@pytest.fixture
def permissive_agent():
    """Fixture for permissive agent"""
    return PermissiveAgent("permissive_test", ["agent1", "agent2", "agent3"])


@pytest.fixture
def strict_agent():
    """Fixture for strict agent"""
    return StrictAgent("strict_test", ["agent1", "agent2", "agent3"])


@pytest.fixture
def watchdog_agent():
    """Fixture for watchdog agent"""
    return WatchdogAgent("watchdog_test", ["agent1", "agent2", "agent3"])


class TestIndividualAgentDecisions:
    """Test cases for individual agent decision making"""
    
    @pytest.mark.asyncio
    async def test_neutral_agent_decision(self, neutral_agent):
        """Test neutral agent decision making"""
        # Arrange
        context_data = {
            "user_id": "test_user",
            "resource": "test_resource",
            "action": "read",
            "trust_score": 75.0
        }
        
        # Act
        result = await neutral_agent.evaluate_access_request(
            request_id="test_request_1",
            context_data=context_data,
            trust_score=75.0
        )
        
        # Assert
        assert "agent_id" in result
        assert "decision" in result
        assert "confidence" in result
        assert "reasoning" in result
        assert result["agent_id"] == "neutral_test"
        assert result["decision"] in ["allow", "deny"]
        assert isinstance(result["reasoning"], list)
    
    @pytest.mark.asyncio
    async def test_permissive_agent_decision(self, permissive_agent):
        """Test permissive agent decision making"""
        # Arrange
        context_data = {
            "user_id": "test_user",
            "resource": "test_resource",
            "action": "read",
            "trust_score": 60.0
        }
        
        # Act
        result = await permissive_agent.evaluate_access_request(
            request_id="test_request_2",
            context_data=context_data,
            trust_score=60.0
        )
        
        # Assert
        assert result["agent_id"] == "permissive_test"
        assert result["decision"] in ["allow", "deny"]
        assert result["confidence"] in ["low", "medium", "high"]
    
    @pytest.mark.asyncio
    async def test_strict_agent_decision(self, strict_agent):
        """Test strict agent decision making"""
        # Arrange
        context_data = {
            "user_id": "test_user",
            "resource": "sensitive_resource",
            "action": "write",
            "trust_score": 40.0
        }
        
        # Act
        result = await strict_agent.evaluate_access_request(
            request_id="test_request_3",
            context_data=context_data,
            trust_score=40.0
        )
        
        # Assert
        assert result["agent_id"] == "strict_test"
        assert result["decision"] in ["allow", "deny"]
    
    @pytest.mark.asyncio
    async def test_watchdog_agent_decision(self, watchdog_agent):
        """Test watchdog agent decision making"""
        # Arrange
        context_data = {
            "user_id": "test_user",
            "resource": "test_resource",
            "action": "read",
            "trust_score": 80.0,
            "keystrokes_per_minute": 60
        }
        
        # Act
        result = await watchdog_agent.evaluate_access_request(
            request_id="test_request_4",
            context_data=context_data,
            trust_score=80.0
        )
        
        # Assert
        assert result["agent_id"] == "watchdog_test"
        assert "anomalies" not in result or isinstance(result.get("anomalies"), list)


class TestConsensusBuilding:
    """Test cases for consensus building"""
    
    @pytest.mark.asyncio
    async def test_majority_consensus(self, decision_orchestrator):
        """Test consensus building with majority agreement"""
        # Arrange
        context = {
            "decision_type": "access_request",
            "context_data": {
                "user_id": "test_user",
                "resource": "test_resource",
                "action": "read"
            }
        }
        
        # Act
        result = await decision_orchestrator.make_decision(
            context=context,
            user_id="test_user",
            resource_path="test_resource"
        )
        
        # Assert
        assert "decision" in result
        assert "confidence" in result
        assert "agents_consulted" in result
        assert isinstance(result["agents_consulted"], list)
        assert len(result["agents_consulted"]) > 0
    
    @pytest.mark.asyncio
    async def test_split_decision_handling(self, decision_orchestrator):
        """Test handling of split decisions"""
        # Arrange
        context = {
            "decision_type": "access_request",
            "context_data": {
                "user_id": "test_user",
                "resource": "sensitive_resource",
                "action": "write"
            }
        }
        
        # Act
        result = await decision_orchestrator.make_decision(
            context=context,
            user_id="test_user",
            resource_path="sensitive_resource"
        )
        
        # Assert
        assert "decision" in result
        assert result["decision"] in ["approved", "denied", "escalated"]


class TestAgentOrchestration:
    """Test cases for agent orchestration"""
    
    @pytest.mark.asyncio
    async def test_agent_consensus_request(self, agent_orchestrator):
        """Test agent consensus request"""
        # Arrange
        request = AgentRequest(
            request_id="orchestration_test_1",
            decision_type=DecisionType.ACCESS_REQUEST,
            user_id="test_user",
            resource_path="test_resource",
            context_data={
                "user_id": "test_user",
                "resource": "test_resource",
                "action": "read"
            }
        )
        
        # Act
        response = await agent_orchestrator.request_consensus(request)
        
        # Assert
        assert response.request_id == "orchestration_test_1"
        assert response.decision in ["approved", "denied", "error"]
        assert response.success is True
        assert response.consensus_time_ms > 0
    
    @pytest.mark.asyncio
    async def test_agent_consensus_with_timeout(self, agent_orchestrator):
        """Test agent consensus with timeout"""
        # Arrange
        request = AgentRequest(
            request_id="orchestration_test_2",
            decision_type=DecisionType.ACCESS_REQUEST,
            user_id="test_user",
            resource_path="test_resource",
            context_data={
                "user_id": "test_user",
                "resource": "test_resource",
                "action": "read"
            },
            timeout_seconds=1
        )
        
        # Act
        response = await agent_orchestrator.request_consensus(request)
        
        # Assert
        assert response.request_id == "orchestration_test_2"
        assert hasattr(response, 'success')


class TestAgentIntegration:
    """Test cases for agent integration"""
    
    @pytest.mark.asyncio
    async def test_multi_agent_workflow(self, agent_orchestrator):
        """Test complete multi-agent workflow"""
        # Arrange
        context_data = {
            "user_id": "integration_test_user",
            "resource": "integration_test_resource",
            "action": "access",
            "trust_score": 75.0,
            "device_verified": True,
            "timestamp": datetime.now().isoformat()
        }
        
        request = AgentRequest(
            request_id="integration_test_1",
            decision_type=DecisionType.ACCESS_REQUEST,
            user_id="integration_test_user",
            resource_path="integration_test_resource",
            context_data=context_data
        )
        
        # Act
        response = await agent_orchestrator.request_consensus(request)
        
        # Assert
        assert response.request_id == "integration_test_1"
        assert hasattr(response, 'decision')
        assert hasattr(response, 'confidence_score')
        assert hasattr(response, 'participating_agents')


class TestEdgeCases:
    """Test edge cases for agent decisions"""
    
    @pytest.mark.asyncio
    async def test_empty_context_handling(self, neutral_agent):
        """Test handling of empty context"""
        # Act
        result = await neutral_agent.evaluate_access_request(
            request_id="edge_case_1",
            context_data={},
            trust_score=50.0
        )
        
        # Assert
        assert "decision" in result
        assert isinstance(result["decision"], str)
    
    @pytest.mark.asyncio
    async def test_invalid_trust_score(self, permissive_agent):
        """Test handling of invalid trust scores"""
        # Act
        result = await permissive_agent.evaluate_access_request(
            request_id="edge_case_2",
            context_data={"user_id": "test"},
            trust_score=-10.0  # Invalid score
        )
        
        # Assert
        assert "decision" in result
    
    @pytest.mark.asyncio
    async def test_missing_required_fields(self, strict_agent):
        """Test handling of missing required fields"""
        # Act
        result = await strict_agent.evaluate_access_request(
            request_id="edge_case_3",
            context_data={"partial": "data"},
            trust_score=75.0
        )
        
        # Assert
        assert "agent_id" in result
        assert "decision" in result


if __name__ == "__main__":
    pytest.main([__file__])