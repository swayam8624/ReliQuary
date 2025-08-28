"""
FastAPI Application Package for ReliQuary

This package contains all components of the FastAPI web application,
including endpoints, services, middleware, and schemas.
"""

# Import main application components
from .main import (
    app,
    get_app,
    configure_middleware,
    configure_routes,
    configure_exception_handlers
)

# Import core services
from .services.context_verifier import (
    ContextVerificationService,
    ContextVerificationRequest,
    ContextVerificationResponse
)

from .services.trust_engine import (
    TrustEngineService,
    TrustEvaluationRequest,
    TrustEvaluationResponse
)

from .services.agent_orchestrator import (
    AgentOrchestrationService,
    OrchestrationRequest,
    OrchestrationResponse
)

from .services.rule_enforcer import (
    RuleEnforcementService,
    RuleEvaluationRequest,
    RuleEvaluationResponse
)

from .services.encryptor import (
    EncryptionService,
    EncryptionRequest,
    EncryptionResponse,
    DecryptionRequest,
    DecryptionResponse
)

# Import middleware
from .middleware.logging import (
    StructuredLoggingMiddleware,
    RequestLoggingMiddleware
)

__all__ = [
    # Main application
    "app",
    "get_app",
    "configure_middleware",
    "configure_routes",
    "configure_exception_handlers",
    
    # Services
    "ContextVerificationService",
    "ContextVerificationRequest",
    "ContextVerificationResponse",
    
    "TrustEngineService",
    "TrustEvaluationRequest",
    "TrustEvaluationResponse",
    
    "AgentOrchestrationService",
    "OrchestrationRequest",
    "OrchestrationResponse",
    
    "RuleEnforcementService",
    "RuleEvaluationRequest",
    "RuleEvaluationResponse",
    
    "EncryptionService",
    "EncryptionRequest",
    "EncryptionResponse",
    "DecryptionRequest",
    "DecryptionResponse",
    
    # Middleware
    "StructuredLoggingMiddleware",
    "RequestLoggingMiddleware"
]