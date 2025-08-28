"""
Observability Integration Manager for ReliQuary

This module provides the main integration point for all observability components
including telemetry, alerting, monitoring, and dashboard integration.
"""

import asyncio
import json
import logging
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, asdict
from enum import Enum

from .telemetry_manager import TelemetryManager, TelemetryConfig, TelemetryLevel
from .alerting_system import IntelligentAlertManager, AlertPriority, NotificationChannel


class ObservabilityLevel(Enum):
    """Observability collection levels"""
    BASIC = "basic"
    STANDARD = "standard"
    COMPREHENSIVE = "comprehensive"
    DEBUG = "debug"


@dataclass
class ObservabilityConfig:
    """Comprehensive observability configuration"""
    service_name: str = "reliquary"
    service_version: str = "5.0.0"
    environment: str = "production"
    observability_level: ObservabilityLevel = ObservabilityLevel.STANDARD
    
    # Telemetry settings
    enable_telemetry: bool = True
    telemetry_level: TelemetryLevel = TelemetryLevel.STANDARD
    metrics_interval: int = 10
    
    # Alerting settings
    enable_alerting: bool = True
    alert_evaluation_interval: int = 30
    
    # Dashboard settings
    enable_dashboards: bool = True
    dashboard_refresh_interval: int = 60
    
    # Integration endpoints
    prometheus_endpoint: Optional[str] = None
    grafana_endpoint: Optional[str] = None
    jaeger_endpoint: Optional[str] = None
    influxdb_url: Optional[str] = None
    influxdb_token: Optional[str] = None
    influxdb_org: Optional[str] = None
    influxdb_bucket: Optional[str] = None


