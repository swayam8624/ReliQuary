# tests/test_auth_identity.py

import pytest
import secrets
import tempfile
import os
from datetime import datetime, timezone
from unittest.mock import Mock, patch

import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../'))

from auth.identity_manager import (
    IdentityManager, UserProfile, IdentityCredential, IdentitySession,
    IdentityProviderType, AccountStatus
)

class TestIdentityManager:
    """Test Identity Manager functionality"""
    
    def setUp(self):
        """Set up test environment with temporary database"""
        self.temp_dir = tempfile.mkdtemp()
        self.db_path = os.path.join(self.temp_dir, "test_identity.db")
        self.identity_manager = IdentityManager(self.db_path)
        
        # Test data
        self.test_username = f"testuser_{secrets.token_hex(4)}"
        self.test_email = f"{self.test_username}@example.com"
        self.test_password = "SecurePassword123!"
    
    def test_create_user_success(self):
        """Test successful user creation"""
        self.setUp()
        
        result = self.identity_manager.create_user(
            username=self.test_username,
            email=self.test_email,
            password=self.test_password,
            display_name="Test User",
            first_name="Test",
            last_name="User",
            organization="Test Corp",
            create_did=True
        )
        
        assert result["status"] == "success"
        assert result["username"] == self.test_username
        assert "user_id" in result
        assert "profile" in result
        assert "credentials" in result
        
        # Check if DID was created
        if result.get("did"):
            assert result["did"].startswith("did:reliquary:")
            assert "did_document" in result
        
        # Verify credentials
        credentials = result["credentials"]
        assert len(credentials) >= 1  # At least password credential
        
        print(f"✅ User creation successful for {self.test_username}")
        return result
    
    def test_create_user_duplicate_username(self):
        """Test user creation with duplicate username"""
        self.setUp()
        
        # Create first user
        self.test_create_user_success()
        
        # Try to create another user with same username
        result = self.identity_manager.create_user(
            username=self.test_username,  # Same username
            email="different@example.com",
            password=self.test_password
        )
        
        assert result["status"] == "error"
        assert "already exists" in result["message"].lower()
        
        print("✅ Duplicate username handling test passed")
    
    def test_create_user_duplicate_email(self):
        """Test user creation with duplicate email"""
        self.setUp()
        
        # Create first user
        self.test_create_user_success()
        
        # Try to create another user with same email
        result = self.identity_manager.create_user(
            username=f"different_{secrets.token_hex(4)}",
            email=self.test_email,  # Same email
            password=self.test_password
        )
        
        assert result["status"] == "error"
        assert "already exists" in result["message"].lower()
        
        print("✅ Duplicate email handling test passed")
    
    def test_authenticate_user_password_success(self):
        """Test successful password authentication"""
        self.setUp()
        
        # Create user first
        create_result = self.test_create_user_success()
        
        # Authenticate with password
        auth_result = self.identity_manager.authenticate_user(
            username=self.test_username,
            password=self.test_password,
            ip_address="192.168.1.100",
            user_agent="Test/1.0"
        )
        
        assert auth_result["status"] == "success"
        assert auth_result["username"] == self.test_username
        assert auth_result["authentication_method"] == IdentityProviderType.OAUTH2_PASSWORD.value
        assert "tokens" in auth_result
        assert "session_id" in auth_result
        assert "profile" in auth_result
        
        # Verify tokens
        tokens = auth_result["tokens"]
        assert "access_token" in tokens
        assert "refresh_token" in tokens
        assert tokens["token_type"] == "bearer"
        
        print(f"✅ Password authentication successful for {self.test_username}")
        return auth_result
    
    def test_authenticate_user_wrong_password(self):
        """Test authentication with wrong password"""
        self.setUp()
        
        # Create user first
        self.test_create_user_success()
        
        # Try to authenticate with wrong password
        auth_result = self.identity_manager.authenticate_user(
            username=self.test_username,
            password="WrongPassword123!",
            ip_address="192.168.1.100"
        )
        
        assert auth_result["status"] == "error"
        assert "invalid" in auth_result["message"].lower() or "password" in auth_result["message"].lower()
        
        print("✅ Wrong password handling test passed")
    
    def test_authenticate_nonexistent_user(self):
        """Test authentication for non-existent user"""
        self.setUp()
        
        nonexistent_username = f"nonexistent_{secrets.token_hex(4)}"
        
        auth_result = self.identity_manager.authenticate_user(
            username=nonexistent_username,
            password=self.test_password
        )
        
        assert auth_result["status"] == "error"
        assert "not found" in auth_result["message"].lower() or "not active" in auth_result["message"].lower()
        
        print("✅ Non-existent user handling test passed")
    
    def test_get_user_profile(self):
        """Test getting user profile"""
        self.setUp()
        
        # Create user first
        create_result = self.test_create_user_success()
        
        # Get user profile
        profile = self.identity_manager.get_user_profile(self.test_username)
        
        assert profile is not None
        assert profile.username == self.test_username
        assert profile.email == self.test_email
        assert profile.display_name == "Test User"
        assert profile.first_name == "Test"
        assert profile.last_name == "User"
        assert profile.organization == "Test Corp"
        assert profile.account_status == AccountStatus.ACTIVE
        
        print(f"✅ Profile retrieval successful for {self.test_username}")
        return profile
    
    def test_get_user_profile_nonexistent(self):
        """Test getting profile for non-existent user"""
        self.setUp()
        
        nonexistent_username = f"nonexistent_{secrets.token_hex(4)}"
        profile = self.identity_manager.get_user_profile(nonexistent_username)
        
        assert profile is None
        
        print("✅ Non-existent profile handling test passed")
    
    def test_password_hashing_and_verification(self):
        """Test password hashing and verification"""
        self.setUp()
        
        password = "TestPassword123!"
        
        # Hash password
        password_hash, salt = self.identity_manager._hash_password(password)
        
        assert password_hash is not None
        assert password_hash != password  # Should be hashed
        
        # Verify correct password
        is_valid = self.identity_manager._verify_password(password, password_hash, salt)
        assert is_valid is True
        
        # Verify incorrect password
        is_valid = self.identity_manager._verify_password("WrongPassword", password_hash, salt)
        assert is_valid is False
        
        print("✅ Password hashing and verification test passed")
    
    def test_create_user_without_did(self):
        """Test creating user without DID"""
        self.setUp()
        
        result = self.identity_manager.create_user(
            username=self.test_username,
            email=self.test_email,
            password=self.test_password,
            create_did=False  # Don't create DID
        )
        
        assert result["status"] == "success"
        assert "did" not in result or result.get("did") is None
        
        # Should still have password credential
        credentials = result["credentials"]
        password_creds = [c for c in credentials if c["type"] == "password"]
        assert len(password_creds) > 0
        
        print("✅ User creation without DID test passed")
    
    def test_create_user_without_password(self):
        """Test creating user without password"""
        self.setUp()
        
        result = self.identity_manager.create_user(
            username=self.test_username,
            email=self.test_email,
            # No password provided
            display_name="Test User No Password",
            create_did=True
        )
        
        assert result["status"] == "success"
        
        # Should only have DID credential, no password credential
        credentials = result["credentials"]
        password_creds = [c for c in credentials if c["type"] == "password"]
        assert len(password_creds) == 0
        
        # Should have DID credential
        if result.get("did"):
            did_creds = [c for c in credentials if c["type"] == "did"]
            assert len(did_creds) > 0
        
        print("✅ User creation without password test passed")

