# auth/rbac.py

from typing import List, Dict, Any, Union
from fastapi import Depends, HTTPException, status
from .oauth2 import verify_auth, get_current_active_user, User
import config_package

class AccessControlError(Exception):
    """Exception raised for access control errors"""
    pass

class Role:
    """Represents a user role"""
    def __init__(self, name: str, permissions: List[str] = None):
        self.name = name
        self.permissions = permissions or []

class Permission:
    """Represents a permission"""
    def __init__(self, name: str, description: str = ""):
        self.name = name
        self.description = description

class Policy:
    """Represents an access control policy"""
    def __init__(self, name: str, roles: List[Role], permissions: List[Permission]):
        self.name = name
        self.roles = roles
        self.permissions = permissions

class RBACManager:
    """Manages Role-Based Access Control"""
    
    def __init__(self):
        self.roles = {}
        self.permissions = {}
        self.policies = {}
    
    def add_role(self, role: Role):
        """Add a role to the RBAC system"""
        self.roles[role.name] = role
    
    def add_permission(self, permission: Permission):
        """Add a permission to the RBAC system"""
        self.permissions[permission.name] = permission
    
    def assign_permission_to_role(self, role_name: str, permission_name: str):
        """Assign a permission to a role"""
        if role_name in self.roles and permission_name in self.permissions:
            self.roles[role_name].permissions.append(permission_name)
        else:
            raise AccessControlError(f"Role or permission not found")
    
    def check_permission(self, user_roles: List[str], permission_name: str) -> bool:
        """Check if a user with given roles has a specific permission"""
        for role_name in user_roles:
            if role_name in self.roles:
                role = self.roles[role_name]
                if permission_name in role.permissions:
                    return True
        return False

class RoleChecker:
    """
    A FastAPI dependency class that checks if the authenticated user/client
    has the required permissions to access an endpoint.
    Supports both OAuth 2.0 JWT tokens and legacy API keys.
    """
    def __init__(self, required_permissions: List[str]):
        self.required_permissions = required_permissions

    def __call__(self, auth_context: Dict[str, Any] = Depends(verify_auth)):
        """
        Validates the user's roles/permissions against the required permissions.
        
        Args:
            auth_context: Authentication context from verify_auth dependency
            
        Returns:
            True if access granted
            
        Raises:
            HTTPException: If insufficient permissions
        """
        auth_type = auth_context.get("auth_type")
        
        if auth_type == "api_key":
            # Legacy API key authentication
            client_roles = auth_context.get("roles", [])
            return self._check_role_permissions(client_roles)
        
        elif auth_type == "oauth2":
            # OAuth 2.0 JWT token authentication
            user_roles = auth_context.get("roles", [])
            user_permissions = auth_context.get("permissions", [])
            
            # Check direct permissions first
            for required_perm in self.required_permissions:
                if required_perm in user_permissions:
                    continue
                    
                # If not in direct permissions, check role-based permissions
                if not self._check_role_permissions(user_roles, [required_perm]):
                    raise HTTPException(
                        status_code=status.HTTP_403_FORBIDDEN,
                        detail=f"Insufficient permissions. Required: {required_perm}"
                    )
            
            return True
        
        else:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication type"
            )
    
    def _check_role_permissions(self, roles: List[str], required_perms: List[str] = None) -> bool:
        """
        Check if roles have the required permissions.
        
        Args:
            roles: List of user/client roles
            required_perms: List of required permissions (defaults to self.required_permissions)
            
        Returns:
            True if all permissions are granted
        """
        if required_perms is None:
            required_perms = self.required_permissions
            
        # Get all permissions granted to the user based on their roles
        client_permissions = set()
        for role in roles:
            permissions_for_role = config_package.RBAC_MATRIX.get(role, [])
            client_permissions.update(permissions_for_role)
            
        # Check if the user has all the required permissions
        for required_perm in required_perms:
            if required_perm not in client_permissions:
                return False
                
        return True

class PermissionChecker:
    """
    Enhanced permission checker with more granular control.
    """
    
    @staticmethod
    def has_permission(auth_context: Dict[str, Any], permission: str) -> bool:
        """
        Check if authentication context has a specific permission.
        
        Args:
            auth_context: Authentication context
            permission: Permission to check
            
        Returns:
            True if permission is granted
        """
        auth_type = auth_context.get("auth_type")
        
        if auth_type == "oauth2":
            # Direct permission check
            permissions = auth_context.get("permissions", [])
            if permission in permissions:
                return True
            
            # Role-based permission check
            roles = auth_context.get("roles", [])
            for role in roles:
                role_permissions = config_package.RBAC_MATRIX.get(role, [])
                if permission in role_permissions:
                    return True
        
        elif auth_type == "api_key":
            # API key role-based check
            roles = auth_context.get("roles", [])
            for role in roles:
                role_permissions = config_package.RBAC_MATRIX.get(role, [])
                if permission in role_permissions:
                    return True
        
        return False
    
    @staticmethod
    def has_any_permission(auth_context: Dict[str, Any], permissions: List[str]) -> bool:
        """
        Check if authentication context has any of the specified permissions.
        
        Args:
            auth_context: Authentication context
            permissions: List of permissions to check
            
        Returns:
            True if any permission is granted
        """
        for permission in permissions:
            if PermissionChecker.has_permission(auth_context, permission):
                return True
        return False
    
    @staticmethod
    def has_all_permissions(auth_context: Dict[str, Any], permissions: List[str]) -> bool:
        """
        Check if authentication context has all of the specified permissions.
        
        Args:
            auth_context: Authentication context
            permissions: List of permissions to check
            
        Returns:
            True if all permissions are granted
        """
        for permission in permissions:
            if not PermissionChecker.has_permission(auth_context, permission):
                return False
        return True

class ScopeChecker:
    """
    OAuth 2.0 scope checker for API endpoints.
    """
    def __init__(self, required_scopes: List[str]):
        self.required_scopes = required_scopes
    
    def __call__(self, auth_context: Dict[str, Any] = Depends(verify_auth)):
        """
        Check if the OAuth 2.0 token has the required scopes.
        
        Args:
            auth_context: Authentication context
            
        Returns:
            True if scopes are valid
            
        Raises:
            HTTPException: If insufficient scopes
        """
        if auth_context.get("auth_type") != "oauth2":
            # Scope checking only applies to OAuth 2.0 tokens
            return True
        
        token_scopes = auth_context.get("scope", [])
        
        for required_scope in self.required_scopes:
            if required_scope not in token_scopes:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Insufficient scope. Required: {required_scope}"
                )
        
        return True

# Convenience functions for common permission checks
def require_vault_read() -> RoleChecker:
    """Require vault read permission"""
    return RoleChecker(["vault:read"])

def require_vault_write() -> RoleChecker:
    """Require vault write permission"""
    return RoleChecker(["vault:write"])

def require_vault_admin() -> RoleChecker:
    """Require vault admin permission"""
    return RoleChecker(["vault:admin"])

def require_audit_read() -> RoleChecker:
    """Require audit read permission"""
    return RoleChecker(["audit:read"])

def require_admin() -> RoleChecker:
    """Require admin role permissions"""
    return RoleChecker(["vault:admin", "audit:read"])

# OAuth 2.0 scope checkers
def require_read_scope() -> ScopeChecker:
    """Require read scope"""
    return ScopeChecker(["read"])

def require_write_scope() -> ScopeChecker:
    """Require write scope"""
    return ScopeChecker(["write"])

def require_admin_scope() -> ScopeChecker:
    """Require admin scope"""
    return ScopeChecker(["admin"])