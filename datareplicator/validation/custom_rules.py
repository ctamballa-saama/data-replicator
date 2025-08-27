"""
Custom validation rules for DataReplicator.

This module provides interfaces for creating and managing custom validation rules.
"""
from typing import Dict, Any, Tuple, List, Optional, Callable, Union
import pandas as pd

from datareplicator.validation.base import ValidationRule, ValidationResult


class CustomRuleRegistry:
    """Registry for managing custom validation rules."""
    
    def __init__(self):
        """Initialize an empty registry."""
        self.rules: Dict[str, ValidationRule] = {}
    
    def register_rule(self, rule: ValidationRule) -> None:
        """
        Register a validation rule.
        
        Args:
            rule: The ValidationRule to register
        """
        if rule.rule_id in self.rules:
            raise ValueError(f"Rule with ID '{rule.rule_id}' already exists")
        
        self.rules[rule.rule_id] = rule
    
    def get_rule(self, rule_id: str) -> Optional[ValidationRule]:
        """
        Get a validation rule by ID.
        
        Args:
            rule_id: The rule ID to lookup
            
        Returns:
            The ValidationRule if found, None otherwise
        """
        return self.rules.get(rule_id)
    
    def list_rules(self) -> List[Dict[str, Any]]:
        """
        List all registered rules.
        
        Returns:
            A list of rule information dictionaries
        """
        return [
            {
                "rule_id": rule_id,
                "description": rule.description,
                "severity": rule.severity
            }
            for rule_id, rule in self.rules.items()
        ]
    
    def unregister_rule(self, rule_id: str) -> bool:
        """
        Unregister a validation rule.
        
        Args:
            rule_id: The rule ID to unregister
            
        Returns:
            True if the rule was unregistered, False if not found
        """
        if rule_id in self.rules:
            del self.rules[rule_id]
            return True
        return False


