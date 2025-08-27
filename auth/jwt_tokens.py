# auth/jwt_tokens.py

import secrets
from datetime import datetime, timedelta, timezone
from typing import Dict, Optional, List, Any
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel
import config_package

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT Configuration
JWT_SECRET_KEY = getattr(config_package, 'JWT_SECRET_KEY', secrets.token_urlsafe(32))
JWT_ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_DAYS = 7

class TokenData(BaseModel):
    """Token payload data structure"""
    username: Optional[str] = None
    user_id: Optional[str] = None
    roles: List[str] = []
    permissions: List[str] = []
    client_id: Optional[str] = None
    scope: List[str] = []
    token_type: str = "bearer"

class TokenResponse(BaseModel):
    """OAuth 2.0 token response"""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int
    scope: str
    user_id: Optional[str] = None

class JWTManager:
    """JWT token management for OAuth 2.0 flows"""
    
    def __init__(self, secret_key: str = JWT_SECRET_KEY, algorithm: str = JWT_ALGORITHM):
        self.secret_key = secret_key
        self.algorithm = algorithm
    
    def create_access_token(
        self, 
        data: Dict[str, Any], 
        expires_delta: Optional[timedelta] = None
    ) -> str:
        """
        Create a JWT access token with expiration.
        
        Args:
            data: Payload data to include in token
            expires_delta: Custom expiration time
            
        Returns:
            Encoded JWT token string
        """
        to_encode = data.copy()
        
        if expires_delta:
            expire = datetime.now(timezone.utc) + expires_delta
        else:
            expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        
        to_encode.update({
            "exp": expire,
            "iat": datetime.now(timezone.utc),
            "type": "access_token"
        })
        
        encoded_jwt = jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
        return encoded_jwt
    
    def create_refresh_token(
        self, 
        data: Dict[str, Any], 
        expires_delta: Optional[timedelta] = None
    ) -> str:
        """
        Create a JWT refresh token with longer expiration.
        
        Args:
            data: Payload data to include in token
            expires_delta: Custom expiration time
            
        Returns:
            Encoded JWT token string
        """
        to_encode = data.copy()
        
        if expires_delta:
            expire = datetime.now(timezone.utc) + expires_delta
        else:
            expire = datetime.now(timezone.utc) + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
        
        to_encode.update({
            "exp": expire,
            "iat": datetime.now(timezone.utc),
            "type": "refresh_token"
        })
        
        encoded_jwt = jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
        return encoded_jwt
    
    def verify_token(self, token: str) -> Optional[Dict[str, Any]]:
        """
        Verify and decode a JWT token.
        
        Args:
            token: JWT token string
            
        Returns:
            Decoded token payload or None if invalid
        """
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            
            # Check expiration
            exp = payload.get("exp")
            if exp and datetime.fromtimestamp(exp, tz=timezone.utc) < datetime.now(timezone.utc):
                return None
                
            return payload
        except JWTError:
            return None
    
    def refresh_access_token(self, refresh_token: str) -> Optional[str]:
        """
        Generate a new access token from a valid refresh token.
        
        Args:
            refresh_token: Valid refresh token
            
        Returns:
            New access token or None if refresh token is invalid
        """
        payload = self.verify_token(refresh_token)
        
        if not payload or payload.get("type") != "refresh_token":
            return None
        
        # Create new access token with same user data
        access_data = {
            "sub": payload.get("sub"),
            "username": payload.get("username"),
            "user_id": payload.get("user_id"),
            "roles": payload.get("roles", []),
            "permissions": payload.get("permissions", []),
            "client_id": payload.get("client_id"),
            "scope": payload.get("scope", [])
        }
        
        return self.create_access_token(access_data)

class PasswordManager:
    """Password hashing and verification utilities"""
    
    @staticmethod
    def hash_password(password: str) -> str:
        """Hash a password using bcrypt"""
        return pwd_context.hash(password)
    
    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """Verify a password against its hash"""
        return pwd_context.verify(plain_password, hashed_password)
    
    @staticmethod
    def generate_secure_password(length: int = 16) -> str:
        """Generate a cryptographically secure password"""
        return secrets.token_urlsafe(length)

# Global JWT manager instance
jwt_manager = JWTManager()

def create_token_response(
    user_id: str,
    username: str,
    roles: List[str],
    permissions: List[str],
    client_id: Optional[str] = None,
    scope: List[str] = None
) -> TokenResponse:
    """
    Create a complete OAuth 2.0 token response.
    
    Args:
        user_id: Unique user identifier
        username: Username or email
        roles: User roles
        permissions: User permissions
        client_id: OAuth client ID
        scope: Requested scopes
        
    Returns:
        Complete token response with access and refresh tokens
    """
    if scope is None:
        scope = ["read", "write"]
    
    token_data = {
        "sub": user_id,
        "username": username,
        "user_id": user_id,
        "roles": roles,
        "permissions": permissions,
        "client_id": client_id,
        "scope": scope
    }
    
    access_token = jwt_manager.create_access_token(token_data)
    refresh_token = jwt_manager.create_refresh_token(token_data)
    
    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        expires_in=ACCESS_TOKEN_EXPIRE_MINUTES * 60,  # Convert to seconds
        scope=" ".join(scope),
        user_id=user_id
    )

if __name__ == "__main__":
    print("--- Testing JWT Token Management ---")
    
    # Test password hashing
    password = "test_password_123"
    hashed = PasswordManager.hash_password(password)
    print(f"✅ Password hashed: {hashed[:50]}...")
    print(f"✅ Password verification: {PasswordManager.verify_password(password, hashed)}")
    
    # Test JWT token creation
    test_data = {
        "sub": "user123",
        "username": "test_user",
        "roles": ["user", "admin"],
        "permissions": ["vault:read", "vault:write"]
    }
    
    access_token = jwt_manager.create_access_token(test_data)
    refresh_token = jwt_manager.create_refresh_token(test_data)
    
    print(f"✅ Access token created: {access_token[:50]}...")
    print(f"✅ Refresh token created: {refresh_token[:50]}...")
    
    # Test token verification
    decoded = jwt_manager.verify_token(access_token)
    print(f"✅ Token verification: {decoded is not None}")
    if decoded:
        print(f"   - User: {decoded.get('username')}")
        print(f"   - Roles: {decoded.get('roles')}")
        print(f"   - Expires: {datetime.fromtimestamp(decoded.get('exp'), tz=timezone.utc)}")
    
    # Test token response creation
    token_response = create_token_response(
        user_id="user123",
        username="test_user",
        roles=["user"],
        permissions=["vault:read"],
        scope=["read", "write"]
    )
    print(f"✅ Token response created: {token_response.token_type} token")
    print(f"   - Expires in: {token_response.expires_in} seconds")
    print(f"   - Scope: {token_response.scope}")
    
    print("✅ All JWT tests passed!")