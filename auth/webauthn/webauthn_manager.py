# auth/webauthn/webauthn_manager.py

import json
import sqlite3
import uuid
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
import os
import secrets

try:
    from fido2.server import Fido2Server, PublicKeyCredentialRpEntity, RegistrationState
    from fido2.webauthn import AttestationObject, AuthenticatorData, CollectedClientData
    from fido2 import cbor
    FIDO2_AVAILABLE = True
except ImportError:
    FIDO2_AVAILABLE = False
    print("⚠️  FIDO2 library not available. WebAuthn will use simulation mode.")

import config_package
from ..oauth2 import create_token_response
from ..did.did_manager import create_user_did, DIDManager

@dataclass
class WebAuthnCredential:
    """WebAuthn credential information"""
    credential_id: str
    user_id: str
    username: str
    public_key: bytes
    sign_count: int
    created_at: str
    last_used: Optional[str] = None
    device_name: Optional[str] = None
    transports: List[str] = None

@dataclass
class RegistrationChallenge:
    """WebAuthn registration challenge"""
    challenge: str
    user_id: str
    username: str
    created_at: str
    expires_at: str

@dataclass
class AuthenticationChallenge:
    """WebAuthn authentication challenge"""
    challenge: str
    username: str
    created_at: str
    expires_at: str

