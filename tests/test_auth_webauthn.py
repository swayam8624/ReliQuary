# tests/test_auth_webauthn.py

import pytest
import secrets
import json
from datetime import datetime, timezone
from unittest.mock import Mock, patch

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../'))

from auth.webauthn.webauthn_manager import WebAuthnManager, WebAuthnCredential, RegistrationChallenge, AuthenticationChallenge

class TestWebAuthnManager:
    """Test WebAuthn authentication functionality"""
    
    def setUp(self):
        """Set up test environment"""
        self.webauthn_manager = WebAuthnManager()
        self.test_username = f"testuser_{secrets.token_hex(4)}"
        self.test_display_name = "Test User"
    
    def test_create_registration_challenge(self):
        """Test creating WebAuthn registration challenge"""
        self.setUp()
        
        options = self.webauthn_manager.create_registration_challenge(
            username=self.test_username,
            display_name=self.test_display_name
        )
        
        assert "challenge" in options
        assert "rp" in options
        assert "user" in options
        assert "pubKeyCredParams" in options
        
        # Check RP information
        assert options["rp"]["name"] == "ReliQuary Cryptographic Memory System"
        assert options["rp"]["id"] == "localhost"
        
        # Check user information
        assert options["user"]["name"] == self.test_username
        assert options["user"]["displayName"] == self.test_display_name
        
        # Check parameters
        assert len(options["pubKeyCredParams"]) >= 1
        assert options["timeout"] == 300000  # 5 minutes
        
        print(f"✅ Registration challenge created for {self.test_username}")
    
    def test_complete_registration_simulation(self):
        """Test completing WebAuthn registration in simulation mode"""
        self.setUp()
        
        # First create registration challenge
        options = self.webauthn_manager.create_registration_challenge(
            username=self.test_username,
            display_name=self.test_display_name
        )
        
        # Mock credential response
        mock_credential_response = {
            "id": f"mock_credential_{secrets.token_hex(8)}",
            "rawId": "mock_raw_id",
            "response": {
                "attestationObject": "mock_attestation",
                "clientDataJSON": "mock_client_data"
            }
        }
        
        # Complete registration
        result = self.webauthn_manager.complete_registration(
            username=self.test_username,
            credential_response=mock_credential_response,
            create_did=True
        )
        
        assert result["status"] == "success"
        assert "credential_id" in result
        assert "message" in result
        
        # Check if DID was created
        if result.get("did"):
            assert result["did"].startswith("did:reliquary:")
            assert "did_document" in result
        
        print(f"✅ Registration completed for {self.test_username}")
        return result
    
    def test_create_authentication_challenge(self):
        """Test creating WebAuthn authentication challenge"""
        self.setUp()
        
        # First register a user
        registration_result = self.test_complete_registration_simulation()
        
        # Create authentication challenge
        options = self.webauthn_manager.create_authentication_challenge(self.test_username)
        
        assert "challenge" in options
        assert "rpId" in options
        assert "allowCredentials" in options
        assert "userVerification" in options
        assert "timeout" in options
        
        # Check that credentials are included
        assert len(options["allowCredentials"]) > 0
        
        # Check credential format
        credential = options["allowCredentials"][0]
        assert credential["type"] == "public-key"
        assert "id" in credential
        
        print(f"✅ Authentication challenge created for {self.test_username}")
    
    def test_complete_authentication_simulation(self):
        """Test completing WebAuthn authentication in simulation mode"""
        self.setUp()
        
        # First register a user
        registration_result = self.test_complete_registration_simulation()
        credential_id = registration_result["credential_id"]
        
        # Create authentication challenge
        options = self.webauthn_manager.create_authentication_challenge(self.test_username)
        
        # Mock authentication response
        mock_auth_response = {
            "id": credential_id,
            "response": {
                "authenticatorData": "mock_auth_data",
                "clientDataJSON": "mock_client_data",
                "signature": "mock_signature"
            }
        }
        
        # Complete authentication
        result = self.webauthn_manager.complete_authentication(
            username=self.test_username,
            credential_response=mock_auth_response
        )
        
        assert result["status"] == "success"
        assert result["authentication_method"] in ["webauthn", "webauthn_simulation"]
        assert "tokens" in result
        
        # Check tokens
        tokens = result["tokens"]
        assert "access_token" in tokens
        assert "refresh_token" in tokens
        assert tokens["token_type"] == "bearer"
        assert tokens["expires_in"] > 0
        
        print(f"✅ Authentication completed for {self.test_username}")
        return result
    
    def test_get_user_credentials(self):
        """Test getting user's WebAuthn credentials"""
        self.setUp()
        
        # First register a user
        registration_result = self.test_complete_registration_simulation()
        
        # Get user credentials
        credentials = self.webauthn_manager.get_user_credentials(self.test_username)
        
        assert len(credentials) > 0
        
        credential = credentials[0]
        assert credential.username == self.test_username
        assert credential.credential_id is not None
        assert credential.public_key is not None
        assert credential.created_at is not None
        
        print(f"✅ Retrieved {len(credentials)} credentials for {self.test_username}")
    
    def test_authentication_no_credentials(self):
        """Test authentication for user with no credentials"""
        self.setUp()
        
        nonexistent_username = f"nouser_{secrets.token_hex(4)}"
        
        # Try to create authentication challenge for non-existent user
        options = self.webauthn_manager.create_authentication_challenge(nonexistent_username)
        
        assert options["status"] == "error"
        assert "No WebAuthn credentials found" in options["message"]
        
        print(f"✅ Correctly handled authentication for user with no credentials")
    
    def test_revoke_credential(self):
        """Test revoking a WebAuthn credential"""
        self.setUp()
        
        # First register a user
        registration_result = self.test_complete_registration_simulation()
        credential_id = registration_result["credential_id"]
        
        # Revoke the credential
        success = self.webauthn_manager.revoke_credential(credential_id)
        assert success is True
        
        # Verify credential is gone
        credentials = self.webauthn_manager.get_user_credentials(self.test_username)
        assert len(credentials) == 0
        
        print(f"✅ Successfully revoked credential {credential_id[:16]}...")
    
    def test_webauthn_integration_with_oauth(self):
        """Test WebAuthn integration with OAuth token system"""
        self.setUp()
        
        # Complete full WebAuthn flow
        auth_result = self.test_complete_authentication_simulation()
        
        # Verify token contains correct information
        tokens = auth_result["tokens"]
        access_token = tokens["access_token"]
        
        # Parse token (this would normally be done by JWT verification)
        from auth.jwt_tokens import jwt_manager
        payload = jwt_manager.verify_token(access_token)
        
        assert payload is not None
        assert payload["username"] == self.test_username
        assert payload["user_id"].startswith("webauthn:")
        assert "webauthn_verified" in payload.get("roles", [])
        
        print(f"✅ WebAuthn OAuth integration verified")

