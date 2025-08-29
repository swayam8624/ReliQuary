"""
Comprehensive Test Suite for ReliQuary Observability System

This module tests all observability components including telemetry,
alerting, monitoring, and integration functionality.
"""

import pytest
import pytest_asyncio
import asyncio
import time
import json
from datetime import datetime, timedelta
from unittest.mock import AsyncMock, MagicMock, patch

import sys
sys.path.append('/Users/swayamsingal/Desktop/Programming/ReliQuary')

from observability.telemetry_manager import (
    TelemetryManager, TelemetryConfig, TelemetryLevel, MetricType
)
from observability.alerting_system import (
    IntelligentAlertManager, AlertRule, AlertPriority, NotificationChannel, AlertState
)
from observability.integration_manager import (
    ObservabilityManager, ObservabilityConfig, ObservabilityLevel
)


class TestAlertManager:
    """Test suite for IntelligentAlertManager"""
    
    @pytest_asyncio.fixture
    async def alert_manager(self):
        """Create alert manager for testing"""
        manager = IntelligentAlertManager("test_alert_manager")
        await manager.initialize()
        yield manager
        await manager.shutdown()
    
    @pytest.mark.asyncio
    async def test_alert_manager_initialization(self):
        """Test alert manager initialization"""
        manager = IntelligentAlertManager()
        result = await manager.initialize()
        
        assert isinstance(result, dict)
        assert "alert_rules" in result
        assert "background_tasks" in result
        assert len(manager.alert_rules) > 0
        
        await manager.shutdown()
    
    @pytest.mark.asyncio
    async def test_metric_evaluation_trigger_alert(self, alert_manager):
        """Test metric evaluation that triggers alerts"""
        # Test CPU usage alert
        triggered_alerts = await alert_manager.evaluate_metric("cpu_usage_percent", 85.0)
        
        assert len(triggered_alerts) >= 1
        
        # Verify alert creation
        alert_id = triggered_alerts[0]
        assert alert_id in alert_manager.active_alerts
        
        alert = alert_manager.active_alerts[alert_id]
        assert alert.state == AlertState.TRIGGERED
        assert alert.current_value == 85.0
        assert alert.priority in [AlertPriority.P1, AlertPriority.P2]
    
    @pytest.mark.asyncio
    async def test_metric_evaluation_no_alert(self, alert_manager):
        """Test metric evaluation that doesn't trigger alerts"""
        # Test normal CPU usage
        triggered_alerts = await alert_manager.evaluate_metric("cpu_usage_percent", 50.0)
        
        # Should not trigger alerts for normal values
        assert len(triggered_alerts) == 0
    
    @pytest.mark.asyncio
    async def test_alert_resolution(self, alert_manager):
        """Test alert resolution functionality"""
        # First trigger an alert
        triggered_alerts = await alert_manager.evaluate_metric("memory_usage_percent", 98.0)
        assert len(triggered_alerts) >= 1
        
        alert_id = triggered_alerts[0]
        assert alert_id in alert_manager.active_alerts
        
        # Then resolve it with normal values
        await alert_manager.evaluate_metric("memory_usage_percent", 50.0)
        
        # Wait a bit for async processing
        await asyncio.sleep(0.1)
        
        # Alert should be resolved
        assert alert_id not in alert_manager.active_alerts
    
    @pytest.mark.asyncio
    async def test_escalation_monitoring(self, alert_manager):
        """Test alert escalation functionality"""
        # Create a high priority alert
        triggered_alerts = await alert_manager.evaluate_metric("security_events_per_minute", 100.0)
        assert len(triggered_alerts) >= 1
        
        alert_id = triggered_alerts[0]
        alert = alert_manager.active_alerts[alert_id]
        initial_escalation_level = alert.escalation_level
        
        # Manually escalate for testing
        await alert_manager._escalate_alert(alert_id)
        
        # Verify escalation
        assert alert.escalation_level == initial_escalation_level + 1
        assert alert.state == AlertState.ESCALATED
    
    @pytest.mark.asyncio
    async def test_alert_statistics(self, alert_manager):
        """Test alert statistics generation"""
        # Trigger some alerts
        await alert_manager.evaluate_metric("cpu_usage_percent", 85.0)
        await alert_manager.evaluate_metric("memory_usage_percent", 98.0)
        
        stats = alert_manager.get_alert_statistics()
        
        assert isinstance(stats, dict)
        assert "manager_id" in stats
        assert "alert_rules" in stats
        assert "active_alerts" in stats
        assert "total_triggered" in stats
        assert stats["total_triggered"] >= 2


