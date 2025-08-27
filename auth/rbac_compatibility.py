# auth/rbac_compatibility.py

from typing import Dict, List, Any, Optional
from fastapi import Depends, HTTPException, status
from .rbac_enhanced import EnhancedRBACManager, ResourceType, Action
from .rbac import RoleChecker as LegacyRoleChecker, PermissionChecker
from .oauth2 import verify_auth
import config_package

class CompatibilityRBACManager:
    """
    Compatibility layer that provides backward compatibility between
    legacy RBAC and enhanced RBAC systems.
    """
    
    def __init__(self):
        self.enhanced_rbac = EnhancedRBACManager()
        self.use_enhanced = getattr(config_package, 'ENHANCED_RBAC_ENABLED', True)
    
    def check_permission_compatibility(
        self,
        auth_context: Dict[str, Any],
        legacy_permissions: List[str],
        enhanced_resource: Optional[ResourceType] = None,
        enhanced_action: Optional[Action] = None,
        resource_id: Optional[str] = None
    ) -> bool:
        """
        Check permissions using both legacy and enhanced RBAC for compatibility.
        
        Args:
            auth_context: Authentication context
            legacy_permissions: Legacy permission strings
            enhanced_resource: Enhanced RBAC resource type
            enhanced_action: Enhanced RBAC action
            resource_id: Specific resource ID
            
        Returns:
            True if permission is granted by either system
        """
        # Try enhanced RBAC first if enabled and parameters provided
        if (self.use_enhanced and enhanced_resource and enhanced_action):
            auth_type = auth_context.get("auth_type")
            
            if auth_type == "oauth2":
                principal_id = auth_context.get("user_id")
                principal_type = "user"
            elif auth_type == "api_key":
                principal_id = auth_context.get("client_name")
                principal_type = "client"
            else:
                principal_id = None
                principal_type = None
            
            if principal_id:
                granted, _ = self.enhanced_rbac.check_permission(
                    principal_id=principal_id,
                    principal_type=principal_type,
                    resource_type=enhanced_resource,
                    action=enhanced_action,
                    resource_id=resource_id,
                    context=auth_context
                )
                
                if granted:
                    return True
        
        # Fall back to legacy RBAC
        try:
            legacy_checker = LegacyRoleChecker(legacy_permissions)
            legacy_checker(auth_context)
            return True
        except HTTPException:
            return False
    
    def get_user_permissions_legacy_format(
        self,
        principal_id: str,
        principal_type: str
    ) -> List[str]:
        """
        Get user permissions in legacy format for backward compatibility.
        
        Args:
            principal_id: User or client ID
            principal_type: "user" or "client"
            
        Returns:
            List of legacy permission strings
        """
        if not self.use_enhanced:
            return []
        
        # Get roles for the principal
        roles = self.enhanced_rbac.get_principal_roles(principal_id, principal_type)
        
        # Convert enhanced permissions to legacy format
        legacy_permissions = set()
        
        for role_id in roles:
            permissions = self.enhanced_rbac.get_role_permissions(role_id)
            
            for perm in permissions:
                # Map enhanced permissions to legacy format
                legacy_perm = self._map_to_legacy_permission(perm.resource_type, perm.action)
                if legacy_perm:
                    legacy_permissions.add(legacy_perm)
        
        return list(legacy_permissions)
    
    def _map_to_legacy_permission(self, resource_type: ResourceType, action: Action) -> Optional[str]:
        """Map enhanced permissions to legacy format"""
        mapping = {
            (ResourceType.VAULT, Action.CREATE): "vault:create",
            (ResourceType.VAULT, Action.READ): "vault:read",
            (ResourceType.VAULT, Action.UPDATE): "vault:update",
            (ResourceType.VAULT, Action.DELETE): "vault:delete",
            (ResourceType.VAULT, Action.ADMIN): "vault:admin",
            (ResourceType.VAULT, Action.LIST): "vault:read",
            (ResourceType.AUDIT_LOG, Action.READ): "audit:read",
            (ResourceType.USER_PROFILE, Action.ADMIN): "user:admin",
            (ResourceType.SYSTEM_CONFIG, Action.ADMIN): "system:admin",
        }
        
        return mapping.get((resource_type, action))

class HybridRoleChecker:
    """
    Hybrid role checker that can work with both legacy and enhanced RBAC.
    """
    
    def __init__(
        self,
        legacy_permissions: List[str],
        enhanced_resource: Optional[ResourceType] = None,
        enhanced_action: Optional[Action] = None,
        resource_id: Optional[str] = None
    ):
        self.legacy_permissions = legacy_permissions
        self.enhanced_resource = enhanced_resource
        self.enhanced_action = enhanced_action
        self.resource_id = resource_id
        self.compatibility_manager = CompatibilityRBACManager()
    
    def __call__(self, auth_context: Dict[str, Any] = Depends(verify_auth)):
        """Check permissions using hybrid approach"""
        granted = self.compatibility_manager.check_permission_compatibility(
            auth_context=auth_context,
            legacy_permissions=self.legacy_permissions,
            enhanced_resource=self.enhanced_resource,
            enhanced_action=self.enhanced_action,
            resource_id=self.resource_id
        )
        
        if not granted:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Insufficient permissions. Required: {self.legacy_permissions}"
            )
        
        return True

