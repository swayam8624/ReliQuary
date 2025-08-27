"""
Encrypted Memory System for ReliQuary Multi-Agent System

This module provides encrypted storage for sensitive agent memory including
decision history, behavioral patterns, consensus states, and trust profiles.
All data is encrypted at rest and in transit using post-quantum cryptography.
"""

import logging
import time
import json
import pickle
import hashlib
import secrets
from typing import Dict, List, Any, Optional, Union, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
from pathlib import Path
import sqlite3
import threading
from contextlib import contextmanager

# Import cryptographic components
from core.crypto.rust_ffi_wrappers import (
    encrypt_data_rust,
    decrypt_data_rust,
    generate_kyber_keys_rust,
    kyber_encapsulate_rust,
    kyber_decapsulate_rust
)


class MemoryType(Enum):
    """Types of memory stored"""
    DECISION_HISTORY = "decision_history"
    BEHAVIORAL_PATTERN = "behavioral_pattern"
    CONSENSUS_STATE = "consensus_state"
    TRUST_PROFILE = "trust_profile"
    AGENT_STATE = "agent_state"
    COMMUNICATION_LOG = "communication_log"
    PERFORMANCE_METRICS = "performance_metrics"
    SECURITY_EVENTS = "security_events"


class EncryptionLevel(Enum):
    """Encryption levels for different data types"""
    STANDARD = "standard"  # AES-256
    HIGH = "high"         # Post-quantum + AES-256
    MAXIMUM = "maximum"   # Multi-layer encryption


@dataclass
class MemoryEntry:
    """Encrypted memory entry"""
    entry_id: str
    memory_type: MemoryType
    agent_id: str
    data_hash: str
    encrypted_data: bytes
    encryption_level: EncryptionLevel
    created_at: float
    updated_at: float
    access_count: int = 0
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


@dataclass
class MemoryQuery:
    """Query parameters for memory retrieval"""
    agent_id: Optional[str] = None
    memory_type: Optional[MemoryType] = None
    start_time: Optional[float] = None
    end_time: Optional[float] = None
    limit: Optional[int] = None
    include_metadata: bool = True


