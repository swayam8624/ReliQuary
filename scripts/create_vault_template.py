#!/usr/bin/env python3
"""
Script to create new vault templates for enterprises.
This script helps generate vault schemas and templates for enterprise clients.
"""

import json
import argparse
import sys
from datetime import datetime
from typing import Dict, Any, Optional


def create_vault_template(
    name: str,
    description: str = "",
    owner_id: str = "enterprise-client",
    encryption_algorithm: str = "AES-GCM-256",
    trust_level: str = "medium",
    access_policy: str = "rbac",
    backup_enabled: bool = True,
    backup_frequency_hours: int = 24,
    retention_days: int = 365,
    custom_fields: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Create a vault template with the specified parameters.
    
    Args:
        name: Name of the vault template
        description: Description of the vault template
        owner_id: Owner identifier
        encryption_algorithm: Encryption algorithm to use
        trust_level: Trust level (low, medium, high)
        access_policy: Access policy type (rbac, abac, hybrid)
        backup_enabled: Whether backups are enabled
        backup_frequency_hours: Backup frequency in hours
        retention_days: Data retention period in days
        custom_fields: Additional custom fields
        
    Returns:
        Dictionary representing the vault template
    """
    template = {
        "template_id": f"template_{int(datetime.now().timestamp())}",
        "name": name,
        "description": description,
        "version": "1.0.0",
        "created_at": datetime.now().isoformat(),
        "owner_id": owner_id,
        "encryption": {
            "algorithm": encryption_algorithm,
            "key_derivation": "PBKDF2-SHA256",
            "key_length": 256
        },
        "trust": {
            "level": trust_level,
            "verification_required": trust_level in ["medium", "high"],
            "multi_factor_auth": trust_level == "high"
        },
        "access_control": {
            "policy_type": access_policy,
            "audit_logging": True,
            "session_timeout_minutes": 30
        },
        "backup": {
            "enabled": backup_enabled,
            "frequency_hours": backup_frequency_hours,
            "retention_days": retention_days,
            "encryption": True
        },
        "compliance": {
            "gdpr_compliant": True,
            "hipaa_compliant": trust_level == "high",
            "soc2_compliant": trust_level in ["medium", "high"]
        },
        "custom_fields": custom_fields or {}
    }
    
    return template


def save_template(template: Dict[str, Any], output_file: str) -> None:
    """
    Save the template to a JSON file.
    
    Args:
        template: The template dictionary
        output_file: Output file path
    """
    with open(output_file, 'w') as f:
        json.dump(template, f, indent=2)
    
    print(f"Vault template saved to {output_file}")


def main():
    """Main function for the create_vault_template script"""
    parser = argparse.ArgumentParser(description="Create a new vault template")
    parser.add_argument("name", help="Name of the vault template")
    parser.add_argument("-d", "--description", default="", help="Description of the vault template")
    parser.add_argument("-o", "--output", help="Output file path (default: <name>.template.json)")
    parser.add_argument("--owner", default="enterprise-client", help="Owner identifier")
    parser.add_argument("--encryption", default="AES-GCM-256", help="Encryption algorithm")
    parser.add_argument("--trust", choices=["low", "medium", "high"], default="medium", help="Trust level")
    parser.add_argument("--policy", choices=["rbac", "abac", "hybrid"], default="rbac", help="Access policy type")
    parser.add_argument("--no-backup", action="store_true", help="Disable backups")
    parser.add_argument("--backup-freq", type=int, default=24, help="Backup frequency in hours")
    parser.add_argument("--retention", type=int, default=365, help="Retention period in days")
    
    args = parser.parse_args()
    
    # Create the template
    template = create_vault_template(
        name=args.name,
        description=args.description,
        owner_id=args.owner,
        encryption_algorithm=args.encryption,
        trust_level=args.trust,
        access_policy=args.policy,
        backup_enabled=not args.no_backup,
        backup_frequency_hours=args.backup_freq,
        retention_days=args.retention
    )
    
    # Determine output file name
    output_file = args.output or f"{args.name.lower().replace(' ', '_')}.template.json"
    
    # Save the template
    save_template(template, output_file)
    
    # Print summary
    print(f"\nCreated vault template: {args.name}")
    print(f"Trust level: {template['trust']['level']}")
    print(f"Encryption: {template['encryption']['algorithm']}")
    print(f"Backups: {'Enabled' if template['backup']['enabled'] else 'Disabled'}")
    print(f"Compliance: GDPR{' + HIPAA' if template['compliance']['hipaa_compliant'] else ''}{' + SOC2' if template['compliance']['soc2_compliant'] else ''}")


if __name__ == "__main__":
    main()