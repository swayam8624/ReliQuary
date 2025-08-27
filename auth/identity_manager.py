# auth/identity_manager.py

import json
import sqlite3
import hashlib
import secrets
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, asdict
from enum import Enum
import os

from .oauth2 import create_token_response
from .jwt_tokens import PasswordManager
from .webauthn.webauthn_manager import WebAuthnManager
from .did.did_manager import DIDManager, create_user_did

class IdentityProviderType(Enum):
    """Types of identity providers supported"""
    LOCAL = "local"
    OAUTH2_PASSWORD = "oauth2_password"
    WEBAUTHN = "webauthn"
    DID = "did"
    API_KEY = "api_key"

class AccountStatus(Enum):
    """Account status options"""
    ACTIVE = "active"
    SUSPENDED = "suspended"
    PENDING_VERIFICATION = "pending_verification"
    DEACTIVATED = "deactivated"

@dataclass
class UserProfile:
    """Comprehensive user profile"""
    user_id: str
    username: str
    email: Optional[str] = None
    display_name: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    phone_number: Optional[str] = None
    organization: Optional[str] = None
    department: Optional[str] = None
    job_title: Optional[str] = None
    profile_picture_url: Optional[str] = None
    timezone: Optional[str] = None
    language: str = "en"
    two_factor_enabled: bool = False
    account_status: AccountStatus = AccountStatus.ACTIVE
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
    last_login: Optional[str] = None
    failed_login_attempts: int = 0
    password_expires_at: Optional[str] = None
    must_change_password: bool = False
    metadata: Dict[str, Any] = None

    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}
        if self.created_at is None:
            self.created_at = datetime.now(timezone.utc).isoformat()
        if self.updated_at is None:
            self.updated_at = self.created_at

@dataclass
class IdentityCredential:
    """Identity credential information"""
    credential_id: str
    user_id: str
    provider_type: IdentityProviderType
    provider_id: str  # The ID within the provider (e.g., DID, credential ID)
    credential_data: Dict[str, Any]  # Provider-specific data
    is_primary: bool = False
    is_verified: bool = True
    created_at: Optional[str] = None
    last_used: Optional[str] = None
    expires_at: Optional[str] = None
    metadata: Dict[str, Any] = None

    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}
        if self.created_at is None:
            self.created_at = datetime.now(timezone.utc).isoformat()

@dataclass
class IdentitySession:
    """Active identity session"""
    session_id: str
    user_id: str
    username: str
    authentication_method: IdentityProviderType
    created_at: str
    expires_at: str
    last_activity: str
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    metadata: Dict[str, Any] = None

