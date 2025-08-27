"""
Context Checker Tool for ReliQuary Multi-Agent System

This tool allows agents to verify and validate context information including
device fingerprints, location data, timestamps, and behavioral patterns.
It integrates with the ZK proof system to ensure privacy-preserving verification.
"""

import logging
import time
import hashlib
import json
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

# Import ZK and trust components
from zk.context_manager import (
    ContextVerificationManager, 
    ContextVerificationRequest,
    DeviceContext,
    TimestampContext,
    LocationContext,
    PatternContext,
    VerificationLevel,
    ContextRequirement
)
from zk.trust_engine import TrustScoringEngine, RiskLevel


class ContextCheckResult(Enum):
    """Results of context verification"""
    VERIFIED = "verified"
    PARTIAL = "partial"
    FAILED = "failed"
    ERROR = "error"
    INSUFFICIENT_DATA = "insufficient_data"


@dataclass
class ContextCheckResponse:
    """Response from context verification check"""
    result: ContextCheckResult
    confidence_score: float
    verification_details: Dict[str, Any]
    privacy_preserved: bool
    proof_hash: Optional[str]
    trust_impact: float
    risk_factors: List[str]
    access_factors: List[str]
    processing_time: float
    error_message: Optional[str] = None


class ContextChecker:
    """
    Context Checker Tool for multi-agent context verification.
    
    This tool provides agents with the ability to verify context information
    using zero-knowledge proofs while maintaining privacy. It supports multiple
    verification types and integrates with the trust scoring system.
    """
    
    def __init__(self):
        """Initialize the context checker tool."""
        self.context_manager = ContextVerificationManager()
        self.trust_engine = TrustScoringEngine()
        self.logger = logging.getLogger("context_checker")
        
        # Verification thresholds
        self.verification_thresholds = {
            VerificationLevel.BASIC: 0.6,
            VerificationLevel.STANDARD: 0.75,
            VerificationLevel.HIGH: 0.85,
            VerificationLevel.MAXIMUM: 0.95
        }
        
        # Performance metrics
        self.total_checks = 0
        self.successful_checks = 0
        self.failed_checks = 0
        self.average_processing_time = 0.0
    
    async def verify_context(self, 
                           user_id: str,
                           context_data: Dict[str, Any],
                           verification_level: str = "standard",
                           required_verifications: List[str] = None) -> ContextCheckResponse:
        """
        Verify context data with zero-knowledge proofs.
        
        Args:
            user_id: User identifier for the context
            context_data: Context information to verify
            verification_level: Level of verification required
            required_verifications: Specific verifications to perform
            
        Returns:
            ContextCheckResponse with verification results
        """
        start_time = time.time()
        self.total_checks += 1
        
        try:
            # Parse verification level
            try:
                level = VerificationLevel[verification_level.upper()]
            except KeyError:
                level = VerificationLevel.STANDARD
            
            # Determine required verifications
            if required_verifications is None:
                required_verifications = ["device", "timestamp"]
            
            # Build requirements mask
            requirements_mask = 0
            for req in required_verifications:
                if req == "device":
                    requirements_mask |= ContextRequirement.DEVICE.value
                elif req == "timestamp":
                    requirements_mask |= ContextRequirement.TIMESTAMP.value
                elif req == "location":
                    requirements_mask |= ContextRequirement.LOCATION.value
                elif req == "pattern":
                    requirements_mask |= ContextRequirement.PATTERN.value
            
            # Create context objects
            device_context = self._create_device_context(context_data)
            timestamp_context = self._create_timestamp_context(context_data)
            location_context = self._create_location_context(context_data)
            pattern_context = self._create_pattern_context(context_data)
            
            # Create verification request
            verification_request = ContextVerificationRequest(
                user_id=user_id,
                verification_level=level,
                requirements_mask=requirements_mask,
                device_context=device_context,
                timestamp_context=timestamp_context,
                location_context=location_context,
                pattern_context=pattern_context,
                challenge_nonce=self._generate_challenge_nonce()
            )
            
            # Perform verification
            result = self.context_manager.verify_context(verification_request)
            
            # Determine verification result
            if result.verified and result.verification_level_met:
                check_result = ContextCheckResult.VERIFIED
            elif result.verified:
                check_result = ContextCheckResult.PARTIAL
            else:
                check_result = ContextCheckResult.FAILED
            
            # Calculate confidence score
            confidence = self._calculate_confidence_score(result)
            
            # Assess trust impact
            trust_impact = self._assess_trust_impact(result, context_data)
            
            # Extract risk and access factors
            risk_factors, access_factors = self._extract_factors(result, context_data)
            
            processing_time = time.time() - start_time
            self.average_processing_time = (
                (self.average_processing_time * (self.total_checks - 1) + processing_time) / 
                self.total_checks
            )
            
            if check_result == ContextCheckResult.VERIFIED:
                self.successful_checks += 1
            else:
                self.failed_checks += 1
            
            return ContextCheckResponse(
                result=check_result,
                confidence_score=confidence,
                verification_details={
                    "device_verified": result.device_verified,
                    "timestamp_verified": result.timestamp_verified,
                    "location_verified": result.location_verified,
                    "pattern_verified": result.pattern_verified,
                    "trust_score": result.trust_score,
                    "verification_level": level.value,
                    "requirements_met": result.verification_level_met
                },
                privacy_preserved=True,  # ZK proofs preserve privacy
                proof_hash=result.proof_hash,
                trust_impact=trust_impact,
                risk_factors=risk_factors,
                access_factors=access_factors,
                processing_time=processing_time
            )
            
        except Exception as e:
            self.logger.error(f"Context verification failed: {e}")
            self.failed_checks += 1
            
            processing_time = time.time() - start_time
            return ContextCheckResponse(
                result=ContextCheckResult.ERROR,
                confidence_score=0.0,
                verification_details={},
                privacy_preserved=False,
                proof_hash=None,
                trust_impact=-10.0,  # Negative impact for errors
                risk_factors=["Verification system error"],
                access_factors=[],
                processing_time=processing_time,
                error_message=str(e)
            )
    
    def _create_device_context(self, context_data: Dict[str, Any]) -> Optional[DeviceContext]:
        """Create device context from context data."""
        if "device_fingerprint" in context_data:
            return DeviceContext(
                fingerprint=context_data["device_fingerprint"],
                challenge_nonce=context_data.get("challenge_nonce", self._generate_challenge_nonce())
            )
        return None
    
    def _create_timestamp_context(self, context_data: Dict[str, Any]) -> Optional[TimestampContext]:
        """Create timestamp context from context data."""
        if "current_timestamp" in context_data or "timestamp" in context_data:
            current_timestamp = context_data.get("current_timestamp", 
                                               context_data.get("timestamp", int(time.time())))
            
            return TimestampContext(
                current_timestamp=int(current_timestamp),
                last_access_time=context_data.get("last_access_time"),
                timezone_offset=context_data.get("timezone_offset", 0),
                require_business_hours=context_data.get("require_business_hours", False),
                require_totp=context_data.get("require_totp", False)
            )
        return None
    
    def _create_location_context(self, context_data: Dict[str, Any]) -> Optional[LocationContext]:
        """Create location context from context data."""
        if "latitude" in context_data and "longitude" in context_data:
            return LocationContext(
                latitude=float(context_data["latitude"]),
                longitude=float(context_data["longitude"]),
                previous_latitude=context_data.get("previous_latitude"),
                previous_longitude=context_data.get("previous_longitude"),
                ip_latitude=context_data.get("ip_latitude"),
                ip_longitude=context_data.get("ip_longitude"),
                travel_time_hours=context_data.get("travel_time_hours")
            )
        return None
    
    def _create_pattern_context(self, context_data: Dict[str, Any]) -> Optional[PatternContext]:
        """Create pattern context from context data."""
        if "keystrokes_per_minute" in context_data:
            return PatternContext(
                action_sequence=context_data.get("action_sequence", [1, 2, 3]),
                timing_intervals=context_data.get("timing_intervals", [100, 150, 120]),
                session_duration=context_data.get("session_duration", 1800),
                keystrokes_per_minute=int(context_data["keystrokes_per_minute"]),
                mouse_movements=context_data.get("mouse_movements", 100),
                access_frequency=context_data.get("access_frequency", 1)
            )
        return None
    
    def _generate_challenge_nonce(self) -> str:
        """Generate a cryptographic challenge nonce."""
        return hashlib.sha256(f"{time.time()}{id(self)}".encode()).hexdigest()[:16]
    
    def _calculate_confidence_score(self, result) -> float:
        """Calculate confidence score based on verification results."""
        base_score = result.trust_score / 100.0
        
        # Boost for successful verifications
        verification_boost = 0
        if result.device_verified:
            verification_boost += 0.2
        if result.timestamp_verified:
            verification_boost += 0.15
        if result.location_verified:
            verification_boost += 0.15
        if result.pattern_verified:
            verification_boost += 0.1
        
        # Penalty for failed verifications
        verification_penalty = 0
        if not result.device_verified:
            verification_penalty += 0.2
        if not result.timestamp_verified:
            verification_penalty += 0.1
        
        confidence = base_score + verification_boost - verification_penalty
        return max(0.0, min(1.0, confidence))
    
    def _assess_trust_impact(self, result, context_data: Dict[str, Any]) -> float:
        """Assess impact on trust score based on verification results."""
        impact = 0.0
        
        # Positive impact for successful verifications
        if result.device_verified:
            impact += 2.0
        if result.timestamp_verified:
            impact += 1.5
        if result.location_verified:
            impact += 1.5
        if result.pattern_verified:
            impact += 1.0
        
        # Negative impact for failures
        if not result.device_verified:
            impact -= 3.0
        if not result.timestamp_verified:
            impact -= 1.0
        
        # Consider context factors
        if context_data.get("access_frequency", 1) > 10:
            impact -= 1.0
        
        if context_data.get("keystrokes_per_minute", 60) > 200:
            impact -= 2.0
        
        return impact
    
    def _extract_factors(self, result, context_data: Dict[str, Any]) -> Tuple[List[str], List[str]]:
        """Extract risk and access factors from verification results."""
        risk_factors = []
        access_factors = []
        
        # Device factors
        if result.device_verified:
            access_factors.append("Device verified")
        else:
            risk_factors.append("Device verification failed")
        
        # Timestamp factors
        if result.timestamp_verified:
            access_factors.append("Timestamp valid")
        else:
            risk_factors.append("Invalid timestamp")
        
        # Location factors
        if result.location_verified:
            access_factors.append("Location verified")
        else:
            risk_factors.append("Location suspicious")
        
        # Pattern factors
        if result.pattern_verified:
            access_factors.append("Behavioral pattern normal")
        else:
            risk_factors.append("Anomalous behavior pattern")
        
        # Context-based factors
        kpm = context_data.get("keystrokes_per_minute", 60)
        if kpm > 200 or kpm < 10:
            risk_factors.append("Unusual typing speed")
        elif 40 <= kpm <= 120:
            access_factors.append("Normal typing speed")
        
        access_freq = context_data.get("access_frequency", 1)
        if access_freq > 15:
            risk_factors.append("Excessive access frequency")
        elif 1 <= access_freq <= 5:
            access_factors.append("Normal access frequency")
        
        return risk_factors, access_factors
    
    async def quick_device_check(self, device_fingerprint: str, challenge_nonce: str = None) -> Dict[str, Any]:
        """Perform a quick device verification check."""
        if challenge_nonce is None:
            challenge_nonce = self._generate_challenge_nonce()
        
        context_data = {
            "device_fingerprint": device_fingerprint,
            "challenge_nonce": challenge_nonce
        }
        
        response = await self.verify_context(
            user_id="quick_check",
            context_data=context_data,
            verification_level="basic",
            required_verifications=["device"]
        )
        
        return {
            "verified": response.result == ContextCheckResult.VERIFIED,
            "confidence": response.confidence_score,
            "proof_hash": response.proof_hash,
            "processing_time": response.processing_time
        }
    
    async def batch_verify_contexts(self, contexts: List[Dict[str, Any]]) -> List[ContextCheckResponse]:
        """Verify multiple contexts in batch."""
        results = []
        
        for i, context_req in enumerate(contexts):
            user_id = context_req.get("user_id", f"batch_user_{i}")
            context_data = context_req.get("context_data", {})
            verification_level = context_req.get("verification_level", "standard")
            required_verifications = context_req.get("required_verifications")
            
            result = await self.verify_context(
                user_id=user_id,
                context_data=context_data,
                verification_level=verification_level,
                required_verifications=required_verifications
            )
            
            results.append(result)
        
        return results
    
    def get_checker_metrics(self) -> Dict[str, Any]:
        """Get context checker performance metrics."""
        success_rate = (self.successful_checks / max(self.total_checks, 1)) * 100
        
        return {
            "total_checks": self.total_checks,
            "successful_checks": self.successful_checks,
            "failed_checks": self.failed_checks,
            "success_rate": success_rate,
            "average_processing_time": self.average_processing_time,
            "throughput": self.total_checks / max(self.average_processing_time * self.total_checks, 1)
        }
    
    def reset_metrics(self):
        """Reset performance metrics."""
        self.total_checks = 0
        self.successful_checks = 0
        self.failed_checks = 0
        self.average_processing_time = 0.0