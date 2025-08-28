"""
Memory Package for ReliQuary Multi-Agent System

This package contains components for managing persistent and encrypted memory
for agents in the multi-agent consensus system.
"""

from .encrypted_memory import (
    EncryptedMemory,
    MemoryType,
    EncryptionLevel,
    MemoryEntry,
    MemoryQuery
)

# Only import DBManager if it exists, otherwise it will be implemented later
try:
    from .db_manager import DBManager
    __all__ = [
        "EncryptedMemory",
        "MemoryType", 
        "EncryptionLevel",
        "MemoryEntry",
        "MemoryQuery",
        "DBManager"
    ]
except ImportError:
    # DBManager will be implemented in a separate file
    __all__ = [
        "EncryptedMemory",
        "MemoryType",
        "EncryptionLevel", 
        "MemoryEntry",
        "MemoryQuery"
    ]