"""
Grafana Dashboard Configuration for ReliQuary Observability

This module provides pre-configured Grafana dashboards for monitoring
ReliQuary system performance, security, and consensus operations.
"""

import json
from typing import Dict, List, Any


class GrafanaDashboardConfig:
    """Grafana dashboard configuration generator"""
    
    @staticmethod
    def generate_system_overview_dashboard() -> Dict[str, Any]:
        """Generate system overview dashboard configuration"""
        return {
            "dashboard": {
                "id": None,
                "title": "ReliQuary System Overview",
                "tags": ["reliquary", "overview"],
                "timezone": "browser",
                "refresh": "30s",
                "time": {
                    "from": "now-1h",
                    "to": "now"
                },
                "panels": [
                    {
                        "id": 1,
                        "title": "System Health Score",
                        "type": "stat",
                        "targets": [
                            {
                                "expr": "reliquary_system_health_score",
                                "legendFormat": "Health Score"
                            }
                        ],
                        "fieldConfig": {
                            "defaults": {
                                "color": {
                                    "mode": "thresholds"
                                },
                                "thresholds": {
                                    "steps": [
                                        {"color": "red", "value": 0},
                                        {"color": "yellow", "value": 0.7},
                                        {"color": "green", "value": 0.9}
                                    ]
                                },
                                "min": 0,
                                "max": 1
                            }
                        },
                        "gridPos": {"h": 8, "w": 6, "x": 0, "y": 0}
                    },
                    {
                        "id": 2,
                        "title": "CPU Usage",
                        "type": "timeseries",
                        "targets": [
                            {
                                "expr": "reliquary_cpu_usage_percent{component=\"system\"}",
                                "legendFormat": "CPU Usage %"
                            }
                        ],
                        "fieldConfig": {
                            "defaults": {
                                "color": {"mode": "palette-classic"},
                                "custom": {"drawStyle": "line", "lineInterpolation": "linear"},
                                "thresholds": {
                                    "steps": [
                                        {"color": "green", "value": 0},
                                        {"color": "yellow", "value": 70},
                                        {"color": "red", "value": 90}
                                    ]
                                }
                            }
                        },
                        "gridPos": {"h": 8, "w": 9, "x": 6, "y": 0}
                    },
                    {
                        "id": 3,
                        "title": "Memory Usage",
                        "type": "timeseries",
                        "targets": [
                            {
                                "expr": "reliquary_memory_usage_bytes{component=\"system\"}",
                                "legendFormat": "Memory Usage"
                            }
                        ],
                        "fieldConfig": {
                            "defaults": {
                                "color": {"mode": "palette-classic"},
                                "custom": {"drawStyle": "line", "lineInterpolation": "linear"},
                                "unit": "bytes"
                            }
                        },
                        "gridPos": {"h": 8, "w": 9, "x": 15, "y": 0}
                    },
                    {
                        "id": 4,
                        "title": "Active Agents",
                        "type": "timeseries",
                        "targets": [
                            {
                                "expr": "reliquary_agent_count",
                                "legendFormat": "{{agent_type}}"
                            }
                        ],
                        "fieldConfig": {
                            "defaults": {
                                "color": {"mode": "palette-classic"},
                                "custom": {"drawStyle": "line", "lineInterpolation": "linear"}
                            }
                        },
                        "gridPos": {"h": 8, "w": 12, "x": 0, "y": 8}
                    },
                    {
                        "id": 5,
                        "title": "Request Rate",
                        "type": "timeseries",
                        "targets": [
                            {
                                "expr": "rate(reliquary_requests_total[5m])",
                                "legendFormat": "{{method}} {{endpoint}}"
                            }
                        ],
                        "fieldConfig": {
                            "defaults": {
                                "color": {"mode": "palette-classic"},
                                "custom": {"drawStyle": "line", "lineInterpolation": "linear"},
                                "unit": "reqps"
                            }
                        },
                        "gridPos": {"h": 8, "w": 12, "x": 12, "y": 8}
                    }
                ]
            }
        }
    
    @staticmethod
    def generate_consensus_dashboard() -> Dict[str, Any]:
        """Generate consensus monitoring dashboard configuration"""
        return {
            "dashboard": {
                "id": None,
                "title": "ReliQuary Consensus Monitoring",
                "tags": ["reliquary", "consensus"],
                "timezone": "browser",
                "refresh": "15s",
                "time": {
                    "from": "now-30m",
                    "to": "now"
                },
                "panels": [
                    {
                        "id": 1,
                        "title": "Consensus Operations Rate",
                        "type": "timeseries",
                        "targets": [
                            {
                                "expr": "rate(reliquary_consensus_operations_total[5m])",
                                "legendFormat": "{{operation_type}} - {{status}}"
                            }
                        ],
                        "fieldConfig": {
                            "defaults": {
                                "color": {"mode": "palette-classic"},
                                "custom": {"drawStyle": "line", "lineInterpolation": "linear"},
                                "unit": "ops"
                            }
                        },
                        "gridPos": {"h": 8, "w": 12, "x": 0, "y": 0}
                    },
                    {
                        "id": 2,
                        "title": "Consensus Duration",
                        "type": "timeseries",
                        "targets": [
                            {
                                "expr": "histogram_quantile(0.95, rate(reliquary_consensus_duration_seconds_bucket[5m]))",
                                "legendFormat": "95th percentile"
                            },
                            {
                                "expr": "histogram_quantile(0.50, rate(reliquary_consensus_duration_seconds_bucket[5m]))",
                                "legendFormat": "50th percentile"
                            }
                        ],
                        "fieldConfig": {
                            "defaults": {
                                "color": {"mode": "palette-classic"},
                                "custom": {"drawStyle": "line", "lineInterpolation": "linear"},
                                "unit": "s"
                            }
                        },
                        "gridPos": {"h": 8, "w": 12, "x": 12, "y": 0}
                    },
                    {
                        "id": 3,
                        "title": "Agent Health Status",
                        "type": "piechart",
                        "targets": [
                            {
                                "expr": "reliquary_agent_count",
                                "legendFormat": "{{agent_type}}"
                            }
                        ],
                        "fieldConfig": {
                            "defaults": {
                                "color": {"mode": "palette-classic"},
                                "custom": {"hideFrom": {"legend": False, "tooltip": False, "vis": False}}
                            }
                        },
                        "gridPos": {"h": 8, "w": 8, "x": 0, "y": 8}
                    },
                    {
                        "id": 4,
                        "title": "Consensus Success Rate",
                        "type": "stat",
                        "targets": [
                            {
                                "expr": "rate(reliquary_consensus_operations_total{status=\"success\"}[5m]) / rate(reliquary_consensus_operations_total[5m]) * 100",
                                "legendFormat": "Success Rate %"
                            }
                        ],
                        "fieldConfig": {
                            "defaults": {
                                "color": {
                                    "mode": "thresholds"
                                },
                                "thresholds": {
                                    "steps": [
                                        {"color": "red", "value": 0},
                                        {"color": "yellow", "value": 90},
                                        {"color": "green", "value": 95}
                                    ]
                                },
                                "unit": "percent"
                            }
                        },
                        "gridPos": {"h": 8, "w": 8, "x": 8, "y": 8}
                    },
                    {
                        "id": 5,
                        "title": "Byzantine Fault Detection",
                        "type": "timeseries",
                        "targets": [
                            {
                                "expr": "reliquary_consensus_operations_total{status=\"byzantine_fault\"}",
                                "legendFormat": "Byzantine Faults Detected"
                            }
                        ],
                        "fieldConfig": {
                            "defaults": {
                                "color": {"mode": "fixed", "fixedColor": "red"},
                                "custom": {"drawStyle": "points", "pointSize": 8}
                            }
                        },
                        "gridPos": {"h": 8, "w": 8, "x": 16, "y": 8}
                    }
                ]
            }
        }
    
    @staticmethod
    def generate_security_dashboard() -> Dict[str, Any]:
        """Generate security monitoring dashboard configuration"""
        return {
            "dashboard": {
                "id": None,
                "title": "ReliQuary Security Monitoring",
                "tags": ["reliquary", "security"],
                "timezone": "browser",
                "refresh": "10s",
                "time": {
                    "from": "now-1h",
                    "to": "now"
                },
                "panels": [
                    {
                        "id": 1,
                        "title": "Security Events",
                        "type": "timeseries",
                        "targets": [
                            {
                                "expr": "rate(reliquary_security_events_total[1m])",
                                "legendFormat": "{{event_type}} - {{severity}}"
                            }
                        ],
                        "fieldConfig": {
                            "defaults": {
                                "color": {"mode": "palette-classic"},
                                "custom": {"drawStyle": "line", "lineInterpolation": "linear"},
                                "unit": "events/min"
                            }
                        },
                        "gridPos": {"h": 8, "w": 24, "x": 0, "y": 0}
                    },
                    {
                        "id": 2,
                        "title": "Authentication Events",
                        "type": "timeseries",
                        "targets": [
                            {
                                "expr": "rate(reliquary_requests_total{endpoint=~\"/auth/.*\"}[5m])",
                                "legendFormat": "{{status_code}}"
                            }
                        ],
                        "fieldConfig": {
                            "defaults": {
                                "color": {"mode": "palette-classic"},
                                "custom": {"drawStyle": "line", "lineInterpolation": "linear"}
                            }
                        },
                        "gridPos": {"h": 8, "w": 12, "x": 0, "y": 8}
                    },
                    {
                        "id": 3,
                        "title": "Failed Access Attempts",
                        "type": "stat",
                        "targets": [
                            {
                                "expr": "sum(rate(reliquary_requests_total{status_code=~\"4..\"}[5m]))",
                                "legendFormat": "Failed Attempts/min"
                            }
                        ],
                        "fieldConfig": {
                            "defaults": {
                                "color": {
                                    "mode": "thresholds"
                                },
                                "thresholds": {
                                    "steps": [
                                        {"color": "green", "value": 0},
                                        {"color": "yellow", "value": 10},
                                        {"color": "red", "value": 50}
                                    ]
                                }
                            }
                        },
                        "gridPos": {"h": 8, "w": 12, "x": 12, "y": 8}
                    }
                ]
            }
        }
    
    @staticmethod
    def generate_performance_dashboard() -> Dict[str, Any]:
        """Generate performance monitoring dashboard configuration"""
        return {
            "dashboard": {
                "id": None,
                "title": "ReliQuary Performance Monitoring",
                "tags": ["reliquary", "performance"],
                "timezone": "browser",
                "refresh": "30s",
                "time": {
                    "from": "now-2h",
                    "to": "now"
                },
                "panels": [
                    {
                        "id": 1,
                        "title": "Response Time Distribution",
                        "type": "heatmap",
                        "targets": [
                            {
                                "expr": "rate(reliquary_request_duration_seconds_bucket[5m])",
                                "legendFormat": "{{le}}"
                            }
                        ],
                        "fieldConfig": {
                            "defaults": {
                                "custom": {
                                    "hideFrom": {"legend": False, "tooltip": False, "vis": False}
                                }
                            }
                        },
                        "gridPos": {"h": 8, "w": 24, "x": 0, "y": 0}
                    },
                    {
                        "id": 2,
                        "title": "Throughput",
                        "type": "timeseries",
                        "targets": [
                            {
                                "expr": "sum(rate(reliquary_requests_total[5m]))",
                                "legendFormat": "Total Requests/sec"
                            }
                        ],
                        "fieldConfig": {
                            "defaults": {
                                "color": {"mode": "palette-classic"},
                                "custom": {"drawStyle": "line", "lineInterpolation": "linear"},
                                "unit": "reqps"
                            }
                        },
                        "gridPos": {"h": 8, "w": 12, "x": 0, "y": 8}
                    },
                    {
                        "id": 3,
                        "title": "Error Rate",
                        "type": "timeseries",
                        "targets": [
                            {
                                "expr": "rate(reliquary_requests_total{status_code=~\"5..\"}[5m]) / rate(reliquary_requests_total[5m]) * 100",
                                "legendFormat": "Error Rate %"
                            }
                        ],
                        "fieldConfig": {
                            "defaults": {
                                "color": {"mode": "fixed", "fixedColor": "red"},
                                "custom": {"drawStyle": "line", "lineInterpolation": "linear"},
                                "unit": "percent"
                            }
                        },
                        "gridPos": {"h": 8, "w": 12, "x": 12, "y": 8}
                    }
                ]
            }
        }
    
    @staticmethod
    def export_dashboard_configs() -> Dict[str, Dict[str, Any]]:
        """Export all dashboard configurations"""
        return {
            "system_overview": GrafanaDashboardConfig.generate_system_overview_dashboard(),
            "consensus_monitoring": GrafanaDashboardConfig.generate_consensus_dashboard(),
            "security_monitoring": GrafanaDashboardConfig.generate_security_dashboard(),
            "performance_monitoring": GrafanaDashboardConfig.generate_performance_dashboard()
        }


