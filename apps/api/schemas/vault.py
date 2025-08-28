"""
Vault Schemas for ReliQuary FastAPI

This module defines Pydantic schemas for vault-related data structures
used in the FastAPI application.
"""

from typing import List, Dict, Any, Optional, Union
from enum import Enum
from pydantic import BaseModel, Field
from datetime import datetime


class VaultType(str, Enum):
    """Types of vaults"""
    PERSONAL = "personal"
    TEAM = "team"
    ORGANIZATION = "organization"
    SHARED = "shared"


class VaultStatus(str, Enum):
    """Vault status values"""
    ACTIVE = "active"
    LOCKED = "locked"
    ARCHIVED = "archived"
    DELETED = "deleted"


class EncryptionAlgorithm(str, Enum):
    """Supported encryption algorithms"""
    AES_256_GCM = "aes-256-gcm"
    KYBER_AES = "kyber-aes"
    FALCON_AES = "falcon-aes"
    HYBRID = "hybrid"


class VaultMetadata(BaseModel):
    """Vault metadata"""
    name: str = Field(..., description="Vault name")
    description: Optional[str] = Field(None, description="Vault description")
    vault_type: VaultType = Field(..., description="Vault type")
    owner_id: str = Field(..., description="Vault owner identifier")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")
    version: str = Field(..., description="Vault version")
    tags: List[str] = Field(default_factory=list, description="Vault tags")


class VaultAccessPolicy(BaseModel):
    """Vault access policy"""
    policy_id: str = Field(..., description="Policy identifier")
    vault_id: str = Field(..., description="Vault identifier")
    user_id: str = Field(..., description="User identifier")
    permissions: List[str] = Field(..., description="List of permissions")
    granted_by: str = Field(..., description="User who granted permissions")
    granted_at: datetime = Field(..., description="When permissions were granted")
    expires_at: Optional[datetime] = Field(None, description="When permissions expire")


class VaultCreateRequest(BaseModel):
    """Request model for vault creation"""
    name: str = Field(..., description="Vault name")
    description: Optional[str] = Field(None, description="Vault description")
    vault_type: VaultType = Field(default=VaultType.PERSONAL, description="Vault type")
    owner_id: str = Field(..., description="Vault owner identifier")
    initial_data: Optional[Dict[str, Any]] = Field(None, description="Initial vault data")
    encryption_algorithm: EncryptionAlgorithm = Field(default=EncryptionAlgorithm.KYBER_AES, description="Encryption algorithm")
    access_policy: Optional[VaultAccessPolicy] = Field(None, description="Initial access policy")
    tags: List[str] = Field(default_factory=list, description="Vault tags")


class VaultCreateResponse(BaseModel):
    """Response model for vault creation"""
    success: bool = Field(..., description="Whether creation was successful")
    vault_id: str = Field(..., description="Created vault identifier")
    message: Optional[str] = Field(None, description="Additional message")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Response timestamp")


class VaultAccessRequest(BaseModel):
    """Request model for vault access"""
    vault_id: str = Field(..., description="Vault identifier")
    user_id: str = Field(..., description="User identifier")
    context_data: Dict[str, Any] = Field(..., description="Context data for access request")
    reason: Optional[str] = Field(None, description="Reason for access")
    timeout: int = Field(default=30, description="Access timeout in seconds")


class VaultAccessResponse(BaseModel):
    """Response model for vault access"""
    vault_id: str = Field(..., description="Vault identifier")
    user_id: str = Field(..., description="User identifier")
    access_granted: bool = Field(..., description="Whether access was granted")
    decrypted_data: Optional[Dict[str, Any]] = Field(None, description="Decrypted vault data")
    access_token: Optional[str] = Field(None, description="Access token for subsequent requests")
    expires_at: Optional[datetime] = Field(None, description="When access expires")
    processing_time: float = Field(..., description="Processing time in seconds")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Response timestamp")


class VaultUpdateRequest(BaseModel):
    """Request model for vault update"""
    vault_id: str = Field(..., description="Vault identifier")
    user_id: str = Field(..., description="User identifier")
    updated_data: Optional[Dict[str, Any]] = Field(None, description="Updated vault data")
    updated_metadata: Optional[VaultMetadata] = Field(None, description="Updated metadata")
    updated_access_policy: Optional[VaultAccessPolicy] = Field(None, description="Updated access policy")
    encryption_algorithm: Optional[EncryptionAlgorithm] = Field(None, description="Updated encryption algorithm")


class VaultUpdateResponse(BaseModel):
    """Response model for vault update"""
    success: bool = Field(..., description="Whether update was successful")
    vault_id: str = Field(..., description="Vault identifier")
    message: Optional[str] = Field(None, description="Additional message")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Response timestamp")


class VaultListResponse(BaseModel):
    """Response model for vault listing"""
    vaults: List[VaultMetadata] = Field(..., description="List of vaults")
    total_count: int = Field(..., description="Total number of vaults")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Response timestamp")


class VaultInfoResponse(BaseModel):
    """Response model for vault information"""
    vault_id: str = Field(..., description="Vault identifier")
    metadata: VaultMetadata = Field(..., description="Vault metadata")
    access_policies: List[VaultAccessPolicy] = Field(default_factory=list, description="Access policies")
    status: VaultStatus = Field(..., description="Vault status")
    size_bytes: int = Field(..., description="Vault size in bytes")
    last_accessed: Optional[datetime] = Field(None, description="Last access timestamp")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Response timestamp")


class VaultDeleteRequest(BaseModel):
    """Request model for vault deletion"""
    vault_id: str = Field(..., description="Vault identifier")
    user_id: str = Field(..., description="User identifier")
    confirm: bool = Field(..., description="Confirmation flag")
    reason: Optional[str] = Field(None, description="Reason for deletion")


class VaultDeleteResponse(BaseModel):
    """Response model for vault deletion"""
    success: bool = Field(..., description="Whether deletion was successful")
    vault_id: str = Field(..., description="Vault identifier")
    message: Optional[str] = Field(None, description="Additional message")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Response timestamp")


class VaultBackupRequest(BaseModel):
    """Request model for vault backup"""
    vault_id: str = Field(..., description="Vault identifier")
    user_id: str = Field(..., description="User identifier")
    backup_location: str = Field(..., description="Backup location")
    encryption_key: Optional[str] = Field(None, description="Encryption key for backup")


class VaultBackupResponse(BaseModel):
    """Response model for vault backup"""
    success: bool = Field(..., description="Whether backup was successful")
    vault_id: str = Field(..., description="Vault identifier")
    backup_path: str = Field(..., description="Backup file path")
    backup_size: int = Field(..., description="Backup size in bytes")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Response timestamp")