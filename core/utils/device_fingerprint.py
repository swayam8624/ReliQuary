"""
Device fingerprinting utility for ReliQuary platform.
Provides functions to generate and verify device fingerprints for context-aware security.
"""

import hashlib
import platform
import uuid
import json
from typing import Dict, Any, Optional


def generate_device_fingerprint() -> str:
    """
    Generate a unique device fingerprint based on hardware and software characteristics.
    
    Returns:
        str: A SHA-256 hash representing the device fingerprint
    """
    # Collect device information
    device_info = {
        "machine_id": _get_machine_id(),
        "platform": platform.platform(),
        "architecture": platform.machine(),
        "processor": platform.processor(),
        "system": platform.system(),
        "release": platform.release(),
        "hostname": platform.node(),
    }
    
    # Create a JSON string of the device information
    device_string = json.dumps(device_info, sort_keys=True)
    
    # Generate SHA-256 hash
    fingerprint = hashlib.sha256(device_string.encode('utf-8')).hexdigest()
    
    return fingerprint


def _get_machine_id() -> str:
    """
    Get a unique machine identifier.
    
    Returns:
        str: A unique identifier for the machine
    """
    try:
        # Try to get machine ID from /etc/machine-id (Linux)
        with open('/etc/machine-id', 'r') as f:
            return f.read().strip()
    except (FileNotFoundError, PermissionError):
        try:
            # Try to get machine ID from /etc/hostid (some Unix systems)
            with open('/etc/hostid', 'rb') as f:
                return f.read().hex()
        except (FileNotFoundError, PermissionError):
            # Fallback to UUID-based approach
            return str(uuid.getnode())


def verify_device_fingerprint(fingerprint: str) -> bool:
    """
    Verify if the provided fingerprint matches the current device.
    
    Args:
        fingerprint (str): The fingerprint to verify
        
    Returns:
        bool: True if the fingerprint matches, False otherwise
    """
    current_fingerprint = generate_device_fingerprint()
    return current_fingerprint == fingerprint


def get_device_info() -> Dict[str, Any]:
    """
    Get detailed information about the current device.
    
    Returns:
        Dict[str, Any]: A dictionary containing device information
    """
    return {
        "fingerprint": generate_device_fingerprint(),
        "platform": platform.platform(),
        "architecture": platform.machine(),
        "processor": platform.processor(),
        "system": platform.system(),
        "release": platform.release(),
        "hostname": platform.node(),
        "machine_id": _get_machine_id(),
    }


def compare_device_fingerprints(fingerprint1: str, fingerprint2: str) -> bool:
    """
    Compare two device fingerprints.
    
    Args:
        fingerprint1 (str): First fingerprint to compare
        fingerprint2 (str): Second fingerprint to compare
        
    Returns:
        bool: True if fingerprints match, False otherwise
    """
    return fingerprint1 == fingerprint2


def is_trusted_device(fingerprint: str, trusted_devices: list) -> bool:
    """
    Check if a device fingerprint is in the list of trusted devices.
    
    Args:
        fingerprint (str): The fingerprint to check
        trusted_devices (list): List of trusted device fingerprints
        
    Returns:
        bool: True if the device is trusted, False otherwise
    """
    return fingerprint in trusted_devices


# Example usage
if __name__ == "__main__":
    # Generate a device fingerprint
    fingerprint = generate_device_fingerprint()
    print(f"Device fingerprint: {fingerprint}")
    
    # Get detailed device information
    info = get_device_info()
    print(f"Device info: {info}")
    
    # Verify the fingerprint
    is_valid = verify_device_fingerprint(fingerprint)
    print(f"Fingerprint verification: {'Valid' if is_valid else 'Invalid'}")