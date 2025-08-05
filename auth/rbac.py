# auth/rbac.py

from typing import List
from fastapi import Depends, HTTPException, status
from auth.oauth import get_api_client_roles
from config_package import RBAC_MATRIX

class RoleChecker:
    """
    A FastAPI dependency class that checks if the authenticated client
    has the required permissions to access an endpoint.
    """
    def __init__(self, required_permissions: List[str]):
        self.required_permissions = required_permissions

    def __call__(self, client_roles: List[str] = Depends(get_api_client_roles)):
        """
        Validates the client's roles against the required permissions.
        """
        # Get all permissions granted to the client based on their roles
        client_permissions = set()
        for role in client_roles:
            permissions_for_role = RBAC_MATRIX.get(role, [])
            client_permissions.update(permissions_for_role)
            
        # Check if the client has all the required permissions
        for required_perm in self.required_permissions:
            if required_perm not in client_permissions:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Not enough permissions. Required: {required_perm}"
                )
        return True # Access granted