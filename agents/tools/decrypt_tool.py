"""
Decrypt Tool for ReliQuary Multi-Agent System

This tool coordinates decryption operations with multi-party consent,
threshold cryptography, and secure key management. It ensures that
decryption only occurs when proper authorization and consensus is achieved.
"""

import logging
import time
import hashlib
import json
import secrets
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
from pathlib import Path

# Import cryptographic components
from core.crypto.rust_ffi_wrappers import (
    encrypt_data_rust as encrypt_data,
    decrypt_data_rust as decrypt_data,
    generate_keypair_rust as generate_keypair,
    derive_key_rust as derive_key
)
from agents.consensus import ThresholdCryptography


class DecryptionStatus(Enum):
    """Status of decryption operation"""
    AUTHORIZED = "authorized"
    UNAUTHORIZED = "unauthorized"
    PENDING_CONSENSUS = "pending_consensus"
    INSUFFICIENT_SHARES = "insufficient_shares"
    ERROR = "error"
    TIMEOUT = "timeout"


class AuthorizationLevel(Enum):
    """Levels of authorization required for decryption"""
    SINGLE_AGENT = "single_agent"
    MAJORITY_CONSENSUS = "majority_consensus"
    UNANIMOUS_CONSENSUS = "unanimous_consensus"
    THRESHOLD_SHARES = "threshold_shares"
    ADMINISTRATIVE = "administrative"


@dataclass
class DecryptionRequest:
    """Request for decryption operation"""
    request_id: str
    requester_id: str
    vault_id: str
    data_identifier: str
    authorization_level: AuthorizationLevel
    justification: str
    emergency: bool = False
    expiration_time: Optional[float] = None
    required_agents: Optional[List[str]] = None


@dataclass
class DecryptionResponse:
    """Response from decryption operation"""
    request_id: str
    status: DecryptionStatus
    success: bool
    decrypted_data: Optional[bytes] = None
    error_message: Optional[str] = None
    authorization_details: Dict[str, Any] = None
    consensus_details: Dict[str, Any] = None
    processing_time: float = 0.0
    audit_trail: List[str] = None
    
    def __post_init__(self):
        if self.authorization_details is None:
            self.authorization_details = {}
        if self.consensus_details is None:
            self.consensus_details = {}
        if self.audit_trail is None:
            self.audit_trail = []


@dataclass
class AuthorizationVote:
    """Vote from an agent for decryption authorization"""
    agent_id: str
    vote: bool
    confidence: float
    reasoning: str
    timestamp: float
    signature: Optional[str] = None


