# core/crypto/rust_ffi_wrappers.py

import os
import sys
import hashlib
import logging
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.exceptions import InvalidTag
import secrets
from typing import Tuple

logger = logging.getLogger(__name__)

# Determine the correct library extension based on OS
if sys.platform == "linux" or sys.platform == "linux2":
    LIB_EXT = ".so"
elif sys.platform == "darwin":
    LIB_EXT = ".dylib"
elif sys.platform == "win32":
    LIB_EXT = ".dll"
else:
    raise OSError("Unsupported operating system for shared library loading.")

# Global flag to track whether Rust modules are available
RUST_MODULES_AVAILABLE = False

# Try to import Rust modules
try:
    import reliquary_encryptor
    import reliquary_merkle
    RUST_MODULES_AVAILABLE = True
except ImportError as e:
    logger.debug("Rust crypto modules unavailable, using Python AES-GCM/Merkle fallbacks: %s", e)
    RUST_MODULES_AVAILABLE = False

# --- Python Fallback Implementations ---

class PythonCryptoFallback:
    """Python-based fallback implementations for cryptographic operations."""
    
    @staticmethod
    def encrypt_data(data: list, key: list) -> tuple[list, list]:
        """AES-GCM encryption using Python cryptography library."""
        if len(key) != 32:
            raise ValueError("Key must be 32 bytes for AES-256-GCM")
        
        key_bytes = bytes(key)
        data_bytes = bytes(data)
        
        aesgcm = AESGCM(key_bytes)
        nonce = secrets.token_bytes(12)  # 96-bit nonce for GCM
        ciphertext = aesgcm.encrypt(nonce, data_bytes, None)
        
        return list(ciphertext), list(nonce)
    
    @staticmethod
    def encrypt_data_with_nonce(data: list, key: list, nonce: list) -> list:
        """AES-GCM encryption with provided nonce."""
        if len(key) != 32:
            raise ValueError("Key must be 32 bytes for AES-256-GCM")
        if len(nonce) != 12:
            raise ValueError("Nonce must be 12 bytes for AES-GCM")
        
        key_bytes = bytes(key)
        data_bytes = bytes(data)
        nonce_bytes = bytes(nonce)
        
        aesgcm = AESGCM(key_bytes)
        ciphertext = aesgcm.encrypt(nonce_bytes, data_bytes, None)
        
        return list(ciphertext)
    
    @staticmethod
    def decrypt_data(ciphertext: bytes, nonce: bytes, key: bytes) -> list:
        """AES-GCM decryption."""
        if len(key) != 32:
            raise ValueError("Key must be 32 bytes for AES-256-GCM")
        if len(nonce) != 12:
            raise ValueError("Nonce must be 12 bytes for AES-GCM")
        
        aesgcm = AESGCM(key)
        try:
            plaintext = aesgcm.decrypt(nonce, ciphertext, None)
        except InvalidTag as exc:
            raise ValueError("Decryption failed") from exc
        
        return list(plaintext)
    
    @staticmethod
    def decrypt_data_with_nonce(ciphertext: list, key: list, nonce: list) -> list:
        """AES-GCM decryption with provided nonce."""
        ciphertext_bytes = bytes(ciphertext)
        key_bytes = bytes(key)
        nonce_bytes = bytes(nonce)
        
        return PythonCryptoFallback.decrypt_data(ciphertext_bytes, nonce_bytes, key_bytes)
    
    @staticmethod
    def generate_kyber_keys() -> tuple[list, list]:
        """Kyber is intentionally unavailable without the Rust extension."""
        raise RuntimeError("Kyber requires the reliquary_encryptor Rust module. Run scripts/build_rust_modules.sh.")
    
    @staticmethod
    def encapsulate_kyber(public_key: list) -> tuple[list, list]:
        """Kyber is intentionally unavailable without the Rust extension."""
        raise RuntimeError("Kyber requires the reliquary_encryptor Rust module. Run scripts/build_rust_modules.sh.")
    
    @staticmethod
    def decapsulate_kyber(ciphertext: list, secret_key: list) -> list:
        """Kyber is intentionally unavailable without the Rust extension."""
        raise RuntimeError("Kyber requires the reliquary_encryptor Rust module. Run scripts/build_rust_modules.sh.")
    
    @staticmethod
    def generate_falcon_keys() -> tuple[list, list]:
        """Falcon is intentionally unavailable without the Rust extension."""
        raise RuntimeError("Falcon requires the reliquary_encryptor Rust module. Run scripts/build_rust_modules.sh.")
    
    @staticmethod
    def sign_falcon(message: list, secret_key: list) -> list:
        """Falcon is intentionally unavailable without the Rust extension."""
        raise RuntimeError("Falcon requires the reliquary_encryptor Rust module. Run scripts/build_rust_modules.sh.")
    
    @staticmethod
    def verify_falcon(message: list, signature: list, public_key: list) -> bool:
        """Falcon is intentionally unavailable without the Rust extension."""
        raise RuntimeError("Falcon requires the reliquary_encryptor Rust module. Run scripts/build_rust_modules.sh.")
    
    @staticmethod
    def create_merkle_root(data_blocks: list) -> list:
        """Create Merkle root using our Python implementation."""
        from ..merkle_logging.merkle import create_merkle_root
        
        # Convert list of lists to list of bytes
        byte_blocks = [bytes(block) for block in data_blocks]
        root = create_merkle_root(byte_blocks)
        
        return list(root)
    
    @staticmethod
    def verify_merkle_proof(data_block: list, proof: list, root: list) -> bool:
        """Verify a simplified lexicographic Merkle proof."""
        current_hash = hashlib.sha256(bytes(data_block)).digest()

        for proof_hash in proof:
            sibling = bytes(proof_hash)
            if current_hash < sibling:
                current_hash = hashlib.sha256(current_hash + sibling).digest()
            else:
                current_hash = hashlib.sha256(sibling + current_hash).digest()

        return current_hash == bytes(root)

