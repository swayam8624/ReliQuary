"""Arweave storage adapter boundary.

Arweave is permanent storage and requires wallet/client setup. The shipped
project must not pretend this backend can save, load, or delete vaults before
that production integration exists.
"""

from vaults.storage.base import StorageError, StorageInterface


class ArweaveStorage(StorageInterface):
    """Unsupported Arweave storage adapter until wallet/client setup is added."""

    def __init__(self, wallet_file_path: str):
        self.wallet_file_path = wallet_file_path
        raise StorageError(
            "Arweave storage is not configured. Use LocalStorage for the shipped "
            "Mac/local demo, or wire a wallet and Arweave client before selecting "
            "this backend."
        )

    def save_vault(self, vault_id: str, data: bytes):
        raise StorageError("Arweave storage is not configured.")

    def load_vault(self, vault_id: str) -> bytes:
        raise StorageError("Arweave storage is not configured.")

    def delete_vault(self, vault_id: str):
        raise StorageError("Arweave data is permanent; deletion is not supported.")


ArweaveStorageBackend = ArweaveStorage
