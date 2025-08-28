"""
SDK Package for ReliQuary

This package contains the official SDKs for integrating with the ReliQuary system.
"""

# Import Python SDK components
try:
    from .python import (
        ReliQuaryClient,
        VaultAccessError,
        AuthenticationError,
        TrustValidationError
    )
    __all__ = [
        "ReliQuaryClient",
        "VaultAccessError",
        "AuthenticationError",
        "TrustValidationError"
    ]
except ImportError:
    # Python SDK not available
    __all__ = []