class TestUserProfile:
    """Test UserProfile data model"""
    
    def test_user_profile_creation(self):
        """Test UserProfile creation and defaults"""
        profile = UserProfile(
            user_id="user_123",
            username="testuser",
            email="test@example.com",
            display_name="Test User"
        )
        
        assert profile.user_id == "user_123"
        assert profile.username == "testuser"
        assert profile.email == "test@example.com"
        assert profile.display_name == "Test User"
        assert profile.account_status == AccountStatus.ACTIVE
        assert profile.two_factor_enabled is False
        assert profile.failed_login_attempts == 0
        assert profile.must_change_password is False
        assert profile.language == "en"
        assert isinstance(profile.metadata, dict)
        assert profile.created_at is not None
        assert profile.updated_at is not None
        
        print("✅ UserProfile creation test passed")
    
    def test_user_profile_account_statuses(self):
        """Test different account statuses"""
        statuses = [
            AccountStatus.ACTIVE,
            AccountStatus.SUSPENDED,
            AccountStatus.PENDING_VERIFICATION,
            AccountStatus.DEACTIVATED
        ]
        
        for status in statuses:
            profile = UserProfile(
                user_id="user_123",
                username="testuser",
                account_status=status
            )
            assert profile.account_status == status
        
        print("✅ Account status test passed")

class TestIdentityCredential:
    """Test IdentityCredential data model"""
    
    def test_credential_creation(self):
        """Test IdentityCredential creation"""
        credential = IdentityCredential(
            credential_id="cred_123",
            user_id="user_123",
            provider_type=IdentityProviderType.OAUTH2_PASSWORD,
            provider_id="password_provider",
            credential_data={"method": "bcrypt"},
            is_primary=True
        )
        
        assert credential.credential_id == "cred_123"
        assert credential.user_id == "user_123"
        assert credential.provider_type == IdentityProviderType.OAUTH2_PASSWORD
        assert credential.provider_id == "password_provider"
        assert credential.credential_data == {"method": "bcrypt"}
        assert credential.is_primary is True
        assert credential.is_verified is True  # Default
        assert credential.created_at is not None
        assert isinstance(credential.metadata, dict)
        
        print("✅ IdentityCredential creation test passed")
    
    def test_credential_provider_types(self):
        """Test different credential provider types"""
        provider_types = [
            IdentityProviderType.LOCAL,
            IdentityProviderType.OAUTH2_PASSWORD,
            IdentityProviderType.WEBAUTHN,
            IdentityProviderType.DID,
            IdentityProviderType.API_KEY
        ]
        
        for provider_type in provider_types:
            credential = IdentityCredential(
                credential_id=f"cred_{provider_type.value}",
                user_id="user_123",
                provider_type=provider_type,
                provider_id=f"{provider_type.value}_provider",
                credential_data={}
            )
            assert credential.provider_type == provider_type
        
        print("✅ Provider types test passed")

