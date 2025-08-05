use pyo3::prelude::*;
use pyo3::Bound; // Import Bound for the updated signature
use sha2::{Digest, Sha256};

/// A Python module for Reliquary's Merkle tree operations.
#[pymodule]
fn reliquary_merkle(_py: Python<'_>, m: &Bound<'_, PyModule>) -> PyResult<()> {
    // Fixed: Changed signature for _py and m
    m.add_function(wrap_pyfunction!(create_merkle_root, m)?)?;
    m.add_function(wrap_pyfunction!(verify_merkle_proof, m)?)?;
    Ok(())
}

/// Creates a Merkle root from a list of data blocks.
#[pyfunction]
fn create_merkle_root(data_blocks: Vec<Vec<u8>>) -> PyResult<Vec<u8>> {
    if data_blocks.is_empty() {
        return Ok(vec![]);
    }

    let mut hashes: Vec<Vec<u8>> = data_blocks
        .into_iter()
        .map(|block| {
            let mut hasher = Sha256::new();
            hasher.update(&block);
            hasher.finalize().to_vec()
        })
        .collect();

    while hashes.len() > 1 {
        let mut next_level_hashes = Vec::new();
        let mut i = 0;
        while i < hashes.len() {
            let left = &hashes[i];
            let right = if i + 1 < hashes.len() {
                &hashes[i + 1]
            } else {
                left // Duplicate the last hash if odd number of leaves
            };

            let mut hasher = Sha256::new();
            hasher.update(left);
            hasher.update(right);
            next_level_hashes.push(hasher.finalize().to_vec());
            i += 2;
        }
        hashes = next_level_hashes;
    }
    Ok(hashes[0].clone())
}

/// Verifies a Merkle proof for a given data block and root.
#[pyfunction]
fn verify_merkle_proof(data_block: Vec<u8>, proof: Vec<Vec<u8>>, root: Vec<u8>) -> PyResult<bool> {
    let mut current_hash: Vec<u8> = {
        let mut hasher = Sha256::new();
        hasher.update(&data_block);
        hasher.finalize().to_vec()
    };

    for p_hash in proof {
        let mut hasher = Sha256::new();
        // The order of hashes in the concatenation needs to be consistent
        // with how the Merkle tree was built (left then right).
        // The comparison `current_hash < p_hash` is a common but not universally correct
        // way to decide order if the tree doesn't enforce sorted leaves.
        // For a simple SHA256 Merkle tree, typically you'd always concatenate in a fixed
        // order (e.g., current_hash then p_hash, or vice-versa) based on the specific Merkle tree construction.
        // For now, keeping your original logic for demonstration:
        if current_hash < p_hash {
            hasher.update(&current_hash);
            hasher.update(&p_hash);
        } else {
            hasher.update(&p_hash);
            hasher.update(&current_hash);
        }
        current_hash = hasher.finalize().to_vec();
    }
    Ok(current_hash == root)
}
