"""
Intelligent Alerting System for ReliQuary Observability

This module implements intelligent alerting with notification channels,
escalation policies, alert correlation, and automated response capabilities.
"""

import asyncio
import json
import logging
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from enum import Enum
from collections import defaultdict, deque
import uuid


class AlertPriority(Enum):
    """Alert priority levels"""
    P1 = "p1"  # Critical
    P2 = "p2"  # High  
    P3 = "p3"  # Medium
    P4 = "p4"  # Low


class NotificationChannel(Enum):
    """Notification delivery channels"""
    EMAIL = "email"
    SLACK = "slack"
    WEBHOOK = "webhook"


class AlertState(Enum):
    """Alert lifecycle states"""
    TRIGGERED = "triggered"
    ACKNOWLEDGED = "acknowledged"
    ESCALATED = "escalated"
    RESOLVED = "resolved"


@dataclass
class AlertRule:
    """Intelligent alert rule"""
    rule_id: str
    name: str
    metric_name: str
    threshold: float
    priority: AlertPriority
    notification_channels: List[NotificationChannel]
    automated_responses: List[str]
    enabled: bool = True


@dataclass
class Alert:
    """Enhanced alert"""
    alert_id: str
    rule_id: str
    title: str
    description: str
    priority: AlertPriority
    state: AlertState
    current_value: float
    threshold_value: float
    first_triggered: datetime
    last_updated: datetime
    escalation_level: int = 0


