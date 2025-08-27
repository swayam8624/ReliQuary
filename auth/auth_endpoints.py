# auth/auth_endpoints.py

from datetime import datetime, timezone
from typing import Dict, List, Optional, Any, Union
from fastapi import APIRouter, Depends, HTTPException, status, Request, Response
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel, EmailStr, Field
import secrets

from .oauth2 import (
    OAuth2LoginRequest, OAuth2RefreshRequest, create_oauth2_login, 
    refresh_oauth2_token, get_current_user, get_current_active_user, User
)
from .identity_manager import IdentityManager, UserProfile, AccountStatus
from .webauthn.webauthn_manager import WebAuthnManager
from .did.did_manager import DIDManager
from .rbac_compatibility import require_vault_admin_hybrid, require_user_admin_hybrid
from .rbac_enhanced import EnhancedRBACManager, ResourceType, Action

# Create FastAPI router for authentication endpoints
auth_router = APIRouter(prefix="/auth", tags=["authentication"])

# Initialize managers
identity_manager = IdentityManager()
webauthn_manager = WebAuthnManager()
did_manager = DIDManager()
rbac_manager = EnhancedRBACManager()

# Request/Response Models
class UserRegistrationRequest(BaseModel):
    """User registration request"""
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    password: str = Field(..., min_length=8)
    display_name: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    organization: Optional[str] = None
    create_did: bool = True

class UserRegistrationResponse(BaseModel):
    """User registration response"""
    status: str
    message: str
    user_id: str
    username: str
    email: str
    did: Optional[str] = None
    credentials: List[Dict[str, Any]]

class WebAuthnRegistrationRequest(BaseModel):
    """WebAuthn registration initiation request"""
    username: str
    display_name: Optional[str] = None

class WebAuthnRegistrationResponse(BaseModel):
    """WebAuthn registration options response"""
    challenge: str
    rp: Dict[str, str]
    user: Dict[str, str]
    pubKeyCredParams: List[Dict[str, Any]]
    authenticatorSelection: Dict[str, Any]
    timeout: int
    attestation: str

class WebAuthnRegistrationCompleteRequest(BaseModel):
    """WebAuthn registration completion request"""
    username: str
    credential_response: Dict[str, Any]
    create_did: bool = True

class WebAuthnAuthenticationRequest(BaseModel):
    """WebAuthn authentication initiation request"""
    username: str

class WebAuthnAuthenticationCompleteRequest(BaseModel):
    """WebAuthn authentication completion request"""
    username: str
    credential_response: Dict[str, Any]

class DIDRegistrationRequest(BaseModel):
    """DID registration request"""
    username: str
    email: Optional[str] = None

class DIDResolutionRequest(BaseModel):
    """DID resolution request"""
    did: str

class TokenRefreshRequest(BaseModel):
    """Token refresh request"""
    refresh_token: str

class UserProfileUpdateRequest(BaseModel):
    """User profile update request"""
    display_name: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[EmailStr] = None
    organization: Optional[str] = None
    department: Optional[str] = None
    job_title: Optional[str] = None

class AuthenticationResponse(BaseModel):
    """Standard authentication response"""
    status: str
    message: str
    user_id: Optional[str] = None
    username: Optional[str] = None
    authentication_method: str
    session_id: Optional[str] = None
    tokens: Optional[Dict[str, Any]] = None
    profile: Optional[Dict[str, Any]] = None

# OAuth 2.0 Endpoints
@auth_router.post("/token", response_model=Dict[str, Any])
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends()
):
    """
    OAuth 2.0 token endpoint for password-based authentication.
    
    Supports:
    - Standard OAuth 2.0 password flow
    - Client credentials flow (via API keys)
    """
    try:
        login_request = OAuth2LoginRequest(
            username=form_data.username,
            password=form_data.password,
            scope=form_data.scopes[0] if form_data.scopes else "read write"
        )
        
        token_response = create_oauth2_login(login_request)
        
        return {
            "access_token": token_response.access_token,
            "refresh_token": token_response.refresh_token,
            "token_type": token_response.token_type,
            "expires_in": token_response.expires_in,
            "scope": token_response.scope
        }
        
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Authentication failed: {str(e)}"
        )

