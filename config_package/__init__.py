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

# Enhanced RBAC Configuration
ENHANCED_RBAC_ENABLED = True
RBAC_AUDIT_ENABLED = True
RBAC_CACHE_TTL = 300  # 5 minutes

# Enhanced RBAC Role Mappings (for migration from legacy system)
LEGACY_ROLE_MAPPINGS = {
    "vault:admin": "vault_admin",
    "vault:read": "vault_readonly", 
    "auditor": "auditor",
    "admin": "system_admin",
    "user": "vault_user",
    "readonly": "vault_readonly"
}

RELIQUARY_RP_ID = "localhost"
RELIQUARY_RP_ORIGIN = f"https://{RELIQUARY_RP_ID}:8000"

def get_config():
    """Get configuration as a dictionary."""
    return {
        "api_version": API_VERSION,
        "encryption": {
            "default_algorithm": DEFAULT_ENCRYPTION_ALGORITHM,
            "aes_gcm_key_len": AES_GCM_KEY_LEN,
            "aes_gcm_nonce_len": AES_GCM_NONCE_LEN
        },
        "pqc": {
            "kem_algorithm": DEFAULT_PQC_KEM_ALGORITHM,
            "signature_algorithm": DEFAULT_PQC_SIGNATURE_ALGORITHM
        },
        "trust": {
            "default_threshold": DEFAULT_TRUST_THRESHOLD,
            "weights_file": TRUST_WEIGHTS_FILE,
            "templates_file": VAULT_TRUST_TEMPLATES_FILE
        },
        "agents": {
            "neutral": AGENT_NEUTRAL,
            "permissive": AGENT_PERMISSIVE,
            "strict": AGENT_STRICT,
            "watchdog": AGENT_WATCHDOG
        },
        "storage": {
            "vault_path": VAULT_STORAGE_PATH_LOCAL,
            "audit_log_path": AUDIT_LOG_FILE_PATH_LOCAL
        },
        "webauthn": {
            "rp_id": RELIQUARY_RP_ID,
            "rp_origin": RELIQUARY_RP_ORIGIN
        }
    }

