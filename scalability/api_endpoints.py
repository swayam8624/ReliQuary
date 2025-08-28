"""
FastAPI Endpoints for ReliQuary Enterprise Scalability System

This module provides REST API endpoints for scalability management,
performance monitoring, and enterprise-scale system administration.
"""

import asyncio
import logging
from datetime import datetime
from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field
from fastapi import APIRouter, HTTPException, BackgroundTasks, Depends, status

from scalability.integration_manager import ScalabilityManager, ScalabilityMetrics, ScalingStrategy, DeploymentMode
from scalability.performance_monitor import PerformanceLevel, SystemHealth
from scalability.agent_pool import AgentType, PoolStatus
from scalability.distributed_consensus import ConsensusRequest


# Global scalability manager
scalability_manager: Optional[ScalabilityManager] = None


# Pydantic models for API
class SystemInitializationRequest(BaseModel):
    """API model for system initialization"""
    deployment_name: str = Field("reliquary_enterprise", description="Deployment name")
    max_total_agents: int = Field(100, ge=10, le=200, description="Maximum total agents")
    initial_agent_config: Optional[Dict[str, int]] = Field(None, description="Initial agent configuration")
    scaling_strategy: str = Field("hybrid", description="Scaling strategy")
    deployment_mode: str = Field("production", description="Deployment mode")
    enable_auto_scaling: bool = Field(True, description="Enable automatic scaling")


class ConsensusRequest(BaseModel):
    """API model for consensus requests"""
    request_type: str = Field(..., description="Type of consensus request")
    payload: Dict[str, Any] = Field(..., description="Request payload")
    priority: int = Field(5, ge=1, le=10, description="Request priority")
    timeout_seconds: float = Field(30.0, ge=1.0, le=300.0, description="Request timeout")
    minimum_consensus: float = Field(0.6, ge=0.1, le=1.0, description="Minimum consensus threshold")


class ScalingRequest(BaseModel):
    """API model for manual scaling requests"""
    agent_type: str = Field(..., description="Type of agent to scale")
    scale_direction: str = Field(..., description="Scale direction: up or down")
    scale_amount: int = Field(1, ge=1, le=10, description="Number of agents to scale")
    reason: str = Field("manual_request", description="Reason for scaling")


class SystemStatusResponse(BaseModel):
    """API model for system status"""
    deployment_name: str
    system_initialized: bool
    total_agents: int
    active_clusters: int
    system_health: str
    consensus_success_rate: float
    average_response_time: float
    throughput: float
    efficiency_score: float
    monitoring_active: bool
    auto_scaling_enabled: bool
    timestamp: str


class PerformanceMetricsResponse(BaseModel):
    """API model for performance metrics"""
    cpu_usage: float
    memory_usage: float
    disk_usage: float
    network_io: Dict[str, float]
    active_agents: int
    pending_decisions: int
    bottlenecks: List[str]
    recommendations: List[str]
    timestamp: str


class AgentPoolStatusResponse(BaseModel):
    """API model for agent pool status"""
    pool_name: str
    status: str
    total_agents: int
    agents_by_type: Dict[str, int]
    agents_by_status: Dict[str, int]
    efficiency: float
    total_requests_processed: int
    recent_scaling_events: List[Dict[str, Any]]
    timestamp: str


# Create API router
router = APIRouter(prefix="/scalability", tags=["Enterprise Scalability"])


async def get_scalability_manager():
    """Dependency to get scalability manager instance"""
    global scalability_manager
    if scalability_manager is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Scalability system not initialized"
        )
    return scalability_manager


@router.on_event("startup")
async def startup_scalability_system():
    """Initialize scalability system on startup"""
    global scalability_manager
    try:
        logging.info("Initializing Enterprise Scalability System...")
        scalability_manager = ScalabilityManager("reliquary_api_deployment")
        logging.info("Scalability system created - call /scalability/initialize to start")
    except Exception as e:
        logging.error(f"Failed to create scalability system: {e}")
        raise


