# --- vaults/manager.py ----
import json
import os
import uuid
import base64
import hashlib
import logging
import traceback
from typing import Optional, List, Dict, Any
from datetime import datetime

# Local project imports
from vaults.models.vault import VaultMetadata, Vault
from vaults.storage.base import StorageInterface
from core.crypto.aes_gcm import encrypt, decrypt
from core.crypto.key_sharding import create_shares, reconstruct_secret

# Basic logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

SECRET_ENVELOPE_PREFIX = "reliquary:aes-gcm:v1:"


class Secret:
    """A secret stored in a vault."""
    def __init__(self, secret_id: str, vault_id: str, secret_name: str, secret_value: str, 
                 metadata: Dict[str, Any], created_at: str, updated_at: str, version: int):
        self.secret_id = secret_id
        self.vault_id = vault_id
        self.secret_name = secret_name
        self.secret_value = secret_value
        self.metadata = metadata
        self.created_at = created_at
        self.updated_at = updated_at
        self.version = version

    def to_dict(self) -> Dict[str, Any]:
        return {
            "secret_id": self.secret_id,
            "vault_id": self.vault_id,
            "secret_name": self.secret_name,
            "secret_value": self.secret_value,
            "metadata": self.metadata,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "version": self.version,
        }

    def __getitem__(self, key: str):
        return self.to_dict()[key]


