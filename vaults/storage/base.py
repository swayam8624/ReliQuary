# vaults/storage/base.py
from abc import ABC, abstractmethod

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