"""
Trust Scorer for ReliQuary.
This module calculates dynamic trust scores based on verified context and historical behavior.
"""

import json
import logging
import os
from typing import Dict, Any, List, Optional
from dataclasses import asdict, dataclass
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path


class TrustLevel(Enum):
    """Levels of trust"""
    VERY_LOW = "very_low"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    VERY_HIGH = "very_high"


@dataclass
class TrustFactors:
    """Factors that contribute to trust score"""
    context_verification: float  # 0.0 to 1.0
    historical_behavior: float   # 0.0 to 1.0
    risk_assessment: float       # 0.0 to 1.0
    consistency: float           # 0.0 to 1.0
    recency: float               # 0.0 to 1.0


@dataclass
class TrustScore:
    """Trust score with metadata"""
    score: float  # 0.0 to 1.0
    level: TrustLevel
    factors: TrustFactors
    timestamp: datetime
    user_id: str
    explanation: str


class RiskLevel(Enum):
    """API-facing risk levels derived from the trust score."""

    VERY_LOW = "very_low"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    VERY_HIGH = "very_high"


class TrustScorer:
    """Calculates dynamic trust scores based on multiple factors"""
    
    def __init__(self, config_file: Optional[str] = None):
        self.logger = logging.getLogger(__name__)
        self.config = self._load_config(config_file)
    
    def _load_config(self, config_file: Optional[str]) -> Dict[str, Any]:
        """Load trust scoring configuration"""
        default_config = {
            "weights": {
                "context_verification": 0.3,
                "historical_behavior": 0.25,
                "risk_assessment": 0.2,
                "consistency": 0.15,
                "recency": 0.1
            },
            "thresholds": {
                "very_high": 0.9,
                "high": 0.7,
                "medium": 0.5,
                "low": 0.3,
                "very_low": 0.0
            }
        }
        
        if config_file:
            try:
                with open(config_file, 'r') as f:
                    config = json.load(f)
                    # Merge with default config
                    for key in default_config:
                        if key in config:
                            default_config[key].update(config[key])
            except Exception as e:
                self.logger.warning(f"Failed to load trust config from {config_file}: {str(e)}")
        
        return default_config
    
    def calculate_trust_score(self, user_id: str, context_data: Dict[str, Any], 
                            history_data: Optional[List[Dict[str, Any]]] = None) -> TrustScore:
        """
        Calculate trust score for a user based on context and history.
        
        Args:
            user_id: ID of the user
            context_data: Current context verification data
            history_data: Historical behavior data
            
        Returns:
            Calculated trust score
        """
        try:
            # Calculate trust factors
            factors = self._calculate_trust_factors(context_data, history_data)
            
            # Calculate weighted score
            weights = self.config["weights"]
            weighted_score = (
                factors.context_verification * weights["context_verification"] +
                factors.historical_behavior * weights["historical_behavior"] +
                factors.risk_assessment * weights["risk_assessment"] +
                factors.consistency * weights["consistency"] +
                factors.recency * weights["recency"]
            )
            
            # Determine trust level
            level = self._determine_trust_level(weighted_score)
            
            # Generate explanation
            explanation = self._generate_explanation(factors, weights)
            
            # Create trust score object
            trust_score = TrustScore(
                score=weighted_score,
                level=level,
                factors=factors,
                timestamp=datetime.now(),
                user_id=user_id,
                explanation=explanation
            )
            
            self.logger.info(f"Trust score calculated for user {user_id}: {weighted_score:.3f} ({level.value})")
            return trust_score
            
        except Exception as e:
            self.logger.error(f"Trust score calculation failed for user {user_id}: {str(e)}")
            # Return a default low trust score
            return TrustScore(
                score=0.1,
                level=TrustLevel.VERY_LOW,
                factors=TrustFactors(0.0, 0.0, 0.0, 0.0, 0.0),
                timestamp=datetime.now(),
                user_id=user_id,
                explanation=f"Error in trust calculation: {str(e)}"
            )
    
    def _calculate_trust_factors(self, context_data: Dict[str, Any], 
                               history_data: Optional[List[Dict[str, Any]]]) -> TrustFactors:
        """
        Calculate individual trust factors.
        
        Args:
            context_data: Current context verification data
            history_data: Historical behavior data
            
        Returns:
            Trust factors object
        """
        # Context verification factor (0.0 to 1.0)
        context_factor = self._calculate_context_factor(context_data)
        
        # Historical behavior factor (0.0 to 1.0)
        history_factor = self._calculate_history_factor(history_data)
        
        # Risk assessment factor (0.0 to 1.0)
        risk_factor = self._calculate_risk_factor(context_data, history_data)
        
        # Consistency factor (0.0 to 1.0)
        consistency_factor = self._calculate_consistency_factor(history_data)
        
        # Recency factor (0.0 to 1.0)
        recency_factor = self._calculate_recency_factor(history_data)
        
        return TrustFactors(
            context_verification=context_factor,
            historical_behavior=history_factor,
            risk_assessment=risk_factor,
            consistency=consistency_factor,
            recency=recency_factor
        )
    
    def _calculate_context_factor(self, context_data: Dict[str, Any]) -> float:
        """Calculate context verification factor"""
        if not context_data:
            return 0.0
        
        # Check if context was verified
        verified = context_data.get("verified", False)
        if not verified:
            return 0.0
        
        # Use confidence score if available
        confidence = context_data.get("confidence_score", 0.5)
        return min(max(confidence, 0.0), 1.0)
    
    def _calculate_history_factor(self, history_data: Optional[List[Dict[str, Any]]]) -> float:
        """Calculate historical behavior factor"""
        if not history_data:
            return 0.5  # Neutral score if no history
        
        # Calculate success rate from history
        total_actions = len(history_data)
        if total_actions == 0:
            return 0.5
        
        successful_actions = sum(1 for action in history_data if action.get("success", False))
        success_rate = successful_actions / total_actions
        
        return success_rate
    
    def _calculate_risk_factor(self, context_data: Dict[str, Any], 
                              history_data: Optional[List[Dict[str, Any]]]) -> float:
        """Calculate risk assessment factor"""
        # Start with a neutral score
        risk_score = 0.5
        
        # Adjust based on context risk assessment
        if context_data and "risk_assessment" in context_data:
            risk_assessment = context_data["risk_assessment"]
            risk_level = risk_assessment.get("risk_level", "medium")
            
            if risk_level == "low":
                risk_score = 0.9
            elif risk_level == "medium":
                risk_score = 0.7
            elif risk_level == "high":
                risk_score = 0.3
        
        # Adjust based on historical anomalies
        if history_data:
            recent_history = history_data[-10:]  # Last 10 actions
            anomalies = sum(1 for action in recent_history if action.get("anomalous", False))
            if anomalies > 0:
                anomaly_rate = anomalies / len(recent_history)
                risk_score *= (1.0 - anomaly_rate)  # Reduce score based on anomaly rate
        
        return max(0.0, min(risk_score, 1.0))
    
    def _calculate_consistency_factor(self, history_data: Optional[List[Dict[str, Any]]]) -> float:
        """Calculate consistency factor"""
        if not history_data or len(history_data) < 2:
            return 0.5  # Neutral score if insufficient history
        
        # Calculate consistency based on pattern regularity
        # This is a simplified implementation
        total_actions = len(history_data)
        consistent_actions = total_actions - len([a for a in history_data if a.get("anomalous", False)])
        consistency_rate = consistent_actions / total_actions
        
        return consistency_rate
    
    def _calculate_recency_factor(self, history_data: Optional[List[Dict[str, Any]]]) -> float:
        """Calculate recency factor"""
        if not history_data:
            return 0.5  # Neutral score if no history
        
        # Get the most recent action
        most_recent = history_data[-1]
        timestamp_str = most_recent.get("timestamp")
        
        if not timestamp_str:
            return 0.5
        
        try:
            # Parse timestamp
            if isinstance(timestamp_str, str):
                action_time = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
            else:
                action_time = datetime.now()  # Default to now if parsing fails
            
            # Calculate time difference
            time_diff = datetime.now() - action_time
            
            # Score based on recency (more recent = higher score)
            # Within last hour: 1.0, within last day: 0.8, within last week: 0.6, older: 0.3
            if time_diff < timedelta(hours=1):
                return 1.0
            elif time_diff < timedelta(days=1):
                return 0.8
            elif time_diff < timedelta(weeks=1):
                return 0.6
            else:
                return 0.3
                
        except Exception:
            return 0.5  # Neutral score if timestamp parsing fails
    
    def _determine_trust_level(self, score: float) -> TrustLevel:
        """Determine trust level based on score"""
        thresholds = self.config["thresholds"]
        
        if score >= thresholds["very_high"]:
            return TrustLevel.VERY_HIGH
        elif score >= thresholds["high"]:
            return TrustLevel.HIGH
        elif score >= thresholds["medium"]:
            return TrustLevel.MEDIUM
        elif score >= thresholds["low"]:
            return TrustLevel.LOW
        else:
            return TrustLevel.VERY_LOW
    
    def _generate_explanation(self, factors: TrustFactors, weights: Dict[str, float]) -> str:
        """Generate explanation for trust score"""
        explanations = []
        
        if factors.context_verification > 0.8:
            explanations.append("Strong context verification")
        elif factors.context_verification < 0.3:
            explanations.append("Weak context verification")
        
        if factors.historical_behavior > 0.8:
            explanations.append("Consistent historical behavior")
        elif factors.historical_behavior < 0.3:
            explanations.append("Inconsistent historical behavior")
        
        if factors.risk_assessment > 0.8:
            explanations.append("Low risk profile")
        elif factors.risk_assessment < 0.3:
            explanations.append("High risk profile")
        
        if factors.consistency > 0.8:
            explanations.append("High behavioral consistency")
        elif factors.consistency < 0.3:
            explanations.append("Low behavioral consistency")
        
        if factors.recency > 0.8:
            explanations.append("Recent activity")
        elif factors.recency < 0.3:
            explanations.append("Inactive user")
        
        if not explanations:
            explanations.append("Moderate trust factors")
        
        return "; ".join(explanations)


