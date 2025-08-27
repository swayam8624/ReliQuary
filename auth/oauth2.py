# auth/oauth2.py

from datetime import datetime, timedelta
from typing import Optional, Dict, List, Any
from fastapi import Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordBearer, HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
import config_package
from .jwt_tokens import jwt_manager, TokenData, TokenResponse, create_token_response

# OAuth 2.0 configuration
oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="auth/token",
    scopes={
        "read": "Read access to resources",
        "write": "Write access to resources", 
        "admin": "Administrative access",
        "vault:read": "Read access to vaults",
        "vault:write": "Write access to vaults",
        "vault:admin": "Administrative access to vaults",
        "audit:read": "Read access to audit logs"
    }
)

# Bearer token authentication for API keys
bearer_scheme = HTTPBearer(auto_error=False)

class User(BaseModel):
    """User model for authentication"""
    user_id: str
    username: str
    email: Optional[str] = None
    full_name: Optional[str] = None
    roles: List[str] = []
    is_active: bool = True
    created_at: Optional[datetime] = None
    last_login: Optional[datetime] = None

class OAuth2LoginRequest(BaseModel):
    """OAuth 2.0 login request"""
    username: str
    password: str
    grant_type: str = "password"
    scope: Optional[str] = "read write"
    client_id: Optional[str] = None

class OAuth2RefreshRequest(BaseModel):
    """OAuth 2.0 refresh token request"""
    refresh_token: str
    grant_type: str = "refresh_token"
    scope: Optional[str] = None

# In-memory user store (in production, this would be a database)
USERS_DB: Dict[str, Dict[str, Any]] = {
    "admin": {
        "user_id": "admin_001",
        "username": "admin",
        "email": "admin@reliquary.dev",
        "full_name": "System Administrator",
        "hashed_password": "$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW",  # secret
        "roles": ["admin", "user"],
        "permissions": ["vault:admin", "vault:read", "vault:write", "audit:read"],
        "is_active": True,
        "created_at": datetime.now(),
        "scopes": ["read", "write", "admin"]
    },
    "user1": {
        "user_id": "user_001", 
        "username": "user1",
        "email": "user1@example.com",
        "full_name": "Regular User",
        "hashed_password": "$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW",  # secret
        "roles": ["user"],
        "permissions": ["vault:read", "vault:write"],
        "is_active": True,
        "created_at": datetime.now(),
        "scopes": ["read", "write"]
    },
    "readonly": {
        "user_id": "readonly_001",
        "username": "readonly",
        "email": "readonly@example.com", 
        "full_name": "Read Only User",
        "hashed_password": "$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW",  # secret
        "roles": ["readonly"],
        "permissions": ["vault:read"],
        "is_active": True,
        "created_at": datetime.now(),
        "scopes": ["read"]
    }
}

class AuthenticationService:
    """Service for handling authentication operations"""
    
    @staticmethod
    def authenticate_user(username: str, password: str) -> Optional[Dict[str, Any]]:
        """
        Authenticate user credentials.
        
        Args:
            username: Username or email
            password: Plain text password
            
        Returns:
            User data if authentication successful, None otherwise
        """
        from .jwt_tokens import PasswordManager
        
        user = USERS_DB.get(username)
        if not user:
            return None
        
        if not user.get("is_active", False):
            return None
        
        if not PasswordManager.verify_password(password, user["hashed_password"]):
            return None
        
        # Update last login
        user["last_login"] = datetime.now()
        return user
    
    @staticmethod
    def get_user_by_id(user_id: str) -> Optional[Dict[str, Any]]:
        """Get user by user ID"""
        for user_data in USERS_DB.values():
            if user_data.get("user_id") == user_id:
                return user_data
        return None
    
    @staticmethod
    def get_user_by_username(username: str) -> Optional[Dict[str, Any]]:
        """Get user by username"""
        return USERS_DB.get(username)

class OAuth2Dependencies:
    """FastAPI dependencies for OAuth 2.0 authentication"""
    
    @staticmethod
    def get_current_user(token: str = Depends(oauth2_scheme)) -> User:
        """
        Get current authenticated user from JWT token.
        
        Args:
            token: JWT access token
            
        Returns:
            Current user object
            
        Raises:
            HTTPException: If token is invalid or user not found
        """
        credentials_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
        
        # Verify and decode token
        payload = jwt_manager.verify_token(token)
        if payload is None:
            raise credentials_exception
        
        # Extract user information
        user_id: str = payload.get("user_id")
        username: str = payload.get("username")
        if user_id is None or username is None:
            raise credentials_exception
        
        # Get user from database
        user_data = AuthenticationService.get_user_by_id(user_id)
        if user_data is None:
            raise credentials_exception
        
        return User(
            user_id=user_data["user_id"],
            username=user_data["username"],
            email=user_data.get("email"),
            full_name=user_data.get("full_name"),
            roles=user_data.get("roles", []),
            is_active=user_data.get("is_active", True),
            created_at=user_data.get("created_at"),
            last_login=user_data.get("last_login")
        )
    
    @staticmethod
    def get_current_active_user(current_user: User = Depends(get_current_user)) -> User:
        """
        Get current active user (must be active).
        
        Args:
            current_user: Current user from token
            
        Returns:
            Active user object
            
        Raises:
            HTTPException: If user is inactive
        """
        if not current_user.is_active:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Inactive user"
            )
        return current_user
    
    @staticmethod
    def verify_api_key_or_token(
        request: Request,
        bearer_token: Optional[HTTPAuthorizationCredentials] = Depends(bearer_scheme)
    ) -> Dict[str, Any]:
        """
        Verify either API key or JWT token for authentication.
        Supports both legacy API key and modern OAuth 2.0 flows.
        
        Args:
            request: FastAPI request object
            bearer_token: Bearer token from Authorization header
            
        Returns:
            Authentication context with user/client info
            
        Raises:
            HTTPException: If authentication fails
        """
        # Check for API key in X-API-Key header (legacy support)
        api_key = request.headers.get("X-API-Key")
        if api_key:
            from .oauth import get_api_client_roles, hash_api_key
            try:
                client_name = get_api_client_roles(api_key) 
                api_key_hash = hash_api_key(api_key)
                client_data = config_package.API_KEYS.get(api_key_hash, {})
                
                return {
                    "auth_type": "api_key",
                    "client_name": client_data.get("client_name", "unknown"),
                    "roles": client_data.get("roles", []),
                    "permissions": [],
                    "user_id": None,
                    "username": None
                }
            except HTTPException:
                pass
        
        # Check for Bearer token (OAuth 2.0)
        if bearer_token and bearer_token.credentials:
            payload = jwt_manager.verify_token(bearer_token.credentials)
            if payload:
                return {
                    "auth_type": "oauth2",
                    "user_id": payload.get("user_id"),
                    "username": payload.get("username"),
                    "roles": payload.get("roles", []),
                    "permissions": payload.get("permissions", []),
                    "client_id": payload.get("client_id"),
                    "scope": payload.get("scope", [])
                }
        
        # No valid authentication found
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

