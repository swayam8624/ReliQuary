"""
DID (Decentralized Identifiers) Package for ReliQuary

This package contains components for DID registration, resolution, and signing.
"""

# Import DID components
from .resolver import (
    DIDResolver,
    DIDDocument,
    DIDResolutionResult
)

from .signer import (
    DIDSigner,
    DIDSignature
)

__all__ = [
    "DIDResolver",
    "DIDDocument",
    "DIDResolutionResult",
    "DIDSigner",
    "DIDSignature"
]