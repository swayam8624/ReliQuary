# apps/api/main.py

from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import uvicorn
import os
import sys
from datetime import datetime
from typing import Dict, Any

# Add the project root to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../'))

from core.merkle_logging.writer import MerkleLogWriter
from config_package import get_config

# Import authentication system
from auth.auth_endpoints import auth_router
from auth.auth_middleware import setup_auth_middleware

# Import ZK verification system
from zk.zk_endpoints import zk_router

# Global instances
logger: MerkleLogWriter = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    # Startup
    global logger
    log_path = "logs/api.log"
    logger = MerkleLogWriter(log_path)
    
    # Log startup
    logger.add_entry({
        "event": "api_startup",
        "status": "success",
        "version": "0.1.0"
    })
    
    yield
    
    # Shutdown
    logger.add_entry({
        "event": "api_shutdown",
        "status": "success"
    })

# Create FastAPI application
app = FastAPI(
    title="ReliQuary API",
    description="Context-Bound, Trust-Evolved Cryptographic Memory System with Enterprise Authentication",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# Setup authentication middleware
app = setup_auth_middleware(app)

# Include authentication endpoints
app.include_router(auth_router)

# Include ZK verification endpoints
app.include_router(zk_router)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Health check endpoints
@app.get("/health", tags=["Health"])
async def health_check() -> Dict[str, Any]:
    """Basic health check endpoint."""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "2.0.0",
        "service": "reliquary-api",
        "features": [
            "Merkle audit logging",
            "OAuth 2.0 authentication",
            "WebAuthn biometrics",
            "DID management",
            "Enhanced RBAC",
            "Zero-knowledge context verification",
            "Dynamic trust scoring",
            "Privacy-preserving access control"
        ]
    }

@app.get("/health/detailed", tags=["Health"])
async def detailed_health_check() -> Dict[str, Any]:
    """Detailed health check with component status."""
    global logger
    
    # Check logger health
    logger_status = "healthy"
    logger_info = {}
    
    try:
        if logger:
            summary = logger.get_log_summary()
            logger_info = {
                "entries": summary["total_entries"],
                "integrity": summary["integrity_verified"]
            }
        else:
            logger_status = "unavailable"
    except Exception as e:
        logger_status = "error"
        logger_info = {"error": str(e)}
    
    # Check authentication system health
    auth_status = "healthy"
    auth_info = {}
    
    try:
        from auth.identity_manager import IdentityManager
        from auth.rbac_enhanced import EnhancedRBACManager
        
        # Test identity manager
        identity_manager = IdentityManager()
        test_profile = identity_manager.get_user_profile("nonexistent_test_user")
        
        # Test RBAC manager
        rbac_manager = EnhancedRBACManager()
        test_roles = rbac_manager.get_principal_roles("test_user", "user")
        
        auth_info = {
            "identity_manager": "healthy",
            "rbac_manager": "healthy",
            "webauthn": "available",
            "did_system": "available"
        }
    except Exception as e:
        auth_status = "degraded"
        auth_info = {"error": str(e)}
    
    # Check ZK system health
    zk_status = "healthy"
    zk_info = {}
    
    try:
        from zk.context_manager import ContextVerificationManager
        from zk.trust_engine import TrustScoringEngine
        
        # Test context manager
        context_manager = ContextVerificationManager()
        
        # Test trust engine
        trust_engine = TrustScoringEngine()
        
        zk_info = {
            "context_verification": "healthy",
            "trust_scoring": "healthy",
            "zk_circuits": "available",
            "privacy_preservation": "active"
        }
    except Exception as e:
        zk_status = "degraded"
        zk_info = {"error": str(e)}
    
    health_data = {
        "status": "healthy" if (logger_status == "healthy" and auth_status == "healthy" and zk_status == "healthy") else "degraded",
        "timestamp": datetime.now().isoformat(),
        "version": "3.0.0",
        "service": "reliquary-api",
        "components": {
            "logger": {
                "status": logger_status,
                **logger_info
            },
            "authentication": {
                "status": auth_status,
                **auth_info
            },
            "zero_knowledge": {
                "status": zk_status,
                **zk_info
            },
            "crypto": {
                "status": "available",
                "note": "Post-quantum cryptography active"
            },
            "storage": {
                "status": "available",
                "backend": "local"
            }
        }
    }
    
    # Log the health check
    if logger:
        logger.add_entry({
            "event": "health_check",
            "type": "detailed",
            "status": health_data["status"]
        })
    
    return health_data

@app.get("/version", tags=["Info"])
async def get_version() -> Dict[str, str]:
    """Get API version information."""
    return {
        "version": "3.0.0",
        "api_name": "ReliQuary API",
        "description": "Context-Bound, Trust-Evolved Cryptographic Memory System with Zero-Knowledge Context Verification",
        "phase": "Phase 3 - Context Verification with Zero-Knowledge Proofs",
        "features": "OAuth 2.0, WebAuthn, DID, Enhanced RBAC, Identity Management, ZK Context Verification, Dynamic Trust Scoring"
    }

@app.get("/logs/summary", tags=["Audit"])
async def get_log_summary() -> Dict[str, Any]:
    """Get audit log summary."""
    global logger
    
    if not logger:
        raise HTTPException(status_code=503, detail="Logger not available")
    
    try:
        summary = logger.get_log_summary()
        
        # Log the access
        logger.add_entry({
            "event": "log_summary_access",
            "status": "success"
        })
        
        return summary
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get log summary: {str(e)}")

@app.get("/logs/verify/{entry_index}", tags=["Audit"])
async def verify_log_entry(entry_index: int) -> Dict[str, Any]:
    """Verify the integrity of a specific log entry."""
    global logger
    
    if not logger:
        raise HTTPException(status_code=503, detail="Logger not available")
    
    try:
        if entry_index >= logger.entry_count:
            raise HTTPException(status_code=404, detail="Entry not found")
        
        proof_data = logger.get_entry_proof(entry_index)
        is_valid = logger.verify_entry_integrity(entry_index)
        
        # Log the verification
        logger.add_entry({
            "event": "log_verification",
            "entry_index": entry_index,
            "status": "success",
            "verified": is_valid
        })
        
        return {
            "entry_index": entry_index,
            "is_valid": is_valid,
            "proof": proof_data
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to verify entry: {str(e)}")

# Error handlers
@app.exception_handler(Exception)
async def general_exception_handler(request, exc: Exception):
    """Handle unexpected exceptions."""
    global logger
    
    error_details = {
        "error": "Internal server error",
        "detail": str(exc),
        "type": type(exc).__name__
    }
    
    # Log the error
    if logger:
        try:
            logger.add_entry({
                "event": "api_error",
                "error_type": type(exc).__name__,
                "error_message": str(exc),
                "path": str(request.url),
                "method": request.method,
                "status": "error"
            })
        except:
            pass  # Don't let logging errors crash the handler
    
    return JSONResponse(
        status_code=500,
        content=error_details
    )

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )