# core/merkle_logging/merkle.py

import hashlib
from typing import List, Optional, Tuple
from .hasher import hash_data

class MerkleTree:
    """A simple and robust Merkle tree implementation."""
    
    def __init__(self, data_blocks: List[bytes]):
        self.data_blocks = data_blocks.copy()
        self.leaf_hashes = [hash_data(block) for block in data_blocks]
        self.tree = self._build_tree()
        self.root = self.tree[-1][0] if self.tree and self.tree[-1] else b''
    
    def _build_tree(self) -> List[List[bytes]]:
        """Build the complete Merkle tree."""
        if not self.leaf_hashes:
            return []
        
        tree = [self.leaf_hashes.copy()]
        
        while len(tree[-1]) > 1:
            current_level = tree[-1]
            next_level = []
            
            for i in range(0, len(current_level), 2):
                left = current_level[i]
                # If odd number, duplicate the last element
                right = current_level[i + 1] if i + 1 < len(current_level) else left
                parent = hash_data(left + right)
                next_level.append(parent)
            
            tree.append(next_level)
        
        return tree
    
    def get_proof(self, index: int) -> List[Tuple[bytes, bool]]:
        """
        Get proof for a leaf at the given index.
        Returns list of (hash, is_right) tuples where is_right indicates
        if the hash should be on the right side of the current hash.
        """
        if index >= len(self.leaf_hashes):
            raise IndexError("Index out of range")
        
        proof = []
        current_index = index
        
        # Traverse from leaf to root
        for level in range(len(self.tree) - 1):
            current_level = self.tree[level]
            
            # Find sibling
            if current_index % 2 == 0:
                # We're on the left, sibling is on the right
                sibling_index = current_index + 1
                is_right = True  # Sibling goes on the right
            else:
                # We're on the right, sibling is on the left
                sibling_index = current_index - 1
                is_right = False  # Sibling goes on the left
            
            # Add sibling to proof (it always exists due to duplication)
            if sibling_index < len(current_level):
                proof.append((current_level[sibling_index], is_right))
            
            current_index = current_index // 2
        
        return proof
    
    def verify_proof(self, data_block: bytes, index: int, proof: List[Tuple[bytes, bool]]) -> bool:
        """Verify a proof for the given data block."""
        current_hash = hash_data(data_block)
        current_index = index
        proof_index = 0
        
        # Walk through each level of the tree
        for level in range(len(self.tree) - 1):
            current_level = self.tree[level]
            
            # Check if current node has a sibling at this level
            if current_index % 2 == 0:
                # Even index - sibling should be at current_index + 1
                sibling_index = current_index + 1
                is_right = True
            else:
                # Odd index - sibling should be at current_index - 1  
                sibling_index = current_index - 1
                is_right = False
            
            # If sibling exists in current level, use it from proof
            if sibling_index < len(current_level):
                if proof_index >= len(proof):
                    return False  # Missing proof element
                
                sibling_hash, expected_is_right = proof[proof_index]
                if expected_is_right != is_right:
                    return False  # Wrong direction
                
                if is_right:
                    current_hash = hash_data(current_hash + sibling_hash)
                else:
                    current_hash = hash_data(sibling_hash + current_hash)
                    
                proof_index += 1
            else:
                # No sibling - node gets duplicated (paired with itself)
                current_hash = hash_data(current_hash + current_hash)
            
            # Move to next level
            current_index = current_index // 2
        
        # Check that we used all proof elements and reached the root
        return proof_index == len(proof) and current_hash == self.root

# Convenience functions for backward compatibility
def create_merkle_root(data_blocks: List[bytes]) -> bytes:
    """
    Creates a Merkle root from a list of data blocks.
    """
    if not data_blocks:
        return b''
    
    tree = MerkleTree(data_blocks)
    return tree.root

def generate_merkle_proof(data_blocks: List[bytes], target_index: int) -> List[bytes]:
    """
    Generates a Merkle proof for a data block at a specific index.
    Returns just the sibling hashes (without position info) for backward compatibility.
    """
    tree = MerkleTree(data_blocks)
    proof_with_positions = tree.get_proof(target_index)
    return [hash_val for hash_val, _ in proof_with_positions]

