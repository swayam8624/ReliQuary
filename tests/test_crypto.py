# tests/test_crypto.py

import pytest
import os
import hashlib
from unittest.mock import patch
import requests

# Import specific functions and constants
# FIXED: Import new functions from aes_gcm
from core.crypto.aes_gcm import encrypt, decrypt, encrypt_with_provided_nonce, decrypt_with_provided_nonce
from core.crypto import key_sharding
from core.crypto.rust_ffi_wrappers import (
    create_merkle_root_rust, verify_merkle_proof_rust,
    generate_kyber_keys_rust, encapsulate_kyber_rust, decapsulate_kyber_rust,
    generate_falcon_keys_rust, sign_falcon_rust, verify_falcon_rust,
)
import config_package 

# --- Fixtures for common test data ---

@pytest.fixture
def aes_key_256():
    """A 256-bit AES key."""
    return os.urandom(config_package.AES_GCM_KEY_LEN)

@pytest.fixture
def sample_plaintext():
    """A sample plaintext for encryption."""
    return b"This is a secret message for testing AES-GCM encryption."

@pytest.fixture
def sample_merkle_blocks():
    """A list of data blocks for Merkle tree testing."""
    return [
        b"block 1 data",
        b"block 2 data",
        b"block 3 data",
        b"block 4 data with some more content",
    ]

# --- Test AES-GCM Encryption/Decryption ---

def test_aes_gcm_encrypt_decrypt_roundtrip(sample_plaintext, aes_key_256):
    """Test successful encryption and decryption of data (nonce generated internally)."""
    ciphertext, nonce, tag = encrypt(sample_plaintext, aes_key_256)
    
    assert isinstance(ciphertext, bytes)
    assert isinstance(nonce, bytes)
    assert isinstance(tag, bytes)
    assert len(nonce) == config_package.AES_GCM_NONCE_LEN
    assert len(tag) == 16 

    decrypted_plaintext = decrypt(ciphertext, nonce, tag, aes_key_256)
    
    assert decrypted_plaintext == sample_plaintext, "Decrypted plaintext should match original plaintext"

def test_aes_gcm_encrypt_decrypt_with_provided_nonce_roundtrip(sample_plaintext, aes_key_256):
    """Test successful encryption and decryption when nonce is explicitly provided."""
    provided_nonce = os.urandom(config_package.AES_GCM_NONCE_LEN)
    
    ciphertext, tag = encrypt_with_provided_nonce(sample_plaintext, aes_key_256, provided_nonce)
    
    assert isinstance(ciphertext, bytes)
    assert isinstance(tag, bytes)
    assert len(tag) == 16

    decrypted_plaintext = decrypt_with_provided_nonce(ciphertext, aes_key_256, provided_nonce, tag)
    
    assert decrypted_plaintext == sample_plaintext, "Decrypted plaintext (with provided nonce) should match original plaintext"

def test_aes_gcm_decryption_with_tampered_ciphertext(sample_plaintext, aes_key_256):
    """Test that tampering with ciphertext causes decryption to fail."""
    ciphertext, nonce, tag = encrypt(sample_plaintext, aes_key_256)
    
    tampered_ciphertext = ciphertext[:-5] + b"XXXXX" 
    if not tampered_ciphertext.endswith(b"XXXXX"): 
        tampered_ciphertext = b"XXXXX" + ciphertext[5:] 

    with pytest.raises(ValueError, match="Decryption failed"): # FIXED: Match the explicit error from Rust
        decrypt(tampered_ciphertext, nonce, tag, aes_key_256)
    
def test_aes_gcm_decryption_with_tampered_tag(sample_plaintext, aes_key_256):
    """Test that tampering with authentication tag causes decryption to fail."""
    ciphertext, nonce, tag = encrypt(sample_plaintext, aes_key_256)
    
    tampered_tag = tag[:-4] + b"YYYY"
    if not tampered_tag.endswith(b"YYYY"): 
        tampered_tag = b"YYYY" + tag[4:]

    with pytest.raises(ValueError, match="Decryption failed"): # FIXED: Match the explicit error from Rust
        decrypt(ciphertext, nonce, tampered_tag, aes_key_256)


