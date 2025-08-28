# vaults/models/vault.py
import uuid
from typing import Optional, List, Dict
from pydantic import BaseModel, Field
from datetime import datetime


class VaultMetadata(BaseModel):
    """Metadata for a vault."""
    vault_id: uuid.UUID = Field(default_factory=uuid.uuid4)
    owner_did: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    last_modified: datetime = Field(default_factory=datetime.utcnow)
    trust_config_id: Optional[str] = None
    # --- FIX: Add the missing field to the model definition ---
    # This tells Pydantic that a 'crypto_info' dictionary is allowed.
    crypto_info: Optional[Dict] = None


class ContextProofSchema(BaseModel):
    """Schema for a context proof."""
    ip_proof: Optional[str] = None
    device_proof: Optional[str] = None
    time_proof: Optional[str] = None


class Vault(BaseModel):
    """A vault entity containing both metadata and encrypted data."""
    metadata: VaultMetadata
    # The data field in the JSON will be a base64 encoded string
    data: str


class VaultVersion(BaseModel):
    """Version information for a vault."""
    version_id: str = Field(..., description="Version identifier")
    vault_id: uuid.UUID = Field(..., description="Vault identifier")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Creation timestamp")
    version_number: int = Field(..., description="Version number")
    changes: Optional[Dict] = Field(None, description="Changes made in this version")