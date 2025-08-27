# auth/rbac_enhanced.py

import json
import sqlite3
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Set, Optional, Any, Union, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
import os
from fastapi import Depends, HTTPException, status

from .oauth2 import verify_auth
import config_package

class ResourceType(Enum):
    """Types of resources that can be protected"""
    VAULT = "vault"
    AUDIT_LOG = "audit_log"
    USER_PROFILE = "user_profile"
    SYSTEM_CONFIG = "system_config"
    DID_DOCUMENT = "did_document"
    WEBAUTHN_CREDENTIAL = "webauthn_credential"
    API_KEY = "api_key"
    SESSION = "session"

class Action(Enum):
    """Actions that can be performed on resources"""
    CREATE = "create"
    READ = "read"
    UPDATE = "update"
    DELETE = "delete"
    LIST = "list"
    ADMIN = "admin"
    EXECUTE = "execute"
    SHARE = "share"
    ARCHIVE = "archive"
    RESTORE = "restore"

class EffectType(Enum):
    """Permission effect types"""
    ALLOW = "allow"
    DENY = "deny"

@dataclass
class Permission:
    """Granular permission definition"""
    resource_type: ResourceType
    action: Action
    effect: EffectType = EffectType.ALLOW
    conditions: Dict[str, Any] = None
    resource_id: Optional[str] = None  # For resource-specific permissions
    
    def __post_init__(self):
        if self.conditions is None:
            self.conditions = {}
    
    def to_string(self) -> str:
        """Convert permission to string format"""
        base = f"{self.resource_type.value}:{self.action.value}"
        if self.resource_id:
            base += f":{self.resource_id}"
        if self.effect == EffectType.DENY:
            base = f"!{base}"
        return base

@dataclass
class Role:
    """Enhanced role definition"""
    role_id: str
    name: str
    description: str
    permissions: List[Permission]
    parent_roles: List[str] = None  # Role hierarchy
    is_system_role: bool = False
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.parent_roles is None:
            self.parent_roles = []
        if self.metadata is None:
            self.metadata = {}
        if self.created_at is None:
            self.created_at = datetime.now(timezone.utc).isoformat()
        if self.updated_at is None:
            self.updated_at = self.created_at

@dataclass
class RoleAssignment:
    """Role assignment to a user/client"""
    assignment_id: str
    principal_id: str  # User ID or client ID
    principal_type: str  # "user" or "client"
    role_id: str
    resource_type: Optional[ResourceType] = None  # For resource-scoped roles
    resource_id: Optional[str] = None  # For specific resource
    granted_by: Optional[str] = None
    granted_at: Optional[str] = None
    expires_at: Optional[str] = None
    conditions: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.conditions is None:
            self.conditions = {}
        if self.granted_at is None:
            self.granted_at = datetime.now(timezone.utc).isoformat()

