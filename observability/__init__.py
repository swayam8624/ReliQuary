"""
ReliQuary Observability System

This package provides comprehensive observability capabilities including:
- OpenTelemetry-based distributed tracing and metrics
- Intelligent alerting with correlation and automation
- Grafana dashboard integration
- Real-time monitoring and performance analytics
- Enterprise-scale monitoring for 100+ agents

Main Components:
- TelemetryManager: Core telemetry collection and processing
- IntelligentAlertManager: Advanced alerting with automation
- ObservabilityManager: Central coordinator and integration point
- Grafana dashboards: Pre-configured monitoring dashboards
- FastAPI endpoints: REST API for observability operations

Usage:
    from observability import ObservabilityManager, ObservabilityConfig
    
    config = ObservabilityConfig(
        service_name="my_service",
        environment="production"
    )
    
    manager = ObservabilityManager(config)
    await manager.initialize()
    
    # Record metrics
    await manager.record_metric("cpu_usage", 75.0)
    
    # Start distributed trace
    span_id = await manager.start_trace("operation_name")
    await manager.end_trace(span_id, "completed")
"""

from .telemetry_manager import (
    TelemetryManager,
    TelemetryConfig,
    TelemetryLevel,
    MetricType,
    MetricPoint,
    TraceSpan
)

from .alerting_system import (
    IntelligentAlertManager,
    AlertRule,
    AlertPriority,
    NotificationChannel,
    AlertState,
    Alert
)

from .integration_manager import (
    ObservabilityManager,
    ObservabilityConfig,
    ObservabilityLevel,
    create_observability_manager,
    setup_basic_observability
)

from .grafana_dashboards import (
    GrafanaDashboardConfig,
    GRAFANA_ALERT_RULES,
    save_dashboard_configs
)

__version__ = "5.0.0"
__author__ = "ReliQuary Team"

__all__ = [
    # Core managers
    "TelemetryManager",
    "IntelligentAlertManager", 
    "ObservabilityManager",
    
    # Configuration
    "TelemetryConfig",
    "ObservabilityConfig",
    
    # Enums and constants
    "TelemetryLevel",
    "ObservabilityLevel",
    "MetricType",
    "AlertPriority",
    "NotificationChannel",
    "AlertState",
    
    # Data models
    "MetricPoint",
    "TraceSpan",
    "Alert",
    "AlertRule",
    
    # Dashboard integration
    "GrafanaDashboardConfig",
    "GRAFANA_ALERT_RULES",
    "save_dashboard_configs",
    
    # Utility functions
    "create_observability_manager",
    "setup_basic_observability"
]