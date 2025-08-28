"""
Trust Schemas for ReliQuary FastAPI

This module defines Pydantic schemas for trust-related data structures
used in the FastAPI application.
"""

from typing import List, Dict, Any, Optional
from enum import Enum
from pydantic import BaseModel, Field
from datetime import datetime


class RiskLevel(str, Enum):
    """Risk assessment levels"""
    VERY_LOW = "very_low"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    VERY_HIGH = "very_high"


class TrustFactor(BaseModel):
    """Individual trust factor"""
    name: str = Field(..., description="Factor name")
    weight: float = Field(..., description="Factor weight", ge=0.0, le=1.0)
    score: float = Field(..., description="Factor score", ge=0.0, le=100.0)
    impact: float = Field(..., description="Factor impact on overall trust", ge=-100.0, le=100.0)


class TrustEvaluationRequest(BaseModel):
    """Request model for trust evaluation"""
    request_id: str = Field(..., description="Unique request identifier")
    user_id: str = Field(..., description="User identifier")
    context_data: Dict[str, Any] = Field(..., description="Context data for evaluation")
    include_analysis: bool = Field(default=True, description="Whether to include detailed analysis")
    update_profile: bool = Field(default=True, description="Whether to update user profile")
    timeout: int = Field(default=30, description="Evaluation timeout in seconds")


class TrustEvaluation(BaseModel):
    """Trust evaluation result"""
    overall_trust_score: float = Field(..., description="Overall trust score", ge=0.0, le=100.0)
    risk_level: RiskLevel = Field(..., description="Risk assessment level")
    confidence_score: float = Field(..., description="Confidence in evaluation", ge=0.0, le=1.0)
    trust_factors: List[TrustFactor] = Field(default_factory=list, description="Individual trust factors")
    historical_scores: List[float] = Field(default_factory=list, description="Historical trust scores")
    last_updated: datetime = Field(..., description="Last update timestamp")


class TrustEvaluationResponse(BaseModel):
    """Response model for trust evaluation"""
    request_id: str = Field(..., description="Request identifier")
    user_id: str = Field(..., description="User identifier")
    evaluation: TrustEvaluation = Field(..., description="Trust evaluation result")
    processing_time: float = Field(..., description="Processing time in seconds")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Response timestamp")


class UserTrustProfile(BaseModel):
    """User trust profile"""
    user_id: str = Field(..., description="User identifier")
    current_trust_score: float = Field(..., description="Current trust score", ge=0.0, le=100.0)
    risk_level: RiskLevel = Field(..., description="Current risk level")
    historical_scores: List[float] = Field(default_factory=list, description="Historical trust scores")
    trust_factors: List[TrustFactor] = Field(default_factory=list, description="Current trust factors")
    created_at: datetime = Field(..., description="Profile creation timestamp")
    last_updated: datetime = Field(..., description="Last update timestamp")
    total_evaluations: int = Field(default=0, description="Total number of evaluations")


class TrustProfileResponse(BaseModel):
    """Response model for trust profile retrieval"""
    user_id: str = Field(..., description="User identifier")
    profile: Optional[UserTrustProfile] = Field(None, description="User trust profile")
    found: bool = Field(..., description="Whether profile was found")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Response timestamp")


class TrustHistoryRequest(BaseModel):
    """Request model for trust history"""
    user_id: str = Field(..., description="User identifier")
    limit: int = Field(default=50, description="Maximum number of history records to return")
    start_time: Optional[datetime] = Field(None, description="Start time for history query")
    end_time: Optional[datetime] = Field(None, description="End time for history query")


class TrustHistoryResponse(BaseModel):
    """Response model for trust history"""
    user_id: str = Field(..., description="User identifier")
    history: List[TrustEvaluation] = Field(..., description="Trust evaluation history")
    total_records: int = Field(..., description="Total number of records")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Response timestamp")


class TrustRule(BaseModel):
    """Trust rule configuration"""
    rule_id: str = Field(..., description="Unique rule identifier")
    name: str = Field(..., description="Rule name")
    description: str = Field(..., description="Rule description")
    condition: str = Field(..., description="Rule condition (JSONLogic or similar)")
    weight: float = Field(..., description="Rule weight", ge=0.0, le=1.0)
    enabled: bool = Field(default=True, description="Whether rule is enabled")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Rule creation timestamp")


class TrustRulesResponse(BaseModel):
    """Response model for trust rules"""
    rules: List[TrustRule] = Field(..., description="List of trust rules")
    total_count: int = Field(..., description="Total number of rules")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Response timestamp")


class TrustScoreUpdate(BaseModel):
    """Trust score update notification"""
    user_id: str = Field(..., description="User identifier")
    old_score: float = Field(..., description="Previous trust score", ge=0.0, le=100.0)
    new_score: float = Field(..., description="New trust score", ge=0.0, le=100.0)
    change_amount: float = Field(..., description="Score change amount")
    reason: str = Field(..., description="Reason for score change")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Update timestamp")