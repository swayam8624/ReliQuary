# vaults/storage/local.py
import os
from vaults.storage.base import StorageInterface

class LocalFileStorage(StorageInterface):
    """
    A storage backend that saves and loads vaults from the local file system.
    """
    def __init__(self, base_path: str):
        self.base_path = base_path
        os.makedirs(base_path, exist_ok=True)

    def _get_file_path(self, vault_id: str) -> str:
        """Constructs the full file path for a given vault ID."""
        return os.path.join(self.base_path, f"{vault_id}.enc")

    def save_vault(self, vault_id: str, data: bytes):
        """Saves encrypted vault data to a local file."""
        file_path = self._get_file_path(vault_id)
        with open(file_path, "wb") as f:
            f.write(data)

    def load_vault(self, vault_id: str) -> bytes:
        """Loads encrypted vault data from a local file."""
        file_path = self._get_file_path(vault_id)
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Vault file for ID '{vault_id}' not found.")
        with open(file_path, "rb") as f:
            return f.read()

    def delete_vault(self, vault_id: str):
        """Deletes a local vault file."""
        file_path = self._get_file_path(vault_id)
        if os.path.exists(file_path):
            os.remove(file_path)
            
if __name__ == "__main__":
    print("--- LocalFileStorage Test ---")
    test_path = "vaults/test_data"
    test_storage = LocalFileStorage(base_path=test_path)
    
    # Clean up any previous test files
    test_id = "test_vault_1"
    test_storage.delete_vault(test_id)
    
    test_data = b"This is my secret data encrypted!"
    
    # 1. Test save_vault
    test_storage.save_vault(test_id, test_data)
    print(f"✅ Saved vault with ID '{test_id}'.")
    
    # 2. Test load_vault
    loaded_data = test_storage.load_vault(test_id)
    assert loaded_data == test_data, "Loaded data should match saved data."
    print(f"✅ Loaded vault successfully. Data matches.")

    # 3. Test delete_vault
    test_storage.delete_vault(test_id)
    assert not os.path.exists(test_storage._get_file_path(test_id)), "File should have been deleted."
    print(f"✅ Deleted vault successfully.")
    
    # Clean up the test directory
    os.rmdir(test_path)
    print("✅ LocalFileStorage test passed.")


# Alias for backward compatibility
LocalStorageBackend = LocalFileStorage
LocalStorage = LocalFileStorage
