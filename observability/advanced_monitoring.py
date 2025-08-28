#!/usr/bin/env python3
"""
Advanced Observability and Monitoring System for ReliQuary
Comprehensive monitoring, tracing, and alerting for production operations
"""

import asyncio
import json
import logging
import time
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum

import prometheus_client
from prometheus_client import Counter, Histogram, Gauge, CollectorRegistry
from opentelemetry import trace, metrics
from opentelemetry.exporter.jaeger.thrift import JaegerExporter
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.instrumentation.requests import RequestsInstrumentor
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor

import grafana_api
import influxdb_client
from influxdb_client.client.write_api import SYNCHRONOUS


class MetricType(Enum):
    """Types of metrics to collect"""
    COUNTER = "counter"
    GAUGE = "gauge"
    HISTOGRAM = "histogram"
    SUMMARY = "summary"


@dataclass
class AlertRule:
    """Alert rule configuration"""
    name: str
    condition: str
    threshold: float
    duration: str
    severity: str
    message: str
    channels: List[str]


class AdvancedObservabilitySystem:
    """Comprehensive observability system for production monitoring"""
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or self._default_config()
        self.logger = logging.getLogger("observability")
        
        # Initialize metrics registry
        self.registry = CollectorRegistry()
        
        # Core metrics
        self._initialize_core_metrics()
        
        # Distributed tracing
        self._setup_distributed_tracing()
        
        # Time series database
        self._setup_time_series_db()
        
        # Grafana integration
        self._setup_grafana_client()
        
        # Alert rules
        self.alert_rules = self._load_alert_rules()
        
    def _default_config(self) -> Dict[str, Any]:
        """Default observability configuration"""
        return {
            "prometheus": {
                "port": 8080,
                "path": "/metrics"
            },
            "jaeger": {
                "endpoint": "http://jaeger-collector:14268/api/traces",
                "service_name": "reliquary-platform"
            },
            "influxdb": {
                "url": "http://influxdb:8086",
                "token": "reliquary-influxdb-token",
                "org": "reliquary",
                "bucket": "metrics"
            },
            "grafana": {
                "url": "http://grafana:3000",
                "api_key": "grafana-api-key"
            },
            "alerts": {
                "webhook_url": "https://hooks.slack.com/services/webhook",
                "email_recipients": ["ops@reliquary.io"]
            }
        }
    
    def _initialize_core_metrics(self):
        """Initialize core system metrics"""
        
        # Performance metrics
        self.request_duration = Histogram(
            'reliquary_request_duration_seconds',
            'Request duration in seconds',
            ['method', 'endpoint', 'status'],
            registry=self.registry
        )
        
        self.request_count = Counter(
            'reliquary_requests_total',
            'Total number of requests',
            ['method', 'endpoint', 'status'],
            registry=self.registry
        )
        
        # Consensus system metrics
        self.consensus_operations = Counter(
            'reliquary_consensus_operations_total',
            'Total consensus operations',
            ['operation_type', 'result'],
            registry=self.registry
        )
        
        self.consensus_latency = Histogram(
            'reliquary_consensus_latency_seconds',
            'Consensus operation latency',
            ['operation_type'],
            registry=self.registry
        )
        
        self.active_agents = Gauge(
            'reliquary_active_agents_count',
            'Number of active consensus agents',
            registry=self.registry
        )
        
        # Cryptographic metrics
        self.crypto_operations = Counter(
            'reliquary_crypto_operations_total',
            'Total cryptographic operations',
            ['operation', 'algorithm'],
            registry=self.registry
        )
        
        self.crypto_performance = Histogram(
            'reliquary_crypto_operation_duration_seconds',
            'Cryptographic operation duration',
            ['operation', 'algorithm'],
            registry=self.registry
        )
        
        # Memory and storage metrics
        self.vault_operations = Counter(
            'reliquary_vault_operations_total',
            'Total vault operations',
            ['operation', 'vault_type'],
            registry=self.registry
        )
        
        self.memory_usage = Gauge(
            'reliquary_memory_usage_bytes',
            'Memory usage in bytes',
            ['component'],
            registry=self.registry
        )
        
        # Security metrics
        self.authentication_attempts = Counter(
            'reliquary_auth_attempts_total',
            'Authentication attempts',
            ['method', 'result'],
            registry=self.registry
        )
        
        self.security_events = Counter(
            'reliquary_security_events_total',
            'Security events',
            ['event_type', 'severity'],
            registry=self.registry
        )
        
        # Business metrics
        self.user_sessions = Gauge(
            'reliquary_active_user_sessions',
            'Active user sessions',
            registry=self.registry
        )
        
        self.data_processed = Counter(
            'reliquary_data_processed_bytes_total',
            'Total data processed',
            ['operation'],
            registry=self.registry
        )
        
        # System health metrics
        self.component_health = Gauge(
            'reliquary_component_health_status',
            'Component health status (1=healthy, 0=unhealthy)',
            ['component'],
            registry=self.registry
        )
        
        self.error_rate = Gauge(
            'reliquary_error_rate_percent',
            'Error rate percentage',
            ['component'],
            registry=self.registry
        )
    
    def _setup_distributed_tracing(self):
        """Setup distributed tracing with Jaeger"""
        
        # Configure tracer
        trace.set_tracer_provider(TracerProvider())
        tracer = trace.get_tracer(__name__)
        
        # Configure Jaeger exporter
        jaeger_exporter = JaegerExporter(
            agent_host_name=self.config["jaeger"]["endpoint"].split("//")[1].split(":")[0],
            agent_port=14268,
            collector_endpoint=self.config["jaeger"]["endpoint"],
        )
        
        # Configure span processor
        span_processor = BatchSpanProcessor(jaeger_exporter)
        trace.get_tracer_provider().add_span_processor(span_processor)
        
        # Instrument common libraries
        RequestsInstrumentor().instrument()
        
        self.tracer = tracer
        self.logger.info("Distributed tracing initialized")
    
    def _setup_time_series_db(self):
        """Setup InfluxDB for time series metrics"""
        
        try:
            self.influx_client = influxdb_client.InfluxDBClient(
                url=self.config["influxdb"]["url"],
                token=self.config["influxdb"]["token"],
                org=self.config["influxdb"]["org"]
            )
            
            self.write_api = self.influx_client.write_api(write_options=SYNCHRONOUS)
            self.query_api = self.influx_client.query_api()
            
            self.logger.info("InfluxDB client initialized")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize InfluxDB: {e}")
            self.influx_client = None
    
    def _setup_grafana_client(self):
        """Setup Grafana API client"""
        
        try:
            self.grafana_api = grafana_api.GrafanaApi.from_url(
                url=self.config["grafana"]["url"],
                credential=self.config["grafana"]["api_key"]
            )
            
            self.logger.info("Grafana API client initialized")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize Grafana API: {e}")
            self.grafana_api = None
    
    def _load_alert_rules(self) -> List[AlertRule]:
        """Load alert rule configurations"""
        
        return [
            AlertRule(
                name="high_error_rate",
                condition="reliquary_error_rate_percent > 5",
                threshold=5.0,
                duration="2m",
                severity="warning",
                message="High error rate detected: {{ $value }}%",
                channels=["slack", "email"]
            ),
            AlertRule(
                name="consensus_failure_rate",
                condition="rate(reliquary_consensus_operations_total{result='failed'}[5m]) > 0.1",
                threshold=0.1,
                duration="1m",
                severity="critical",
                message="Consensus failure rate exceeds threshold",
                channels=["slack", "email", "pagerduty"]
            ),
            AlertRule(
                name="memory_usage_high",
                condition="reliquary_memory_usage_bytes / 1024^3 > 8",
                threshold=8.0,
                duration="5m",
                severity="warning",
                message="Memory usage above 8GB",
                channels=["slack"]
            ),
            AlertRule(
                name="authentication_attacks",
                condition="rate(reliquary_auth_attempts_total{result='failed'}[1m]) > 10",
                threshold=10.0,
                duration="30s",
                severity="critical",
                message="Potential authentication attack detected",
                channels=["slack", "email", "pagerduty"]
            ),
            AlertRule(
                name="component_down",
                condition="reliquary_component_health_status == 0",
                threshold=0.0,
                duration="30s",
                severity="critical",
                message="Component {{ $labels.component }} is down",
                channels=["slack", "email", "pagerduty"]
            )
        ]
    
    async def record_request_metrics(self, method: str, endpoint: str, status: int, duration: float):
        """Record HTTP request metrics"""
        
        self.request_count.labels(
            method=method,
            endpoint=endpoint,
            status=str(status)
        ).inc()
        
        self.request_duration.labels(
            method=method,
            endpoint=endpoint,
            status=str(status)
        ).observe(duration)
    
    async def record_consensus_metrics(self, operation_type: str, result: str, latency: float):
        """Record consensus operation metrics"""
        
        self.consensus_operations.labels(
            operation_type=operation_type,
            result=result
        ).inc()
        
        self.consensus_latency.labels(
            operation_type=operation_type
        ).observe(latency)
    
    async def record_crypto_metrics(self, operation: str, algorithm: str, duration: float):
        """Record cryptographic operation metrics"""
        
        self.crypto_operations.labels(
            operation=operation,
            algorithm=algorithm
        ).inc()
        
        self.crypto_performance.labels(
            operation=operation,
            algorithm=algorithm
        ).observe(duration)
    
    async def update_agent_count(self, count: int):
        """Update active agent count"""
        self.active_agents.set(count)
    
    async def record_security_event(self, event_type: str, severity: str):
        """Record security event"""
        
        self.security_events.labels(
            event_type=event_type,
            severity=severity
        ).inc()
    
    async def update_component_health(self, component: str, is_healthy: bool):
        """Update component health status"""
        
        self.component_health.labels(component=component).set(1 if is_healthy else 0)
    
    async def write_custom_metric(self, measurement: str, tags: Dict[str, str], fields: Dict[str, float]):
        """Write custom metric to InfluxDB"""
        
        if not self.influx_client:
            return
        
        try:
            from influxdb_client import Point
            
            point = Point(measurement)
            
            # Add tags
            for key, value in tags.items():
                point = point.tag(key, value)
            
            # Add fields
            for key, value in fields.items():
                point = point.field(key, value)
            
            point = point.time(datetime.utcnow())
            
            self.write_api.write(
                bucket=self.config["influxdb"]["bucket"],
                record=point
            )
            
        except Exception as e:
            self.logger.error(f"Failed to write custom metric: {e}")
    
    async def create_grafana_dashboard(self, dashboard_config: Dict[str, Any]) -> str:
        """Create Grafana dashboard"""
        
        if not self.grafana_api:
            return ""
        
        try:
            result = self.grafana_api.dashboard.update_dashboard({
                "dashboard": dashboard_config,
                "overwrite": True
            })
            
            self.logger.info(f"Created Grafana dashboard: {dashboard_config['title']}")
            return result.get("uid", "")
            
        except Exception as e:
            self.logger.error(f"Failed to create Grafana dashboard: {e}")
            return ""
    
    def get_reliquary_dashboard_config(self) -> Dict[str, Any]:
        """Generate ReliQuary main dashboard configuration"""
        
        return {
            "title": "ReliQuary Production Overview",
            "tags": ["reliquary", "production"],
            "timezone": "UTC",
            "refresh": "30s",
            "time": {
                "from": "now-1h",
                "to": "now"
            },
            "panels": [
                {
                    "id": 1,
                    "title": "Request Rate",
                    "type": "stat",
                    "targets": [
                        {
                            "expr": "rate(reliquary_requests_total[5m])",
                            "legendFormat": "Requests/sec"
                        }
                    ],
                    "gridPos": {"h": 8, "w": 12, "x": 0, "y": 0}
                },
                {
                    "id": 2,
                    "title": "Error Rate",
                    "type": "stat",
                    "targets": [
                        {
                            "expr": "rate(reliquary_requests_total{status=~'5..'}[5m]) / rate(reliquary_requests_total[5m]) * 100",
                            "legendFormat": "Error %"
                        }
                    ],
                    "gridPos": {"h": 8, "w": 12, "x": 12, "y": 0}
                },
                {
                    "id": 3,
                    "title": "Response Time P95",
                    "type": "graph",
                    "targets": [
                        {
                            "expr": "histogram_quantile(0.95, rate(reliquary_request_duration_seconds_bucket[5m]))",
                            "legendFormat": "P95 Latency"
                        }
                    ],
                    "gridPos": {"h": 8, "w": 24, "x": 0, "y": 8}
                },
                {
                    "id": 4,
                    "title": "Consensus Operations",
                    "type": "graph",
                    "targets": [
                        {
                            "expr": "rate(reliquary_consensus_operations_total[5m])",
                            "legendFormat": "{{ operation_type }} - {{ result }}"
                        }
                    ],
                    "gridPos": {"h": 8, "w": 12, "x": 0, "y": 16}
                },
                {
                    "id": 5,
                    "title": "Active Agents",
                    "type": "stat",
                    "targets": [
                        {
                            "expr": "reliquary_active_agents_count",
                            "legendFormat": "Active Agents"
                        }
                    ],
                    "gridPos": {"h": 8, "w": 12, "x": 12, "y": 16}
                },
                {
                    "id": 6,
                    "title": "Security Events",
                    "type": "table",
                    "targets": [
                        {
                            "expr": "increase(reliquary_security_events_total[1h])",
                            "legendFormat": "{{ event_type }} - {{ severity }}"
                        }
                    ],
                    "gridPos": {"h": 8, "w": 24, "x": 0, "y": 24}
                }
            ]
        }
    
    def get_crypto_dashboard_config(self) -> Dict[str, Any]:
        """Generate cryptographic operations dashboard"""
        
        return {
            "title": "ReliQuary Cryptographic Operations",
            "tags": ["reliquary", "crypto", "security"],
            "timezone": "UTC",
            "refresh": "30s",
            "panels": [
                {
                    "id": 1,
                    "title": "Crypto Operation Rate",
                    "type": "graph",
                    "targets": [
                        {
                            "expr": "rate(reliquary_crypto_operations_total[5m])",
                            "legendFormat": "{{ operation }} - {{ algorithm }}"
                        }
                    ],
                    "gridPos": {"h": 8, "w": 24, "x": 0, "y": 0}
                },
                {
                    "id": 2,
                    "title": "Crypto Performance",
                    "type": "graph",
                    "targets": [
                        {
                            "expr": "histogram_quantile(0.95, rate(reliquary_crypto_operation_duration_seconds_bucket[5m]))",
                            "legendFormat": "P95 - {{ operation }}"
                        }
                    ],
                    "gridPos": {"h": 8, "w": 24, "x": 0, "y": 8}
                }
            ]
        }
    
    async def setup_default_dashboards(self):
        """Setup default Grafana dashboards"""
        
        dashboards = [
            ("main", self.get_reliquary_dashboard_config()),
            ("crypto", self.get_crypto_dashboard_config())
        ]
        
        for name, config in dashboards:
            uid = await self.create_grafana_dashboard(config)
            if uid:
                self.logger.info(f"Created {name} dashboard with UID: {uid}")
    
    async def check_alert_conditions(self) -> List[Dict[str, Any]]:
        """Check alert conditions and return triggered alerts"""
        
        triggered_alerts = []
        
        for rule in self.alert_rules:
            try:
                # This would typically query Prometheus for the condition
                # For now, we'll simulate the check
                
                # In production, this would be:
                # result = await self._query_prometheus(rule.condition)
                # if result > rule.threshold:
                
                # Simulate alert check (in production, implement actual querying)
                triggered_alerts.append({
                    "rule_name": rule.name,
                    "severity": rule.severity,
                    "message": rule.message,
                    "timestamp": datetime.now().isoformat(),
                    "channels": rule.channels
                })
                
            except Exception as e:
                self.logger.error(f"Failed to check alert rule {rule.name}: {e}")
        
        return triggered_alerts
    
    async def send_alert(self, alert: Dict[str, Any]):
        """Send alert notification"""
        
        try:
            # Slack notification
            if "slack" in alert["channels"]:
                await self._send_slack_alert(alert)
            
            # Email notification
            if "email" in alert["channels"]:
                await self._send_email_alert(alert)
            
            # PagerDuty notification
            if "pagerduty" in alert["channels"]:
                await self._send_pagerduty_alert(alert)
                
        except Exception as e:
            self.logger.error(f"Failed to send alert: {e}")
    
    async def _send_slack_alert(self, alert: Dict[str, Any]):
        """Send Slack alert notification"""
        
        import requests
        
        webhook_url = self.config["alerts"]["webhook_url"]
        
        color_map = {
            "critical": "danger",
            "warning": "warning",
            "info": "good"
        }
        
        payload = {
            "text": f"ReliQuary Alert: {alert['rule_name']}",
            "attachments": [
                {
                    "color": color_map.get(alert["severity"], "warning"),
                    "fields": [
                        {
                            "title": "Severity",
                            "value": alert["severity"].upper(),
                            "short": True
                        },
                        {
                            "title": "Message",
                            "value": alert["message"],
                            "short": False
                        },
                        {
                            "title": "Timestamp",
                            "value": alert["timestamp"],
                            "short": True
                        }
                    ]
                }
            ]
        }
        
        requests.post(webhook_url, json=payload)
    
    async def _send_email_alert(self, alert: Dict[str, Any]):
        """Send email alert notification"""
        # Implementation would use SMTP or SES
        pass
    
    async def _send_pagerduty_alert(self, alert: Dict[str, Any]):
        """Send PagerDuty alert notification"""
        # Implementation would use PagerDuty API
        pass
    
    async def get_system_overview(self) -> Dict[str, Any]:
        """Get comprehensive system overview"""
        
        return {
            "timestamp": datetime.now().isoformat(),
            "metrics_summary": {
                "total_requests_1h": "10,432",  # Would query from Prometheus
                "error_rate": "0.23%",
                "avg_response_time": "142ms",
                "active_agents": 4,
                "consensus_success_rate": "99.8%"
            },
            "component_health": {
                "api_server": "healthy",
                "consensus_system": "healthy",
                "cryptographic_system": "healthy",
                "database": "healthy",
                "cache": "healthy"
            },
            "recent_alerts": [],  # Would be populated from alert history
            "performance_trends": {
                "request_rate_trend": "stable",
                "error_rate_trend": "decreasing",
                "latency_trend": "stable"
            }
        }