@auth_router.post("/refresh", response_model=Dict[str, Any])
async def refresh_access_token(refresh_request: TokenRefreshRequest):
    """Refresh OAuth 2.0 access token using refresh token"""
    try:
        oauth_refresh = OAuth2RefreshRequest(refresh_token=refresh_request.refresh_token)
        token_response = refresh_oauth2_token(oauth_refresh)
        
        return {
            "access_token": token_response.access_token,
            "refresh_token": token_response.refresh_token,
            "token_type": token_response.token_type,
            "expires_in": token_response.expires_in,
            "scope": token_response.scope
        }
        
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Token refresh failed: {str(e)}"
        )

# User Management Endpoints
@auth_router.post("/register", response_model=UserRegistrationResponse)
async def register_user(registration: UserRegistrationRequest):
    """Register a new user with comprehensive identity setup"""
    try:
        # Create user using identity manager
        result = identity_manager.create_user(
            username=registration.username,
            email=registration.email,
            password=registration.password,
            display_name=registration.display_name,
            first_name=registration.first_name,
            last_name=registration.last_name,
            organization=registration.organization,
            create_did=registration.create_did
        )
        
        if result["status"] != "success":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result["message"]
            )
        
        return UserRegistrationResponse(
            status=result["status"],
            message=result["message"],
            user_id=result["user_id"],
            username=result["username"],
            email=registration.email,
            did=result.get("did"),
            credentials=result.get("credentials", [])
        )
        
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"User registration failed: {str(e)}"
        )

@auth_router.get("/profile", response_model=Dict[str, Any])
async def get_user_profile(current_user: User = Depends(get_current_active_user)):
    """Get current user's profile"""
    try:
        profile = identity_manager.get_user_profile(current_user.username)
        
        if not profile:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User profile not found"
            )
        
        from dataclasses import asdict
        return {
            "status": "success",
            "profile": asdict(profile)
        }
        
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get profile: {str(e)}"
        )

@auth_router.put("/profile", response_model=Dict[str, Any])
async def update_user_profile(
    profile_update: UserProfileUpdateRequest,
    current_user: User = Depends(get_current_active_user)
):
    """Update current user's profile"""
    try:
        # This would be implemented in the identity manager
        # For now, return a placeholder response
        return {
            "status": "success",
            "message": "Profile update functionality to be implemented",
            "updated_fields": profile_update.dict(exclude_none=True)
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Profile update failed: {str(e)}"
        )

# WebAuthn Endpoints
@auth_router.post("/webauthn/register/begin", response_model=WebAuthnRegistrationResponse)
async def begin_webauthn_registration(registration: WebAuthnRegistrationRequest):
    """Begin WebAuthn registration process"""
    try:
        options = webauthn_manager.create_registration_challenge(
            username=registration.username,
            display_name=registration.display_name
        )
        
        return WebAuthnRegistrationResponse(**options)
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"WebAuthn registration initiation failed: {str(e)}"
        )

@auth_router.post("/webauthn/register/complete", response_model=Dict[str, Any])
async def complete_webauthn_registration(completion: WebAuthnRegistrationCompleteRequest):
    """Complete WebAuthn registration process"""
    try:
        result = webauthn_manager.complete_registration(
            username=completion.username,
            credential_response=completion.credential_response,
            create_did=completion.create_did
        )
        
        return result
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"WebAuthn registration completion failed: {str(e)}"
        )

@auth_router.post("/webauthn/authenticate/begin", response_model=Dict[str, Any])
async def begin_webauthn_authentication(auth_request: WebAuthnAuthenticationRequest):
    """Begin WebAuthn authentication process"""
    try:
        options = webauthn_manager.create_authentication_challenge(auth_request.username)
        
        return options
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"WebAuthn authentication initiation failed: {str(e)}"
        )

@auth_router.post("/webauthn/authenticate/complete", response_model=AuthenticationResponse)
async def complete_webauthn_authentication(completion: WebAuthnAuthenticationCompleteRequest):
    """Complete WebAuthn authentication process"""
    try:
        result = webauthn_manager.complete_authentication(
            username=completion.username,
            credential_response=completion.credential_response
        )
        
        if result["status"] != "success":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=result["message"]
            )
        
        return AuthenticationResponse(
            status=result["status"],
            message=result["message"],
            authentication_method=result["authentication_method"],
            tokens=result.get("tokens")
        )
        
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"WebAuthn authentication completion failed: {str(e)}"
        )

