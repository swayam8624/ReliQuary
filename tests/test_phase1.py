# tests/test_phase1.py

import pytest
import requests
import tempfile
import os
import json
from typing import Dict, Any

# Import our modules
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../'))

from core.merkle_logging.hasher import hash_data
from core.merkle_logging.merkle import MerkleTree, create_merkle_root, verify_merkle_proof
from core.merkle_logging.writer import MerkleLogWriter, MerkleLogEntry

class TestMerkleLogging:
    """Test suite for Merkle logging components."""
    
    def test_hash_function(self):
        """Test the basic hash function."""
        data = b"test data"
        hash_result = hash_data(data)
        
        assert isinstance(hash_result, bytes)
        assert len(hash_result) == 32  # SHA-256 produces 32-byte hashes
        
        # Hash should be deterministic
        assert hash_data(data) == hash_result
        
        # Different data should produce different hashes
        assert hash_data(b"different data") != hash_result
    
    def test_merkle_tree_basic(self):
        """Test basic Merkle tree functionality."""
        data_blocks = [
            b"block 1",
            b"block 2", 
            b"block 3",
            b"block 4"
        ]
        
        tree = MerkleTree(data_blocks)
        
        # Tree should have a root
        assert tree.root is not None
        assert len(tree.root) == 32
        
        # Test proof generation and verification for all blocks
        for i, block in enumerate(data_blocks):
            proof = tree.get_proof(i)
            is_valid = tree.verify_proof(block, i, proof)
            assert is_valid, f"Proof for block {i} should be valid"
    
    def test_merkle_tree_edge_cases(self):
        """Test Merkle tree with edge cases."""
        # Single block
        single_block = [b"single block"]
        tree_single = MerkleTree(single_block)
        assert tree_single.root == hash_data(single_block[0])
        
        # Empty tree
        tree_empty = MerkleTree([])
        assert tree_empty.root == b''
        
        # Odd number of blocks
        odd_blocks = [b"block 1", b"block 2", b"block 3"]
        tree_odd = MerkleTree(odd_blocks)
        
        for i, block in enumerate(odd_blocks):
            proof = tree_odd.get_proof(i)
            is_valid = tree_odd.verify_proof(block, i, proof)
            assert is_valid, f"Proof for block {i} in odd tree should be valid"
    
    def test_merkle_log_writer(self):
        """Test the MerkleLogWriter functionality."""
        with tempfile.TemporaryDirectory() as temp_dir:
            log_file = os.path.join(temp_dir, "test.log")
            writer = MerkleLogWriter(log_file)
            
            # Add some entries
            entries = [
                {"event": "user_login", "user": "alice"},
                {"event": "data_access", "resource": "vault1"},
                {"event": "encryption", "algorithm": "AES-256"}
            ]
            
            for entry_data in entries:
                writer.add_entry(entry_data)
            
            # Check summary
            summary = writer.get_log_summary()
            assert summary["total_entries"] == len(entries)
            assert summary["integrity_verified"] is True
            
            # Test proof generation and verification
            for i in range(len(entries)):
                proof_data = writer.get_entry_proof(i)
                is_valid = writer.verify_entry_integrity(i)
                assert is_valid, f"Entry {i} should be valid"
                
                # Verify proof structure
                assert "entry_index" in proof_data
                assert "entry_hash" in proof_data
                assert "merkle_root" in proof_data
                assert "proof" in proof_data
    
    def test_log_persistence(self):
        """Test that logs persist across writer instances."""
        with tempfile.TemporaryDirectory() as temp_dir:
            log_file = os.path.join(temp_dir, "persistent.log")
            
            # Create first writer and add entries
            writer1 = MerkleLogWriter(log_file)
            writer1.add_entry({"event": "first_entry"})
            writer1.add_entry({"event": "second_entry"})
            
            first_summary = writer1.get_log_summary()
            
            # Create second writer (should load existing entries)
            writer2 = MerkleLogWriter(log_file)
            second_summary = writer2.get_log_summary()
            
            # Should have same state
            assert first_summary["total_entries"] == second_summary["total_entries"]
            assert first_summary["merkle_root"] == second_summary["merkle_root"]
            
            # Add more entries with second writer
            writer2.add_entry({"event": "third_entry"})
            
            final_summary = writer2.get_log_summary()
            assert final_summary["total_entries"] == 3

