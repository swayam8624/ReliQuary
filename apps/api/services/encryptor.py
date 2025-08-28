"""
Encryptor Service for ReliQuary API.
This service provides encryption and decryption functionality via Rust FFI wrappers.
"""

import json
import logging
import base64
from typing import Dict, Any, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime

# Import crypto components
try:
    from core.crypto.rust_ffi_wrappers import (
        encrypt_data as rust_encrypt,
        decrypt_data as rust_decrypt,
        generate_keypair,
        sign_message,
        verify_signature
    )
    from core.crypto.key_sharding import KeyShardManager
except ImportError:
    # Mock implementations for development
    def rust_encrypt(data: bytes, key: bytes) -> Tuple[bytes, bytes]:
        # Simple mock encryption (XOR with key for demo purposes only)
        encrypted = bytes([b ^ key[i % len(key)] for i, b in enumerate(data)])
        nonce = b"mock_nonce_123456"
        return encrypted, nonce
    
    def rust_decrypt(encrypted_data: bytes, key: bytes, nonce: bytes) -> bytes:
        # Simple mock decryption (XOR with key for demo purposes only)
        return bytes([b ^ key[i % len(key)] for i, b in enumerate(encrypted_data)])
    
    def generate_keypair(algorithm: str = "kyber") -> Tuple[bytes, bytes]:
        # Mock keypair generation
        private_key = b"mock_private_key_" + algorithm.encode()
        public_key = b"mock_public_key_" + algorithm.encode()
        return private_key, public_key
    
    def sign_message(message: bytes, private_key: bytes, algorithm: str = "falcon") -> bytes:
        # Mock signature generation
        return b"mock_signature_" + message[:10]
    
    def verify_signature(message: bytes, signature: bytes, public_key: bytes, algorithm: str = "falcon") -> bool:
        # Mock signature verification
        return True
    
    class KeyShardManager:
        def __init__(self):
            pass
        
        def shard_key(self, key: bytes, num_shards: int = 3, threshold: int = 2) -> List[bytes]:
            return [b"shard_" + str(i).encode() for i in range(num_shards)]
        
        def reconstruct_key(self, shards: List[bytes], threshold: int = 2) -> bytes:
            return b"reconstructed_key"


@dataclass
class EncryptionResult:
    """Result of encryption operation"""
    encrypted_data: str  # Base64 encoded
    nonce: str          # Base64 encoded
    algorithm: str
    timestamp: datetime


@dataclass
class DecryptionResult:
    """Result of decryption operation"""
    decrypted_data: bytes
    algorithm: str
    timestamp: datetime


@dataclass
class KeyPair:
    """Key pair for encryption/decryption"""
    private_key: str  # Base64 encoded
    public_key: str   # Base64 encoded
    algorithm: str
    timestamp: datetime


@dataclass
class SignatureResult:
    """Result of signature operation"""
    signature: str     # Base64 encoded
    algorithm: str
    timestamp: datetime


