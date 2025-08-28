"""
Metrics module for exposing Prometheus/OpenTelemetry metrics.
This module provides functionality for collecting and exposing system metrics.
"""

import time
import logging
from typing import Dict, Any, Optional
from dataclasses import dataclass, asdict
from collections import defaultdict
from threading import Lock


@dataclass
class Metric:
    """Base metric class"""
    name: str
    value: float
    labels: Dict[str, str]
    timestamp: float
    metric_type: str


class MetricsCollector:
    """Collects and exposes system metrics"""
    
    def __init__(self):
        self.metrics = {}
        self.counters = defaultdict(float)
        self.gauges = defaultdict(float)
        self.histograms = defaultdict(list)
        self.lock = Lock()
        self.logger = logging.getLogger(__name__)
    
    def increment_counter(self, name: str, value: float = 1.0, labels: Optional[Dict[str, str]] = None):
        """Increment a counter metric"""
        with self.lock:
            key = self._get_metric_key(name, labels)
            self.counters[key] += value
            self._update_metric(name, self.counters[key], labels, "counter")
    
    def set_gauge(self, name: str, value: float, labels: Optional[Dict[str, str]] = None):
        """Set a gauge metric"""
        with self.lock:
            key = self._get_metric_key(name, labels)
            self.gauges[key] = value
            self._update_metric(name, value, labels, "gauge")
    
    def observe_histogram(self, name: str, value: float, labels: Optional[Dict[str, str]] = None):
        """Observe a histogram metric"""
        with self.lock:
            key = self._get_metric_key(name, labels)
            self.histograms[key].append(value)
            # Keep only the last 1000 observations to prevent memory issues
            if len(self.histograms[key]) > 1000:
                self.histograms[key] = self.histograms[key][-1000:]
            self._update_metric(name, value, labels, "histogram")
    
    def _get_metric_key(self, name: str, labels: Optional[Dict[str, str]]) -> str:
        """Generate a unique key for a metric"""
        if not labels:
            return name
        label_str = ",".join([f"{k}={v}" for k, v in sorted(labels.items())])
        return f"{name}[{label_str}]"
    
    def _update_metric(self, name: str, value: float, labels: Optional[Dict[str, str]], metric_type: str):
        """Update a metric in the metrics dictionary"""
        key = self._get_metric_key(name, labels)
        self.metrics[key] = Metric(
            name=name,
            value=value,
            labels=labels or {},
            timestamp=time.time(),
            metric_type=metric_type
        )
    
    def get_metrics(self) -> Dict[str, Metric]:
        """Get all collected metrics"""
        with self.lock:
            return self.metrics.copy()
    
    def get_metrics_text(self) -> str:
        """Get metrics in Prometheus text format"""
        metrics = self.get_metrics()
        lines = []
        
        for metric in metrics.values():
            # Format labels
            if metric.labels:
                label_str = ",".join([f'{k}="{v}"' for k, v in metric.labels.items()])
                metric_line = f'{metric.name}{{{label_str}}} {metric.value}'
            else:
                metric_line = f'{metric.name} {metric.value}'
            
            lines.append(metric_line)
        
        return "\n".join(lines)
    
    def reset(self):
        """Reset all metrics"""
        with self.lock:
            self.metrics.clear()
            self.counters.clear()
            self.gauges.clear()
            self.histograms.clear()


# Global metrics collector instance
_metrics_collector = MetricsCollector()


def get_metrics_collector() -> MetricsCollector:
    """Get the global metrics collector instance"""
    return _metrics_collector


def increment_counter(name: str, value: float = 1.0, labels: Optional[Dict[str, str]] = None):
    """Increment a counter metric"""
    _metrics_collector.increment_counter(name, value, labels)


def set_gauge(name: str, value: float, labels: Optional[Dict[str, str]] = None):
    """Set a gauge metric"""
    _metrics_collector.set_gauge(name, value, labels)


def observe_histogram(name: str, value: float, labels: Optional[Dict[str, str]] = None):
    """Observe a histogram metric"""
    _metrics_collector.observe_histogram(name, value, labels)


def get_metrics_text() -> str:
    """Get all metrics in Prometheus text format"""
    return _metrics_collector.get_metrics_text()


# Example usage and common metrics
class SystemMetrics:
    """Common system metrics"""
    
    @staticmethod
    def record_api_request(endpoint: str, method: str, status_code: int, duration_ms: float):
        """Record an API request"""
        labels = {
            "endpoint": endpoint,
            "method": method,
            "status_code": str(status_code)
        }
        
        increment_counter("api_requests_total", 1, labels)
        observe_histogram("api_request_duration_ms", duration_ms, labels)
    
    @staticmethod
    def record_consensus_decision(decision: str, confidence: float, duration_ms: float):
        """Record a consensus decision"""
        labels = {"decision": decision}
        
        increment_counter("consensus_decisions_total", 1, labels)
        observe_histogram("consensus_duration_ms", duration_ms, labels)
        set_gauge("consensus_confidence_score", confidence, labels)
    
    @staticmethod
    def record_zk_proof_generation(circuit_type: str, duration_ms: float, success: bool):
        """Record ZK proof generation"""
        labels = {
            "circuit_type": circuit_type,
            "success": str(success).lower()
        }
        
        increment_counter("zk_proofs_generated_total", 1, labels)
        observe_histogram("zk_proof_generation_duration_ms", duration_ms, labels)
    
    @staticmethod
    def record_vault_operation(operation: str, success: bool, duration_ms: float):
        """Record a vault operation"""
        labels = {
            "operation": operation,
            "success": str(success).lower()
        }
        
        increment_counter("vault_operations_total", 1, labels)
        observe_histogram("vault_operation_duration_ms", duration_ms, labels)