class TestIdentitySession:
    """Test IdentitySession data model"""
    
    def test_session_creation(self):
        """Test IdentitySession creation"""
        now = datetime.now(timezone.utc).isoformat()
        expires = datetime.now(timezone.utc).isoformat()
        
        session = IdentitySession(
            session_id="sess_123",
            user_id="user_123",
            username="testuser",
            authentication_method=IdentityProviderType.OAUTH2_PASSWORD,
            created_at=now,
            expires_at=expires,
            last_activity=now,
            ip_address="192.168.1.100",
            user_agent="Test/1.0",
            metadata={}  # Initialize metadata
        )
        
        assert session.session_id == "sess_123"
        assert session.user_id == "user_123"
        assert session.username == "testuser"
        assert session.authentication_method == IdentityProviderType.OAUTH2_PASSWORD
        assert session.created_at == now
        assert session.expires_at == expires
        assert session.last_activity == now
        assert session.ip_address == "192.168.1.100"
        assert session.user_agent == "Test/1.0"
        assert isinstance(session.metadata, dict)
        
        print("✅ IdentitySession creation test passed")

class TestIdentityIntegration:
    """Test identity system integration with other components"""
    
    def test_identity_webauthn_integration(self):
        """Test identity manager integration with WebAuthn"""
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = os.path.join(tmpdir, "integration_test.db")
            identity_manager = IdentityManager(db_path)
            
            # Create user
            username = f"webauthn_user_{secrets.token_hex(4)}"
            email = f"{username}@example.com"
            
            result = identity_manager.create_user(
                username=username,
                email=email,
                display_name="WebAuthn User",
                create_did=True
            )
            
            assert result["status"] == "success"
            
            # Verify WebAuthn manager is accessible
            webauthn_manager = identity_manager.webauthn_manager
            assert webauthn_manager is not None
            
            # Test WebAuthn registration flow
            options = webauthn_manager.create_registration_challenge(username)
            assert "challenge" in options
            
            print("✅ Identity-WebAuthn integration test passed")
    
    def test_identity_did_integration(self):
        """Test identity manager integration with DID system"""
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = os.path.join(tmpdir, "did_integration_test.db")
            identity_manager = IdentityManager(db_path)
            
            # Create user with DID
            username = f"did_user_{secrets.token_hex(4)}"
            email = f"{username}@example.com"
            
            result = identity_manager.create_user(
                username=username,
                email=email,
                display_name="DID User",
                create_did=True
            )
            
            assert result["status"] == "success"
            
            # Check DID was created
            if result.get("did"):
                assert result["did"].startswith("did:reliquary:")
                assert "did_document" in result
                
                # Verify DID document structure
                did_doc = result["did_document"]
                assert did_doc["id"] == result["did"]
                assert "verificationMethod" in did_doc
                assert "authentication" in did_doc
            
            print("✅ Identity-DID integration test passed")

if __name__ == "__main__":
    print("Running Identity Management Tests...")
    
    # Test Identity Manager
    test_identity = TestIdentityManager()
    
    print("\\n1. Testing user creation...")
    test_identity.test_create_user_success()
    test_identity.test_create_user_duplicate_username()
    test_identity.test_create_user_duplicate_email()
    test_identity.test_create_user_without_did()
    test_identity.test_create_user_without_password()
    
    print("\\n2. Testing user authentication...")
    test_identity.test_authenticate_user_password_success()
    test_identity.test_authenticate_user_wrong_password()
    test_identity.test_authenticate_nonexistent_user()
    
    print("\\n3. Testing profile management...")
    test_identity.test_get_user_profile()
    test_identity.test_get_user_profile_nonexistent()
    
    print("\\n4. Testing password security...")
    test_identity.test_password_hashing_and_verification()
    
    # Test Data Models
    test_profile = TestUserProfile()
    
    print("\\n5. Testing data models...")
    test_profile.test_user_profile_creation()
    test_profile.test_user_profile_account_statuses()
    
    test_credential = TestIdentityCredential()
    test_credential.test_credential_creation()
    test_credential.test_credential_provider_types()
    
    test_session = TestIdentitySession()
    test_session.test_session_creation()
    
    # Test Integration
    test_integration = TestIdentityIntegration()
    
    print("\\n6. Testing system integration...")
    test_integration.test_identity_webauthn_integration()
    test_integration.test_identity_did_integration()
    
    print("\\n✅ All Identity Management tests completed successfully!")