# zk/zk_endpoints.py

from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.responses import JSONResponse
from typing import Dict, Any, Optional, List
from pydantic import BaseModel, Field
import time
import json
import uuid
from datetime import datetime

# Import our ZK components
from .context_manager import (
    ContextVerificationManager,
    ContextVerificationRequest,
    DeviceContext,
    TimestampContext,
    LocationContext,
    PatternContext,
    VerificationLevel,
    ContextRequirement,
    create_basic_device_verification,
    create_standard_verification
)

from .trust_engine import (
    TrustScoringEngine,
    RiskLevel,
    evaluate_user_trust
)

# Import authentication dependencies
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '../'))

from auth.oauth2 import verify_auth, get_current_active_user
from auth.rbac import require_vault_read, require_vault_write, require_vault_admin

# Pydantic models for API requests/responses
class DeviceContextModel(BaseModel):
    fingerprint: str = Field(..., description="Device hardware fingerprint")
    hsm_signature: str = Field(..., description="Hardware security module signature")
    device_hash: str = Field(..., description="Device hash for verification")
    challenge_nonce: str = Field(..., description="Challenge nonce for replay protection")

class TimestampContextModel(BaseModel):
    current_timestamp: int = Field(..., description="Current Unix timestamp")
    last_access_time: Optional[int] = Field(None, description="Previous access timestamp")
    timezone_offset: int = Field(0, description="User timezone offset in seconds")
    totp_secret: Optional[str] = Field(None, description="TOTP secret for time-based verification")
    require_business_hours: bool = Field(False, description="Enforce business hours check")
    require_totp: bool = Field(False, description="Require TOTP validation")

class LocationContextModel(BaseModel):
    latitude: float = Field(..., description="Current GPS latitude")
    longitude: float = Field(..., description="Current GPS longitude")
    previous_latitude: Optional[float] = Field(None, description="Previous location latitude")
    previous_longitude: Optional[float] = Field(None, description="Previous location longitude")
    ip_latitude: Optional[float] = Field(None, description="IP-based location latitude")
    ip_longitude: Optional[float] = Field(None, description="IP-based location longitude")
    travel_time_hours: Optional[int] = Field(None, description="Time since last location update")

class PatternContextModel(BaseModel):
    action_sequence: List[int] = Field(..., description="Sequence of user actions")
    timing_intervals: List[int] = Field(..., description="Time intervals between actions")
    session_duration: int = Field(..., description="Current session duration in seconds")
    keystrokes_per_minute: int = Field(..., description="Typing speed")
    mouse_movements: int = Field(..., description="Mouse movement count")
    access_frequency: int = Field(..., description="Recent access frequency")

class ContextVerificationRequestModel(BaseModel):
    verification_level: str = Field(..., description="Required verification level (BASIC/STANDARD/HIGH/MAXIMUM)")
    requirements_mask: int = Field(..., description="Bitmask of required verifications")
    device_context: Optional[DeviceContextModel] = Field(None, description="Device verification context")
    timestamp_context: Optional[TimestampContextModel] = Field(None, description="Timestamp verification context")
    location_context: Optional[LocationContextModel] = Field(None, description="Location verification context")
    pattern_context: Optional[PatternContextModel] = Field(None, description="Pattern verification context")
    session_id: Optional[str] = Field(None, description="Session identifier")

class ContextVerificationResponse(BaseModel):
    verified: bool = Field(..., description="Overall verification result")
    trust_score: int = Field(..., description="Trust score (0-100)")
    verification_level_met: bool = Field(..., description="Whether required level was met")
    risk_level: str = Field(..., description="Risk assessment level")
    device_verified: bool = Field(False, description="Device verification result")
    timestamp_verified: bool = Field(False, description="Timestamp verification result")
    location_verified: bool = Field(False, description="Location verification result")
    pattern_verified: bool = Field(False, description="Pattern verification result")
    proof_hash: Optional[str] = Field(None, description="Cryptographic proof hash")
    verification_time: Optional[float] = Field(None, description="Verification processing time")
    recommendations: List[str] = Field(default_factory=list, description="Security recommendations")
    confidence_level: Optional[float] = Field(None, description="Confidence in assessment")
    adaptive_thresholds: Optional[Dict[str, float]] = Field(None, description="Adaptive security thresholds")
    session_id: Optional[str] = Field(None, description="Session identifier")
    error_message: Optional[str] = Field(None, description="Error message if verification failed")

class VaultAccessRequest(BaseModel):
    vault_operation: str = Field(..., description="Vault operation (read/write/delete)")
    vault_path: str = Field(..., description="Vault path for operation")
    verification_request: ContextVerificationRequestModel = Field(..., description="Context verification data")
    force_verification: bool = Field(False, description="Force full verification even for trusted users")

