# auth/rbac_migration.py

import secrets
from typing import Dict, List, Any
from .rbac_enhanced import EnhancedRBACManager, RoleAssignment, ResourceType, Action, Permission, Role
from .identity_manager import IdentityManager
import config_package

class RBACMigrationManager:
    """
    Migration manager to help transition from legacy RBAC to enhanced RBAC.
    Provides utilities to:
    - Migrate existing API key roles to enhanced RBAC
    - Import legacy role assignments
    - Provide backward compatibility
    """
    
    def __init__(self):
        self.enhanced_rbac = EnhancedRBACManager()
        self.identity_manager = IdentityManager()
    
    def migrate_api_keys(self) -> Dict[str, Any]:
        """
        Migrate existing API keys to enhanced RBAC system.
        
        Returns:
            Migration results
        """
        results = {
            "migrated_clients": [],
            "failed_migrations": [],
            "total_processed": 0
        }
        
        try:
            for api_key_hash, client_data in config_package.API_KEYS.items():
                results["total_processed"] += 1
                
                client_name = client_data.get("client_name", f"client_{api_key_hash[:8]}")
                legacy_roles = client_data.get("roles", [])
                
                # Map legacy roles to enhanced roles
                enhanced_roles = []
                for legacy_role in legacy_roles:
                    enhanced_role = config_package.LEGACY_ROLE_MAPPINGS.get(legacy_role, legacy_role)
                    enhanced_roles.append(enhanced_role)
                
                # Create role assignments for each enhanced role
                migration_success = True
                for enhanced_role in enhanced_roles:
                    assignment = RoleAssignment(
                        assignment_id=f"migrate_{secrets.token_hex(8)}",
                        principal_id=client_name,
                        principal_type="client",
                        role_id=enhanced_role,
                        granted_by="migration_system"
                    )
                    
                    if not self.enhanced_rbac.assign_role(assignment):
                        migration_success = False
                        break
                
                if migration_success:
                    results["migrated_clients"].append({
                        "client_name": client_name,
                        "legacy_roles": legacy_roles,
                        "enhanced_roles": enhanced_roles
                    })
                else:
                    results["failed_migrations"].append({
                        "client_name": client_name,
                        "reason": "Failed to assign enhanced roles"
                    })
        
        except Exception as e:
            results["migration_error"] = str(e)
        
        return results
    
    def migrate_oauth_users(self) -> Dict[str, Any]:
        """
        Migrate existing OAuth users to enhanced RBAC.
        
        Returns:
            Migration results
        """
        results = {
            "migrated_users": [],
            "failed_migrations": [],
            "total_processed": 0
        }
        
        try:
            from .oauth2 import USERS_DB
            
            for username, user_data in USERS_DB.items():
                results["total_processed"] += 1
                
                user_id = user_data.get("user_id")
                legacy_roles = user_data.get("roles", [])
                
                # Map legacy roles to enhanced roles
                enhanced_roles = []
                for legacy_role in legacy_roles:
                    enhanced_role = config_package.LEGACY_ROLE_MAPPINGS.get(legacy_role, legacy_role)
                    enhanced_roles.append(enhanced_role)
                
                # Create role assignments
                migration_success = True
                for enhanced_role in enhanced_roles:
                    assignment = RoleAssignment(
                        assignment_id=f"migrate_{secrets.token_hex(8)}",
                        principal_id=user_id,
                        principal_type="user",
                        role_id=enhanced_role,
                        granted_by="migration_system"
                    )
                    
                    if not self.enhanced_rbac.assign_role(assignment):
                        migration_success = False
                        break
                
                if migration_success:
                    results["migrated_users"].append({
                        "user_id": user_id,
                        "username": username,
                        "legacy_roles": legacy_roles,
                        "enhanced_roles": enhanced_roles
                    })
                else:
                    results["failed_migrations"].append({
                        "user_id": user_id,
                        "username": username,
                        "reason": "Failed to assign enhanced roles"
                    })
        
        except Exception as e:
            results["migration_error"] = str(e)
        
        return results
    
    def create_custom_role(
        self,
        role_name: str,
        description: str,
        permissions: List[Dict[str, str]],
        parent_roles: List[str] = None
    ) -> bool:
        """
        Create a custom role for specific organizational needs.
        
        Args:
            role_name: Name of the role
            description: Role description
            permissions: List of permission dictionaries with 'resource' and 'action' keys
            parent_roles: List of parent role IDs for inheritance
            
        Returns:
            Success status
        """
        try:
            # Convert permission dictionaries to Permission objects
            perm_objects = []
            for perm_dict in permissions:
                resource_type = ResourceType(perm_dict["resource"])
                action = Action(perm_dict["action"])
                perm_objects.append(Permission(resource_type, action))
            
            # Create role
            role = Role(
                role_id=role_name.lower().replace(" ", "_"),
                name=role_name,
                description=description,
                permissions=perm_objects,
                parent_roles=parent_roles or [],
                is_system_role=False
            )
            
            return self.enhanced_rbac.create_role(role)
            
        except Exception as e:
            print(f"Error creating custom role: {e}")
            return False
    
    def verify_migration(self) -> Dict[str, Any]:
        """
        Verify that migration was successful by testing permission checks.
        
        Returns:
            Verification results
        """
        results = {
            "verification_tests": [],
            "all_passed": True
        }
        
        test_cases = [
            {
                "name": "API Client Vault Admin Access",
                "principal_id": "VaultAdmin-Client",
                "principal_type": "client",
                "resource": ResourceType.VAULT,
                "action": Action.ADMIN,
                "expected": True
            },
            {
                "name": "API Client Read-Only Access",
                "principal_id": "ReadOnly-Client", 
                "principal_type": "client",
                "resource": ResourceType.VAULT,
                "action": Action.READ,
                "expected": True
            },
            {
                "name": "API Client Read-Only No Admin",
                "principal_id": "ReadOnly-Client",
                "principal_type": "client", 
                "resource": ResourceType.VAULT,
                "action": Action.ADMIN,
                "expected": False
            },
            {
                "name": "OAuth Admin User Full Access",
                "principal_id": "admin_001",
                "principal_type": "user",
                "resource": ResourceType.VAULT,
                "action": Action.ADMIN,
                "expected": True
            },
            {
                "name": "OAuth Regular User No Admin",
                "principal_id": "user_001",
                "principal_type": "user",
                "resource": ResourceType.VAULT,
                "action": Action.ADMIN,
                "expected": False
            }
        ]
        
        for test_case in test_cases:
            try:
                granted, reason = self.enhanced_rbac.check_permission(
                    principal_id=test_case["principal_id"],
                    principal_type=test_case["principal_type"],
                    resource_type=test_case["resource"],
                    action=test_case["action"]
                )
                
                passed = granted == test_case["expected"]
                results["verification_tests"].append({
                    "name": test_case["name"],
                    "expected": test_case["expected"],
                    "actual": granted,
                    "passed": passed,
                    "reason": reason
                })
                
                if not passed:
                    results["all_passed"] = False
                    
            except Exception as e:
                results["verification_tests"].append({
                    "name": test_case["name"],
                    "passed": False,
                    "error": str(e)
                })
                results["all_passed"] = False
        
        return results
    
    def generate_migration_report(self) -> str:
        """Generate a comprehensive migration report"""
        report = []
        report.append("=" * 60)
        report.append("ReliQuary Enhanced RBAC Migration Report")
        report.append("=" * 60)
        
        # Migrate API keys
        report.append("\n1. API Key Migration")
        report.append("-" * 30)
        api_migration = self.migrate_api_keys()
        report.append(f"Total Processed: {api_migration['total_processed']}")
        report.append(f"Successfully Migrated: {len(api_migration['migrated_clients'])}")
        report.append(f"Failed Migrations: {len(api_migration['failed_migrations'])}")
        
        for client in api_migration['migrated_clients']:
            report.append(f"  ✅ {client['client_name']}: {client['legacy_roles']} → {client['enhanced_roles']}")
        
        for failure in api_migration['failed_migrations']:
            report.append(f"  ❌ {failure['client_name']}: {failure['reason']}")
        
        # Migrate OAuth users
        report.append("\n2. OAuth User Migration")
        report.append("-" * 30)
        user_migration = self.migrate_oauth_users()
        report.append(f"Total Processed: {user_migration['total_processed']}")
        report.append(f"Successfully Migrated: {len(user_migration['migrated_users'])}")
        report.append(f"Failed Migrations: {len(user_migration['failed_migrations'])}")
        
        for user in user_migration['migrated_users']:
            report.append(f"  ✅ {user['username']}: {user['legacy_roles']} → {user['enhanced_roles']}")
        
        for failure in user_migration['failed_migrations']:
            report.append(f"  ❌ {failure['username']}: {failure['reason']}")
        
        # Verification
        report.append("\n3. Migration Verification")
        report.append("-" * 30)
        verification = self.verify_migration()
        report.append(f"Overall Status: {'✅ PASSED' if verification['all_passed'] else '❌ FAILED'}")
        
        for test in verification['verification_tests']:
            status = "✅" if test['passed'] else "❌"
            report.append(f"  {status} {test['name']}: Expected={test['expected']}, Actual={test.get('actual', 'ERROR')}")
            if 'reason' in test:
                report.append(f"       Reason: {test['reason']}")
            if 'error' in test:
                report.append(f"       Error: {test['error']}")
        
        report.append("\n" + "=" * 60)
        report.append("Migration Complete!")
        report.append("=" * 60)
        
        return "\n".join(report)

def run_migration():
    """Run the complete RBAC migration process"""
    migration_manager = RBACMigrationManager()
    
    print("Starting Enhanced RBAC Migration...")
    print("=" * 50)
    
    # Generate and print migration report
    report = migration_manager.generate_migration_report()
    print(report)
    
    return migration_manager

if __name__ == "__main__":
    run_migration()