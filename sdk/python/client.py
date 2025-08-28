"""
Core Python client for the ReliQuary API.
This module provides the main client interface for interacting with the ReliQuary platform.
"""

import asyncio
import aiohttp
import json
import logging
from typing import Dict, List, Optional, Any, Union
from datetime import datetime

from .exceptions import ReliQuaryAPIError, ReliQuaryAuthError
from .models.api_schemas import (
    ConsensusRequest, ConsensusResult, 
    ZKProofRequest, ZKProofResult,
    VaultMetadata, SecretData
)


class ReliQuaryAPIClient:
    """Main client for interacting with the ReliQuary API"""
    
    def __init__(self, 
                 base_url: str = "http://localhost:8000",
                 api_key: Optional[str] = None,
                 username: Optional[str] = None,
                 password: Optional[str] = None,
                 timeout: int = 30):
        """
        Initialize the ReliQuary API client.
        
        Args:
            base_url: Base URL for the ReliQuary API
            api_key: API key for authentication
            username: Username for authentication
            password: Password for authentication
            timeout: Request timeout in seconds
        """
        self.base_url = base_url.rstrip('/')
        self.api_key = api_key
        self.username = username
        self.password = password
        self.timeout = timeout
        self.access_token = None
        self.session = None
        self.logger = logging.getLogger(__name__)
    
    async def __aenter__(self):
        """Async context manager entry"""
        await self.connect()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        await self.disconnect()
    
    async def connect(self):
        """Establish connection and authenticate"""
        if self.session is None:
            self.session = aiohttp.ClientSession(
                timeout=aiohttp.ClientTimeout(total=self.timeout)
            )
        
        if self.api_key or (self.username and self.password):
            await self._authenticate()
    
    async def disconnect(self):
        """Close the connection"""
        if self.session:
            await self.session.close()
            self.session = None
    
    async def _authenticate(self):
        """Authenticate with the API"""
        if self.api_key:
            # API key authentication
            self.access_token = self.api_key
        elif self.username and self.password:
            # Username/password authentication
            auth_data = {
                "username": self.username,
                "password": self.password
            }
            
            try:
                response = await self._make_request("POST", "/auth/login", json=auth_data)
                self.access_token = response.get("access_token")
            except Exception as e:
                raise ReliQuaryAuthError(f"Authentication failed: {str(e)}")
    
    async def _get_headers(self) -> Dict[str, str]:
        """Get headers for API requests"""
        headers = {
            "Content-Type": "application/json",
            "User-Agent": "ReliQuary-Python-SDK/1.0.0"
        }
        
        if self.access_token:
            headers["Authorization"] = f"Bearer {self.access_token}"
        
        return headers
    
    async def _make_request(self, method: str, endpoint: str, **kwargs) -> Dict[str, Any]:
        """Make an authenticated request to the API"""
        if not self.session:
            raise ReliQuaryAPIError("Client not connected. Call connect() first.")
        
        url = f"{self.base_url}{endpoint}"
        headers = await self._get_headers()
        
        try:
            async with self.session.request(method, url, headers=headers, **kwargs) as response:
                if response.status >= 400:
                    error_text = await response.text()
                    if response.status == 401:
                        raise ReliQuaryAuthError(f"Authentication failed: {error_text}")
                    else:
                        raise ReliQuaryAPIError(f"API request failed with status {response.status}: {error_text}")
                
                if response.status == 204:  # No content
                    return {}
                
                return await response.json()
        except aiohttp.ClientError as e:
            raise ReliQuaryAPIError(f"Network error: {str(e)}")
    
    # Health check methods
    async def health_check(self) -> Dict[str, Any]:
        """Check the health of the ReliQuary service"""
        return await self._make_request("GET", "/health")
    
    # Consensus methods
    async def submit_consensus_request(self, request: ConsensusRequest) -> ConsensusResult:
        """Submit a consensus request to the multi-agent system"""
        response = await self._make_request("POST", "/consensus/submit", json=request.to_dict())
        return ConsensusResult.from_dict(response)
    
    async def get_consensus_result(self, request_id: str) -> ConsensusResult:
        """Get the result of a consensus request"""
        response = await self._make_request("GET", f"/consensus/result/{request_id}")
        return ConsensusResult.from_dict(response)
    
    # Zero-knowledge proof methods
    async def generate_zk_proof(self, request: ZKProofRequest) -> ZKProofResult:
        """Generate a zero-knowledge proof"""
        response = await self._make_request("POST", "/zk/generate", json=request.to_dict())
        return ZKProofResult.from_dict(response)
    
    async def verify_zk_proof(self, proof: ZKProofResult) -> bool:
        """Verify a zero-knowledge proof"""
        request_data = {
            "proof": proof.proof,
            "public_signals": proof.public_signals
        }
        response = await self._make_request("POST", "/zk/verify", json=request_data)
        return response.get("valid", False)
    
    # Vault methods
    async def create_vault(self, name: str, description: str = "") -> VaultMetadata:
        """Create a new vault"""
        request_data = {
            "name": name,
            "description": description
        }
        response = await self._make_request("POST", "/vaults", json=request_data)
        return VaultMetadata.from_dict(response)
    
    async def get_vault(self, vault_id: str) -> VaultMetadata:
        """Get vault metadata"""
        response = await self._make_request("GET", f"/vaults/{vault_id}")
        return VaultMetadata.from_dict(response)
    
    async def list_vaults(self) -> List[VaultMetadata]:
        """List all vaults"""
        response = await self._make_request("GET", "/vaults")
        return [VaultMetadata.from_dict(vault_data) for vault_data in response.get("vaults", [])]
    
    async def store_secret(self, vault_id: str, secret_name: str, secret_value: str, 
                          metadata: Optional[Dict[str, Any]] = None) -> SecretData:
        """Store a secret in a vault"""
        request_data = {
            "vault_id": vault_id,
            "secret_name": secret_name,
            "secret_value": secret_value,
            "metadata": metadata or {}
        }
        response = await self._make_request("POST", "/vaults/secrets", json=request_data)
        return SecretData.from_dict(response)
    
    async def retrieve_secret(self, vault_id: str, secret_name: str) -> SecretData:
        """Retrieve a secret from a vault"""
        params = {"vault_id": vault_id, "secret_name": secret_name}
        response = await self._make_request("GET", "/vaults/secrets", params=params)
        return SecretData.from_dict(response)


