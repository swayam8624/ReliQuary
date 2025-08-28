"""
API schemas for the ReliQuary SDK.
This module defines data models for API requests and responses.
"""

from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from datetime import datetime
from enum import Enum


class ConsensusType(Enum):
    """Types of consensus operations"""
    ACCESS_REQUEST = "access_request"
    GOVERNANCE_DECISION = "governance_decision"
    EMERGENCY_RESPONSE = "emergency_response"
    SECURITY_VALIDATION = "security_validation"


@dataclass
class ConsensusRequest:
    """Request for multi-agent consensus"""
    request_type: ConsensusType
    context_data: Dict[str, Any]
    user_id: str
    resource_path: str
    priority: int = 5
    timeout_seconds: int = 30
    required_agents: Optional[List[str]] = None
    metadata: Optional[Dict[str, Any]] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for API request"""
        return {
            "request_type": self.request_type.value,
            "context_data": self.context_data,
            "user_id": self.user_id,
            "resource_path": self.resource_path,
            "priority": self.priority,
            "timeout_seconds": self.timeout_seconds,
            "required_agents": self.required_agents,
            "metadata": self.metadata or {}
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ConsensusRequest':
        """Create from dictionary"""
        # Convert string to enum if needed
        if isinstance(data.get("request_type"), str):
            data["request_type"] = ConsensusType(data["request_type"])
        
        return cls(**data)


@dataclass
class ConsensusResult:
    """Result of multi-agent consensus"""
    request_id: str
    decision: str
    confidence_score: float
    participating_agents: List[str]
    consensus_time_ms: float
    detailed_votes: Dict[str, Any]
    risk_assessment: Dict[str, Any]
    timestamp: datetime
    success: bool
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for API response"""
        return {
            "request_id": self.request_id,
            "decision": self.decision,
            "confidence_score": self.confidence_score,
            "participating_agents": self.participating_agents,
            "consensus_time_ms": self.consensus_time_ms,
            "detailed_votes": self.detailed_votes,
            "risk_assessment": self.risk_assessment,
            "timestamp": self.timestamp.isoformat() if isinstance(self.timestamp, datetime) else self.timestamp,
            "success": self.success
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ConsensusResult':
        """Create from dictionary"""
        # Convert timestamp string to datetime if needed
        if isinstance(data.get("timestamp"), str):
            data["timestamp"] = datetime.fromisoformat(data["timestamp"])
        
        return cls(**data)


@dataclass
class ZKProofRequest:
    """Request for zero-knowledge proof generation"""
    circuit_type: str
    inputs: Dict[str, Any]
    public_signals: List[str]
    metadata: Optional[Dict[str, Any]] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for API request"""
        return {
            "circuit_type": self.circuit_type,
            "inputs": self.inputs,
            "public_signals": self.public_signals,
            "metadata": self.metadata or {}
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ZKProofRequest':
        """Create from dictionary"""
        return cls(**data)


@dataclass
class ZKProofResult:
    """Result of zero-knowledge proof generation"""
    proof_id: str
    proof: Dict[str, Any]
    public_signals: List[str]
    verification_key: Dict[str, Any]
    circuit_type: str
    generation_time_ms: float
    valid: bool
    timestamp: datetime
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for API response"""
        return {
            "proof_id": self.proof_id,
            "proof": self.proof,
            "public_signals": self.public_signals,
            "verification_key": self.verification_key,
            "circuit_type": self.circuit_type,
            "generation_time_ms": self.generation_time_ms,
            "valid": self.valid,
            "timestamp": self.timestamp.isoformat() if isinstance(self.timestamp, datetime) else self.timestamp
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ZKProofResult':
        """Create from dictionary"""
        # Convert timestamp string to datetime if needed
        if isinstance(data.get("timestamp"), str):
            data["timestamp"] = datetime.fromisoformat(data["timestamp"])
        
        return cls(**data)


@dataclass
class VaultMetadata:
    """Metadata for a vault"""
    vault_id: str
    name: str
    description: str
    created_at: datetime
    updated_at: datetime
    owner_id: str
    size_bytes: int
    encryption_algorithm: str
    status: str
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for API response"""
        return {
            "vault_id": self.vault_id,
            "name": self.name,
            "description": self.description,
            "created_at": self.created_at.isoformat() if isinstance(self.created_at, datetime) else self.created_at,
            "updated_at": self.updated_at.isoformat() if isinstance(self.updated_at, datetime) else self.updated_at,
            "owner_id": self.owner_id,
            "size_bytes": self.size_bytes,
            "encryption_algorithm": self.encryption_algorithm,
            "status": self.status
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'VaultMetadata':
        """Create from dictionary"""
        # Convert timestamp strings to datetime if needed
        for field in ["created_at", "updated_at"]:
            if isinstance(data.get(field), str):
                data[field] = datetime.fromisoformat(data[field])
        
        return cls(**data)


@dataclass
class SecretData:
    """Data for a secret"""
    secret_id: str
    vault_id: str
    secret_name: str
    secret_value: str
    created_at: datetime
    updated_at: datetime
    metadata: Dict[str, Any]
    version: int
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for API response"""
        return {
            "secret_id": self.secret_id,
            "vault_id": self.vault_id,
            "secret_name": self.secret_name,
            "secret_value": self.secret_value,
            "created_at": self.created_at.isoformat() if isinstance(self.created_at, datetime) else self.created_at,
            "updated_at": self.updated_at.isoformat() if isinstance(self.updated_at, datetime) else self.updated_at,
            "metadata": self.metadata,
            "version": self.version
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'SecretData':
        """Create from dictionary"""
        # Convert timestamp strings to datetime if needed
        for field in ["created_at", "updated_at"]:
            if isinstance(data.get(field), str):
                data[field] = datetime.fromisoformat(data[field])
        
        return cls(**data)