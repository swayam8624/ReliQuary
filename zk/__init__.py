"""
Zero-Knowledge Proofs Package for ReliQuary

This package contains all components related to Zero-Knowledge proofs,
including circuits, verifiers, and context verification systems.
"""

# Import core ZK components
from .context_manager import (
    ContextVerificationManager,
    ContextVerificationRequest,
    ContextVerificationResponse,
    DeviceContext,
    TimestampContext,
    LocationContext,
    PatternContext,
    VerificationLevel,
    ContextRequirement
)

from .trust_engine import (
    TrustScoringEngine,
    TrustEvaluation,
    RiskLevel,
    UserTrustProfile,
    TrustFactor
)

# Import verifier components
from .verifier.zk_runner import (
    ZKProofRunner,
    ProofGenerationResult,
    ProofVerificationResult
)

from .verifier.zk_batch_verifier import (
    ZKBatchVerifier,
    BatchVerificationResult
)

__all__ = [
    # Context verification
    "ContextVerificationManager",
    "ContextVerificationRequest",
    "ContextVerificationResponse",
    "DeviceContext",
    "TimestampContext",
    "LocationContext",
    "PatternContext",
    "VerificationLevel",
    "ContextRequirement",
    
    # Trust engine
    "TrustScoringEngine",
    "TrustEvaluation",
    "RiskLevel",
    "UserTrustProfile",
    "TrustFactor",
    
    # ZK proof runner
    "ZKProofRunner",
    "ProofGenerationResult",
    "ProofVerificationResult",
    
    # ZK batch verifier
    "ZKBatchVerifier",
    "BatchVerificationResult"
]