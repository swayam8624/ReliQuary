# vaults/storage/ipfs.py
from vaults.storage.base import StorageInterface

class IPFSStorage(StorageInterface):
    """
    Placeholder for an IPFS storage backend (V2 Roadmap).
    
    This implementation will use a library like 'ipfs-http-client' to pin data
    to a local or remote IPFS node.
    """
    def __init__(self, ipfs_api_url: str):
        self.ipfs_api_url = ipfs_api_url
        # TODO: Implement initialization with ipfs client
        pass

    def save_vault(self, vault_id: str, data: bytes):
        # TODO: Implement adding data to IPFS and returning the CID
        pass

    def load_vault(self, vault_id: str) -> bytes:
        # TODO: Implement retrieving data from IPFS by CID
        pass

    def delete_vault(self, vault_id: str):
        # TODO: Implement un-pinning data from IPFS
        pass