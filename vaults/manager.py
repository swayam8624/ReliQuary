# --- vaults/manager.py ----
import json
import os
import uuid
import base64
import logging
import traceback
from typing import Optional

# Local project imports
from vaults.vault import VaultMetadata, Vault
from vaults.storage.base import StorageInterface
from core.crypto.aes_gcm import encrypt, decrypt
from core.crypto.key_sharding import create_shares, reconstruct_secret

# Basic logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


class VaultManager:
    """
    Manages the creation, retrieval, and deletion of vaults.
    """
    def __init__(self, storage_backend: 'StorageInterface'): # Use string hint for type
        self.storage = storage_backend

    def create_vault(self, owner_did: str, plaintext_data: str) -> VaultMetadata:
        """
        Creates a new vault, encrypts its data, and stores it.
        """
        vault_id = uuid.uuid4()
        metadata = VaultMetadata(vault_id=vault_id, owner_did=owner_did)
        
        # 1. Generate master key and create shares
        master_key = os.urandom(32)  # AES-256 key
        # In a real run, this calls your microservice
        shares = create_shares(master_key, num_shares=5, threshold=3)
        
        # 2. Encrypt the plaintext data
        encrypted_data_bytes, nonce, tag = encrypt(plaintext_data.encode('utf-8'), master_key)

        # 3. Base64-encode the encrypted bytes for safe JSON serialization
        encrypted_data_b64_str = base64.b64encode(encrypted_data_bytes).decode('ascii')
        
        # 4. Store crypto info needed for decryption in the metadata
        #    This now works because the field exists in the VaultMetadata model.
        metadata.crypto_info = {
            "key_shares": shares,
            "nonce": nonce.hex(),
            "tag": tag.hex()
        }

        # 5. Create the final Vault object with the base64 string
        vault = Vault(metadata=metadata, data=encrypted_data_b64_str)
        
        # 6. Save the complete vault object as a JSON file
        self.storage.save_vault(str(vault_id), vault.model_dump_json().encode('utf-8'))
        
        return metadata

    def get_vault(self, vault_id: str) -> Optional[dict]:
        """
        Retrieves a vault by ID, decrypts its data, and returns a dictionary
        containing the metadata and decrypted plaintext.
        """
        try:
            vault_bytes = self.storage.load_vault(vault_id)
            vault_data = json.loads(vault_bytes)

            metadata = vault_data["metadata"]
            crypto_info = metadata["crypto_info"]
            
            # 1. Reconstruct the master key from shares
            shares = [bytes.fromhex(s) for s in crypto_info["key_shares"]]
            master_key = reconstruct_secret(shares)
            
            # 2. Get decryption parameters
            nonce = bytes.fromhex(crypto_info["nonce"])
            tag = bytes.fromhex(crypto_info["tag"])
            
            # 3. Decode the base64 data from the JSON payload back into bytes
            encrypted_data_b64_str = vault_data["data"]
            encrypted_data_bytes = base64.b64decode(encrypted_data_b64_str)
            
            # 4. Decrypt the data
            decrypted_data_bytes = decrypt(encrypted_data_bytes, nonce, tag, master_key)
            
            # 5. Return a simple dictionary with the results
            return {
                "metadata": metadata,
                "decrypted_data": decrypted_data_bytes.decode('utf-8')
            }
        except FileNotFoundError:
            logging.warning(f"Vault with ID '{vault_id}' not found.")
            return None
        except Exception as e:
            logging.error(f"Error retrieving or decrypting vault: {e}")
            traceback.print_exc()
            return None

    def delete_vault(self, vault_id: str):
        """Deletes a vault from storage."""
        self.storage.delete_vault(vault_id)


# Dummy classes and functions to make the test runnable standalone
class StorageInterface:
    def save_vault(self, vault_id: str, data: bytes): pass
    def load_vault(self, vault_id: str) -> bytes: pass
    def delete_vault(self, vault_id: str): pass

class LocalFileStorage(StorageInterface):
    def __init__(self, base_path: str):
        self.base_path = base_path
        os.makedirs(base_path, exist_ok=True)
    def _get_file_path(self, vault_id: str):
        return os.path.join(self.base_path, f"{vault_id}.enc")
    def save_vault(self, vault_id: str, data: bytes):
        with open(self._get_file_path(vault_id), "wb") as f: f.write(data)
    def load_vault(self, vault_id: str) -> bytes:
        with open(self._get_file_path(vault_id), "rb") as f: return f.read()
    def delete_vault(self, vault_id: str):
        if os.path.exists(self._get_file_path(vault_id)): os.remove(self._get_file_path(vault_id))

def create_shares(secret, num_shares, threshold): return [b'share1'.hex(), b'share2'.hex()]
def reconstruct_secret(shares): return os.urandom(32)
def encrypt(data, key): return (data, b'nonce', b'tag')
def decrypt(data, nonce, tag, key): return data


if __name__ == "__main__":
    print("--- VaultManager Test ---")
    
    test_storage_path = os.path.join(os.getcwd(), 'vaults', 'test_data')
    storage_backend = LocalFileStorage(base_path=test_storage_path)
    manager = VaultManager(storage_backend)
    
    owner_did = "did:reliquary:testuser"
    plaintext = "My deepest secrets and cryptographic keys."
    print(f"Creating a new vault for owner: {owner_did}")
    
    new_vault_metadata = manager.create_vault(owner_did, plaintext)
    vault_id_str = str(new_vault_metadata.vault_id)
    print(f"✅ Vault created successfully with ID: {vault_id_str}")
    
    print("\nAttempting to retrieve and decrypt the vault...")
    retrieved_vault = manager.get_vault(vault_id_str)
    
    if retrieved_vault:
        decrypted_data = retrieved_vault["decrypted_data"]
        assert decrypted_data == plaintext, "Decrypted data does not match original plaintext!"
        print(f"✅ Vault retrieved and decrypted successfully.")
        print(f"   Decrypted data: '{decrypted_data}'")
    else:
        print("❌ Failed to retrieve vault.")
        
    print(f"\nAttempting to delete vault with ID: {vault_id_str}")
    manager.delete_vault(vault_id_str)
    
    final_check = manager.get_vault(vault_id_str)
    if final_check is None:
        print(f"✅ Vault with ID {vault_id_str} deleted successfully.")
    else:
        print(f"❌ Vault deletion check failed.")

    if os.path.exists(test_storage_path):
        os.rmdir(test_storage_path)
    print("✅ VaultManager test passed.")