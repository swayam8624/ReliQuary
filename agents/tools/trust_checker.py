"""
Trust Checker Tool for ReliQuary Multi-Agent System

This tool allows agents to evaluate trust scores, analyze trust patterns,
and assess risk levels for users based on their behavioral history and
current context. It integrates with the trust scoring engine for comprehensive
evaluation.
"""

import logging
import time
import statistics
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
from collections import defaultdict, deque

# Import trust components
from zk.trust_engine import (
    TrustScoringEngine,
    TrustEvaluation,
    RiskLevel,
    UserTrustProfile
)


class TrustCheckResult(Enum):
    """Results of trust evaluation"""
    TRUSTED = "trusted"
    CONDITIONAL = "conditional"
    UNTRUSTED = "untrusted"
    INSUFFICIENT_DATA = "insufficient_data"
    ERROR = "error"


class TrustTrend(Enum):
    """Trust score trend direction"""
    IMPROVING = "improving"
    STABLE = "stable"
    DECLINING = "declining"
    VOLATILE = "volatile"
    UNKNOWN = "unknown"


@dataclass
class TrustCheckResponse:
    """Response from trust evaluation check"""
    result: TrustCheckResult
    trust_score: float
    risk_level: RiskLevel
    confidence: float
    trend: TrustTrend
    behavioral_analysis: Dict[str, Any]
    risk_factors: List[str]
    trust_factors: List[str]
    recommendations: List[str]
    historical_context: Dict[str, Any]
    processing_time: float
    error_message: Optional[str] = None


@dataclass
class TrustPattern:
    """Trust pattern analysis result"""
    pattern_type: str
    frequency: int
    last_occurrence: float
    risk_score: float
    description: str
    mitigation_suggestions: List[str]


