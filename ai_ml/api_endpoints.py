"""
FastAPI Endpoints for ReliQuary AI/ML Enhanced Decision System

This module provides REST API endpoints for AI/ML enhanced decision processing,
intelligent analysis, and behavioral pattern recognition.
"""

import asyncio
import json
import logging
from datetime import datetime
from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field
from fastapi import APIRouter, HTTPException, BackgroundTasks, Depends, status

from ai_ml.integration_manager import (
    AIMLIntegrationManager, AIEnhancedDecisionRequest, AIEnhancedDecisionResult,
    create_ai_enhanced_request, process_batch_decisions
)
from ai_ml.decision_optimizer import OptimizationStrategy
from ai_ml.intelligence_engine import DecisionConfidence, IntelligenceModelType


# Global AI/ML integration manager
aiml_manager: Optional[AIMLIntegrationManager] = None


# Pydantic models for API
class AIDecisionRequest(BaseModel):
    """API model for AI-enhanced decision requests"""
    decision_type: str = Field(..., description="Type of decision (access_request, governance, emergency)")
    user_id: str = Field(..., description="User identifier")
    context_data: Dict[str, Any] = Field(..., description="Decision context data")
    user_data: Dict[str, Any] = Field(..., description="User profile data")
    activity_data: Dict[str, Any] = Field(..., description="User activity data")
    optimization_strategy: str = Field("balanced", description="Optimization strategy")
    audit_text: Optional[str] = Field(None, description="Audit text for NLP analysis")


class AIDecisionResponse(BaseModel):
    """API model for AI-enhanced decision responses"""
    request_id: str
    original_decision: str
    final_recommendation: str
    confidence_score: float
    risk_mitigation_score: float
    ai_reasoning: List[str]
    optimization_applied: str
    safeguards_recommended: List[str]
    processing_time_ms: float
    timestamp: str


class BatchDecisionRequest(BaseModel):
    """API model for batch decision processing"""
    decisions: List[AIDecisionRequest] = Field(..., description="List of decisions to process")
    parallel_processing: bool = Field(True, description="Enable parallel processing")


class TrainingDataRequest(BaseModel):
    """API model for model training data"""
    trust_data: Optional[List[Dict[str, Any]]] = Field(None, description="Trust prediction training data")
    normal_activity: Optional[List[Dict[str, Any]]] = Field(None, description="Normal activity patterns")
    threat_examples: Optional[List[Dict[str, Any]]] = Field(None, description="Threat examples")


class SystemStatusResponse(BaseModel):
    """API model for system status"""
    integration_id: str
    total_requests: int
    success_rate: float
    average_processing_time: float
    enhancement_effectiveness: float
    agent_systems_connected: bool
    model_status: Dict[str, Any]
    timestamp: str


# Create API router
router = APIRouter(prefix="/ai-ml", tags=["AI/ML Enhanced Decisions"])


async def get_aiml_manager():
    """Dependency to get AI/ML manager instance"""
    global aiml_manager
    if aiml_manager is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="AI/ML system not initialized"
        )
    return aiml_manager


@router.on_event("startup")
async def startup_aiml_system():
    """Initialize AI/ML system on startup"""
    global aiml_manager
    try:
        logging.info("Initializing AI/ML Enhanced Decision System...")
        
        aiml_manager = AIMLIntegrationManager()
        
        # Initialize with default training data if none provided
        init_result = await aiml_manager.initialize()
        
        logging.info(f"AI/ML system initialized: {init_result}")
        
    except Exception as e:
        logging.error(f"Failed to initialize AI/ML system: {e}")
        raise