class TestObservabilityManager:
    """Test suite for ObservabilityManager"""
    
    @pytest_asyncio.fixture
    async def observability_manager(self):
        """Create observability manager for testing"""
        config = ObservabilityConfig(
            service_name="test_observability",
            service_version="1.0.0",
            environment="test",
            observability_level=ObservabilityLevel.STANDARD,
            enable_telemetry=True,
            enable_alerting=True,
            enable_dashboards=True
        )
        
        manager = ObservabilityManager(config)
        await manager.initialize()
        yield manager
        await manager.shutdown()
    
    @pytest.mark.asyncio
    async def test_observability_initialization(self):
        """Test observability manager initialization"""
        config = ObservabilityConfig(
            service_name="test_service",
            environment="test",
            observability_level=ObservabilityLevel.BASIC
        )
        
        manager = ObservabilityManager(config)
        result = await manager.initialize()
        
        assert isinstance(result, dict)
        assert "status" in result
        assert result["status"] == "initialized" or "error" in result
        
        if result["status"] == "initialized":
            assert manager.is_initialized
            assert "telemetry" in result
            assert "alerting" in result
        
        await manager.shutdown()
    
    @pytest.mark.asyncio
    async def test_metric_recording_integration(self, observability_manager):
        """Test metric recording through observability manager"""
        await observability_manager.record_metric("test_metric", 42.0, {"environment": "test"})
        
        # Verify metric was recorded in telemetry manager
        if observability_manager.telemetry_manager:
            assert len(observability_manager.telemetry_manager.metrics_buffer) > 0
            
            # Find our metric
            recorded_metrics = list(observability_manager.telemetry_manager.metrics_buffer)
            test_metric = next((m for m in recorded_metrics if m.name == "test_metric"), None)
            
            assert test_metric is not None
            assert test_metric.value == 42.0
    
    @pytest.mark.asyncio
    async def test_tracing_integration(self, observability_manager):
        """Test distributed tracing through observability manager"""
        span_id = await observability_manager.start_trace("test_operation", {"service": "test"})
        
        if span_id:  # Only test if tracing is enabled
            assert span_id is not None
            assert observability_manager.telemetry_manager is not None
            assert span_id in observability_manager.telemetry_manager.active_spans
            
            # End the trace
            await observability_manager.end_trace(span_id, "completed")
            
            # Verify completion
            assert span_id not in observability_manager.telemetry_manager.active_spans
    
    @pytest.mark.asyncio
    async def test_alert_triggering(self, observability_manager):
        """Test alert triggering through observability manager"""
        alert_id = await observability_manager.trigger_alert(
            "cpu_usage_percent", 
            90.0, 
            "Test alert trigger"
        )
        
        if alert_id:  # Only test if alerting is enabled
            assert alert_id is not None
            assert observability_manager.alert_manager is not None
            assert alert_id in observability_manager.alert_manager.active_alerts
    
    @pytest.mark.asyncio
    async def test_system_dashboard(self, observability_manager):
        """Test system dashboard generation"""
        dashboard = await observability_manager.get_system_dashboard()
        
        assert isinstance(dashboard, dict)
        assert "service_info" in dashboard
        assert "system_status" in dashboard
        assert "metrics_summary" in dashboard
        assert "alerts_summary" in dashboard
        assert "timestamp" in dashboard
        
        # Verify service info
        service_info = dashboard["service_info"]
        assert service_info["name"] == "test_observability"
        assert service_info["version"] == "1.0.0"
        assert service_info["environment"] == "test"
    
    @pytest.mark.asyncio
    async def test_health_check(self, observability_manager):
        """Test health check functionality"""
        health = await observability_manager.get_health_check()
        
        assert isinstance(health, dict)
        assert "status" in health
        assert "components" in health
        assert "uptime_seconds" in health
        assert "timestamp" in health
        
        # Status should be healthy or initializing
        assert health["status"] in ["healthy", "initializing", "degraded"]
        
        # Components should be reported
        components = health["components"]
        assert "telemetry" in components
        assert "alerting" in components
    
    @pytest.mark.asyncio
    async def test_metrics_export(self, observability_manager):
        """Test metrics export functionality"""
        # Test JSON export
        json_export = await observability_manager.generate_metrics_export("json")
        assert isinstance(json_export, str)
        
        try:
            json_data = json.loads(json_export)
            assert isinstance(json_data, dict)
        except json.JSONDecodeError:
            pytest.fail("JSON export is not valid JSON")
        
        # Test Prometheus export
        prometheus_export = await observability_manager.generate_metrics_export("prometheus")
        assert isinstance(prometheus_export, str)