class ObservabilityManager:
    """Main observability system coordinator"""
    
    def __init__(self, config: ObservabilityConfig):
        self.config = config
        self.logger = logging.getLogger(f"observability.{config.service_name}")
        
        # Component managers
        self.telemetry_manager = None
        self.alert_manager = None
        
        # System state
        self.is_initialized = False
        self.start_time = datetime.now()
        
        # Background tasks
        self.background_tasks = []
        self.shutdown_event = asyncio.Event()
        
        # Performance tracking
        self.system_metrics = {
            "uptime_seconds": 0,
            "total_metrics_collected": 0,
            "total_alerts_triggered": 0,
            "total_traces_processed": 0,
            "observability_overhead_ms": 0.0
        }
        
        self.logger.info(f"Observability Manager initialized for {config.service_name}")
    
    async def initialize(self) -> Dict[str, Any]:
        """Initialize the complete observability system"""
        try:
            start_time = time.time()
            
            # Initialize telemetry manager
            telemetry_config = TelemetryConfig(
                service_name=self.config.service_name,
                service_version=self.config.service_version,
                environment=self.config.environment,
                telemetry_level=self.config.telemetry_level,
                jaeger_endpoint=self.config.jaeger_endpoint,
                prometheus_endpoint=self.config.prometheus_endpoint,
                influxdb_url=self.config.influxdb_url,
                influxdb_token=self.config.influxdb_token,
                influxdb_org=self.config.influxdb_org,
                influxdb_bucket=self.config.influxdb_bucket,
                metrics_interval=self.config.metrics_interval,
                enable_tracing=True,
                enable_metrics=True,
                enable_logging=True
            )
            
            if self.config.enable_telemetry:
                self.telemetry_manager = TelemetryManager(telemetry_config)
                telemetry_result = await self.telemetry_manager.initialize()
            else:
                telemetry_result = {"status": "disabled"}
            
            # Initialize alert manager
            if self.config.enable_alerting:
                self.alert_manager = IntelligentAlertManager()
                alert_result = await self.alert_manager.initialize()
            else:
                alert_result = {"status": "disabled"}
            
            # Start background monitoring
            await self._start_background_monitoring()
            
            # Start metric collection integration
            await self._start_metric_integration()
            
            self.is_initialized = True
            initialization_time = time.time() - start_time
            
            result = {
                "status": "initialized",
                "service_name": self.config.service_name,
                "observability_level": self.config.observability_level.value,
                "telemetry": telemetry_result,
                "alerting": alert_result,
                "background_tasks": len(self.background_tasks),
                "initialization_time_ms": initialization_time * 1000,
                "timestamp": datetime.now().isoformat()
            }
            
            self.logger.info(f"Observability system initialized successfully: {result}")
            return result
            
        except Exception as e:
            self.logger.error(f"Observability initialization failed: {e}")
            return {"status": "failed", "error": str(e)}
    
    async def _start_background_monitoring(self):
        """Start background monitoring tasks"""
        # System health monitoring
        health_task = asyncio.create_task(self._system_health_monitoring())
        self.background_tasks.append(health_task)
        
        # Performance monitoring
        performance_task = asyncio.create_task(self._performance_monitoring())
        self.background_tasks.append(performance_task)
        
        # Observability self-monitoring
        self_monitor_task = asyncio.create_task(self._observability_self_monitoring())
        self.background_tasks.append(self_monitor_task)
        
        self.logger.info(f"Started {len(self.background_tasks)} background monitoring tasks")
    
    async def _start_metric_integration(self):
        """Start metric collection integration between components"""
        if self.telemetry_manager and self.alert_manager:
            integration_task = asyncio.create_task(self._metric_alert_integration())
            self.background_tasks.append(integration_task)
    
    async def _system_health_monitoring(self):
        """Monitor overall system health"""
        while not self.shutdown_event.is_set():
            try:
                if self.telemetry_manager:
                    # Get system overview from telemetry
                    overview = await self.telemetry_manager.get_system_overview()
                    
                    # Record key health metrics
                    cpu_usage = overview["system_health"]["cpu_usage_percent"]
                    memory_usage = overview["system_health"]["memory_usage_percent"]
                    
                    # Calculate health score
                    health_score = self._calculate_health_score(cpu_usage, memory_usage)
                    
                    # Record health metrics
                    await self.record_metric("system_health_score", health_score)
                    await self.record_metric("observability_active_connections", 
                                           overview["system_health"]["active_connections"])
                
                await asyncio.sleep(60)  # Check every minute
                
            except Exception as e:
                self.logger.error(f"System health monitoring error: {e}")
                await asyncio.sleep(60)
    
    async def _performance_monitoring(self):
        """Monitor observability system performance"""
        while not self.shutdown_event.is_set():
            try:
                # Update uptime
                self.system_metrics["uptime_seconds"] = (datetime.now() - self.start_time).total_seconds()
                
                # Monitor telemetry performance
                if self.telemetry_manager:
                    telemetry_metrics = len(self.telemetry_manager.metrics_buffer)
                    self.system_metrics["total_metrics_collected"] = telemetry_metrics
                    
                    traces_active = len(self.telemetry_manager.active_spans)
                    self.system_metrics["total_traces_processed"] = traces_active
                
                # Monitor alert performance
                if self.alert_manager:
                    alert_stats = self.alert_manager.get_alert_statistics()
                    self.system_metrics["total_alerts_triggered"] = alert_stats["total_triggered"]
                
                # Record performance metrics
                await self.record_metric("observability_uptime_seconds", 
                                       self.system_metrics["uptime_seconds"])
                await self.record_metric("observability_metrics_collected", 
                                       self.system_metrics["total_metrics_collected"])
                
                await asyncio.sleep(self.config.dashboard_refresh_interval)
                
            except Exception as e:
                self.logger.error(f"Performance monitoring error: {e}")
                await asyncio.sleep(60)
    
    async def _observability_self_monitoring(self):
        """Monitor the observability system itself"""
        while not self.shutdown_event.is_set():
            try:
                start_time = time.time()
                
                # Check component health
                telemetry_healthy = self.telemetry_manager is not None
                alerting_healthy = self.alert_manager is not None
                
                # Calculate overhead
                overhead = (time.time() - start_time) * 1000
                self.system_metrics["observability_overhead_ms"] = overhead
                
                # Record self-monitoring metrics
                await self.record_metric("observability_telemetry_healthy", 1 if telemetry_healthy else 0)
                await self.record_metric("observability_alerting_healthy", 1 if alerting_healthy else 0)
                await self.record_metric("observability_overhead_ms", overhead)
                
                await asyncio.sleep(300)  # Self-monitor every 5 minutes
                
            except Exception as e:
                self.logger.error(f"Self-monitoring error: {e}")
                await asyncio.sleep(300)
    
    async def _metric_alert_integration(self):
        """Integrate metrics with alerting system"""
        while not self.shutdown_event.is_set():
            try:
                if not self.telemetry_manager or not self.alert_manager:
                    await asyncio.sleep(30)
                    continue
                
                # Get recent metrics from telemetry
                recent_metrics = list(self.telemetry_manager.metrics_buffer)[-50:]
                
                # Process each metric through alert system
                for metric in recent_metrics:
                    triggered_alerts = await self.alert_manager.evaluate_metric(
                        metric.name, metric.value, metric.timestamp
                    )
                    
                    if triggered_alerts:
                        self.logger.info(f"Triggered {len(triggered_alerts)} alerts for metric {metric.name}")
                
                await asyncio.sleep(self.config.alert_evaluation_interval)
                
            except Exception as e:
                self.logger.error(f"Metric-alert integration error: {e}")
                await asyncio.sleep(30)
    
    def _calculate_health_score(self, cpu_usage: float, memory_usage: float) -> float:
        """Calculate overall system health score (0-1)"""
        cpu_score = max(0, 1 - (cpu_usage / 100))
        memory_score = max(0, 1 - (memory_usage / 100))
        
        # Weighted average
        health_score = (cpu_score * 0.4 + memory_score * 0.6)
        return round(health_score, 3)
    
    async def record_metric(self, name: str, value: float, labels: Optional[Dict[str, str]] = None):
        """Record a metric through the observability system"""
        if self.telemetry_manager:
            from .telemetry_manager import MetricType
            self.telemetry_manager.record_metric(
                name, value, MetricType.GAUGE, labels
            )
    
    async def start_trace(self, operation_name: str, tags: Optional[Dict[str, Any]] = None) -> Optional[str]:
        """Start a distributed trace"""
        if self.telemetry_manager:
            return self.telemetry_manager.start_trace(operation_name, tags)
        return None
    
    async def end_trace(self, span_id: str, status: str = "completed", tags: Optional[Dict[str, Any]] = None):
        """End a distributed trace"""
        if self.telemetry_manager and span_id:
            self.telemetry_manager.end_trace(span_id, status, tags)
    
    async def trigger_alert(self, metric_name: str, value: float, 
                          description: str = "Manual alert trigger") -> Optional[str]:
        """Manually trigger an alert"""
        if self.alert_manager:
            triggered_alerts = await self.alert_manager.evaluate_metric(metric_name, value)
            if triggered_alerts:
                return triggered_alerts[0]
        return None
    
    async def get_system_dashboard(self) -> Dict[str, Any]:
        """Get comprehensive system dashboard data"""
        try:
            dashboard = {
                "service_info": {
                    "name": self.config.service_name,
                    "version": self.config.service_version,
                    "environment": self.config.environment,
                    "observability_level": self.config.observability_level.value,
                    "uptime_seconds": self.system_metrics["uptime_seconds"]
                },
                "system_status": {
                    "initialized": self.is_initialized,
                    "telemetry_enabled": self.telemetry_manager is not None,
                    "alerting_enabled": self.alert_manager is not None,
                    "background_tasks": len(self.background_tasks)
                },
                "metrics_summary": {
                    "total_metrics_collected": self.system_metrics["total_metrics_collected"],
                    "total_traces_processed": self.system_metrics["total_traces_processed"],
                    "observability_overhead_ms": self.system_metrics["observability_overhead_ms"]
                },
                "alerts_summary": {},
                "telemetry_overview": {},
                "timestamp": datetime.now().isoformat()
            }
            
            # Add telemetry overview
            if self.telemetry_manager:
                telemetry_overview = await self.telemetry_manager.get_system_overview()
                dashboard["telemetry_overview"] = telemetry_overview
            
            # Add alerts summary
            if self.alert_manager:
                alert_stats = self.alert_manager.get_alert_statistics()
                dashboard["alerts_summary"] = alert_stats
            
            return dashboard
            
        except Exception as e:
            self.logger.error(f"Dashboard generation failed: {e}")
            return {"error": str(e), "timestamp": datetime.now().isoformat()}
    
    async def get_health_check(self) -> Dict[str, Any]:
        """Get observability system health check"""
        try:
            health = {
                "status": "healthy" if self.is_initialized else "initializing",
                "components": {
                    "telemetry": "healthy" if self.telemetry_manager else "disabled",
                    "alerting": "healthy" if self.alert_manager else "disabled"
                },
                "uptime_seconds": self.system_metrics["uptime_seconds"],
                "background_tasks_running": len(self.background_tasks),
                "timestamp": datetime.now().isoformat()
            }
            
            # Check component health
            if self.telemetry_manager:
                try:
                    telemetry_overview = await self.telemetry_manager.get_system_overview()
                    health["components"]["telemetry"] = "healthy"
                except Exception:
                    health["components"]["telemetry"] = "unhealthy"
            
            if self.alert_manager:
                try:
                    alert_stats = self.alert_manager.get_alert_statistics()
                    health["components"]["alerting"] = "healthy"
                except Exception:
                    health["components"]["alerting"] = "unhealthy"
            
            # Overall status
            unhealthy_components = [k for k, v in health["components"].items() if v == "unhealthy"]
            if unhealthy_components:
                health["status"] = "degraded"
                health["unhealthy_components"] = unhealthy_components
            
            return health
            
        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    async def generate_metrics_export(self, format_type: str = "prometheus") -> str:
        """Generate metrics in specified format for external systems"""
        try:
            if format_type.lower() == "prometheus" and self.telemetry_manager:
                # Generate Prometheus format
                from prometheus_client import generate_latest, REGISTRY
                if self.telemetry_manager.prometheus_registry:
                    return generate_latest(self.telemetry_manager.prometheus_registry).decode('utf-8')
            
            # Default JSON format
            dashboard = await self.get_system_dashboard()
            return json.dumps(dashboard, indent=2)
            
        except Exception as e:
            self.logger.error(f"Metrics export failed: {e}")
            return f"# Error generating metrics: {e}"
    
    async def shutdown(self):
        """Shutdown the observability system"""
        self.logger.info("Shutting down observability system...")
        
        # Signal shutdown
        self.shutdown_event.set()
        
        # Wait for background tasks
        if self.background_tasks:
            await asyncio.gather(*self.background_tasks, return_exceptions=True)
        
        # Shutdown components
        if self.telemetry_manager:
            await self.telemetry_manager.shutdown()
        
        if self.alert_manager:
            await self.alert_manager.shutdown()
        
        self.logger.info("Observability system shutdown complete")


# Utility functions for easy integration

async def create_observability_manager(
    service_name: str = "reliquary",
    environment: str = "production",
    observability_level: ObservabilityLevel = ObservabilityLevel.STANDARD
) -> ObservabilityManager:
    """Create and initialize observability manager with default config"""
    config = ObservabilityConfig(
        service_name=service_name,
        environment=environment,
        observability_level=observability_level
    )
    
    manager = ObservabilityManager(config)
    await manager.initialize()
    return manager


async def setup_basic_observability() -> ObservabilityManager:
    """Setup basic observability for development/testing"""
    config = ObservabilityConfig(
        service_name="reliquary-dev",
        environment="development",
        observability_level=ObservabilityLevel.BASIC,
        enable_telemetry=True,
        enable_alerting=True,
        enable_dashboards=False
    )
    
    manager = ObservabilityManager(config)
    await manager.initialize()
    return manager