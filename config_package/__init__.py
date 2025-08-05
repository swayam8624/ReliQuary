# config.py

API_VERSION = "v1"
DEFAULT_ENCRYPTION_ALGORITHM = "AES_GCM_256"
DEFAULT_PQC_KEM_ALGORITHM = "Kyber768"
DEFAULT_PQC_SIGNATURE_ALGORITHM = "Falcon512"
DEFAULT_MERKLE_HASH_ALGORITHM = "SHA256"

# AES-GCM specific constants
AES_GCM_KEY_LEN = 32  # 256 bits for AES-256-GCM
AES_GCM_NONCE_LEN = 12 # 96 bits for AES-GCM

# Trust Engine Defaults
DEFAULT_TRUST_THRESHOLD = 70 # Out of 100
TRUST_WEIGHTS_FILE = "config/trust_defaults.json" # This refers to config/trust_defaults.json
VAULT_TRUST_TEMPLATES_FILE = "config/vault_trust_templates.yaml" # This refers to config/vault_trust_templates.yaml

# Agent Names
AGENT_NEUTRAL = "NeutralAgent"
AGENT_PERMISSIVE = "PermissiveAgent"
AGENT_STRICT = "StrictAgent"
AGENT_WATCHDOG = "WatchdogAgent"

# File Paths (relative to project root or Docker working dir)
VAULT_STORAGE_PATH_LOCAL = "vaults/data" # For local storage backend
AUDIT_LOG_FILE_PATH_LOCAL = "audit_logs/reliquary.log"


# ===============================
# Phase 2: Security Configuration
# ===============================
# A dictionary to store API keys and their associated roles.
# In a real-world application, this would be a secure database or a secrets manager.
API_KEYS = {
    # Hashed API keys for security
    "59cdd0deecfa63907936a609e4322855694bf373ef4d076bd4a880f0834a7f8f": {"client_name": "VaultAdmin-Client", "roles": ["vault:admin", "auditor"]},
    "049c8490c79252b7ef8ad5b4255e4c0f619e8a2a5d9367d2567e1427c1e0657c": {"client_name": "ReadOnly-Client", "roles": ["vault:read"]}
}

# The RBAC matrix defines which roles have access to which permissions.
# This will be used by our RoleChecker dependency.
RBAC_MATRIX = {
    "vault:admin": ["vault:create", "vault:read", "vault:update", "vault:delete"],
    "vault:read": ["vault:read"],
    "auditor": ["audit:read"]
}

RELIQUARY_RP_ID = "localhost"
RELIQUARY_RP_ORIGIN = f"https://{RELIQUARY_RP_ID}:8000"