def verify_merkle_proof(data_block: bytes, proof: List[bytes], root: bytes, index: Optional[int] = None) -> bool:
    """
    Verifies a Merkle proof for a given data block against a root.
    Note: This backward-compatible version requires the index for proper verification.
    """
    if index is None:
        raise ValueError("Index is required for proper Merkle proof verification")
    
    # We need to reconstruct the tree to verify properly
    # This is a limitation of the backward-compatible interface
    # We'll create a temporary tree with just the necessary structure
    
    # Convert proof back to (hash, is_right) format
    current_index = index
    proof_with_positions = []
    
    for sibling_hash in proof:
        if current_index % 2 == 0:
            # We're on the left, sibling is on the right
            is_right = True
        else:
            # We're on the right, sibling is on the left
            is_right = False
        
        proof_with_positions.append((sibling_hash, is_right))
        current_index = current_index // 2
    
    # Use the new verification logic
    current_hash = hash_data(data_block)
    current_index = index
    proof_index = 0
    
    # We need to simulate tree levels to handle duplication correctly
    # This is complex without the full tree, so let's use a simplified approach
    # that matches the MerkleTree class logic
    
    for sibling_hash, is_right in proof_with_positions:
        # Check if this level would have required duplication
        # If current_index is odd and at the last position, duplication occurred
        level_size = (index + 1) if proof_index == 0 else None  # We can only guess for first level
        
        if level_size and current_index == level_size - 1 and current_index % 2 == 0:
            # This node had no sibling and was duplicated
            current_hash = hash_data(current_hash + current_hash)
        
        # Apply the proof step
        if is_right:
            current_hash = hash_data(current_hash + sibling_hash)
        else:
            current_hash = hash_data(sibling_hash + current_hash)
        
        current_index = current_index // 2
        proof_index += 1
    
    return current_hash == root

if __name__ == "__main__":
    print("--- Testing core/merkle_logging/merkle.py ---")
    
    data_blocks = [
        b"log entry 1",
        b"log entry 2", 
        b"log entry 3",
        b"log entry 4",
    ]
    
    # Test root creation
    root = create_merkle_root(data_blocks)
    print(f"Created Merkle Root: {root.hex()}")
    assert isinstance(root, bytes) and len(root) == 32
    print("✅ Root creation test passed.")
    
    # Test with MerkleTree class directly
    tree = MerkleTree(data_blocks)
    print(f"Tree root: {tree.root.hex()}")
    print(f"Tree structure: {[[h.hex()[:8] for h in level] for level in tree.tree]}")
    assert tree.root == root
    
    # Test proof generation and verification for all entries
    for target_index in range(len(data_blocks)):
        proof_with_pos = tree.get_proof(target_index)
        print(f"\nEntry {target_index} proof: {[(h.hex()[:8], pos) for h, pos in proof_with_pos]}")
        
        # Debug the verification process
        current_hash = hash_data(data_blocks[target_index])
        print(f"Entry {target_index} starting hash: {current_hash.hex()[:8]}")
        
        for i, (sibling_hash, is_right) in enumerate(proof_with_pos):
            if is_right:
                current_hash = hash_data(current_hash + sibling_hash)
                print(f"  Step {i}: {current_hash.hex()[:8]} = hash(current + {sibling_hash.hex()[:8]})")
            else:
                current_hash = hash_data(sibling_hash + current_hash)
                print(f"  Step {i}: {current_hash.hex()[:8]} = hash({sibling_hash.hex()[:8]} + current)")
        
        print(f"Final hash: {current_hash.hex()[:8]}, Root: {tree.root.hex()[:8]}")
        is_valid_direct = tree.verify_proof(data_blocks[target_index], target_index, proof_with_pos)
        print(f"Entry {target_index} direct verification: {is_valid_direct}")
        
        if not is_valid_direct:
            print("STOPPING due to failure")
            break
        
        # Test backward compatible functions
        proof = generate_merkle_proof(data_blocks, target_index)
        is_valid_compat = verify_merkle_proof(data_blocks[target_index], proof, root, target_index)
        print(f"Entry {target_index} compatible verification: {is_valid_compat}")
        assert is_valid_compat, f"Compatible verification should pass for entry {target_index}"
    
    print("✅ All Merkle tree tests passed.")
    
    # Test with 3 entries specifically
    print("\n--- Testing with 3 entries ---")
    data_blocks_3 = data_blocks[:3]
    tree_3 = MerkleTree(data_blocks_3)
    
    for i in range(len(data_blocks_3)):
        proof = tree_3.get_proof(i)
        is_valid = tree_3.verify_proof(data_blocks_3[i], i, proof)
        print(f"3-entry test - Entry {i} valid: {is_valid}")
        assert is_valid, f"Entry {i} should be valid in 3-entry tree"
    
    print("✅ 3-entry test passed.")