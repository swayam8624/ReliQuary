"""
Context Schemas for ReliQuary FastAPI

This module defines Pydantic schemas for context-related data structures
used in the FastAPI application.
"""

from typing import List, Dict, Any, Optional
from enum import Enum
from pydantic import BaseModel, Field
from datetime import datetime


class VerificationLevel(str, Enum):
    """Context verification levels"""
    BASIC = "basic"
    STANDARD = "standard"
    HIGH = "high"
    MAXIMUM = "maximum"


class ContextRequirement(int, Enum):
    """Context verification requirements"""
    DEVICE = 1
    TIMESTAMP = 2
    LOCATION = 4
    PATTERN = 8


class ContextVerificationRequest(BaseModel):
    """Request model for context verification"""
    request_id: str = Field(..., description="Unique request identifier")
    user_id: str = Field(..., description="User identifier")
    context_data: Dict[str, Any] = Field(..., description="Context data to verify")
    verification_level: VerificationLevel = Field(default=VerificationLevel.STANDARD, description="Verification level")
    required_verifications: List[str] = Field(default=["device", "timestamp"], description="Required verifications")
    timeout: int = Field(default=30, description="Verification timeout in seconds")


class ContextVerificationResult(BaseModel):
    """Context verification result"""
    verified: bool = Field(..., description="Whether context was verified")
    verification_level_met: bool = Field(..., description="Whether required verification level was met")
    device_verified: bool = Field(default=False, description="Whether device was verified")
    timestamp_verified: bool = Field(default=False, description="Whether timestamp was verified")
    location_verified: bool = Field(default=False, description="Whether location was verified")
    pattern_verified: bool = Field(default=False, description="Whether pattern was verified")
    trust_score: float = Field(..., description="Trust score from verification", ge=0.0, le=100.0)
    proof_hash: Optional[str] = Field(None, description="ZK proof hash")
    confidence_score: float = Field(..., description="Confidence score", ge=0.0, le=1.0)


class ContextVerificationResponse(BaseModel):
    """Response model for context verification"""
    request_id: str = Field(..., description="Request identifier")
    result: ContextVerificationResult = Field(..., description="Verification result")
    processing_time: float = Field(..., description="Processing time in seconds")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Response timestamp")


class DeviceContext(BaseModel):
    """Device context information"""
    fingerprint: str = Field(..., description="Device fingerprint")
    challenge_nonce: str = Field(..., description="Challenge nonce for verification")
    device_type: Optional[str] = Field(None, description="Device type")
    os_info: Optional[str] = Field(None, description="Operating system information")
    browser_info: Optional[str] = Field(None, description="Browser information")


class TimestampContext(BaseModel):
    """Timestamp context information"""
    current_timestamp: int = Field(..., description="Current timestamp")
    last_access_time: Optional[int] = Field(None, description="Last access timestamp")
    timezone_offset: int = Field(default=0, description="Timezone offset in seconds")
    require_business_hours: bool = Field(default=False, description="Whether business hours are required")
    require_totp: bool = Field(default=False, description="Whether TOTP is required")


class LocationContext(BaseModel):
    """Location context information"""
    latitude: float = Field(..., description="Latitude")
    longitude: float = Field(..., description="Longitude")
    previous_latitude: Optional[float] = Field(None, description="Previous latitude")
    previous_longitude: Optional[float] = Field(None, description="Previous longitude")
    ip_latitude: Optional[float] = Field(None, description="IP-based latitude")
    ip_longitude: Optional[float] = Field(None, description="IP-based longitude")
    travel_time_hours: Optional[float] = Field(None, description="Travel time in hours")


class PatternContext(BaseModel):
    """Pattern context information"""
    action_sequence: List[int] = Field(default_factory=lambda: [1, 2, 3], description="Action sequence")
    timing_intervals: List[int] = Field(default_factory=lambda: [100, 150, 120], description="Timing intervals")
    session_duration: int = Field(default=1800, description="Session duration in seconds")
    keystrokes_per_minute: int = Field(default=60, description="Keystrokes per minute")
    mouse_movements: int = Field(default=100, description="Mouse movements")
    access_frequency: int = Field(default=1, description="Access frequency")


class BatchContextVerificationRequest(BaseModel):
    """Request model for batch context verification"""
    batch_id: str = Field(..., description="Batch identifier")
    contexts: List[ContextVerificationRequest] = Field(..., description="List of context verification requests")
    timeout: int = Field(default=60, description="Batch timeout in seconds")


class BatchContextVerificationResponse(BaseModel):
    """Response model for batch context verification"""
    batch_id: str = Field(..., description="Batch identifier")
    results: List[ContextVerificationResponse] = Field(..., description="List of verification results")
    successful_verifications: int = Field(..., description="Number of successful verifications")
    failed_verifications: int = Field(..., description="Number of failed verifications")
    processing_time: float = Field(..., description="Total processing time in seconds")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Response timestamp")