class IdentityManager:
    """
    Comprehensive identity management system that integrates all authentication methods:
    - OAuth 2.0 password authentication
    - WebAuthn biometric authentication
    - DID-based authentication
    - API key authentication
    - User profile management
    - Credential management
    - Session management
    """
    
    def __init__(self, db_path: Optional[str] = None):
        if db_path is None:
            script_dir = os.path.dirname(os.path.realpath(__file__))
            self.db_path = os.path.join(script_dir, "identity.db")
        else:
            self.db_path = db_path
        
        self._init_database()
        
        # Initialize component managers
        self.webauthn_manager = WebAuthnManager()
        self.did_manager = DIDManager()
    
    def _init_database(self):
        """Initialize identity management database"""
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # User profiles table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS user_profiles (
                    user_id TEXT PRIMARY KEY,
                    username TEXT UNIQUE NOT NULL,
                    email TEXT UNIQUE,
                    display_name TEXT,
                    first_name TEXT,
                    last_name TEXT,
                    phone_number TEXT,
                    organization TEXT,
                    department TEXT,
                    job_title TEXT,
                    profile_picture_url TEXT,
                    timezone TEXT,
                    language TEXT DEFAULT 'en',
                    two_factor_enabled BOOLEAN DEFAULT FALSE,
                    account_status TEXT DEFAULT 'active',
                    created_at TIMESTAMP NOT NULL,
                    updated_at TIMESTAMP NOT NULL,
                    last_login TIMESTAMP,
                    failed_login_attempts INTEGER DEFAULT 0,
                    password_expires_at TIMESTAMP,
                    must_change_password BOOLEAN DEFAULT FALSE,
                    metadata TEXT
                )
            ''')
            
            # Identity credentials table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS identity_credentials (
                    credential_id TEXT PRIMARY KEY,
                    user_id TEXT NOT NULL,
                    provider_type TEXT NOT NULL,
                    provider_id TEXT NOT NULL,
                    credential_data TEXT NOT NULL,
                    is_primary BOOLEAN DEFAULT FALSE,
                    is_verified BOOLEAN DEFAULT TRUE,
                    created_at TIMESTAMP NOT NULL,
                    last_used TIMESTAMP,
                    expires_at TIMESTAMP,
                    metadata TEXT,
                    FOREIGN KEY (user_id) REFERENCES user_profiles (user_id),
                    UNIQUE(user_id, provider_type, provider_id)
                )
            ''')
            
            # Active sessions table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS identity_sessions (
                    session_id TEXT PRIMARY KEY,
                    user_id TEXT NOT NULL,
                    username TEXT NOT NULL,
                    authentication_method TEXT NOT NULL,
                    created_at TIMESTAMP NOT NULL,
                    expires_at TIMESTAMP NOT NULL,
                    last_activity TIMESTAMP NOT NULL,
                    ip_address TEXT,
                    user_agent TEXT,
                    metadata TEXT,
                    FOREIGN KEY (user_id) REFERENCES user_profiles (user_id)
                )
            ''')
            
            # Password credentials table (for OAuth2 password flow)
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS password_credentials (
                    user_id TEXT PRIMARY KEY,
                    password_hash TEXT NOT NULL,
                    salt TEXT NOT NULL,
                    created_at TIMESTAMP NOT NULL,
                    updated_at TIMESTAMP NOT NULL,
                    FOREIGN KEY (user_id) REFERENCES user_profiles (user_id)
                )
            ''')
            
            conn.commit()
    
    def create_user(
        self, 
        username: str,
        email: Optional[str] = None,
        password: Optional[str] = None,
        display_name: Optional[str] = None,
        create_did: bool = True,
        **profile_data
    ) -> Dict[str, Any]:
        """
        Create a new user with comprehensive identity setup.
        
        Args:
            username: Unique username
            email: User email address
            password: Password for OAuth2 authentication (optional)
            display_name: Human-readable display name
            create_did: Whether to create a DID for the user
            **profile_data: Additional profile data
            
        Returns:
            User creation result with credentials
        """
        try:
            user_id = f"usr_{secrets.token_hex(16)}"
            
            # Create user profile
            profile = UserProfile(
                user_id=user_id,
                username=username,
                email=email,
                display_name=display_name or username,
                **profile_data
            )
            
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Check if username or email already exists
                cursor.execute('''
                    SELECT user_id FROM user_profiles 
                    WHERE username = ? OR (email IS NOT NULL AND email = ?)
                ''', (username, email))
                
                if cursor.fetchone():
                    return {
                        "status": "error",
                        "message": "Username or email already exists"
                    }
                
                # Insert user profile
                cursor.execute('''
                    INSERT INTO user_profiles (
                        user_id, username, email, display_name, first_name, last_name,
                        phone_number, organization, department, job_title,
                        profile_picture_url, timezone, language, two_factor_enabled,
                        account_status, created_at, updated_at, last_login,
                        failed_login_attempts, password_expires_at, must_change_password, metadata
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    profile.user_id, profile.username, profile.email, profile.display_name,
                    profile.first_name, profile.last_name, profile.phone_number,
                    profile.organization, profile.department, profile.job_title,
                    profile.profile_picture_url, profile.timezone, profile.language,
                    profile.two_factor_enabled, profile.account_status.value,
                    profile.created_at, profile.updated_at, profile.last_login,
                    profile.failed_login_attempts, profile.password_expires_at,
                    profile.must_change_password, json.dumps(profile.metadata)
                ))
                
                # Create password credential if provided
                if password:
                    password_hash, salt = self._hash_password(password)
                    
                    cursor.execute('''
                        INSERT INTO password_credentials (
                            user_id, password_hash, salt, created_at, updated_at
                        ) VALUES (?, ?, ?, ?, ?)
                    ''', (
                        user_id, password_hash, salt,
                        datetime.now(timezone.utc).isoformat(),
                        datetime.now(timezone.utc).isoformat()
                    ))
                    
                    # Add password credential record
                    self._add_credential_record(
                        cursor, user_id, IdentityProviderType.OAUTH2_PASSWORD,
                        username, {"method": "bcrypt"}, is_primary=True
                    )
                
                conn.commit()
            
            result = {
                "status": "success",
                "message": "User created successfully",
                "user_id": user_id,
                "username": username,
                "profile": asdict(profile),
                "credentials": []
            }
            
            # Create DID if requested
            if create_did:
                try:
                    did_doc, private_key = create_user_did(username, email)
                    
                    # Add DID credential record
                    with sqlite3.connect(self.db_path) as conn:
                        cursor = conn.cursor()
                        self._add_credential_record(
                            cursor, user_id, IdentityProviderType.DID,
                            did_doc.id, {"document": did_doc.to_dict()}, is_primary=False
                        )
                        conn.commit()
                    
                    result["did"] = did_doc.id
                    result["did_document"] = did_doc.to_dict()
                    result["credentials"].append({
                        "type": "did",
                        "id": did_doc.id
                    })
                    
                except Exception as e:
                    result["did_warning"] = f"Failed to create DID: {e}"
            
            if password:
                result["credentials"].append({
                    "type": "password",
                    "method": "oauth2_password"
                })
            
            return result
            
        except Exception as e:
            return {
                "status": "error",
                "message": f"User creation failed: {e}"
            }
    
    def authenticate_user(
        self, 
        username: str, 
        password: Optional[str] = None,
        webauthn_response: Optional[Dict[str, Any]] = None,
        api_key: Optional[str] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Authenticate a user using various methods.
        
        Args:
            username: Username
            password: Password for OAuth2 authentication
            webauthn_response: WebAuthn authentication response
            api_key: API key for API authentication
            ip_address: Client IP address
            user_agent: Client user agent
            
        Returns:
            Authentication result with tokens and session
        """
        try:
            # Get user profile
            profile = self.get_user_profile(username)
            if not profile or profile.account_status != AccountStatus.ACTIVE:
                return {
                    "status": "error",
                    "message": "User not found or account not active"
                }
            
            auth_result = None
            auth_method = None
            
            # Try password authentication
            if password:
                auth_result = self._authenticate_password(username, password)
                auth_method = IdentityProviderType.OAUTH2_PASSWORD
            
            # Try WebAuthn authentication
            elif webauthn_response:
                auth_result = self.webauthn_manager.complete_authentication(
                    username, webauthn_response
                )
                auth_method = IdentityProviderType.WEBAUTHN
            
            # Try API key authentication
            elif api_key:
                # This would integrate with existing API key system
                auth_result = {"status": "error", "message": "API key auth not implemented in this method"}
                auth_method = IdentityProviderType.API_KEY
            
            else:
                return {
                    "status": "error",
                    "message": "No valid authentication method provided"
                }
            
            if auth_result.get("status") != "success":
                self._record_failed_login(username)
                return auth_result
            
            # Create session
            session = self._create_session(
                profile.user_id, username, auth_method,
                ip_address, user_agent
            )
            
            # Update last login
            self._update_last_login(username)
            
            # Create or use existing token response
            if auth_result.get("tokens"):
                tokens = auth_result["tokens"]
            else:
                token_response = create_token_response(
                    user_id=profile.user_id,
                    username=username,
                    roles=["user"],
                    permissions=["vault:read", "vault:write"],
                    scope=["read", "write"]
                )
                tokens = {
                    "access_token": token_response.access_token,
                    "refresh_token": token_response.refresh_token,
                    "token_type": token_response.token_type,
                    "expires_in": token_response.expires_in
                }
            
            return {
                "status": "success",
                "message": "Authentication successful",
                "user_id": profile.user_id,
                "username": username,
                "authentication_method": auth_method.value,
                "session_id": session.session_id,
                "tokens": tokens,
                "profile": asdict(profile)
            }
            
        except Exception as e:
            return {
                "status": "error",
                "message": f"Authentication failed: {e}"
            }
    
    def _authenticate_password(self, username: str, password: str) -> Dict[str, Any]:
        """Authenticate using password"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Get user and password hash
                cursor.execute('''
                    SELECT up.user_id, pc.password_hash, pc.salt
                    FROM user_profiles up
                    JOIN password_credentials pc ON up.user_id = pc.user_id
                    WHERE up.username = ?
                ''', (username,))
                
                result = cursor.fetchone()
                if not result:
                    return {
                        "status": "error",
                        "message": "Invalid username or password"
                    }
                
                user_id, password_hash, salt = result
                
                # Verify password
                if self._verify_password(password, password_hash, salt):
                    return {"status": "success"}
                else:
                    return {
                        "status": "error", 
                        "message": "Invalid username or password"
                    }
                    
        except Exception as e:
            return {
                "status": "error",
                "message": f"Password authentication failed: {e}"
            }
    
    def get_user_profile(self, username: str) -> Optional[UserProfile]:
        """Get user profile by username"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT * FROM user_profiles WHERE username = ?
                ''', (username,))
                
                result = cursor.fetchone()
                if not result:
                    return None
                
                return UserProfile(
                    user_id=result[0],
                    username=result[1],
                    email=result[2],
                    display_name=result[3],
                    first_name=result[4],
                    last_name=result[5],
                    phone_number=result[6],
                    organization=result[7],
                    department=result[8],
                    job_title=result[9],
                    profile_picture_url=result[10],
                    timezone=result[11],
                    language=result[12],
                    two_factor_enabled=bool(result[13]),
                    account_status=AccountStatus(result[14]),
                    created_at=result[15],
                    updated_at=result[16],
                    last_login=result[17],
                    failed_login_attempts=result[18],
                    password_expires_at=result[19],
                    must_change_password=bool(result[20]),
                    metadata=json.loads(result[21]) if result[21] else {}
                )
                
        except Exception as e:
            print(f"Error getting user profile: {e}")
            return None
    
    def _hash_password(self, password: str) -> tuple[str, str]:
        """Hash password with salt"""
        # Use PasswordManager for consistent hashing
        password_hash = PasswordManager.hash_password(password)
        salt = ""  # PasswordManager handles salting internally
        return password_hash, salt
    
    def _verify_password(self, password: str, password_hash: str, salt: str) -> bool:
        """Verify password against hash"""
        try:
            # PasswordManager handles salt internally, so we don't need the salt parameter
            return PasswordManager.verify_password(password, password_hash)
        except Exception:
            return False
    
    def _add_credential_record(
        self, cursor, user_id: str, provider_type: IdentityProviderType,
        provider_id: str, credential_data: Dict[str, Any], is_primary: bool = False
    ):
        """Add credential record to database"""
        credential_id = f"cred_{secrets.token_hex(16)}"
        
        cursor.execute('''
            INSERT INTO identity_credentials (
                credential_id, user_id, provider_type, provider_id,
                credential_data, is_primary, is_verified, created_at, metadata
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            credential_id, user_id, provider_type.value, provider_id,
            json.dumps(credential_data), is_primary, True,
            datetime.now(timezone.utc).isoformat(), "{}"
        ))
    
    def _create_session(
        self, user_id: str, username: str, auth_method: IdentityProviderType,
        ip_address: Optional[str] = None, user_agent: Optional[str] = None
    ) -> IdentitySession:
        """Create a new identity session"""
        session_id = f"sess_{secrets.token_hex(32)}"
        now = datetime.now(timezone.utc)
        expires_at = now + timedelta(hours=24)  # 24 hour session
        
        session = IdentitySession(
            session_id=session_id,
            user_id=user_id,
            username=username,
            authentication_method=auth_method,
            created_at=now.isoformat(),
            expires_at=expires_at.isoformat(),
            last_activity=now.isoformat(),
            ip_address=ip_address,
            user_agent=user_agent,
            metadata={}
        )
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO identity_sessions (
                    session_id, user_id, username, authentication_method,
                    created_at, expires_at, last_activity, ip_address, user_agent, metadata
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                session.session_id, session.user_id, session.username,
                session.authentication_method.value, session.created_at,
                session.expires_at, session.last_activity, session.ip_address,
                session.user_agent, json.dumps(session.metadata)
            ))
            conn.commit()
        
        return session
    
    def _update_last_login(self, username: str):
        """Update user's last login timestamp"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                UPDATE user_profiles 
                SET last_login = ?, failed_login_attempts = 0
                WHERE username = ?
            ''', (datetime.now(timezone.utc).isoformat(), username))
            conn.commit()
    
    def _record_failed_login(self, username: str):
        """Record failed login attempt"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                UPDATE user_profiles 
                SET failed_login_attempts = failed_login_attempts + 1
                WHERE username = ?
            ''', (username,))
            conn.commit()

if __name__ == "__main__":
    print("--- Testing Identity Manager ---")
    
    manager = IdentityManager()
    
    # Test user creation
    username = "alice_identity"
    email = "alice@example.com"
    password = "SecurePassword123!"
    
    print(f"\n1. Creating user: {username}")
    create_result = manager.create_user(
        username=username,
        email=email,
        password=password,
        display_name="Alice Identity",
        first_name="Alice",
        last_name="Smith",
        organization="ReliQuary Corp",
        create_did=True
    )
    
    print(f"✅ User creation: {create_result['status']}")
    if create_result.get('did'):
        print(f"   - DID: {create_result['did']}")
    print(f"   - Credentials: {len(create_result.get('credentials', []))}")
    
    # Test authentication
    print(f"\n2. Authenticating user with password")
    auth_result = manager.authenticate_user(
        username=username,
        password=password,
        ip_address="192.168.1.100",
        user_agent="ReliQuary-Test/1.0"
    )
    
    print(f"✅ Authentication: {auth_result['status']}")
    if auth_result.get('tokens'):
        print(f"   - Access token: {auth_result['tokens']['access_token'][:30]}...")
        print(f"   - Session ID: {auth_result.get('session_id', 'N/A')}")
    
    # Test profile retrieval
    print(f"\n3. Getting user profile")
    profile = manager.get_user_profile(username)
    if profile:
        print(f"✅ Profile retrieved: {profile.display_name}")
        print(f"   - User ID: {profile.user_id}")
        print(f"   - Email: {profile.email}")
        print(f"   - Status: {profile.account_status.value}")
    
    print("\n✅ Identity manager tests completed!")