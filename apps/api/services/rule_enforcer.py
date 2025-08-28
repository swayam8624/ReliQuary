"""
Rule Enforcer Service for ReliQuary API.
This service enforces rules based on trust scores and context.
"""

import json
import logging
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from datetime import datetime
from enum import Enum


class ActionType(Enum):
    """Types of actions that can be enforced"""
    ALLOW = "allow"
    DENY = "deny"
    CHALLENGE = "challenge"
    MONITOR = "monitor"
    ESCALATE = "escalate"


class EnforcementDecision(Enum):
    """Possible enforcement decisions"""
    PERMIT = "permit"
    DENY = "deny"
    CHALLENGE = "challenge"
    MONITOR = "monitor"
    ESCALATE = "escalate"


@dataclass
class EnforcementContext:
    """Context for rule enforcement"""
    user_id: str
    resource_path: str
    action: str
    trust_score: float
    context_data: Dict[str, Any]
    metadata: Optional[Dict[str, Any]] = None


@dataclass
class EnforcementRule:
    """Rule for enforcement"""
    id: str
    name: str
    description: str
    conditions: List[Dict[str, Any]]
    actions: List[Dict[str, Any]]
    priority: int = 0
    enabled: bool = True
    metadata: Optional[Dict[str, Any]] = None


@dataclass
class EnforcementResult:
    """Result of rule enforcement"""
    decision: EnforcementDecision
    rule_id: str
    reason: str
    action_parameters: Optional[Dict[str, Any]] = None
    timestamp: datetime = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()


