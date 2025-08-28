"""
OpenTelemetry Telemetry Manager for ReliQuary Observability

This module implements comprehensive telemetry collection, metrics aggregation,
tracing, and distributed observability for the ReliQuary enterprise platform.
"""

import asyncio
import time
import json
import logging
import threading
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional, Any, Union
from dataclasses import dataclass, asdict
from enum import Enum
from collections import defaultdict, deque
import uuid
import weakref

# OpenTelemetry imports with fallbacks
try:
    from opentelemetry import trace, metrics
    from opentelemetry.exporter.prometheus import PrometheusMetricReader
    from opentelemetry.exporter.jaeger.thrift import JaegerExporter
    from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
    from opentelemetry.sdk.trace import TracerProvider
    from opentelemetry.sdk.trace.export import BatchSpanProcessor
    from opentelemetry.sdk.metrics import MeterProvider
    from opentelemetry.sdk.resources import Resource
    from opentelemetry.semconv.resource import ResourceAttributes
    from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
    from opentelemetry.instrumentation.asyncio import AsyncioInstrumentor
    OTEL_AVAILABLE = True
except ImportError:
    OTEL_AVAILABLE = False
    logging.warning("OpenTelemetry not available - using simulation mode")

# Prometheus imports with fallbacks
try:
    import prometheus_client
    from prometheus_client import Counter, Histogram, Gauge, Summary, CollectorRegistry
    PROMETHEUS_AVAILABLE = True
except ImportError:
    PROMETHEUS_AVAILABLE = False
    logging.warning("Prometheus client not available - using basic metrics")

# Grafana/InfluxDB imports with fallbacks
try:
    import influxdb_client
    from influxdb_client import InfluxDBClient, Point, WritePrecision
    from influxdb_client.client.write_api import SYNCHRONOUS
    INFLUXDB_AVAILABLE = True
except ImportError:
    INFLUXDB_AVAILABLE = False
    logging.warning("InfluxDB client not available - using memory storage")


class TelemetryLevel(Enum):
    """Telemetry collection levels"""
    MINIMAL = "minimal"
    STANDARD = "standard"
    DETAILED = "detailed"
    DEBUG = "debug"


class MetricType(Enum):
    """Types of metrics collected"""
    COUNTER = "counter"
    GAUGE = "gauge" 
    HISTOGRAM = "histogram"
    SUMMARY = "summary"


class AlertSeverity(Enum):
    """Alert severity levels"""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


@dataclass
class TelemetryConfig:
    """Telemetry system configuration"""
    service_name: str
    service_version: str
    environment: str
    telemetry_level: TelemetryLevel
    jaeger_endpoint: Optional[str] = None
    prometheus_endpoint: Optional[str] = None
    influxdb_url: Optional[str] = None
    influxdb_token: Optional[str] = None
    influxdb_org: Optional[str] = None
    influxdb_bucket: Optional[str] = None
    sampling_rate: float = 1.0
    metrics_interval: int = 10
    enable_tracing: bool = True
    enable_metrics: bool = True
    enable_logging: bool = True


@dataclass
class MetricPoint:
    """Individual metric data point"""
    name: str
    value: float
    metric_type: MetricType
    timestamp: datetime
    labels: Dict[str, str]
    description: str


@dataclass
class TraceSpan:
    """Distributed trace span"""
    trace_id: str
    span_id: str
    parent_span_id: Optional[str]
    operation_name: str
    start_time: datetime
    end_time: Optional[datetime]
    duration_ms: Optional[float]
    status: str
    tags: Dict[str, Any]
    logs: List[Dict[str, Any]]


@dataclass
class Alert:
    """System alert"""
    alert_id: str
    severity: AlertSeverity
    title: str
    description: str
    metric_name: str
    threshold_value: float
    current_value: float
    labels: Dict[str, str]
    timestamp: datetime
    resolved: bool = False
    resolution_time: Optional[datetime] = None


