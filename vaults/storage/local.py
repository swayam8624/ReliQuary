# vaults/storage/local.py
import os
import base64
import shutil
from typing import List, Optional
from vaults.storage.base import StorageInterface

class LocalFileStorage(StorageInterface):
    """
    A storage backend that saves and loads vaults from the local file system.
    """
    def __init__(self, base_path: str = "/tmp/reliquary-vaults"):
        self.base_path = base_path
        os.makedirs(base_path, exist_ok=True)

    def _get_file_path(self, vault_id: str) -> str:
        """Constructs the full file path for a given vault ID."""
        return os.path.join(self.base_path, "vaults", f"{vault_id}.json")

    def _secret_dir(self, vault_id: str) -> str:
        return os.path.join(self.base_path, "secrets", vault_id)

    def _secret_file_name(self, secret_name: str) -> str:
        encoded = base64.urlsafe_b64encode(secret_name.encode("utf-8")).decode("ascii")
        return f"{encoded}.json"

    def _secret_file_path(self, vault_id: str, secret_name: str) -> str:
        return os.path.join(self._secret_dir(vault_id), self._secret_file_name(secret_name))

    def save_vault(self, vault_id: str, data: bytes):
        """Saves encrypted vault data to a local file."""
        file_path = self._get_file_path(vault_id)
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
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
        """Deletes a local vault file and its secret records."""
        file_path = self._get_file_path(vault_id)
        if os.path.exists(file_path):
            os.remove(file_path)
        shutil.rmtree(self._secret_dir(vault_id), ignore_errors=True)

    def list_vaults(self, owner_id: Optional[str] = None) -> List[bytes]:
        """Loads all local vault records. Owner filtering is handled by VaultManager."""
        records = []
        vault_dir = os.path.join(self.base_path, "vaults")
        if not os.path.isdir(vault_dir):
            return records
        for filename in sorted(os.listdir(vault_dir)):
            if not filename.endswith(".json"):
                continue
            with open(os.path.join(vault_dir, filename), "rb") as f:
                records.append(f.read())
        return records

    def save_secret(self, secret_id: str, data: bytes):
        """Saves encrypted secret metadata to the local file system."""
        import json

        payload = json.loads(data.decode("utf-8"))
        vault_id = payload["vault_id"]
        secret_name = payload["secret_name"]
        secret_dir = self._secret_dir(vault_id)
        os.makedirs(secret_dir, exist_ok=True)
        with open(self._secret_file_path(vault_id, secret_name), "wb") as f:
            f.write(data)

    def load_secret(self, vault_id: str, secret_name: str) -> bytes:
        """Loads encrypted secret metadata by vault and name."""
        file_path = self._secret_file_path(vault_id, secret_name)
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Secret '{secret_name}' in vault '{vault_id}' not found.")
        with open(file_path, "rb") as f:
            return f.read()

    def list_secrets(self, vault_id: Optional[str] = None) -> List[bytes]:
        """Lists serialized secret records."""
        records = []
        secrets_root = os.path.join(self.base_path, "secrets")
        if not os.path.isdir(secrets_root):
            return records

        vault_dirs = [vault_id] if vault_id else sorted(os.listdir(secrets_root))
        for current_vault_id in vault_dirs:
            current_dir = os.path.join(secrets_root, current_vault_id)
            if not os.path.isdir(current_dir):
                continue
            for filename in sorted(os.listdir(current_dir)):
                if not filename.endswith(".json"):
                    continue
                with open(os.path.join(current_dir, filename), "rb") as f:
                    records.append(f.read())
        return records
            
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