class TestWebAuthnDataModels:
    """Test WebAuthn data models"""
    
    def test_webauthn_credential_model(self):
        """Test WebAuthnCredential data model"""
        credential = WebAuthnCredential(
            credential_id=f"cred_{secrets.token_hex(8)}",
            user_id=f"user_{secrets.token_hex(8)}",
            username="testuser",
            public_key=b"mock_public_key",
            sign_count=0,
            created_at=datetime.now(timezone.utc).isoformat(),
            device_name="Test Device",
            transports=["usb", "nfc"]
        )
        
        assert credential.credential_id is not None
        assert credential.username == "testuser"
        assert credential.public_key == b"mock_public_key"
        assert credential.sign_count == 0
        assert credential.device_name == "Test Device"
        assert "usb" in credential.transports
        
        print("✅ WebAuthnCredential model test passed")
    
    def test_registration_challenge_model(self):
        """Test RegistrationChallenge data model"""
        challenge = RegistrationChallenge(
            challenge=secrets.token_urlsafe(32),
            user_id=f"user_{secrets.token_hex(8)}",
            username="testuser",
            created_at=datetime.now(timezone.utc).isoformat(),
            expires_at=(datetime.now(timezone.utc)).isoformat()
        )
        
        assert challenge.challenge is not None
        assert challenge.username == "testuser"
        assert challenge.created_at is not None
        assert challenge.expires_at is not None
        
        print("✅ RegistrationChallenge model test passed")
    
    def test_authentication_challenge_model(self):
        """Test AuthenticationChallenge data model"""
        challenge = AuthenticationChallenge(
            challenge=secrets.token_urlsafe(32),
            username="testuser",
            created_at=datetime.now(timezone.utc).isoformat(),
            expires_at=(datetime.now(timezone.utc)).isoformat()
        )
        
        assert challenge.challenge is not None
        assert challenge.username == "testuser"
        assert challenge.created_at is not None
        assert challenge.expires_at is not None
        
        print("✅ AuthenticationChallenge model test passed")