class RuleBuilder:
    """Helper class for building custom validation rules."""
    
    @staticmethod
    def create_range_rule(
        rule_id: str,
        field_name: str,
        min_value: Optional[float] = None,
        max_value: Optional[float] = None,
        inclusive: bool = True,
        severity: str = "ERROR"
    ) -> ValidationRule:
        """
        Create a rule that validates a numeric field is within a range.
        
        Args:
            rule_id: Unique identifier for the rule
            field_name: The name of the field to validate
            min_value: The minimum allowed value (or None for no minimum)
            max_value: The maximum allowed value (or None for no maximum)
            inclusive: Whether the range bounds are inclusive
            severity: The severity level (ERROR, WARNING, INFO)
            
        Returns:
            A ValidationRule that checks the field is within the range
        """
        # Build the description based on the parameters
        description_parts = []
        if min_value is not None and max_value is not None:
            op = "between" if inclusive else "exclusively between"
            description_parts.append(f"must be {op} {min_value} and {max_value}")
        elif min_value is not None:
            op = ">=" if inclusive else ">"
            description_parts.append(f"must be {op} {min_value}")
        elif max_value is not None:
            op = "<=" if inclusive else "<"
            description_parts.append(f"must be {op} {max_value}")
        
        description = f"Field '{field_name}' {' '.join(description_parts)}"
        
        def validate_range(data: pd.DataFrame) -> Tuple[bool, Dict[str, Any]]:
            # Skip if the field doesn't exist
            if field_name not in data.columns:
                return True, {}
            
            # Get the field values
            values = data[field_name]
            
            # Check for violations
            violations = []
            for idx, value in enumerate(values):
                # Skip NaN values
                if pd.isna(value):
                    continue
                
                try:
                    # Convert to float for numeric comparison
                    float_value = float(value)
                    
                    # Check minimum
                    if min_value is not None:
                        if inclusive and float_value < min_value:
                            violations.append(idx)
                        elif not inclusive and float_value <= min_value:
                            violations.append(idx)
                    
                    # Check maximum
                    if max_value is not None:
                        if inclusive and float_value > max_value:
                            violations.append(idx)
                        elif not inclusive and float_value >= max_value:
                            violations.append(idx)
                except (ValueError, TypeError):
                    # Non-numeric values are violations
                    violations.append(idx)
            
            # Return result
            if violations:
                return False, {
                    'field_name': field_name,
                    'error_message': f"Field '{field_name}' has values outside the allowed range at rows: {violations[:5]}{'...' if len(violations) > 5 else ''}",
                    'row_index': violations[0]  # Report the first violation
                }
            
            return True, {}
        
        return ValidationRule(
            rule_id=rule_id,
            description=description,
            validation_fn=validate_range,
            severity=severity
        )
    
    @staticmethod
    def create_pattern_rule(
        rule_id: str,
        field_name: str,
        pattern: str,
        pattern_description: str,
        severity: str = "ERROR"
    ) -> ValidationRule:
        """
        Create a rule that validates a text field matches a regex pattern.
        
        Args:
            rule_id: Unique identifier for the rule
            field_name: The name of the field to validate
            pattern: Regular expression pattern to match
            pattern_description: Human-readable description of the pattern
            severity: The severity level (ERROR, WARNING, INFO)
            
        Returns:
            A ValidationRule that checks the field matches the pattern
        """
        description = f"Field '{field_name}' must match pattern: {pattern_description}"
        
        def validate_pattern(data: pd.DataFrame) -> Tuple[bool, Dict[str, Any]]:
            # Skip if the field doesn't exist
            if field_name not in data.columns:
                return True, {}
            
            # Get the field values
            values = data[field_name]
            
            # Check for violations
            import re
            pattern_regex = re.compile(pattern)
            violations = []
            
            for idx, value in enumerate(values):
                # Skip NaN values
                if pd.isna(value):
                    continue
                
                # Check if the value matches the pattern
                try:
                    str_value = str(value)
                    if not pattern_regex.match(str_value):
                        violations.append(idx)
                except Exception:
                    violations.append(idx)
            
            # Return result
            if violations:
                return False, {
                    'field_name': field_name,
                    'error_message': f"Field '{field_name}' has values that don't match pattern '{pattern_description}' at rows: {violations[:5]}{'...' if len(violations) > 5 else ''}",
                    'row_index': violations[0]  # Report the first violation
                }
            
            return True, {}
        
        return ValidationRule(
            rule_id=rule_id,
            description=description,
            validation_fn=validate_pattern,
            severity=severity
        )
    
    @staticmethod
    def create_unique_rule(
        rule_id: str,
        field_name: str,
        severity: str = "ERROR"
    ) -> ValidationRule:
        """
        Create a rule that validates a field has unique values.
        
        Args:
            rule_id: Unique identifier for the rule
            field_name: The name of the field to validate
            severity: The severity level (ERROR, WARNING, INFO)
            
        Returns:
            A ValidationRule that checks the field has unique values
        """
        description = f"Field '{field_name}' must have unique values"
        
        def validate_unique(data: pd.DataFrame) -> Tuple[bool, Dict[str, Any]]:
            # Skip if the field doesn't exist
            if field_name not in data.columns:
                return True, {}
            
            # Get the field values
            values = data[field_name]
            
            # Check for duplicates
            duplicates = values.duplicated()
            duplicate_indices = duplicates[duplicates].index.tolist()
            
            # Return result
            if duplicate_indices:
                return False, {
                    'field_name': field_name,
                    'error_message': f"Field '{field_name}' has duplicate values at rows: {duplicate_indices[:5]}{'...' if len(duplicate_indices) > 5 else ''}",
                    'row_index': duplicate_indices[0]  # Report the first violation
                }
            
            return True, {}
        
        return ValidationRule(
            rule_id=rule_id,
            description=description,
            validation_fn=validate_unique,
            severity=severity
        )
    
    @staticmethod
    def create_custom_rule(
        rule_id: str,
        description: str,
        validation_fn: Callable[[pd.DataFrame], Tuple[bool, Dict[str, Any]]],
        severity: str = "ERROR"
    ) -> ValidationRule:
        """
        Create a completely custom validation rule.
        
        Args:
            rule_id: Unique identifier for the rule
            description: Human-readable description of the rule
            validation_fn: Function that implements the validation logic
            severity: The severity level (ERROR, WARNING, INFO)
            
        Returns:
            A ValidationRule that uses the custom validation function
        """
        return ValidationRule(
            rule_id=rule_id,
            description=description,
            validation_fn=validation_fn,
            severity=severity
        )
