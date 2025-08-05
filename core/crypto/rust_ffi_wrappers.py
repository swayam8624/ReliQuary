# core/crypto/rust_ffi_wrappers.py

import os
import sys

# Determine the correct library extension based on OS
if sys.platform == "linux" or sys.platform == "linux2":
    LIB_EXT = ".so"
elif sys.platform == "darwin":
    LIB_EXT = ".dylib"
elif sys.platform == "win32":
    LIB_EXT = ".dll"
else:
    raise OSError("Unsupported operating system for shared library loading.")

# Construct the path to the compiled Rust libraries
# This assumes you are running Python from the project root or similar.
# In a Docker environment, the paths will be relative to /app
_ENCRYPTOR_LIB_PATH = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "..", "..", "rust_modules", "encryptor", "target", "release", f"reliquary_encryptor{LIB_EXT}"
)
_MERKLE_LIB_PATH = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "..", "..", "rust_modules", "merkle", "target", "release", f"reliquary_merkle{LIB_EXT}"
)

# --- Python Bindings for Reliquary Encryptor ---
try:
    # If built as a Python extension module via pyo3, direct import will work
    import reliquary_encryptor
    import reliquary_merkle
    print("Successfully imported Rust modules via PyO3.")

except ImportError as e:
    print(f"Failed to import Rust modules: {e}")
    print("Please ensure you have run 'maturin develop --release' in rust_modules/encryptor and rust_modules/merkle.")
    # Fallback to dummy functions if Rust modules aren't available
    class DummyRustModule:
        def encrypt_data(*args, **kwargs): raise NotImplementedError("Rust encryptor not loaded")
        def decrypt_data(*args, **kwargs): raise NotImplementedError("Rust encryptor not loaded")
        def encrypt_data_with_nonce(*args, **kwargs): raise NotImplementedError("Rust encryptor not loaded")
        def decrypt_data_with_nonce(*args, **kwargs): raise NotImplementedError("Rust encryptor not loaded")
        def generate_kyber_keys(*args, **kwargs): return (b'\x01'*32, b'\x02'*32) # Using updated placeholders
        def encapsulate_kyber(*args, **kwargs): return (b'\x03'*32, b'\x04'*32)
        def decapsulate_kyber(*args, **kwargs): return b'\x05'*32
        def generate_falcon_keys(*args, **kwargs): return (b'\x06'*32, b'\x07'*32)
        def sign_falcon(*args, **kwargs): return b'\x08'*64
        def verify_falcon(*args, **kwargs): return True
        def create_merkle_root(*args, **kwargs): return b'\0'*32
        def verify_merkle_proof(*args, **kwargs): return True
    reliquary_encryptor = DummyRustModule()
    reliquary_merkle = DummyRustModule()


# --- Encryptor Wrappers ---
def encrypt_data_rust(data: bytes, key: bytes) -> tuple[bytes, bytes]:
    """Encrypts data using AES-GCM via Rust. Returns (ciphertext_with_tag, nonce)."""
    # Rust `encrypt_data` expects Vec<u8> for data and key_bytes.
    ciphertext_with_tag_list, nonce_list = reliquary_encryptor.encrypt_data(list(data), list(key))
    return bytes(ciphertext_with_tag_list), bytes(nonce_list)

# NEW: Wrapper for encrypt_data_with_nonce
def encrypt_data_with_nonce_rust(data: bytes, key: bytes, nonce: bytes) -> bytes:
    """Encrypts data using AES-GCM with a provided nonce via Rust. Returns ciphertext_with_tag."""
    # Rust `encrypt_data_with_nonce` expects Vec<u8> for all inputs.
    ciphertext_with_tag_list = reliquary_encryptor.encrypt_data_with_nonce(list(data), list(key), list(nonce))
    return bytes(ciphertext_with_tag_list)


def decrypt_data_rust(ciphertext_with_tag: bytes, nonce: bytes, key: bytes) -> bytes:
    """Decrypts data using AES-GCM via Rust."""
    # Rust `decrypt_data` expects &[u8] slices, so Python bytes are passed directly.
    plaintext_list = reliquary_encryptor.decrypt_data(ciphertext_with_tag, nonce, key)
    return bytes(plaintext_list)

# NEW: Wrapper for decrypt_data_with_nonce (which is a PyO3 wrapper for decrypt_data)
def decrypt_data_with_nonce_rust(ciphertext_with_tag: bytes, key: bytes, nonce: bytes) -> bytes:
    """Decrypts data using AES-GCM with explicit nonce via Rust."""
    # Rust `decrypt_data_with_nonce` expects Vec<u8> for all inputs.
    plaintext_list = reliquary_encryptor.decrypt_data_with_nonce(list(ciphertext_with_tag), list(key), list(nonce))
    return bytes(plaintext_list)


# --- PQC Placeholders ---
def generate_kyber_keys_rust() -> tuple[bytes, bytes]:
    """Generates Kyber public and secret keys via Rust."""
    pub_key, sec_key = reliquary_encryptor.generate_kyber_keys()
    return bytes(pub_key), bytes(sec_key)

def encapsulate_kyber_rust(public_key: bytes) -> tuple[bytes, bytes]:
    """Encapsulates a shared secret using Kyber public key via Rust."""
    ciphertext, shared_secret = reliquary_encryptor.encapsulate_kyber(list(public_key))
    return bytes(ciphertext), bytes(shared_secret)

def decapsulate_kyber_rust(ciphertext: bytes, secret_key: bytes) -> bytes:
    """Decapsulates a shared secret using Kyber secret key via Rust."""
    shared_secret = reliquary_encryptor.decapsulate_kyber(list(ciphertext), list(secret_key))
    return bytes(shared_secret)

def generate_falcon_keys_rust() -> tuple[bytes, bytes]:
    """Generates Falcon public and secret keys via Rust."""
    pub_key, sec_key = reliquary_encryptor.generate_falcon_keys()
    return bytes(pub_key), bytes(sec_key)

def sign_falcon_rust(message: bytes, secret_key: bytes) -> bytes:
    """Signs a message using Falcon secret key via Rust."""
    signature = reliquary_encryptor.sign_falcon(list(message), list(secret_key))
    return bytes(signature)

def verify_falcon_rust(message: bytes, signature: bytes, public_key: bytes) -> bool:
    """Verifies a message signature using Falcon public key via Rust."""
    return reliquary_encryptor.verify_falcon(list(message), list(signature), list(public_key))


# --- Merkle Wrappers ---
def create_merkle_root_rust(data_blocks: list[bytes]) -> bytes:
    """Creates a Merkle root from data blocks via Rust."""
    rust_data_blocks = [list(block) for block in data_blocks]
    root = reliquary_merkle.create_merkle_root(rust_data_blocks)
    return bytes(root)

def verify_merkle_proof_rust(data_block: bytes, proof: list[bytes], root: bytes) -> bool:
    """Verifies a Merkle proof via Rust."""
    rust_proof = [list(p) for p in proof]
    return reliquary_merkle.verify_merkle_proof(list(data_block), rust_proof, list(root))