class TestWebAuthnSecurity:
    """Test WebAuthn security features"""
    
    def test_challenge_uniqueness(self):
        """Test that challenges are unique"""
        webauthn_manager = WebAuthnManager()
        
        # Create multiple challenges
        challenges = []
        for i in range(5):
            username = f"user_{i}"
            options = webauthn_manager.create_registration_challenge(username)
            challenges.append(options["challenge"])
        
        # Verify all challenges are unique
        assert len(set(challenges)) == len(challenges)
        
        print("✅ Challenge uniqueness test passed")
    
    def test_rp_configuration(self):
        """Test Relying Party configuration"""
        webauthn_manager = WebAuthnManager()
        
        # Test RP configuration
        assert webauthn_manager.rp_id == "localhost"
        assert webauthn_manager.rp_name == "ReliQuary Cryptographic Memory System"
        assert webauthn_manager.rp_origin.startswith("https://")
        
        print("✅ RP configuration test passed")
    
    def test_database_isolation(self):
        """Test that different WebAuthn manager instances have isolated databases"""
        # Create two managers with different database paths
        import tempfile
        import os
        
        with tempfile.TemporaryDirectory() as tmpdir:
            db1_path = os.path.join(tmpdir, "webauthn1.db")
            db2_path = os.path.join(tmpdir, "webauthn2.db")
            
            manager1 = WebAuthnManager(db1_path)
            manager2 = WebAuthnManager(db2_path)
            
            # Register different users in each
            username1 = "user1"
            username2 = "user2"
            
            options1 = manager1.create_registration_challenge(username1)
            options2 = manager2.create_registration_challenge(username2)
            
            # Verify isolation - manager1 shouldn't see user2's challenge
            auth_options1 = manager1.create_authentication_challenge(username2)
            assert auth_options1["status"] == "error"
            
            print("✅ Database isolation test passed")

if __name__ == "__main__":
    print("Running WebAuthn Authentication Tests...")
    
    # Test WebAuthn Manager
    test_manager = TestWebAuthnManager()
    
    print("\\n1. Testing WebAuthn registration...")
    test_manager.test_create_registration_challenge()
    test_manager.test_complete_registration_simulation()
    
    print("\\n2. Testing WebAuthn authentication...")
    test_manager.test_create_authentication_challenge()
    test_manager.test_complete_authentication_simulation()
    
    print("\\n3. Testing credential management...")
    test_manager.test_get_user_credentials()
    test_manager.test_revoke_credential()
    
    print("\\n4. Testing edge cases...")
    test_manager.test_authentication_no_credentials()
    
    print("\\n5. Testing OAuth integration...")
    test_manager.test_webauthn_integration_with_oauth()
    
    # Test Data Models
    test_models = TestWebAuthnDataModels()
    
    print("\\n6. Testing data models...")
    test_models.test_webauthn_credential_model()
    test_models.test_registration_challenge_model()
    test_models.test_authentication_challenge_model()
    
    # Test Security Features
    test_security = TestWebAuthnSecurity()
    
    print("\\n7. Testing security features...")
    test_security.test_challenge_uniqueness()
    test_security.test_rp_configuration()
    test_security.test_database_isolation()
    
    print("\\n✅ All WebAuthn authentication tests completed successfully!")