class EnhancedRBACManager:
    """
    Enhanced Role-Based Access Control manager with:
    - Hierarchical roles
    - Resource-based permissions
    - Conditional access
    - Permission inheritance
    - Audit logging
    """
    
    def __init__(self, db_path: Optional[str] = None):
        if db_path is None:
            script_dir = os.path.dirname(os.path.realpath(__file__))
            self.db_path = os.path.join(script_dir, "rbac.db")
        else:
            self.db_path = db_path
        
        self._init_database()
        self._init_default_roles()
    
    def _init_database(self):
        """Initialize RBAC database"""
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Roles table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS roles (
                    role_id TEXT PRIMARY KEY,
                    name TEXT UNIQUE NOT NULL,
                    description TEXT,
                    parent_roles TEXT,
                    is_system_role BOOLEAN DEFAULT FALSE,
                    created_at TIMESTAMP NOT NULL,
                    updated_at TIMESTAMP NOT NULL,
                    metadata TEXT
                )
            ''')
            
            # Permissions table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS permissions (
                    permission_id TEXT PRIMARY KEY,
                    role_id TEXT NOT NULL,
                    resource_type TEXT NOT NULL,
                    action TEXT NOT NULL,
                    effect TEXT DEFAULT 'allow',
                    resource_id TEXT,
                    conditions TEXT,
                    FOREIGN KEY (role_id) REFERENCES roles (role_id)
                )
            ''')
            
            # Role assignments table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS role_assignments (
                    assignment_id TEXT PRIMARY KEY,
                    principal_id TEXT NOT NULL,
                    principal_type TEXT NOT NULL,
                    role_id TEXT NOT NULL,
                    resource_type TEXT,
                    resource_id TEXT,
                    granted_by TEXT,
                    granted_at TIMESTAMP NOT NULL,
                    expires_at TIMESTAMP,
                    conditions TEXT,
                    FOREIGN KEY (role_id) REFERENCES roles (role_id)
                )
            ''')
            
            # Permission audit log
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS permission_audit (
                    audit_id TEXT PRIMARY KEY,
                    principal_id TEXT NOT NULL,
                    principal_type TEXT NOT NULL,
                    resource_type TEXT NOT NULL,
                    resource_id TEXT,
                    action TEXT NOT NULL,
                    effect TEXT NOT NULL,
                    granted BOOLEAN NOT NULL,
                    reason TEXT,
                    timestamp TIMESTAMP NOT NULL,
                    metadata TEXT
                )
            ''')
            
            conn.commit()
    
    def _init_default_roles(self):
        """Initialize default system roles"""
        default_roles = [
            Role(
                role_id="system_admin",
                name="System Administrator",
                description="Full system access",
                permissions=[
                    Permission(ResourceType.VAULT, Action.ADMIN),
                    Permission(ResourceType.USER_PROFILE, Action.ADMIN),
                    Permission(ResourceType.SYSTEM_CONFIG, Action.ADMIN),
                    Permission(ResourceType.AUDIT_LOG, Action.READ),
                    Permission(ResourceType.DID_DOCUMENT, Action.ADMIN),
                    Permission(ResourceType.WEBAUTHN_CREDENTIAL, Action.ADMIN),
                    Permission(ResourceType.API_KEY, Action.ADMIN),
                    Permission(ResourceType.SESSION, Action.ADMIN),
                ],
                is_system_role=True
            ),
            Role(
                role_id="vault_admin",
                name="Vault Administrator",
                description="Full vault management access",
                permissions=[
                    Permission(ResourceType.VAULT, Action.CREATE),
                    Permission(ResourceType.VAULT, Action.READ),
                    Permission(ResourceType.VAULT, Action.UPDATE),
                    Permission(ResourceType.VAULT, Action.DELETE),
                    Permission(ResourceType.VAULT, Action.LIST),
                    Permission(ResourceType.VAULT, Action.SHARE),
                    Permission(ResourceType.VAULT, Action.ARCHIVE),
                    Permission(ResourceType.VAULT, Action.RESTORE),
                ],
                is_system_role=True
            ),
            Role(
                role_id="vault_user",
                name="Vault User",
                description="Standard vault access",
                permissions=[
                    Permission(ResourceType.VAULT, Action.CREATE),
                    Permission(ResourceType.VAULT, Action.READ),
                    Permission(ResourceType.VAULT, Action.UPDATE),
                    Permission(ResourceType.VAULT, Action.LIST),
                ],
                is_system_role=True
            ),
            Role(
                role_id="vault_readonly",
                name="Vault Read-Only",
                description="Read-only vault access",
                permissions=[
                    Permission(ResourceType.VAULT, Action.READ),
                    Permission(ResourceType.VAULT, Action.LIST),
                ],
                is_system_role=True
            ),
            Role(
                role_id="auditor",
                name="Auditor",
                description="Audit log access",
                permissions=[
                    Permission(ResourceType.AUDIT_LOG, Action.READ),
                    Permission(ResourceType.AUDIT_LOG, Action.LIST),
                    Permission(ResourceType.VAULT, Action.READ),
                    Permission(ResourceType.VAULT, Action.LIST),
                ],
                is_system_role=True
            ),
            Role(
                role_id="user_manager",
                name="User Manager",
                description="User profile management",
                permissions=[
                    Permission(ResourceType.USER_PROFILE, Action.CREATE),
                    Permission(ResourceType.USER_PROFILE, Action.READ),
                    Permission(ResourceType.USER_PROFILE, Action.UPDATE),
                    Permission(ResourceType.USER_PROFILE, Action.LIST),
                    Permission(ResourceType.DID_DOCUMENT, Action.READ),
                    Permission(ResourceType.WEBAUTHN_CREDENTIAL, Action.READ),
                ],
                is_system_role=True
            ),
        ]
        
        for role in default_roles:
            self.create_role(role)
    
    def create_role(self, role: Role) -> bool:
        """Create a new role"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Check if role already exists
                cursor.execute('SELECT role_id FROM roles WHERE role_id = ?', (role.role_id,))
                if cursor.fetchone():
                    return True  # Role already exists
                
                # Insert role
                cursor.execute('''
                    INSERT INTO roles (
                        role_id, name, description, parent_roles, is_system_role,
                        created_at, updated_at, metadata
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    role.role_id, role.name, role.description,
                    json.dumps(role.parent_roles), role.is_system_role,
                    role.created_at, role.updated_at, json.dumps(role.metadata)
                ))
                
                # Insert permissions
                for i, perm in enumerate(role.permissions):
                    permission_id = f"{role.role_id}_perm_{i}"
                    cursor.execute('''
                        INSERT INTO permissions (
                            permission_id, role_id, resource_type, action, effect,
                            resource_id, conditions
                        ) VALUES (?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        permission_id, role.role_id, perm.resource_type.value,
                        perm.action.value, perm.effect.value, perm.resource_id,
                        json.dumps(perm.conditions)
                    ))
                
                conn.commit()
                return True
                
        except Exception as e:
            print(f"Error creating role: {e}")
            return False
    
    def assign_role(self, assignment: RoleAssignment) -> bool:
        """Assign a role to a principal (user or client)"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Check if role exists
                cursor.execute('SELECT role_id FROM roles WHERE role_id = ?', (assignment.role_id,))
                if not cursor.fetchone():
                    return False
                
                # Insert assignment
                cursor.execute('''
                    INSERT INTO role_assignments (
                        assignment_id, principal_id, principal_type, role_id,
                        resource_type, resource_id, granted_by, granted_at,
                        expires_at, conditions
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    assignment.assignment_id, assignment.principal_id,
                    assignment.principal_type, assignment.role_id,
                    assignment.resource_type.value if assignment.resource_type else None,
                    assignment.resource_id, assignment.granted_by,
                    assignment.granted_at, assignment.expires_at,
                    json.dumps(assignment.conditions)
                ))
                
                conn.commit()
                return True
                
        except Exception as e:
            print(f"Error assigning role: {e}")
            return False
    
    def check_permission(
        self,
        principal_id: str,
        principal_type: str,
        resource_type: ResourceType,
        action: Action,
        resource_id: Optional[str] = None,
        context: Dict[str, Any] = None
    ) -> Tuple[bool, str]:
        """
        Check if a principal has permission to perform an action on a resource.
        
        Args:
            principal_id: User ID or client ID
            principal_type: "user" or "client"
            resource_type: Type of resource
            action: Action to perform
            resource_id: Specific resource ID (optional)
            context: Additional context for permission evaluation
            
        Returns:
            Tuple of (granted: bool, reason: str)
        """
        if context is None:
            context = {}
        
        try:
            # Get all roles assigned to the principal
            roles = self.get_principal_roles(principal_id, principal_type)
            
            # Check permissions for each role
            allowed_permissions = []
            denied_permissions = []
            
            for role_id in roles:
                role_permissions = self.get_role_permissions(role_id)
                
                for perm in role_permissions:
                    # Check if permission matches
                    if (perm.resource_type == resource_type and 
                        perm.action == action):
                        
                        # Check resource-specific permissions
                        if perm.resource_id and perm.resource_id != resource_id:
                            continue
                        
                        # Evaluate conditions
                        if not self._evaluate_conditions(perm.conditions, context):
                            continue
                        
                        if perm.effect == EffectType.ALLOW:
                            allowed_permissions.append(perm)
                        else:
                            denied_permissions.append(perm)
            
            # Explicit deny takes precedence
            if denied_permissions:
                reason = f"Access denied by explicit deny permission"
                self._audit_permission_check(
                    principal_id, principal_type, resource_type, resource_id,
                    action, False, reason, context
                )
                return False, reason
            
            # Check for allow permissions
            if allowed_permissions:
                reason = f"Access granted by role permission"
                self._audit_permission_check(
                    principal_id, principal_type, resource_type, resource_id,
                    action, True, reason, context
                )
                return True, reason
            
            # No matching permissions found
            reason = f"No matching permissions found"
            self._audit_permission_check(
                principal_id, principal_type, resource_type, resource_id,
                action, False, reason, context
            )
            return False, reason
            
        except Exception as e:
            reason = f"Permission check error: {e}"
            self._audit_permission_check(
                principal_id, principal_type, resource_type, resource_id,
                action, False, reason, context
            )
            return False, reason
    
    def get_principal_roles(self, principal_id: str, principal_type: str) -> List[str]:
        """Get all roles assigned to a principal"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Get non-expired role assignments
                now = datetime.now(timezone.utc).isoformat()
                cursor.execute('''
                    SELECT role_id FROM role_assignments
                    WHERE principal_id = ? AND principal_type = ?
                    AND (expires_at IS NULL OR expires_at > ?)
                ''', (principal_id, principal_type, now))
                
                return [row[0] for row in cursor.fetchall()]
                
        except Exception as e:
            print(f"Error getting principal roles: {e}")
            return []
    
    def get_role_permissions(self, role_id: str) -> List[Permission]:
        """Get all permissions for a role, including inherited permissions"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                permissions = []
                visited_roles = set()
                
                def collect_permissions(current_role_id: str):
                    if current_role_id in visited_roles:
                        return  # Avoid circular dependencies
                    visited_roles.add(current_role_id)
                    
                    # Get direct permissions
                    cursor.execute('''
                        SELECT resource_type, action, effect, resource_id, conditions
                        FROM permissions WHERE role_id = ?
                    ''', (current_role_id,))
                    
                    for row in cursor.fetchall():
                        permissions.append(Permission(
                            resource_type=ResourceType(row[0]),
                            action=Action(row[1]),
                            effect=EffectType(row[2]),
                            resource_id=row[3],
                            conditions=json.loads(row[4]) if row[4] else {}
                        ))
                    
                    # Get parent roles
                    cursor.execute('SELECT parent_roles FROM roles WHERE role_id = ?', (current_role_id,))
                    result = cursor.fetchone()
                    if result and result[0]:
                        parent_roles = json.loads(result[0])
                        for parent_role in parent_roles:
                            collect_permissions(parent_role)
                
                collect_permissions(role_id)
                return permissions
                
        except Exception as e:
            print(f"Error getting role permissions: {e}")
            return []
    
    def _evaluate_conditions(self, conditions: Dict[str, Any], context: Dict[str, Any]) -> bool:
        """Evaluate permission conditions against context"""
        if not conditions:
            return True
        
        for key, expected_value in conditions.items():
            if key not in context:
                return False
            
            actual_value = context[key]
            
            # Simple equality check for now
            # In a production system, this would support complex expressions
            if actual_value != expected_value:
                return False
        
        return True
    
    def _audit_permission_check(
        self,
        principal_id: str,
        principal_type: str,
        resource_type: ResourceType,
        resource_id: Optional[str],
        action: Action,
        granted: bool,
        reason: str,
        context: Dict[str, Any]
    ):
        """Audit permission check"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                audit_id = f"audit_{datetime.now().timestamp()}"
                cursor.execute('''
                    INSERT INTO permission_audit (
                        audit_id, principal_id, principal_type, resource_type,
                        resource_id, action, effect, granted, reason, timestamp, metadata
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    audit_id, principal_id, principal_type, resource_type.value,
                    resource_id, action.value, "allow" if granted else "deny",
                    granted, reason, datetime.now(timezone.utc).isoformat(),
                    json.dumps(context)
                ))
                
                conn.commit()
                
        except Exception as e:
            print(f"Error auditing permission check: {e}")

