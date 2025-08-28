"""
ReliQuary Enterprise Python SDK

This SDK provides a comprehensive Python client for integrating with
the ReliQuary multi-agent consensus and security platform.

Features:
- Authentication and authorization
- Multi-agent consensus operations  
- Zero-knowledge proof generation
- Cross-chain interactions
- AI/ML enhanced decisions
- Observability and monitoring
- Enterprise security controls
"""

import asyncio
import aiohttp
import json
import logging
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, asdict
from enum import Enum
import uuid


class ConsensusType(Enum):
    """Types of consensus operations"""
    ACCESS_REQUEST = "access_request"
    GOVERNANCE_DECISION = "governance_decision"
    EMERGENCY_RESPONSE = "emergency_response"
    SECURITY_VALIDATION = "security_validation"


class DecisionStrategy(Enum):
    """AI/ML decision optimization strategies"""
    CONSERVATIVE = "conservative"
    BALANCED = "balanced"
    AGGRESSIVE = "aggressive"
    ADAPTIVE = "adaptive"


@dataclass
class AuthCredentials:
    """Authentication credentials"""
    username: Optional[str] = None
    password: Optional[str] = None
    api_key: Optional[str] = None
    access_token: Optional[str] = None
    did_private_key: Optional[str] = None


@dataclass
class ConsensusRequest:
    """Multi-agent consensus request"""
    request_type: ConsensusType
    context_data: Dict[str, Any]
    user_id: str
    resource_path: str
    priority: int = 5
    timeout_seconds: int = 30
    required_agents: Optional[List[str]] = None
    metadata: Optional[Dict[str, Any]] = None


@dataclass
class ConsensusResult:
    """Multi-agent consensus result"""
    request_id: str
    decision: str
    confidence_score: float
    participating_agents: List[str]
    consensus_time_ms: float
    detailed_votes: Dict[str, Any]
    risk_assessment: Dict[str, Any]
    timestamp: datetime
    success: bool


@dataclass
class ZKProofRequest:
    """Zero-knowledge proof generation request"""
    circuit_type: str
    inputs: Dict[str, Any]
    public_signals: List[str]
    metadata: Optional[Dict[str, Any]] = None


@dataclass
class ZKProofResult:
    """Zero-knowledge proof result"""
    proof_id: str
    proof: Dict[str, Any]
    public_signals: List[str]
    verification_key: Dict[str, Any]
    circuit_type: str
    generation_time_ms: float
    valid: bool
    timestamp: datetime