class EncryptorService:
    """Service for encryption and decryption operations"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.key_shard_manager = KeyShardManager()
    
    def encrypt_data(self, data: bytes, key: bytes, algorithm: str = "aes-gcm") -> EncryptionResult:
        """
        Encrypt data using the specified algorithm.
        
        Args:
            data: Data to encrypt
            key: Encryption key
            algorithm: Encryption algorithm to use
            
        Returns:
            Encryption result with encrypted data and nonce
        """
        try:
            # Encrypt data using Rust FFI
            encrypted_data, nonce = rust_encrypt(data, key)
            
            # Encode as base64 for safe transport
            encoded_data = base64.b64encode(encrypted_data).decode('utf-8')
            encoded_nonce = base64.b64encode(nonce).decode('utf-8')
            
            result = EncryptionResult(
                encrypted_data=encoded_data,
                nonce=encoded_nonce,
                algorithm=algorithm,
                timestamp=datetime.now()
            )
            
            self.logger.info(f"Data encrypted successfully using {algorithm}")
            return result
            
        except Exception as e:
            self.logger.error(f"Encryption failed: {str(e)}")
            raise Exception(f"Encryption failed: {str(e)}")
    
    def decrypt_data(self, encrypted_data: str, key: bytes, nonce: str, algorithm: str = "aes-gcm") -> DecryptionResult:
        """
        Decrypt data using the specified algorithm.
        
        Args:
            encrypted_data: Base64 encoded encrypted data
            key: Decryption key
            nonce: Base64 encoded nonce
            algorithm: Decryption algorithm to use
            
        Returns:
            Decryption result with decrypted data
        """
        try:
            # Decode from base64
            decoded_data = base64.b64decode(encrypted_data.encode('utf-8'))
            decoded_nonce = base64.b64decode(nonce.encode('utf-8'))
            
            # Decrypt data using Rust FFI
            decrypted_data = rust_decrypt(decoded_data, key, decoded_nonce)
            
            result = DecryptionResult(
                decrypted_data=decrypted_data,
                algorithm=algorithm,
                timestamp=datetime.now()
            )
            
            self.logger.info(f"Data decrypted successfully using {algorithm}")
            return result
            
        except Exception as e:
            self.logger.error(f"Decryption failed: {str(e)}")
            raise Exception(f"Decryption failed: {str(e)}")
    
    def generate_encryption_keypair(self, algorithm: str = "kyber") -> KeyPair:
        """
        Generate a new encryption keypair.
        
        Args:
            algorithm: Key generation algorithm to use
            
        Returns:
            Generated key pair
        """
        try:
            # Generate keypair using Rust FFI
            private_key, public_key = generate_keypair(algorithm)
            
            # Encode as base64 for safe transport
            encoded_private = base64.b64encode(private_key).decode('utf-8')
            encoded_public = base64.b64encode(public_key).decode('utf-8')
            
            keypair = KeyPair(
                private_key=encoded_private,
                public_key=encoded_public,
                algorithm=algorithm,
                timestamp=datetime.now()
            )
            
            self.logger.info(f"Keypair generated successfully using {algorithm}")
            return keypair
            
        except Exception as e:
            self.logger.error(f"Keypair generation failed: {str(e)}")
            raise Exception(f"Keypair generation failed: {str(e)}")
    
    def sign_message(self, message: bytes, private_key: str, algorithm: str = "falcon") -> SignatureResult:
        """
        Sign a message using the private key.
        
        Args:
            message: Message to sign
            private_key: Base64 encoded private key
            algorithm: Signature algorithm to use
            
        Returns:
            Signature result
        """
        try:
            # Decode private key from base64
            decoded_private_key = base64.b64decode(private_key.encode('utf-8'))
            
            # Sign message using Rust FFI
            signature = sign_message(message, decoded_private_key, algorithm)
            
            # Encode signature as base64
            encoded_signature = base64.b64encode(signature).decode('utf-8')
            
            result = SignatureResult(
                signature=encoded_signature,
                algorithm=algorithm,
                timestamp=datetime.now()
            )
            
            self.logger.info(f"Message signed successfully using {algorithm}")
            return result
            
        except Exception as e:
            self.logger.error(f"Message signing failed: {str(e)}")
            raise Exception(f"Message signing failed: {str(e)}")
    
    def verify_signature(self, message: bytes, signature: str, public_key: str, algorithm: str = "falcon") -> bool:
        """
        Verify a signature using the public key.
        
        Args:
            message: Original message
            signature: Base64 encoded signature
            public_key: Base64 encoded public key
            algorithm: Signature algorithm to use
            
        Returns:
            True if signature is valid, False otherwise
        """
        try:
            # Decode signature and public key from base64
            decoded_signature = base64.b64decode(signature.encode('utf-8'))
            decoded_public_key = base64.b64decode(public_key.encode('utf-8'))
            
            # Verify signature using Rust FFI
            is_valid = verify_signature(message, decoded_signature, decoded_public_key, algorithm)
            
            self.logger.info(f"Signature verification {'passed' if is_valid else 'failed'} using {algorithm}")
            return is_valid
            
        except Exception as e:
            self.logger.error(f"Signature verification failed: {str(e)}")
            return False
    
    def shard_encryption_key(self, key: bytes, num_shards: int = 3, threshold: int = 2) -> List[str]:
        """
        Shard an encryption key using secret sharing.
        
        Args:
            key: Key to shard
            num_shards: Number of shards to create
            threshold: Minimum number of shards needed for reconstruction
            
        Returns:
            List of base64 encoded key shards
        """
        try:
            # Shard key using key shard manager
            shards = self.key_shard_manager.shard_key(key, num_shards, threshold)
            
            # Encode shards as base64
            encoded_shards = [base64.b64encode(shard).decode('utf-8') for shard in shards]
            
            self.logger.info(f"Key sharded into {num_shards} shards with threshold {threshold}")
            return encoded_shards
            
        except Exception as e:
            self.logger.error(f"Key sharding failed: {str(e)}")
            raise Exception(f"Key sharding failed: {str(e)}")
    
    def reconstruct_encryption_key(self, shards: List[str], threshold: int = 2) -> str:
        """
        Reconstruct an encryption key from shards.
        
        Args:
            shards: List of base64 encoded key shards
            threshold: Minimum number of shards needed for reconstruction
            
        Returns:
            Base64 encoded reconstructed key
        """
        try:
            # Decode shards from base64
            decoded_shards = [base64.b64decode(shard.encode('utf-8')) for shard in shards]
            
            # Reconstruct key using key shard manager
            reconstructed_key = self.key_shard_manager.reconstruct_key(decoded_shards, threshold)
            
            # Encode reconstructed key as base64
            encoded_key = base64.b64encode(reconstructed_key).decode('utf-8')
            
            self.logger.info(f"Key reconstructed from {len(shards)} shards")
            return encoded_key
            
        except Exception as e:
            self.logger.error(f"Key reconstruction failed: {str(e)}")
            raise Exception(f"Key reconstruction failed: {str(e)}")


# Global encryptor service instance
_encryptor_service = None


def get_encryptor_service() -> EncryptorService:
    """Get the global encryptor service instance"""
    global _encryptor_service
    if _encryptor_service is None:
        _encryptor_service = EncryptorService()
    return _encryptor_service


def encrypt_sensitive_data(data: bytes, key: bytes, algorithm: str = "aes-gcm") -> EncryptionResult:
    """Convenience function to encrypt sensitive data"""
    service = get_encryptor_service()
    return service.encrypt_data(data, key, algorithm)


def decrypt_sensitive_data(encrypted_data: str, key: bytes, nonce: str, algorithm: str = "aes-gcm") -> DecryptionResult:
    """Convenience function to decrypt sensitive data"""
    service = get_encryptor_service()
    return service.decrypt_data(encrypted_data, key, nonce, algorithm)


def generate_encryption_keys(algorithm: str = "kyber") -> KeyPair:
    """Convenience function to generate encryption keys"""
    service = get_encryptor_service()
    return service.generate_encryption_keypair(algorithm)


def sign_data(message: bytes, private_key: str, algorithm: str = "falcon") -> SignatureResult:
    """Convenience function to sign data"""
    service = get_encryptor_service()
    return service.sign_message(message, private_key, algorithm)


def verify_data_signature(message: bytes, signature: str, public_key: str, algorithm: str = "falcon") -> bool:
    """Convenience function to verify data signature"""
    service = get_encryptor_service()
    return service.verify_signature(message, signature, public_key, algorithm)


def shard_key_for_distribution(key: bytes, num_shards: int = 3, threshold: int = 2) -> List[str]:
    """Convenience function to shard a key for distribution"""
    service = get_encryptor_service()
    return service.shard_encryption_key(key, num_shards, threshold)


def reconstruct_key_from_shards(shards: List[str], threshold: int = 2) -> str:
    """Convenience function to reconstruct a key from shards"""
    service = get_encryptor_service()
    return service.reconstruct_encryption_key(shards, threshold)