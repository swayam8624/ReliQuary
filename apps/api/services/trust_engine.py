"""Compatibility service wrapper for the real trust scoring engine."""

import logging
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, List, Optional

from core.rules.validator import RulesValidator
from core.trust.scorer import TrustScoringEngine


@dataclass
class TrustEvaluationRequest:
    """Request for trust evaluation."""

    user_id: str
    context_data: Dict[str, Any]
    history_data: Optional[List[Dict[str, Any]]] = None
    metadata: Optional[Dict[str, Any]] = None


@dataclass
class TrustEvaluationResponse:
    """Response from trust evaluation."""

    user_id: str
    trust_score: float
    trust_level: str
    factors: Dict[str, float]
    timestamp: datetime
    explanation: str
    metadata: Optional[Dict[str, Any]] = None


class TrustEngineService:
    """API service layer backed by the persistent trust scoring engine."""

    def __init__(self, engine: Optional[TrustScoringEngine] = None):
        self.logger = logging.getLogger(__name__)
        self.engine = engine or TrustScoringEngine()
        self.rules_validator = RulesValidator()

    def evaluate_trust(self, request: TrustEvaluationRequest) -> TrustEvaluationResponse:
        record = self.engine.evaluate_trust(request.user_id, request.context_data)
        return TrustEvaluationResponse(
            user_id=request.user_id,
            trust_score=record["overall_trust_score"] / 100.0,
            trust_level=record["risk_level"],
            factors={factor["name"]: factor["score"] / 100.0 for factor in record["trust_factors"]},
            timestamp=datetime.fromisoformat(record["last_updated"]),
            explanation=record.get("explanation", ""),
            metadata=request.metadata,
        )

    def get_user_trust_history(self, user_id: str, limit: int = 50) -> List[Dict[str, Any]]:
        return self.engine.get_history(user_id, limit=limit)

    def update_trust_rules(self, rules_data: Dict[str, Any]) -> bool:
        validation_result = self.rules_validator.validate_rules(rules_data)
        if not validation_result.valid:
            self.logger.warning("Invalid trust rules provided: %s", validation_result.issues)
            return False
        return True

    def get_trust_configuration(self) -> Dict[str, Any]:
        return {
            "version": "1.0.0",
            "active_rules": len(self.rules_validator.get_active_rules()),
            "scoring_weights": self.engine.scorer.config["weights"],
            "thresholds": self.engine.scorer.config["thresholds"],
        }


_trust_engine_service = None


def get_trust_engine_service() -> TrustEngineService:
    """Get the global trust engine service instance."""
    global _trust_engine_service
    if _trust_engine_service is None:
        _trust_engine_service = TrustEngineService()
    return _trust_engine_service


def evaluate_user_trust(request: TrustEvaluationRequest) -> TrustEvaluationResponse:
    """Convenience function to evaluate user trust."""
    return get_trust_engine_service().evaluate_trust(request)


def get_user_trust_history(user_id: str, limit: int = 50) -> List[Dict[str, Any]]:
    """Convenience function to get user trust history."""
    return get_trust_engine_service().get_user_trust_history(user_id, limit)


def update_trust_rules(rules_data: Dict[str, Any]) -> bool:
    """Convenience function to validate trust rules."""
    return get_trust_engine_service().update_trust_rules(rules_data)


def get_trust_configuration() -> Dict[str, Any]:
    """Convenience function to get trust configuration."""
    return get_trust_engine_service().get_trust_configuration()
