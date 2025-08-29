"""
Core Constants for ReliQuary

This module defines the fundamental constants used throughout the ReliQuary system.
"""

# Trust and consensus thresholds
DEFAULT_TRUST_THRESHOLD = 0.7
DEFAULT_CONSENSUS_THRESHOLD = 0.8

# System performance constants
MAX_CONCURRENT_TASKS = 100
DEFAULT_TIMEOUT = 30  # seconds

# Cryptographic constants
ENCRYPTION_KEY_LENGTH = 32  # 256 bits
HASH_ALGORITHM = "sha3_256"

# Logging constants
LOGGING_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
AUDIT_LOG_LEVEL = "INFO"

# Trust scoring constants
TRUST_DECAY_RATE = 0.01  # 1% per day
MAX_TRUST_SCORE = 100.0
MIN_TRUST_SCORE = 0.0

# Vault constants
VAULT_NAME_MAX_LENGTH = 100
SECRET_KEY_MAX_LENGTH = 50
SECRET_VALUE_MAX_LENGTH = 10000

# API constants
API_VERSION = "v1"
DEFAULT_PAGE_SIZE = 50
MAX_PAGE_SIZE = 1000

# Merkle tree constants
MERKLE_TREE_MAX_DEPTH = 32
MERKLE_HASH_ALGORITHM = "sha3_256"

# ZK proof constants
ZK_PROOF_DEFAULT_TIMEOUT = 60  # seconds