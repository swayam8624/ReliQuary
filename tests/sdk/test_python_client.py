"""
Tests for the ReliQuary Python SDK.
This module contains tests for the Python SDK client functionality.
"""

import pytest
import asyncio
from unittest.mock import Mock, patch, AsyncMock

from sdk.python.client import ReliQuaryClient, ReliQuaryAPIClient
from sdk.python.exceptions import ReliQuaryAPIError, ReliQuaryAuthError
from sdk.python.models.api_schemas import (
    ConsensusRequest, ConsensusResult, ConsensusType,
    ZKProofRequest, ZKProofResult
)


class TestReliQuaryAPIClient:
    """Tests for the async ReliQuary API client"""
    
    @pytest.fixture
    def client(self):
        """Create a test client"""
        return ReliQuaryAPIClient(
            base_url="http://localhost:8000",
            api_key="test-api-key"
        )
    
    @pytest.mark.asyncio
    async def test_init(self, client):
        """Test client initialization"""
        assert client.base_url == "http://localhost:8000"
        assert client.api_key == "test-api-key"
        assert client.session is None
    
    @pytest.mark.asyncio
    async def test_connect_disconnect(self, client):
        """Test client connect/disconnect"""
        with patch('aiohttp.ClientSession') as mock_session_class:
            mock_session = AsyncMock()
            mock_session_class.return_value = mock_session
            
            await client.connect()
            assert client.session is not None
            mock_session_class.assert_called_once()
            
            await client.disconnect()
            mock_session.close.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_authentication_with_api_key(self, client):
        """Test authentication with API key"""
        client.api_key = "test-key"
        # Authentication with API key should just set the access token
        await client._authenticate()
        assert client.access_token == "test-key"
    
    @pytest.mark.asyncio
    async def test_authentication_with_username_password(self, client):
        """Test authentication with username/password"""
        client.api_key = None
        client.username = "testuser"
        client.password = "testpass"
        
        mock_response = {"access_token": "mock-token", "expires_in": 3600}
        
        with patch.object(client, '_make_request', return_value=mock_response):
            await client._authenticate()
            assert client.access_token == "mock-token"
    
    @pytest.mark.asyncio
    async def test_make_request_not_connected(self, client):
        """Test making a request when not connected"""
        with pytest.raises(ReliQuaryAPIError, match="Client not connected"):
            await client._make_request("GET", "/test")
    
    @pytest.mark.asyncio
    async def test_health_check(self, client):
        """Test health check"""
        mock_response = {"status": "healthy", "timestamp": "2023-01-01T00:00:00Z"}
        
        with patch.object(client, '_make_request', return_value=mock_response):
            result = await client.health_check()
            assert result == mock_response


class TestReliQuaryClient:
    """Tests for the synchronous ReliQuary client"""
    
    def test_init(self):
        """Test client initialization"""
        client = ReliQuaryClient(
            base_url="http://localhost:8000",
            api_key="test-api-key"
        )
        
        assert client.base_url == "http://localhost:8000"
        assert client.api_key == "test-api-key"
        assert client._async_client is None
    
    @patch('sdk.python.client.asyncio.run')
    def test_context_manager(self, mock_run):
        """Test context manager"""
        mock_async_client = Mock()
        mock_run.side_effect = [
            mock_async_client,  # _create_async_client
            None  # disconnect
        ]
        
        with ReliQuaryClient() as client:
            assert client._async_client == mock_async_client
        
        assert mock_run.call_count == 2


# Integration-style tests for data models
class TestAPISchemas:
    """Tests for API schema data models"""
    
    def test_consensus_request_to_dict(self):
        """Test ConsensusRequest to_dict method"""
        request = ConsensusRequest(
            request_type=ConsensusType.ACCESS_REQUEST,
            context_data={"test": "data"},
            user_id="user123",
            resource_path="/test/resource"
        )
        
        result = request.to_dict()
        assert result["request_type"] == "access_request"
        assert result["context_data"] == {"test": "data"}
        assert result["user_id"] == "user123"
        assert result["resource_path"] == "/test/resource"
    
    def test_consensus_result_from_dict(self):
        """Test ConsensusResult from_dict method"""
        from datetime import datetime
        data = {
            "request_id": "req123",
            "decision": "approved",
            "confidence_score": 0.95,
            "participating_agents": ["agent1", "agent2"],
            "consensus_time_ms": 150.5,
            "detailed_votes": {"agent1": "approve", "agent2": "approve"},
            "risk_assessment": {"risk_level": "low"},
            "timestamp": "2023-01-01T12:00:00",
            "success": True
        }
        
        result = ConsensusResult.from_dict(data)
        assert result.request_id == "req123"
        assert result.decision == "approved"
        assert result.confidence_score == 0.95
        assert isinstance(result.timestamp, datetime)
    
    def test_zk_proof_request_to_dict(self):
        """Test ZKProofRequest to_dict method"""
        request = ZKProofRequest(
            circuit_type="test_circuit",
            inputs={"a": 1, "b": 2},
            public_signals=["signal1", "signal2"]
        )
        
        result = request.to_dict()
        assert result["circuit_type"] == "test_circuit"
        assert result["inputs"] == {"a": 1, "b": 2}
        assert result["public_signals"] == ["signal1", "signal2"]


if __name__ == "__main__":
    pytest.main([__file__])