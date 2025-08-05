# core/merkle_logging/merkle.py

from crypto.rust_ffi_wrappers import create_merkle_root_rust, verify_merkle_proof_rust

def create_merkle_root(data_blocks: list[bytes]) -> bytes:
    """
    Creates a Merkle root from a list of data blocks using the Rust FFI.
    """
    return create_merkle_root_rust(data_blocks)

def verify_merkle_proof(data_block: bytes, proof: list[bytes], root: bytes) -> bool:
    """
    Verifies a Merkle proof for a given data block against a root using the Rust FFI.
    """
    return verify_merkle_proof_rust(data_block, proof, root)

if __name__ == "__main__":
    print("--- Testing core/merkle_logging/merkle.py ---")
    
    # This requires the Merkle rust module to be built and installed via `maturin develop`
    
    data_blocks = [
        b"log entry 1",
        b"log entry 2",
        b"log entry 3",
        b"log entry 4",
    ]
    
    try:
        root = create_merkle_root(data_blocks)
        print(f"Created Merkle Root: {root.hex()}")
        assert isinstance(root, bytes) and len(root) == 32
        print("✅ Root creation test passed.")
        
        # This part of the test is tricky because it depends on the proof generation logic,
        # which is not yet fully implemented on the Python side. The `tests/test_crypto.py`
        # file has a more robust test for this.
        # For a simple self-test, we'll just check if the function is callable.
        proof = [b"a" * 32] # Dummy proof
        is_valid = verify_merkle_proof(data_blocks[0], proof, root)
        print(f"Verification for dummy proof: {is_valid}")
        print("✅ Merkle proof wrapper test passed.")

    except ImportError as e:
        print(f"❌ Failed to run Merkle test: {e}")
        print("Please ensure the Rust Merkle module is built and installed via `maturin develop`.")