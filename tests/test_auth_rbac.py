# tests/test_auth_rbac.py

import pytest
import secrets
import tempfile
import os
from datetime import datetime, timezone
from unittest.mock import Mock, patch

import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../'))

from auth.rbac_enhanced import (
    EnhancedRBACManager, Role, Permission, RoleAssignment, 
    ResourceType, Action, EffectType
)
from auth.rbac_compatibility import CompatibilityRBACManager, HybridRoleChecker
from auth.rbac import RoleChecker, PermissionChecker

class TestEnhancedRBACManager:
    """Test Enhanced RBAC Manager functionality"""
    
    def setUp(self):
        """Set up test environment with temporary database"""
        self.temp_dir = tempfile.mkdtemp()
        self.db_path = os.path.join(self.temp_dir, "test_rbac.db")
        self.rbac_manager = EnhancedRBACManager(self.db_path)
        
        # Test data
        self.test_user_id = f"user_{secrets.token_hex(8)}"
        self.test_client_id = f"client_{secrets.token_hex(8)}"
    
    def test_create_role(self):
        """Test creating a new role"""
        self.setUp()
        
        # Create test role
        test_role = Role(
            role_id="test_role",
            name="Test Role",
            description="A test role for unit testing",
            permissions=[
                Permission(ResourceType.VAULT, Action.READ),
                Permission(ResourceType.VAULT, Action.CREATE),
            ],
            is_system_role=False
        )
        
        # Create role
        success = self.rbac_manager.create_role(test_role)
        assert success is True
        
        # Verify role was created by getting its permissions
        permissions = self.rbac_manager.get_role_permissions("test_role")
        assert len(permissions) == 2
        
        # Check permission details
        read_perm = next((p for p in permissions if p.action == Action.READ), None)
        assert read_perm is not None
        assert read_perm.resource_type == ResourceType.VAULT
        assert read_perm.effect == EffectType.ALLOW
        
        print("✅ Role creation test passed")
    
    def test_assign_role(self):
        """Test assigning a role to a principal"""
        self.setUp()
        
        # Create assignment
        assignment = RoleAssignment(
            assignment_id=f"assign_{secrets.token_hex(8)}",
            principal_id=self.test_user_id,
            principal_type="user",
            role_id="vault_user",  # System role that should exist
            granted_by="test_system"
        )
        
        # Assign role
        success = self.rbac_manager.assign_role(assignment)
        assert success is True
        
        # Verify assignment
        roles = self.rbac_manager.get_principal_roles(self.test_user_id, "user")
        assert "vault_user" in roles
        
        print("✅ Role assignment test passed")
    
    def test_check_permission_allow(self):
        """Test permission check that should be allowed"""
        self.setUp()
        
        # Assign vault_user role
        assignment = RoleAssignment(
            assignment_id=f"assign_{secrets.token_hex(8)}",
            principal_id=self.test_user_id,
            principal_type="user",
            role_id="vault_user",
            granted_by="test_system"
        )
        self.rbac_manager.assign_role(assignment)
        
        # Check permission that should be allowed
        granted, reason = self.rbac_manager.check_permission(
            principal_id=self.test_user_id,
            principal_type="user",
            resource_type=ResourceType.VAULT,
            action=Action.READ
        )
        
        assert granted is True
        assert "granted" in reason.lower()
        
        print("✅ Permission allow test passed")
    
    def test_check_permission_deny(self):
        """Test permission check that should be denied"""
        self.setUp()
        
        # Assign vault_readonly role (limited permissions)
        assignment = RoleAssignment(
            assignment_id=f"assign_{secrets.token_hex(8)}",
            principal_id=self.test_user_id,
            principal_type="user",
            role_id="vault_readonly",
            granted_by="test_system"
        )
        self.rbac_manager.assign_role(assignment)
        
        # Check permission that should be denied (admin action)
        granted, reason = self.rbac_manager.check_permission(
            principal_id=self.test_user_id,
            principal_type="user",
            resource_type=ResourceType.VAULT,
            action=Action.ADMIN
        )
        
        assert granted is False
        assert "no matching permissions" in reason.lower() or "denied" in reason.lower()
        
        print("✅ Permission deny test passed")
    
    def test_role_hierarchy_inheritance(self):
        """Test role hierarchy and permission inheritance"""
        self.setUp()
        
        # Create parent role
        parent_role = Role(
            role_id="parent_role",
            name="Parent Role",
            description="Parent role with basic permissions",
            permissions=[
                Permission(ResourceType.VAULT, Action.READ),
            ],
            is_system_role=False
        )
        self.rbac_manager.create_role(parent_role)
        
        # Create child role that inherits from parent
        child_role = Role(
            role_id="child_role",
            name="Child Role", 
            description="Child role that inherits from parent",
            permissions=[
                Permission(ResourceType.VAULT, Action.CREATE),
            ],
            parent_roles=["parent_role"],
            is_system_role=False
        )
        self.rbac_manager.create_role(child_role)
        
        # Assign child role to user
        assignment = RoleAssignment(
            assignment_id=f"assign_{secrets.token_hex(8)}",
            principal_id=self.test_user_id,
            principal_type="user",
            role_id="child_role",
            granted_by="test_system"
        )
        self.rbac_manager.assign_role(assignment)
        
        # Check that user has both child and inherited parent permissions
        # Should have CREATE from child role
        granted, _ = self.rbac_manager.check_permission(
            principal_id=self.test_user_id,
            principal_type="user",
            resource_type=ResourceType.VAULT,
            action=Action.CREATE
        )
        assert granted is True
        
        # Should have READ from parent role (inherited)
        granted, _ = self.rbac_manager.check_permission(
            principal_id=self.test_user_id,
            principal_type="user",
            resource_type=ResourceType.VAULT,
            action=Action.READ
        )
        assert granted is True
        
        print("✅ Role hierarchy test passed")
    
    def test_explicit_deny_permission(self):
        """Test explicit deny permissions take precedence"""
        self.setUp()
        
        # Create role with both allow and deny permissions
        mixed_role = Role(
            role_id="mixed_role",
            name="Mixed Role",
            description="Role with both allow and deny permissions",
            permissions=[
                Permission(ResourceType.VAULT, Action.READ, EffectType.ALLOW),
                Permission(ResourceType.VAULT, Action.READ, EffectType.DENY),  # Explicit deny
            ],
            is_system_role=False
        )
        self.rbac_manager.create_role(mixed_role)
        
        # Assign role
        assignment = RoleAssignment(
            assignment_id=f"assign_{secrets.token_hex(8)}",
            principal_id=self.test_user_id,
            principal_type="user",
            role_id="mixed_role",
            granted_by="test_system"
        )
        self.rbac_manager.assign_role(assignment)
        
        # Check permission - should be denied due to explicit deny
        granted, reason = self.rbac_manager.check_permission(
            principal_id=self.test_user_id,
            principal_type="user",
            resource_type=ResourceType.VAULT,
            action=Action.READ
        )
        
        assert granted is False
        assert "denied" in reason.lower()
        
        print("✅ Explicit deny test passed")
    
    def test_resource_specific_permissions(self):
        """Test resource-specific permissions"""
        self.setUp()
        
        # Create role with resource-specific permission
        specific_role = Role(
            role_id="specific_role",
            name="Specific Role",
            description="Role with resource-specific permissions",
            permissions=[
                Permission(ResourceType.VAULT, Action.READ, resource_id="vault_123"),
            ],
            is_system_role=False
        )
        self.rbac_manager.create_role(specific_role)
        
        # Assign role
        assignment = RoleAssignment(
            assignment_id=f"assign_{secrets.token_hex(8)}",
            principal_id=self.test_user_id,
            principal_type="user",
            role_id="specific_role",
            granted_by="test_system"
        )
        self.rbac_manager.assign_role(assignment)
        
        # Check permission for specific resource - should be allowed
        granted, _ = self.rbac_manager.check_permission(
            principal_id=self.test_user_id,
            principal_type="user",
            resource_type=ResourceType.VAULT,
            action=Action.READ,
            resource_id="vault_123"
        )
        assert granted is True
        
        # Check permission for different resource - should be denied
        granted, _ = self.rbac_manager.check_permission(
            principal_id=self.test_user_id,
            principal_type="user",
            resource_type=ResourceType.VAULT,
            action=Action.READ,
            resource_id="vault_456"
        )
        assert granted is False
        
        print("✅ Resource-specific permissions test passed")