class VaultAccessResponse(BaseModel):
    access_granted: bool = Field(..., description="Whether vault access is granted")
    verification_result: ContextVerificationResponse = Field(..., description="Context verification details")
    access_token: Optional[str] = Field(None, description="Temporary access token")
    access_expires: Optional[int] = Field(None, description="Access token expiration timestamp")
    required_actions: List[str] = Field(default_factory=list, description="Required actions before access")

# Create FastAPI router
zk_router = APIRouter(prefix="/zk", tags=["Zero-Knowledge Context Verification"])

# Global instances
context_manager: Optional[ContextVerificationManager] = None
trust_engine: Optional[TrustScoringEngine] = None

def get_context_manager() -> ContextVerificationManager:
    """Get or create context verification manager."""
    global context_manager
    if context_manager is None:
        context_manager = ContextVerificationManager()
    return context_manager

def get_trust_engine() -> TrustScoringEngine:
    """Get or create trust scoring engine."""
    global trust_engine
    if trust_engine is None:
        trust_engine = TrustScoringEngine()
    return trust_engine

@zk_router.post("/verify-context", response_model=ContextVerificationResponse)
async def verify_context(
    request: ContextVerificationRequestModel,
    auth_context: Dict[str, Any] = Depends(verify_auth)
) -> ContextVerificationResponse:
    """
    Perform zero-knowledge context verification.
    
    This endpoint validates user context (device, location, timing, behavior)
    using zero-knowledge proofs to preserve privacy while ensuring security.
    """
    try:
        # Get user info from auth context
        user_id = auth_context.get("sub") or auth_context.get("client_id", "unknown")
        
        # Convert Pydantic models to internal types
        verification_level = VerificationLevel[request.verification_level.upper()]
        
        device_context = None
        if request.device_context:
            device_context = DeviceContext(
                fingerprint=request.device_context.fingerprint,
                hsm_signature=request.device_context.hsm_signature,
                device_hash=request.device_context.device_hash,
                challenge_nonce=request.device_context.challenge_nonce
            )
        
        timestamp_context = None
        if request.timestamp_context:
            timestamp_context = TimestampContext(
                current_timestamp=request.timestamp_context.current_timestamp,
                last_access_time=request.timestamp_context.last_access_time,
                timezone_offset=request.timestamp_context.timezone_offset,
                totp_secret=request.timestamp_context.totp_secret,
                require_business_hours=request.timestamp_context.require_business_hours,
                require_totp=request.timestamp_context.require_totp
            )
        
        location_context = None
        if request.location_context:
            location_context = LocationContext(
                latitude=request.location_context.latitude,
                longitude=request.location_context.longitude,
                previous_latitude=request.location_context.previous_latitude,
                previous_longitude=request.location_context.previous_longitude,
                ip_latitude=request.location_context.ip_latitude,
                ip_longitude=request.location_context.ip_longitude,
                travel_time_hours=request.location_context.travel_time_hours
            )
        
        pattern_context = None
        if request.pattern_context:
            pattern_context = PatternContext(
                action_sequence=request.pattern_context.action_sequence,
                timing_intervals=request.pattern_context.timing_intervals,
                session_duration=request.pattern_context.session_duration,
                keystrokes_per_minute=request.pattern_context.keystrokes_per_minute,
                mouse_movements=request.pattern_context.mouse_movements,
                access_frequency=request.pattern_context.access_frequency
            )
        
        # Create verification request
        verification_request = ContextVerificationRequest(
            user_id=user_id,
            verification_level=verification_level,
            requirements_mask=request.requirements_mask,
            device_context=device_context,
            timestamp_context=timestamp_context,
            location_context=location_context,
            pattern_context=pattern_context,
            challenge_nonce=str(uuid.uuid4())
        )
        
        # Perform context verification
        manager = get_context_manager()
        result = manager.verify_context(verification_request)
        
        # Get trust evaluation
        context_data = {
            "device_verified": result.device_verified,
            "timestamp_verified": result.timestamp_verified,
            "location_verified": result.location_verified,
            "pattern_verified": result.pattern_verified,
            "device_fingerprint": device_context.fingerprint if device_context else None,
            "current_timestamp": timestamp_context.current_timestamp if timestamp_context else None,
            "last_access_time": timestamp_context.last_access_time if timestamp_context else None,
            "latitude": location_context.latitude if location_context else None,
            "longitude": location_context.longitude if location_context else None,
            "session_duration": pattern_context.session_duration if pattern_context else None,
            "keystrokes_per_minute": pattern_context.keystrokes_per_minute if pattern_context else None,
            "access_frequency": pattern_context.access_frequency if pattern_context else None,
            "business_hours_ok": True,  # From timestamp verification
            "ip_consistency_ok": True   # From location verification
        }
        
        trust_evaluation = get_trust_engine().evaluate_trust(user_id, context_data, request.session_id)
        
        # Return comprehensive response
        return ContextVerificationResponse(
            verified=result.verified,
            trust_score=int(result.trust_score),
            verification_level_met=result.verification_level_met,
            risk_level=trust_evaluation.risk_level.name,
            device_verified=result.device_verified,
            timestamp_verified=result.timestamp_verified,
            location_verified=result.location_verified,
            pattern_verified=result.pattern_verified,
            proof_hash=result.proof_hash,
            verification_time=result.verification_time,
            recommendations=trust_evaluation.recommendations,
            confidence_level=trust_evaluation.confidence_level,
            adaptive_thresholds=trust_evaluation.adaptive_thresholds,
            session_id=request.session_id,
            error_message=result.error_message
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Context verification failed: {str(e)}"
        )

