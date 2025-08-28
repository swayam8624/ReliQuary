"""
FastAPI Endpoints for ReliQuary Observability System

This module provides REST API endpoints for observability, monitoring,
alerting, and dashboard integration.
"""

import asyncio
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field
from fastapi import APIRouter, HTTPException, BackgroundTasks, Depends, status, Response

from .integration_manager import ObservabilityManager, ObservabilityConfig, ObservabilityLevel
from .telemetry_manager import MetricType
from .alerting_system import AlertPriority


# Global observability manager
observability_manager: Optional[ObservabilityManager] = None


# Pydantic models for API
class MetricRequest(BaseModel):
    """API model for metric recording"""
    name: str = Field(..., description="Metric name")
    value: float = Field(..., description="Metric value")
    metric_type: str = Field("gauge", description="Metric type (counter, gauge, histogram, summary)")
    labels: Optional[Dict[str, str]] = Field(None, description="Metric labels")
    timestamp: Optional[str] = Field(None, description="ISO timestamp (optional)")


class TraceRequest(BaseModel):
    """API model for trace operations"""
    operation_name: str = Field(..., description="Operation name")
    tags: Optional[Dict[str, Any]] = Field(None, description="Trace tags")


class AlertTriggerRequest(BaseModel):
    """API model for manual alert triggering"""
    metric_name: str = Field(..., description="Metric name to evaluate")
    value: float = Field(..., description="Metric value")
    description: Optional[str] = Field("Manual alert trigger", description="Alert description")


class SystemHealthResponse(BaseModel):
    """API model for system health response"""
    status: str
    components: Dict[str, str]
    uptime_seconds: float
    background_tasks_running: int
    timestamp: str


class DashboardResponse(BaseModel):
    """API model for dashboard data"""
    service_info: Dict[str, Any]
    system_status: Dict[str, Any]
    metrics_summary: Dict[str, Any]
    alerts_summary: Dict[str, Any]
    telemetry_overview: Dict[str, Any]
    timestamp: str


# Create API router
router = APIRouter(prefix="/observability", tags=["Observability"])


async def get_observability_manager():
    """Dependency to get observability manager instance"""
    global observability_manager
    if observability_manager is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Observability system not initialized"
        )
    return observability_manager


@router.on_event("startup")
async def startup_observability_system():
    """Initialize observability system on startup"""
    global observability_manager
    try:
        logging.info("Initializing ReliQuary Observability System...")
        
        # Create observability configuration
        config = ObservabilityConfig(
            service_name="reliquary",
            service_version="5.0.0",
            environment="production",
            observability_level=ObservabilityLevel.COMPREHENSIVE,
            enable_telemetry=True,
            enable_alerting=True,
            enable_dashboards=True,
            metrics_interval=10,
            alert_evaluation_interval=30
        )
        
        observability_manager = ObservabilityManager(config)
        init_result = await observability_manager.initialize()
        
        logging.info(f"Observability system initialized: {init_result}")
        
    except Exception as e:
        logging.error(f"Failed to initialize observability system: {e}")
        raise