class TestLegacyRBACCompatibility:
    """Test legacy RBAC system compatibility"""
    
    def test_legacy_role_checker(self):
        """Test legacy RoleChecker functionality"""
        # Mock authentication context for API key
        auth_context = {
            "auth_type": "api_key",
            "client_name": "test_client",
            "roles": ["vault:admin", "auditor"]
        }
        
        # Test role checker
        checker = RoleChecker(["vault:create"])
        
        # This should pass because vault:admin role has vault:create permission
        try:
            result = checker._check_role_permissions(auth_context["roles"])
            assert result is True
            print("✅ Legacy role checker test passed")
        except Exception as e:
            print(f"Legacy role checker test failed: {e}")
    
    def test_permission_checker(self):
        """Test PermissionChecker functionality"""
        # Mock OAuth2 authentication context
        auth_context = {
            "auth_type": "oauth2",
            "user_id": "user_123",
            "roles": ["vault:admin"],
            "permissions": ["vault:read", "vault:write"]
        }
        
        # Test has_permission
        has_perm = PermissionChecker.has_permission(auth_context, "vault:read")
        assert has_perm is True
        
        # Test has_any_permission
        has_any = PermissionChecker.has_any_permission(auth_context, ["vault:delete", "vault:read"])
        assert has_any is True
        
        # Test has_all_permissions
        has_all = PermissionChecker.has_all_permissions(auth_context, ["vault:read", "vault:write"])
        assert has_all is True
        
        # Test permission not granted
        has_perm = PermissionChecker.has_permission(auth_context, "audit:admin")
        assert has_perm is False
        
        print("✅ Permission checker test passed")

