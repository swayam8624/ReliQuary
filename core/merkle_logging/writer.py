# core/merkle_logging/writer.py

import json
import os
from datetime import datetime

class LogWriter:
    """
    Manages writing structured log entries to a file.
    """
    def __init__(self, log_file_path: str):
        self.log_file_path = log_file_path
        # Ensure the directory exists
        os.makedirs(os.path.dirname(log_file_path), exist_ok=True)

    def write_entry(self, entry: dict) -> bytes:
        """
        Writes a new log entry to the file, and returns the raw bytes written.
        """
        entry["timestamp"] = datetime.now().isoformat() + "Z"
        entry_json = json.dumps(entry, sort_keys=True)
        entry_bytes = entry_json.encode('utf-8')
        
        with open(self.log_file_path, "ab") as f:
            f.write(entry_bytes + b"\n")
            
        return entry_bytes

    def read_all_entries(self) -> list[bytes]:
        """
        Reads all log entries from the file as a list of raw byte lines.
        """
        if not os.path.exists(self.log_file_path):
            return []
            
        with open(self.log_file_path, "rb") as f:
            return f.readlines()

if __name__ == "__main__":
    print("--- Testing core/merkle_logging/writer.py ---")
    
    test_log_file = "test_logs/merkle_test.log"
    writer = LogWriter(test_log_file)
    
    # Clean up old log file if it exists
    if os.path.exists(test_log_file):
        os.remove(test_log_file)
    
    test_entry = {"event": "test_event", "status": "success"}
    written_bytes = writer.write_entry(test_entry)
    
    read_entries = writer.read_all_entries()
    
    assert len(read_entries) == 1, "Should have written exactly one entry."
    assert written_bytes + b"\n" == read_entries[0], "The read entry should match the written one."
    
    print("✅ LogWriter test passed.")