class EnhancedRoleChecker:
    """Enhanced role checker using the new RBAC system"""
    
    def __init__(
        self,
        resource_type: ResourceType,
        action: Action,
        resource_id: Optional[str] = None
    ):
        self.resource_type = resource_type
        self.action = action
        self.resource_id = resource_id
        self.rbac_manager = EnhancedRBACManager()
    
    def __call__(self, auth_context: Dict[str, Any] = Depends(verify_auth)):
        """Check permissions using enhanced RBAC"""
        auth_type = auth_context.get("auth_type")
        
        if auth_type == "oauth2":
            principal_id = auth_context.get("user_id")
            principal_type = "user"
        elif auth_type == "api_key":
            principal_id = auth_context.get("client_name")
            principal_type = "client"
        else:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication type"
            )
        
        if not principal_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="No principal ID found"
            )
        
        # Check permission
        granted, reason = self.rbac_manager.check_permission(
            principal_id=principal_id,
            principal_type=principal_type,
            resource_type=self.resource_type,
            action=self.action,
            resource_id=self.resource_id,
            context=auth_context
        )
        
        if not granted:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access denied: {reason}"
            )
        
        return True

# Convenience functions for common operations
def require_vault_create() -> EnhancedRoleChecker:
    """Require vault creation permission"""
    return EnhancedRoleChecker(ResourceType.VAULT, Action.CREATE)