@router.get("/health")
async def health_check():
    """Health check endpoint for AI/ML system"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "system": "ReliQuary AI/ML Enhanced Decisions",
        "version": "1.0.0"
    }


@router.get("/status", response_model=SystemStatusResponse)
async def get_system_status(manager: AIMLIntegrationManager = Depends(get_aiml_manager)):
    """Get comprehensive AI/ML system status"""
    try:
        status_data = await manager.get_system_status()
        
        return SystemStatusResponse(
            integration_id=status_data["integration_id"],
            total_requests=status_data["total_requests"],
            success_rate=status_data["success_rate"],
            average_processing_time=status_data["average_processing_time"],
            enhancement_effectiveness=status_data["enhancement_effectiveness"],
            agent_systems_connected=status_data["agent_systems_connected"],
            model_status=status_data["intelligence_engine"],
            timestamp=datetime.now().isoformat()
        )
        
    except Exception as e:
        logging.error(f"Failed to get system status: {e}")
        raise HTTPException(status_code=500, detail=f"Status check failed: {str(e)}")


@router.post("/decisions/enhance", response_model=AIDecisionResponse)
async def enhance_decision(
    request: AIDecisionRequest,
    background_tasks: BackgroundTasks,
    manager: AIMLIntegrationManager = Depends(get_aiml_manager)
):
    """Enhance a decision using AI/ML analysis"""
    try:
        # Validate optimization strategy
        try:
            strategy = OptimizationStrategy[request.optimization_strategy.upper()]
        except KeyError:
            strategy = OptimizationStrategy.BALANCED
        
        # Create AI-enhanced request
        ai_request = create_ai_enhanced_request(
            decision_type=request.decision_type,
            user_id=request.user_id,
            context_data=request.context_data,
            user_data=request.user_data,
            activity_data=request.activity_data,
            strategy=strategy,
            audit_text=request.audit_text
        )
        
        # Process decision
        result = await manager.process_ai_enhanced_decision(ai_request)
        
        # Convert processing time to milliseconds
        processing_time_ms = sum(result.processing_metrics.values()) * 1000
        
        # Extract AI reasoning
        ai_reasoning = result.intelligent_decision.reasoning.copy()
        ai_reasoning.extend(result.optimized_decision.reasoning)
        
        return AIDecisionResponse(
            request_id=result.request_id,
            original_decision=result.original_decision,
            final_recommendation=result.final_recommendation,
            confidence_score=result.confidence_score,
            risk_mitigation_score=result.risk_mitigation_score,
            ai_reasoning=ai_reasoning,
            optimization_applied=result.optimized_decision.optimization_strategy.value,
            safeguards_recommended=result.optimized_decision.safeguards_added,
            processing_time_ms=processing_time_ms,
            timestamp=result.timestamp.isoformat()
        )
        
    except Exception as e:
        logging.error(f"Decision enhancement failed: {e}")
        raise HTTPException(status_code=500, detail=f"Decision enhancement failed: {str(e)}")


@router.post("/decisions/batch")
async def process_batch_enhanced_decisions(
    request: BatchDecisionRequest,
    background_tasks: BackgroundTasks,
    manager: AIMLIntegrationManager = Depends(get_aiml_manager)
):
    """Process multiple decisions in batch"""
    try:
        if len(request.decisions) > 100:
            raise HTTPException(
                status_code=400,
                detail="Batch size cannot exceed 100 decisions"
            )
        
        # Convert to AI-enhanced requests
        ai_requests = []
        for decision in request.decisions:
            try:
                strategy = OptimizationStrategy[decision.optimization_strategy.upper()]
            except KeyError:
                strategy = OptimizationStrategy.BALANCED
            
            ai_request = create_ai_enhanced_request(
                decision_type=decision.decision_type,
                user_id=decision.user_id,
                context_data=decision.context_data,
                user_data=decision.user_data,
                activity_data=decision.activity_data,
                strategy=strategy,
                audit_text=decision.audit_text
            )
            ai_requests.append(ai_request)
        
        # Process decisions
        if request.parallel_processing:
            results = await process_batch_decisions(manager, ai_requests)
        else:
            results = []
            for ai_request in ai_requests:
                result = await manager.process_ai_enhanced_decision(ai_request)
                results.append(result)
        
        # Convert results
        response_results = []
        for result in results:
            if result is not None:
                processing_time_ms = sum(result.processing_metrics.values()) * 1000
                ai_reasoning = result.intelligent_decision.reasoning.copy() if result.intelligent_decision else []
                if result.optimized_decision:
                    ai_reasoning.extend(result.optimized_decision.reasoning)
                
                response_results.append(AIDecisionResponse(
                    request_id=result.request_id,
                    original_decision=result.original_decision,
                    final_recommendation=result.final_recommendation,
                    confidence_score=result.confidence_score,
                    risk_mitigation_score=result.risk_mitigation_score,
                    ai_reasoning=ai_reasoning,
                    optimization_applied=result.optimized_decision.optimization_strategy.value if result.optimized_decision else "none",
                    safeguards_recommended=result.optimized_decision.safeguards_added if result.optimized_decision else [],
                    processing_time_ms=processing_time_ms,
                    timestamp=result.timestamp.isoformat()
                ))
        
        return {
            "batch_id": f"batch_{int(datetime.now().timestamp())}",
            "total_decisions": len(request.decisions),
            "processed_decisions": len(response_results),
            "parallel_processing": request.parallel_processing,
            "results": response_results,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logging.error(f"Batch decision processing failed: {e}")
        raise HTTPException(status_code=500, detail=f"Batch processing failed: {str(e)}")


@router.post("/models/train")
async def train_models(
    training_data: TrainingDataRequest,
    background_tasks: BackgroundTasks,
    manager: AIMLIntegrationManager = Depends(get_aiml_manager)
):
    """Train AI/ML models with new data"""
    try:
        # Prepare training data
        train_data = {}
        if training_data.trust_data:
            train_data['trust_data'] = training_data.trust_data
        if training_data.normal_activity:
            train_data['normal_activity'] = training_data.normal_activity
        if training_data.threat_examples:
            train_data['threat_examples'] = training_data.threat_examples
        
        if not train_data:
            raise HTTPException(
                status_code=400,
                detail="No training data provided"
            )
        
        # Schedule retraining in background
        background_tasks.add_task(manager.retrain_models, train_data)
        
        return {
            "status": "training_scheduled",
            "message": "Model retraining scheduled in background",
            "training_data_size": sum(len(data) for data in train_data.values()),
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logging.error(f"Model training failed: {e}")
        raise HTTPException(status_code=500, detail=f"Model training failed: {str(e)}")


@router.get("/analytics/patterns")
async def analyze_decision_patterns(
    time_period_hours: int = 24,
    manager: AIMLIntegrationManager = Depends(get_aiml_manager)
):
    """Analyze decision patterns over a time period"""
    try:
        if time_period_hours < 1 or time_period_hours > 168:  # Max 1 week
            raise HTTPException(
                status_code=400,
                detail="Time period must be between 1 and 168 hours"
            )
        
        analysis = await manager.analyze_decision_patterns(time_period_hours)
        
        return {
            "analysis": analysis,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logging.error(f"Pattern analysis failed: {e}")
        raise HTTPException(status_code=500, detail=f"Pattern analysis failed: {str(e)}")


@router.get("/models/status")
async def get_model_status(manager: AIMLIntegrationManager = Depends(get_aiml_manager)):
    """Get detailed status of AI/ML models"""
    try:
        status = await manager.get_system_status()
        
        return {
            "intelligence_engine": status["intelligence_engine"],
            "model_availability": {
                "sklearn": status["intelligence_engine"].get("sklearn_available", False),
                "torch": status["intelligence_engine"].get("torch_available", False)
            },
            "cache_metrics": {
                "cache_size": status["cache_size"],
                "cache_utilization": "active" if status["cache_size"] > 0 else "empty"
            },
            "performance_metrics": {
                "total_requests": status["total_requests"],
                "success_rate": status["success_rate"],
                "average_processing_time": status["average_processing_time"],
                "enhancement_effectiveness": status["enhancement_effectiveness"]
            },
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logging.error(f"Model status check failed: {e}")
        raise HTTPException(status_code=500, detail=f"Model status check failed: {str(e)}")


@router.post("/decisions/simulate")
async def simulate_decision(
    request: AIDecisionRequest,
    manager: AIMLIntegrationManager = Depends(get_aiml_manager)
):
    """Simulate a decision without affecting system state"""
    try:
        # Add simulation flag to context
        simulation_context = request.context_data.copy()
        simulation_context['simulation_mode'] = True
        
        # Create simulation request
        try:
            strategy = OptimizationStrategy[request.optimization_strategy.upper()]
        except KeyError:
            strategy = OptimizationStrategy.BALANCED
        
        ai_request = create_ai_enhanced_request(
            decision_type=request.decision_type,
            user_id=request.user_id,
            context_data=simulation_context,
            user_data=request.user_data,
            activity_data=request.activity_data,
            strategy=strategy,
            audit_text=request.audit_text
        )
        
        # Process simulation (this doesn't affect caches or metrics)
        result = await manager.process_ai_enhanced_decision(ai_request)
        
        return {
            "simulation_result": {
                "original_decision": result.original_decision,
                "final_recommendation": result.final_recommendation,
                "confidence_score": result.confidence_score,
                "risk_mitigation_score": result.risk_mitigation_score,
                "ai_reasoning": result.intelligent_decision.reasoning if result.intelligent_decision else [],
                "risk_factors": result.intelligent_decision.risk_factors if result.intelligent_decision else [],
                "safeguards": result.optimized_decision.safeguards_added if result.optimized_decision else []
            },
            "simulation_mode": True,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logging.error(f"Decision simulation failed: {e}")
        raise HTTPException(status_code=500, detail=f"Decision simulation failed: {str(e)}")


@router.delete("/cache/clear")
async def clear_decision_cache(manager: AIMLIntegrationManager = Depends(get_aiml_manager)):
    """Clear the decision cache"""
    try:
        cache_size_before = len(manager.decision_cache)
        manager.decision_cache.clear()
        
        return {
            "status": "success",
            "message": "Decision cache cleared",
            "cache_entries_cleared": cache_size_before,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logging.error(f"Cache clear failed: {e}")
        raise HTTPException(status_code=500, detail=f"Cache clear failed: {str(e)}")