"""IPFS storage adapter boundary.

ReliQuary does not ship an IPFS client by default. This class exists so config
can reject unsupported IPFS use loudly instead of accepting writes and losing
data through no-op methods.
"""

from vaults.storage.base import StorageError, StorageInterface


class IPFSStorage(StorageInterface):
    """Unsupported IPFS storage adapter until an IPFS client is configured."""

    def __init__(self, ipfs_api_url: str):
        self.ipfs_api_url = ipfs_api_url
        raise StorageError(
            "IPFS storage is not configured. Use LocalStorage for the shipped "
            "Mac/local demo, or install and wire an IPFS HTTP client before "
            "selecting this backend."
        )

    def save_vault(self, vault_id: str, data: bytes):
        raise StorageError("IPFS storage is not configured.")

    def load_vault(self, vault_id: str) -> bytes:
        raise StorageError("IPFS storage is not configured.")

    def delete_vault(self, vault_id: str):
        raise StorageError("IPFS storage is not configured.")


IPFSStorageBackend = IPFSStorage
