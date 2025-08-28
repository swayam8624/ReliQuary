"""
Vault API Endpoints for ReliQuary.
This module provides API endpoints for vault management operations.
"""

import json
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime

from fastapi import APIRouter, HTTPException, Depends, status
from pydantic import BaseModel, Field

# Import vault components
try:
    from vaults.manager import VaultManager
    from vaults.models.vault import Vault
    from vaults.storage.local import LocalStorage
except ImportError:
    # Mock implementations for development
    class Vault:
        def __init__(self, vault_id: str, name: str, description: str = "", owner_id: str = "", 
                     created_at: datetime = None, updated_at: datetime = None):
            self.vault_id = vault_id
            self.name = name
            self.description = description
            self.owner_id = owner_id
            self.created_at = created_at or datetime.now()
            self.updated_at = updated_at or datetime.now()
            self.size_bytes = 0
            self.encryption_algorithm = "AES-GCM"
            self.status = "active"
    
    class LocalStorage:
        def __init__(self, base_path: str = "/tmp/vaults"):
            self.base_path = base_path
    
    class VaultManager:
        def __init__(self, storage):
            self.storage = storage
            self.vaults = {}
            self.secrets = {}
        
        def create_vault(self, name: str, description: str = "", owner_id: str = "") -> Vault:
            vault_id = f"vault_{len(self.vaults) + 1}"
            vault = Vault(vault_id, name, description, owner_id)
            self.vaults[vault_id] = vault
            return vault
        
        def get_vault(self, vault_id: str) -> Vault:
            return self.vaults.get(vault_id)
        
        def list_vaults(self, owner_id: str = None) -> List[Vault]:
            if owner_id:
                return [v for v in self.vaults.values() if v.owner_id == owner_id]
            return list(self.vaults.values())
        
        def update_vault(self, vault_id: str, **kwargs) -> Vault:
            vault = self.vaults.get(vault_id)
            if vault:
                for key, value in kwargs.items():
                    if hasattr(vault, key):
                        setattr(vault, key, value)
                vault.updated_at = datetime.now()
            return vault
        
        def delete_vault(self, vault_id: str) -> bool:
            if vault_id in self.vaults:
                del self.vaults[vault_id]
                return True
            return False
        
        def store_secret(self, vault_id: str, secret_name: str, secret_value: str, 
                        metadata: Dict[str, Any] = None) -> Dict[str, Any]:
            if vault_id not in self.vaults:
                raise ValueError("Vault not found")
            
            secret_id = f"secret_{len(self.secrets) + 1}"
            secret = {
                "secret_id": secret_id,
                "vault_id": vault_id,
                "secret_name": secret_name,
                "secret_value": secret_value,  # In reality this would be encrypted
                "metadata": metadata or {},
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat(),
                "version": 1
            }
            self.secrets[secret_id] = secret
            return secret
        
        def retrieve_secret(self, vault_id: str, secret_name: str) -> Dict[str, Any]:
            for secret in self.secrets.values():
                if secret["vault_id"] == vault_id and secret["secret_name"] == secret_name:
                    return secret
            raise ValueError("Secret not found")


# Pydantic models for request/response validation
class VaultCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    description: str = Field(default="", max_length=500)
    owner_id: str = Field(..., min_length=1, max_length=100)
    encryption_algorithm: str = Field(default="AES-GCM", max_length=50)


class VaultUpdate(BaseModel):
    name: Optional[str] = Field(default=None, min_length=1, max_length=100)
    description: Optional[str] = Field(default=None, max_length=500)


class VaultResponse(BaseModel):
    vault_id: str
    name: str
    description: str
    owner_id: str
    created_at: datetime
    updated_at: datetime
    size_bytes: int
    encryption_algorithm: str
    status: str


class SecretCreate(BaseModel):
    secret_name: str = Field(..., min_length=1, max_length=100)
    secret_value: str = Field(..., min_length=1)
    metadata: Optional[Dict[str, Any]] = None


class SecretResponse(BaseModel):
    secret_id: str
    vault_id: str
    secret_name: str
    metadata: Optional[Dict[str, Any]] = None
    created_at: datetime
    updated_at: datetime
    version: int


# Router for vault endpoints
router = APIRouter(prefix="/vaults", tags=["vaults"])

# Global vault manager instance
_vault_manager = None


def get_vault_manager() -> VaultManager:
    """Get the global vault manager instance"""
    global _vault_manager
    if _vault_manager is None:
        storage = LocalStorage()
        _vault_manager = VaultManager(storage)
    return _vault_manager


@router.post("/", response_model=VaultResponse, status_code=status.HTTP_201_CREATED)
async def create_vault(vault_data: VaultCreate, vault_manager: VaultManager = Depends(get_vault_manager)):
    """
    Create a new vault.
    
    Args:
        vault_data: Vault creation data
        vault_manager: Vault manager instance
        
    Returns:
        Created vault information
    """
    try:
        vault = vault_manager.create_vault(
            name=vault_data.name,
            description=vault_data.description,
            owner_id=vault_data.owner_id
        )
        
        return VaultResponse(
            vault_id=vault.vault_id,
            name=vault.name,
            description=vault.description,
            owner_id=vault.owner_id,
            created_at=vault.created_at,
            updated_at=vault.updated_at,
            size_bytes=vault.size_bytes,
            encryption_algorithm=vault.encryption_algorithm,
            status=vault.status
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create vault: {str(e)}"
        )


