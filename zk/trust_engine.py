# zk/trust_engine.py

import json
import time
import math
import statistics
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
import logging
from datetime import datetime, timedelta
import hashlib

# Import our components
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '../'))

from core.merkle_logging.writer import MerkleLogWriter

class TrustFactor(Enum):
    """Individual trust factors for evaluation"""
    DEVICE_CONSISTENCY = "device_consistency"
    TEMPORAL_PATTERNS = "temporal_patterns"
    GEOGRAPHIC_CONSISTENCY = "geographic_consistency"
    BEHAVIORAL_PATTERNS = "behavioral_patterns"
    ACCESS_FREQUENCY = "access_frequency"
    RISK_INDICATORS = "risk_indicators"
    COMPLIANCE_SCORE = "compliance_score"
    HISTORICAL_RELIABILITY = "historical_reliability"

class RiskLevel(Enum):
    """Risk levels for trust evaluation"""
    VERY_LOW = 1
    LOW = 2
    MEDIUM = 3
    HIGH = 4
    VERY_HIGH = 5

@dataclass
class TrustMetrics:
    """Individual trust metrics"""
    device_consistency: float = 0.0
    temporal_patterns: float = 0.0
    geographic_consistency: float = 0.0
    behavioral_patterns: float = 0.0
    access_frequency: float = 0.0
    risk_indicators: float = 0.0
    compliance_score: float = 0.0
    historical_reliability: float = 0.0

@dataclass
class TrustEvaluation:
    """Complete trust evaluation result"""
    user_id: str
    overall_trust_score: float
    risk_level: RiskLevel
    trust_metrics: TrustMetrics
    confidence_level: float
    adaptive_thresholds: Dict[str, float]
    recommendations: List[str]
    evaluation_timestamp: int
    session_id: Optional[str] = None

@dataclass
class UserTrustProfile:
    """User's trust profile with historical data"""
    user_id: str
    baseline_trust_score: float
    trust_history: List[float]
    behavioral_baselines: Dict[str, float]
    risk_events: List[Dict[str, Any]]
    last_evaluation: Optional[int] = None
    total_evaluations: int = 0
    compliance_violations: int = 0
    