# Synchronous client wrapper
class ReliQuaryClient:
    """Synchronous wrapper for the ReliQuary API client"""
    
    def __init__(self, 
                 base_url: str = "http://localhost:8000",
                 api_key: Optional[str] = None,
                 username: Optional[str] = None,
                 password: Optional[str] = None,
                 timeout: int = 30):
        """
        Initialize the synchronous ReliQuary client.
        
        Args:
            base_url: Base URL for the ReliQuary API
            api_key: API key for authentication
            username: Username for authentication
            password: Password for authentication
            timeout: Request timeout in seconds
        """
        self.base_url = base_url
        self.api_key = api_key
        self.username = username
        self.password = password
        self.timeout = timeout
        self._async_client = None
    
    def __enter__(self):
        """Context manager entry"""
        self._async_client = asyncio.run(self._create_async_client())
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        if self._async_client:
            asyncio.run(self._async_client.disconnect())
    
    async def _create_async_client(self):
        """Create the underlying async client"""
        client = ReliQuaryAPIClient(
            base_url=self.base_url,
            api_key=self.api_key,
            username=self.username,
            password=self.password,
            timeout=self.timeout
        )
        await client.connect()
        return client
    
    # Health check methods
    def health_check(self) -> Dict[str, Any]:
        """Check the health of the ReliQuary service"""
        return asyncio.run(self._async_client.health_check())
    
    # Consensus methods
    def submit_consensus_request(self, request: ConsensusRequest) -> ConsensusResult:
        """Submit a consensus request to the multi-agent system"""
        return asyncio.run(self._async_client.submit_consensus_request(request))
    
    def get_consensus_result(self, request_id: str) -> ConsensusResult:
        """Get the result of a consensus request"""
        return asyncio.run(self._async_client.get_consensus_result(request_id))
    
    # Zero-knowledge proof methods
    def generate_zk_proof(self, request: ZKProofRequest) -> ZKProofResult:
        """Generate a zero-knowledge proof"""
        return asyncio.run(self._async_client.generate_zk_proof(request))
    
    def verify_zk_proof(self, proof: ZKProofResult) -> bool:
        """Verify a zero-knowledge proof"""
        return asyncio.run(self._async_client.verify_zk_proof(proof))
    
    # Vault methods
    def create_vault(self, name: str, description: str = "") -> VaultMetadata:
        """Create a new vault"""
        return asyncio.run(self._async_client.create_vault(name, description))
    
    def get_vault(self, vault_id: str) -> VaultMetadata:
        """Get vault metadata"""
        return asyncio.run(self._async_client.get_vault(vault_id))
    
    def list_vaults(self) -> List[VaultMetadata]:
        """List all vaults"""
        return asyncio.run(self._async_client.list_vaults())
    
    def store_secret(self, vault_id: str, secret_name: str, secret_value: str, 
                    metadata: Optional[Dict[str, Any]] = None) -> SecretData:
        """Store a secret in a vault"""
        return asyncio.run(self._async_client.store_secret(vault_id, secret_name, secret_value, metadata))
    
    def retrieve_secret(self, vault_id: str, secret_name: str) -> SecretData:
        """Retrieve a secret from a vault"""
        return asyncio.run(self._async_client.retrieve_secret(vault_id, secret_name))