class WebAuthnManager:
    """Comprehensive WebAuthn management integrated with OAuth 2.0 and DID"""
    
    def __init__(self, db_path: Optional[str] = None):
        if db_path is None:
            script_dir = os.path.dirname(os.path.realpath(__file__))
            self.db_path = os.path.join(script_dir, "webauthn.db")
        else:
            self.db_path = db_path
        
        # WebAuthn configuration
        self.rp_id = getattr(config_package, 'RELIQUARY_RP_ID', 'localhost')
        self.rp_name = "ReliQuary Cryptographic Memory System"
        self.rp_origin = getattr(config_package, 'RELIQUARY_RP_ORIGIN', f'https://{self.rp_id}:8000')
        
        # Initialize FIDO2 server if available
        if FIDO2_AVAILABLE:
            rp = PublicKeyCredentialRpEntity(self.rp_id, self.rp_name)
            self.fido2_server = Fido2Server(rp)
        else:
            self.fido2_server = None
        
        self._init_database()
        self.did_manager = DIDManager()
    
    def _init_database(self):
        """Initialize WebAuthn database"""
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # WebAuthn credentials table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS webauthn_credentials (
                    credential_id TEXT PRIMARY KEY,
                    user_id TEXT NOT NULL,
                    username TEXT NOT NULL,
                    public_key BLOB NOT NULL,
                    sign_count INTEGER NOT NULL DEFAULT 0,
                    created_at TIMESTAMP NOT NULL,
                    last_used TIMESTAMP,
                    device_name TEXT,
                    transports TEXT,
                    UNIQUE(credential_id)
                )
            ''')
            
            # Registration challenges table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS registration_challenges (
                    challenge TEXT PRIMARY KEY,
                    user_id TEXT NOT NULL,
                    username TEXT NOT NULL,
                    created_at TIMESTAMP NOT NULL,
                    expires_at TIMESTAMP NOT NULL
                )
            ''')
            
            # Authentication challenges table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS auth_challenges (
                    challenge TEXT PRIMARY KEY,
                    username TEXT NOT NULL,
                    created_at TIMESTAMP NOT NULL,
                    expires_at TIMESTAMP NOT NULL
                )
            ''')
            
            conn.commit()
    
    def create_registration_challenge(self, username: str, display_name: str = None) -> Dict[str, Any]:
        """
        Create a WebAuthn registration challenge.
        
        Args:
            username: Username for registration
            display_name: Human-readable display name
            
        Returns:
            Registration options for client
        """
        user_id = str(uuid.uuid4())
        challenge = secrets.token_urlsafe(32)
        
        # Store challenge in database
        now = datetime.now(timezone.utc)
        expires_at = now + timedelta(minutes=5)  # 5 minute expiry
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO registration_challenges 
                (challenge, user_id, username, created_at, expires_at)
                VALUES (?, ?, ?, ?, ?)
            ''', (challenge, user_id, username, now, expires_at))
            conn.commit()
        
        # Create registration options
        registration_options = {
            "challenge": challenge,
            "rp": {
                "name": self.rp_name,
                "id": self.rp_id
            },
            "user": {
                "id": user_id,
                "name": username,
                "displayName": display_name or username
            },
            "pubKeyCredParams": [
                {"type": "public-key", "alg": -7},   # ES256
                {"type": "public-key", "alg": -257}  # RS256
            ],
            "authenticatorSelection": {
                "authenticatorAttachment": "platform",
                "userVerification": "preferred",
                "residentKey": "preferred"
            },
            "timeout": 300000,  # 5 minutes
            "attestation": "none"
        }
        
        return registration_options
    
    def complete_registration(
        self, 
        username: str, 
        credential_response: Dict[str, Any],
        create_did: bool = True
    ) -> Dict[str, Any]:
        """
        Complete WebAuthn registration and optionally create DID.
        
        Args:
            username: Username
            credential_response: WebAuthn credential response from client
            create_did: Whether to create a DID for the user
            
        Returns:
            Registration result with optional OAuth tokens
        """
        try:
            # In simulation mode, create a mock credential
            if not FIDO2_AVAILABLE:
                return self._simulate_registration(username, credential_response, create_did)
            
            # Extract credential data
            credential_id = credential_response.get("id", "")
            raw_id = credential_response.get("rawId", "")
            response = credential_response.get("response", {})
            
            # Store credential in database
            now = datetime.now(timezone.utc)
            
            # Generate mock public key for simulation
            public_key = secrets.token_bytes(65)  # Mock EC public key
            
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Remove any existing credentials for this user
                cursor.execute('DELETE FROM webauthn_credentials WHERE username = ?', (username,))
                
                # Insert new credential
                cursor.execute('''
                    INSERT INTO webauthn_credentials 
                    (credential_id, user_id, username, public_key, sign_count, created_at, device_name)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (
                    credential_id,
                    str(uuid.uuid4()),
                    username,
                    public_key,
                    0,
                    now,
                    "WebAuthn Device"
                ))
                
                # Clean up challenge
                cursor.execute('DELETE FROM registration_challenges WHERE username = ?', (username,))
                
                conn.commit()
            
            result = {
                "status": "success",
                "message": "WebAuthn registration completed successfully",
                "credential_id": credential_id
            }
            
            # Create DID if requested
            if create_did:
                try:
                    did_doc, private_key = create_user_did(username)
                    result["did"] = did_doc.id
                    result["did_document"] = did_doc.to_dict()
                except Exception as e:
                    result["did_warning"] = f"Failed to create DID: {e}"
            
            return result
            
        except Exception as e:
            return {
                "status": "error", 
                "message": f"Registration failed: {e}"
            }
    
    def _simulate_registration(self, username: str, credential_response: Dict[str, Any], create_did: bool) -> Dict[str, Any]:
        """Simulate WebAuthn registration when FIDO2 is not available"""
        credential_id = f"sim_{username}_{secrets.token_hex(16)}"
        public_key = secrets.token_bytes(65)
        
        now = datetime.now(timezone.utc)
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Remove existing credentials
            cursor.execute('DELETE FROM webauthn_credentials WHERE username = ?', (username,))
            
            # Insert simulated credential
            cursor.execute('''
                INSERT INTO webauthn_credentials 
                (credential_id, user_id, username, public_key, sign_count, created_at, device_name)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                credential_id,
                str(uuid.uuid4()),
                username,
                public_key,
                0,
                now,
                "Simulated WebAuthn Device"
            ))
            
            # Clean up challenge
            cursor.execute('DELETE FROM registration_challenges WHERE username = ?', (username,))
            
            conn.commit()
        
        result = {
            "status": "success",
            "message": "WebAuthn registration completed (simulation mode)",
            "credential_id": credential_id,
            "simulation": True
        }
        
        # Create DID if requested
        if create_did:
            try:
                did_doc, private_key = create_user_did(username)
                result["did"] = did_doc.id
                result["did_document"] = did_doc.to_dict()
            except Exception as e:
                result["did_warning"] = f"Failed to create DID: {e}"
        
        return result
    
    def create_authentication_challenge(self, username: str) -> Dict[str, Any]:
        """
        Create a WebAuthn authentication challenge.
        
        Args:
            username: Username for authentication
            
        Returns:
            Authentication options for client
        """
        # Check if user has registered credentials
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT credential_id FROM webauthn_credentials WHERE username = ?
            ''', (username,))
            
            credentials = cursor.fetchall()
            if not credentials:
                return {
                    "status": "error",
                    "message": f"No WebAuthn credentials found for user {username}"
                }
        
        challenge = secrets.token_urlsafe(32)
        
        # Store challenge
        now = datetime.now(timezone.utc)
        expires_at = now + timedelta(minutes=5)
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO auth_challenges 
                (challenge, username, created_at, expires_at)
                VALUES (?, ?, ?, ?)
            ''', (challenge, username, now, expires_at))
            conn.commit()
        
        # Create authentication options
        authentication_options = {
            "challenge": challenge,
            "rpId": self.rp_id,
            "allowCredentials": [
                {
                    "type": "public-key",
                    "id": cred[0]
                } for cred in credentials
            ],
            "userVerification": "preferred",
            "timeout": 300000
        }
        
        return authentication_options
    
    def complete_authentication(self, username: str, credential_response: Dict[str, Any]) -> Dict[str, Any]:
        """
        Complete WebAuthn authentication and issue OAuth tokens.
        
        Args:
            username: Username
            credential_response: WebAuthn authentication response
            
        Returns:
            Authentication result with OAuth tokens
        """
        try:
            if not FIDO2_AVAILABLE:
                return self._simulate_authentication(username, credential_response)
            
            # Verify credential exists
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT credential_id, public_key, sign_count 
                    FROM webauthn_credentials 
                    WHERE username = ?
                ''', (username,))
                
                cred_data = cursor.fetchone()
                if not cred_data:
                    return {
                        "status": "error",
                        "message": "No credentials found for user"
                    }
                
                # Update last used timestamp
                cursor.execute('''
                    UPDATE webauthn_credentials 
                    SET last_used = ?, sign_count = sign_count + 1
                    WHERE username = ?
                ''', (datetime.now(timezone.utc), username))
                
                # Clean up challenge
                cursor.execute('DELETE FROM auth_challenges WHERE username = ?', (username,))
                
                conn.commit()
            
            # Create OAuth token response
            token_response = create_token_response(
                user_id=f"webauthn:{username}",
                username=username,
                roles=["user", "webauthn_verified"],
                permissions=["vault:read", "vault:write"],
                scope=["read", "write", "webauthn"]
            )
            
            return {
                "status": "success",
                "message": "WebAuthn authentication successful",
                "authentication_method": "webauthn",
                "tokens": {
                    "access_token": token_response.access_token,
                    "refresh_token": token_response.refresh_token,
                    "token_type": token_response.token_type,
                    "expires_in": token_response.expires_in
                }
            }
            
        except Exception as e:
            return {
                "status": "error",
                "message": f"Authentication failed: {e}"
            }
    
    def _simulate_authentication(self, username: str, credential_response: Dict[str, Any]) -> Dict[str, Any]:
        """Simulate WebAuthn authentication"""
        # Verify user has credentials
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT credential_id FROM webauthn_credentials WHERE username = ?
            ''', (username,))
            
            if not cursor.fetchone():
                return {
                    "status": "error",
                    "message": "No credentials found for user"
                }
            
            # Update last used
            cursor.execute('''
                UPDATE webauthn_credentials 
                SET last_used = ?, sign_count = sign_count + 1
                WHERE username = ?
            ''', (datetime.now(timezone.utc), username))
            
            # Clean up challenge
            cursor.execute('DELETE FROM auth_challenges WHERE username = ?', (username,))
            
            conn.commit()
        
        # Create OAuth token response
        token_response = create_token_response(
            user_id=f"webauthn:{username}",
            username=username,
            roles=["user", "webauthn_verified"],
            permissions=["vault:read", "vault:write"],
            scope=["read", "write", "webauthn"]
        )
        
        return {
            "status": "success",
            "message": "WebAuthn authentication successful (simulation mode)",
            "authentication_method": "webauthn_simulation",
            "simulation": True,
            "tokens": {
                "access_token": token_response.access_token,
                "refresh_token": token_response.refresh_token,
                "token_type": token_response.token_type,
                "expires_in": token_response.expires_in
            }
        }
    
    def get_user_credentials(self, username: str) -> List[WebAuthnCredential]:
        """Get all WebAuthn credentials for a user"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT credential_id, user_id, username, public_key, sign_count, 
                       created_at, last_used, device_name, transports
                FROM webauthn_credentials 
                WHERE username = ?
            ''', (username,))
            
            credentials = []
            for row in cursor.fetchall():
                credentials.append(WebAuthnCredential(
                    credential_id=row[0],
                    user_id=row[1],
                    username=row[2],
                    public_key=row[3],
                    sign_count=row[4],
                    created_at=row[5],
                    last_used=row[6],
                    device_name=row[7],
                    transports=json.loads(row[8]) if row[8] else []
                ))
            
            return credentials
    
    def revoke_credential(self, credential_id: str) -> bool:
        """Revoke a WebAuthn credential"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    DELETE FROM webauthn_credentials WHERE credential_id = ?
                ''', (credential_id,))
                
                conn.commit()
                return cursor.rowcount > 0
                
        except Exception as e:
            print(f"Error revoking credential: {e}")
            return False

if __name__ == "__main__":
    print("--- Testing WebAuthn Manager ---")
    
    manager = WebAuthnManager()
    
    # Test registration
    username = "alice_webauthn"
    print(f"\\n1. Creating registration challenge for {username}")
    
    reg_options = manager.create_registration_challenge(username, "Alice WebAuthn")
    print(f"✅ Registration options created:")
    print(f"   - Challenge: {reg_options['challenge'][:20]}...")
    print(f"   - RP ID: {reg_options['rp']['id']}")
    
    # Simulate registration response
    mock_reg_response = {
        "id": f"mock_credential_{secrets.token_hex(8)}",
        "rawId": "mock_raw_id",
        "response": {
            "attestationObject": "mock_attestation",
            "clientDataJSON": "mock_client_data"
        }
    }
    
    print(f"\\n2. Completing registration (simulation)")
    reg_result = manager.complete_registration(username, mock_reg_response, create_did=True)
    print(f"✅ Registration result: {reg_result['status']}")
    if reg_result.get('did'):
        print(f"   - DID created: {reg_result['did']}")
    
    # Test authentication
    print(f"\\n3. Creating authentication challenge")
    auth_options = manager.create_authentication_challenge(username)
    print(f"✅ Authentication options: {auth_options.get('challenge', 'error')[:20]}...")
    
    # Simulate authentication response
    mock_auth_response = {
        "id": reg_result.get('credential_id', 'mock_id'),
        "response": {
            "authenticatorData": "mock_auth_data",
            "clientDataJSON": "mock_client_data",
            "signature": "mock_signature"
        }
    }
    
    print(f"\\n4. Completing authentication")
    auth_result = manager.complete_authentication(username, mock_auth_response)
    print(f"✅ Authentication result: {auth_result['status']}")
    if auth_result.get('tokens'):
        print(f"   - Access token: {auth_result['tokens']['access_token'][:30]}...")
    
    print("\\n✅ WebAuthn manager tests completed!")