class TrustChecker:
    """
    Trust Checker Tool for comprehensive trust evaluation.
    
    This tool provides agents with advanced trust scoring capabilities,
    including behavioral analysis, risk assessment, and trend analysis.
    It maintains user trust profiles and provides recommendations.
    """
    
    def __init__(self):
        """Initialize the trust checker tool."""
        self.trust_engine = TrustScoringEngine()
        self.logger = logging.getLogger("trust_checker")
        
        # Trust thresholds
        self.trust_thresholds = {
            "high_trust": 80.0,
            "medium_trust": 60.0,
            "low_trust": 40.0,
            "untrusted": 20.0
        }
        
        # Pattern tracking
        self.user_patterns: Dict[str, List[TrustPattern]] = defaultdict(list)
        self.global_patterns: Dict[str, deque] = defaultdict(lambda: deque(maxlen=1000))
        
        # Performance metrics
        self.total_evaluations = 0
        self.successful_evaluations = 0
        self.failed_evaluations = 0
        self.average_processing_time = 0.0
    
    async def evaluate_trust(self, 
                           user_id: str,
                           context_data: Dict[str, Any],
                           include_analysis: bool = True,
                           update_profile: bool = True) -> TrustCheckResponse:
        """
        Comprehensive trust evaluation for a user.
        
        Args:
            user_id: User identifier
            context_data: Current context information
            include_analysis: Whether to include detailed behavioral analysis
            update_profile: Whether to update the user's trust profile
            
        Returns:
            TrustCheckResponse with trust evaluation results
        """
        start_time = time.time()
        self.total_evaluations += 1
        
        try:
            # Evaluate trust using trust engine
            trust_evaluation = self.trust_engine.evaluate_trust(user_id, context_data)
            
            # Determine trust result
            trust_result = self._classify_trust_result(trust_evaluation.overall_trust_score)
            
            # Analyze trust trend
            trend = self._analyze_trust_trend(user_id, trust_evaluation.overall_trust_score)
            
            # Perform behavioral analysis if requested
            behavioral_analysis = {}
            if include_analysis:
                behavioral_analysis = await self._perform_behavioral_analysis(
                    user_id, context_data, trust_evaluation
                )
            
            # Extract factors
            risk_factors, trust_factors = self._extract_trust_factors(
                trust_evaluation, context_data
            )
            
            # Generate recommendations
            recommendations = self._generate_recommendations(
                trust_evaluation, behavioral_analysis, risk_factors
            )
            
            # Get historical context
            historical_context = self._get_historical_context(user_id)
            
            # Update patterns if requested
            if update_profile:
                await self._update_trust_patterns(user_id, trust_evaluation, context_data)
            
            processing_time = time.time() - start_time
            self._update_metrics(processing_time, True)
            
            return TrustCheckResponse(
                result=trust_result,
                trust_score=trust_evaluation.overall_trust_score,
                risk_level=trust_evaluation.risk_level,
                confidence=trust_evaluation.confidence_score,
                trend=trend,
                behavioral_analysis=behavioral_analysis,
                risk_factors=risk_factors,
                trust_factors=trust_factors,
                recommendations=recommendations,
                historical_context=historical_context,
                processing_time=processing_time
            )
            
        except Exception as e:
            self.logger.error(f"Trust evaluation failed: {e}")
            processing_time = time.time() - start_time
            self._update_metrics(processing_time, False)
            
            return TrustCheckResponse(
                result=TrustCheckResult.ERROR,
                trust_score=0.0,
                risk_level=RiskLevel.VERY_HIGH,
                confidence=0.0,
                trend=TrustTrend.UNKNOWN,
                behavioral_analysis={},
                risk_factors=["Trust evaluation system error"],
                trust_factors=[],
                recommendations=["Retry trust evaluation", "Contact system administrator"],
                historical_context={},
                processing_time=processing_time,
                error_message=str(e)
            )
    
    def _classify_trust_result(self, trust_score: float) -> TrustCheckResult:
        """Classify trust score into result category."""
        if trust_score >= self.trust_thresholds["high_trust"]:
            return TrustCheckResult.TRUSTED
        elif trust_score >= self.trust_thresholds["medium_trust"]:
            return TrustCheckResult.CONDITIONAL
        elif trust_score >= self.trust_thresholds["untrusted"]:
            return TrustCheckResult.UNTRUSTED
        else:
            return TrustCheckResult.UNTRUSTED
    
    def _analyze_trust_trend(self, user_id: str, current_score: float) -> TrustTrend:
        """Analyze trust score trend for a user."""
        try:
            # Get user's trust profile
            profile = self.trust_engine.get_user_profile(user_id)
            
            if not profile or not profile.historical_scores:
                return TrustTrend.UNKNOWN
            
            # Get recent scores (last 10)
            recent_scores = list(profile.historical_scores)[-10:]
            recent_scores.append(current_score)
            
            if len(recent_scores) < 3:
                return TrustTrend.UNKNOWN
            
            # Calculate trend
            first_half = recent_scores[:len(recent_scores)//2]
            second_half = recent_scores[len(recent_scores)//2:]
            
            first_avg = statistics.mean(first_half)
            second_avg = statistics.mean(second_half)
            
            # Calculate variance to detect volatility
            variance = statistics.variance(recent_scores)
            
            if variance > 100:  # High variance threshold
                return TrustTrend.VOLATILE
            elif second_avg > first_avg + 5:
                return TrustTrend.IMPROVING
            elif second_avg < first_avg - 5:
                return TrustTrend.DECLINING
            else:
                return TrustTrend.STABLE
                
        except Exception as e:
            self.logger.warning(f"Trust trend analysis failed: {e}")
            return TrustTrend.UNKNOWN
    
    async def _perform_behavioral_analysis(self, 
                                         user_id: str,
                                         context_data: Dict[str, Any],
                                         trust_evaluation: TrustEvaluation) -> Dict[str, Any]:
        """Perform detailed behavioral analysis."""
        analysis = {
            "typing_behavior": {},
            "access_patterns": {},
            "temporal_patterns": {},
            "anomaly_indicators": [],
            "consistency_score": 0.0
        }
        
        try:
            # Typing behavior analysis
            kpm = context_data.get("keystrokes_per_minute", 0)
            if kpm > 0:
                analysis["typing_behavior"] = {
                    "current_speed": kpm,
                    "human_like": 10 <= kpm <= 200,
                    "consistency_rating": "normal" if 40 <= kpm <= 120 else "unusual",
                    "automation_risk": kpm > 300 or kpm < 5
                }
                
                if kpm > 300:
                    analysis["anomaly_indicators"].append("Extremely high typing speed")
                elif kpm < 5:
                    analysis["anomaly_indicators"].append("Extremely low typing speed")
            
            # Access pattern analysis
            access_freq = context_data.get("access_frequency", 1)
            session_duration = context_data.get("session_duration", 1800)
            
            analysis["access_patterns"] = {
                "frequency": access_freq,
                "session_duration": session_duration,
                "normal_frequency": 1 <= access_freq <= 10,
                "normal_duration": 300 <= session_duration <= 14400,
                "burst_activity": access_freq > 15
            }
            
            if access_freq > 20:
                analysis["anomaly_indicators"].append("Excessive access frequency")
            if session_duration < 60:
                analysis["anomaly_indicators"].append("Unusually short session")
            
            # Temporal pattern analysis
            current_hour = int(time.time() % 86400 / 3600)
            analysis["temporal_patterns"] = {
                "access_hour": current_hour,
                "business_hours": 9 <= current_hour <= 17,
                "off_hours": current_hour < 6 or current_hour > 22,
                "weekend_access": False  # Simplified
            }
            
            if analysis["temporal_patterns"]["off_hours"]:
                analysis["anomaly_indicators"].append("Off-hours access")
            
            # Calculate consistency score
            consistency_factors = [
                analysis["typing_behavior"].get("human_like", False),
                analysis["access_patterns"].get("normal_frequency", False),
                analysis["access_patterns"].get("normal_duration", False)
            ]
            
            analysis["consistency_score"] = sum(consistency_factors) / len(consistency_factors) * 100
            
        except Exception as e:
            self.logger.warning(f"Behavioral analysis failed: {e}")
            analysis["error"] = str(e)
        
        return analysis
    
    def _extract_trust_factors(self, 
                             trust_evaluation: TrustEvaluation,
                             context_data: Dict[str, Any]) -> Tuple[List[str], List[str]]:
        """Extract risk and trust factors from evaluation."""
        risk_factors = []
        trust_factors = []
        
        # Trust score based factors
        if trust_evaluation.overall_trust_score >= 80:
            trust_factors.append("High trust score")
        elif trust_evaluation.overall_trust_score >= 60:
            trust_factors.append("Good trust score")
        elif trust_evaluation.overall_trust_score < 40:
            risk_factors.append("Low trust score")
        
        # Risk level based factors
        if trust_evaluation.risk_level == RiskLevel.LOW:
            trust_factors.append("Low risk assessment")
        elif trust_evaluation.risk_level in [RiskLevel.HIGH, RiskLevel.VERY_HIGH]:
            risk_factors.append(f"High risk level: {trust_evaluation.risk_level.value}")
        
        # Context-based factors
        if context_data.get("device_verified", False):
            trust_factors.append("Device verified")
        else:
            risk_factors.append("Device not verified")
        
        if context_data.get("location_verified", False):
            trust_factors.append("Location verified")
        
        # Behavioral factors
        kpm = context_data.get("keystrokes_per_minute", 60)
        if 40 <= kpm <= 120:
            trust_factors.append("Normal typing behavior")
        elif kpm > 200 or kpm < 10:
            risk_factors.append("Unusual typing behavior")
        
        access_freq = context_data.get("access_frequency", 1)
        if access_freq > 15:
            risk_factors.append("High access frequency")
        elif 1 <= access_freq <= 5:
            trust_factors.append("Normal access frequency")
        
        return risk_factors, trust_factors
    
    def _generate_recommendations(self, 
                                trust_evaluation: TrustEvaluation,
                                behavioral_analysis: Dict[str, Any],
                                risk_factors: List[str]) -> List[str]:
        """Generate actionable recommendations based on trust evaluation."""
        recommendations = []
        
        # Trust score based recommendations
        if trust_evaluation.overall_trust_score < 40:
            recommendations.append("Require additional verification factors")
            recommendations.append("Implement enhanced monitoring")
        elif trust_evaluation.overall_trust_score < 60:
            recommendations.append("Consider step-up authentication")
            recommendations.append("Monitor for behavioral changes")
        
        # Risk level based recommendations
        if trust_evaluation.risk_level in [RiskLevel.HIGH, RiskLevel.VERY_HIGH]:
            recommendations.append("Deny access pending investigation")
            recommendations.append("Require administrative approval")
        elif trust_evaluation.risk_level == RiskLevel.MEDIUM:
            recommendations.append("Grant limited access with monitoring")
        
        # Behavioral analysis based recommendations
        if behavioral_analysis.get("anomaly_indicators"):
            recommendations.append("Investigate anomalous behavior patterns")
            if "automation_risk" in str(behavioral_analysis):
                recommendations.append("Implement CAPTCHA or human verification")
        
        # Risk factor based recommendations
        if "Device not verified" in risk_factors:
            recommendations.append("Require device re-registration")
        
        if "High access frequency" in risk_factors:
            recommendations.append("Implement rate limiting")
        
        if "Off-hours access" in str(behavioral_analysis):
            recommendations.append("Verify legitimate business need for off-hours access")
        
        # Default recommendations
        if not recommendations:
            if trust_evaluation.overall_trust_score >= 80:
                recommendations.append("Grant full access")
            else:
                recommendations.append("Monitor session activity")
        
        return recommendations
    
    def _get_historical_context(self, user_id: str) -> Dict[str, Any]:
        """Get historical context for the user."""
        try:
            profile = self.trust_engine.get_user_profile(user_id)
            if not profile:
                return {"message": "No historical data available"}
            
            historical_scores = list(profile.historical_scores) if profile.historical_scores else []
            
            return {
                "total_evaluations": len(historical_scores),
                "average_score": statistics.mean(historical_scores) if historical_scores else 0,
                "score_range": {
                    "min": min(historical_scores) if historical_scores else 0,
                    "max": max(historical_scores) if historical_scores else 0
                },
                "recent_scores": historical_scores[-5:] if len(historical_scores) >= 5 else historical_scores,
                "profile_age_days": (time.time() - profile.created_at) / 86400 if profile.created_at else 0
            }
        except Exception as e:
            self.logger.warning(f"Historical context retrieval failed: {e}")
            return {"error": str(e)}
    
    async def _update_trust_patterns(self, 
                                   user_id: str,
                                   trust_evaluation: TrustEvaluation,
                                   context_data: Dict[str, Any]):
        """Update trust patterns for the user."""
        try:
            # Track patterns in global data
            self.global_patterns["trust_scores"].append(trust_evaluation.overall_trust_score)
            self.global_patterns["risk_levels"].append(trust_evaluation.risk_level.value)
            
            # Update user-specific patterns
            current_time = time.time()
            
            # Detect and record patterns
            if trust_evaluation.overall_trust_score < 30:
                pattern = TrustPattern(
                    pattern_type="low_trust_event",
                    frequency=1,
                    last_occurrence=current_time,
                    risk_score=0.8,
                    description="Trust score below 30",
                    mitigation_suggestions=["Require re-authentication", "Limit access scope"]
                )
                self.user_patterns[user_id].append(pattern)
            
            # Clean old patterns (keep last 50)
            if len(self.user_patterns[user_id]) > 50:
                self.user_patterns[user_id] = self.user_patterns[user_id][-50:]
                
        except Exception as e:
            self.logger.warning(f"Pattern update failed: {e}")
    
    def _update_metrics(self, processing_time: float, success: bool):
        """Update performance metrics."""
        if success:
            self.successful_evaluations += 1
        else:
            self.failed_evaluations += 1
        
        self.average_processing_time = (
            (self.average_processing_time * (self.total_evaluations - 1) + processing_time) / 
            self.total_evaluations
        )
    
    async def quick_trust_check(self, user_id: str, current_trust_score: float) -> Dict[str, Any]:
        """Perform a quick trust check without full evaluation."""
        result = self._classify_trust_result(current_trust_score)
        trend = self._analyze_trust_trend(user_id, current_trust_score)
        
        return {
            "trust_result": result.value,
            "trust_score": current_trust_score,
            "trend": trend.value,
            "quick_recommendation": (
                "Allow access" if result == TrustCheckResult.TRUSTED
                else "Require additional verification" if result == TrustCheckResult.CONDITIONAL
                else "Deny access"
            )
        }
    
    def get_user_trust_summary(self, user_id: str) -> Dict[str, Any]:
        """Get a summary of user's trust history and patterns."""
        try:
            profile = self.trust_engine.get_user_profile(user_id)
            patterns = self.user_patterns.get(user_id, [])
            
            if not profile:
                return {"message": "User not found"}
            
            historical_scores = list(profile.historical_scores) if profile.historical_scores else []
            
            return {
                "user_id": user_id,
                "current_score": historical_scores[-1] if historical_scores else 0,
                "average_score": statistics.mean(historical_scores) if historical_scores else 0,
                "total_evaluations": len(historical_scores),
                "pattern_count": len(patterns),
                "recent_patterns": [p.pattern_type for p in patterns[-5:]],
                "trust_stability": statistics.stdev(historical_scores) if len(historical_scores) > 1 else 0,
                "profile_created": profile.created_at,
                "last_updated": profile.last_updated
            }
        except Exception as e:
            return {"error": str(e)}
    
    def get_trust_metrics(self) -> Dict[str, Any]:
        """Get trust checker performance metrics."""
        success_rate = (self.successful_evaluations / max(self.total_evaluations, 1)) * 100
        
        return {
            "total_evaluations": self.total_evaluations,
            "successful_evaluations": self.successful_evaluations,
            "failed_evaluations": self.failed_evaluations,
            "success_rate": success_rate,
            "average_processing_time": self.average_processing_time,
            "throughput": self.total_evaluations / max(self.average_processing_time * self.total_evaluations, 1),
            "tracked_users": len(self.user_patterns),
            "global_patterns_size": sum(len(pattern_queue) for pattern_queue in self.global_patterns.values())
        }