def test_aes_gcm_invalid_key_length():
    """Test that encryption/decryption fails with an invalid key length."""
    invalid_key = os.urandom(15) 
    plaintext = b"some data"
    
    with pytest.raises(ValueError, match="AES key must be 32 bytes long for AES-256-GCM."):
 # FIXED: Match Rust's exact error message
        encrypt(plaintext, invalid_key)

    valid_key = os.urandom(config_package.AES_GCM_KEY_LEN) 
    ciphertext, nonce, tag = encrypt(plaintext, valid_key)
    with pytest.raises(ValueError, match="AES key must be 32 bytes long for AES-256-GCM."): # FIXED: Match Rust's exact error message
        decrypt(ciphertext, nonce, tag, invalid_key)

def test_aes_gcm_invalid_nonce_length(sample_plaintext, aes_key_256):
    """Test that decryption fails with an invalid nonce length."""
    ciphertext, nonce, tag = encrypt(sample_plaintext, aes_key_256)
    invalid_nonce = os.urandom(11) 

    # Test decrypt
    with pytest.raises(ValueError, match="AES-GCM nonce must be 12 bytes long."): # FIXED: Match Rust's exact error message
        decrypt(ciphertext, invalid_nonce, tag, aes_key_256)
    
    # Test encrypt_with_provided_nonce
    with pytest.raises(ValueError, match="Nonce must be 12 bytes long."): # FIXED: Match Rust's exact error message
        encrypt_with_provided_nonce(sample_plaintext, aes_key_256, invalid_nonce)


# --- Test Shamir's Secret Sharing (SSS) ---

# Fixture to skip SSS tests if Node.js server is not running
@pytest.fixture(scope="module", autouse=True)
def skip_if_sss_service_down():
    try:
        requests.get(f"{key_sharding.NODE_SSS_API_BASE_URL}/", timeout=1) 
    except (requests.exceptions.ConnectionError, requests.exceptions.Timeout):
        pytest.skip("Node.js SSS server not running. Skipping SSS tests.")

def test_sss_create_and_reconstruct_secret():
    """Test creating shares and reconstructing with enough shares."""
    secret = b"My super secret data for SSS"
    num_shares = 5
    threshold = 3

    shares = key_sharding.create_shares(secret, num_shares, threshold)

    assert len(shares) == num_shares, "Should create the specified number of shares"
    for share in shares:
        assert isinstance(share, str) and len(share) > 0, "Each share should be non-empty hex string" 

    reconstructed_secret = key_sharding.reconstruct_secret(shares[:threshold], threshold) 
    assert reconstructed_secret == secret, "Secret should be reconstructed with threshold shares"

    reconstructed_secret_more = key_sharding.reconstruct_secret(shares[1:threshold+1], threshold) 
    assert reconstructed_secret_more == secret, "Secret should be reconstructed with more than threshold shares"

def test_sss_reconstruct_with_insufficient_shares():
    """Test that reconstruction fails with fewer than threshold shares."""
    secret = b"Another secret"
    num_shares = 5
    threshold = 3

    shares = key_sharding.create_shares(secret, num_shares, threshold)

    with pytest.raises(ValueError, match=f"Not enough shares to reconstruct secret: {threshold-1} provided, need {threshold}."): 
        key_sharding.reconstruct_secret(shares[:threshold-1], threshold) 

def test_sss_invalid_parameters():
    """Test that SSS creation fails with invalid parameters."""
    secret = b"test"
    
    with pytest.raises(ValueError, match="Threshold must be >= 2 and <= num_shares."): 
        key_sharding.create_shares(secret, 1, 2) 

    with pytest.raises(ValueError, match="Threshold must be >= 2 and <= num_shares."): 
        key_sharding.create_shares(secret, 5, 1) 


# --- Test Merkle Tree Operations ---

def test_merkle_root_creation(sample_merkle_blocks):
    """Test creation of a Merkle root."""
    root = create_merkle_root_rust(sample_merkle_blocks)
    assert isinstance(root, bytes)
    assert len(root) == 32 

    empty_root = create_merkle_root_rust([])
    assert empty_root == b'', "Empty list should result in empty root (as per current Rust impl)"

    single_block = b"single block"
    single_block_root = create_merkle_root_rust([single_block])
    expected_single_root = hashlib.sha256(single_block).digest()
    assert single_block_root == expected_single_root