@router.get("/health")
async def health_check():
    """Health check endpoint for observability system"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "system": "ReliQuary Observability System",
        "version": "5.0.0"
    }


@router.get("/status", response_model=SystemHealthResponse)
async def get_system_health(manager: ObservabilityManager = Depends(get_observability_manager)):
    """Get comprehensive system health status"""
    try:
        health_data = await manager.get_health_check()
        
        return SystemHealthResponse(
            status=health_data["status"],
            components=health_data["components"],
            uptime_seconds=health_data["uptime_seconds"],
            background_tasks_running=health_data["background_tasks_running"],
            timestamp=health_data["timestamp"]
        )
        
    except Exception as e:
        logging.error(f"Failed to get system health: {e}")
        raise HTTPException(status_code=500, detail=f"Health check failed: {str(e)}")


@router.get("/dashboard", response_model=DashboardResponse)
async def get_system_dashboard(manager: ObservabilityManager = Depends(get_observability_manager)):
    """Get comprehensive system dashboard data"""
    try:
        dashboard_data = await manager.get_system_dashboard()
        
        return DashboardResponse(
            service_info=dashboard_data["service_info"],
            system_status=dashboard_data["system_status"],
            metrics_summary=dashboard_data["metrics_summary"],
            alerts_summary=dashboard_data["alerts_summary"],
            telemetry_overview=dashboard_data["telemetry_overview"],
            timestamp=dashboard_data["timestamp"]
        )
        
    except Exception as e:
        logging.error(f"Failed to get dashboard data: {e}")
        raise HTTPException(status_code=500, detail=f"Dashboard generation failed: {str(e)}")


@router.post("/metrics/record")
async def record_metric(
    request: MetricRequest,
    manager: ObservabilityManager = Depends(get_observability_manager)
):
    """Record a custom metric"""
    try:
        # Parse timestamp if provided
        timestamp = None
        if request.timestamp:
            timestamp = datetime.fromisoformat(request.timestamp.replace('Z', '+00:00'))
        
        # Record the metric
        await manager.record_metric(
            name=request.name,
            value=request.value,
            labels=request.labels
        )
        
        return {
            "status": "success",
            "message": f"Metric '{request.name}' recorded successfully",
            "metric": {
                "name": request.name,
                "value": request.value,
                "type": request.metric_type,
                "labels": request.labels
            },
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logging.error(f"Failed to record metric: {e}")
        raise HTTPException(status_code=500, detail=f"Metric recording failed: {str(e)}")


@router.post("/metrics/batch")
async def record_metrics_batch(
    metrics: List[MetricRequest],
    manager: ObservabilityManager = Depends(get_observability_manager)
):
    """Record multiple metrics in batch"""
    try:
        if len(metrics) > 100:
            raise HTTPException(
                status_code=400,
                detail="Batch size cannot exceed 100 metrics"
            )
        
        recorded_count = 0
        failed_count = 0
        
        for metric in metrics:
            try:
                await manager.record_metric(
                    name=metric.name,
                    value=metric.value,
                    labels=metric.labels
                )
                recorded_count += 1
            except Exception as e:
                logging.error(f"Failed to record metric {metric.name}: {e}")
                failed_count += 1
        
        return {
            "status": "completed",
            "total_metrics": len(metrics),
            "recorded_successfully": recorded_count,
            "failed": failed_count,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logging.error(f"Batch metric recording failed: {e}")
        raise HTTPException(status_code=500, detail=f"Batch recording failed: {str(e)}")


@router.post("/traces/start")
async def start_trace(
    request: TraceRequest,
    manager: ObservabilityManager = Depends(get_observability_manager)
):
    """Start a new distributed trace"""
    try:
        span_id = await manager.start_trace(
            operation_name=request.operation_name,
            tags=request.tags
        )
        
        if span_id:
            return {
                "status": "success",
                "span_id": span_id,
                "operation_name": request.operation_name,
                "timestamp": datetime.now().isoformat()
            }
        else:
            return {
                "status": "tracing_disabled",
                "message": "Distributed tracing is not enabled",
                "timestamp": datetime.now().isoformat()
            }
        
    except Exception as e:
        logging.error(f"Failed to start trace: {e}")
        raise HTTPException(status_code=500, detail=f"Trace start failed: {str(e)}")


@router.post("/traces/{span_id}/end")
async def end_trace(
    span_id: str,
    status_value: str = "completed",
    tags: Optional[Dict[str, Any]] = None,
    manager: ObservabilityManager = Depends(get_observability_manager)
):
    """End a distributed trace"""
    try:
        await manager.end_trace(span_id, status_value, tags)
        
        return {
            "status": "success",
            "span_id": span_id,
            "trace_status": status_value,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logging.error(f"Failed to end trace: {e}")
        raise HTTPException(status_code=500, detail=f"Trace end failed: {str(e)}")


@router.post("/alerts/trigger")
async def trigger_manual_alert(
    request: AlertTriggerRequest,
    manager: ObservabilityManager = Depends(get_observability_manager)
):
    """Manually trigger an alert for testing or emergency situations"""
    try:
        alert_id = await manager.trigger_alert(
            metric_name=request.metric_name,
            value=request.value,
            description=request.description
        )
        
        if alert_id:
            return {
                "status": "alert_triggered",
                "alert_id": alert_id,
                "metric_name": request.metric_name,
                "value": request.value,
                "description": request.description,
                "timestamp": datetime.now().isoformat()
            }
        else:
            return {
                "status": "no_alert_triggered",
                "message": "No alert rules matched the provided metric",
                "metric_name": request.metric_name,
                "value": request.value,
                "timestamp": datetime.now().isoformat()
            }
        
    except Exception as e:
        logging.error(f"Failed to trigger alert: {e}")
        raise HTTPException(status_code=500, detail=f"Alert trigger failed: {str(e)}")


@router.get("/alerts/active")
async def get_active_alerts(manager: ObservabilityManager = Depends(get_observability_manager)):
    """Get all currently active alerts"""
    try:
        if not manager.alert_manager:
            raise HTTPException(status_code=503, detail="Alert manager not available")
        
        alert_stats = manager.alert_manager.get_alert_statistics()
        
        # Get detailed active alerts
        active_alerts = []
        for alert in manager.alert_manager.active_alerts.values():
            active_alerts.append({
                "alert_id": alert.alert_id,
                "title": alert.title,
                "description": alert.description,
                "priority": alert.priority.value,
                "state": alert.state.value,
                "current_value": alert.current_value,
                "threshold_value": alert.threshold_value,
                "first_triggered": alert.first_triggered.isoformat(),
                "escalation_level": alert.escalation_level
            })
        
        return {
            "active_alerts": active_alerts,
            "summary": alert_stats,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logging.error(f"Failed to get active alerts: {e}")
        raise HTTPException(status_code=500, detail=f"Alert retrieval failed: {str(e)}")


@router.get("/metrics/export")
async def export_metrics(
    format_type: str = "json",
    manager: ObservabilityManager = Depends(get_observability_manager)
):
    """Export metrics in various formats (json, prometheus)"""
    try:
        if format_type.lower() not in ["json", "prometheus"]:
            raise HTTPException(
                status_code=400,
                detail="Supported formats: json, prometheus"
            )
        
        exported_data = await manager.generate_metrics_export(format_type)
        
        if format_type.lower() == "prometheus":
            return Response(
                content=exported_data,
                media_type="text/plain; version=0.0.4; charset=utf-8"
            )
        else:
            return Response(
                content=exported_data,
                media_type="application/json"
            )
        
    except Exception as e:
        logging.error(f"Failed to export metrics: {e}")
        raise HTTPException(status_code=500, detail=f"Metrics export failed: {str(e)}")


@router.get("/analytics/system-overview")
async def get_system_analytics(
    time_range_hours: int = 24,
    manager: ObservabilityManager = Depends(get_observability_manager)
):
    """Get system analytics and trends over specified time range"""
    try:
        if time_range_hours < 1 or time_range_hours > 168:  # Max 1 week
            raise HTTPException(
                status_code=400,
                detail="Time range must be between 1 and 168 hours"
            )
        
        # Get current dashboard data
        dashboard_data = await manager.get_system_dashboard()
        
        # Add analytics calculations
        analytics = {
            "time_range_hours": time_range_hours,
            "current_metrics": dashboard_data["metrics_summary"],
            "current_alerts": dashboard_data["alerts_summary"],
            "system_trends": {
                "uptime_hours": dashboard_data["service_info"]["uptime_seconds"] / 3600,
                "observability_overhead": dashboard_data["metrics_summary"].get("observability_overhead_ms", 0),
                "health_trend": "stable"  # Would calculate from historical data
            },
            "performance_indicators": {
                "metrics_collection_rate": dashboard_data["metrics_summary"]["total_metrics_collected"] / max(1, dashboard_data["service_info"]["uptime_seconds"]),
                "alert_frequency": dashboard_data["alerts_summary"].get("total_triggered", 0) / max(1, dashboard_data["service_info"]["uptime_seconds"] / 3600),
                "system_stability": "high" if dashboard_data["alerts_summary"].get("active_alerts", 0) < 5 else "medium"
            },
            "recommendations": [],
            "timestamp": datetime.now().isoformat()
        }
        
        # Generate recommendations
        if analytics["performance_indicators"]["alert_frequency"] > 1:
            analytics["recommendations"].append("Consider reviewing alert thresholds - high alert frequency detected")
        
        if analytics["performance_indicators"]["metrics_collection_rate"] < 0.1:
            analytics["recommendations"].append("Metrics collection rate is low - consider increasing monitoring coverage")
        
        if not analytics["recommendations"]:
            analytics["recommendations"].append("System is performing well - no immediate action required")
        
        return analytics
        
    except Exception as e:
        logging.error(f"Failed to get system analytics: {e}")
        raise HTTPException(status_code=500, detail=f"Analytics generation failed: {str(e)}")


@router.get("/config")
async def get_observability_config(manager: ObservabilityManager = Depends(get_observability_manager)):
    """Get current observability system configuration"""
    try:
        config = manager.config
        
        return {
            "service_name": config.service_name,
            "service_version": config.service_version,
            "environment": config.environment,
            "observability_level": config.observability_level.value,
            "telemetry_enabled": config.enable_telemetry,
            "alerting_enabled": config.enable_alerting,
            "dashboards_enabled": config.enable_dashboards,
            "metrics_interval": config.metrics_interval,
            "alert_evaluation_interval": config.alert_evaluation_interval,
            "integrations": {
                "prometheus_endpoint": config.prometheus_endpoint,
                "grafana_endpoint": config.grafana_endpoint,
                "jaeger_endpoint": config.jaeger_endpoint,
                "influxdb_configured": bool(config.influxdb_url)
            },
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logging.error(f"Failed to get configuration: {e}")
        raise HTTPException(status_code=500, detail=f"Configuration retrieval failed: {str(e)}")


@router.post("/maintenance/cleanup")
async def maintenance_cleanup(
    background_tasks: BackgroundTasks,
    manager: ObservabilityManager = Depends(get_observability_manager)
):
    """Perform maintenance cleanup of observability data"""
    try:
        def cleanup_task():
            # In a real implementation, this would clean up old metrics, traces, and alerts
            logging.info("Performing observability maintenance cleanup...")
            # Cleanup logic here
            logging.info("Maintenance cleanup completed")
        
        background_tasks.add_task(cleanup_task)
        
        return {
            "status": "cleanup_scheduled",
            "message": "Maintenance cleanup scheduled in background",
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logging.error(f"Failed to schedule maintenance cleanup: {e}")
        raise HTTPException(status_code=500, detail=f"Cleanup scheduling failed: {str(e)}")


@router.get("/integrations/status")
async def get_integration_status(manager: ObservabilityManager = Depends(get_observability_manager)):
    """Get status of external integrations (Prometheus, Grafana, etc.)"""
    try:
        integration_status = {
            "prometheus": {
                "enabled": manager.telemetry_manager and manager.telemetry_manager.prometheus_registry is not None,
                "endpoint": manager.config.prometheus_endpoint,
                "metrics_exposed": True if manager.telemetry_manager else False
            },
            "grafana": {
                "enabled": manager.config.enable_dashboards,
                "endpoint": manager.config.grafana_endpoint,
                "dashboards_available": manager.config.enable_dashboards
            },
            "jaeger": {
                "enabled": manager.telemetry_manager and manager.config.jaeger_endpoint is not None,
                "endpoint": manager.config.jaeger_endpoint,
                "tracing_active": manager.telemetry_manager and len(manager.telemetry_manager.active_spans) > 0
            },
            "influxdb": {
                "enabled": manager.telemetry_manager and manager.telemetry_manager.influxdb_client is not None,
                "url": manager.config.influxdb_url,
                "bucket": manager.config.influxdb_bucket
            },
            "timestamp": datetime.now().isoformat()
        }
        
        return integration_status
        
    except Exception as e:
        logging.error(f"Failed to get integration status: {e}")
        raise HTTPException(status_code=500, detail=f"Integration status failed: {str(e)}")