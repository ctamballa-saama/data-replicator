"""
Base validation framework for DataReplicator.

This module provides the abstract base classes and interfaces for data validation.
"""
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional, Union
import pandas as pd


class ValidationResult:
    """Class representing the result of a validation check."""
    
    def __init__(
        self, 
        is_valid: bool, 
        rule_id: str,
        rule_description: str, 
        field_name: Optional[str] = None,
        error_message: Optional[str] = None,
        row_index: Optional[int] = None,
        severity: str = "ERROR"
    ):
        """
        Initialize a validation result.
        
        Args:
            is_valid: Whether the validation passed
            rule_id: Unique identifier for the validation rule
            rule_description: Human-readable description of the rule
            field_name: The name of the field being validated
            error_message: Detailed error message if validation failed
            row_index: The index of the row where validation failed
            severity: The severity level (ERROR, WARNING, INFO)
        """
        self.is_valid = is_valid
        self.rule_id = rule_id
        self.rule_description = rule_description
        self.field_name = field_name
        self.error_message = error_message
        self.row_index = row_index
        self.severity = severity
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the validation result to a dictionary."""
        return {
            "is_valid": self.is_valid,
            "rule_id": self.rule_id,
            "rule_description": self.rule_description,
            "field_name": self.field_name,
            "error_message": self.error_message,
            "row_index": self.row_index,
            "severity": self.severity
        }


class ValidationSummary:
    """Class summarizing validation results for a dataset."""
    
    def __init__(self, domain_name: str):
        """
        Initialize a validation summary.
        
        Args:
            domain_name: The name of the domain being validated
        """
        self.domain_name = domain_name
        self.results: List[ValidationResult] = []
        self.error_count = 0
        self.warning_count = 0
        self.info_count = 0
    
    def add_result(self, result: ValidationResult) -> None:
        """Add a validation result to the summary."""
        self.results.append(result)
        if not result.is_valid:
            if result.severity == "ERROR":
                self.error_count += 1
            elif result.severity == "WARNING":
                self.warning_count += 1
            elif result.severity == "INFO":
                self.info_count += 1
    
    @property
    def is_valid(self) -> bool:
        """Return whether the validation passed overall (no errors)."""
        return self.error_count == 0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the validation summary to a dictionary."""
        return {
            "domain_name": self.domain_name,
            "is_valid": self.is_valid,
            "error_count": self.error_count,
            "warning_count": self.warning_count,
            "info_count": self.info_count,
            "results": [r.to_dict() for r in self.results]
        }


class BaseValidator(ABC):
    """Abstract base class for all validators."""
    
    def __init__(self, name: str, description: str):
        """
        Initialize a validator.
        
        Args:
            name: The name of the validator
            description: A description of what this validator checks
        """
        self.name = name
        self.description = description
        self.rule_id = f"{self.__class__.__name__}"
    
    @abstractmethod
    def validate(self, data: Union[pd.DataFrame, Dict[str, Any]]) -> ValidationResult:
        """
        Validate the data and return a validation result.
        
        Args:
            data: The data to validate, either a DataFrame or dictionary
            
        Returns:
            A ValidationResult object
        """
        pass


class ValidationRule:
    """Class representing a validation rule that can be registered with a validator."""
    
    def __init__(
        self, 
        rule_id: str, 
        description: str, 
        validation_fn: callable,
        severity: str = "ERROR"
    ):
        """
        Initialize a validation rule.
        
        Args:
            rule_id: Unique identifier for the rule
            description: Human-readable description of the rule
            validation_fn: Function that implements the validation logic
            severity: The severity level (ERROR, WARNING, INFO)
        """
        self.rule_id = rule_id
        self.description = description
        self.validation_fn = validation_fn
        self.severity = severity


class CompositeValidator(BaseValidator):
    """Validator that combines multiple validation rules."""
    
    def __init__(self, name: str, description: str):
        """Initialize a composite validator."""
        super().__init__(name, description)
        self.rules: List[ValidationRule] = []
    
    def add_rule(self, rule: ValidationRule) -> None:
        """Add a validation rule to this validator."""
        self.rules.append(rule)
    
    def validate(self, data: Union[pd.DataFrame, Dict[str, Any]]) -> List[ValidationResult]:
        """
        Validate the data against all registered rules.
        
        Args:
            data: The data to validate
            
        Returns:
            A list of ValidationResult objects
        """
        results = []
        for rule in self.rules:
            try:
                # Call the validation function with the data
                is_valid, error_info = rule.validation_fn(data)
                
                # Create result
                field_name = error_info.get('field_name') if not is_valid and isinstance(error_info, dict) else None
                error_message = error_info.get('error_message') if not is_valid and isinstance(error_info, dict) else None
                row_index = error_info.get('row_index') if not is_valid and isinstance(error_info, dict) else None
                
                result = ValidationResult(
                    is_valid=is_valid,
                    rule_id=rule.rule_id,
                    rule_description=rule.description,
                    field_name=field_name,
                    error_message=error_message,
                    row_index=row_index,
                    severity=rule.severity
                )
                results.append(result)
            except Exception as e:
                # If the rule validation throws an exception, create a failing result
                result = ValidationResult(
                    is_valid=False,
                    rule_id=rule.rule_id,
                    rule_description=rule.description,
                    error_message=f"Rule evaluation failed: {str(e)}",
                    severity=rule.severity
                )
                results.append(result)
        
        return results