class RuleEnforcer:
    """Enforces rules based on trust scores and context"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.rules = self._load_default_rules()
    
    def _load_default_rules(self) -> List[EnforcementRule]:
        """Load default enforcement rules"""
        return [
            EnforcementRule(
                id="high_trust_access",
                name="High Trust Access",
                description="Allow access for high trust users",
                conditions=[
                    {"field": "trust_score", "operator": "greater_than", "value": 0.8}
                ],
                actions=[
                    {"type": "allow", "parameters": {"reason": "High trust user"}}
                ],
                priority=10
            ),
            EnforcementRule(
                id="medium_trust_challenge",
                name="Medium Trust Challenge",
                description="Challenge medium trust users",
                conditions=[
                    {"field": "trust_score", "operator": "greater_than", "value": 0.5},
                    {"field": "trust_score", "operator": "less_than_equal", "value": 0.8}
                ],
                actions=[
                    {"type": "challenge", "parameters": {"challenge_type": "mfa", "reason": "Medium trust user"}}
                ],
                priority=5
            ),
            EnforcementRule(
                id="low_trust_deny",
                name="Low Trust Deny",
                description="Deny access for low trust users",
                conditions=[
                    {"field": "trust_score", "operator": "less_than_equal", "value": 0.5}
                ],
                actions=[
                    {"type": "deny", "parameters": {"reason": "Low trust user"}}
                ],
                priority=1
            ),
            EnforcementRule(
                id="sensitive_resource",
                name="Sensitive Resource Protection",
                description="Extra protection for sensitive resources",
                conditions=[
                    {"field": "resource_path", "operator": "contains", "value": "/sensitive/"},
                    {"field": "trust_score", "operator": "less_than", "value": 0.9}
                ],
                actions=[
                    {"type": "challenge", "parameters": {"challenge_type": "biometric", "reason": "Sensitive resource access"}}
                ],
                priority=15
            )
        ]
    
    def enforce_rules(self, context: EnforcementContext) -> EnforcementResult:
        """
        Enforce rules based on the provided context.
        
        Args:
            context: Enforcement context with user, resource, and trust information
            
        Returns:
            Enforcement result with decision and reasoning
        """
        try:
            # Sort rules by priority (highest first)
            sorted_rules = sorted(self.rules, key=lambda r: r.priority, reverse=True)
            
            # Evaluate rules in priority order
            for rule in sorted_rules:
                if not rule.enabled:
                    continue
                
                # Check if all conditions match
                if self._evaluate_conditions(rule.conditions, context):
                    # Execute the first matching action
                    for action in rule.actions:
                        result = self._execute_action(action, rule.id, context)
                        if result:
                            self.logger.info(f"Rule {rule.id} enforced: {result.decision.value}")
                            return result
            
            # Default deny if no rules match
            default_result = EnforcementResult(
                decision=EnforcementDecision.DENY,
                rule_id="default",
                reason="No matching rules found"
            )
            
            self.logger.info(f"Default enforcement applied: {default_result.decision.value}")
            return default_result
            
        except Exception as e:
            self.logger.error(f"Rule enforcement failed: {str(e)}")
            # Return a safe default (deny)
            return EnforcementResult(
                decision=EnforcementDecision.DENY,
                rule_id="error",
                reason=f"Enforcement error: {str(e)}"
            )
    
    def _evaluate_conditions(self, conditions: List[Dict[str, Any]], context: EnforcementContext) -> bool:
        """
        Evaluate whether all conditions match the context.
        
        Args:
            conditions: List of conditions to evaluate
            context: Enforcement context
            
        Returns:
            True if all conditions match, False otherwise
        """
        for condition in conditions:
            field = condition.get("field")
            operator = condition.get("operator")
            value = condition.get("value")
            
            if not field or not operator:
                continue
            
            # Get field value from context
            field_value = self._get_context_field(context, field)
            if field_value is None:
                return False
            
            # Evaluate condition
            if not self._evaluate_condition(field_value, operator, value):
                return False
        
        return True
    
    def _get_context_field(self, context: EnforcementContext, field: str) -> Any:
        """Get a field value from the context"""
        # Handle special fields
        if field == "trust_score":
            return context.trust_score
        elif field == "user_id":
            return context.user_id
        elif field == "resource_path":
            return context.resource_path
        elif field == "action":
            return context.action
        
        # Handle nested fields in context_data
        if field.startswith("context."):
            context_field = field[8:]  # Remove "context." prefix
            return context.context_data.get(context_field)
        
        # Handle metadata fields
        if field.startswith("metadata."):
            metadata_field = field[9:]  # Remove "metadata." prefix
            return context.metadata.get(metadata_field) if context.metadata else None
        
        return None
    
    def _evaluate_condition(self, field_value: Any, operator: str, condition_value: Any) -> bool:
        """Evaluate a single condition"""
        try:
            if operator == "equals":
                return field_value == condition_value
            elif operator == "not_equals":
                return field_value != condition_value
            elif operator == "greater_than":
                return field_value > condition_value
            elif operator == "less_than":
                return field_value < condition_value
            elif operator == "greater_than_equal":
                return field_value >= condition_value
            elif operator == "less_than_equal":
                return field_value <= condition_value
            elif operator == "contains":
                if isinstance(field_value, str) and isinstance(condition_value, str):
                    return condition_value in field_value
                elif isinstance(field_value, list):
                    return condition_value in field_value
                return False
            elif operator == "not_contains":
                if isinstance(field_value, str) and isinstance(condition_value, str):
                    return condition_value not in field_value
                elif isinstance(field_value, list):
                    return condition_value not in field_value
                return False
            else:
                self.logger.warning(f"Unknown operator: {operator}")
                return False
                
        except Exception as e:
            self.logger.warning(f"Condition evaluation failed: {str(e)}")
            return False
    
    def _execute_action(self, action: Dict[str, Any], rule_id: str, context: EnforcementContext) -> Optional[EnforcementResult]:
        """Execute an enforcement action"""
        action_type = action.get("type")
        parameters = action.get("parameters", {})
        
        if action_type == "allow":
            return EnforcementResult(
                decision=EnforcementDecision.PERMIT,
                rule_id=rule_id,
                reason=parameters.get("reason", "Access permitted by rule"),
                action_parameters=parameters
            )
        elif action_type == "deny":
            return EnforcementResult(
                decision=EnforcementDecision.DENY,
                rule_id=rule_id,
                reason=parameters.get("reason", "Access denied by rule"),
                action_parameters=parameters
            )
        elif action_type == "challenge":
            return EnforcementResult(
                decision=EnforcementDecision.CHALLENGE,
                rule_id=rule_id,
                reason=parameters.get("reason", "Additional verification required"),
                action_parameters=parameters
            )
        elif action_type == "monitor":
            return EnforcementResult(
                decision=EnforcementDecision.MONITOR,
                rule_id=rule_id,
                reason=parameters.get("reason", "Access monitored"),
                action_parameters=parameters
            )
        elif action_type == "escalate":
            return EnforcementResult(
                decision=EnforcementDecision.ESCALATE,
                rule_id=rule_id,
                reason=parameters.get("reason", "Access escalated for review"),
                action_parameters=parameters
            )
        else:
            self.logger.warning(f"Unknown action type: {action_type}")
            return None
    
    def add_rule(self, rule: EnforcementRule) -> bool:
        """
        Add a new enforcement rule.
        
        Args:
            rule: Enforcement rule to add
            
        Returns:
            True if rule was added successfully, False otherwise
        """
        try:
            # Check if rule with same ID already exists
            for existing_rule in self.rules:
                if existing_rule.id == rule.id:
                    self.logger.warning(f"Rule with ID {rule.id} already exists")
                    return False
            
            self.rules.append(rule)
            self.logger.info(f"Rule {rule.id} added successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to add rule {rule.id}: {str(e)}")
            return False
    
    def remove_rule(self, rule_id: str) -> bool:
        """
        Remove an enforcement rule.
        
        Args:
            rule_id: ID of the rule to remove
            
        Returns:
            True if rule was removed successfully, False otherwise
        """
        try:
            for i, rule in enumerate(self.rules):
                if rule.id == rule_id:
                    removed_rule = self.rules.pop(i)
                    self.logger.info(f"Rule {removed_rule.id} removed successfully")
                    return True
            
            self.logger.warning(f"Rule with ID {rule_id} not found")
            return False
            
        except Exception as e:
            self.logger.error(f"Failed to remove rule {rule_id}: {str(e)}")
            return False
    
    def get_rules(self) -> List[EnforcementRule]:
        """Get all enforcement rules"""
        return self.rules.copy()
    
    def update_rule(self, rule_id: str, updates: Dict[str, Any]) -> bool:
        """
        Update an existing enforcement rule.
        
        Args:
            rule_id: ID of the rule to update
            updates: Dictionary of fields to update
            
        Returns:
            True if rule was updated successfully, False otherwise
        """
        try:
            for rule in self.rules:
                if rule.id == rule_id:
                    # Update fields
                    for key, value in updates.items():
                        if hasattr(rule, key):
                            setattr(rule, key, value)
                    
                    self.logger.info(f"Rule {rule_id} updated successfully")
                    return True
            
            self.logger.warning(f"Rule with ID {rule_id} not found")
            return False
            
        except Exception as e:
            self.logger.error(f"Failed to update rule {rule_id}: {str(e)}")
            return False


# Global rule enforcer instance
_rule_enforcer = None


def get_rule_enforcer() -> RuleEnforcer:
    """Get the global rule enforcer instance"""
    global _rule_enforcer
    if _rule_enforcer is None:
        _rule_enforcer = RuleEnforcer()
    return _rule_enforcer


def enforce_security_rules(context: EnforcementContext) -> EnforcementResult:
    """Convenience function to enforce security rules"""
    enforcer = get_rule_enforcer()
    return enforcer.enforce_rules(context)


def add_enforcement_rule(rule: EnforcementRule) -> bool:
    """Convenience function to add an enforcement rule"""
    enforcer = get_rule_enforcer()
    return enforcer.add_rule(rule)


def remove_enforcement_rule(rule_id: str) -> bool:
    """Convenience function to remove an enforcement rule"""
    enforcer = get_rule_enforcer()
    return enforcer.remove_rule(rule_id)