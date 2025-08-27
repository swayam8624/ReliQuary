# core/merkle_logging/writer.py

import json
import os
from datetime import datetime
from typing import List, Dict, Any, Optional
from .merkle import MerkleTree, hash_data

class MerkleLogEntry:
    """Represents a single log entry with Merkle proof capability."""
    
    def __init__(self, data: Dict[str, Any], timestamp: Optional[str] = None):
        self.data = data.copy()
        self.timestamp = timestamp or datetime.now().isoformat() + "Z"
        self.data["timestamp"] = self.timestamp
        
    def to_bytes(self) -> bytes:
        """Convert the log entry to bytes for hashing."""
        entry_json = json.dumps(self.data, sort_keys=True)
        return entry_json.encode('utf-8')
    
    def hash(self) -> bytes:
        """Get the hash of this log entry."""
        return hash_data(self.to_bytes())

class MerkleLogWriter:
    """
    Manages writing structured log entries with Merkle tree integrity verification.
    """
    
    def __init__(self, log_file_path: str, merkle_file_path: Optional[str] = None):
        self.log_file_path = log_file_path
        self.merkle_file_path = merkle_file_path or log_file_path + ".merkle"
        
        # Ensure directories exist
        os.makedirs(os.path.dirname(log_file_path), exist_ok=True)
        if self.merkle_file_path != log_file_path:
            os.makedirs(os.path.dirname(self.merkle_file_path), exist_ok=True)
        
        self._entries_cache: List[MerkleLogEntry] = []
        self._current_root: Optional[bytes] = None
        self._load_existing_entries()
    
    def _load_existing_entries(self):
        """Load existing log entries from file."""
        if not os.path.exists(self.log_file_path):
            return
        
        with open(self.log_file_path, "rb") as f:
            for line in f:
                line = line.strip()
                if line:
                    try:
                        data = json.loads(line.decode('utf-8'))
                        entry = MerkleLogEntry(data, data.get("timestamp"))
                        self._entries_cache.append(entry)
                    except (json.JSONDecodeError, UnicodeDecodeError) as e:
                        print(f"Warning: Failed to parse log entry: {e}")
        
        # Recalculate Merkle root
        if self._entries_cache:
            self._update_merkle_root()
    
    def _update_merkle_root(self):
        """Update the current Merkle root based on all entries."""
        if not self._entries_cache:
            self._current_root = None
            return
        
        entry_bytes = [entry.to_bytes() for entry in self._entries_cache]
        tree = MerkleTree(entry_bytes)
        self._current_root = tree.root
        
        # Save Merkle root to file
        merkle_data = {
            "root": self._current_root.hex(),
            "entry_count": len(self._entries_cache),
            "last_updated": datetime.now().isoformat() + "Z"
        }
        
        with open(self.merkle_file_path, "w") as f:
            json.dump(merkle_data, f, indent=2)
    
    def add_entry(self, entry_data: Dict[str, Any]) -> MerkleLogEntry:
        """
        Add a new log entry and update the Merkle tree.
        
        Args:
            entry_data: Dictionary containing log entry data
            
        Returns:
            The created MerkleLogEntry
        """
        entry = MerkleLogEntry(entry_data)
        
        # Write to log file
        with open(self.log_file_path, "ab") as f:
            f.write(entry.to_bytes() + b"\n")
        
        # Add to cache and update Merkle root
        self._entries_cache.append(entry)
        self._update_merkle_root()
        
        return entry
    
    def get_entry_proof(self, entry_index: int) -> Dict[str, Any]:
        """
        Generate a Merkle proof for a specific log entry.
        
        Args:
            entry_index: Index of the entry in the log
            
        Returns:
            Dictionary containing the proof data
        """
        if entry_index >= len(self._entries_cache):
            raise IndexError("Entry index out of range")
        
        entry_bytes = [entry.to_bytes() for entry in self._entries_cache]
        tree = MerkleTree(entry_bytes)
        proof_with_positions = tree.get_proof(entry_index)
        
        # Convert to legacy format (just the hashes)
        proof = [hash_val for hash_val, _ in proof_with_positions]
        
        return {
            "entry_index": entry_index,
            "entry_hash": self._entries_cache[entry_index].hash().hex(),
            "merkle_root": self._current_root.hex() if self._current_root else None,
            "proof": [p.hex() for p in proof],
            "total_entries": len(self._entries_cache)
        }
    
    def verify_entry_integrity(self, entry_index: int, provided_proof: Optional[List[str]] = None) -> bool:
        """
        Verify the integrity of a specific log entry.
        
        Args:
            entry_index: Index of the entry to verify
            provided_proof: Optional external proof to verify against
            
        Returns:
            True if the entry is valid, False otherwise
        """
        if entry_index >= len(self._entries_cache):
            return False
        
        if not self._current_root:
            return len(self._entries_cache) == 0
        
        entry = self._entries_cache[entry_index]
        entry_bytes = [entry.to_bytes() for entry in self._entries_cache]
        tree = MerkleTree(entry_bytes)
        
        if provided_proof:
            # Convert provided proof to (hash, is_right) format
            proof_bytes = [bytes.fromhex(p) for p in provided_proof]
            # We need to determine the directions based on index
            current_index = entry_index
            proof_with_positions = []
            
            for sibling_hash in proof_bytes:
                if current_index % 2 == 0:
                    is_right = True
                else:
                    is_right = False
                proof_with_positions.append((sibling_hash, is_right))
                current_index = current_index // 2
            
            return tree.verify_proof(entry.to_bytes(), entry_index, proof_with_positions)
        else:
            # Use tree's own proof generation and verification
            proof_with_positions = tree.get_proof(entry_index)
            return tree.verify_proof(entry.to_bytes(), entry_index, proof_with_positions)
    
    def verify_log_integrity(self) -> bool:
        """
        Verify the integrity of the entire log.
        
        Returns:
            True if all entries are valid, False otherwise
        """
        if not self._entries_cache:
            return True
        
        # Recalculate Merkle root and compare
        entry_bytes = [entry.to_bytes() for entry in self._entries_cache]
        tree = MerkleTree(entry_bytes)
        calculated_root = tree.root
        
        return calculated_root == self._current_root
    
    def get_log_summary(self) -> Dict[str, Any]:
        """
        Get a summary of the current log state.
        
        Returns:
            Dictionary containing log summary information
        """
        return {
            "total_entries": len(self._entries_cache),
            "merkle_root": self._current_root.hex() if self._current_root else None,
            "log_file": self.log_file_path,
            "merkle_file": self.merkle_file_path,
            "integrity_verified": self.verify_log_integrity()
        }
    
    @property
    def entry_count(self) -> int:
        """Get the number of entries in the log."""
        return len(self._entries_cache)
    
    @property
    def merkle_root(self) -> Optional[bytes]:
        """Get the current Merkle root."""
        return self._current_root

