"""
Core Cryptography Package for ReliQuary

This package contains all cryptographic implementations for the ReliQuary system,
including post-quantum cryptography, symmetric encryption, key management,
and FFI wrappers for Rust implementations.
"""

# Import core cryptographic components
from .rust_ffi_wrappers import (
    encrypt_data_rust,
    decrypt_data_rust,
    generate_kyber_keys_rust,
    encapsulate_kyber_rust,
    decapsulate_kyber_rust,
    generate_falcon_keys_rust,
    sign_falcon_rust,
    verify_falcon_rust,
    generate_keypair_rust,
    derive_key_rust
)

from .aes_gcm import (
    encrypt_aes_gcm,
    decrypt_aes_gcm
)

from .key_sharding import (
    split_key_into_shards,
    reconstruct_key_from_shards,
    KeyShard
)

__all__ = [
    # Rust FFI wrappers
    "encrypt_data_rust",
    "decrypt_data_rust",
    "generate_kyber_keys_rust",
    "encapsulate_kyber_rust",
    "decapsulate_kyber_rust",
    "generate_falcon_keys_rust",
    "sign_falcon_rust",
    "verify_falcon_rust",
    "generate_keypair_rust",
    "derive_key_rust",
    
    # AES-GCM implementations
    "encrypt_aes_gcm",
    "decrypt_aes_gcm",
    
    # Key sharding
    "split_key_into_shards",
    "reconstruct_key_from_shards",
    "KeyShard"
]