class TelemetryManager:
    """Comprehensive telemetry management system"""
    
    def __init__(self, config: TelemetryConfig):
        self.config = config
        self.logger = logging.getLogger(f"telemetry.{config.service_name}")
        
        # OpenTelemetry components
        self.tracer_provider = None
        self.meter_provider = None
        self.tracer = None
        self.meter = None
        
        # Prometheus registry
        self.prometheus_registry = None
        self.prometheus_metrics = {}
        
        # InfluxDB client
        self.influxdb_client = None
        self.influxdb_write_api = None
        
        # Metrics storage
        self.metrics_buffer = deque(maxlen=10000)
        self.traces_buffer = deque(maxlen=1000)
        self.active_spans = {}
        
        # Alert system
        self.alert_rules = {}
        self.active_alerts = {}
        self.alert_history = deque(maxlen=1000)
        
        # Background processing
        self.background_tasks = []
        self.shutdown_event = threading.Event()
        
        self.logger.info(f"Telemetry Manager initialized for {config.service_name}")
    
    async def initialize(self) -> Dict[str, Any]:
        """Initialize telemetry system components"""
        try:
            results = {}
            
            # Initialize OpenTelemetry
            if self.config.enable_tracing and OTEL_AVAILABLE:
                otel_result = await self._initialize_opentelemetry()
                results['opentelemetry'] = otel_result
            
            # Initialize Prometheus
            if self.config.enable_metrics and PROMETHEUS_AVAILABLE:
                prometheus_result = await self._initialize_prometheus()
                results['prometheus'] = prometheus_result
            
            # Initialize InfluxDB
            if INFLUXDB_AVAILABLE and self.config.influxdb_url:
                influxdb_result = await self._initialize_influxdb()
                results['influxdb'] = influxdb_result
            
            # Setup alert rules
            await self._setup_default_alert_rules()
            results['alert_rules'] = len(self.alert_rules)
            
            # Start background tasks
            await self._start_background_tasks()
            results['background_tasks'] = len(self.background_tasks)
            
            self.logger.info(f"Telemetry system initialized: {results}")
            return results
            
        except Exception as e:
            self.logger.error(f"Telemetry initialization failed: {e}")
            return {"error": str(e)}
    
    async def _initialize_opentelemetry(self) -> Dict[str, Any]:
        """Initialize OpenTelemetry tracing and metrics"""
        try:
            # Create resource
            resource = Resource.create({
                ResourceAttributes.SERVICE_NAME: self.config.service_name,
                ResourceAttributes.SERVICE_VERSION: self.config.service_version,
                ResourceAttributes.DEPLOYMENT_ENVIRONMENT: self.config.environment
            })
            
            # Initialize tracing
            self.tracer_provider = TracerProvider(resource=resource)
            trace.set_tracer_provider(self.tracer_provider)
            
            # Add Jaeger exporter if configured
            if self.config.jaeger_endpoint:
                jaeger_exporter = JaegerExporter(
                    agent_host_name="localhost",
                    agent_port=14268,
                    collector_endpoint=self.config.jaeger_endpoint
                )
                self.tracer_provider.add_span_processor(
                    BatchSpanProcessor(jaeger_exporter)
                )
            
            # Add OTLP exporter for general telemetry
            otlp_exporter = OTLPSpanExporter(
                endpoint="http://localhost:4317",
                insecure=True
            )
            self.tracer_provider.add_span_processor(
                BatchSpanProcessor(otlp_exporter)
            )
            
            self.tracer = trace.get_tracer(__name__)
            
            # Initialize metrics
            metric_readers = []
            if PROMETHEUS_AVAILABLE:
                metric_readers.append(PrometheusMetricReader())
            
            self.meter_provider = MeterProvider(
                resource=resource,
                metric_readers=metric_readers
            )
            metrics.set_meter_provider(self.meter_provider)
            self.meter = metrics.get_meter(__name__)
            
            # Instrument FastAPI and asyncio
            FastAPIInstrumentor.instrument()
            AsyncioInstrumentor.instrument()
            
            return {
                "tracer_initialized": True,
                "meter_initialized": True,
                "instrumentation": ["fastapi", "asyncio"]
            }
            
        except Exception as e:
            self.logger.error(f"OpenTelemetry initialization failed: {e}")
            return {"error": str(e)}
    
    async def _initialize_prometheus(self) -> Dict[str, Any]:
        """Initialize Prometheus metrics collection"""
        try:
            self.prometheus_registry = CollectorRegistry()
            
            # Core system metrics
            self.prometheus_metrics = {
                'requests_total': Counter(
                    'reliquary_requests_total',
                    'Total number of requests',
                    ['method', 'endpoint', 'status_code'],
                    registry=self.prometheus_registry
                ),
                'request_duration_seconds': Histogram(
                    'reliquary_request_duration_seconds',
                    'Request duration in seconds',
                    ['method', 'endpoint'],
                    registry=self.prometheus_registry
                ),
                'active_connections': Gauge(
                    'reliquary_active_connections',
                    'Number of active connections',
                    registry=self.prometheus_registry
                ),
                'agent_count': Gauge(
                    'reliquary_agent_count',
                    'Number of active agents',
                    ['agent_type'],
                    registry=self.prometheus_registry
                ),
                'consensus_operations': Counter(
                    'reliquary_consensus_operations_total',
                    'Total consensus operations',
                    ['operation_type', 'status'],
                    registry=self.prometheus_registry
                ),
                'consensus_duration': Histogram(
                    'reliquary_consensus_duration_seconds',
                    'Consensus operation duration in seconds',
                    ['operation_type'],
                    registry=self.prometheus_registry
                ),
                'security_events': Counter(
                    'reliquary_security_events_total',
                    'Total security events',
                    ['event_type', 'severity'],
                    registry=self.prometheus_registry
                ),
                'system_health_score': Gauge(
                    'reliquary_system_health_score',
                    'Overall system health score (0-1)',
                    registry=self.prometheus_registry
                ),
                'memory_usage_bytes': Gauge(
                    'reliquary_memory_usage_bytes',
                    'Memory usage in bytes',
                    ['component'],
                    registry=self.prometheus_registry
                ),
                'cpu_usage_percent': Gauge(
                    'reliquary_cpu_usage_percent',
                    'CPU usage percentage',
                    ['component'],
                    registry=self.prometheus_registry
                )
            }
            
            return {
                "registry_created": True,
                "metrics_count": len(self.prometheus_metrics),
                "metrics": list(self.prometheus_metrics.keys())
            }
            
        except Exception as e:
            self.logger.error(f"Prometheus initialization failed: {e}")
            return {"error": str(e)}
    
    async def _initialize_influxdb(self) -> Dict[str, Any]:
        """Initialize InfluxDB for time-series data storage"""
        try:
            self.influxdb_client = InfluxDBClient(
                url=self.config.influxdb_url,
                token=self.config.influxdb_token,
                org=self.config.influxdb_org
            )
            
            # Test connection
            health = self.influxdb_client.health()
            if health.status != "pass":
                raise Exception(f"InfluxDB health check failed: {health.message}")
            
            self.influxdb_write_api = self.influxdb_client.write_api(write_options=SYNCHRONOUS)
            
            return {
                "connection_status": "connected",
                "health": health.status,
                "bucket": self.config.influxdb_bucket,
                "organization": self.config.influxdb_org
            }
            
        except Exception as e:
            self.logger.error(f"InfluxDB initialization failed: {e}")
            return {"error": str(e)}
    
    async def _setup_default_alert_rules(self):
        """Setup default alerting rules"""
        # CPU usage alerts
        self.add_alert_rule(
            "high_cpu_usage",
            metric_name="cpu_usage_percent",
            threshold=80.0,
            severity=AlertSeverity.WARNING,
            description="High CPU usage detected"
        )
        
        self.add_alert_rule(
            "critical_cpu_usage",
            metric_name="cpu_usage_percent",
            threshold=95.0,
            severity=AlertSeverity.CRITICAL,
            description="Critical CPU usage detected"
        )
        
        # Memory usage alerts
        self.add_alert_rule(
            "high_memory_usage",
            metric_name="memory_usage_percent",
            threshold=85.0,
            severity=AlertSeverity.WARNING,
            description="High memory usage detected"
        )
        
        # Consensus failure alerts
        self.add_alert_rule(
            "consensus_failure_rate",
            metric_name="consensus_failure_rate",
            threshold=10.0,
            severity=AlertSeverity.ERROR,
            description="High consensus failure rate"
        )
        
        # Security event alerts
        self.add_alert_rule(
            "security_events_spike",
            metric_name="security_events_per_minute",
            threshold=50.0,
            severity=AlertSeverity.ERROR,
            description="Spike in security events detected"
        )
        
        # Response time alerts
        self.add_alert_rule(
            "slow_response_time",
            metric_name="avg_response_time_ms",
            threshold=5000.0,
            severity=AlertSeverity.WARNING,
            description="Slow response times detected"
        )
    
    async def _start_background_tasks(self):
        """Start background telemetry processing tasks"""
        # Metrics collection task
        metrics_task = asyncio.create_task(self._metrics_collection_loop())
        self.background_tasks.append(metrics_task)
        
        # Alert evaluation task
        alert_task = asyncio.create_task(self._alert_evaluation_loop())
        self.background_tasks.append(alert_task)
        
        # Data persistence task
        if self.influxdb_write_api:
            persistence_task = asyncio.create_task(self._data_persistence_loop())
            self.background_tasks.append(persistence_task)
        
        self.logger.info(f"Started {len(self.background_tasks)} background tasks")
    
    async def _metrics_collection_loop(self):
        """Background metrics collection loop"""
        while not self.shutdown_event.is_set():
            try:
                # Collect system metrics
                await self._collect_system_metrics()
                
                # Process metrics buffer
                await self._process_metrics_buffer()
                
                await asyncio.sleep(self.config.metrics_interval)
                
            except Exception as e:
                self.logger.error(f"Metrics collection error: {e}")
                await asyncio.sleep(self.config.metrics_interval)
    
    async def _alert_evaluation_loop(self):
        """Background alert evaluation loop"""
        while not self.shutdown_event.is_set():
            try:
                await self._evaluate_alert_rules()
                await asyncio.sleep(30)  # Check alerts every 30 seconds
                
            except Exception as e:
                self.logger.error(f"Alert evaluation error: {e}")
                await asyncio.sleep(30)
    
    async def _data_persistence_loop(self):
        """Background data persistence loop"""
        while not self.shutdown_event.is_set():
            try:
                if self.influxdb_write_api:
                    await self._persist_metrics_to_influxdb()
                
                await asyncio.sleep(60)  # Persist every minute
                
            except Exception as e:
                self.logger.error(f"Data persistence error: {e}")
                await asyncio.sleep(60)
    
    async def _collect_system_metrics(self):
        """Collect system-level metrics"""
        try:
            import psutil
            
            # CPU metrics
            cpu_percent = psutil.cpu_percent(interval=1)
            self.record_metric("cpu_usage_percent", cpu_percent, MetricType.GAUGE, {"component": "system"})
            
            # Memory metrics
            memory = psutil.virtual_memory()
            self.record_metric("memory_usage_percent", memory.percent, MetricType.GAUGE, {"component": "system"})
            self.record_metric("memory_usage_bytes", memory.used, MetricType.GAUGE, {"component": "system"})
            
            # Disk metrics
            disk = psutil.disk_usage('/')
            disk_percent = (disk.used / disk.total) * 100
            self.record_metric("disk_usage_percent", disk_percent, MetricType.GAUGE, {"component": "system"})
            
            # Network metrics
            network = psutil.net_io_counters()
            self.record_metric("network_bytes_sent", network.bytes_sent, MetricType.COUNTER, {"component": "system"})
            self.record_metric("network_bytes_recv", network.bytes_recv, MetricType.COUNTER, {"component": "system"})
            
        except Exception as e:
            self.logger.error(f"System metrics collection failed: {e}")
    
    def record_metric(self, name: str, value: float, metric_type: MetricType, 
                     labels: Optional[Dict[str, str]] = None, description: str = ""):
        """Record a metric data point"""
        labels = labels or {}
        
        metric_point = MetricPoint(
            name=name,
            value=value,
            metric_type=metric_type,
            timestamp=datetime.now(),
            labels=labels,
            description=description
        )
        
        self.metrics_buffer.append(metric_point)
        
        # Update Prometheus metrics
        if PROMETHEUS_AVAILABLE and name in self.prometheus_metrics:
            self._update_prometheus_metric(name, value, metric_type, labels)
    
    def _update_prometheus_metric(self, name: str, value: float, 
                                 metric_type: MetricType, labels: Dict[str, str]):
        """Update Prometheus metrics"""
        try:
            prom_metric = self.prometheus_metrics.get(name)
            if not prom_metric:
                return
            
            if metric_type == MetricType.COUNTER:
                if labels:
                    prom_metric.labels(**labels).inc(value)
                else:
                    prom_metric.inc(value)
            elif metric_type == MetricType.GAUGE:
                if labels:
                    prom_metric.labels(**labels).set(value)
                else:
                    prom_metric.set(value)
            elif metric_type == MetricType.HISTOGRAM:
                if labels:
                    prom_metric.labels(**labels).observe(value)
                else:
                    prom_metric.observe(value)
                    
        except Exception as e:
            self.logger.error(f"Prometheus metric update failed: {e}")
    
    async def _process_metrics_buffer(self):
        """Process metrics buffer and calculate derived metrics"""
        if len(self.metrics_buffer) < 10:
            return
        
        try:
            # Calculate derived metrics
            recent_metrics = list(self.metrics_buffer)[-100:]  # Last 100 metrics
            
            # Calculate response time averages
            response_times = [m.value for m in recent_metrics if "response_time" in m.name]
            if response_times:
                avg_response_time = sum(response_times) / len(response_times)
                self.record_metric("avg_response_time_ms", avg_response_time, MetricType.GAUGE)
            
            # Calculate error rates
            error_counts = [m.value for m in recent_metrics if "error" in m.name]
            total_requests = [m.value for m in recent_metrics if "requests_total" in m.name]
            
            if error_counts and total_requests:
                error_rate = (sum(error_counts) / sum(total_requests)) * 100
                self.record_metric("error_rate_percent", error_rate, MetricType.GAUGE)
            
        except Exception as e:
            self.logger.error(f"Metrics buffer processing failed: {e}")
    
    def start_trace(self, operation_name: str, tags: Optional[Dict[str, Any]] = None) -> str:
        """Start a new distributed trace"""
        tags = tags or {}
        trace_id = str(uuid.uuid4())
        span_id = str(uuid.uuid4())
        
        span = TraceSpan(
            trace_id=trace_id,
            span_id=span_id,
            parent_span_id=None,
            operation_name=operation_name,
            start_time=datetime.now(),
            end_time=None,
            duration_ms=None,
            status="started",
            tags=tags,
            logs=[]
        )
        
        self.active_spans[span_id] = span
        
        # Create OpenTelemetry span if available
        if OTEL_AVAILABLE and self.tracer:
            otel_span = self.tracer.start_span(operation_name)
            for key, value in tags.items():
                otel_span.set_attribute(key, str(value))
            span.tags['otel_span'] = otel_span
        
        return span_id
    
    def end_trace(self, span_id: str, status: str = "completed", 
                  tags: Optional[Dict[str, Any]] = None):
        """End a distributed trace"""
        if span_id not in self.active_spans:
            return
        
        span = self.active_spans[span_id]
        span.end_time = datetime.now()
        span.duration_ms = (span.end_time - span.start_time).total_seconds() * 1000
        span.status = status
        
        if tags:
            span.tags.update(tags)
        
        # End OpenTelemetry span if available
        if 'otel_span' in span.tags:
            otel_span = span.tags['otel_span']
            otel_span.set_status(trace.Status(trace.StatusCode.OK if status == "completed" else trace.StatusCode.ERROR))
            otel_span.end()
        
        # Move to completed traces
        self.traces_buffer.append(span)
        del self.active_spans[span_id]
        
        # Record trace metrics
        self.record_metric(
            "trace_duration_ms",
            span.duration_ms,
            MetricType.HISTOGRAM,
            {"operation": span.operation_name, "status": status}
        )
    
    def add_alert_rule(self, rule_id: str, metric_name: str, threshold: float,
                      severity: AlertSeverity, description: str,
                      labels: Optional[Dict[str, str]] = None):
        """Add an alert rule"""
        self.alert_rules[rule_id] = {
            "metric_name": metric_name,
            "threshold": threshold,
            "severity": severity,
            "description": description,
            "labels": labels or {},
            "enabled": True
        }
    
    async def _evaluate_alert_rules(self):
        """Evaluate alert rules against current metrics"""
        try:
            recent_metrics = list(self.metrics_buffer)[-50:]  # Recent metrics
            
            for rule_id, rule in self.alert_rules.items():
                if not rule["enabled"]:
                    continue
                
                # Find matching metrics
                matching_metrics = [
                    m for m in recent_metrics 
                    if m.name == rule["metric_name"]
                ]
                
                if not matching_metrics:
                    continue
                
                # Get latest value
                latest_metric = matching_metrics[-1]
                current_value = latest_metric.value
                
                # Check threshold
                if current_value > rule["threshold"]:
                    await self._trigger_alert(rule_id, rule, current_value)
                elif rule_id in self.active_alerts:
                    await self._resolve_alert(rule_id)
                    
        except Exception as e:
            self.logger.error(f"Alert evaluation failed: {e}")
    
    async def _trigger_alert(self, rule_id: str, rule: Dict[str, Any], current_value: float):
        """Trigger an alert"""
        if rule_id in self.active_alerts:
            return  # Alert already active
        
        alert = Alert(
            alert_id=str(uuid.uuid4()),
            severity=rule["severity"],
            title=f"Alert: {rule['description']}",
            description=f"Metric {rule['metric_name']} has value {current_value:.2f}, exceeding threshold {rule['threshold']:.2f}",
            metric_name=rule["metric_name"],
            threshold_value=rule["threshold"],
            current_value=current_value,
            labels=rule["labels"],
            timestamp=datetime.now()
        )
        
        self.active_alerts[rule_id] = alert
        self.alert_history.append(alert)
        
        self.logger.warning(f"Alert triggered: {alert.title}")
        
        # Record alert metric
        self.record_metric(
            "alerts_triggered_total",
            1,
            MetricType.COUNTER,
            {"severity": alert.severity.value, "metric": alert.metric_name}
        )
    
    async def _resolve_alert(self, rule_id: str):
        """Resolve an active alert"""
        if rule_id not in self.active_alerts:
            return
        
        alert = self.active_alerts[rule_id]
        alert.resolved = True
        alert.resolution_time = datetime.now()
        
        del self.active_alerts[rule_id]
        
        self.logger.info(f"Alert resolved: {alert.title}")
        
        # Record resolution metric
        self.record_metric(
            "alerts_resolved_total",
            1,
            MetricType.COUNTER,
            {"severity": alert.severity.value, "metric": alert.metric_name}
        )
    
    async def _persist_metrics_to_influxdb(self):
        """Persist metrics to InfluxDB"""
        if not self.influxdb_write_api or len(self.metrics_buffer) == 0:
            return
        
        try:
            points = []
            
            # Convert metrics to InfluxDB points
            for metric in list(self.metrics_buffer):
                point = Point(metric.name) \
                    .field("value", metric.value) \
                    .time(metric.timestamp, WritePrecision.NS)
                
                # Add labels as tags
                for key, value in metric.labels.items():
                    point = point.tag(key, value)
                
                points.append(point)
            
            # Write points to InfluxDB
            self.influxdb_write_api.write(
                bucket=self.config.influxdb_bucket,
                record=points
            )
            
            self.logger.debug(f"Persisted {len(points)} metrics to InfluxDB")
            
        except Exception as e:
            self.logger.error(f"InfluxDB persistence failed: {e}")
    
    async def get_system_overview(self) -> Dict[str, Any]:
        """Get comprehensive system overview"""
        recent_metrics = list(self.metrics_buffer)[-100:] if self.metrics_buffer else []
        
        # Calculate key metrics
        cpu_usage = next((m.value for m in reversed(recent_metrics) if m.name == "cpu_usage_percent"), 0)
        memory_usage = next((m.value for m in reversed(recent_metrics) if m.name == "memory_usage_percent"), 0)
        
        return {
            "service_info": {
                "name": self.config.service_name,
                "version": self.config.service_version,
                "environment": self.config.environment,
                "telemetry_level": self.config.telemetry_level.value
            },
            "system_health": {
                "cpu_usage_percent": cpu_usage,
                "memory_usage_percent": memory_usage,
                "active_connections": len(self.active_spans),
                "metrics_collected": len(self.metrics_buffer),
                "traces_active": len(self.active_spans)
            },
            "alerts": {
                "active_alerts": len(self.active_alerts),
                "total_alert_rules": len(self.alert_rules),
                "alerts_last_24h": len([a for a in self.alert_history if (datetime.now() - a.timestamp).days < 1])
            },
            "integrations": {
                "opentelemetry": OTEL_AVAILABLE and self.tracer is not None,
                "prometheus": PROMETHEUS_AVAILABLE and self.prometheus_registry is not None,
                "influxdb": INFLUXDB_AVAILABLE and self.influxdb_client is not None
            },
            "background_tasks": len(self.background_tasks),
            "timestamp": datetime.now().isoformat()
        }
    
    async def shutdown(self):
        """Shutdown telemetry system"""
        self.logger.info("Shutting down telemetry system...")
        
        # Signal shutdown
        self.shutdown_event.set()
        
        # Wait for background tasks
        if self.background_tasks:
            await asyncio.gather(*self.background_tasks, return_exceptions=True)
        
        # Close connections
        if self.influxdb_client:
            self.influxdb_client.close()
        
        self.logger.info("Telemetry system shutdown complete")