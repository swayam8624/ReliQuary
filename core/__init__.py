"""
Core Package for ReliQuary

This package contains the fundamental components of the ReliQuary system,
including cryptography, utilities, constants, and core services.
"""

# Import core components
from .constants import (
    DEFAULT_TRUST_THRESHOLD,
    DEFAULT_CONSENSUS_THRESHOLD,
    MAX_CONCURRENT_TASKS,
    DEFAULT_TIMEOUT,
    ENCRYPTION_KEY_LENGTH,
    HASH_ALGORITHM,
    LOGGING_FORMAT,
    AUDIT_LOG_LEVEL,
    TRUST_DECAY_RATE,
    MAX_TRUST_SCORE,
    MIN_TRUST_SCORE
)

# Import utility functions
from .utils import (
    generate_device_fingerprint,
    verify_device_fingerprint,
    get_device_info,
    secure_delete_file,
    calculate_file_hash,
    safe_read_file,
    ensure_directory_exists,
    get_current_timestamp,
    timestamp_to_iso,
    get_time_range,
    is_within_time_window
)

# Import core services
from .audit import (
    AuditTrailManager
)

from .metrics import (
    MetricsCollector,
    get_metrics_collector,
    increment_counter,
    set_gauge,
    observe_histogram,
    SystemMetrics
)

__all__ = [
    # Constants
    "DEFAULT_TRUST_THRESHOLD",
    "DEFAULT_CONSENSUS_THRESHOLD",
    "MAX_CONCURRENT_TASKS",
    "DEFAULT_TIMEOUT",
    "ENCRYPTION_KEY_LENGTH",
    "HASH_ALGORITHM",
    "LOGGING_FORMAT",
    "AUDIT_LOG_LEVEL",
    "TRUST_DECAY_RATE",
    "MAX_TRUST_SCORE",
    "MIN_TRUST_SCORE",
    
    # Device fingerprint utilities
    "generate_device_fingerprint",
    "verify_device_fingerprint",
    "get_device_info",
    
    # File utilities
    "secure_delete_file",
    "calculate_file_hash",
    "safe_read_file",
    "ensure_directory_exists",
    
    # Time utilities
    "get_current_timestamp",
    "timestamp_to_iso",
    "get_time_range",
    "is_within_time_window",
    
    # Audit services
    "AuditTrailManager",
    
    # Metrics services
    "MetricsCollector",
    "get_metrics_collector",
    "increment_counter",
    "set_gauge",
    "observe_histogram",
    "SystemMetrics"
]