class ReliQuaryClient:
    """Enterprise ReliQuary Python SDK Client"""
    
    def __init__(self, 
                 base_url: str = "http://localhost:8000",
                 credentials: Optional[AuthCredentials] = None,
                 timeout: int = 30,
                 max_retries: int = 3):
        """
        Initialize ReliQuary client
        
        Args:
            base_url: ReliQuary API base URL
            credentials: Authentication credentials
            timeout: Request timeout in seconds
            max_retries: Maximum number of retries for failed requests
        """
        self.base_url = base_url.rstrip('/')
        self.credentials = credentials or AuthCredentials()
        self.timeout = timeout
        self.max_retries = max_retries
        
        self.session = None
        self.access_token = None
        self.token_expires = None
        
        self.logger = logging.getLogger("reliquary_client")
        
        # Performance tracking
        self.request_count = 0
        self.total_response_time = 0.0
        self.error_count = 0
    
    async def __aenter__(self):
        """Async context manager entry"""
        await self.connect()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        await self.disconnect()
    
    async def connect(self):
        """Establish connection and authenticate"""
        self.session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=self.timeout)
        )
        
        if self.credentials.access_token:
            self.access_token = self.credentials.access_token
        else:
            await self._authenticate()
        
        self.logger.info("Connected to ReliQuary platform")
    
    async def disconnect(self):
        """Close connection"""
        if self.session:
            await self.session.close()
        self.logger.info("Disconnected from ReliQuary platform")
    
    async def _authenticate(self):
        """Perform authentication"""
        if self.credentials.api_key:
            # API key authentication
            self.access_token = self.credentials.api_key
        elif self.credentials.username and self.credentials.password:
            # Username/password authentication
            auth_data = {
                "username": self.credentials.username,
                "password": self.credentials.password
            }
            
            response = await self._make_request("POST", "/auth/login", json=auth_data)
            self.access_token = response["access_token"]
            
            # Calculate token expiration
            expires_in = response.get("expires_in", 3600)
            self.token_expires = datetime.now() + timedelta(seconds=expires_in)
        elif self.credentials.did_private_key:
            # DID-based authentication
            # This would implement DID authentication flow
            pass
        else:
            raise ValueError("No valid authentication credentials provided")
    
    async def _get_headers(self) -> Dict[str, str]:
        """Get request headers with authentication"""
        headers = {
            "Content-Type": "application/json",
            "User-Agent": "ReliQuary-Python-SDK/1.0.0"
        }
        
        if self.access_token:
            headers["Authorization"] = f"Bearer {self.access_token}"
        
        return headers
    
    async def _make_request(self, method: str, endpoint: str, **kwargs) -> Dict[str, Any]:
        """Make authenticated API request with retries"""
        url = f"{self.base_url}{endpoint}"
        headers = await self._get_headers()
        
        for attempt in range(self.max_retries + 1):
            try:
                start_time = time.time()
                
                async with self.session.request(
                    method, url, headers=headers, **kwargs
                ) as response:
                    response_time = time.time() - start_time
                    self.request_count += 1
                    self.total_response_time += response_time
                    
                    if response.status == 401 and attempt == 0:
                        # Token might be expired, retry authentication
                        await self._authenticate()
                        headers = await self._get_headers()
                        continue
                    
                    response.raise_for_status()
                    result = await response.json()
                    
                    self.logger.debug(f"{method} {endpoint} -> {response.status} ({response_time:.3f}s)")
                    return result
                    
            except Exception as e:
                self.error_count += 1
                self.logger.warning(f"Request attempt {attempt + 1} failed: {e}")
                
                if attempt == self.max_retries:
                    raise
                
                # Exponential backoff
                await asyncio.sleep(2 ** attempt)
    
    # Health and Status Methods
    
    async def health_check(self) -> Dict[str, Any]:
        """Check system health"""
        return await self._make_request("GET", "/health")
    
    async def get_system_status(self) -> Dict[str, Any]:
        """Get comprehensive system status"""
        return await self._make_request("GET", "/status")
    
    # Authentication Methods
    
    async def refresh_token(self) -> str:
        """Refresh authentication token"""
        response = await self._make_request("POST", "/auth/refresh")
        self.access_token = response["access_token"]
        return self.access_token
    
    async def get_user_profile(self) -> Dict[str, Any]:
        """Get current user profile"""
        return await self._make_request("GET", "/auth/profile")
    
    # Multi-Agent Consensus Methods
    
    async def submit_consensus_request(self, request: ConsensusRequest) -> ConsensusResult:
        """Submit request for multi-agent consensus"""
        request_data = {
            "request_type": request.request_type.value,
            "context_data": request.context_data,
            "user_id": request.user_id,
            "resource_path": request.resource_path,
            "priority": request.priority,
            "timeout_seconds": request.timeout_seconds,
            "required_agents": request.required_agents,
            "metadata": request.metadata or {}
        }
        
        response = await self._make_request("POST", "/consensus/submit", json=request_data)
        
        return ConsensusResult(
            request_id=response["request_id"],
            decision=response["decision"],
            confidence_score=response["confidence_score"],
            participating_agents=response["participating_agents"],
            consensus_time_ms=response["consensus_time_ms"],
            detailed_votes=response["detailed_votes"],
            risk_assessment=response["risk_assessment"],
            timestamp=datetime.fromisoformat(response["timestamp"]),
            success=response["success"]
        )
    
    async def get_consensus_result(self, request_id: str) -> ConsensusResult:
        """Get consensus result by request ID"""
        response = await self._make_request("GET", f"/consensus/result/{request_id}")
        
        return ConsensusResult(
            request_id=response["request_id"],
            decision=response["decision"],
            confidence_score=response["confidence_score"],
            participating_agents=response["participating_agents"],
            consensus_time_ms=response["consensus_time_ms"],
            detailed_votes=response["detailed_votes"],
            risk_assessment=response["risk_assessment"],
            timestamp=datetime.fromisoformat(response["timestamp"]),
            success=response["success"]
        )
    
    async def list_active_consensus(self) -> List[Dict[str, Any]]:
        """List active consensus operations"""
        response = await self._make_request("GET", "/consensus/active")
        return response["active_consensus"]
    
    # Zero-Knowledge Proof Methods
    
    async def generate_zk_proof(self, request: ZKProofRequest) -> ZKProofResult:
        """Generate zero-knowledge proof"""
        request_data = {
            "circuit_type": request.circuit_type,
            "inputs": request.inputs,
            "public_signals": request.public_signals,
            "metadata": request.metadata or {}
        }
        
        response = await self._make_request("POST", "/zk/generate", json=request_data)
        
        return ZKProofResult(
            proof_id=response["proof_id"],
            proof=response["proof"],
            public_signals=response["public_signals"],
            verification_key=response["verification_key"],
            circuit_type=response["circuit_type"],
            generation_time_ms=response["generation_time_ms"],
            valid=response["valid"],
            timestamp=datetime.fromisoformat(response["timestamp"])
        )
    
    async def verify_zk_proof(self, proof_id: str, proof: Dict[str, Any], 
                            public_signals: List[str]) -> bool:
        """Verify zero-knowledge proof"""
        request_data = {
            "proof_id": proof_id,
            "proof": proof,
            "public_signals": public_signals
        }
        
        response = await self._make_request("POST", "/zk/verify", json=request_data)
        return response["valid"]
    
    # AI/ML Enhanced Decision Methods
    
    async def get_ai_enhanced_decision(self, 
                                     decision_type: str,
                                     user_data: Dict[str, Any],
                                     context_data: Dict[str, Any],
                                     strategy: DecisionStrategy = DecisionStrategy.BALANCED) -> Dict[str, Any]:
        """Get AI/ML enhanced decision"""
        request_data = {
            "decision_type": decision_type,
            "user_data": user_data,
            "context_data": context_data,
            "optimization_strategy": strategy.value
        }
        
        return await self._make_request("POST", "/ai-ml/decisions/enhance", json=request_data)
    
    async def analyze_behavioral_patterns(self, 
                                        user_id: str,
                                        time_range_hours: int = 24) -> Dict[str, Any]:
        """Analyze user behavioral patterns"""
        params = {
            "user_id": user_id,
            "time_range_hours": time_range_hours
        }
        
        return await self._make_request("GET", "/ai-ml/analytics/patterns", params=params)
    
    # Cross-Chain Methods
    
    async def submit_cross_chain_transaction(self, 
                                           source_chain: str,
                                           target_chain: str,
                                           transaction_data: Dict[str, Any]) -> Dict[str, Any]:
        """Submit cross-chain transaction"""
        request_data = {
            "source_chain": source_chain,
            "target_chain": target_chain,
            "transaction_data": transaction_data
        }
        
        return await self._make_request("POST", "/crosschain/submit", json=request_data)
    
    async def get_cross_chain_status(self, transaction_id: str) -> Dict[str, Any]:
        """Get cross-chain transaction status"""
        return await self._make_request("GET", f"/crosschain/status/{transaction_id}")
    
    # Observability Methods
    
    async def record_metric(self, name: str, value: float, 
                          labels: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
        """Record custom metric"""
        request_data = {
            "name": name,
            "value": value,
            "labels": labels or {}
        }
        
        return await self._make_request("POST", "/observability/metrics/record", json=request_data)
    
    async def get_system_dashboard(self) -> Dict[str, Any]:
        """Get system dashboard data"""
        return await self._make_request("GET", "/observability/dashboard")
    
    async def trigger_alert(self, metric_name: str, value: float, 
                          description: str = "SDK triggered alert") -> Dict[str, Any]:
        """Manually trigger an alert"""
        request_data = {
            "metric_name": metric_name,
            "value": value,
            "description": description
        }
        
        return await self._make_request("POST", "/observability/alerts/trigger", json=request_data)
    
    # Vault and Secret Management Methods
    
    async def store_secret(self, vault_id: str, secret_name: str, 
                         secret_value: str, metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Store secret in vault"""
        request_data = {
            "vault_id": vault_id,
            "secret_name": secret_name,
            "secret_value": secret_value,
            "metadata": metadata or {}
        }
        
        return await self._make_request("POST", "/vaults/secrets", json=request_data)
    
    async def retrieve_secret(self, vault_id: str, secret_name: str) -> Dict[str, Any]:
        """Retrieve secret from vault"""
        params = {
            "vault_id": vault_id,
            "secret_name": secret_name
        }
        
        return await self._make_request("GET", "/vaults/secrets", params=params)
    
    # Performance and Statistics
    
    def get_client_stats(self) -> Dict[str, Any]:
        """Get client performance statistics"""
        avg_response_time = self.total_response_time / max(self.request_count, 1)
        error_rate = self.error_count / max(self.request_count, 1) * 100
        
        return {
            "total_requests": self.request_count,
            "average_response_time_ms": avg_response_time * 1000,
            "error_count": self.error_count,
            "error_rate_percent": error_rate,
            "base_url": self.base_url,
            "authenticated": bool(self.access_token)
        }


# Convenience functions for common operations

async def create_client(base_url: str = "http://localhost:8000",
                       api_key: Optional[str] = None,
                       username: Optional[str] = None,
                       password: Optional[str] = None) -> ReliQuaryClient:
    """Create and connect ReliQuary client"""
    credentials = AuthCredentials(
        api_key=api_key,
        username=username,
        password=password
    )
    
    client = ReliQuaryClient(base_url=base_url, credentials=credentials)
    await client.connect()
    return client


async def quick_consensus(base_url: str, api_key: str, 
                        request_type: ConsensusType,
                        context_data: Dict[str, Any],
                        user_id: str,
                        resource_path: str) -> ConsensusResult:
    """Quick consensus operation"""
    async with create_client(base_url, api_key=api_key) as client:
        request = ConsensusRequest(
            request_type=request_type,
            context_data=context_data,
            user_id=user_id,
            resource_path=resource_path
        )
        return await client.submit_consensus_request(request)


async def quick_ai_decision(base_url: str, api_key: str,
                          decision_type: str,
                          user_data: Dict[str, Any],
                          context_data: Dict[str, Any]) -> Dict[str, Any]:
    """Quick AI-enhanced decision"""
    async with create_client(base_url, api_key=api_key) as client:
        return await client.get_ai_enhanced_decision(
            decision_type, user_data, context_data
        )


# Example usage
if __name__ == "__main__":
    async def main():
        # Example usage of the SDK
        credentials = AuthCredentials(api_key="your-api-key")
        
        async with ReliQuaryClient("http://localhost:8000", credentials) as client:
            # Health check
            health = await client.health_check()
            print(f"System health: {health}")
            
            # Submit consensus request
            request = ConsensusRequest(
                request_type=ConsensusType.ACCESS_REQUEST,
                context_data={"resource_sensitivity": "high"},
                user_id="user123",
                resource_path="/secure/data"
            )
            
            result = await client.submit_consensus_request(request)
            print(f"Consensus decision: {result.decision}")
            
            # Record metric
            await client.record_metric("sdk_usage", 1.0, {"operation": "consensus"})
            
            # Get client statistics
            stats = client.get_client_stats()
            print(f"Client stats: {stats}")
    
    asyncio.run(main())