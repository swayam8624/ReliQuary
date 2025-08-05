# vaults/storage/arweave.py
from vaults.storage.base import StorageInterface

class ArweaveStorage(StorageInterface):
    """
    Placeholder for an Arweave storage backend (V2 Roadmap).
    
    This implementation will use a library like 'arweave-python' for permanent
    and decentralized data storage.
    """
    def __init__(self, wallet_file_path: str):
        self.wallet_file_path = wallet_file_path
        # TODO: Implement initialization with Arweave wallet and client
        pass

    def save_vault(self, vault_id: str, data: bytes):
        # TODO: Implement creating and submitting a transaction to Arweave
        pass

    def load_vault(self, vault_id: str) -> bytes:
        # TODO: Implement retrieving a transaction from Arweave
        pass

    def delete_vault(self, vault_id: str):
        # Arweave data is permanent, so this method will not be implemented.
        raise NotImplementedError("Arweave is permanent storage; delete is not supported.")