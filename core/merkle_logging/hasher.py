# core/merkle_logging/hasher.py

import hashlib

def hash_data(data: bytes) -> bytes:
    """
    Hashes the given bytes using SHA-256.
    """
    return hashlib.sha256(data).digest()

if __name__ == "__main__":
    print("--- Testing core/merkle_logging/hasher.py ---")
    test_data = b"Hello, Merkle!"
    hashed_data = hash_data(test_data)
    print(f"Original data: {test_data}")
    print(f"Hashed data (SHA-256): {hashed_data.hex()}")
    assert len(hashed_data) == 32, "Hash length should be 32 bytes for SHA-256."
    print("✅ Hasher test passed.")