# Hybrid convenience functions that work with both systems
def require_vault_read_hybrid(vault_id: Optional[str] = None) -> HybridRoleChecker:
    """Hybrid vault read permission checker"""
    return HybridRoleChecker(
        legacy_permissions=["vault:read"],
        enhanced_resource=ResourceType.VAULT,
        enhanced_action=Action.READ,
        resource_id=vault_id
    )

def require_vault_write_hybrid(vault_id: Optional[str] = None) -> HybridRoleChecker:
    """Hybrid vault write permission checker"""
    return HybridRoleChecker(
        legacy_permissions=["vault:write", "vault:update"],
        enhanced_resource=ResourceType.VAULT,
        enhanced_action=Action.UPDATE,
        resource_id=vault_id
    )

def require_vault_admin_hybrid(vault_id: Optional[str] = None) -> HybridRoleChecker:
    """Hybrid vault admin permission checker"""
    return HybridRoleChecker(
        legacy_permissions=["vault:admin"],
        enhanced_resource=ResourceType.VAULT,
        enhanced_action=Action.ADMIN,
        resource_id=vault_id
    )

def require_audit_read_hybrid() -> HybridRoleChecker:
    """Hybrid audit read permission checker"""
    return HybridRoleChecker(
        legacy_permissions=["audit:read"],
        enhanced_resource=ResourceType.AUDIT_LOG,
        enhanced_action=Action.READ
    )

def require_user_admin_hybrid() -> HybridRoleChecker:
    """Hybrid user administration permission checker"""
    return HybridRoleChecker(
        legacy_permissions=["user:admin"],
        enhanced_resource=ResourceType.USER_PROFILE,
        enhanced_action=Action.ADMIN
    )

class MigrationStatusChecker:
    """Utility to check migration status and provide recommendations"""
    
    def __init__(self):
        self.compatibility_manager = CompatibilityRBACManager()
    
    def check_migration_status(self) -> Dict[str, Any]:
        """Check the status of RBAC migration"""
        status = {
            "enhanced_rbac_enabled": getattr(config_package, 'ENHANCED_RBAC_ENABLED', False),
            "migration_recommendations": [],
            "compatibility_issues": [],
            "next_steps": []
        }
        
        # Check if enhanced RBAC is enabled
        if not status["enhanced_rbac_enabled"]:
            status["migration_recommendations"].append(
                "Enable enhanced RBAC by setting ENHANCED_RBAC_ENABLED = True in config"
            )
        
        # Check for potential compatibility issues
        try:
            from .rbac_migration import RBACMigrationManager
            migration_manager = RBACMigrationManager()
            
            # Run verification
            verification = migration_manager.verify_migration()
            if not verification["all_passed"]:
                status["compatibility_issues"].append(
                    "Some verification tests failed - check migration results"
                )
                
                failed_tests = [test for test in verification["verification_tests"] if not test["passed"]]
                for test in failed_tests:
                    status["compatibility_issues"].append(f"Failed: {test['name']}")
        
        except Exception as e:
            status["compatibility_issues"].append(f"Migration verification error: {e}")
        
        # Provide next steps
        if status["enhanced_rbac_enabled"]:
            status["next_steps"].append("✅ Enhanced RBAC is enabled")
            if not status["compatibility_issues"]:
                status["next_steps"].append("✅ No compatibility issues detected")
                status["next_steps"].append("Consider gradually migrating endpoints to use enhanced RBAC checkers")
            else:
                status["next_steps"].append("🔍 Review compatibility issues and fix role assignments")
        else:
            status["next_steps"].append("1. Enable enhanced RBAC in configuration")
            status["next_steps"].append("2. Run RBAC migration")
            status["next_steps"].append("3. Verify migration results")
            status["next_steps"].append("4. Update endpoints to use hybrid checkers")
        
        return status

if __name__ == "__main__":
    print("--- Testing RBAC Compatibility Layer ---")
    
    # Check migration status
    status_checker = MigrationStatusChecker()
    status = status_checker.check_migration_status()
    
    print(f"\\nEnhanced RBAC Enabled: {status['enhanced_rbac_enabled']}")
    
    if status["migration_recommendations"]:
        print("\\nMigration Recommendations:")
        for rec in status["migration_recommendations"]:
            print(f"  • {rec}")
    
    if status["compatibility_issues"]:
        print("\\nCompatibility Issues:")
        for issue in status["compatibility_issues"]:
            print(f"  ⚠️  {issue}")
    
    print("\\nNext Steps:")
    for step in status["next_steps"]:
        print(f"  {step}")
    
    # Test compatibility manager
    print("\\n--- Testing Compatibility Manager ---")
    compat_manager = CompatibilityRBACManager()
    
    # Test getting permissions in legacy format
    legacy_perms = compat_manager.get_user_permissions_legacy_format("admin_001", "user")
    print(f"\\nAdmin user legacy permissions: {legacy_perms}")
    
    print("\\n✅ Compatibility layer tests completed!")