class DecryptTool:
    """
    Decrypt Tool for coordinated decryption operations.
    
    This tool manages secure decryption with multi-party authorization,
    threshold cryptography, and comprehensive audit logging. It ensures
    that sensitive data is only decrypted when proper consensus is achieved.
    """
    
    def __init__(self, agent_id: str, vault_path: str = None):
        """Initialize the decrypt tool."""
        self.agent_id = agent_id
        self.vault_path = Path(vault_path) if vault_path else Path("vaults")
        self.vault_path.mkdir(exist_ok=True)
        
        self.logger = logging.getLogger(f"decrypt_tool.{agent_id}")
        
        # Initialize threshold cryptography
        self.threshold_crypto = ThresholdCryptography(threshold=2, total_parties=4)
        
        # Active decryption requests
        self.active_requests: Dict[str, DecryptionRequest] = {}
        self.pending_votes: Dict[str, List[AuthorizationVote]] = {}
        self.authorization_cache: Dict[str, Dict[str, Any]] = {}
        
        # Authorization thresholds
        self.authorization_thresholds = {
            AuthorizationLevel.SINGLE_AGENT: 1,
            AuthorizationLevel.MAJORITY_CONSENSUS: 3,
            AuthorizationLevel.UNANIMOUS_CONSENSUS: 4,
            AuthorizationLevel.THRESHOLD_SHARES: 2,
            AuthorizationLevel.ADMINISTRATIVE: 1
        }
        
        # Performance metrics
        self.total_requests = 0
        self.successful_decryptions = 0
        self.failed_decryptions = 0
        self.unauthorized_attempts = 0
        
        # Security settings
        self.max_request_lifetime = 300  # 5 minutes
        self.emergency_override_enabled = True
        self.audit_all_operations = True
    
    async def request_decryption(self, 
                               vault_id: str,
                               data_identifier: str,
                               requester_id: str,
                               justification: str,
                               authorization_level: str = "majority_consensus",
                               emergency: bool = False,
                               required_agents: List[str] = None) -> DecryptionResponse:
        """
        Request decryption of encrypted data.
        
        Args:
            vault_id: Identifier of the vault containing the data
            data_identifier: Identifier of the specific data to decrypt
            requester_id: ID of the entity requesting decryption
            justification: Justification for the decryption request
            authorization_level: Level of authorization required
            emergency: Whether this is an emergency request
            required_agents: Specific agents required for authorization
            
        Returns:
            DecryptionResponse with operation result
        """
        start_time = time.time()
        self.total_requests += 1
        
        try:
            # Parse authorization level
            try:
                auth_level = AuthorizationLevel[authorization_level.upper()]
            except KeyError:
                auth_level = AuthorizationLevel.MAJORITY_CONSENSUS
            
            # Create request
            request_id = self._generate_request_id()
            request = DecryptionRequest(
                request_id=request_id,
                requester_id=requester_id,
                vault_id=vault_id,
                data_identifier=data_identifier,
                authorization_level=auth_level,
                justification=justification,
                emergency=emergency,
                expiration_time=time.time() + self.max_request_lifetime,
                required_agents=required_agents
            )
            
            # Store active request
            self.active_requests[request_id] = request
            self.pending_votes[request_id] = []
            
            # Log the request
            audit_entry = f"Decryption requested by {requester_id} for {vault_id}:{data_identifier}"
            
            # Check if immediate authorization is possible
            if auth_level == AuthorizationLevel.SINGLE_AGENT:
                # Single agent can authorize immediately
                result = await self._perform_decryption(request)
                processing_time = time.time() - start_time
                result.processing_time = processing_time
                result.audit_trail.append(audit_entry)
                return result
            
            elif emergency and self.emergency_override_enabled:
                # Emergency override
                result = await self._emergency_decryption(request)
                processing_time = time.time() - start_time
                result.processing_time = processing_time
                result.audit_trail.append(audit_entry)
                result.audit_trail.append("Emergency override applied")
                return result
            
            else:
                # Multi-party authorization required
                return await self._initiate_consensus(request, audit_entry)
        
        except Exception as e:
            self.logger.error(f"Decryption request failed: {e}")
            self.failed_decryptions += 1
            
            processing_time = time.time() - start_time
            return DecryptionResponse(
                request_id="error",
                status=DecryptionStatus.ERROR,
                success=False,
                error_message=str(e),
                processing_time=processing_time,
                audit_trail=[f"Decryption request error: {str(e)}"]
            )
    
    async def vote_on_decryption(self, 
                               request_id: str,
                               agent_id: str,
                               approve: bool,
                               confidence: float,
                               reasoning: str) -> Dict[str, Any]:
        """
        Vote on a pending decryption request.
        
        Args:
            request_id: ID of the decryption request
            agent_id: ID of the voting agent
            approve: Whether to approve the decryption
            confidence: Confidence level in the vote (0.0 to 1.0)
            reasoning: Reasoning for the vote
            
        Returns:
            Vote processing result
        """
        try:
            if request_id not in self.active_requests:
                return {
                    "success": False,
                    "error": "Request not found or expired"
                }
            
            request = self.active_requests[request_id]
            
            # Check if request has expired
            if request.expiration_time and time.time() > request.expiration_time:
                self._cleanup_expired_request(request_id)
                return {
                    "success": False,
                    "error": "Request has expired"
                }
            
            # Check if agent is required/allowed to vote
            if request.required_agents and agent_id not in request.required_agents:
                return {
                    "success": False,
                    "error": "Agent not authorized to vote on this request"
                }
            
            # Check if agent has already voted
            existing_vote = next(
                (vote for vote in self.pending_votes[request_id] if vote.agent_id == agent_id),
                None
            )
            
            if existing_vote:
                return {
                    "success": False,
                    "error": "Agent has already voted on this request"
                }
            
            # Create vote
            vote = AuthorizationVote(
                agent_id=agent_id,
                vote=approve,
                confidence=confidence,
                reasoning=reasoning,
                timestamp=time.time(),
                signature=self._sign_vote(request_id, agent_id, approve)
            )
            
            # Add vote to pending votes
            self.pending_votes[request_id].append(vote)
            
            # Check if consensus is reached
            consensus_result = self._check_consensus(request_id)
            
            if consensus_result["consensus_reached"]:
                # Perform decryption if approved
                if consensus_result["approved"]:
                    decryption_result = await self._perform_decryption(request)
                    
                    # Clean up request
                    self._cleanup_request(request_id)
                    
                    return {
                        "success": True,
                        "consensus_reached": True,
                        "approved": True,
                        "decryption_result": decryption_result.__dict__
                    }
                else:
                    # Consensus to deny
                    self._cleanup_request(request_id)
                    self.unauthorized_attempts += 1
                    
                    return {
                        "success": True,
                        "consensus_reached": True,
                        "approved": False,
                        "reason": "Consensus denied decryption request"
                    }
            else:
                return {
                    "success": True,
                    "consensus_reached": False,
                    "votes_received": len(self.pending_votes[request_id]),
                    "votes_needed": self.authorization_thresholds[request.authorization_level]
                }
        
        except Exception as e:
            self.logger.error(f"Vote processing failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def _initiate_consensus(self, request: DecryptionRequest, audit_entry: str) -> DecryptionResponse:
        """Initiate consensus process for decryption authorization."""
        return DecryptionResponse(
            request_id=request.request_id,
            status=DecryptionStatus.PENDING_CONSENSUS,
            success=False,
            authorization_details={
                "required_level": request.authorization_level.value,
                "required_votes": self.authorization_thresholds[request.authorization_level],
                "current_votes": 0,
                "expiration_time": request.expiration_time
            },
            consensus_details={
                "initiated": True,
                "required_agents": request.required_agents,
                "emergency": request.emergency
            },
            audit_trail=[audit_entry, "Consensus process initiated"]
        )
    
    async def _perform_decryption(self, request: DecryptionRequest) -> DecryptionResponse:
        """Perform the actual decryption operation."""
        try:
            # Load encrypted data from vault
            encrypted_data = self._load_encrypted_data(request.vault_id, request.data_identifier)
            
            if encrypted_data is None:
                return DecryptionResponse(
                    request_id=request.request_id,
                    status=DecryptionStatus.ERROR,
                    success=False,
                    error_message="Encrypted data not found",
                    audit_trail=["Data not found in vault"]
                )
            
            # Decrypt data using Rust FFI
            decrypted_data = decrypt_data(encrypted_data["data"], encrypted_data["key"])
            
            if decrypted_data is None:
                return DecryptionResponse(
                    request_id=request.request_id,
                    status=DecryptionStatus.ERROR,
                    success=False,
                    error_message="Decryption failed",
                    audit_trail=["Cryptographic decryption failed"]
                )
            
            self.successful_decryptions += 1
            
            return DecryptionResponse(
                request_id=request.request_id,
                status=DecryptionStatus.AUTHORIZED,
                success=True,
                decrypted_data=decrypted_data,
                authorization_details={
                    "authorized_by": request.requester_id,
                    "authorization_level": request.authorization_level.value,
                    "justification": request.justification
                },
                audit_trail=[
                    f"Decryption authorized for {request.vault_id}:{request.data_identifier}",
                    f"Data decrypted successfully"
                ]
            )
        
        except Exception as e:
            self.logger.error(f"Decryption operation failed: {e}")
            self.failed_decryptions += 1
            
            return DecryptionResponse(
                request_id=request.request_id,
                status=DecryptionStatus.ERROR,
                success=False,
                error_message=str(e),
                audit_trail=[f"Decryption operation error: {str(e)}"]
            )
    
    async def _emergency_decryption(self, request: DecryptionRequest) -> DecryptionResponse:
        """Perform emergency decryption with reduced authorization requirements."""
        self.logger.warning(f"Emergency decryption requested: {request.request_id}")
        
        # Perform emergency validation
        if not self._validate_emergency_request(request):
            self.unauthorized_attempts += 1
            return DecryptionResponse(
                request_id=request.request_id,
                status=DecryptionStatus.UNAUTHORIZED,
                success=False,
                error_message="Emergency request validation failed",
                audit_trail=["Emergency validation failed"]
            )
        
        # Proceed with decryption
        result = await self._perform_decryption(request)
        result.authorization_details["emergency_override"] = True
        result.audit_trail.append("Emergency decryption performed")
        
        return result
    
    def _validate_emergency_request(self, request: DecryptionRequest) -> bool:
        """Validate emergency decryption request."""
        # Simplified emergency validation
        # In production, this would implement comprehensive emergency protocols
        
        # Check if emergency flag is set
        if not request.emergency:
            return False
        
        # Check justification contains emergency keywords
        emergency_keywords = ["emergency", "critical", "urgent", "incident", "breach"]
        justification_lower = request.justification.lower()
        
        if not any(keyword in justification_lower for keyword in emergency_keywords):
            return False
        
        # Additional validation could include:
        # - Time-based restrictions
        # - Requester authorization level
        # - Data sensitivity classification
        # - External incident validation
        
        return True
    
    def _check_consensus(self, request_id: str) -> Dict[str, Any]:
        """Check if consensus has been reached for a decryption request."""
        request = self.active_requests[request_id]
        votes = self.pending_votes[request_id]
        
        required_votes = self.authorization_thresholds[request.authorization_level]
        
        # Count approval votes
        approval_votes = sum(1 for vote in votes if vote.vote)
        total_votes = len(votes)
        
        # Check different consensus types
        if request.authorization_level == AuthorizationLevel.MAJORITY_CONSENSUS:
            consensus_reached = total_votes >= required_votes
            if consensus_reached:
                approved = approval_votes > (total_votes / 2)
            else:
                approved = False
                
        elif request.authorization_level == AuthorizationLevel.UNANIMOUS_CONSENSUS:
            consensus_reached = total_votes >= required_votes
            approved = consensus_reached and approval_votes == total_votes
            
        elif request.authorization_level == AuthorizationLevel.THRESHOLD_SHARES:
            consensus_reached = approval_votes >= required_votes
            approved = consensus_reached
            
        else:
            consensus_reached = total_votes >= required_votes
            approved = approval_votes >= required_votes
        
        return {
            "consensus_reached": consensus_reached,
            "approved": approved,
            "approval_votes": approval_votes,
            "total_votes": total_votes,
            "required_votes": required_votes
        }
    
    def _load_encrypted_data(self, vault_id: str, data_identifier: str) -> Optional[Dict[str, Any]]:
        """Load encrypted data from vault storage."""
        try:
            vault_file = self.vault_path / f"{vault_id}.json"
            
            if not vault_file.exists():
                return None
            
            with open(vault_file, 'r') as f:
                vault_data = json.load(f)
            
            if data_identifier not in vault_data:
                return None
            
            # For development, return dummy encrypted data
            # In production, this would load actual encrypted data
            return {
                "data": vault_data[data_identifier].get("encrypted_data", b"dummy_encrypted_data"),
                "key": vault_data[data_identifier].get("encryption_key", b"dummy_key")
            }
        
        except Exception as e:
            self.logger.error(f"Failed to load encrypted data: {e}")
            return None
    
    def _generate_request_id(self) -> str:
        """Generate a unique request ID."""
        timestamp = str(int(time.time() * 1000))
        random_suffix = secrets.token_hex(8)
        return f"decrypt_{timestamp}_{random_suffix}"
    
    def _sign_vote(self, request_id: str, agent_id: str, vote: bool) -> str:
        """Sign a vote for audit trail (simplified implementation)."""
        vote_data = f"{request_id}:{agent_id}:{vote}:{time.time()}"
        return hashlib.sha256(vote_data.encode()).hexdigest()
    
    def _cleanup_request(self, request_id: str):
        """Clean up completed request."""
        if request_id in self.active_requests:
            del self.active_requests[request_id]
        if request_id in self.pending_votes:
            del self.pending_votes[request_id]
    
    def _cleanup_expired_request(self, request_id: str):
        """Clean up expired request."""
        self.logger.info(f"Cleaning up expired request: {request_id}")
        self._cleanup_request(request_id)
    
    def get_pending_requests(self) -> List[Dict[str, Any]]:
        """Get list of pending decryption requests."""
        pending = []
        current_time = time.time()
        
        for request_id, request in self.active_requests.items():
            if request.expiration_time and current_time > request.expiration_time:
                continue
            
            votes = self.pending_votes.get(request_id, [])
            
            pending.append({
                "request_id": request_id,
                "vault_id": request.vault_id,
                "data_identifier": request.data_identifier,
                "requester_id": request.requester_id,
                "authorization_level": request.authorization_level.value,
                "emergency": request.emergency,
                "votes_received": len(votes),
                "votes_needed": self.authorization_thresholds[request.authorization_level],
                "time_remaining": max(0, request.expiration_time - current_time) if request.expiration_time else None
            })
        
        return pending
    
    def get_decrypt_metrics(self) -> Dict[str, Any]:
        """Get decryption tool performance metrics."""
        success_rate = (self.successful_decryptions / max(self.total_requests, 1)) * 100
        
        return {
            "total_requests": self.total_requests,
            "successful_decryptions": self.successful_decryptions,
            "failed_decryptions": self.failed_decryptions,
            "unauthorized_attempts": self.unauthorized_attempts,
            "success_rate": success_rate,
            "pending_requests": len(self.active_requests),
            "active_consensus_processes": len(self.pending_votes)
        }