# core/audit.py

import os
from merkle_logging.writer import LogWriter
from merkle_logging.merkle import create_merkle_root
from merkle_logging.hasher import hash_data
import config_package

class AuditTrailManager:
    """
    Manages the audit trail by writing entries and maintaining a verifiable Merkle root.
    """
    def __init__(self, log_file_path: str):
        self.log_writer = LogWriter(log_file_path)
        self.merkle_root = self._rebuild_merkle_root()

    def _rebuild_merkle_root(self) -> bytes:
        """
        Reads all log entries and computes a new Merkle root.
        """
        log_entries_bytes = self.log_writer.read_all_entries()
        if not log_entries_bytes:
            return b""
            
        return create_merkle_root(log_entries_bytes)

    def log_action(self, action: str, data: dict, signature: bytes = b"") -> bytes:
        """
        Creates a new log entry, writes it, and updates the Merkle root.
        """
        log_entry = {
            "action": action,
            "data": data,
            "signature": signature.hex()
        }
        
        new_entry_bytes = self.log_writer.write_entry(log_entry)
        
        # The Merkle root would ideally be updated incrementally, but for simplicity
        # we'll rebuild the entire tree here.
        self.merkle_root = self._rebuild_merkle_root()
        
        return self.merkle_root
        
    def get_current_root(self) -> bytes:
        """
        Returns the current Merkle root of the audit trail.
        """
        return self.merkle_root
        
    def verify_entry(self, entry_bytes: bytes, proof: list[bytes]) -> bool:
        """
        Verifies if a specific entry is part of the audit trail.
        Note: This is an oversimplification. A real system would need to store/rebuild
        the entire tree to generate a proper proof.
        """
        return verify_merkle_proof(entry_bytes, proof, self.merkle_root)
        
if __name__ == "__main__":
    print("--- Testing core/audit.py ---")
    
    test_log_file = os.path.join("test_logs", "audit_test.log")
    
    # Clean up old log file if it exists
    if os.path.exists(test_log_file):
        os.remove(test_log_file)
        
    audit_manager = AuditTrailManager(test_log_file)
    
    # 1. Test initial state
    initial_root = audit_manager.get_current_root()
    print(f"Initial Merkle Root: {initial_root.hex()}")
    assert initial_root == b"", "Initial root of an empty log should be empty bytes."
    print("✅ Initial state test passed.")
    
    # 2. Log a first action
    first_data = {"user": "Alice", "vault_id": "123"}
    first_root = audit_manager.log_action(
        action="VAULT_CREATE", 
        data=first_data, 
        signature=b"test_sig_1"
    )
    print(f"Root after first action: {first_root.hex()}")
    assert len(first_root) == 32
    print("✅ First log action test passed.")
    
    # 3. Log a second action
    second_data = {"user": "Bob", "vault_id": "456"}
    second_root = audit_manager.log_action(
        action="VAULT_ACCESS", 
        data=second_data, 
        signature=b"test_sig_2"
    )
    print(f"Root after second action: {second_root.hex()}")
    assert len(second_root) == 32
    assert second_root != first_root, "Merkle root should change after new log entry."
    print("✅ Second log action test passed.")