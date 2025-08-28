"""
Database Manager for ReliQuary Multi-Agent System

This module provides a robust database management system for persistent storage
of agent memory, trust history, and consensus records. It uses SQLite for 
local development and can be extended to support other databases in production.
"""

import logging
import sqlite3
import json
import time
import threading
from typing import Dict, List, Any, Optional, Tuple
from contextlib import contextmanager
from dataclasses import dataclass, asdict
from pathlib import Path

from .encrypted_memory import MemoryType, EncryptionLevel


@dataclass
class DBRecord:
    """Database record structure"""
    id: str
    agent_id: str
    record_type: str  # 'memory', 'trust_history', 'consensus_record', etc.
    data: str  # JSON serialized data
    created_at: float
    updated_at: float
    metadata: str  # JSON serialized metadata


class DBManager:
    """
    Database Manager for persistent agent memory and trust history storage.
    
    This class provides a database interface for storing and retrieving
    agent memory, trust history, and consensus records with proper
    indexing and query capabilities.
    """
    
    def __init__(self, db_path: str = None):
        """
        Initialize the database manager.
        
        Args:
            db_path: Path to the SQLite database file. If None, uses default location.
        """
        if db_path is None:
            db_path = "agents/memory/agent_memory.db"
        
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        
        self.logger = logging.getLogger("db_manager")
        self._lock = threading.RLock()
        
        # Initialize database
        self._initialize_database()
        
        self.logger.info(f"Database manager initialized with database at {self.db_path}")
    
    def _initialize_database(self):
        """Initialize the database schema."""
        with self._get_connection() as conn:
            # Create tables
            conn.execute('''
                CREATE TABLE IF NOT EXISTS records (
                    id TEXT PRIMARY KEY,
                    agent_id TEXT NOT NULL,
                    record_type TEXT NOT NULL,
                    data TEXT NOT NULL,
                    created_at REAL NOT NULL,
                    updated_at REAL NOT NULL,
                    metadata TEXT
                )
            ''')
            
            # Create indexes for performance
            conn.execute('''
                CREATE INDEX IF NOT EXISTS idx_agent_id ON records(agent_id)
            ''')
            
            conn.execute('''
                CREATE INDEX IF NOT EXISTS idx_record_type ON records(record_type)
            ''')
            
            conn.execute('''
                CREATE INDEX IF NOT EXISTS idx_created_at ON records(created_at)
            ''')
            
            conn.execute('''
                CREATE INDEX IF NOT EXISTS idx_agent_type_created ON records(agent_id, record_type, created_at)
            ''')
            
            conn.commit()
    
    @contextmanager
    def _get_connection(self):
        """Get a database connection with proper error handling."""
        conn = None
        try:
            conn = sqlite3.connect(str(self.db_path), timeout=30.0)
            conn.row_factory = sqlite3.Row  # Enable dict-like access to rows
            yield conn
        except Exception as e:
            if conn:
                conn.rollback()
            self.logger.error(f"Database connection error: {e}")
            raise
        finally:
            if conn:
                conn.close()
    
    async def store_record(self, 
                          record_id: str,
                          agent_id: str,
                          record_type: str,
                          data: Dict[str, Any],
                          metadata: Dict[str, Any] = None) -> bool:
        """
        Store a record in the database.
        
        Args:
            record_id: Unique identifier for the record
            agent_id: Agent identifier
            record_type: Type of record (e.g., 'memory', 'trust_history')
            data: Record data as dictionary
            metadata: Additional metadata
            
        Returns:
            True if successfully stored, False otherwise
        """
        with self._lock:
            try:
                timestamp = time.time()
                
                # Serialize data and metadata
                serialized_data = json.dumps(data, sort_keys=True)
                serialized_metadata = json.dumps(metadata or {}, sort_keys=True)
                
                with self._get_connection() as conn:
                    # Check if record exists
                    cursor = conn.execute(
                        "SELECT id FROM records WHERE id = ?", (record_id,)
                    )
                    
                    if cursor.fetchone():
                        # Update existing record
                        conn.execute('''
                            UPDATE records 
                            SET agent_id = ?, record_type = ?, data = ?, 
                                updated_at = ?, metadata = ?
                            WHERE id = ?
                        ''', (agent_id, record_type, serialized_data, 
                              timestamp, serialized_metadata, record_id))
                    else:
                        # Insert new record
                        conn.execute('''
                            INSERT INTO records 
                            (id, agent_id, record_type, data, created_at, updated_at, metadata)
                            VALUES (?, ?, ?, ?, ?, ?, ?)
                        ''', (record_id, agent_id, record_type, serialized_data, 
                              timestamp, timestamp, serialized_metadata))
                    
                    conn.commit()
                
                self.logger.debug(f"Stored record {record_id} for agent {agent_id}")
                return True
                
            except Exception as e:
                self.logger.error(f"Failed to store record {record_id}: {e}")
                return False
    
    async def retrieve_record(self, record_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve a record from the database.
        
        Args:
            record_id: Unique identifier for the record
            
        Returns:
            Record data as dictionary, or None if not found
        """
        with self._lock:
            try:
                with self._get_connection() as conn:
                    cursor = conn.execute(
                        "SELECT * FROM records WHERE id = ?", (record_id,)
                    )
                    row = cursor.fetchone()
                    
                    if row:
                        return {
                            "id": row["id"],
                            "agent_id": row["agent_id"],
                            "record_type": row["record_type"],
                            "data": json.loads(row["data"]),
                            "created_at": row["created_at"],
                            "updated_at": row["updated_at"],
                            "metadata": json.loads(row["metadata"]) if row["metadata"] else {}
                        }
                
                return None
                
            except Exception as e:
                self.logger.error(f"Failed to retrieve record {record_id}: {e}")
                return None
    
    async def query_records(self, 
                          agent_id: Optional[str] = None,
                          record_type: Optional[str] = None,
                          limit: Optional[int] = None,
                          offset: Optional[int] = None,
                          start_time: Optional[float] = None,
                          end_time: Optional[float] = None) -> List[Dict[str, Any]]:
        """
        Query records based on criteria.
        
        Args:
            agent_id: Filter by agent ID
            record_type: Filter by record type
            limit: Maximum number of records to return
            offset: Number of records to skip
            start_time: Filter by creation time (start)
            end_time: Filter by creation time (end)
            
        Returns:
            List of matching records
        """
        with self._lock:
            try:
                # Build query dynamically
                query_parts = ["SELECT * FROM records WHERE 1=1"]
                params = []
                
                if agent_id:
                    query_parts.append("AND agent_id = ?")
                    params.append(agent_id)
                
                if record_type:
                    query_parts.append("AND record_type = ?")
                    params.append(record_type)
                
                if start_time:
                    query_parts.append("AND created_at >= ?")
                    params.append(start_time)
                
                if end_time:
                    query_parts.append("AND created_at <= ?")
                    params.append(end_time)
                
                # Order by creation time (newest first)
                query_parts.append("ORDER BY created_at DESC")
                
                if limit:
                    query_parts.append("LIMIT ?")
                    params.append(limit)
                
                if offset:
                    query_parts.append("OFFSET ?")
                    params.append(offset)
                
                query = " ".join(query_parts)
                
                with self._get_connection() as conn:
                    cursor = conn.execute(query, params)
                    rows = cursor.fetchall()
                
                # Convert rows to dictionaries
                records = []
                for row in rows:
                    records.append({
                        "id": row["id"],
                        "agent_id": row["agent_id"],
                        "record_type": row["record_type"],
                        "data": json.loads(row["data"]),
                        "created_at": row["created_at"],
                        "updated_at": row["updated_at"],
                        "metadata": json.loads(row["metadata"]) if row["metadata"] else {}
                    })
                
                self.logger.debug(f"Query returned {len(records)} records")
                return records
                
            except Exception as e:
                self.logger.error(f"Record query failed: {e}")
                return []
    
    async def delete_record(self, record_id: str) -> bool:
        """
        Delete a record from the database.
        
        Args:
            record_id: Unique identifier for the record
            
        Returns:
            True if successfully deleted, False otherwise
        """
        with self._lock:
            try:
                with self._get_connection() as conn:
                    cursor = conn.execute(
                        "DELETE FROM records WHERE id = ?", (record_id,)
                    )
                    conn.commit()
                    
                    deleted_count = cursor.rowcount
                
                if deleted_count > 0:
                    self.logger.debug(f"Deleted record {record_id}")
                    return True
                else:
                    self.logger.debug(f"Record {record_id} not found for deletion")
                    return False
                
            except Exception as e:
                self.logger.error(f"Failed to delete record {record_id}: {e}")
                return False
    
    async def store_memory_entry(self, 
                               entry_id: str,
                               agent_id: str,
                               memory_type: MemoryType,
                               data: Any,
                               encryption_level: EncryptionLevel = EncryptionLevel.STANDARD,
                               metadata: Dict[str, Any] = None) -> bool:
        """
        Store an encrypted memory entry in the database.
        
        Args:
            entry_id: Entry identifier
            agent_id: Agent identifier
            memory_type: Type of memory
            data: Encrypted data (should already be encrypted)
            encryption_level: Encryption level used
            metadata: Additional metadata
            
        Returns:
            True if successfully stored, False otherwise
        """
        memory_data = {
            "entry_id": entry_id,
            "agent_id": agent_id,
            "memory_type": memory_type.value,
            "data": data if isinstance(data, (str, bytes)) else json.dumps(data),
            "encryption_level": encryption_level.value,
            "stored_at": time.time()
        }
        
        return await self.store_record(
            record_id=entry_id,
            agent_id=agent_id,
            record_type="memory",
            data=memory_data,
            metadata=metadata
        )
    
    async def retrieve_memory_entry(self, entry_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve an encrypted memory entry from the database.
        
        Args:
            entry_id: Entry identifier
            
        Returns:
            Memory entry data, or None if not found
        """
        record = await self.retrieve_record(entry_id)
        if record and record.get("record_type") == "memory":
            return record["data"]
        return None
    
    async def store_trust_history(self, 
                                history_id: str,
                                agent_id: str,
                                user_id: str,
                                trust_score: float,
                                factors: List[str],
                                timestamp: float = None) -> bool:
        """
        Store trust history record.
        
        Args:
            history_id: History record identifier
            agent_id: Agent identifier
            user_id: User identifier
            trust_score: Trust score value
            factors: Factors contributing to trust score
            timestamp: When the trust evaluation occurred
            
        Returns:
            True if successfully stored, False otherwise
        """
        if timestamp is None:
            timestamp = time.time()
        
        trust_data = {
            "history_id": history_id,
            "agent_id": agent_id,
            "user_id": user_id,
            "trust_score": trust_score,
            "factors": factors,
            "timestamp": timestamp
        }
        
        return await self.store_record(
            record_id=history_id,
            agent_id=agent_id,
            record_type="trust_history",
            data=trust_data,
            metadata={"user_id": user_id, "trust_score": trust_score}
        )
    
    async def get_trust_history(self, 
                              user_id: str,
                              agent_id: str = None,
                              limit: int = 100) -> List[Dict[str, Any]]:
        """
        Get trust history for a user.
        
        Args:
            user_id: User identifier
            agent_id: Filter by agent (optional)
            limit: Maximum number of records to return
            
        Returns:
            List of trust history records
        """
        records = await self.query_records(
            agent_id=agent_id,
            record_type="trust_history",
            limit=limit
        )
        
        # Filter by user_id in metadata
        trust_history = []
        for record in records:
            if record.get("metadata", {}).get("user_id") == user_id:
                trust_history.append(record["data"])
        
        return trust_history
    
    async def store_consensus_record(self, 
                                   consensus_id: str,
                                   agent_id: str,
                                   decision: str,
                                   confidence: float,
                                   participating_agents: List[str],
                                   reasoning: List[str]) -> bool:
        """
        Store consensus decision record.
        
        Args:
            consensus_id: Consensus record identifier
            agent_id: Agent identifier
            decision: Final decision
            confidence: Confidence level
            participating_agents: List of agents that participated
            reasoning: Reasoning chain
            
        Returns:
            True if successfully stored, False otherwise
        """
        consensus_data = {
            "consensus_id": consensus_id,
            "agent_id": agent_id,
            "decision": decision,
            "confidence": confidence,
            "participating_agents": participating_agents,
            "reasoning": reasoning,
            "timestamp": time.time()
        }
        
        return await self.store_record(
            record_id=consensus_id,
            agent_id=agent_id,
            record_type="consensus_record",
            data=consensus_data,
            metadata={
                "decision": decision,
                "confidence": confidence,
                "participant_count": len(participating_agents)
            }
        )
    
    async def get_recent_consensus_records(self, 
                                         agent_id: str = None,
                                         limit: int = 50) -> List[Dict[str, Any]]:
        """
        Get recent consensus records.
        
        Args:
            agent_id: Filter by agent (optional)
            limit: Maximum number of records to return
            
        Returns:
            List of recent consensus records
        """
        records = await self.query_records(
            agent_id=agent_id,
            record_type="consensus_record",
            limit=limit
        )
        
        return [record["data"] for record in records]
    
    def get_database_stats(self) -> Dict[str, Any]:
        """
        Get database statistics.
        
        Returns:
            Dictionary with database statistics
        """
        try:
            with self._get_connection() as conn:
                # Get record counts by type
                cursor = conn.execute('''
                    SELECT record_type, COUNT(*) as count
                    FROM records
                    GROUP BY record_type
                ''')
                type_counts = dict(cursor.fetchall())
                
                # Get total record count
                cursor = conn.execute("SELECT COUNT(*) FROM records")
                total_records = cursor.fetchone()[0]
                
                # Get agent count
                cursor = conn.execute('''
                    SELECT COUNT(DISTINCT agent_id) 
                    FROM records
                ''')
                agent_count = cursor.fetchone()[0]
                
                # Get database size
                db_size = self.db_path.stat().st_size if self.db_path.exists() else 0
                
                return {
                    "total_records": total_records,
                    "agent_count": agent_count,
                    "record_types": type_counts,
                    "database_size_bytes": db_size,
                    "database_path": str(self.db_path)
                }
                
        except Exception as e:
            self.logger.error(f"Failed to get database stats: {e}")
            return {
                "error": str(e)
            }
    
    async def cleanup_old_records(self, 
                                record_type: Optional[str] = None,
                                older_than_days: int = 30) -> int:
        """
        Clean up old records from the database.
        
        Args:
            record_type: Type of records to clean up (None for all types)
            older_than_days: Age threshold in days
            
        Returns:
            Number of records deleted
        """
        with self._lock:
            try:
                cutoff_time = time.time() - (older_than_days * 24 * 60 * 60)
                
                with self._get_connection() as conn:
                    if record_type:
                        cursor = conn.execute('''
                            DELETE FROM records 
                            WHERE record_type = ? AND created_at < ?
                        ''', (record_type, cutoff_time))
                    else:
                        cursor = conn.execute('''
                            DELETE FROM records 
                            WHERE created_at < ?
                        ''', (cutoff_time,))
                    
                    conn.commit()
                    deleted_count = cursor.rowcount
                
                self.logger.info(f"Cleaned up {deleted_count} old records")
                return deleted_count
                
            except Exception as e:
                self.logger.error(f"Failed to clean up old records: {e}")
                return 0
    
    def backup_database(self, backup_path: str = None) -> bool:
        """
        Create a backup of the database.
        
        Args:
            backup_path: Path for backup file (default: auto-generated)
            
        Returns:
            True if backup successful, False otherwise
        """
        try:
            if backup_path is None:
                timestamp = int(time.time())
                backup_path = f"{self.db_path}.backup.{timestamp}"
            
            backup_path = Path(backup_path)
            backup_path.parent.mkdir(parents=True, exist_ok=True)
            
            with self._get_connection() as conn:
                backup_conn = sqlite3.connect(str(backup_path))
                conn.backup(backup_conn)
                backup_conn.close()
            
            self.logger.info(f"Database backed up to {backup_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"Database backup failed: {e}")
            return False


# Convenience function to create a standard database manager
def create_standard_db_manager() -> DBManager:
    """
    Create a standard database manager with default configuration.
    
    Returns:
        DBManager instance with standard configuration
    """
    return DBManager()