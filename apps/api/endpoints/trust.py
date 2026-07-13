"""
Trust API endpoints for ReliQuary.
"""

import logging
from datetime import UTC, datetime

from fastapi import APIRouter, Depends, HTTPException, status

from apps.api.schemas.trust import (
    RiskLevel,
    TrustEvaluation,
    TrustEvaluationRequest,
    TrustEvaluationResponse,
    TrustHistoryRequest,
    TrustHistoryResponse,
    TrustProfileResponse,
    TrustRule,
    TrustRulesResponse,
    UserTrustProfile,
)
from core.rules.validator import RuleValidator
from core.trust.scorer import TrustScoringEngine

router = APIRouter(prefix="/trust", tags=["trust"])
logger = logging.getLogger(__name__)

_trust_engine = None


async def get_trust_engine() -> TrustScoringEngine:
    """Return a process-global trust engine so profile history is reused."""
    global _trust_engine
    if _trust_engine is None:
        _trust_engine = TrustScoringEngine()
    return _trust_engine


async def get_rule_validator() -> RuleValidator:
    return RuleValidator()


def _evaluation_from_record(record: dict) -> TrustEvaluation:
    return TrustEvaluation(
        overall_trust_score=record["overall_trust_score"],
        risk_level=RiskLevel(record["risk_level"]),
        confidence_score=record["confidence_score"],
        trust_factors=record["trust_factors"],
        historical_scores=record["historical_scores"],
        last_updated=datetime.fromisoformat(record["last_updated"]),
    )


@router.post("/evaluate", response_model=TrustEvaluationResponse)
async def evaluate_trust(
    request: TrustEvaluationRequest,
    trust_engine: TrustScoringEngine = Depends(get_trust_engine),
):
    """Evaluate and persist a trust score for a user."""
    try:
        start_time = datetime.now(UTC)
        record = trust_engine.evaluate_trust(
            user_id=request.user_id,
            context=request.context_data,
        )
        return TrustEvaluationResponse(
            request_id=request.request_id,
            user_id=request.user_id,
            evaluation=_evaluation_from_record(record),
            processing_time=(datetime.now(UTC) - start_time).total_seconds(),
        )
    except Exception as e:
        logger.error("Trust evaluation failed for user %s: %s", request.user_id, e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Trust evaluation failed: {str(e)}",
        )


@router.get("/profile/{user_id}", response_model=TrustProfileResponse)
async def get_trust_profile(
    user_id: str,
    trust_engine: TrustScoringEngine = Depends(get_trust_engine),
):
    """Retrieve a user trust profile derived from stored evaluations."""
    try:
        profile_data = trust_engine.get_profile(user_id)
        if profile_data is None:
            return TrustProfileResponse(user_id=user_id, profile=None, found=False)

        profile = UserTrustProfile(
            user_id=profile_data["user_id"],
            current_trust_score=profile_data["current_trust_score"],
            risk_level=RiskLevel(profile_data["risk_level"]),
            historical_scores=profile_data["historical_scores"],
            trust_factors=profile_data["trust_factors"],
            created_at=datetime.fromisoformat(profile_data["created_at"]),
            last_updated=datetime.fromisoformat(profile_data["last_updated"]),
            total_evaluations=profile_data["total_evaluations"],
        )
        return TrustProfileResponse(user_id=user_id, profile=profile, found=True)
    except Exception as e:
        logger.error("Failed to retrieve trust profile for user %s: %s", user_id, e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve trust profile: {str(e)}",
        )


@router.post("/history", response_model=TrustHistoryResponse)
async def get_trust_history(
    request: TrustHistoryRequest,
    trust_engine: TrustScoringEngine = Depends(get_trust_engine),
):
    """Retrieve persisted trust evaluation history for a user."""
    try:
        records = trust_engine.get_history(
            request.user_id,
            limit=request.limit,
            start_time=request.start_time,
            end_time=request.end_time,
        )
        history = [_evaluation_from_record(record) for record in records]
        return TrustHistoryResponse(
            user_id=request.user_id,
            history=history,
            total_records=len(history),
        )
    except Exception as e:
        logger.error("Failed to retrieve trust history for user %s: %s", request.user_id, e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve trust history: {str(e)}",
        )


@router.get("/rules", response_model=TrustRulesResponse)
async def get_trust_rules(
    rule_validator: RuleValidator = Depends(get_rule_validator),
):
    """Retrieve active baseline trust policy rules."""
    try:
        rules = [
            TrustRule(
                rule_id=rule["rule_id"],
                name=rule["name"],
                description=rule["description"],
                condition=rule["condition"],
                weight=rule["weight"],
                enabled=rule["enabled"],
            )
            for rule in rule_validator.get_active_rules()
        ]
        return TrustRulesResponse(rules=rules, total_count=len(rules))
    except Exception as e:
        logger.error("Failed to retrieve trust rules: %s", e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve trust rules: {str(e)}",
        )


@router.get("/score/{user_id}")
async def get_current_trust_score(
    user_id: str,
    trust_engine: TrustScoringEngine = Depends(get_trust_engine),
):
    """Get the latest persisted trust score for a user."""
    try:
        current = trust_engine.get_current_score(user_id)
        if current is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No trust score found for user '{user_id}'",
            )
        return {
            "user_id": user_id,
            "trust_score": current["overall_trust_score"],
            "risk_level": current["risk_level"],
            "last_updated": current["last_updated"],
            "confidence": current["confidence_score"],
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to retrieve trust score for user %s: %s", user_id, e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve trust score: {str(e)}",
        )


@router.post("/refresh/{user_id}")
async def refresh_trust_score(
    user_id: str,
    context_data: dict | None = None,
    trust_engine: TrustScoringEngine = Depends(get_trust_engine),
):
    """Recalculate and persist a user trust score."""
    try:
        old = trust_engine.get_current_score(user_id)
        new = trust_engine.evaluate_trust(user_id=user_id, context=context_data or {})
        old_score = old["overall_trust_score"] if old else None
        change = None if old_score is None else new["overall_trust_score"] - old_score
        return {
            "user_id": user_id,
            "old_trust_score": old_score,
            "new_trust_score": new["overall_trust_score"],
            "change": change,
            "message": "Trust score refreshed successfully",
            "timestamp": new["last_updated"],
        }
    except Exception as e:
        logger.error("Failed to refresh trust score for user %s: %s", user_id, e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to refresh trust score: {str(e)}",
        )