def test_merkle_proof_verification_valid(sample_merkle_blocks):
    """
    Test successful Merkle proof verification for a simple 2-block case.
    This test aligns with the *current simplified* Rust Merkle verify_merkle_proof,
    which processes hashes lexicographically, not a standard Merkle proof path.
    """
    block_a = b"first block"
    block_b = b"second block"

    hash_a = hashlib.sha256(block_a).digest()
    hash_b = hashlib.sha256(block_b).digest()

    if hash_a < hash_b:
        root_calculated = hashlib.sha256(hash_a + hash_b).digest()
        proof_for_a = [hash_b] 
    else:
        root_calculated = hashlib.sha256(hash_b + hash_a).digest()
        proof_for_a = [hash_b] 

    root_of_two_via_rust = create_merkle_root_rust([block_a, block_b])

    assert root_calculated == root_of_two_via_rust

    is_valid = verify_merkle_proof_rust(block_a, proof_for_a, root_of_two_via_rust)
    assert is_valid, "Merkle proof for two blocks should be valid"


def test_merkle_proof_verification_invalid(sample_merkle_blocks):
    """Test Merkle proof verification failure with tampered data/proof."""
    block_a = b"first block"
    block_b = b"second block"

    hash_a = hashlib.sha256(block_a).digest()
    hash_b = hashlib.sha256(block_b).digest()

    if hash_a < hash_b:
        root_of_two = hashlib.sha256(hash_a + hash_b).digest()
        proof_for_a = [hash_b]
    else:
        root_of_two = hashlib.sha256(hash_b + hash_a).digest()
        proof_for_a = [hash_b]

    tampered_block = b"tampered data"
    is_invalid_data = verify_merkle_proof_rust(tampered_block, proof_for_a, root_of_two)
    assert not is_invalid_data, "Proof should fail with tampered data"

    tampered_proof = [os.urandom(32)] 
    
    is_invalid_proof = verify_merkle_proof_rust(block_a, tampered_proof, root_of_two)
    assert not is_invalid_proof, "Proof should fail with tampered proof hashes"

    tampered_root = b"a" * 32 
    is_invalid_root = verify_merkle_proof_rust(block_a, proof_for_a, tampered_root)
    assert not is_invalid_root, "Proof should fail with tampered root"


# --- Test PQC Placeholder Functions (Kyber/Falcon) ---

def test_kyber_key_generation():
    """Test Kyber key generation placeholder."""
    # FIXED: Expected sizes from new Rust placeholder
    pub_key, sec_key = generate_kyber_keys_rust()
    assert isinstance(pub_key, bytes) and len(pub_key) == 32 
    assert isinstance(sec_key, bytes) and len(sec_key) == 32 
    assert pub_key == b'\x01' * 32 # Assert specific content of placeholder
    assert sec_key == b'\x02' * 32 # Assert specific content of placeholder

def test_kyber_encapsulate_decapsulate():
    """Test Kyber encapsulation/decapsulation placeholders."""
    _, sec_key = generate_kyber_keys_rust() # Get a dummy secret key
    public_key_dummy = b"\x00" * 32 

    # FIXED: Expected sizes and content from new Rust placeholder
    ciphertext, shared_secret_encap = encapsulate_kyber_rust(public_key_dummy)
    assert isinstance(ciphertext, bytes) and len(ciphertext) == 32 
    assert isinstance(shared_secret_encap, bytes) and len(shared_secret_encap) == 32 
    assert ciphertext == b'\x03' * 32
    assert shared_secret_encap == b'\x04' * 32

    # FIXED: Expected sizes and content from new Rust placeholder
    shared_secret_decap = decapsulate_kyber_rust(ciphertext, sec_key)
    assert isinstance(shared_secret_decap, bytes) and len(shared_secret_decap) == 32 
    assert shared_secret_decap == b'\x05' * 32


def test_falcon_key_generation():
    """Test Falcon key generation placeholder."""
    # FIXED: Expected sizes and content from new Rust placeholder
    pub_key, sec_key = generate_falcon_keys_rust()
    assert isinstance(pub_key, bytes) and len(pub_key) == 32 
    assert isinstance(sec_key, bytes) and len(sec_key) == 32 
    assert pub_key == b'\x06' * 32
    assert sec_key == b'\x07' * 32

def test_falcon_sign_verify():
    """Test Falcon sign/verify placeholders."""
    _, sec_key = generate_falcon_keys_rust()
    message = b"Data to be signed by Falcon"
    public_key_dummy = b"\x00" * 32 

    # FIXED: Expected size and content from new Rust placeholder
    signature = sign_falcon_rust(message, sec_key)
    assert isinstance(signature, bytes) and len(signature) == 64 
    assert signature == b'\x08' * 64

    is_valid = verify_falcon_rust(message, signature, public_key_dummy)
    assert is_valid == True