@router.get("/{vault_id}", response_model=VaultResponse)
async def get_vault(vault_id: str, vault_manager: VaultManager = Depends(get_vault_manager)):
    """
    Get vault information.
    
    Args:
        vault_id: ID of the vault to retrieve
        vault_manager: Vault manager instance
        
    Returns:
        Vault information
    """
    try:
        vault = vault_manager.get_vault(vault_id)
        if not vault:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Vault not found"
            )
        
        return VaultResponse(
            vault_id=vault.vault_id,
            name=vault.name,
            description=vault.description,
            owner_id=vault.owner_id,
            created_at=vault.created_at,
            updated_at=vault.updated_at,
            size_bytes=vault.size_bytes,
            encryption_algorithm=vault.encryption_algorithm,
            status=vault.status
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve vault: {str(e)}"
        )


@router.get("/", response_model=List[VaultResponse])
async def list_vaults(owner_id: Optional[str] = None, vault_manager: VaultManager = Depends(get_vault_manager)):
    """
    List vaults, optionally filtered by owner.
    
    Args:
        owner_id: Optional owner ID to filter vaults
        vault_manager: Vault manager instance
        
    Returns:
        List of vaults
    """
    try:
        vaults = vault_manager.list_vaults(owner_id)
        
        return [
            VaultResponse(
                vault_id=vault.vault_id,
                name=vault.name,
                description=vault.description,
                owner_id=vault.owner_id,
                created_at=vault.created_at,
                updated_at=vault.updated_at,
                size_bytes=vault.size_bytes,
                encryption_algorithm=vault.encryption_algorithm,
                status=vault.status
            )
            for vault in vaults
        ]
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list vaults: {str(e)}"
        )


@router.put("/{vault_id}", response_model=VaultResponse)
async def update_vault(vault_id: str, vault_data: VaultUpdate, vault_manager: VaultManager = Depends(get_vault_manager)):
    """
    Update vault information.
    
    Args:
        vault_id: ID of the vault to update
        vault_data: Vault update data
        vault_manager: Vault manager instance
        
    Returns:
        Updated vault information
    """
    try:
        update_kwargs = {}
        if vault_data.name is not None:
            update_kwargs["name"] = vault_data.name
        if vault_data.description is not None:
            update_kwargs["description"] = vault_data.description
        
        vault = vault_manager.update_vault(vault_id, **update_kwargs)
        if not vault:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Vault not found"
            )
        
        return VaultResponse(
            vault_id=vault.vault_id,
            name=vault.name,
            description=vault.description,
            owner_id=vault.owner_id,
            created_at=vault.created_at,
            updated_at=vault.updated_at,
            size_bytes=vault.size_bytes,
            encryption_algorithm=vault.encryption_algorithm,
            status=vault.status
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update vault: {str(e)}"
        )


@router.delete("/{vault_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_vault(vault_id: str, vault_manager: VaultManager = Depends(get_vault_manager)):
    """
    Delete a vault.
    
    Args:
        vault_id: ID of the vault to delete
        vault_manager: Vault manager instance
    """
    try:
        success = vault_manager.delete_vault(vault_id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Vault not found"
            )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete vault: {str(e)}"
        )


@router.post("/secrets", response_model=SecretResponse, status_code=status.HTTP_201_CREATED)
async def store_secret(secret_data: SecretCreate, vault_id: str, vault_manager: VaultManager = Depends(get_vault_manager)):
    """
    Store a secret in a vault.
    
    Args:
        secret_data: Secret data to store
        vault_id: ID of the vault to store the secret in
        vault_manager: Vault manager instance
        
    Returns:
        Stored secret information
    """
    try:
        secret = vault_manager.store_secret(
            vault_id=vault_id,
            secret_name=secret_data.secret_name,
            secret_value=secret_data.secret_value,
            metadata=secret_data.metadata
        )
        
        return SecretResponse(
            secret_id=secret["secret_id"],
            vault_id=secret["vault_id"],
            secret_name=secret["secret_name"],
            metadata=secret["metadata"],
            created_at=datetime.fromisoformat(secret["created_at"]),
            updated_at=datetime.fromisoformat(secret["updated_at"]),
            version=secret["version"]
        )
        
    except ValueError as e:
        if "not found" in str(e).lower():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=str(e)
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to store secret: {str(e)}"
            )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to store secret: {str(e)}"
        )


@router.get("/secrets/{secret_name}", response_model=SecretResponse)
async def retrieve_secret(vault_id: str, secret_name: str, vault_manager: VaultManager = Depends(get_vault_manager)):
    """
    Retrieve a secret from a vault.
    
    Args:
        vault_id: ID of the vault to retrieve the secret from
        secret_name: Name of the secret to retrieve
        vault_manager: Vault manager instance
        
    Returns:
        Retrieved secret information
    """
    try:
        secret = vault_manager.retrieve_secret(vault_id, secret_name)
        
        return SecretResponse(
            secret_id=secret["secret_id"],
            vault_id=secret["vault_id"],
            secret_name=secret["secret_name"],
            metadata=secret["metadata"],
            created_at=datetime.fromisoformat(secret["created_at"]),
            updated_at=datetime.fromisoformat(secret["updated_at"]),
            version=secret["version"]
        )
        
    except ValueError as e:
        if "not found" in str(e).lower():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=str(e)
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to retrieve secret: {str(e)}"
            )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve secret: {str(e)}"
        )