class TrustScoringEngine:
    """
    Advanced Trust Scoring Engine with Dynamic Evaluation.
    
    This engine provides:
    - Dynamic trust scoring based on multiple factors
    - Machine learning-based pattern recognition
    - Adaptive thresholds based on user behavior
    - Risk assessment and anomaly detection
    - Historical trend analysis
    - Compliance monitoring
    """
    
    def __init__(self, data_path: str = None):
        """
        Initialize the trust scoring engine.
        
        Args:
            data_path: Path to store trust profiles and historical data
        """
        if data_path is None:
            data_path = Path(__file__).parent / "trust_data"
        
        self.data_path = Path(data_path)
        self.data_path.mkdir(exist_ok=True)
        
        # Initialize logging
        self.logger = logging.getLogger(__name__)
        
        # Initialize audit logging
        try:
            self.audit_logger = MerkleLogWriter("logs/trust_scoring.log")
        except Exception as e:
            self.logger.warning(f"Could not initialize audit logging: {e}")
            self.audit_logger = None
        
        # Trust factor weights (can be dynamically adjusted)
        self.trust_weights = {
            TrustFactor.DEVICE_CONSISTENCY: 0.20,
            TrustFactor.TEMPORAL_PATTERNS: 0.15,
            TrustFactor.GEOGRAPHIC_CONSISTENCY: 0.15,
            TrustFactor.BEHAVIORAL_PATTERNS: 0.20,
            TrustFactor.ACCESS_FREQUENCY: 0.10,
            TrustFactor.RISK_INDICATORS: 0.10,
            TrustFactor.COMPLIANCE_SCORE: 0.05,
            TrustFactor.HISTORICAL_RELIABILITY: 0.05
        }
        
        # Default trust thresholds
        self.default_thresholds = {
            "very_low_risk": 90.0,
            "low_risk": 75.0,
            "medium_risk": 60.0,
            "high_risk": 40.0,
            "very_high_risk": 20.0
        }
        
        # Load existing user profiles
        self.user_profiles: Dict[str, UserTrustProfile] = {}
        self._load_user_profiles()
    
    def evaluate_trust(self, user_id: str, context_data: Dict[str, Any], 
                      session_id: Optional[str] = None) -> TrustEvaluation:
        """
        Perform comprehensive trust evaluation for a user.
        
        Args:
            user_id: User identifier
            context_data: Context verification data and results
            session_id: Optional session identifier
            
        Returns:
            TrustEvaluation with complete trust assessment
        """
        start_time = time.time()
        
        try:
            # Get or create user profile
            user_profile = self._get_user_profile(user_id)
            
            # Calculate individual trust metrics
            trust_metrics = self._calculate_trust_metrics(user_id, context_data, user_profile)
            
            # Calculate overall trust score
            overall_score = self._calculate_overall_trust_score(trust_metrics)
            
            # Determine risk level
            risk_level = self._determine_risk_level(overall_score, trust_metrics)
            
            # Calculate confidence level
            confidence = self._calculate_confidence_level(user_profile, trust_metrics)
            
            # Get adaptive thresholds
            adaptive_thresholds = self._get_adaptive_thresholds(user_profile)
            
            # Generate recommendations
            recommendations = self._generate_recommendations(trust_metrics, risk_level, user_profile)
            
            # Create evaluation result
            evaluation = TrustEvaluation(
                user_id=user_id,
                overall_trust_score=overall_score,
                risk_level=risk_level,
                trust_metrics=trust_metrics,
                confidence_level=confidence,
                adaptive_thresholds=adaptive_thresholds,
                recommendations=recommendations,
                evaluation_timestamp=int(time.time()),
                session_id=session_id
            )
            
            # Update user profile
            self._update_user_profile(user_profile, evaluation, context_data)
            
            # Log the evaluation
            self._log_trust_evaluation(evaluation, time.time() - start_time)
            
            return evaluation
            
        except Exception as e:
            self.logger.error(f"Trust evaluation failed for user {user_id}: {str(e)}")
            # Return minimal evaluation on error
            return TrustEvaluation(
                user_id=user_id,
                overall_trust_score=0.0,
                risk_level=RiskLevel.VERY_HIGH,
                trust_metrics=TrustMetrics(),
                confidence_level=0.0,
                adaptive_thresholds=self.default_thresholds,
                recommendations=["System error - manual review required"],
                evaluation_timestamp=int(time.time()),
                session_id=session_id
            )
    
    def _calculate_trust_metrics(self, user_id: str, context_data: Dict[str, Any], 
                                user_profile: UserTrustProfile) -> TrustMetrics:
        """Calculate individual trust metrics."""
        
        # Device consistency score
        device_score = self._evaluate_device_consistency(
            context_data.get("device_verified", False),
            context_data.get("device_fingerprint", ""),
            user_profile
        )
        
        # Temporal patterns score
        temporal_score = self._evaluate_temporal_patterns(
            context_data.get("timestamp_verified", False),
            context_data.get("current_timestamp", 0),
            context_data.get("last_access_time", 0),
            user_profile
        )
        
        # Geographic consistency score
        geographic_score = self._evaluate_geographic_consistency(
            context_data.get("location_verified", False),
            context_data.get("latitude", 0),
            context_data.get("longitude", 0),
            user_profile
        )
        
        # Behavioral patterns score
        behavioral_score = self._evaluate_behavioral_patterns(
            context_data.get("pattern_verified", False),
            context_data.get("session_duration", 0),
            context_data.get("keystrokes_per_minute", 0),
            user_profile
        )
        
        # Access frequency score
        frequency_score = self._evaluate_access_frequency(
            context_data.get("access_frequency", 0),
            user_profile
        )
        
        # Risk indicators score
        risk_score = self._evaluate_risk_indicators(context_data, user_profile)
        
        # Compliance score
        compliance_score = self._evaluate_compliance_score(context_data, user_profile)
        
        # Historical reliability score
        historical_score = self._evaluate_historical_reliability(user_profile)
        
        return TrustMetrics(
            device_consistency=device_score,
            temporal_patterns=temporal_score,
            geographic_consistency=geographic_score,
            behavioral_patterns=behavioral_score,
            access_frequency=frequency_score,
            risk_indicators=risk_score,
            compliance_score=compliance_score,
            historical_reliability=historical_score
        )
    
    def _evaluate_device_consistency(self, device_verified: bool, device_fingerprint: str, 
                                   user_profile: UserTrustProfile) -> float:
        """Evaluate device consistency and recognition."""
        base_score = 80.0 if device_verified else 0.0
        
        # Check if this is a known device
        if device_fingerprint:
            device_hash = hashlib.sha256(device_fingerprint.encode()).hexdigest()
            known_devices = user_profile.behavioral_baselines.get("known_devices", [])
            
            if device_hash in known_devices:
                base_score += 20.0  # Bonus for known device
            elif device_verified:
                base_score += 10.0  # Smaller bonus for new but verified device
        
        return min(base_score, 100.0)
    
    def _evaluate_temporal_patterns(self, timestamp_verified: bool, current_timestamp: int,
                                  last_access_time: int, user_profile: UserTrustProfile) -> float:
        """Evaluate temporal access patterns."""
        base_score = 70.0 if timestamp_verified else 0.0
        
        if current_timestamp and last_access_time:
            time_diff = current_timestamp - last_access_time
            
            # Evaluate access pattern consistency
            typical_intervals = user_profile.behavioral_baselines.get("typical_access_intervals", [])
            
            if typical_intervals:
                avg_interval = statistics.mean(typical_intervals)
                # Score based on how close the current interval is to typical pattern
                if avg_interval > 0:
                    deviation = abs(time_diff - avg_interval) / avg_interval
                    pattern_score = max(0, 30.0 * (1 - deviation))
                    base_score += pattern_score
        
        return min(base_score, 100.0)
    
    def _evaluate_geographic_consistency(self, location_verified: bool, latitude: float,
                                       longitude: float, user_profile: UserTrustProfile) -> float:
        """Evaluate geographic access patterns."""
        base_score = 70.0 if location_verified else 0.0
        
        if latitude and longitude:
            # Check against known locations
            known_locations = user_profile.behavioral_baselines.get("known_locations", [])
            
            if known_locations:
                # Calculate distance to nearest known location
                min_distance = float('inf')
                for known_lat, known_lon in known_locations:
                    distance = self._calculate_distance(latitude, longitude, known_lat, known_lon)
                    min_distance = min(min_distance, distance)
                
                # Score based on proximity to known locations
                if min_distance < 10:  # Within 10 km
                    base_score += 30.0
                elif min_distance < 50:  # Within 50 km
                    base_score += 20.0
                elif min_distance < 200:  # Within 200 km
                    base_score += 10.0
        
        return min(base_score, 100.0)
    
    def _evaluate_behavioral_patterns(self, pattern_verified: bool, session_duration: int,
                                    keystrokes_per_minute: int, user_profile: UserTrustProfile) -> float:
        """Evaluate behavioral consistency."""
        base_score = 70.0 if pattern_verified else 0.0
        
        # Evaluate session duration patterns
        if session_duration:
            typical_durations = user_profile.behavioral_baselines.get("typical_session_durations", [])
            if typical_durations:
                avg_duration = statistics.mean(typical_durations)
                if avg_duration > 0:
                    duration_deviation = abs(session_duration - avg_duration) / avg_duration
                    duration_score = max(0, 15.0 * (1 - duration_deviation))
                    base_score += duration_score
        
        # Evaluate typing patterns
        if keystrokes_per_minute:
            typical_typing = user_profile.behavioral_baselines.get("typical_typing_speed", [])
            if typical_typing:
                avg_typing = statistics.mean(typical_typing)
                if avg_typing > 0:
                    typing_deviation = abs(keystrokes_per_minute - avg_typing) / avg_typing
                    typing_score = max(0, 15.0 * (1 - typing_deviation))
                    base_score += typing_score
        
        return min(base_score, 100.0)
    
    def _evaluate_access_frequency(self, access_frequency: int, user_profile: UserTrustProfile) -> float:
        """Evaluate access frequency patterns."""
        # Get typical access frequency from user profile
        typical_frequency = user_profile.behavioral_baselines.get("typical_access_frequency", 5)
        
        # Score based on how close to typical frequency
        if typical_frequency > 0:
            frequency_ratio = access_frequency / typical_frequency
            if 0.5 <= frequency_ratio <= 2.0:  # Within normal range
                return 90.0
            elif 0.2 <= frequency_ratio <= 3.0:  # Slightly unusual
                return 70.0
            else:  # Very unusual
                return 40.0
        
        return 60.0  # Default for new users
    
    def _evaluate_risk_indicators(self, context_data: Dict[str, Any], 
                                user_profile: UserTrustProfile) -> float:
        """Evaluate risk indicators and anomalies."""
        risk_score = 100.0  # Start with perfect score, subtract for risks
        
        # Check for recent compliance violations
        recent_violations = sum(1 for event in user_profile.risk_events 
                              if event.get("timestamp", 0) > time.time() - 86400 * 7)  # Last 7 days
        risk_score -= recent_violations * 10.0
        
        # Check for unusual verification patterns
        verification_results = [
            context_data.get("device_verified", False),
            context_data.get("timestamp_verified", False),
            context_data.get("location_verified", False),
            context_data.get("pattern_verified", False)
        ]
        
        failed_verifications = sum(1 for v in verification_results if not v)
        risk_score -= failed_verifications * 15.0
        
        # Check for rapid access attempts
        if context_data.get("last_access_time", 0):
            time_since_last = context_data.get("current_timestamp", 0) - context_data.get("last_access_time", 0)
            if time_since_last < 60:  # Less than 1 minute
                risk_score -= 20.0
        
        return max(risk_score, 0.0)
    
    def _evaluate_compliance_score(self, context_data: Dict[str, Any], 
                                 user_profile: UserTrustProfile) -> float:
        """Evaluate compliance with security policies."""
        compliance_score = 100.0
        
        # Subtract for each compliance violation
        compliance_score -= user_profile.compliance_violations * 5.0
        
        # Check current session compliance
        if not context_data.get("business_hours_ok", True):
            compliance_score -= 10.0
        
        if not context_data.get("ip_consistency_ok", True):
            compliance_score -= 15.0
        
        return max(compliance_score, 0.0)
    
    def _evaluate_historical_reliability(self, user_profile: UserTrustProfile) -> float:
        """Evaluate historical reliability and consistency."""
        if not user_profile.trust_history:
            return 50.0  # Default for new users
        
        # Calculate average historical trust score
        avg_historical_trust = statistics.mean(user_profile.trust_history)
        
        # Calculate consistency (lower variance = higher reliability)
        if len(user_profile.trust_history) > 1:
            trust_variance = statistics.variance(user_profile.trust_history)
            consistency_score = max(0, 100.0 - trust_variance)
        else:
            consistency_score = 70.0
        
        # Combine average performance and consistency
        return (avg_historical_trust * 0.7 + consistency_score * 0.3)
    
    def _calculate_overall_trust_score(self, trust_metrics: TrustMetrics) -> float:
        """Calculate weighted overall trust score."""
        total_score = 0.0
        
        for factor, weight in self.trust_weights.items():
            metric_value = getattr(trust_metrics, factor.value, 0.0)
            total_score += metric_value * weight
        
        return min(total_score, 100.0)
    
    def _determine_risk_level(self, overall_score: float, trust_metrics: TrustMetrics) -> RiskLevel:
        """Determine risk level based on trust score and metrics."""
        if overall_score >= 90:
            return RiskLevel.VERY_LOW
        elif overall_score >= 75:
            return RiskLevel.LOW
        elif overall_score >= 60:
            return RiskLevel.MEDIUM
        elif overall_score >= 40:
            return RiskLevel.HIGH
        else:
            return RiskLevel.VERY_HIGH
    
    def _calculate_confidence_level(self, user_profile: UserTrustProfile, 
                                  trust_metrics: TrustMetrics) -> float:
        """Calculate confidence level in the trust evaluation."""
        # Base confidence on amount of historical data
        base_confidence = min(user_profile.total_evaluations * 2.0, 80.0)
        
        # Adjust based on consistency of historical scores
        if len(user_profile.trust_history) > 1:
            trust_variance = statistics.variance(user_profile.trust_history)
            consistency_bonus = max(0, 20.0 - trust_variance / 5.0)
            base_confidence += consistency_bonus
        
        return min(base_confidence, 100.0)
    
    def _get_adaptive_thresholds(self, user_profile: UserTrustProfile) -> Dict[str, float]:
        """Get adaptive thresholds based on user's historical behavior."""
        if not user_profile.trust_history:
            return self.default_thresholds.copy()
        
        avg_trust = statistics.mean(user_profile.trust_history)
        
        # Adjust thresholds based on user's typical trust level
        adaptive_thresholds = {}
        for level, threshold in self.default_thresholds.items():
            # Adjust threshold based on user's baseline
            adjustment = (avg_trust - 75.0) * 0.1  # Adjust by 10% of difference from 75
            adaptive_thresholds[level] = max(0, threshold + adjustment)
        
        return adaptive_thresholds
    
    def _generate_recommendations(self, trust_metrics: TrustMetrics, risk_level: RiskLevel,
                                user_profile: UserTrustProfile) -> List[str]:
        """Generate actionable recommendations based on trust evaluation."""
        recommendations = []
        
        # Device-related recommendations
        if trust_metrics.device_consistency < 50:
            recommendations.append("Consider device re-authentication or registration")
        
        # Temporal pattern recommendations
        if trust_metrics.temporal_patterns < 50:
            recommendations.append("Unusual access timing detected - verify legitimate use")
        
        # Geographic recommendations
        if trust_metrics.geographic_consistency < 50:
            recommendations.append("Access from unusual location - consider additional verification")
        
        # Behavioral recommendations
        if trust_metrics.behavioral_patterns < 50:
            recommendations.append("Behavioral anomalies detected - recommend pattern re-baseline")
        
        # Risk-based recommendations
        if risk_level in [RiskLevel.HIGH, RiskLevel.VERY_HIGH]:
            recommendations.append("High risk detected - require additional authentication factors")
            recommendations.append("Consider manual security review")
        
        # Compliance recommendations
        if trust_metrics.compliance_score < 80:
            recommendations.append("Compliance issues detected - review security policies")
        
        if not recommendations:
            recommendations.append("Trust evaluation passed - standard access approved")
        
        return recommendations
    
    def _update_user_profile(self, user_profile: UserTrustProfile, evaluation: TrustEvaluation,
                           context_data: Dict[str, Any]):
        """Update user profile with new evaluation data."""
        
        # Update trust history
        user_profile.trust_history.append(evaluation.overall_trust_score)
        
        # Limit history to last 100 evaluations
        if len(user_profile.trust_history) > 100:
            user_profile.trust_history = user_profile.trust_history[-100:]
        
        # Update baseline trust score (moving average)
        user_profile.baseline_trust_score = statistics.mean(user_profile.trust_history)
        
        # Update behavioral baselines
        self._update_behavioral_baselines(user_profile, context_data)
        
        # Record risk events if needed
        if evaluation.risk_level in [RiskLevel.HIGH, RiskLevel.VERY_HIGH]:
            user_profile.risk_events.append({
                "timestamp": evaluation.evaluation_timestamp,
                "risk_level": evaluation.risk_level.name,
                "trust_score": evaluation.overall_trust_score,
                "session_id": evaluation.session_id
            })
        
        # Update counters
        user_profile.total_evaluations += 1
        user_profile.last_evaluation = evaluation.evaluation_timestamp
        
        # Save updated profile
        self._save_user_profile(user_profile)
    
    def _update_behavioral_baselines(self, user_profile: UserTrustProfile, context_data: Dict[str, Any]):
        """Update behavioral baselines with new data."""
        
        # Update device fingerprints
        if context_data.get("device_fingerprint"):
            device_hash = hashlib.sha256(context_data["device_fingerprint"].encode()).hexdigest()
            known_devices = user_profile.behavioral_baselines.get("known_devices", [])
            if device_hash not in known_devices:
                known_devices.append(device_hash)
                user_profile.behavioral_baselines["known_devices"] = known_devices[-10:]  # Keep last 10
        
        # Update location patterns
        if context_data.get("latitude") and context_data.get("longitude"):
            lat, lon = context_data["latitude"], context_data["longitude"]
            known_locations = user_profile.behavioral_baselines.get("known_locations", [])
            
            # Add location if it's significantly different from known locations
            is_new_location = True
            for known_lat, known_lon in known_locations:
                if self._calculate_distance(lat, lon, known_lat, known_lon) < 5:  # Within 5km
                    is_new_location = False
                    break
            
            if is_new_location:
                known_locations.append((lat, lon))
                user_profile.behavioral_baselines["known_locations"] = known_locations[-20:]  # Keep last 20
        
        # Update timing patterns
        if context_data.get("current_timestamp") and context_data.get("last_access_time"):
            interval = context_data["current_timestamp"] - context_data["last_access_time"]
            intervals = user_profile.behavioral_baselines.get("typical_access_intervals", [])
            intervals.append(interval)
            user_profile.behavioral_baselines["typical_access_intervals"] = intervals[-50:]  # Keep last 50
        
        # Update session duration patterns
        if context_data.get("session_duration"):
            durations = user_profile.behavioral_baselines.get("typical_session_durations", [])
            durations.append(context_data["session_duration"])
            user_profile.behavioral_baselines["typical_session_durations"] = durations[-30:]  # Keep last 30
        
        # Update typing patterns
        if context_data.get("keystrokes_per_minute"):
            typing_speeds = user_profile.behavioral_baselines.get("typical_typing_speed", [])
            typing_speeds.append(context_data["keystrokes_per_minute"])
            user_profile.behavioral_baselines["typical_typing_speed"] = typing_speeds[-30:]  # Keep last 30
    
    def _calculate_distance(self, lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """Calculate distance between two geographic points in kilometers."""
        # Simplified distance calculation (Euclidean approximation)
        lat_diff = lat1 - lat2
        lon_diff = lon1 - lon2
        return math.sqrt(lat_diff**2 + lon_diff**2) * 111  # Rough conversion to km
    
    def _get_user_profile(self, user_id: str) -> UserTrustProfile:
        """Get or create user trust profile."""
        if user_id not in self.user_profiles:
            self.user_profiles[user_id] = UserTrustProfile(
                user_id=user_id,
                baseline_trust_score=50.0,  # Default baseline
                trust_history=[],
                behavioral_baselines={},
                risk_events=[],
                total_evaluations=0,
                compliance_violations=0
            )
        
        return self.user_profiles[user_id]
    
    def _save_user_profile(self, user_profile: UserTrustProfile):
        """Save user profile to disk."""
        try:
            profile_file = self.data_path / f"{user_profile.user_id}_profile.json"
            with open(profile_file, 'w') as f:
                json.dump(asdict(user_profile), f, indent=2)
        except Exception as e:
            self.logger.error(f"Failed to save user profile {user_profile.user_id}: {e}")
    
    def _load_user_profiles(self):
        """Load existing user profiles from disk."""
        try:
            for profile_file in self.data_path.glob("*_profile.json"):
                with open(profile_file, 'r') as f:
                    profile_data = json.load(f)
                    user_profile = UserTrustProfile(**profile_data)
                    self.user_profiles[user_profile.user_id] = user_profile
        except Exception as e:
            self.logger.error(f"Failed to load user profiles: {e}")
    
    def _log_trust_evaluation(self, evaluation: TrustEvaluation, processing_time: float):
        """Log trust evaluation for audit purposes."""
        if self.audit_logger:
            try:
                self.audit_logger.add_entry({
                    "event": "trust_evaluation",
                    "user_id": evaluation.user_id,
                    "trust_score": evaluation.overall_trust_score,
                    "risk_level": evaluation.risk_level.name,
                    "confidence": evaluation.confidence_level,
                    "processing_time": processing_time,
                    "session_id": evaluation.session_id,
                    "timestamp": evaluation.evaluation_timestamp
                })
            except Exception as e:
                self.logger.warning(f"Could not log trust evaluation: {e}")

# Utility functions for integration
def create_trust_engine() -> TrustScoringEngine:
    """Create a new trust scoring engine instance."""
    return TrustScoringEngine()

def evaluate_user_trust(user_id: str, context_verification_result: Dict[str, Any]) -> TrustEvaluation:
    """
    Convenience function to evaluate user trust.
    
    Args:
        user_id: User identifier
        context_verification_result: Results from context verification
        
    Returns:
        TrustEvaluation with complete trust assessment
    """
    trust_engine = create_trust_engine()
    return trust_engine.evaluate_trust(user_id, context_verification_result)