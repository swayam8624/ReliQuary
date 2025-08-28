"""
Vaults package for ReliQuary platform.

This package provides the core functionality for managing encrypted data vaults,
including storage backends, data models, and trust management.
"""

# Import core vault components
from .vault import Vault
from .manager import VaultManager
from .storage.base import StorageBackend

# Version information
__version__ = "1.0.0"
__author__ = "ReliQuary Team"
__email__ = "support@reliquary.io"

# Package metadata
__all__ = [
    "Vault",
    "VaultManager", 
    "StorageBackend"
]

# Package description
__description__ = """
ReliQuary Vaults - Secure, encrypted data storage with contextual trust verification.

Features:
- Post-quantum encryption (Kyber, Falcon)
- Zero-knowledge proofs for context verification
- Multi-agent consensus for access decisions
- Pluggable storage backends (local, cloud, decentralized)
- Trust scoring based on behavioral analysis
"""

# Initialize package-level logging
import logging
logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())

# Package initialization message
def _initialize_package():
    """Initialize the vaults package."""
    logger.info("Initializing ReliQuary Vaults package v%s", __version__)

# Run package initialization
_initialize_package()