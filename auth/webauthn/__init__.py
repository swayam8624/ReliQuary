"""
WebAuthn Package for ReliQuary

This package contains components for WebAuthn registration and verification.
"""

# Import WebAuthn components
from .register import (
    WebAuthnRegistrationManager,
    RegistrationOptions
)

from .verify import (
    WebAuthnVerificationManager,
    AuthenticationOptions
)

__all__ = [
    "WebAuthnRegistrationManager",
    "RegistrationOptions",
    "WebAuthnVerificationManager",
    "AuthenticationOptions"
]