class TestFastAPIEndpoints:
    """Test suite for FastAPI endpoints."""
    
    BASE_URL = "http://localhost:8000"
    
    @pytest.fixture(scope="class", autouse=True)
    def ensure_api_running(self):
        """Ensure the API is running before tests."""
        try:
            response = requests.get(f"{self.BASE_URL}/health", timeout=5)
            if response.status_code != 200:
                pytest.skip("API is not running. Start it with: cd apps/api && python main.py")
        except requests.exceptions.RequestException:
            pytest.skip("API is not running. Start it with: cd apps/api && python main.py")
    
    def test_health_endpoint(self):
        """Test the basic health endpoint."""
        response = requests.get(f"{self.BASE_URL}/health")
        assert response.status_code == 200
        
        data = response.json()
        assert data["status"] == "healthy"
        assert "timestamp" in data
        assert "version" in data
        assert data["service"] == "reliquary-api"
    
    def test_detailed_health_endpoint(self):
        """Test the detailed health endpoint."""
        response = requests.get(f"{self.BASE_URL}/health/detailed")
        assert response.status_code == 200
        
        data = response.json()
        assert "status" in data
        assert "components" in data
        
        components = data["components"]
        assert "logger" in components
        assert "crypto" in components
        assert "storage" in components
        
        # Logger should be healthy
        assert components["logger"]["status"] == "healthy"
    
    def test_version_endpoint(self):
        """Test the version endpoint."""
        response = requests.get(f"{self.BASE_URL}/version")
        assert response.status_code == 200
        
        data = response.json()
        assert "version" in data
        assert "api_name" in data
        assert data["api_name"] == "ReliQuary API"
    
    def test_log_summary_endpoint(self):
        """Test the log summary endpoint."""
        response = requests.get(f"{self.BASE_URL}/logs/summary")
        assert response.status_code == 200
        
        data = response.json()
        assert "total_entries" in data
        assert "merkle_root" in data
        assert "integrity_verified" in data
        assert data["integrity_verified"] is True
    
    def test_log_verification_endpoint(self):
        """Test log entry verification."""
        # First get the summary to know how many entries exist
        summary_response = requests.get(f"{self.BASE_URL}/logs/summary")
        summary = summary_response.json()
        
        if summary["total_entries"] > 0:
            # Verify the first entry
            response = requests.get(f"{self.BASE_URL}/logs/verify/0")
            assert response.status_code == 200
            
            data = response.json()
            assert "entry_index" in data
            assert "is_valid" in data
            assert "proof" in data
            assert data["is_valid"] is True
    
    def test_invalid_entry_verification(self):
        """Test verification of non-existent entry."""
        response = requests.get(f"{self.BASE_URL}/logs/verify/99999")
        assert response.status_code == 404

class TestIntegration:
    """Integration tests for the complete system."""
    
    def test_api_logging_integration(self):
        """Test that API calls are properly logged."""
        base_url = "http://localhost:8000"
        
        # Get initial log count
        initial_response = requests.get(f"{base_url}/logs/summary")
        if initial_response.status_code == 200:
            initial_count = initial_response.json()["total_entries"]
            
            # Make some API calls
            requests.get(f"{base_url}/health")
            requests.get(f"{base_url}/version")
            
            # Check if log count increased
            final_response = requests.get(f"{base_url}/logs/summary")
            if final_response.status_code == 200:
                final_count = final_response.json()["total_entries"]
                assert final_count > initial_count, "API calls should be logged"

if __name__ == "__main__":
    pytest.main([__file__, "-v"])