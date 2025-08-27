"""
Validation service for DataReplicator.

This module provides the ValidationService which orchestrates data validation.
"""
import logging
from typing import Dict, List, Any, Optional, Union
import pandas as pd

from datareplicator.validation.base import (
    BaseValidator, 
    ValidationResult, 
    ValidationSummary,
    CompositeValidator
)
from datareplicator.validation.cdisc_validators import CDISCValidator
from datareplicator.validation.custom_rules import CustomRuleRegistry, RuleBuilder

# Configure logging
logger = logging.getLogger(__name__)


class ValidationService:
    """Service for validating data against rules and standards."""
    
    def __init__(self):
        """Initialize the validation service."""
        self.validators: Dict[str, BaseValidator] = {}
        self.custom_rule_registry = CustomRuleRegistry()
        
        # Register default validators
        self._register_default_validators()
    
    def _register_default_validators(self):
        """Register the default validators."""
        # Register CDISC validator
        self.register_validator("cdisc", CDISCValidator())
    
    def register_validator(self, validator_id: str, validator: BaseValidator) -> None:
        """
        Register a validator.
        
        Args:
            validator_id: Unique identifier for the validator
            validator: The validator to register
        """
        if validator_id in self.validators:
            raise ValueError(f"Validator with ID '{validator_id}' already exists")
        
        self.validators[validator_id] = validator
    
    def validate_domain(
        self, 
        domain_data: pd.DataFrame, 
        domain_name: str,
        validator_ids: Optional[List[str]] = None
    ) -> ValidationSummary:
        """
        Validate a domain against registered validators.
        
        Args:
            domain_data: The data to validate
            domain_name: The name of the domain
            validator_ids: Optional list of validator IDs to use (default: all)
            
        Returns:
            A ValidationSummary with the results
        """
        summary = ValidationSummary(domain_name)
        
        # Determine which validators to use
        if validator_ids is None:
            validators_to_use = self.validators.values()
        else:
            validators_to_use = [
                validator for validator_id, validator in self.validators.items()
                if validator_id in validator_ids
            ]
        
        # Run validation with each validator
        for validator in validators_to_use:
            try:
                logger.info(f"Running validator {validator.name} on {domain_name}")
                
                if isinstance(validator, CompositeValidator):
                    # Composite validators return multiple results
                    results = validator.validate(domain_data)
                    for result in results:
                        summary.add_result(result)
                else:
                    # Single validators return one result
                    result = validator.validate(domain_data)
                    summary.add_result(result)
                    
            except Exception as e:
                logger.error(f"Error validating {domain_name} with {validator.name}: {str(e)}")
                # Create a failure result for the validator
                error_result = ValidationResult(
                    is_valid=False,
                    rule_id=f"{validator.name}.Error",
                    rule_description=validator.description,
                    error_message=f"Validator failed with error: {str(e)}",
                    severity="ERROR"
                )
                summary.add_result(error_result)
        
        return summary
    
    def create_custom_validator(
        self, 
        validator_id: str,
        name: str,
        description: str
    ) -> CompositeValidator:
        """
        Create a new custom validator.
        
        Args:
            validator_id: Unique identifier for the validator
            name: Name of the validator
            description: Description of the validator
            
        Returns:
            A new CompositeValidator
        """
        validator = CompositeValidator(name, description)
        self.register_validator(validator_id, validator)
        return validator
    
    def add_custom_rule(
        self,
        validator_id: str,
        rule_id: str,
        description: str,
        validation_fn: callable,
        severity: str = "ERROR"
    ) -> None:
        """
        Add a custom rule to an existing validator.
        
        Args:
            validator_id: ID of the validator to add the rule to
            rule_id: Unique identifier for the rule
            description: Description of the rule
            validation_fn: Function that implements the validation logic
            severity: The severity level (ERROR, WARNING, INFO)
        """
        if validator_id not in self.validators:
            raise ValueError(f"Validator with ID '{validator_id}' does not exist")
        
        validator = self.validators[validator_id]
        if not isinstance(validator, CompositeValidator):
            raise ValueError(f"Validator '{validator_id}' does not support adding rules")
        
        # Create and register the rule
        rule = RuleBuilder.create_custom_rule(
            rule_id=rule_id,
            description=description,
            validation_fn=validation_fn,
            severity=severity
        )
        
        validator.add_rule(rule)
        self.custom_rule_registry.register_rule(rule)
    
    def list_validators(self) -> List[Dict[str, Any]]:
        """
        List all registered validators.
        
        Returns:
            A list of validator information dictionaries
        """
        return [
            {
                "id": validator_id,
                "name": validator.name,
                "description": validator.description
            }
            for validator_id, validator in self.validators.items()
        ]
    
    def list_rules(self, validator_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        List all registered rules.
        
        Args:
            validator_id: Optional validator ID to filter rules by
            
        Returns:
            A list of rule information dictionaries
        """
        if validator_id is not None:
            if validator_id not in self.validators:
                raise ValueError(f"Validator with ID '{validator_id}' does not exist")
            
            validator = self.validators[validator_id]
            if not isinstance(validator, CompositeValidator):
                return []
            
            return [
                {
                    "rule_id": rule.rule_id,
                    "description": rule.description,
                    "severity": rule.severity
                }
                for rule in validator.rules
            ]
        else:
            return self.custom_rule_registry.list_rules()


# Create a singleton instance for the application
validation_service = ValidationService()