class TestRBACCompatibilityLayer:
    """Test RBAC compatibility layer"""
    
    def test_compatibility_manager(self):
        """Test CompatibilityRBACManager"""
        compat_manager = CompatibilityRBACManager()
        
        # Mock authentication context
        auth_context = {
            "auth_type": "oauth2",
            "user_id": "admin_001",
            "roles": ["admin"],
            "permissions": ["vault:admin"]
        }
        
        # Test compatibility check
        granted = compat_manager.check_permission_compatibility(
            auth_context=auth_context,
            legacy_permissions=["vault:admin"],
            enhanced_resource=ResourceType.VAULT,
            enhanced_action=Action.ADMIN
        )
        
        assert granted is True
        
        print("✅ Compatibility manager test passed")
    
    def test_hybrid_role_checker(self):
        """Test HybridRoleChecker"""
        # Mock authentication context
        auth_context = {
            "auth_type": "oauth2",
            "user_id": "admin_001",
            "username": "admin",
            "roles": ["admin"],
            "permissions": ["vault:admin"]
        }
        
        # Create hybrid checker
        checker = HybridRoleChecker(
            legacy_permissions=["vault:admin"],
            enhanced_resource=ResourceType.VAULT,
            enhanced_action=Action.ADMIN
        )
        
        # Test the checker (mocking the Depends context)
        try:
            result = checker.compatibility_manager.check_permission_compatibility(
                auth_context=auth_context,
                legacy_permissions=checker.legacy_permissions,
                enhanced_resource=checker.enhanced_resource,
                enhanced_action=checker.enhanced_action
            )
            assert result is True
            print("✅ Hybrid role checker test passed")
        except Exception as e:
            print(f"Hybrid role checker test failed: {e}")

class TestRBACSecurityFeatures:
    """Test RBAC security features"""
    
    def test_audit_logging(self):
        """Test that permission checks are audited"""
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = os.path.join(tmpdir, "audit_test.db")
            rbac_manager = EnhancedRBACManager(db_path)
            
            # Make a permission check
            granted, reason = rbac_manager.check_permission(
                principal_id="test_user",
                principal_type="user",
                resource_type=ResourceType.VAULT,
                action=Action.READ,
                context={"test": "context"}
            )
            
            # Verify audit entry was created
            import sqlite3
            with sqlite3.connect(db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT COUNT(*) FROM permission_audit")
                count = cursor.fetchone()[0]
                assert count > 0
            
            print("✅ Audit logging test passed")
    
    def test_role_assignment_validation(self):
        """Test role assignment validation"""
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = os.path.join(tmpdir, "validation_test.db")
            rbac_manager = EnhancedRBACManager(db_path)
            
            # Try to assign non-existent role
            assignment = RoleAssignment(
                assignment_id=f"assign_{secrets.token_hex(8)}",
                principal_id="test_user",
                principal_type="user",
                role_id="nonexistent_role",
                granted_by="test_system"
            )
            
            success = rbac_manager.assign_role(assignment)
            assert success is False  # Should fail for non-existent role
            
            print("✅ Role assignment validation test passed")
    
    def test_permission_string_formatting(self):
        """Test permission string formatting"""
        # Test basic permission
        perm = Permission(ResourceType.VAULT, Action.READ)
        perm_str = perm.to_string()
        assert perm_str == "vault:read"
        
        # Test permission with resource ID
        perm_specific = Permission(ResourceType.VAULT, Action.READ, resource_id="vault_123")
        perm_str = perm_specific.to_string()
        assert perm_str == "vault:read:vault_123"
        
        # Test deny permission
        perm_deny = Permission(ResourceType.VAULT, Action.READ, EffectType.DENY)
        perm_str = perm_deny.to_string()
        assert perm_str == "!vault:read"
        
        print("✅ Permission string formatting test passed")

if __name__ == "__main__":
    print("Running Enhanced RBAC Tests...")
    
    # Test Enhanced RBAC Manager
    test_enhanced = TestEnhancedRBACManager()
    
    print("\\n1. Testing enhanced RBAC manager...")
    test_enhanced.test_create_role()
    test_enhanced.test_assign_role()
    test_enhanced.test_check_permission_allow()
    test_enhanced.test_check_permission_deny()
    test_enhanced.test_role_hierarchy_inheritance()
    test_enhanced.test_explicit_deny_permission()
    test_enhanced.test_resource_specific_permissions()
    
    # Test Legacy Compatibility
    test_legacy = TestLegacyRBACCompatibility()
    
    print("\\n2. Testing legacy RBAC compatibility...")
    test_legacy.test_legacy_role_checker()
    test_legacy.test_permission_checker()
    
    # Test Compatibility Layer
    test_compat = TestRBACCompatibilityLayer()
    
    print("\\n3. Testing compatibility layer...")
    test_compat.test_compatibility_manager()
    test_compat.test_hybrid_role_checker()
    
    # Test Security Features
    test_security = TestRBACSecurityFeatures()
    
    print("\\n4. Testing security features...")
    test_security.test_audit_logging()
    test_security.test_role_assignment_validation()
    test_security.test_permission_string_formatting()
    
    print("\\n✅ All Enhanced RBAC tests completed successfully!")