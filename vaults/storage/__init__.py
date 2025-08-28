"""
Vault Storage Package for ReliQuary

This package contains storage implementations for vault data.
"""

# Import storage components
from .base import (
    StorageBackend,
    StorageError
)

from .local import (
    LocalStorageBackend
)

# Cloud storage placeholders
try:
    from .s3 import S3StorageBackend
except ImportError:
    S3StorageBackend = None

try:
    from .ipfs import IPFSStorageBackend
except ImportError:
    IPFSStorageBackend = None

try:
    from .arweave import ArweaveStorageBackend
except ImportError:
    ArweaveStorageBackend = None

__all__ = [
    "StorageBackend",
    "StorageError",
    "LocalStorageBackend",
    "S3StorageBackend",
    "IPFSStorageBackend",
    "ArweaveStorageBackend"
]