def require_vault_read(vault_id: Optional[str] = None) -> EnhancedRoleChecker:
    """Require vault read permission"""
    return EnhancedRoleChecker(ResourceType.VAULT, Action.READ, vault_id)

def require_vault_update(vault_id: Optional[str] = None) -> EnhancedRoleChecker:
    """Require vault update permission"""
    return EnhancedRoleChecker(ResourceType.VAULT, Action.UPDATE, vault_id)

def require_vault_delete(vault_id: Optional[str] = None) -> EnhancedRoleChecker:
    """Require vault delete permission"""
    return EnhancedRoleChecker(ResourceType.VAULT, Action.DELETE, vault_id)

def require_audit_read() -> EnhancedRoleChecker:
    """Require audit log read permission"""
    return EnhancedRoleChecker(ResourceType.AUDIT_LOG, Action.READ)

def require_user_admin() -> EnhancedRoleChecker:
    """Require user administration permission"""
    return EnhancedRoleChecker(ResourceType.USER_PROFILE, Action.ADMIN)

if __name__ == "__main__":
    print("--- Testing Enhanced RBAC Manager ---")
    
    import secrets
    from .identity_manager import IdentityManager
    
    rbac_manager = EnhancedRBACManager()
    
    # Test role assignment
    test_user_id = "test_user_001"
    assignment = RoleAssignment(
        assignment_id=f"assign_{secrets.token_hex(8)}",
        principal_id=test_user_id,
        principal_type="user",
        role_id="vault_user",
        granted_by="system"
    )
    
    print(f"\\n1. Assigning vault_user role to {test_user_id}")
    result = rbac_manager.assign_role(assignment)
    print(f"✅ Role assignment: {'success' if result else 'failed'}")
    
    # Test permission check
    print(f"\\n2. Checking vault read permission")
    granted, reason = rbac_manager.check_permission(
        principal_id=test_user_id,
        principal_type="user",
        resource_type=ResourceType.VAULT,
        action=Action.READ
    )
    print(f"✅ Permission check: {'granted' if granted else 'denied'}")
    print(f"   Reason: {reason}")
    
    # Test permission check for admin action (should be denied)
    print(f"\\n3. Checking vault admin permission (should be denied)")
    granted, reason = rbac_manager.check_permission(
        principal_id=test_user_id,
        principal_type="user",
        resource_type=ResourceType.VAULT,
        action=Action.ADMIN
    )
    print(f"✅ Permission check: {'granted' if granted else 'denied'}")
    print(f"   Reason: {reason}")
    
    # Test role hierarchy by assigning admin role
    admin_assignment = RoleAssignment(
        assignment_id=f"assign_{secrets.token_hex(8)}",
        principal_id=test_user_id,
        principal_type="user",
        role_id="system_admin",
        granted_by="system"
    )
    
    print(f"\\n4. Assigning system_admin role")
    result = rbac_manager.assign_role(admin_assignment)
    print(f"✅ Admin role assignment: {'success' if result else 'failed'}")
    
    # Test admin permission
    print(f"\\n5. Checking vault admin permission (should be granted now)")
    granted, reason = rbac_manager.check_permission(
        principal_id=test_user_id,
        principal_type="user",
        resource_type=ResourceType.VAULT,
        action=Action.ADMIN
    )
    print(f"✅ Permission check: {'granted' if granted else 'denied'}")
    print(f"   Reason: {reason}")
    
    print("\\n✅ Enhanced RBAC manager tests completed!")