# Legacy LogWriter for backward compatibility
class LogWriter(MerkleLogWriter):
    """Legacy LogWriter class for backward compatibility."""
    
    def write_entry(self, entry: Dict[str, Any]) -> bytes:
        """Write a log entry and return its bytes (legacy interface)."""
        log_entry = self.add_entry(entry)
        return log_entry.to_bytes()
    
    def read_all_entries(self) -> List[bytes]:
        """Read all log entries as raw bytes (legacy interface)."""
        return [entry.to_bytes() for entry in self._entries_cache]

if __name__ == "__main__":
    print("--- Testing core/merkle_logging/writer.py ---")
    
    test_log_file = "test_logs/merkle_test.log"
    test_merkle_file = "test_logs/merkle_test.log.merkle"
    
    # Clean up old files
    for file_path in [test_log_file, test_merkle_file]:
        if os.path.exists(file_path):
            os.remove(file_path)
    
    # Test MerkleLogWriter
    writer = MerkleLogWriter(test_log_file)
    
    # Add some test entries
    test_entries = [
        {"event": "user_login", "user_id": "user123", "status": "success"},
        {"event": "data_access", "resource": "vault456", "action": "read"},
        {"event": "encryption", "algorithm": "AES-256", "key_id": "key789"}
    ]
    
    for entry_data in test_entries:
        writer.add_entry(entry_data)
    
    print(f"Added {len(test_entries)} entries")
    print(f"Log summary: {writer.get_log_summary()}")
    
    # Test proof generation and verification
    for i in range(len(test_entries)):
        proof_data = writer.get_entry_proof(i)
        print(f"Entry {i} proof data: {proof_data}")
        
        # Also test the underlying Merkle functions directly
        entry_bytes = [entry.to_bytes() for entry in writer._entries_cache]
        print(f"Entry {i} bytes: {entry_bytes[i][:50]}...")
        
        from .merkle import generate_merkle_proof, verify_merkle_proof
        direct_proof = generate_merkle_proof(entry_bytes, i)
        direct_verify = verify_merkle_proof(entry_bytes[i], direct_proof, writer._current_root, i)
        print(f"Entry {i} direct verification: {direct_verify}")
        
        is_valid = writer.verify_entry_integrity(i)
        print(f"Entry {i} writer verification: {is_valid}")
        
        if not is_valid:
            print(f"Entry {i} FAILED - investigating...")
            # Let's check if the issue is in our writer logic
            proof_bytes = [bytes.fromhex(p) for p in proof_data["proof"]]
            manual_verify = verify_merkle_proof(entry_bytes[i], proof_bytes, writer._current_root, i)
            print(f"Entry {i} manual verification: {manual_verify}")
            break
        
        assert is_valid, f"Entry {i} should be valid"
    
    # Test overall integrity
    overall_integrity = writer.verify_log_integrity()
    print(f"Overall log integrity: {overall_integrity}")
    assert overall_integrity, "Overall log should be valid"
    
    # Test legacy interface
    legacy_writer = LogWriter(test_log_file + ".legacy")
    legacy_bytes = legacy_writer.write_entry({"test": "legacy"})
    assert isinstance(legacy_bytes, bytes)
    
    print("✅ All MerkleLogWriter tests passed.")