# Configuration for alert rules in Grafana
GRAFANA_ALERT_RULES = {
    "high_cpu_usage": {
        "expr": "reliquary_cpu_usage_percent > 80",
        "for": "5m",
        "labels": {"severity": "warning"},
        "annotations": {
            "summary": "High CPU usage detected",
            "description": "CPU usage is above 80% for more than 5 minutes"
        }
    },
    "critical_memory_usage": {
        "expr": "reliquary_memory_usage_bytes / reliquary_memory_total_bytes * 100 > 95",
        "for": "1m",
        "labels": {"severity": "critical"},
        "annotations": {
            "summary": "Critical memory usage",
            "description": "Memory usage is above 95%"
        }
    },
    "consensus_failure_rate": {
        "expr": "rate(reliquary_consensus_operations_total{status=\"failure\"}[5m]) / rate(reliquary_consensus_operations_total[5m]) * 100 > 10",
        "for": "3m",
        "labels": {"severity": "error"},
        "annotations": {
            "summary": "High consensus failure rate",
            "description": "Consensus failure rate is above 10%"
        }
    },
    "security_events_spike": {
        "expr": "rate(reliquary_security_events_total[1m]) > 50",
        "for": "2m",
        "labels": {"severity": "critical"},
        "annotations": {
            "summary": "Security events spike detected",
            "description": "Unusual spike in security events"
        }
    }
}


def save_dashboard_configs(output_dir: str = "./dashboards"):
    """Save dashboard configurations to JSON files"""
    import os
    
    os.makedirs(output_dir, exist_ok=True)
    
    configs = GrafanaDashboardConfig.export_dashboard_configs()
    
    for name, config in configs.items():
        file_path = os.path.join(output_dir, f"{name}.json")
        with open(file_path, 'w') as f:
            json.dump(config, f, indent=2)
        
        print(f"Dashboard configuration saved: {file_path}")
    
    # Save alert rules
    alert_rules_path = os.path.join(output_dir, "alert_rules.json")
    with open(alert_rules_path, 'w') as f:
        json.dump(GRAFANA_ALERT_RULES, f, indent=2)
    
    print(f"Alert rules configuration saved: {alert_rules_path}")


if __name__ == "__main__":
    save_dashboard_configs()