# Create the module interface
if RUST_MODULES_AVAILABLE:
    # Use actual Rust modules
    crypto_module = reliquary_encryptor
    merkle_module = reliquary_merkle
else:
    # Use Python fallback
    crypto_module = PythonCryptoFallback()
    merkle_module = PythonCryptoFallback()


# --- High-level API Functions ---

def encrypt_data_rust(data: bytes, key: bytes) -> tuple[bytes, bytes]:
    """Encrypts data using AES-GCM. Returns (ciphertext_with_tag, nonce)."""
    ciphertext_with_tag_list, nonce_list = crypto_module.encrypt_data(list(data), list(key))
    return bytes(ciphertext_with_tag_list), bytes(nonce_list)

def encrypt_data_with_nonce_rust(data: bytes, key: bytes, nonce: bytes) -> bytes:
    """Encrypts data using AES-GCM with a provided nonce. Returns ciphertext_with_tag."""
    ciphertext_with_tag_list = crypto_module.encrypt_data_with_nonce(list(data), list(key), list(nonce))
    return bytes(ciphertext_with_tag_list)

def decrypt_data_rust(ciphertext_with_tag: bytes, nonce: bytes, key: bytes) -> bytes:
    """Decrypts data using AES-GCM."""
    plaintext_list = crypto_module.decrypt_data(ciphertext_with_tag, nonce, key)
    return bytes(plaintext_list)

def decrypt_data_with_nonce_rust(ciphertext_with_tag: bytes, key: bytes, nonce: bytes) -> bytes:
    """Decrypts data using AES-GCM with explicit nonce."""
    plaintext_list = crypto_module.decrypt_data_with_nonce(list(ciphertext_with_tag), list(key), list(nonce))
    return bytes(plaintext_list)

# --- Post-Quantum Cryptography Functions ---

