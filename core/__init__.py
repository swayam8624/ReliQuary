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
from .utils.device_fingerprint import (
    generate_device_fingerprint,
    validate_device_fingerprint,
    extract_device_features
)

from .utils.file_utils import (
    secure_delete_file,
    calculate_file_hash,
    verify_file_integrity,
    create_secure_temp_file
)

from .utils.time_utils import (
    get_current_timestamp,
    format_timestamp,
    calculate_time_difference,
    is_within_time_window
)

# Import core services
from .audit import (
    AuditLogger,
    AuditEvent,
    AuditLevel
)

from .metrics import (
    MetricsCollector,
    MetricType,
    CounterMetric,
    GaugeMetric,
    HistogramMetric
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
    "validate_device_fingerprint",
    "extract_device_features",
    
    # File utilities
    "secure_delete_file",
    "calculate_file_hash",
    "verify_file_integrity",
    "create_secure_temp_file",
    
    # Time utilities
    "get_current_timestamp",
    "format_timestamp",
    "calculate_time_difference",
    "is_within_time_window",
    
    # Audit services
    "AuditLogger",
    "AuditEvent",
    "AuditLevel",
    
    # Metrics services
    "MetricsCollector",
    "MetricType",
    "CounterMetric",
    "GaugeMetric",
    "HistogramMetric"
]