# DID Endpoints
@auth_router.post("/did/register", response_model=Dict[str, Any])
async def register_did(
    did_request: DIDRegistrationRequest,
    current_user: User = Depends(get_current_active_user)
):
    """Register a new DID for the authenticated user"""
    try:
        # Verify user can only register DID for themselves or has admin privileges
        if current_user.username != did_request.username:
            # Check if user has admin privileges
            granted, _ = rbac_manager.check_permission(
                principal_id=current_user.user_id,
                principal_type="user",
                resource_type=ResourceType.DID_DOCUMENT,
                action=Action.CREATE
            )
            
            if not granted:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Cannot register DID for another user"
                )
        
        from .did.did_manager import create_user_did
        did_doc, private_key = create_user_did(
            username=did_request.username,
            email=did_request.email
        )
        
        return {
            "status": "success",
            "message": "DID registered successfully",
            "did": did_doc.id,
            "did_document": did_doc.to_dict()
        }
        
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"DID registration failed: {str(e)}"
        )

@auth_router.post("/did/resolve", response_model=Dict[str, Any])
async def resolve_did(resolution: DIDResolutionRequest):
    """Resolve a DID to its DID Document"""
    try:
        from .did.resolver import resolve_did
        result = resolve_did(resolution.did)
        
        return result
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"DID resolution failed: {str(e)}"
        )

# Admin Endpoints
@auth_router.get("/admin/users", response_model=Dict[str, Any])
async def list_users(
    skip: int = 0,
    limit: int = 100,
    _: bool = Depends(require_user_admin_hybrid())
):
    """List all users (admin only)"""
    try:
        # This would be implemented in the identity manager
        return {
            "status": "success",
            "message": "User listing functionality to be implemented",
            "pagination": {"skip": skip, "limit": limit}
        }
        
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list users: {str(e)}"
        )

@auth_router.get("/admin/sessions", response_model=Dict[str, Any])
async def list_active_sessions(
    _: bool = Depends(require_user_admin_hybrid())
):
    """List all active sessions (admin only)"""
    try:
        # This would be implemented in the identity manager
        return {
            "status": "success",
            "message": "Session listing functionality to be implemented"
        }
        
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list sessions: {str(e)}"
        )

# Health and Status Endpoints
@auth_router.get("/health", response_model=Dict[str, Any])
async def auth_health_check():
    """Authentication system health check"""
    try:
        # Check various components
        health_status = {
            "status": "healthy",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "components": {
                "identity_manager": "healthy",
                "webauthn_manager": "healthy", 
                "did_manager": "healthy",
                "rbac_manager": "healthy"
            }
        }
        
        # Test basic functionality
        try:
            # Test identity manager
            test_profile = identity_manager.get_user_profile("nonexistent_user")
            health_status["components"]["identity_manager"] = "healthy"
        except Exception:
            health_status["components"]["identity_manager"] = "degraded"
        
        # Test WebAuthn manager
        try:
            webauthn_manager.create_registration_challenge("test_user")
            health_status["components"]["webauthn_manager"] = "healthy"
        except Exception:
            health_status["components"]["webauthn_manager"] = "degraded"
        
        # Check if any components are degraded
        if any(status == "degraded" for status in health_status["components"].values()):
            health_status["status"] = "degraded"
        
        return health_status
        
    except Exception as e:
        return {
            "status": "unhealthy",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "error": str(e)
        }

@auth_router.get("/info", response_model=Dict[str, Any])
async def auth_system_info():
    """Get authentication system information"""
    return {
        "name": "ReliQuary Authentication System",
        "version": "2.0.0",
        "features": [
            "OAuth 2.0 with JWT tokens",
            "WebAuthn biometric authentication",
            "W3C Decentralized Identifiers (DID)",
            "Enhanced Role-Based Access Control (RBAC)",
            "Comprehensive identity management",
            "Session management",
            "Audit logging"
        ],
        "supported_flows": [
            "OAuth 2.0 Password Grant",
            "OAuth 2.0 Client Credentials",
            "OAuth 2.0 Refresh Token",
            "WebAuthn Registration",
            "WebAuthn Authentication",
            "DID Registration",
            "DID Resolution"
        ],
        "endpoints": {
            "token": "/auth/token",
            "refresh": "/auth/refresh",
            "register": "/auth/register",
            "profile": "/auth/profile",
            "webauthn": "/auth/webauthn/*",
            "did": "/auth/did/*",
            "admin": "/auth/admin/*"
        }
    }

# Include the router in your main FastAPI app with:
# app.include_router(auth_router)