class VaultManager:
    """
    Manages the creation, retrieval, and deletion of vaults.
    """
    def __init__(self, storage_backend: 'StorageInterface'): # Use string hint for type
        self.storage = storage_backend
        self.vaults = {}  # In-memory cache for vaults
        self.secrets = {}  # In-memory cache for secrets

    def _secret_encryption_key(self) -> bytes:
        key_b64 = os.environ.get("RELIQUARY_SECRET_KEY_B64")
        if key_b64:
            try:
                key = base64.b64decode(key_b64, validate=True)
            except Exception as exc:
                raise ValueError("RELIQUARY_SECRET_KEY_B64 must be valid base64") from exc
            if len(key) != 32:
                raise ValueError("RELIQUARY_SECRET_KEY_B64 must decode to exactly 32 bytes")
            return key

        if os.environ.get("RELIQUARY_ENV", "").lower() == "production":
            raise RuntimeError("Set RELIQUARY_SECRET_KEY_B64 before storing secrets in production")

        seed = os.environ.get("RELIQUARY_DEV_SECRET_KEY", "reliquary-local-dev-secret-key")
        return hashlib.sha256(seed.encode("utf-8")).digest()

    def _encrypt_secret_value(self, secret_value: str) -> str:
        ciphertext, nonce, tag = encrypt(secret_value.encode("utf-8"), self._secret_encryption_key())
        envelope = {
            "ciphertext": base64.b64encode(ciphertext).decode("ascii"),
            "nonce": base64.b64encode(nonce).decode("ascii"),
            "tag": base64.b64encode(tag).decode("ascii"),
        }
        return SECRET_ENVELOPE_PREFIX + base64.b64encode(
            json.dumps(envelope, separators=(",", ":")).encode("utf-8")
        ).decode("ascii")

    def _decrypt_secret_value(self, stored_value: str) -> str:
        if stored_value.startswith(SECRET_ENVELOPE_PREFIX):
            encoded = stored_value[len(SECRET_ENVELOPE_PREFIX):]
            envelope = json.loads(base64.b64decode(encoded).decode("utf-8"))
            plaintext = decrypt(
                base64.b64decode(envelope["ciphertext"]),
                base64.b64decode(envelope["nonce"]),
                base64.b64decode(envelope["tag"]),
                self._secret_encryption_key(),
            )
            return plaintext.decode("utf-8")

        # Backward compatibility for records created before the AES-GCM envelope.
        if stored_value.startswith("encrypted_"):
            return stored_value[10:]

        return stored_value

    def create_vault(self, name: str = None, description: str = "", owner_id: str = "", 
                     owner_did: str = None, plaintext_data: str = None, 
                     encryption_algorithm: str = "AES-GCM", **kwargs) -> Vault:
        """
        Creates a new vault, encrypts its data, and stores it.
        
        Args:
            name: Name of the vault
            description: Description of the vault
            owner_id: Owner ID of the vault
            owner_did: Owner DID of the vault (alternative to owner_id)
            plaintext_data: Initial plaintext data to store in the vault
            encryption_algorithm: Encryption algorithm to use
            **kwargs: Additional keyword arguments for compatibility
            
        Returns:
            Vault object
        """
        # Handle both owner_id and owner_did for compatibility
        owner_identifier = owner_id or owner_did or "unknown_owner"
        
        vault_id = str(uuid.uuid4())
        created_at = datetime.now()
        
        # Create metadata
        metadata = VaultMetadata(
            vault_id=uuid.UUID(vault_id),
            owner_did=owner_identifier,
            created_at=created_at,
            last_modified=created_at
        )
        
        # If we have plaintext data, encrypt and store it
        if plaintext_data:
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
        else:
            # Create an empty vault
            vault = Vault(metadata=metadata, data="")
        
        # Add additional attributes for API compatibility
        vault.name = name or f"vault_{vault_id[:8]}"
        vault.description = description
        vault.owner_id = owner_identifier
        vault.size_bytes = len(vault.data) if vault.data else 0
        vault.encryption_algorithm = encryption_algorithm
        vault.status = "active"
        vault.updated_at = created_at

        # Persist only after all queryable API fields are attached.
        self.storage.save_vault(vault_id, vault.model_dump_json().encode('utf-8'))
        
        # Cache the vault
        self.vaults[vault_id] = vault
        
        return vault

    def get_vault(self, vault_id: str) -> Optional[dict]:
        """
        Retrieves a vault by ID, decrypts its data, and returns a dictionary
        containing the metadata and decrypted plaintext.
        """
        try:
            # Check cache first
            if vault_id in self.vaults:
                return self.vaults[vault_id]
            
            vault_bytes = self.storage.load_vault(vault_id)
            vault_data = json.loads(vault_bytes)
            
            # Convert to Vault object
            vault = Vault(**vault_data)
            
            # Cache the vault
            self.vaults[vault_id] = vault
            
            return vault
        except FileNotFoundError:
            logging.warning(f"Vault with ID '{vault_id}' not found.")
            return None
        except Exception as e:
            logging.error(f"Error retrieving vault: {e}")
            traceback.print_exc()
            return None

    def list_vaults(self, owner_id: str = None) -> List[Vault]:
        """
        List all vaults, optionally filtered by owner.
        
        Args:
            owner_id: Optional owner ID to filter vaults
            
        Returns:
            List of vaults
        """
        try:
            records = self.storage.list_vaults(owner_id)
            vaults = [self._deserialize_vault(record) for record in records]
            for vault in vaults:
                self.vaults[vault.vault_id] = vault
            return vaults
        except NotImplementedError:
            if owner_id:
                return [vault for vault in self.vaults.values() if getattr(vault, 'owner_id', '') == owner_id]
            return list(self.vaults.values())

    def update_vault(self, vault_id: str, **kwargs) -> Optional[Vault]:
        """
        Update vault information.
        
        Args:
            vault_id: ID of the vault to update
            **kwargs: Fields to update
            
        Returns:
            Updated vault or None if not found
        """
        vault = self.get_vault(vault_id)
        if not vault:
            return None
            
        # Update fields
        for key, value in kwargs.items():
            if hasattr(vault, key):
                setattr(vault, key, value)
        
        # Update last modified time
        vault.metadata.last_modified = datetime.now()
        if hasattr(vault, 'updated_at'):
            vault.updated_at = datetime.now()
        
        # Save updated vault
        self.storage.save_vault(vault_id, vault.model_dump_json().encode('utf-8'))
        
        # Update cache
        self.vaults[vault_id] = vault
        
        return vault

    def delete_vault(self, vault_id: str):
        """Deletes a vault from storage."""
        if not self.get_vault(vault_id):
            return False

        # Remove from cache
        if vault_id in self.vaults:
            del self.vaults[vault_id]
            
        # Remove from storage
        self.storage.delete_vault(vault_id)
        return True

    def store_secret(self, vault_id: str, secret_name: str, secret_value: str, 
                     metadata: Dict[str, Any] = None) -> 'Secret':
        """
        Store a secret in a vault.
        
        Args:
            vault_id: ID of the vault to store the secret in
            secret_name: Name of the secret
            secret_value: Value of the secret
            metadata: Optional metadata for the secret
            
        Returns:
            Secret object
        """
        if not self.get_vault(vault_id):
            raise ValueError("Vault not found")

        secret_id = str(uuid.uuid4())
        now = datetime.now().isoformat()
        secret_data = {
            "secret_id": secret_id,
            "vault_id": vault_id,
            "secret_name": secret_name,
            "secret_value": self._encrypt_secret_value(secret_value),
            "metadata": metadata or {},
            "created_at": now,
            "updated_at": now,
            "version": 1
        }
        self.secrets[secret_id] = secret_data
        try:
            self.storage.save_secret(secret_id, json.dumps(secret_data).encode("utf-8"))
        except NotImplementedError:
            pass
        return Secret(**secret_data)

    def retrieve_secret(self, vault_id: str, secret_name: str) -> 'Secret':
        """
        Retrieve a secret from a vault.
        
        Args:
            vault_id: ID of the vault to retrieve the secret from
            secret_name: Name of the secret to retrieve
            
        Returns:
            Secret object
        """
        try:
            secret_bytes = self.storage.load_secret(vault_id, secret_name)
            secret_copy = json.loads(secret_bytes)
            secret_copy["secret_value"] = self._decrypt_secret_value(secret_copy["secret_value"])
            return Secret(**secret_copy)
        except NotImplementedError:
            pass
        except FileNotFoundError:
            pass

        for secret in self.secrets.values():
            if secret["vault_id"] == vault_id and secret["secret_name"] == secret_name:
                secret_copy = secret.copy()
                secret_copy["secret_value"] = self._decrypt_secret_value(secret_copy["secret_value"])
                return Secret(**secret_copy)
        raise ValueError("Secret not found")

    def _deserialize_vault(self, vault_bytes: bytes) -> Vault:
        vault_data = json.loads(vault_bytes)
        return Vault(**vault_data)