def create_oauth2_login(login_request: OAuth2LoginRequest) -> TokenResponse:
    """
    Authenticate user and create OAuth 2.0 token response.
    
    Args:
        login_request: Login credentials and parameters
        
    Returns:
        Token response with access and refresh tokens
        
    Raises:
        HTTPException: If authentication fails
    """
    # Authenticate user
    user_data = AuthenticationService.authenticate_user(
        login_request.username, 
        login_request.password
    )
    
    if not user_data:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Parse requested scopes
    requested_scopes = login_request.scope.split() if login_request.scope else ["read"]
    user_scopes = user_data.get("scopes", ["read"])
    
    # Only grant scopes that user has permission for
    granted_scopes = [scope for scope in requested_scopes if scope in user_scopes]
    
    if not granted_scopes:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient scope permissions"
        )
    
    # Create token response
    return create_token_response(
        user_id=user_data["user_id"],
        username=user_data["username"],
        roles=user_data.get("roles", []),
        permissions=user_data.get("permissions", []),
        client_id=login_request.client_id,
        scope=granted_scopes
    )

def refresh_oauth2_token(refresh_request: OAuth2RefreshRequest) -> TokenResponse:
    """
    Refresh OAuth 2.0 access token using refresh token.
    
    Args:
        refresh_request: Refresh token request
        
    Returns:
        New token response
        
    Raises:
        HTTPException: If refresh token is invalid
    """
    # Verify refresh token
    payload = jwt_manager.verify_token(refresh_request.refresh_token)
    
    if not payload or payload.get("type") != "refresh_token":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Get user data
    user_id = payload.get("user_id")
    user_data = AuthenticationService.get_user_by_id(user_id)
    
    if not user_data or not user_data.get("is_active"):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or inactive"
        )
    
    # Handle scope changes
    if refresh_request.scope:
        requested_scopes = refresh_request.scope.split()
        user_scopes = user_data.get("scopes", ["read"])
        granted_scopes = [scope for scope in requested_scopes if scope in user_scopes]
    else:
        granted_scopes = payload.get("scope", ["read"])
    
    # Create new token response
    return create_token_response(
        user_id=user_data["user_id"],
        username=user_data["username"],
        roles=user_data.get("roles", []),
        permissions=user_data.get("permissions", []),
        client_id=payload.get("client_id"),
        scope=granted_scopes
    )

# Convenience dependencies
get_current_user = OAuth2Dependencies.get_current_user
get_current_active_user = OAuth2Dependencies.get_current_active_user
verify_auth = OAuth2Dependencies.verify_api_key_or_token

if __name__ == "__main__":
    print("--- Testing OAuth 2.0 Authentication ---")
    
    # Test user authentication
    auth_service = AuthenticationService()
    
    user_data = auth_service.authenticate_user("admin", "secret")
    if user_data:
        print(f"✅ User authentication successful: {user_data['username']}")
        print(f"   - Roles: {user_data['roles']}")
        print(f"   - Permissions: {user_data['permissions']}")
    else:
        print("❌ User authentication failed")
    
    # Test OAuth 2.0 login
    login_request = OAuth2LoginRequest(
        username="admin",
        password="secret",
        scope="read write admin"
    )
    
    try:
        token_response = create_oauth2_login(login_request)
        print(f"✅ OAuth 2.0 login successful")
        print(f"   - Token type: {token_response.token_type}")
        print(f"   - Expires in: {token_response.expires_in} seconds") 
        print(f"   - Scope: {token_response.scope}")
        print(f"   - Access token: {token_response.access_token[:50]}...")
        
        # Test token refresh
        refresh_request = OAuth2RefreshRequest(
            refresh_token=token_response.refresh_token
        )
        
        new_token_response = refresh_oauth2_token(refresh_request)
        print(f"✅ Token refresh successful")
        print(f"   - New access token: {new_token_response.access_token[:50]}...")
        
    except Exception as e:
        print(f"❌ OAuth 2.0 test failed: {e}")
    
    print("✅ All OAuth 2.0 tests completed!")