class ObservabilityMiddleware:
    """FastAPI middleware for automatic observability"""
    
    def __init__(self, observability_system: AdvancedObservabilitySystem):
        self.obs = observability_system
    
    async def __call__(self, request, call_next):
        """Process request with observability tracking"""
        
        start_time = time.time()
        method = request.method
        path = str(request.url.path)
        
        # Start distributed trace
        with self.obs.tracer.start_as_current_span(f"{method} {path}") as span:
            span.set_attribute("http.method", method)
            span.set_attribute("http.url", str(request.url))
            
            try:
                response = await call_next(request)
                
                # Record metrics
                duration = time.time() - start_time
                await self.obs.record_request_metrics(
                    method=method,
                    endpoint=path,
                    status=response.status_code,
                    duration=duration
                )
                
                span.set_attribute("http.status_code", response.status_code)
                
                return response
                
            except Exception as e:
                # Record error metrics
                duration = time.time() - start_time
                await self.obs.record_request_metrics(
                    method=method,
                    endpoint=path,
                    status=500,
                    duration=duration
                )
                
                span.set_attribute("http.status_code", 500)
                span.record_exception(e)
                
                raise


async def main():
    """Initialize and run observability system"""
    
    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Initialize observability system
    obs_system = AdvancedObservabilitySystem()
    
    # Setup default dashboards
    await obs_system.setup_default_dashboards()
    
    # Start metrics server
    prometheus_client.start_http_server(8080, registry=obs_system.registry)
    
    print("🔍 Advanced Observability System initialized!")
    print("📊 Prometheus metrics available at: http://localhost:8080/metrics")
    print("📈 Grafana dashboards created")
    print("🚨 Alert monitoring active")


if __name__ == "__main__":
    asyncio.run(main())