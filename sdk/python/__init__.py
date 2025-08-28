"""
ReliQuary Python SDK
Enterprise-grade cryptographic memory vault system SDK
"""

from .client import ReliQuaryClient, ReliQuaryAPIClient
from .exceptions import (
    ReliQuaryError,
    ReliQuaryAPIError,
    ReliQuaryAuthError,
    ReliQuaryValidationError,
    ReliQuaryConsensusError,
    ReliQuaryZKError,
    ReliQuaryVaultError,
    ReliQuaryNetworkError,
    ReliQuaryTimeoutError
)
from .models.api_schemas import (
    ConsensusRequest,
    ConsensusResult,
    ConsensusType,
    ZKProofRequest,
    ZKProofResult,
    VaultMetadata,
    SecretData
)

__version__ = "1.0.0"
__author__ = "ReliQuary Team"
__description__ = "Python SDK for the ReliQuary enterprise cryptographic memory vault system"

# Convenience exports
__all__ = [
    "ReliQuaryClient",
    "ReliQuaryAPIClient",
    "ReliQuaryError",
    "ReliQuaryAPIError",
    "ReliQuaryAuthError",
    "ReliQuaryValidationError",
    "ReliQuaryConsensusError",
    "ReliQuaryZKError",
    "ReliQuaryVaultError",
    "ReliQuaryNetworkError",
    "ReliQuaryTimeoutError",
    "ConsensusRequest",
    "ConsensusResult",
    "ConsensusType",
    "ZKProofRequest",
    "ZKProofResult",
    "VaultMetadata",
    "SecretData"
]