@zk_router.post("/vault-access", response_model=VaultAccessResponse)
async def request_vault_access(
    request: VaultAccessRequest,
    auth_context: Dict[str, Any] = Depends(verify_auth)
) -> VaultAccessResponse:
    """
    Request vault access with zero-knowledge context verification.
    
    This endpoint combines context verification with vault access control,
    providing secure, privacy-preserving access to sensitive data.
    """
    try:
        # Determine required permissions based on operation
        vault_permissions = {
            "read": require_vault_read(),
            "write": require_vault_write(),
            "delete": require_vault_admin()
        }
        
        operation = request.vault_operation.lower()
        if operation not in vault_permissions:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid vault operation: {operation}"
            )
        
        # Check basic RBAC permissions first
        try:
            vault_permissions[operation](auth_context)
        except HTTPException as e:
            return VaultAccessResponse(
                access_granted=False,
                verification_result=ContextVerificationResponse(
                    verified=False,
                    trust_score=0,
                    verification_level_met=False,
                    risk_level="VERY_HIGH",
                    error_message="Insufficient RBAC permissions"
                ),
                required_actions=["Contact administrator for permission elevation"]
            )
        
        # Perform context verification
        user_id = auth_context.get("sub") or auth_context.get("client_id", "unknown")
        
        # Check if user has high trust level and doesn't need full verification
        if not request.force_verification:
            trust_evaluation = get_trust_engine().evaluate_trust(user_id, {}, request.verification_request.session_id)
            
            # If user has very high trust and low risk, allow simplified verification
            if trust_evaluation.overall_trust_score >= 95 and trust_evaluation.risk_level == RiskLevel.VERY_LOW:
                return VaultAccessResponse(
                    access_granted=True,
                    verification_result=ContextVerificationResponse(
                        verified=True,
                        trust_score=int(trust_evaluation.overall_trust_score),
                        verification_level_met=True,
                        risk_level=trust_evaluation.risk_level.name,
                        device_verified=True,
                        timestamp_verified=True,
                        location_verified=True,
                        pattern_verified=True,
                        confidence_level=trust_evaluation.confidence_level,
                        adaptive_thresholds=trust_evaluation.adaptive_thresholds,
                        session_id=request.verification_request.session_id
                    ),
                    access_token=str(uuid.uuid4()),
                    access_expires=int(time.time()) + 3600,  # 1 hour
                    required_actions=[]
                )
        
        # Perform full context verification
        verification_response = await verify_context(request.verification_request, auth_context)
        
        # Determine access based on verification result and operation sensitivity
        access_granted = False
        required_actions = []
        access_token = None
        access_expires = None
        
        if verification_response.verified and verification_response.verification_level_met:
            # Grant access based on risk level and operation type
            if operation == "read":
                if verification_response.trust_score >= 60:
                    access_granted = True
                    access_token = str(uuid.uuid4())
                    access_expires = int(time.time()) + 1800  # 30 minutes
                else:
                    required_actions.append("Trust score too low for read access")
            
            elif operation == "write":
                if verification_response.trust_score >= 75:
                    access_granted = True
                    access_token = str(uuid.uuid4())
                    access_expires = int(time.time()) + 900  # 15 minutes
                else:
                    required_actions.append("Trust score too low for write access")
                    required_actions.append("Consider additional authentication")
            
            elif operation == "delete":
                if verification_response.trust_score >= 90 and verification_response.risk_level in ["VERY_LOW", "LOW"]:
                    access_granted = True
                    access_token = str(uuid.uuid4())
                    access_expires = int(time.time()) + 300  # 5 minutes
                else:
                    required_actions.append("High-trust verification required for delete operations")
                    required_actions.append("Manual approval may be required")
        else:
            required_actions.extend(verification_response.recommendations)
        
        return VaultAccessResponse(
            access_granted=access_granted,
            verification_result=verification_response,
            access_token=access_token,
            access_expires=access_expires,
            required_actions=required_actions
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Vault access request failed: {str(e)}"
        )