def generate_kyber_keys_rust() -> tuple[bytes, bytes]:
    """Generates Kyber public and secret keys."""
    pub_key, sec_key = crypto_module.generate_kyber_keys()
    return bytes(pub_key), bytes(sec_key)

def encapsulate_kyber_rust(public_key: bytes) -> tuple[bytes, bytes]:
    """Encapsulates a shared secret using Kyber public key."""
    ciphertext, shared_secret = crypto_module.encapsulate_kyber(list(public_key))
    return bytes(ciphertext), bytes(shared_secret)

def decapsulate_kyber_rust(ciphertext: bytes, secret_key: bytes) -> bytes:
    """Decapsulates a shared secret using Kyber secret key."""
    shared_secret = crypto_module.decapsulate_kyber(list(ciphertext), list(secret_key))
    return bytes(shared_secret)

def generate_falcon_keys_rust() -> tuple[bytes, bytes]:
    """Generates Falcon public and secret keys."""
    pub_key, sec_key = crypto_module.generate_falcon_keys()
    return bytes(pub_key), bytes(sec_key)

def sign_falcon_rust(message: bytes, secret_key: bytes) -> bytes:
    """Signs a message using Falcon secret key."""
    signature = crypto_module.sign_falcon(list(message), list(secret_key))
    return bytes(signature)

def verify_falcon_rust(message: bytes, signature: bytes, public_key: bytes) -> bool:
    """Verifies a message signature using Falcon public key."""
    return crypto_module.verify_falcon(list(message), list(signature), list(public_key))

# --- Generic Key Generation Functions for Backward Compatibility ---

def generate_keypair_rust() -> tuple[bytes, bytes]:
    """Generate a generic keypair using Kyber post-quantum algorithm."""
    return generate_kyber_keys_rust()

def derive_key_rust(shared_secret: bytes, info: bytes = b"") -> bytes:
    """Derive a key from shared secret using HKDF-SHA256."""
    from cryptography.hazmat.primitives import hashes
    from cryptography.hazmat.primitives.kdf.hkdf import HKDF
    from cryptography.hazmat.backends import default_backend
    
    # Use HKDF to derive a 32-byte key
    hkdf = HKDF(
        algorithm=hashes.SHA256(),
        length=32,
        salt=None,
        info=info,
        backend=default_backend()
    )
    return hkdf.derive(shared_secret)

# --- Merkle Tree Functions ---

def create_merkle_root_rust(data_blocks: list[bytes]) -> bytes:
    """Creates a Merkle root from data blocks."""
    rust_data_blocks = [list(block) for block in data_blocks]
    root = merkle_module.create_merkle_root(rust_data_blocks)
    return bytes(root)

def verify_merkle_proof_rust(data_block: bytes, proof: list[bytes], root: bytes) -> bool:
    """Verifies a Merkle proof."""
    rust_proof = [list(p) for p in proof]
    return merkle_module.verify_merkle_proof(list(data_block), rust_proof, list(root))

# --- Backward Compatibility Functions ---

def encrypt_data(data: bytes, key: bytes) -> Tuple[bytes, bytes]:
    """Encrypts data using AES-GCM (backward compatibility function).
    Returns (ciphertext_with_tag, nonce)."""
    return encrypt_data_rust(data, key)

def decrypt_data(encrypted_data: bytes, key: bytes, nonce: bytes) -> bytes:
    """Decrypts data using AES-GCM (backward compatibility function)."""
    return decrypt_data_rust(encrypted_data, nonce, key)

def generate_keypair(algorithm: str = "kyber") -> Tuple[bytes, bytes]:
    """Generate a keypair using the specified algorithm (backward compatibility function)."""
    if algorithm.lower() == "kyber":
        return generate_kyber_keys_rust()
    elif algorithm.lower() == "falcon":
        return generate_falcon_keys_rust()
    else:
        # Default to Kyber for unknown algorithms
        return generate_kyber_keys_rust()