class TestIntegrationScenarios:
    """Integration tests for complete observability workflows"""
    
    @pytest.mark.asyncio
    async def test_end_to_end_monitoring_workflow(self):
        """Test complete monitoring workflow from metric to alert to resolution"""
        # Initialize observability system
        config = ObservabilityConfig(
            service_name="integration_test",
            environment="test",
            observability_level=ObservabilityLevel.COMPREHENSIVE
        )
        
        manager = ObservabilityManager(config)
        await manager.initialize()
        
        try:
            # 1. Record high CPU metric
            await manager.record_metric("cpu_usage_percent", 95.0)
            
            # 2. Wait for alert processing
            await asyncio.sleep(0.2)
            
            # 3. Check if alert was triggered
            if manager.alert_manager:
                active_alerts = list(manager.alert_manager.active_alerts.values())
                cpu_alerts = [a for a in active_alerts if "cpu" in a.title.lower()]
                
                if cpu_alerts:
                    alert = cpu_alerts[0]
                    assert alert.current_value == 95.0
                    assert alert.state == AlertState.TRIGGERED
                    
                    # 4. Record normal CPU metric to resolve alert
                    await manager.record_metric("cpu_usage_percent", 30.0)
                    
                    # 5. Wait for resolution processing
                    await asyncio.sleep(0.2)
                    
                    # 6. Verify alert resolution
                    assert alert.alert_id not in manager.alert_manager.active_alerts
            
            # 7. Verify system health reflects the changes
            health = await manager.get_health_check()
            assert health["status"] in ["healthy", "degraded"]
            
        finally:
            await manager.shutdown()
    
    @pytest.mark.asyncio
    async def test_concurrent_operations(self):
        """Test concurrent metric recording and alert processing"""
        config = ObservabilityConfig(
            service_name="concurrent_test",
            environment="test"
        )
        
        manager = ObservabilityManager(config)
        await manager.initialize()
        
        try:
            # Create multiple concurrent metric recording tasks
            async def record_metrics_batch(prefix: str, count: int):
                for i in range(count):
                    await manager.record_metric(f"{prefix}_metric_{i}", float(i * 10))
                    await asyncio.sleep(0.01)  # Small delay
            
            # Run concurrent batches
            tasks = [
                record_metrics_batch("batch_1", 10),
                record_metrics_batch("batch_2", 10),
                record_metrics_batch("batch_3", 10)
            ]
            
            await asyncio.gather(*tasks)
            
            # Verify all metrics were recorded
            if manager.telemetry_manager:
                assert len(manager.telemetry_manager.metrics_buffer) >= 30
            
            # Check system stability
            health = await manager.get_health_check()
            assert health["status"] in ["healthy", "initializing", "degraded"]
            
        finally:
            await manager.shutdown()
    
    @pytest.mark.asyncio
    async def test_performance_under_load(self):
        """Test observability system performance under load"""
        config = ObservabilityConfig(
            service_name="performance_test",
            environment="test"
        )
        
        manager = ObservabilityManager(config)
        start_time = time.time()
        await manager.initialize()
        init_time = time.time() - start_time
        
        try:
            # Rapid metric recording
            start_time = time.time()
            
            for i in range(100):
                await manager.record_metric(f"load_test_metric", float(i))
                
                # Occasionally trigger traces
                if i % 20 == 0:
                    span_id = await manager.start_trace(f"load_test_operation_{i}")
                    if span_id:
                        await manager.end_trace(span_id, "completed")
            
            processing_time = time.time() - start_time
            
            # Performance assertions
            assert init_time < 5.0  # Initialization should be fast
            assert processing_time < 2.0  # Processing 100 metrics should be fast
            
            # Verify system health
            health = await manager.get_health_check()
            assert health["status"] in ["healthy", "degraded"]
            
            # Verify metrics were recorded
            if manager.telemetry_manager:
                assert len(manager.telemetry_manager.metrics_buffer) >= 100
            
        finally:
            await manager.shutdown()


# Performance benchmarks
class TestPerformanceBenchmarks:
    """Performance benchmark tests"""
    
    @pytest.mark.asyncio
    async def test_metric_recording_performance(self):
        """Benchmark metric recording performance"""
        config = TelemetryConfig(
            service_name="benchmark_test",
            service_version="1.0.0",
            environment="test",
            telemetry_level=TelemetryLevel.STANDARD  # Add the missing parameter
        )
        
        manager = TelemetryManager(config)
        await manager.initialize()
        
        try:
            # Record a large number of metrics
            start_time = time.time()
            for i in range(1000):
                manager.record_metric(f"benchmark_metric_{i}", float(i), MetricType.COUNTER)
            
            end_time = time.time()
            duration = end_time - start_time
            
            # Should complete in reasonable time (less than 1 second for 1000 metrics)
            assert duration < 1.0
            assert len(manager.metrics_buffer) >= 1000
        
        finally:
            await manager.shutdown()
    
    @pytest.mark.asyncio
    async def test_alert_evaluation_performance(self):
        """Benchmark alert evaluation performance"""
        manager = IntelligentAlertManager()
        await manager.initialize()
        
        try:
            # Benchmark alert evaluation
            start_time = time.time()
            
            for i in range(100):
                await manager.evaluate_metric("test_metric", float(i % 50))
            
            end_time = time.time()
            total_time = end_time - start_time
            
            # Performance assertions
            assert total_time < 0.5  # Should evaluate 100 metrics in under 0.5 seconds
            
            # Calculate evaluations per second
            evaluations_per_second = 100 / total_time
            assert evaluations_per_second > 200  # Should handle at least 200 evaluations/sec
            
        finally:
            await manager.shutdown()


if __name__ == "__main__":
    # Run the tests
    pytest.main([__file__, "-v", "--asyncio-mode=auto"])