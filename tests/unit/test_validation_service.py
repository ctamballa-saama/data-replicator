"""
Tests for the validation service.
"""
import unittest
import pandas as pd
from unittest.mock import patch, MagicMock
from datareplicator.validation.service import ValidationService, validation_service
from datareplicator.validation.base import (
    ValidationResult, ValidationSummary, BaseValidator, CompositeValidator
)


class TestValidationService(unittest.TestCase):
    """Test cases for ValidationService class."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Create a fresh validation service for each test
        self.service = ValidationService()
    
    def test_register_validator(self):
        """Test registering a validator."""
        # Create a mock validator
        mock_validator = MagicMock(spec=BaseValidator)
        mock_validator.name = "Mock Validator"
        mock_validator.description = "A mock validator for testing"
        
        # Register it
        self.service.register_validator("mock", mock_validator)
        
        # Check it was registered
        self.assertIn("mock", self.service.validators)
        self.assertEqual(self.service.validators["mock"], mock_validator)
    
    def test_register_duplicate_validator(self):
        """Test that registering a duplicate validator raises an error."""
        # Create a mock validator
        mock_validator = MagicMock(spec=BaseValidator)
        mock_validator.name = "Mock Validator"
        
        # Register it
        self.service.register_validator("mock", mock_validator)
        
        # Try to register another validator with the same ID
        duplicate_validator = MagicMock(spec=BaseValidator)
        duplicate_validator.name = "Duplicate Validator"
        
        with self.assertRaises(ValueError):
            self.service.register_validator("mock", duplicate_validator)
    
    def test_validate_domain_with_all_validators(self):
        """Test validating a domain with all validators."""
        # Create mock validators
        mock_validator1 = MagicMock(spec=BaseValidator)
        mock_validator1.name = "Validator 1"
        mock_validator1.description = "First mock validator"
        # Make validate() return a ValidationResult
        mock_result1 = ValidationResult(
            is_valid=True,
            rule_id="rule1",
            rule_description="Rule 1",
            severity="INFO"
        )
        mock_validator1.validate.return_value = mock_result1
        
        mock_validator2 = MagicMock(spec=BaseValidator)
        mock_validator2.name = "Validator 2"
        mock_validator2.description = "Second mock validator"
        # Make validate() return a ValidationResult
        mock_result2 = ValidationResult(
            is_valid=False,
            rule_id="rule2",
            rule_description="Rule 2",
            severity="ERROR"
        )
        mock_validator2.validate.return_value = mock_result2
        
        # Register the validators
        self.service.register_validator("validator1", mock_validator1)
        self.service.register_validator("validator2", mock_validator2)
        
        # Create test data
        test_data = pd.DataFrame({"A": [1, 2, 3], "B": ["x", "y", "z"]})
        
        # Validate the domain
        summary = self.service.validate_domain(test_data, "test_domain")
        
        # Check the summary
        self.assertEqual(summary.domain_name, "test_domain")
        self.assertFalse(summary.is_valid)  # One validator failed
        self.assertEqual(summary.error_count, 1)
        self.assertEqual(summary.info_count, 0)  # Valid results don't count
        self.assertEqual(len(summary.results), 2)
        
        # Check that both validators were called
        mock_validator1.validate.assert_called_once_with(test_data)
        mock_validator2.validate.assert_called_once_with(test_data)
    
    def test_validate_domain_with_specific_validators(self):
        """Test validating a domain with specific validators."""
        # Create mock validators
        mock_validator1 = MagicMock(spec=BaseValidator)
        mock_validator1.name = "Validator 1"
        mock_validator1.validate.return_value = ValidationResult(
            is_valid=True,
            rule_id="rule1",
            rule_description="Rule 1",
            severity="INFO"
        )
        
        mock_validator2 = MagicMock(spec=BaseValidator)
        mock_validator2.name = "Validator 2"
        mock_validator2.validate.return_value = ValidationResult(
            is_valid=False,
            rule_id="rule2",
            rule_description="Rule 2",
            severity="ERROR"
        )
        
        # Register the validators
        self.service.register_validator("validator1", mock_validator1)
        self.service.register_validator("validator2", mock_validator2)
        
        # Create test data
        test_data = pd.DataFrame({"A": [1, 2, 3], "B": ["x", "y", "z"]})
        
        # Validate the domain with only the first validator
        summary = self.service.validate_domain(
            test_data, 
            "test_domain", 
            validator_ids=["validator1"]
        )
        
        # Check the summary
        self.assertEqual(summary.domain_name, "test_domain")
        self.assertTrue(summary.is_valid)  # Only the passing validator was used
        self.assertEqual(summary.error_count, 0)
        self.assertEqual(len(summary.results), 1)
        
        # Check that only validator1 was called
        mock_validator1.validate.assert_called_once_with(test_data)
        mock_validator2.validate.assert_not_called()
    
    def test_validate_domain_with_composite_validator(self):
        """Test validating a domain with a composite validator."""
        # Create a composite validator
        composite = CompositeValidator("Composite", "A composite validator")
        
        # Add some mock rules to it
        rule_results = [
            ValidationResult(is_valid=True, rule_id="rule1", rule_description="Rule 1", severity="INFO"),
            ValidationResult(is_valid=False, rule_id="rule2", rule_description="Rule 2", severity="WARNING"),
            ValidationResult(is_valid=False, rule_id="rule3", rule_description="Rule 3", severity="ERROR")
        ]
        
        # Mock the validate method to return the predefined results
        composite.validate = MagicMock(return_value=rule_results)
        
        # Register the validator
        self.service.register_validator("composite", composite)
        
        # Create test data
        test_data = pd.DataFrame({"A": [1, 2, 3], "B": ["x", "y", "z"]})
        
        # Validate the domain
        summary = self.service.validate_domain(test_data, "test_domain")
        
        # Check the summary
        self.assertEqual(summary.domain_name, "test_domain")
        self.assertFalse(summary.is_valid)  # One ERROR result
        self.assertEqual(summary.error_count, 1)
        self.assertEqual(summary.warning_count, 1)
        self.assertEqual(summary.info_count, 0)  # Valid results don't count
        self.assertEqual(len(summary.results), 3)
        
        # Check that the validator was called
        composite.validate.assert_called_once_with(test_data)
    
    def test_validate_domain_with_validator_error(self):
        """Test validating a domain when a validator raises an error."""
        # Create a mock validator that raises an exception
        mock_validator = MagicMock(spec=BaseValidator)
        mock_validator.name = "Error Validator"
        mock_validator.description = "A validator that raises an error"
        mock_validator.validate.side_effect = Exception("Validation error")
        
        # Register the validator
        self.service.register_validator("error", mock_validator)
        
        # Create test data
        test_data = pd.DataFrame({"A": [1, 2, 3], "B": ["x", "y", "z"]})
        
        # Validate the domain
        summary = self.service.validate_domain(test_data, "test_domain")
        
        # Check the summary
        self.assertEqual(summary.domain_name, "test_domain")
        self.assertFalse(summary.is_valid)  # The error is treated as a failure
        self.assertEqual(summary.error_count, 1)
        self.assertEqual(len(summary.results), 1)
        
        # Check the error result
        error_result = summary.results[0]
        self.assertFalse(error_result.is_valid)
        self.assertEqual(error_result.rule_id, "Error Validator.Error")
        self.assertTrue("Validation error" in error_result.error_message)
        self.assertEqual(error_result.severity, "ERROR")
    
    def test_create_custom_validator(self):
        """Test creating a custom validator."""
        validator = self.service.create_custom_validator(
            validator_id="custom",
            name="Custom Validator",
            description="A custom validator"
        )
        
        # Check the validator was created and registered
        self.assertIn("custom", self.service.validators)
        self.assertEqual(validator.name, "Custom Validator")
        self.assertEqual(validator.description, "A custom validator")
        self.assertEqual(len(validator.rules), 0)
    
    def test_add_custom_rule(self):
        """Test adding a custom rule to a validator."""
        # Create a custom validator
        validator = self.service.create_custom_validator(
            validator_id="custom",
            name="Custom Validator",
            description="A custom validator"
        )
        
        # Create a simple validation function
        def test_validation(data):
            return True, {}
        
        # Add a rule to it
        self.service.add_custom_rule(
            validator_id="custom",
            rule_id="test_rule",
            description="Test rule",
            validation_fn=test_validation,
            severity="INFO"
        )
        
        # Check the rule was added
        self.assertEqual(len(validator.rules), 1)
        self.assertEqual(validator.rules[0].rule_id, "test_rule")
        self.assertEqual(validator.rules[0].description, "Test rule")
        self.assertEqual(validator.rules[0].severity, "INFO")
        
        # Also check it was registered in the rule registry
        rule = self.service.custom_rule_registry.get_rule("test_rule")
        self.assertIsNotNone(rule)
        self.assertEqual(rule.rule_id, "test_rule")
    
    def test_add_rule_to_nonexistent_validator(self):
        """Test adding a rule to a non-existent validator."""
        # Create a simple validation function
        def test_validation(data):
            return True, {}
        
        # Try to add a rule to a non-existent validator
        with self.assertRaises(ValueError):
            self.service.add_custom_rule(
                validator_id="nonexistent",
                rule_id="test_rule",
                description="Test rule",
                validation_fn=test_validation
            )
    
    def test_add_rule_to_non_composite_validator(self):
        """Test adding a rule to a non-composite validator."""
        # Create a mock validator that is not a composite
        mock_validator = MagicMock(spec=BaseValidator)
        mock_validator.name = "Simple Validator"
        
        # Register it
        self.service.register_validator("simple", mock_validator)
        
        # Create a simple validation function
        def test_validation(data):
            return True, {}
        
        # Try to add a rule to it
        with self.assertRaises(ValueError):
            self.service.add_custom_rule(
                validator_id="simple",
                rule_id="test_rule",
                description="Test rule",
                validation_fn=test_validation
            )
    
    def test_list_validators(self):
        """Test listing all validators."""
        # Register some validators
        mock_validator1 = MagicMock(spec=BaseValidator)
        mock_validator1.name = "Validator 1"
        mock_validator1.description = "First mock validator"
        
        mock_validator2 = MagicMock(spec=BaseValidator)
        mock_validator2.name = "Validator 2"
        mock_validator2.description = "Second mock validator"
        
        self.service.register_validator("validator1", mock_validator1)
        self.service.register_validator("validator2", mock_validator2)
        
        # List validators
        validators_list = self.service.list_validators()
        
        # Check the list
        self.assertEqual(len(validators_list), 2)
        
        # Check the validator info dictionaries
        validator_ids = [v["id"] for v in validators_list]
        self.assertIn("validator1", validator_ids)
        self.assertIn("validator2", validator_ids)
        
        # Check the first validator details
        validator1_info = next(v for v in validators_list if v["id"] == "validator1")
        self.assertEqual(validator1_info["name"], "Validator 1")
        self.assertEqual(validator1_info["description"], "First mock validator")
    
    def test_list_rules(self):
        """Test listing all rules."""
        # Create a custom validator with rules
        validator = self.service.create_custom_validator(
            validator_id="custom",
            name="Custom Validator",
            description="A custom validator"
        )
        
        # Create a simple validation function
        def test_validation(data):
            return True, {}
        
        # Add rules to it
        self.service.add_custom_rule(
            validator_id="custom",
            rule_id="rule1",
            description="Rule 1",
            validation_fn=test_validation,
            severity="INFO"
        )
        
        self.service.add_custom_rule(
            validator_id="custom",
            rule_id="rule2",
            description="Rule 2",
            validation_fn=test_validation,
            severity="WARNING"
        )
        
        # List all rules
        rules_list = self.service.list_rules()
        
        # Check the list
        self.assertEqual(len(rules_list), 2)
        
        # Check the rule info dictionaries
        rule_ids = [rule["rule_id"] for rule in rules_list]
        self.assertIn("rule1", rule_ids)
        self.assertIn("rule2", rule_ids)
    
    def test_list_rules_for_specific_validator(self):
        """Test listing rules for a specific validator."""
        # Create two custom validators with rules
        validator1 = self.service.create_custom_validator(
            validator_id="custom1",
            name="Custom Validator 1",
            description="First custom validator"
        )
        
        validator2 = self.service.create_custom_validator(
            validator_id="custom2",
            name="Custom Validator 2",
            description="Second custom validator"
        )
        
        # Create a simple validation function
        def test_validation(data):
            return True, {}
        
        # Add rules to the first validator
        self.service.add_custom_rule(
            validator_id="custom1",
            rule_id="rule1",
            description="Rule 1",
            validation_fn=test_validation,
            severity="INFO"
        )
        
        self.service.add_custom_rule(
            validator_id="custom1",
            rule_id="rule2",
            description="Rule 2",
            validation_fn=test_validation,
            severity="WARNING"
        )
        
        # Add a rule to the second validator
        self.service.add_custom_rule(
            validator_id="custom2",
            rule_id="rule3",
            description="Rule 3",
            validation_fn=test_validation,
            severity="ERROR"
        )
        
        # List rules for the first validator
        rules_list = self.service.list_rules("custom1")
        
        # Check the list
        self.assertEqual(len(rules_list), 2)
        
        # Check the rule info dictionaries
        rule_ids = [rule["rule_id"] for rule in rules_list]
        self.assertIn("rule1", rule_ids)
        self.assertIn("rule2", rule_ids)
        self.assertNotIn("rule3", rule_ids)
    
    def test_list_rules_for_nonexistent_validator(self):
        """Test listing rules for a non-existent validator."""
        with self.assertRaises(ValueError):
            self.service.list_rules("nonexistent")


if __name__ == "__main__":
    unittest.main()
