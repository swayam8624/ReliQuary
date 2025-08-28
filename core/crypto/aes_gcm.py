# core/crypto/aes_gcm.py
import os
# FIXED: Import updated FFI wrappers
from core.crypto.rust_ffi_wrappers import encrypt_data_rust, decrypt_data_rust, encrypt_data_with_nonce_rust, decrypt_data_with_nonce_rust
import config_package

# AES-GCM-256 uses 32-byte key, 12-byte nonce, and produces a 16-byte authentication tag
# (These constants are now imported from config_package in test_crypto.py)
# AES_GCM_KEY_LEN = 32 # This constant is in config_package
# AES_GCM_NONCE_LEN = 12 # This constant is in config_package

def encrypt(data: bytes, key: bytes) -> tuple[bytes, bytes, bytes]:
    """
    Encrypts data using AES-GCM-256.
    Generates a unique nonce internally.
    Returns (ciphertext, nonce, tag).
    """
    if len(key) != config_package.AES_GCM_KEY_LEN:
        raise ValueError(f"AES key must be {config_package.AES_GCM_KEY_LEN} bytes long for AES-256-GCM.")

    # Rust function now generates nonce and returns (ciphertext+tag, nonce)
    ciphertext_and_tag, nonce = encrypt_data_rust(data, key)
    
    # Assuming the tag is 16 bytes and concatenated to ciphertext
    ciphertext = ciphertext_and_tag[:-16]
    tag = ciphertext_and_tag[-16:]

    return ciphertext, nonce, tag

def encrypt_with_provided_nonce(data: bytes, key: bytes, nonce: bytes) -> tuple[bytes, bytes]:
    """
    Encrypts data using AES-GCM-256 with an explicitly provided nonce.
    Returns (ciphertext, tag).
    Caller is responsible for unique nonce generation.
    """
    if len(key) != config_package.AES_GCM_KEY_LEN:
        raise ValueError(f"AES key must be {config_package.AES_GCM_KEY_LEN} bytes long for AES-256-GCM.")
    if len(nonce) != config_package.AES_GCM_NONCE_LEN:
        raise ValueError(f"Nonce must be {config_package.AES_GCM_NONCE_LEN} bytes long.")
    
    # Rust function returns only ciphertext+tag
    ciphertext_and_tag = encrypt_data_with_nonce_rust(data, key, nonce)

    # Assuming the tag is 16 bytes and concatenated to ciphertext
    ciphertext = ciphertext_and_tag[:-16]
    tag = ciphertext_and_tag[-16:]

    return ciphertext, tag


def decrypt(ciphertext: bytes, nonce: bytes, tag: bytes, key: bytes) -> bytes:
    """
    Decrypts data using AES-GCM-256.
    Takes (ciphertext, nonce, tag, key).
    """
    if len(key) != config_package.AES_GCM_KEY_LEN:
        raise ValueError(f"AES key must be {config_package.AES_GCM_KEY_LEN} bytes long for AES-256-GCM.")
    if len(nonce) != config_package.AES_GCM_NONCE_LEN:
        raise ValueError(f"AES-GCM nonce must be {config_package.AES_GCM_NONCE_LEN} bytes long.")
    if len(tag) != 16: # AES-GCM authentication tag is typically 16 bytes
        raise ValueError("AES-GCM tag must be 16 bytes long.")

    ciphertext_with_tag = ciphertext + tag
    
    # decrypt_data_rust takes bytes for ciphertext_with_tag, nonce, key
    plaintext = decrypt_data_rust(ciphertext_with_tag, nonce, key)
    return plaintext

# NEW: For advanced use or if it maps to a direct Rust function
def decrypt_with_provided_nonce(ciphertext: bytes, key: bytes, nonce: bytes, tag: bytes) -> bytes:
    """
    Decrypts data using AES-GCM-256 with explicitly provided nonce and key.
    This maps to the Rust decrypt_data_with_nonce wrapper.
    """
    if len(key) != config_package.AES_GCM_KEY_LEN:
        raise ValueError(f"AES key must be {config_package.AES_GCM_KEY_LEN} bytes long for AES-256-GCM.")
    if len(nonce) != config_package.AES_GCM_NONCE_LEN:
        raise ValueError(f"AES-GCM nonce must be {config_package.AES_GCM_NONCE_LEN} bytes long.")
    if len(tag) != 16:
        raise ValueError("AES-GCM tag must be 16 bytes long.")

    ciphertext_with_tag = ciphertext + tag
    
    plaintext = decrypt_data_with_nonce_rust(ciphertext_with_tag, key, nonce) # Note: Rust decrypt_data_with_nonce takes (ciphertext_with_tag, key, nonce) order
    return plaintext


def encrypt_aes_gcm(data: bytes, key: bytes) -> tuple[bytes, bytes, bytes]:
    """
    Encrypts data using AES-GCM-256 (alias for encrypt function).
    Generates a unique nonce internally.
    Returns (ciphertext, nonce, tag).
    """
    return encrypt(data, key)


def decrypt_aes_gcm(ciphertext: bytes, nonce: bytes, tag: bytes, key: bytes) -> bytes:
    """
    Decrypts data using AES-GCM-256 (alias for decrypt function).
    Takes (ciphertext, nonce, tag, key).
    """
    return decrypt(ciphertext, nonce, tag, key)
