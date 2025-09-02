"""
Tests for the base validation framework classes.
"""
import unittest
import pandas as pd
from datareplicator.validation.base import (
    ValidationResult, 
    ValidationSummary, 
    BaseValidator, 
    ValidationRule,
    CompositeValidator
)


class TestValidationResult(unittest.TestCase):
    """Test cases for ValidationResult class."""
    
    def test_validation_result_creation(self):
        """Test creating a validation result."""
        result = ValidationResult(
            is_valid=False,
            rule_id="test_rule",
            rule_description="Test rule description",
            field_name="test_field",
            error_message="Test error message",
            row_index=5,
            severity="ERROR"
        )
        
        self.assertFalse(result.is_valid)
        self.assertEqual(result.rule_id, "test_rule")
        self.assertEqual(result.rule_description, "Test rule description")
        self.assertEqual(result.field_name, "test_field")
        self.assertEqual(result.error_message, "Test error message")
        self.assertEqual(result.row_index, 5)
        self.assertEqual(result.severity, "ERROR")
    
    def test_to_dict_method(self):
        """Test conversion to dictionary."""
        result = ValidationResult(
            is_valid=True,
            rule_id="test_rule",
            rule_description="Test rule description",
            severity="WARNING"
        )
        
        result_dict = result.to_dict()
        self.assertTrue(result_dict["is_valid"])
        self.assertEqual(result_dict["rule_id"], "test_rule")
        self.assertEqual(result_dict["rule_description"], "Test rule description")
        self.assertIsNone(result_dict["field_name"])
        self.assertIsNone(result_dict["error_message"])
        self.assertIsNone(result_dict["row_index"])
        self.assertEqual(result_dict["severity"], "WARNING")


class TestValidationSummary(unittest.TestCase):
    """Test cases for ValidationSummary class."""
    
    def test_validation_summary_creation(self):
        """Test creating a validation summary."""
        summary = ValidationSummary("test_domain")
        self.assertEqual(summary.domain_name, "test_domain")
        self.assertEqual(len(summary.results), 0)
        self.assertEqual(summary.error_count, 0)
        self.assertEqual(summary.warning_count, 0)
        self.assertEqual(summary.info_count, 0)
        self.assertTrue(summary.is_valid)
    
    def test_add_result(self):
        """Test adding results to a summary."""
        summary = ValidationSummary("test_domain")
        
        # Add a valid result
        valid_result = ValidationResult(
            is_valid=True,
            rule_id="valid_rule",
            rule_description="Valid rule",
            severity="INFO"
        )
        summary.add_result(valid_result)
        self.assertEqual(len(summary.results), 1)
        self.assertEqual(summary.error_count, 0)
        self.assertEqual(summary.warning_count, 0)
        self.assertEqual(summary.info_count, 0)
        self.assertTrue(summary.is_valid)
        
        # Add an invalid result with ERROR severity
        error_result = ValidationResult(
            is_valid=False,
            rule_id="error_rule",
            rule_description="Error rule",
            severity="ERROR"
        )
        summary.add_result(error_result)
        self.assertEqual(len(summary.results), 2)
        self.assertEqual(summary.error_count, 1)
        self.assertEqual(summary.warning_count, 0)
        self.assertEqual(summary.info_count, 0)
        self.assertFalse(summary.is_valid)
        
        # Add an invalid result with WARNING severity
        warning_result = ValidationResult(
            is_valid=False,
            rule_id="warning_rule",
            rule_description="Warning rule",
            severity="WARNING"
        )
        summary.add_result(warning_result)
        self.assertEqual(len(summary.results), 3)
        self.assertEqual(summary.error_count, 1)
        self.assertEqual(summary.warning_count, 1)
        self.assertEqual(summary.info_count, 0)
        self.assertFalse(summary.is_valid)
        
        # Add an invalid result with INFO severity
        info_result = ValidationResult(
            is_valid=False,
            rule_id="info_rule",
            rule_description="Info rule",
            severity="INFO"
        )
        summary.add_result(info_result)
        self.assertEqual(len(summary.results), 4)
        self.assertEqual(summary.error_count, 1)
        self.assertEqual(summary.warning_count, 1)
        self.assertEqual(summary.info_count, 1)
        self.assertFalse(summary.is_valid)
    
    def test_to_dict_method(self):
        """Test conversion to dictionary."""
        summary = ValidationSummary("test_domain")
        result = ValidationResult(
            is_valid=False,
            rule_id="test_rule",
            rule_description="Test description",
            severity="ERROR"
        )
        summary.add_result(result)
        
        summary_dict = summary.to_dict()
        self.assertEqual(summary_dict["domain_name"], "test_domain")
        self.assertFalse(summary_dict["is_valid"])
        self.assertEqual(summary_dict["error_count"], 1)
        self.assertEqual(summary_dict["warning_count"], 0)
        self.assertEqual(summary_dict["info_count"], 0)
        self.assertEqual(len(summary_dict["results"]), 1)


class TestCompositeValidator(unittest.TestCase):
    """Test cases for CompositeValidator class."""
    
    def test_composite_validator_creation(self):
        """Test creating a composite validator."""
        validator = CompositeValidator("Test Validator", "Test description")
        self.assertEqual(validator.name, "Test Validator")
        self.assertEqual(validator.description, "Test description")
        self.assertEqual(len(validator.rules), 0)
    
    def test_add_rule(self):
        """Test adding rules to a composite validator."""
        validator = CompositeValidator("Test Validator", "Test description")
        
        # Create a simple validation rule
        def test_validation(data):
            return True, {}
        
        rule = ValidationRule(
            rule_id="test_rule",
            description="Test rule",
            validation_fn=test_validation,
            severity="INFO"
        )
        
        validator.add_rule(rule)
        self.assertEqual(len(validator.rules), 1)
        self.assertEqual(validator.rules[0].rule_id, "test_rule")
    
    def test_validate_with_passing_rules(self):
        """Test validation with rules that pass."""
        validator = CompositeValidator("Test Validator", "Test description")
        
        # Create a validation rule that always passes
        def passing_validation(data):
            return True, {}
        
        rule = ValidationRule(
            rule_id="passing_rule",
            description="Passing rule",
            validation_fn=passing_validation,
            severity="ERROR"
        )
        
        validator.add_rule(rule)
        
        # Create test data
        data = pd.DataFrame({"A": [1, 2, 3], "B": ["x", "y", "z"]})
        
        # Validate
        results = validator.validate(data)
        self.assertEqual(len(results), 1)
        self.assertTrue(results[0].is_valid)
        self.assertEqual(results[0].rule_id, "passing_rule")
    
    def test_validate_with_failing_rules(self):
        """Test validation with rules that fail."""
        validator = CompositeValidator("Test Validator", "Test description")
        
        # Create a validation rule that always fails
        def failing_validation(data):
            return False, {"reason": "Always fails"}
        
        rule = ValidationRule(
            rule_id="failing_rule",
            description="Failing rule",
            validation_fn=failing_validation,
            severity="ERROR"
        )
        
        validator.add_rule(rule)
        
        # Create test data
        data = pd.DataFrame({"A": [1, 2, 3], "B": ["x", "y", "z"]})
        
        # Validate
        results = validator.validate(data)
        self.assertEqual(len(results), 1)
        self.assertFalse(results[0].is_valid)
        self.assertEqual(results[0].rule_id, "failing_rule")
        self.assertEqual(results[0].severity, "ERROR")


if __name__ == "__main__":
    unittest.main()
