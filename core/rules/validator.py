"""
Rules Validator for ReliQuary Trust Engine.
This module validates trust rule configurations.
"""

import json
import logging
import yaml
from typing import Dict, Any, List, Optional, Union
from dataclasses import dataclass
from enum import Enum


class RuleType(Enum):
    """Types of trust rules"""
    ACCESS_CONTROL = "access_control"
    CONTEXT_VALIDATION = "context_validation"
    RISK_ASSESSMENT = "risk_assessment"
    BEHAVIORAL_ANALYSIS = "behavioral_analysis"
    THRESHOLD_POLICY = "threshold_policy"


class ValidationSeverity(Enum):
    """Severity levels for validation issues"""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"


@dataclass
class ValidationIssue:
    """Issue found during rule validation"""
    severity: ValidationSeverity
    message: str
    field: Optional[str] = None
    rule_id: Optional[str] = None


@dataclass
class ValidationResult:
    """Result of rule validation"""
    valid: bool
    issues: List[ValidationIssue]
    rule_count: int


class RulesValidator:
    """Validates trust rule configurations"""
    
    def __init__(self, schema_file: Optional[str] = None):
        self.logger = logging.getLogger(__name__)
        self.schema = self._load_schema(schema_file)
    
    def _load_schema(self, schema_file: Optional[str]) -> Dict[str, Any]:
        """Load validation schema"""
        # Default schema for trust rules
        default_schema = {
            "required_fields": ["id", "type", "conditions", "actions"],
            "valid_types": [rule_type.value for rule_type in RuleType],
            "condition_operators": ["equals", "not_equals", "greater_than", "less_than", "contains", "not_contains"],
            "action_types": ["allow", "deny", "challenge", "monitor", "escalate"]
        }
        
        if schema_file:
            try:
                with open(schema_file, 'r') as f:
                    if schema_file.endswith('.yaml') or schema_file.endswith('.yml'):
                        schema = yaml.safe_load(f)
                    else:
                        schema = json.load(f)
                    # Merge with default schema
                    default_schema.update(schema)
            except Exception as e:
                self.logger.warning(f"Failed to load schema from {schema_file}: {str(e)}")
        
        return default_schema
    
    def validate_rules(self, rules_data: Union[Dict[str, Any], List[Dict[str, Any]]]) -> ValidationResult:
        """
        Validate trust rules configuration.
        
        Args:
            rules_data: Rules configuration data (dict or list)
            
        Returns:
            Validation result with issues found
        """
        try:
            # Normalize input to list format
            if isinstance(rules_data, dict):
                if "rules" in rules_data:
                    rules_list = rules_data["rules"]
                else:
                    rules_list = [rules_data]
            else:
                rules_list = rules_data
            
            issues = []
            valid_rules = 0
            
            # Validate each rule
            for i, rule in enumerate(rules_list):
                rule_id = rule.get("id", f"rule_{i}")
                rule_issues = self._validate_single_rule(rule, rule_id)
                issues.extend(rule_issues)
                
                # Count valid rules (rules without ERROR severity issues)
                error_issues = [issue for issue in rule_issues if issue.severity == ValidationSeverity.ERROR]
                if not error_issues:
                    valid_rules += 1
            
            # Overall validation result
            has_errors = any(issue.severity == ValidationSeverity.ERROR for issue in issues)
            is_valid = not has_errors
            
            result = ValidationResult(
                valid=is_valid,
                issues=issues,
                rule_count=len(rules_list)
            )
            
            self.logger.info(f"Rules validation completed: {valid_rules}/{len(rules_list)} rules valid")
            return result
            
        except Exception as e:
            self.logger.error(f"Rules validation failed: {str(e)}")
            return ValidationResult(
                valid=False,
                issues=[ValidationIssue(
                    severity=ValidationSeverity.ERROR,
                    message=f"Validation failed: {str(e)}"
                )],
                rule_count=0
            )
    
    def _validate_single_rule(self, rule: Dict[str, Any], rule_id: str) -> List[ValidationIssue]:
        """Validate a single rule"""
        issues = []
        
        # Check required fields
        for field in self.schema["required_fields"]:
            if field not in rule:
                issues.append(ValidationIssue(
                    severity=ValidationSeverity.ERROR,
                    message=f"Required field '{field}' is missing",
                    field=field,
                    rule_id=rule_id
                ))
        
        # Validate rule type
        rule_type = rule.get("type")
        if rule_type and rule_type not in self.schema["valid_types"]:
            issues.append(ValidationIssue(
                    severity=ValidationSeverity.ERROR,
                    message=f"Invalid rule type '{rule_type}'. Valid types: {self.schema['valid_types']}",
                    field="type",
                    rule_id=rule_id
                ))
        
        # Validate conditions
        conditions = rule.get("conditions", [])
        if not isinstance(conditions, list):
            issues.append(ValidationIssue(
                severity=ValidationSeverity.ERROR,
                message="Conditions must be a list",
                field="conditions",
                rule_id=rule_id
            ))
        else:
            for j, condition in enumerate(conditions):
                condition_issues = self._validate_condition(condition, f"{rule_id}.conditions[{j}]")
                issues.extend(condition_issues)
        
        # Validate actions
        actions = rule.get("actions", [])
        if not isinstance(actions, list):
            issues.append(ValidationIssue(
                severity=ValidationSeverity.ERROR,
                message="Actions must be a list",
                field="actions",
                rule_id=rule_id
            ))
        else:
            for k, action in enumerate(actions):
                action_issues = self._validate_action(action, f"{rule_id}.actions[{k}]")
                issues.extend(action_issues)
        
        # Validate priority if present
        priority = rule.get("priority")
        if priority is not None:
            if not isinstance(priority, int) or priority < 0:
                issues.append(ValidationIssue(
                    severity=ValidationSeverity.WARNING,
                    message="Priority should be a non-negative integer",
                    field="priority",
                    rule_id=rule_id
                ))
        
        # Validate enabled flag if present
        enabled = rule.get("enabled")
        if enabled is not None and not isinstance(enabled, bool):
            issues.append(ValidationIssue(
                severity=ValidationSeverity.WARNING,
                message="Enabled flag should be a boolean value",
                field="enabled",
                rule_id=rule_id
            ))
        
        return issues
    
    def _validate_condition(self, condition: Dict[str, Any], condition_id: str) -> List[ValidationIssue]:
        """Validate a single condition"""
        issues = []
        
        # Check required fields for condition
        required_condition_fields = ["field", "operator", "value"]
        for field in required_condition_fields:
            if field not in condition:
                issues.append(ValidationIssue(
                    severity=ValidationSeverity.ERROR,
                    message=f"Required condition field '{field}' is missing",
                    field=field,
                    rule_id=condition_id
                ))
        
        # Validate operator
        operator = condition.get("operator")
        if operator and operator not in self.schema["condition_operators"]:
            issues.append(ValidationIssue(
                severity=ValidationSeverity.ERROR,
                message=f"Invalid operator '{operator}'. Valid operators: {self.schema['condition_operators']}",
                field="operator",
                rule_id=condition_id
            ))
        
        # Validate field name format (should not contain spaces or special chars)
        field_name = condition.get("field", "")
        if field_name and not isinstance(field_name, str):
            issues.append(ValidationIssue(
                severity=ValidationSeverity.ERROR,
                message="Field name must be a string",
                field="field",
                rule_id=condition_id
            ))
        elif field_name and not field_name.replace("_", "").replace(".", "").isalnum():
            issues.append(ValidationIssue(
                severity=ValidationSeverity.WARNING,
                message="Field name should contain only alphanumeric characters, underscores, and dots",
                field="field",
                rule_id=condition_id
            ))
        
        return issues
    
    def _validate_action(self, action: Dict[str, Any], action_id: str) -> List[ValidationIssue]:
        """Validate a single action"""
        issues = []
        
        # Check required fields for action
        if "type" not in action:
            issues.append(ValidationIssue(
                severity=ValidationSeverity.ERROR,
                message="Required action field 'type' is missing",
                field="type",
                rule_id=action_id
            ))
        
        # Validate action type
        action_type = action.get("type")
        if action_type and action_type not in self.schema["action_types"]:
            issues.append(ValidationIssue(
                severity=ValidationSeverity.ERROR,
                message=f"Invalid action type '{action_type}'. Valid types: {self.schema['action_types']}",
                field="type",
                rule_id=action_id
            ))
        
        # Validate parameters if present
        parameters = action.get("parameters", {})
        if not isinstance(parameters, dict):
            issues.append(ValidationIssue(
                severity=ValidationSeverity.ERROR,
                message="Action parameters must be a dictionary",
                field="parameters",
                rule_id=action_id
            ))
        
        return issues
    
    def validate_rule_file(self, file_path: str) -> ValidationResult:
        """
        Validate rules from a file.
        
        Args:
            file_path: Path to the rules file (.json or .yaml)
            
        Returns:
            Validation result
        """
        try:
            with open(file_path, 'r') as f:
                if file_path.endswith('.yaml') or file_path.endswith('.yml'):
                    rules_data = yaml.safe_load(f)
                else:
                    rules_data = json.load(f)
            
            return self.validate_rules(rules_data)
            
        except Exception as e:
            self.logger.error(f"Failed to validate rules file {file_path}: {str(e)}")
            return ValidationResult(
                valid=False,
                issues=[ValidationIssue(
                    severity=ValidationSeverity.ERROR,
                    message=f"Failed to read or parse file: {str(e)}",
                    field=None
                )],
                rule_count=0
            )


# Global rules validator instance
_rules_validator = None


def get_rules_validator(schema_file: Optional[str] = None) -> RulesValidator:
    """Get the global rules validator instance"""
    global _rules_validator
    if _rules_validator is None:
        _rules_validator = RulesValidator(schema_file)
    return _rules_validator


def validate_trust_rules(rules_data: Union[Dict[str, Any], List[Dict[str, Any]]]) -> ValidationResult:
    """Convenience function to validate trust rules"""
    validator = get_rules_validator()
    return validator.validate_rules(rules_data)


def validate_rules_file(file_path: str) -> ValidationResult:
    """Convenience function to validate rules from a file"""
    validator = get_rules_validator()
    return validator.validate_rule_file(file_path)