@router.get("/health")
async def health_check():
    """Health check endpoint for scalability system"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "system": "ReliQuary Enterprise Scalability",
        "version": "1.0.0"
    }


@router.post("/initialize")
async def initialize_system(
    request: SystemInitializationRequest,
    background_tasks: BackgroundTasks,
    manager: ScalabilityManager = Depends(get_scalability_manager)
):
    """Initialize the enterprise scalability system"""
    try:
        # Update configuration
        manager.config.max_total_agents = request.max_total_agents
        manager.config.enable_auto_scaling = request.enable_auto_scaling
        
        try:
            manager.config.scaling_strategy = ScalingStrategy[request.scaling_strategy.upper()]
        except KeyError:
            manager.config.scaling_strategy = ScalingStrategy.HYBRID
        
        try:
            manager.config.deployment_mode = DeploymentMode[request.deployment_mode.upper()]
        except KeyError:
            manager.config.deployment_mode = DeploymentMode.PRODUCTION
        
        # Initialize system
        result = await manager.initialize_system(request.initial_agent_config)
        
        return {
            "status": "success",
            "message": "Scalability system initialized successfully",
            "initialization_result": result,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logging.error(f"System initialization failed: {e}")
        raise HTTPException(status_code=500, detail=f"Initialization failed: {str(e)}")


@router.get("/status", response_model=SystemStatusResponse)
async def get_system_status(manager: ScalabilityManager = Depends(get_scalability_manager)):
    """Get comprehensive system status"""
    try:
        if not manager.system_initialized:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="System not initialized - call /scalability/initialize first"
            )
        
        metrics = manager.get_scalability_metrics()
        
        return SystemStatusResponse(
            deployment_name=manager.deployment_name,
            system_initialized=manager.system_initialized,
            total_agents=metrics.total_agents,
            active_clusters=metrics.active_clusters,
            system_health=metrics.system_health.value,
            consensus_success_rate=metrics.consensus_success_rate,
            average_response_time=metrics.average_response_time,
            throughput=metrics.throughput,
            efficiency_score=metrics.efficiency_score,
            monitoring_active=manager.monitoring_active,
            auto_scaling_enabled=manager.config.enable_auto_scaling,
            timestamp=metrics.timestamp.isoformat()
        )
        
    except Exception as e:
        logging.error(f"Status check failed: {e}")
        raise HTTPException(status_code=500, detail=f"Status check failed: {str(e)}")


@router.get("/metrics", response_model=PerformanceMetricsResponse)
async def get_performance_metrics(manager: ScalabilityManager = Depends(get_scalability_manager)):
    """Get detailed performance metrics"""
    try:
        system_health = manager.performance_monitor.assess_system_health()
        
        return PerformanceMetricsResponse(
            cpu_usage=system_health.cpu_usage,
            memory_usage=system_health.memory_usage,
            disk_usage=system_health.disk_usage,
            network_io=system_health.network_io,
            active_agents=system_health.active_agents,
            pending_decisions=system_health.pending_decisions,
            bottlenecks=system_health.bottlenecks,
            recommendations=system_health.recommendations,
            timestamp=system_health.timestamp.isoformat()
        )
        
    except Exception as e:
        logging.error(f"Metrics collection failed: {e}")
        raise HTTPException(status_code=500, detail=f"Metrics collection failed: {str(e)}")


@router.get("/agents/pool", response_model=AgentPoolStatusResponse)
async def get_agent_pool_status(manager: ScalabilityManager = Depends(get_scalability_manager)):
    """Get agent pool status and statistics"""
    try:
        pool_status = manager.agent_pool.get_pool_status()
        
        return AgentPoolStatusResponse(
            pool_name=pool_status["pool_name"],
            status=pool_status["status"],
            total_agents=pool_status["total_agents"],
            agents_by_type=pool_status["agents_by_type"],
            agents_by_status=pool_status["agents_by_status"],
            efficiency=pool_status["efficiency"],
            total_requests_processed=pool_status["total_requests_processed"],
            recent_scaling_events=pool_status["recent_scaling_events"],
            timestamp=pool_status["timestamp"]
        )
        
    except Exception as e:
        logging.error(f"Agent pool status failed: {e}")
        raise HTTPException(status_code=500, detail=f"Agent pool status failed: {str(e)}")


@router.post("/consensus")
async def process_consensus_request(
    request: ConsensusRequest,
    background_tasks: BackgroundTasks,
    manager: ScalabilityManager = Depends(get_scalability_manager)
):
    """Process a consensus request through the scalable system"""
    try:
        if not manager.system_initialized:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="System not initialized"
            )
        
        # Convert request to internal format
        request_data = {
            "request_id": f"api_req_{int(datetime.now().timestamp())}",
            "request_type": request.request_type,
            "payload": request.payload,
            "priority": request.priority,
            "timeout_seconds": request.timeout_seconds,
            "minimum_consensus": request.minimum_consensus
        }
        
        # Process consensus request
        result = await manager.process_consensus_request(request_data)
        
        return {
            "request_id": result.request_id,
            "consensus_reached": result.consensus_reached,
            "final_decision": result.final_decision,
            "participating_clusters": result.participating_clusters,
            "global_consensus_confidence": result.global_consensus_confidence,
            "processing_time": result.processing_time,
            "timestamp": result.timestamp.isoformat()
        }
        
    except Exception as e:
        logging.error(f"Consensus request failed: {e}")
        raise HTTPException(status_code=500, detail=f"Consensus request failed: {str(e)}")


@router.post("/scaling/manual")
async def manual_scaling_request(
    request: ScalingRequest,
    background_tasks: BackgroundTasks,
    manager: ScalabilityManager = Depends(get_scalability_manager)
):
    """Execute manual scaling request"""
    try:
        if not manager.system_initialized:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="System not initialized"
            )
        
        # Validate agent type
        try:
            agent_type = AgentType[request.agent_type.upper()]
        except KeyError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid agent type: {request.agent_type}"
            )
        
        # Validate scale direction
        if request.scale_direction.lower() not in ["up", "down"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Scale direction must be 'up' or 'down'"
            )
        
        # Execute scaling
        if request.scale_direction.lower() == "up":
            await manager._scale_up_system(agent_type, request.scale_amount, request.reason)
        else:
            await manager._scale_down_system(agent_type, request.scale_amount, request.reason)
        
        return {
            "status": "success",
            "message": f"Manual scaling {request.scale_direction} executed",
            "agent_type": request.agent_type,
            "scale_amount": request.scale_amount,
            "reason": request.reason,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logging.error(f"Manual scaling failed: {e}")
        raise HTTPException(status_code=500, detail=f"Manual scaling failed: {str(e)}")


@router.get("/scaling/history")
async def get_scaling_history(
    limit: int = 50,
    manager: ScalabilityManager = Depends(get_scalability_manager)
):
    """Get scaling event history"""
    try:
        history = manager.scaling_history[-limit:] if manager.scaling_history else []
        
        return {
            "scaling_events": history,
            "total_events": len(manager.scaling_history),
            "returned_events": len(history),
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logging.error(f"Scaling history retrieval failed: {e}")
        raise HTTPException(status_code=500, detail=f"Scaling history failed: {str(e)}")


@router.get("/alerts")
async def get_system_alerts(
    limit: int = 20,
    manager: ScalabilityManager = Depends(get_scalability_manager)
):
    """Get system alerts and warnings"""
    try:
        alerts = manager.system_alerts[-limit:] if manager.system_alerts else []
        
        return {
            "alerts": alerts,
            "total_alerts": len(manager.system_alerts),
            "returned_alerts": len(alerts),
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logging.error(f"Alerts retrieval failed: {e}")
        raise HTTPException(status_code=500, detail=f"Alerts retrieval failed: {str(e)}")


@router.get("/consensus/metrics")
async def get_consensus_metrics(manager: ScalabilityManager = Depends(get_scalability_manager)):
    """Get consensus system metrics"""
    try:
        if not manager.system_initialized:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="System not initialized"
            )
        
        metrics = manager.consensus_manager.get_consensus_metrics()
        
        return {
            "consensus_metrics": metrics,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logging.error(f"Consensus metrics failed: {e}")
        raise HTTPException(status_code=500, detail=f"Consensus metrics failed: {str(e)}")


@router.post("/configuration/update")
async def update_configuration(
    configuration: Dict[str, Any],
    manager: ScalabilityManager = Depends(get_scalability_manager)
):
    """Update system configuration"""
    try:
        # Update supported configuration parameters
        if "max_total_agents" in configuration:
            manager.config.max_total_agents = configuration["max_total_agents"]
        
        if "enable_auto_scaling" in configuration:
            manager.config.enable_auto_scaling = configuration["enable_auto_scaling"]
        
        if "monitoring_interval" in configuration:
            manager.config.monitoring_interval = configuration["monitoring_interval"]
        
        if "performance_thresholds" in configuration:
            manager.config.performance_thresholds.update(configuration["performance_thresholds"])
        
        return {
            "status": "success",
            "message": "Configuration updated successfully",
            "updated_config": {
                "max_total_agents": manager.config.max_total_agents,
                "enable_auto_scaling": manager.config.enable_auto_scaling,
                "monitoring_interval": manager.config.monitoring_interval,
                "performance_thresholds": manager.config.performance_thresholds
            },
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logging.error(f"Configuration update failed: {e}")
        raise HTTPException(status_code=500, detail=f"Configuration update failed: {str(e)}")


@router.get("/performance/history")
async def get_performance_history(
    hours: int = 24,
    manager: ScalabilityManager = Depends(get_scalability_manager)
):
    """Get performance history for specified time period"""
    try:
        # Filter performance history by time
        from datetime import timedelta
        cutoff_time = datetime.now() - timedelta(hours=hours)
        
        filtered_history = [
            entry for entry in manager.performance_history
            if datetime.fromisoformat(entry["timestamp"]) > cutoff_time
        ]
        
        return {
            "performance_history": filtered_history,
            "total_entries": len(manager.performance_history),
            "filtered_entries": len(filtered_history),
            "time_period_hours": hours,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logging.error(f"Performance history retrieval failed: {e}")
        raise HTTPException(status_code=500, detail=f"Performance history failed: {str(e)}")


@router.post("/shutdown")
async def shutdown_system(
    background_tasks: BackgroundTasks,
    manager: ScalabilityManager = Depends(get_scalability_manager)
):
    """Gracefully shutdown the scalability system"""
    try:
        # Schedule shutdown in background
        background_tasks.add_task(manager.shutdown)
        
        return {
            "status": "success",
            "message": "Scalability system shutdown initiated",
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logging.error(f"System shutdown failed: {e}")
        raise HTTPException(status_code=500, detail=f"System shutdown failed: {str(e)}")


@router.get("/diagnostics")
async def get_system_diagnostics(manager: ScalabilityManager = Depends(get_scalability_manager)):
    """Get comprehensive system diagnostics"""
    try:
        diagnostics = {
            "deployment_name": manager.deployment_name,
            "system_initialized": manager.system_initialized,
            "monitoring_active": manager.monitoring_active,
            "configuration": {
                "max_total_agents": manager.config.max_total_agents,
                "scaling_strategy": manager.config.scaling_strategy.value,
                "deployment_mode": manager.config.deployment_mode.value,
                "auto_scaling_enabled": manager.config.enable_auto_scaling,
                "predictive_scaling_enabled": manager.config.enable_predictive_scaling
            },
            "component_status": {
                "performance_monitor": manager.performance_monitor is not None,
                "consensus_manager": manager.consensus_manager is not None,
                "agent_pool": manager.agent_pool is not None,
                "load_predictor": manager.load_predictor is not None
            },
            "system_health": manager.get_scalability_metrics() if manager.system_initialized else None,
            "timestamp": datetime.now().isoformat()
        }
        
        return diagnostics
        
    except Exception as e:
        logging.error(f"Diagnostics failed: {e}")
        raise HTTPException(status_code=500, detail=f"Diagnostics failed: {str(e)}")