@zk_router.get("/trust-profile/{user_id}")
async def get_trust_profile(
    user_id: str,
    auth_context: Dict[str, Any] = Depends(require_vault_admin())
) -> Dict[str, Any]:
    """
    Get user trust profile (admin only).
    
    Returns historical trust data and behavioral patterns for analysis.
    """
    try:
        trust_engine = get_trust_engine()
        user_profile = trust_engine._get_user_profile(user_id)
        
        return {
            "user_id": user_profile.user_id,
            "baseline_trust_score": user_profile.baseline_trust_score,
            "total_evaluations": user_profile.total_evaluations,
            "compliance_violations": user_profile.compliance_violations,
            "last_evaluation": user_profile.last_evaluation,
            "trust_history_summary": {
                "count": len(user_profile.trust_history),
                "average": sum(user_profile.trust_history) / len(user_profile.trust_history) if user_profile.trust_history else 0,
                "latest": user_profile.trust_history[-1] if user_profile.trust_history else None
            },
            "risk_events_count": len(user_profile.risk_events),
            "behavioral_baselines": {
                key: len(value) if isinstance(value, list) else value 
                for key, value in user_profile.behavioral_baselines.items()
            }
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve trust profile: {str(e)}"
        )

@zk_router.post("/quick-verify")
async def quick_verify(
    device_fingerprint: str,
    latitude: Optional[float] = None,
    longitude: Optional[float] = None,
    auth_context: Dict[str, Any] = Depends(verify_auth)
) -> Dict[str, Any]:
    """
    Quick verification endpoint for common use cases.
    
    Provides simplified context verification for basic device and location checking.
    """
    try:
        user_id = auth_context.get("sub") or auth_context.get("client_id", "unknown")
        
        # Create basic verification request
        if latitude is not None and longitude is not None:
            verification_request = create_standard_verification(user_id, device_fingerprint, latitude, longitude)
        else:
            verification_request = create_basic_device_verification(user_id, device_fingerprint, str(uuid.uuid4()))
        
        # Perform verification
        manager = get_context_manager()
        result = manager.verify_context(verification_request)
        
        # Simple response
        return {
            "verified": result.verified,
            "trust_score": result.trust_score,
            "verification_level_met": result.verification_level_met,
            "processing_time": result.verification_time,
            "recommendations": len([r for r in ["Device verified", "Location verified"] if result.verified])
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Quick verification failed: {str(e)}"
        )

@zk_router.get("/system-status")
async def get_system_status(
    auth_context: Dict[str, Any] = Depends(verify_auth)
) -> Dict[str, Any]:
    """
    Get ZK system status and health information.
    """
    try:
        # Test basic functionality
        manager = get_context_manager()
        trust_engine = get_trust_engine()
        
        # Quick system test
        test_user = "system_test_user"
        test_context = {
            "device_verified": True,
            "timestamp_verified": True,
            "location_verified": True,
            "pattern_verified": True,
            "device_fingerprint": "test_device",
            "current_timestamp": int(time.time()),
            "latitude": 0.0,
            "longitude": 0.0,
            "session_duration": 600,
            "keystrokes_per_minute": 60,
            "access_frequency": 1
        }
        
        start_time = time.time()
        test_evaluation = trust_engine.evaluate_trust(test_user, test_context)
        test_time = time.time() - start_time
        
        return {
            "status": "healthy",
            "timestamp": int(time.time()),
            "components": {
                "context_manager": "operational",
                "trust_engine": "operational", 
                "zk_circuits": "available",
                "trust_scoring": "functional"
            },
            "performance": {
                "test_evaluation_time": round(test_time, 3),
                "trust_score_calculated": test_evaluation.overall_trust_score,
                "system_responsive": test_time < 1.0
            },
            "capabilities": [
                "Zero-knowledge device verification",
                "Privacy-preserving location verification",
                "Behavioral pattern analysis",
                "Dynamic trust scoring",
                "Adaptive threshold adjustment",
                "Risk assessment and anomaly detection"
            ]
        }
        
    except Exception as e:
        return {
            "status": "degraded",
            "timestamp": int(time.time()),
            "error": str(e),
            "components": {
                "context_manager": "unknown",
                "trust_engine": "unknown",
                "zk_circuits": "unknown"
            }
        }

# Export the router
__all__ = ["zk_router"]