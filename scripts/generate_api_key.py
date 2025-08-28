#!/usr/bin/env python3
"""
Utility to generate API keys for enterprise clients.
This script generates secure API keys for authenticating with the ReliQuary API.
"""

import argparse
import secrets
import string
import json
import sys
from datetime import datetime, timedelta
from typing import Dict, Any, Optional


def generate_api_key(length: int = 32) -> str:
    """
    Generate a secure API key.
    
    Args:
        length: Length of the API key (default: 32)
        
    Returns:
        Generated API key string
    """
    alphabet = string.ascii_letters + string.digits
    return ''.join(secrets.choice(alphabet) for _ in range(length))


def generate_api_key_record(
    client_name: str,
    client_id: Optional[str] = None,
    permissions: Optional[list] = None,
    expires_in_days: Optional[int] = None,
    description: str = ""
) -> Dict[str, Any]:
    """
    Generate a complete API key record.
    
    Args:
        client_name: Name of the client
        client_id: Client identifier (auto-generated if not provided)
        permissions: List of permissions for this API key
        expires_in_days: Number of days until expiration (None for no expiration)
        description: Description of the API key's purpose
        
    Returns:
        Dictionary containing the API key record
    """
    if client_id is None:
        client_id = f"client_{secrets.token_hex(8)}"
    
    if permissions is None:
        permissions = ["read", "write"]
    
    api_key = generate_api_key()
    
    record = {
        "client_id": client_id,
        "client_name": client_name,
        "api_key": api_key,
        "created_at": datetime.now().isoformat(),
        "permissions": permissions,
        "description": description
    }
    
    if expires_in_days is not None:
        expiration_date = datetime.now() + timedelta(days=expires_in_days)
        record["expires_at"] = expiration_date.isoformat()
    
    return record


def save_api_key_record(record: Dict[str, Any], output_file: str) -> None:
    """
    Save the API key record to a JSON file.
    
    Args:
        record: The API key record dictionary
        output_file: Output file path
    """
    with open(output_file, 'w') as f:
        json.dump(record, f, indent=2)
    
    print(f"API key record saved to {output_file}")


def main():
    """Main function for the generate_api_key script"""
    parser = argparse.ArgumentParser(description="Generate API key for enterprise clients")
    parser.add_argument("client_name", help="Name of the client")
    parser.add_argument("-o", "--output", help="Output file path (default: <client_name>.api_key.json)")
    parser.add_argument("-i", "--client-id", help="Client identifier (auto-generated if not provided)")
    parser.add_argument("-p", "--permissions", nargs="+", default=["read", "write"],
                        help="Permissions for this API key (default: read write)")
    parser.add_argument("-e", "--expires", type=int, help="Expiration in days (default: no expiration)")
    parser.add_argument("-d", "--description", default="", help="Description of the API key's purpose")
    parser.add_argument("-q", "--quiet", action="store_true", help="Quiet mode (only output the API key)")
    
    args = parser.parse_args()
    
    # Generate the API key record
    record = generate_api_key_record(
        client_name=args.client_name,
        client_id=args.client_id,
        permissions=args.permissions,
        expires_in_days=args.expires,
        description=args.description
    )
    
    if args.quiet:
        print(record["api_key"])
        return
    
    # Determine output file name
    output_file = args.output or f"{args.client_name.lower().replace(' ', '_')}.api_key.json"
    
    # Save the record
    save_api_key_record(record, output_file)
    
    # Print summary
    print(f"\nGenerated API key for: {args.client_name}")
    print(f"Client ID: {record['client_id']}")
    print(f"Permissions: {', '.join(record['permissions'])}")
    if "expires_at" in record:
        print(f"Expires: {record['expires_at']}")
    else:
        print("Expires: Never")
    
    if args.description:
        print(f"Description: {args.description}")
    
    print(f"\nAPI Key: {record['api_key']}")
    print("\n⚠️  IMPORTANT: Store this API key securely. It will not be shown again!")


if __name__ == "__main__":
    main()