class TrustHistoryStore:
    """Small JSON-backed trust history store for local/open-source runs."""

    def __init__(self, path: Optional[str] = None):
        default_path = Path("runtime/trust_history.json")
        self.path = Path(path or os.environ.get("RELIQUARY_TRUST_HISTORY", default_path))
        self.path.parent.mkdir(parents=True, exist_ok=True)

    def append(self, user_id: str, record: Dict[str, Any]) -> None:
        records = self._read_all()
        records.setdefault(user_id, []).append(record)
        self.path.write_text(json.dumps(records, indent=2, sort_keys=True), encoding="utf-8")

    def history(
        self,
        user_id: str,
        limit: int = 50,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
    ) -> List[Dict[str, Any]]:
        records = self._read_all().get(user_id, [])
        filtered = []
        for record in records:
            updated = datetime.fromisoformat(record["last_updated"])
            if start_time and updated < start_time:
                continue
            if end_time and updated > end_time:
                continue
            filtered.append(record)
        return filtered[-limit:]

    def latest(self, user_id: str) -> Optional[Dict[str, Any]]:
        records = self.history(user_id, limit=1)
        return records[-1] if records else None

    def _read_all(self) -> Dict[str, List[Dict[str, Any]]]:
        if not self.path.exists():
            return {}
        try:
            return json.loads(self.path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            return {}


class TrustScoringEngine:
    """API adapter that evaluates trust and persists profile history."""

    def __init__(self, config_file: Optional[str] = None, history_path: Optional[str] = None):
        self.scorer = TrustScorer(config_file)
        self.history_store = TrustHistoryStore(history_path)

    def evaluate_trust(self, user_id: str, context: Dict[str, Any]) -> Dict[str, Any]:
        prior = self.history_store.history(user_id, limit=100)
        history_data = [
            {
                "success": item["overall_trust_score"] >= 50.0,
                "anomalous": item["risk_level"] in {"high", "very_high"},
                "timestamp": item["last_updated"],
            }
            for item in prior
        ]
        score = self.scorer.calculate_trust_score(user_id, context, history_data)
        record = self._record_from_score(score, prior)
        self.history_store.append(user_id, record)
        return record

    def get_profile(self, user_id: str) -> Optional[Dict[str, Any]]:
        records = self.history_store.history(user_id, limit=100)
        if not records:
            return None
        latest = records[-1]
        return {
            "user_id": user_id,
            "current_trust_score": latest["overall_trust_score"],
            "risk_level": latest["risk_level"],
            "historical_scores": [record["overall_trust_score"] for record in records],
            "trust_factors": latest["trust_factors"],
            "created_at": records[0]["last_updated"],
            "last_updated": latest["last_updated"],
            "total_evaluations": len(records),
        }

    def get_history(
        self,
        user_id: str,
        limit: int = 50,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
    ) -> List[Dict[str, Any]]:
        return self.history_store.history(user_id, limit, start_time, end_time)

    def get_current_score(self, user_id: str) -> Optional[Dict[str, Any]]:
        return self.history_store.latest(user_id)

    def _record_from_score(self, score: TrustScore, prior: List[Dict[str, Any]]) -> Dict[str, Any]:
        factor_weights = self.scorer.config["weights"]
        factor_values = asdict(score.factors)
        trust_factors = [
            {
                "name": name,
                "weight": factor_weights[name],
                "score": value * 100.0,
                "impact": (value - 0.5) * factor_weights[name] * 100.0,
            }
            for name, value in factor_values.items()
        ]
        historical_scores = [record["overall_trust_score"] for record in prior][-20:]
        historical_scores.append(score.score * 100.0)
        return {
            "overall_trust_score": score.score * 100.0,
            "risk_level": self._risk_from_trust_level(score.level).value,
            "confidence_score": min(1.0, 0.55 + min(len(prior), 20) * 0.02),
            "trust_factors": trust_factors,
            "historical_scores": historical_scores,
            "last_updated": score.timestamp.isoformat(),
            "explanation": score.explanation,
        }

    @staticmethod
    def _risk_from_trust_level(level: TrustLevel) -> RiskLevel:
        mapping = {
            TrustLevel.VERY_HIGH: RiskLevel.VERY_LOW,
            TrustLevel.HIGH: RiskLevel.LOW,
            TrustLevel.MEDIUM: RiskLevel.MEDIUM,
            TrustLevel.LOW: RiskLevel.HIGH,
            TrustLevel.VERY_LOW: RiskLevel.VERY_HIGH,
        }
        return mapping[level]


# Global trust scorer instance
_trust_scorer = None


def get_trust_scorer(config_file: Optional[str] = None) -> TrustScorer:
    """Get the global trust scorer instance"""
    global _trust_scorer
    if _trust_scorer is None:
        _trust_scorer = TrustScorer(config_file)
    return _trust_scorer


def calculate_user_trust_score(user_id: str, context_data: Dict[str, Any], 
                              history_data: Optional[List[Dict[str, Any]]] = None) -> TrustScore:
    """Convenience function to calculate user trust score"""
    scorer = get_trust_scorer()
    return scorer.calculate_trust_score(user_id, context_data, history_data)
