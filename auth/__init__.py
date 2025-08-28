"""
Authentication Package for ReliQuary

This package contains all components related to authentication and authorization,
including OAuth, DID, WebAuthn, and RBAC systems.
"""

# Import OAuth components
from .oauth import (
    OAuthManager,
    TokenManager,
    ClientCredentials,
    JWTToken,
    OAuthError
)

# Import DID components
from .did.resolver import (
    DIDResolver,
    DIDDocument,
    DIDResolutionResult
)

from .did.signer import (
    DIDSigner,
    DIDSignature
)

# Import WebAuthn components
from .webauthn.register import (
    WebAuthnRegistrationManager,
    RegistrationOptions
)

from .webauthn.verify import (
    WebAuthnVerificationManager,
    AuthenticationOptions
)

# Import RBAC components
from .rbac import (
    RBACManager,
    Role,
    Permission,
    Policy,
    AccessControlError
)

__all__ = [
    # OAuth components
    "OAuthManager",
    "TokenManager",
    "ClientCredentials",
    "JWTToken",
    "OAuthError",
    
    # DID components
    "DIDResolver",
    "DIDDocument",
    "DIDResolutionResult",
    "DIDSigner",
    "DIDSignature",
    
    # WebAuthn components
    "WebAuthnRegistrationManager",
    "RegistrationOptions",
    "WebAuthnVerificationManager",
    "AuthenticationOptions",
    
    # RBAC components
    "RBACManager",
    "Role",
    "Permission",
    "Policy",
    "AccessControlError"
]