def sign_message(message: bytes, private_key: bytes, algorithm: str = "falcon") -> bytes:
    """Sign a message using the specified algorithm (backward compatibility function)."""
    if algorithm.lower() == "falcon":
        return sign_falcon_rust(message, private_key)
    else:
        # Default to Falcon for unknown algorithms
        return sign_falcon_rust(message, private_key)

def verify_signature(message: bytes, signature: bytes, public_key: bytes, algorithm: str = "falcon") -> bool:
    """Verify a signature using the specified algorithm (backward compatibility function)."""
    if algorithm.lower() == "falcon":
        return verify_falcon_rust(message, signature, public_key)
    else:
        # Default to Falcon for unknown algorithms
        return verify_falcon_rust(message, signature, public_key)

# --- Utility Functions ---

def get_crypto_backend_info() -> dict:
    """Get information about which crypto backend is being used."""
    return {
        "rust_available": RUST_MODULES_AVAILABLE,
        "backend": "rust" if RUST_MODULES_AVAILABLE else "python",
        "aes_gcm_available": True,
        "post_quantum_available": RUST_MODULES_AVAILABLE,  # PQC only available with Rust
        "merkle_available": True
    }

def is_post_quantum_available() -> bool:
    """Check if post-quantum cryptography is available."""
    return RUST_MODULES_AVAILABLE

if __name__ == "__main__":
    print("--- Testing FFI Wrappers ---")
    
    # Test crypto backend info
    backend_info = get_crypto_backend_info()
    print(f"Backend info: {backend_info}")
    
    # Test AES-GCM encryption
    test_data = b"Hello, ReliQuary!"
    test_key = secrets.token_bytes(32)
    
    try:
        ciphertext, nonce = encrypt_data_rust(test_data, test_key)
        decrypted = decrypt_data_rust(ciphertext, nonce, test_key)
        
        print(f"AES-GCM test: {'PASS' if decrypted == test_data else 'FAIL'}")
        print(f"Original: {test_data}")
        print(f"Decrypted: {decrypted}")
    except Exception as e:
        print(f"AES-GCM test failed: {e}")
    
    # Test Kyber when Rust modules are installed.
    try:
        kyber_pub, kyber_sec = generate_kyber_keys_rust()
        ciphertext, shared_secret1 = encapsulate_kyber_rust(kyber_pub)
        shared_secret2 = decapsulate_kyber_rust(ciphertext, kyber_sec)
        
        print("Kyber test: generated keys and performed encapsulation")
        print(f"Public key size: {len(kyber_pub)} bytes")
        print(f"Secret key size: {len(kyber_sec)} bytes")
        print(f"Shared secret size: {len(shared_secret1)} bytes")
    except Exception as e:
        print(f"Kyber test failed: {e}")
    
    # Test Falcon when Rust modules are installed.
    try:
        falcon_pub, falcon_sec = generate_falcon_keys_rust()
        signature = sign_falcon_rust(test_data, falcon_sec)
        is_valid = verify_falcon_rust(test_data, signature, falcon_pub)
        
        print(f"Falcon test: {'PASS' if is_valid else 'FAIL'}")
        print(f"Public key size: {len(falcon_pub)} bytes")
        print(f"Secret key size: {len(falcon_sec)} bytes")
        print(f"Signature size: {len(signature)} bytes")
    except Exception as e:
        print(f"Falcon test failed: {e}")
    
    # Test Merkle
    try:
        test_blocks = [b"block1", b"block2", b"block3"]
        merkle_root = create_merkle_root_rust(test_blocks)
        
        print(f"Merkle test: Created root")
        print(f"Root: {merkle_root.hex()[:16]}...")
        print(f"Root size: {len(merkle_root)} bytes")
    except Exception as e:
        print(f"Merkle test failed: {e}")
    
    print("✅ FFI wrapper tests completed")