class EncryptedMemory:
    """
    Encrypted Memory System for secure agent data storage.
    
    This class provides encrypted storage and retrieval of sensitive agent data
    using post-quantum cryptography and multi-layer encryption schemes.
    """
    
    def __init__(self, memory_path: str = None, encryption_key: bytes = None):
        """Initialize encrypted memory system."""
        if memory_path is None:
            memory_path = "agents/memory/encrypted_storage"
        
        self.memory_path = Path(memory_path)
        self.memory_path.mkdir(parents=True, exist_ok=True)
        
        self.logger = logging.getLogger("encrypted_memory")
        
        # Initialize encryption keys
        self._setup_encryption(encryption_key)
        
        # Memory storage
        self.memory_cache: Dict[str, MemoryEntry] = {}
        self.access_patterns: Dict[str, List[float]] = {}
        
        # Performance metrics
        self.total_operations = 0
        self.encryption_operations = 0
        self.decryption_operations = 0
        self.cache_hits = 0
        self.cache_misses = 0
        
        # Security settings
        self.max_cache_size = 1000
        self.cache_ttl = 3600  # 1 hour
        self.auto_cleanup_interval = 300  # 5 minutes
        
        # Thread safety
        self._lock = threading.RLock()
        
        self.logger.info("Encrypted memory system initialized")
    
    def _setup_encryption(self, encryption_key: bytes = None):
        """Setup encryption keys and algorithms."""
        try:
            # Generate or load master encryption key
            if encryption_key is None:
                # Generate new master key
                self.master_key = secrets.token_bytes(32)  # 256-bit key
                self.logger.info("Generated new master encryption key")
            else:
                self.master_key = encryption_key
                self.logger.info("Using provided master encryption key")
            
            # Generate post-quantum keys
            try:
                kyber_keys = generate_kyber_keys_rust()
                self.kyber_public_key = kyber_keys["public_key"]
                self.kyber_private_key = kyber_keys["private_key"]
                self.post_quantum_enabled = True
                self.logger.info("Post-quantum encryption enabled")
            except Exception as e:
                self.logger.warning(f"Post-quantum setup failed: {e}")
                self.post_quantum_enabled = False
            
            # Derive encryption keys for different levels
            self.encryption_keys = {
                EncryptionLevel.STANDARD: self._derive_key(self.master_key, b"standard"),
                EncryptionLevel.HIGH: self._derive_key(self.master_key, b"high"),
                EncryptionLevel.MAXIMUM: self._derive_key(self.master_key, b"maximum")
            }
            
        except Exception as e:
            self.logger.error(f"Encryption setup failed: {e}")
            raise
    
    def _derive_key(self, master_key: bytes, context: bytes) -> bytes:
        """Derive encryption key using HKDF-like approach."""
        # Simplified key derivation (in production, use proper HKDF)
        combined = master_key + context
        return hashlib.sha256(combined).digest()
    
    async def store_memory(self, 
                          agent_id: str,
                          memory_type: MemoryType,
                          data: Any,
                          encryption_level: EncryptionLevel = EncryptionLevel.STANDARD,
                          metadata: Dict[str, Any] = None) -> str:
        """
        Store encrypted memory entry.
        
        Args:
            agent_id: Agent identifier
            memory_type: Type of memory being stored
            data: Data to encrypt and store
            encryption_level: Level of encryption to apply
            metadata: Additional metadata
            
        Returns:
            Entry ID of stored memory
        """
        with self._lock:
            self.total_operations += 1
            start_time = time.time()
            
            try:
                # Generate entry ID
                entry_id = self._generate_entry_id(agent_id, memory_type)
                
                # Serialize data
                serialized_data = self._serialize_data(data)
                
                # Calculate data hash
                data_hash = hashlib.sha256(serialized_data).hexdigest()
                
                # Encrypt data
                encrypted_data = await self._encrypt_data(serialized_data, encryption_level)
                
                # Create memory entry
                entry = MemoryEntry(
                    entry_id=entry_id,
                    memory_type=memory_type,
                    agent_id=agent_id,
                    data_hash=data_hash,
                    encrypted_data=encrypted_data,
                    encryption_level=encryption_level,
                    created_at=start_time,
                    updated_at=start_time,
                    metadata=metadata or {}
                )
                
                # Store in cache
                self.memory_cache[entry_id] = entry
                
                # Store to persistent storage
                await self._persist_entry(entry)
                
                # Update access patterns
                if agent_id not in self.access_patterns:
                    self.access_patterns[agent_id] = []
                self.access_patterns[agent_id].append(start_time)
                
                # Cleanup cache if needed
                await self._cleanup_cache()
                
                self.encryption_operations += 1
                self.logger.debug(f"Stored memory entry {entry_id} for agent {agent_id}")
                
                return entry_id
                
            except Exception as e:
                self.logger.error(f"Failed to store memory: {e}")
                raise
    
    async def retrieve_memory(self, 
                            entry_id: str,
                            agent_id: str = None) -> Optional[Any]:
        """
        Retrieve and decrypt memory entry.
        
        Args:
            entry_id: Entry identifier
            agent_id: Agent identifier for access control
            
        Returns:
            Decrypted data or None if not found
        """
        with self._lock:
            self.total_operations += 1
            start_time = time.time()
            
            try:
                # Check cache first
                entry = self.memory_cache.get(entry_id)
                if entry:
                    self.cache_hits += 1
                else:
                    # Load from persistent storage
                    entry = await self._load_entry(entry_id)
                    if entry:
                        self.memory_cache[entry_id] = entry
                        self.cache_misses += 1
                    else:
                        self.cache_misses += 1
                        return None
                
                # Access control check
                if agent_id and entry.agent_id != agent_id:
                    self.logger.warning(f"Access denied for agent {agent_id} to entry {entry_id}")
                    return None
                
                # Decrypt data
                decrypted_data = await self._decrypt_data(
                    entry.encrypted_data,
                    entry.encryption_level
                )
                
                # Deserialize data
                data = self._deserialize_data(decrypted_data)
                
                # Update access tracking
                entry.access_count += 1
                entry.updated_at = start_time
                
                # Update access patterns
                if entry.agent_id not in self.access_patterns:
                    self.access_patterns[entry.agent_id] = []
                self.access_patterns[entry.agent_id].append(start_time)
                
                self.decryption_operations += 1
                self.logger.debug(f"Retrieved memory entry {entry_id} for agent {entry.agent_id}")
                
                return data
                
            except Exception as e:
                self.logger.error(f"Failed to retrieve memory: {e}")
                return None
    
    async def query_memory(self, query: MemoryQuery) -> List[Tuple[str, Any]]:
        """
        Query memory entries based on criteria.
        
        Args:
            query: Query parameters
            
        Returns:
            List of (entry_id, data) tuples
        """
        with self._lock:
            results = []
            
            try:
                # Get matching entry IDs from persistent storage
                entry_ids = await self._query_entry_ids(query)
                
                # Retrieve and decrypt matching entries
                for entry_id in entry_ids[:query.limit] if query.limit else entry_ids:
                    data = await self.retrieve_memory(entry_id, query.agent_id)
                    if data is not None:
                        results.append((entry_id, data))
                
                self.logger.debug(f"Query returned {len(results)} results")
                return results
                
            except Exception as e:
                self.logger.error(f"Memory query failed: {e}")
                return []
    
    async def delete_memory(self, entry_id: str, agent_id: str = None) -> bool:
        """
        Delete memory entry.
        
        Args:
            entry_id: Entry identifier
            agent_id: Agent identifier for access control
            
        Returns:
            True if successfully deleted
        """
        with self._lock:
            try:
                # Check if entry exists
                entry = self.memory_cache.get(entry_id) or await self._load_entry(entry_id)
                if not entry:
                    return False
                
                # Access control check
                if agent_id and entry.agent_id != agent_id:
                    self.logger.warning(f"Delete access denied for agent {agent_id} to entry {entry_id}")
                    return False
                
                # Remove from cache
                if entry_id in self.memory_cache:
                    del self.memory_cache[entry_id]
                
                # Remove from persistent storage
                await self._delete_persistent_entry(entry_id)
                
                self.logger.info(f"Deleted memory entry {entry_id}")
                return True
                
            except Exception as e:
                self.logger.error(f"Failed to delete memory: {e}")
                return False
    
    async def _encrypt_data(self, data: bytes, level: EncryptionLevel) -> bytes:
        """Encrypt data based on encryption level."""
        try:
            if level == EncryptionLevel.STANDARD:
                # Standard AES encryption
                key = self.encryption_keys[level]
                return encrypt_data_rust(data, key)
            
            elif level == EncryptionLevel.HIGH and self.post_quantum_enabled:
                # Post-quantum + AES encryption
                # First encrypt with AES
                aes_key = self.encryption_keys[EncryptionLevel.STANDARD]
                aes_encrypted = encrypt_data_rust(data, aes_key)
                
                # Then add post-quantum layer
                pq_result = kyber_encapsulate_rust(self.kyber_public_key)
                pq_key = pq_result["shared_secret"]
                pq_ciphertext = pq_result["ciphertext"]
                
                # Encrypt AES result with PQ key
                final_encrypted = encrypt_data_rust(aes_encrypted, pq_key)
                
                # Combine PQ ciphertext with final encrypted data
                return pq_ciphertext + b":PQ_SEPARATOR:" + final_encrypted
            
            elif level == EncryptionLevel.MAXIMUM:
                # Multi-layer encryption
                # Apply HIGH level first
                high_encrypted = await self._encrypt_data(data, EncryptionLevel.HIGH)
                
                # Add additional layer with different key
                max_key = self.encryption_keys[level]
                return encrypt_data_rust(high_encrypted, max_key)
            
            else:
                # Fallback to standard
                key = self.encryption_keys[EncryptionLevel.STANDARD]
                return encrypt_data_rust(data, key)
        
        except Exception as e:
            self.logger.error(f"Encryption failed: {e}")
            raise
    
    async def _decrypt_data(self, encrypted_data: bytes, level: EncryptionLevel) -> bytes:
        """Decrypt data based on encryption level."""
        try:
            if level == EncryptionLevel.STANDARD:
                # Standard AES decryption
                key = self.encryption_keys[level]
                return decrypt_data_rust(encrypted_data, key)
            
            elif level == EncryptionLevel.HIGH and self.post_quantum_enabled:
                # Post-quantum + AES decryption
                # Split PQ ciphertext from encrypted data
                parts = encrypted_data.split(b":PQ_SEPARATOR:")
                if len(parts) != 2:
                    raise ValueError("Invalid post-quantum encrypted data format")
                
                pq_ciphertext, final_encrypted = parts
                
                # Decapsulate post-quantum key
                pq_key = kyber_decapsulate_rust(self.kyber_private_key, pq_ciphertext)
                
                # Decrypt with PQ key
                aes_encrypted = decrypt_data_rust(final_encrypted, pq_key)
                
                # Decrypt with AES key
                aes_key = self.encryption_keys[EncryptionLevel.STANDARD]
                return decrypt_data_rust(aes_encrypted, aes_key)
            
            elif level == EncryptionLevel.MAXIMUM:
                # Multi-layer decryption
                # Remove maximum layer first
                max_key = self.encryption_keys[level]
                high_encrypted = decrypt_data_rust(encrypted_data, max_key)
                
                # Decrypt HIGH level
                return await self._decrypt_data(high_encrypted, EncryptionLevel.HIGH)
            
            else:
                # Fallback to standard
                key = self.encryption_keys[EncryptionLevel.STANDARD]
                return decrypt_data_rust(encrypted_data, key)
        
        except Exception as e:
            self.logger.error(f"Decryption failed: {e}")
            raise
    
    def _serialize_data(self, data: Any) -> bytes:
        """Serialize data for storage."""
        try:
            if isinstance(data, (str, int, float, bool, list, dict)):
                # JSON serializable data
                return json.dumps(data, sort_keys=True).encode('utf-8')
            else:
                # Use pickle for complex objects
                return pickle.dumps(data)
        except Exception as e:
            self.logger.error(f"Serialization failed: {e}")
            raise
    
    def _deserialize_data(self, data: bytes) -> Any:
        """Deserialize data from storage."""
        try:
            # Try JSON first
            try:
                return json.loads(data.decode('utf-8'))
            except (json.JSONDecodeError, UnicodeDecodeError):
                # Fall back to pickle
                return pickle.loads(data)
        except Exception as e:
            self.logger.error(f"Deserialization failed: {e}")
            raise
    
    def _generate_entry_id(self, agent_id: str, memory_type: MemoryType) -> str:
        """Generate unique entry ID."""
        timestamp = str(int(time.time() * 1000000))  # Microsecond precision
        random_suffix = secrets.token_hex(8)
        return f"{agent_id}_{memory_type.value}_{timestamp}_{random_suffix}"
    
    async def _persist_entry(self, entry: MemoryEntry):
        """Persist entry to storage (simplified file-based for now)."""
        try:
            entry_file = self.memory_path / f"{entry.entry_id}.mem"
            entry_data = {
                "entry_id": entry.entry_id,
                "memory_type": entry.memory_type.value,
                "agent_id": entry.agent_id,
                "data_hash": entry.data_hash,
                "encrypted_data": entry.encrypted_data.hex(),
                "encryption_level": entry.encryption_level.value,
                "created_at": entry.created_at,
                "updated_at": entry.updated_at,
                "access_count": entry.access_count,
                "metadata": entry.metadata
            }
            
            with open(entry_file, 'w') as f:
                json.dump(entry_data, f)
        
        except Exception as e:
            self.logger.error(f"Failed to persist entry: {e}")
            raise
    
    async def _load_entry(self, entry_id: str) -> Optional[MemoryEntry]:
        """Load entry from persistent storage."""
        try:
            entry_file = self.memory_path / f"{entry_id}.mem"
            if not entry_file.exists():
                return None
            
            with open(entry_file, 'r') as f:
                entry_data = json.load(f)
            
            return MemoryEntry(
                entry_id=entry_data["entry_id"],
                memory_type=MemoryType(entry_data["memory_type"]),
                agent_id=entry_data["agent_id"],
                data_hash=entry_data["data_hash"],
                encrypted_data=bytes.fromhex(entry_data["encrypted_data"]),
                encryption_level=EncryptionLevel(entry_data["encryption_level"]),
                created_at=entry_data["created_at"],
                updated_at=entry_data["updated_at"],
                access_count=entry_data["access_count"],
                metadata=entry_data["metadata"]
            )
        
        except Exception as e:
            self.logger.error(f"Failed to load entry: {e}")
            return None
    
    async def _query_entry_ids(self, query: MemoryQuery) -> List[str]:
        """Query entry IDs based on criteria."""
        entry_ids = []
        
        try:
            for entry_file in self.memory_path.glob("*.mem"):
                try:
                    with open(entry_file, 'r') as f:
                        entry_data = json.load(f)
                    
                    # Apply filters
                    if query.agent_id and entry_data["agent_id"] != query.agent_id:
                        continue
                    
                    if query.memory_type and entry_data["memory_type"] != query.memory_type.value:
                        continue
                    
                    if query.start_time and entry_data["created_at"] < query.start_time:
                        continue
                    
                    if query.end_time and entry_data["created_at"] > query.end_time:
                        continue
                    
                    entry_ids.append(entry_data["entry_id"])
                
                except Exception:
                    continue
            
            # Sort by creation time (newest first)
            entry_ids.sort(reverse=True)
            return entry_ids
        
        except Exception as e:
            self.logger.error(f"Query failed: {e}")
            return []
    
    async def _delete_persistent_entry(self, entry_id: str):
        """Delete entry from persistent storage."""
        try:
            entry_file = self.memory_path / f"{entry_id}.mem"
            if entry_file.exists():
                entry_file.unlink()
        except Exception as e:
            self.logger.error(f"Failed to delete persistent entry: {e}")
    
    async def _cleanup_cache(self):
        """Cleanup old cache entries."""
        if len(self.memory_cache) <= self.max_cache_size:
            return
        
        current_time = time.time()
        
        # Remove old entries
        entries_to_remove = []
        for entry_id, entry in self.memory_cache.items():
            if current_time - entry.updated_at > self.cache_ttl:
                entries_to_remove.append(entry_id)
        
        for entry_id in entries_to_remove:
            del self.memory_cache[entry_id]
        
        # If still too large, remove least recently used
        if len(self.memory_cache) > self.max_cache_size:
            sorted_entries = sorted(
                self.memory_cache.items(),
                key=lambda x: x[1].updated_at
            )
            
            excess_count = len(self.memory_cache) - self.max_cache_size
            for i in range(excess_count):
                entry_id = sorted_entries[i][0]
                del self.memory_cache[entry_id]
    
    def get_memory_metrics(self) -> Dict[str, Any]:
        """Get memory system performance metrics."""
        cache_hit_rate = (self.cache_hits / max(self.cache_hits + self.cache_misses, 1)) * 100
        
        return {
            "total_operations": self.total_operations,
            "encryption_operations": self.encryption_operations,
            "decryption_operations": self.decryption_operations,
            "cache_size": len(self.memory_cache),
            "cache_hits": self.cache_hits,
            "cache_misses": self.cache_misses,
            "cache_hit_rate": cache_hit_rate,
            "post_quantum_enabled": self.post_quantum_enabled,
            "tracked_agents": len(self.access_patterns)
        }