class IntelligentAlertManager:
    """Intelligent alerting system with correlation and automation"""
    
    def __init__(self, manager_id: str = "alert_manager_v1"):
        self.manager_id = manager_id
        self.logger = logging.getLogger(f"alert_manager.{manager_id}")
        
        self.alert_rules = {}
        self.active_alerts = {}
        self.alert_history = deque(maxlen=10000)
        
        self.notification_configs = {}
        self.background_tasks = []
        self.shutdown_event = asyncio.Event()
        
        self.alert_stats = {
            "total_triggered": 0,
            "total_resolved": 0,
            "avg_resolution_time": 0.0
        }
        
        self.logger.info(f"Intelligent Alert Manager {manager_id} initialized")
    
    async def initialize(self) -> Dict[str, Any]:
        """Initialize alert manager"""
        try:
            await self._setup_default_alert_rules()
            await self._start_background_tasks()
            
            return {
                "alert_rules": len(self.alert_rules),
                "background_tasks": len(self.background_tasks)
            }
        except Exception as e:
            self.logger.error(f"Alert manager initialization failed: {e}")
            return {"error": str(e)}
    
    async def _setup_default_alert_rules(self):
        """Setup default intelligent alert rules"""
        rules = [
            AlertRule(
                rule_id="cpu_usage_high",
                name="High CPU Usage",
                metric_name="cpu_usage_percent",
                threshold=80.0,
                priority=AlertPriority.P2,
                notification_channels=[NotificationChannel.EMAIL, NotificationChannel.SLACK],
                automated_responses=["scale_up_resources"]
            ),
            AlertRule(
                rule_id="memory_usage_critical",
                name="Critical Memory Usage",
                metric_name="memory_usage_percent",
                threshold=95.0,
                priority=AlertPriority.P1,
                notification_channels=[NotificationChannel.EMAIL, NotificationChannel.SLACK],
                automated_responses=["emergency_cleanup", "scale_up_memory"]
            ),
            AlertRule(
                rule_id="security_events_spike",
                name="Security Events Spike",
                metric_name="security_events_per_minute",
                threshold=50.0,
                priority=AlertPriority.P1,
                notification_channels=[NotificationChannel.EMAIL, NotificationChannel.SLACK],
                automated_responses=["block_suspicious_ips", "enable_enhanced_monitoring"]
            ),
            AlertRule(
                rule_id="consensus_failure_high",
                name="High Consensus Failure Rate",
                metric_name="consensus_failure_rate",
                threshold=10.0,
                priority=AlertPriority.P2,
                notification_channels=[NotificationChannel.EMAIL],
                automated_responses=["restart_failed_agents", "rebalance_consensus"]
            )
        ]
        
        for rule in rules:
            self.alert_rules[rule.rule_id] = rule
    
    async def evaluate_metric(self, metric_name: str, value: float, 
                            timestamp: Optional[datetime] = None) -> List[str]:
        """Evaluate metric against alert rules"""
        timestamp = timestamp or datetime.now()
        triggered_alerts = []
        
        for rule_id, rule in self.alert_rules.items():
            if not rule.enabled or rule.metric_name != metric_name:
                continue
            
            if value >= rule.threshold:
                alert_id = await self._handle_rule_trigger(rule, value, timestamp)
                if alert_id:
                    triggered_alerts.append(alert_id)
            else:
                await self._check_alert_resolution(rule_id, value, timestamp)
        
        return triggered_alerts
    
    async def _handle_rule_trigger(self, rule: AlertRule, value: float, timestamp: datetime) -> Optional[str]:
        """Handle alert rule trigger"""
        try:
            # Check if alert already exists
            existing_alert = self._find_existing_alert(rule.rule_id)
            if existing_alert:
                existing_alert.current_value = value
                existing_alert.last_updated = timestamp
                return existing_alert.alert_id
            
            # Create new alert
            alert_id = await self._create_alert(rule, value, timestamp)
            
            # Trigger notifications
            await self._trigger_notifications(alert_id)
            
            # Execute automated responses
            await self._execute_automated_responses(alert_id, rule.automated_responses)
            
            return alert_id
        except Exception as e:
            self.logger.error(f"Alert trigger handling failed: {e}")
            return None
    
    def _find_existing_alert(self, rule_id: str) -> Optional[Alert]:
        """Find existing alert for rule"""
        for alert in self.active_alerts.values():
            if (alert.rule_id == rule_id and 
                alert.state in [AlertState.TRIGGERED, AlertState.ACKNOWLEDGED]):
                return alert
        return None
    
    async def _create_alert(self, rule: AlertRule, value: float, timestamp: datetime) -> str:
        """Create a new alert"""
        alert_id = str(uuid.uuid4())
        
        alert = Alert(
            alert_id=alert_id,
            rule_id=rule.rule_id,
            title=rule.name,
            description=f"{rule.name}. Current value: {value:.2f}",
            priority=rule.priority,
            state=AlertState.TRIGGERED,
            current_value=value,
            threshold_value=rule.threshold,
            first_triggered=timestamp,
            last_updated=timestamp
        )
        
        self.active_alerts[alert_id] = alert
        self.alert_history.append(alert)
        self.alert_stats["total_triggered"] += 1
        
        self.logger.warning(f"Alert created: {alert.title} (ID: {alert_id})")
        return alert_id
    
    async def _trigger_notifications(self, alert_id: str):
        """Trigger notifications for alert"""
        alert = self.active_alerts[alert_id]
        rule = self.alert_rules[alert.rule_id]
        
        for channel in rule.notification_channels:
            await self._send_notification(alert, channel)
    
    async def _send_notification(self, alert: Alert, channel: NotificationChannel):
        """Send notification through specified channel"""
        try:
            if channel == NotificationChannel.EMAIL:
                await self._send_email_notification(alert)
            elif channel == NotificationChannel.SLACK:
                await self._send_slack_notification(alert)
            elif channel == NotificationChannel.WEBHOOK:
                await self._send_webhook_notification(alert)
        except Exception as e:
            self.logger.error(f"Notification sending failed: {e}")
    
    async def _send_email_notification(self, alert: Alert):
        """Send email notification (simulation)"""
        self.logger.info(f"EMAIL: [{alert.priority.value.upper()}] {alert.title}")
        self.logger.info(f"  Description: {alert.description}")
        self.logger.info(f"  Current: {alert.current_value:.2f}, Threshold: {alert.threshold_value:.2f}")
    
    async def _send_slack_notification(self, alert: Alert):
        """Send Slack notification (simulation)"""
        self.logger.info(f"SLACK: [{alert.priority.value.upper()}] {alert.title}")
        self.logger.info(f"  🚨 {alert.description}")
    
    async def _send_webhook_notification(self, alert: Alert):
        """Send webhook notification (simulation)"""
        payload = {
            "alert_id": alert.alert_id,
            "title": alert.title,
            "priority": alert.priority.value,
            "current_value": alert.current_value,
            "threshold_value": alert.threshold_value
        }
        self.logger.info(f"WEBHOOK: {json.dumps(payload)}")
    
    async def _execute_automated_responses(self, alert_id: str, responses: List[str]):
        """Execute automated responses for alert"""
        alert = self.active_alerts[alert_id]
        
        for response in responses:
            success = await self._execute_response(response, alert)
            self.logger.info(f"Automated response '{response}' executed for alert {alert_id}: {success}")
    
    async def _execute_response(self, response: str, alert: Alert) -> bool:
        """Execute individual automated response"""
        response_handlers = {
            "scale_up_resources": self._scale_up_resources,
            "emergency_cleanup": self._emergency_cleanup,
            "scale_up_memory": self._scale_up_memory,
            "block_suspicious_ips": self._block_suspicious_ips,
            "enable_enhanced_monitoring": self._enable_enhanced_monitoring,
            "restart_failed_agents": self._restart_failed_agents,
            "rebalance_consensus": self._rebalance_consensus
        }
        
        handler = response_handlers.get(response)
        if handler:
            return await handler(alert)
        return False
    
    async def _scale_up_resources(self, alert: Alert) -> bool:
        """Scale up system resources"""
        self.logger.info(f"🔧 Scaling up resources for alert {alert.alert_id}")
        return True
    
    async def _emergency_cleanup(self, alert: Alert) -> bool:
        """Perform emergency memory cleanup"""
        self.logger.info(f"🧹 Emergency cleanup for alert {alert.alert_id}")
        return True
    
    async def _scale_up_memory(self, alert: Alert) -> bool:
        """Scale up memory allocation"""
        self.logger.info(f"💾 Scaling up memory for alert {alert.alert_id}")
        return True
    
    async def _block_suspicious_ips(self, alert: Alert) -> bool:
        """Block suspicious IP addresses"""
        self.logger.info(f"🛡️ Blocking suspicious IPs for alert {alert.alert_id}")
        return True
    
    async def _enable_enhanced_monitoring(self, alert: Alert) -> bool:
        """Enable enhanced security monitoring"""
        self.logger.info(f"👁️ Enhanced monitoring enabled for alert {alert.alert_id}")
        return True
    
    async def _restart_failed_agents(self, alert: Alert) -> bool:
        """Restart failed consensus agents"""
        self.logger.info(f"🔄 Restarting failed agents for alert {alert.alert_id}")
        return True
    
    async def _rebalance_consensus(self, alert: Alert) -> bool:
        """Rebalance consensus load"""
        self.logger.info(f"⚖️ Rebalancing consensus for alert {alert.alert_id}")
        return True
    
    async def _check_alert_resolution(self, rule_id: str, value: float, timestamp: datetime):
        """Check if alerts should be auto-resolved"""
        rule = self.alert_rules[rule_id]
        
        for alert in list(self.active_alerts.values()):
            if (alert.rule_id == rule_id and 
                alert.state in [AlertState.TRIGGERED, AlertState.ACKNOWLEDGED] and
                value < rule.threshold):
                await self._resolve_alert(alert.alert_id, "auto_resolved", timestamp)
    
    async def _resolve_alert(self, alert_id: str, resolved_by: str, timestamp: datetime) -> bool:
        """Resolve an alert"""
        if alert_id not in self.active_alerts:
            return False
        
        alert = self.active_alerts[alert_id]
        alert.state = AlertState.RESOLVED
        alert.last_updated = timestamp
        
        # Update statistics
        resolution_time = (timestamp - alert.first_triggered).total_seconds() / 60
        self.alert_stats["total_resolved"] += 1
        
        # Remove from active alerts
        del self.active_alerts[alert_id]
        
        self.logger.info(f"✅ Alert {alert_id} resolved by {resolved_by} after {resolution_time:.1f} minutes")
        return True
    
    async def _start_background_tasks(self):
        """Start background processing tasks"""
        escalation_task = asyncio.create_task(self._escalation_monitoring_loop())
        self.background_tasks.append(escalation_task)
    
    async def _escalation_monitoring_loop(self):
        """Monitor alerts for escalation"""
        while not self.shutdown_event.is_set():
            try:
                await self._check_escalations()
                await asyncio.sleep(60)
            except Exception as e:
                self.logger.error(f"Escalation monitoring error: {e}")
                await asyncio.sleep(60)
    
    async def _check_escalations(self):
        """Check if alerts need escalation"""
        for alert in self.active_alerts.values():
            if alert.state == AlertState.TRIGGERED:
                time_since_trigger = datetime.now() - alert.first_triggered
                
                escalation_thresholds = {
                    AlertPriority.P1: 15,  # 15 minutes
                    AlertPriority.P2: 30,  # 30 minutes
                    AlertPriority.P3: 120, # 2 hours
                    AlertPriority.P4: 1440 # 24 hours
                }
                
                threshold = escalation_thresholds.get(alert.priority, 60)
                
                if time_since_trigger.total_seconds() / 60 > threshold:
                    await self._escalate_alert(alert.alert_id)
    
    async def _escalate_alert(self, alert_id: str):
        """Escalate an alert"""
        if alert_id not in self.active_alerts:
            return
        
        alert = self.active_alerts[alert_id]
        alert.escalation_level += 1
        alert.state = AlertState.ESCALATED
        alert.last_updated = datetime.now()
        
        self.logger.warning(f"🚨 Alert {alert_id} escalated to level {alert.escalation_level}")
        
        # Send escalation notifications
        await self._trigger_notifications(alert_id)
    
    def get_alert_statistics(self) -> Dict[str, Any]:
        """Get comprehensive alert statistics"""
        active_by_priority = defaultdict(int)
        for alert in self.active_alerts.values():
            active_by_priority[alert.priority.value] += 1
        
        return {
            "manager_id": self.manager_id,
            "alert_rules": len(self.alert_rules),
            "active_alerts": len(self.active_alerts),
            "active_by_priority": dict(active_by_priority),
            "total_triggered": self.alert_stats["total_triggered"],
            "total_resolved": self.alert_stats["total_resolved"],
            "avg_resolution_time_minutes": self.alert_stats["avg_resolution_time"],
            "timestamp": datetime.now().isoformat()
        }
    
    async def shutdown(self):
        """Shutdown alert manager"""
        self.logger.info("Shutting down alert manager...")
        self.shutdown_event.set()
        
        if self.background_tasks:
            await asyncio.gather(*self.background_tasks, return_exceptions=True)
        
        self.logger.info("Alert manager shutdown complete")