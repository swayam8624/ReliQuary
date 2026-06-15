# vaults/storage/base.py
from abc import ABC, abstractmethod
from typing import List, Optional

class StorageInterface(ABC):
    """
    Abstract base class for all storage backends.
    All concrete storage classes must implement these methods.
    """
    @abstractmethod
    def save_vault(self, vault_id: str, data: bytes):
        """Saves encrypted vault data with a unique ID."""
        pass

    @abstractmethod
    def load_vault(self, vault_id: str) -> bytes:
        """Loads encrypted vault data by its unique ID."""
        pass

    @abstractmethod
    def delete_vault(self, vault_id: str):
        """Deletes a vault by its unique ID."""
        pass

    def list_vaults(self, owner_id: Optional[str] = None) -> List[bytes]:
        """Lists serialized vault records when the backend supports queries."""
        raise NotImplementedError("This storage backend does not support vault listing.")

    def save_secret(self, secret_id: str, data: bytes):
        """Saves serialized secret metadata when the backend supports secrets."""
        raise NotImplementedError("This storage backend does not support secret storage.")

    def load_secret(self, vault_id: str, secret_name: str) -> bytes:
        """Loads serialized secret metadata by vault and name."""
        raise NotImplementedError("This storage backend does not support secret storage.")

    def list_secrets(self, vault_id: Optional[str] = None) -> List[bytes]:
        """Lists serialized secret metadata when the backend supports queries."""
        raise NotImplementedError("This storage backend does not support secret listing.")


# Alias for backward compatibility
StorageBackend = StorageInterface


class StorageError(Exception):
    """Base exception for storage-related errors"""
    pass
