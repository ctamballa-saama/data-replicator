"""
Tests for the custom validation rules functionality.
"""
import unittest
import pandas as pd
import re
from datareplicator.validation.custom_rules import CustomRuleRegistry, RuleBuilder
from datareplicator.validation.base import ValidationRule


class TestCustomRuleRegistry(unittest.TestCase):
    """Test cases for CustomRuleRegistry class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.registry = CustomRuleRegistry()
    
    def test_register_rule(self):
        """Test registering a rule."""
        # Create a simple rule
        def test_validation(data):
            return True, {}
        
        rule = ValidationRule(
            rule_id="test_rule",
            description="Test rule",
            validation_fn=test_validation,
            severity="INFO"
        )
        
        # Register the rule
        self.registry.register_rule(rule)
        
        # Check it was registered
        self.assertIn("test_rule", self.registry.rules)
        self.assertEqual(self.registry.rules["test_rule"], rule)
    
    def test_register_duplicate_rule(self):
        """Test that registering a duplicate rule raises an error."""
        # Create a simple rule
        def test_validation(data):
            return True, {}
        
        rule = ValidationRule(
            rule_id="test_rule",
            description="Test rule",
            validation_fn=test_validation,
            severity="INFO"
        )
        
        # Register the rule
        self.registry.register_rule(rule)
        
        # Try to register another rule with the same ID
        duplicate_rule = ValidationRule(
            rule_id="test_rule",
            description="Duplicate rule",
            validation_fn=test_validation,
            severity="WARNING"
        )
        
        with self.assertRaises(ValueError):
            self.registry.register_rule(duplicate_rule)
    
    def test_get_rule(self):
        """Test getting a rule by ID."""
        # Create a simple rule
        def test_validation(data):
            return True, {}
        
        rule = ValidationRule(
            rule_id="test_rule",
            description="Test rule",
            validation_fn=test_validation,
            severity="INFO"
        )
        
        # Register the rule
        self.registry.register_rule(rule)
        
        # Get the rule
        retrieved_rule = self.registry.get_rule("test_rule")
        self.assertEqual(retrieved_rule, rule)
        
        # Try to get a non-existent rule
        non_existent_rule = self.registry.get_rule("non_existent")
        self.assertIsNone(non_existent_rule)
    
    def test_list_rules(self):
        """Test listing all rules."""
        # Create and register two rules
        def test_validation(data):
            return True, {}
        
        rule1 = ValidationRule(
            rule_id="rule1",
            description="Rule 1",
            validation_fn=test_validation,
            severity="INFO"
        )
        
        rule2 = ValidationRule(
            rule_id="rule2",
            description="Rule 2",
            validation_fn=test_validation,
            severity="WARNING"
        )
        
        self.registry.register_rule(rule1)
        self.registry.register_rule(rule2)
        
        # List rules
        rules_list = self.registry.list_rules()
        self.assertEqual(len(rules_list), 2)
        
        # Check the rule info dictionaries
        rule_ids = [rule["rule_id"] for rule in rules_list]
        self.assertIn("rule1", rule_ids)
        self.assertIn("rule2", rule_ids)


class TestRuleBuilder(unittest.TestCase):
    """Test cases for RuleBuilder class."""
    
    def test_create_range_rule(self):
        """Test creating a range validation rule."""
        # Create a range rule
        rule = RuleBuilder.create_range_rule(
            rule_id="test_range",
            field_name="age",
            min_value=18,
            max_value=65,
            inclusive=True,
            severity="ERROR"
        )
        
        # Verify rule properties
        self.assertEqual(rule.rule_id, "test_range")
        self.assertEqual(rule.severity, "ERROR")
        self.assertTrue("age" in rule.description.lower())
        
        # Test the validation function with valid data
        valid_data = pd.DataFrame({"age": [20, 30, 40, 50, 60]})
        is_valid, error_info = rule.validation_fn(valid_data)
        self.assertTrue(is_valid)
        
        # Test with invalid data
        invalid_data = pd.DataFrame({"age": [10, 20, 70, 40]})
        is_valid, error_info = rule.validation_fn(invalid_data)
        self.assertFalse(is_valid)
        self.assertIn("row_indices", error_info)
        self.assertEqual(len(error_info["row_indices"]), 2)  # Two invalid rows (10 and 70)
    
    def test_create_pattern_rule(self):
        """Test creating a pattern validation rule."""
        # Create a pattern rule for email validation
        rule = RuleBuilder.create_pattern_rule(
            rule_id="email_pattern",
            field_name="email",
            pattern=r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$",
            pattern_description="Valid email address",
            severity="ERROR"
        )
        
        # Verify rule properties
        self.assertEqual(rule.rule_id, "email_pattern")
        self.assertEqual(rule.severity, "ERROR")
        self.assertTrue("email" in rule.description.lower())
        
        # Test the validation function with valid data
        valid_data = pd.DataFrame({"email": ["user@example.com", "test.user@company.org"]})
        is_valid, error_info = rule.validation_fn(valid_data)
        self.assertTrue(is_valid)
        
        # Test with invalid data
        invalid_data = pd.DataFrame({"email": ["user@example", "test.user@", "invalid"]})
        is_valid, error_info = rule.validation_fn(invalid_data)
        self.assertFalse(is_valid)
        self.assertIn("row_indices", error_info)
        self.assertEqual(len(error_info["row_indices"]), 3)  # Three invalid emails
    
    def test_create_unique_rule(self):
        """Test creating a uniqueness validation rule."""
        # Create a unique rule
        rule = RuleBuilder.create_unique_rule(
            rule_id="unique_id",
            field_name="id",
            severity="ERROR"
        )
        
        # Verify rule properties
        self.assertEqual(rule.rule_id, "unique_id")
        self.assertEqual(rule.severity, "ERROR")
        self.assertTrue("id" in rule.description.lower())
        self.assertTrue("unique" in rule.description.lower())
        
        # Test the validation function with valid data
        valid_data = pd.DataFrame({"id": [1, 2, 3, 4, 5]})
        is_valid, error_info = rule.validation_fn(valid_data)
        self.assertTrue(is_valid)
        
        # Test with invalid data (duplicate IDs)
        invalid_data = pd.DataFrame({"id": [1, 2, 2, 3, 1]})
        is_valid, error_info = rule.validation_fn(invalid_data)
        self.assertFalse(is_valid)
        self.assertIn("duplicate_values", error_info)
        self.assertEqual(len(error_info["duplicate_values"]), 2)  # Two duplicate values (1 and 2)
    
    def test_create_custom_rule(self):
        """Test creating a custom validation rule."""
        # Create a custom validation function
        def validate_positive(data):
            if "amount" not in data.columns:
                return False, {"error": "Column 'amount' not found"}
            
            negative_indices = data.index[data["amount"] < 0].tolist()
            if negative_indices:
                return False, {
                    "field_name": "amount",
                    "row_indices": negative_indices,
                    "error": "Amount must be positive"
                }
            return True, {}
        
        # Create a custom rule
        rule = RuleBuilder.create_custom_rule(
            rule_id="positive_amount",
            description="Amount must be positive",
            validation_fn=validate_positive,
            severity="ERROR"
        )
        
        # Verify rule properties
        self.assertEqual(rule.rule_id, "positive_amount")
        self.assertEqual(rule.description, "Amount must be positive")
        self.assertEqual(rule.severity, "ERROR")
        
        # Test the validation function with valid data
        valid_data = pd.DataFrame({"amount": [10.5, 20.0, 30.75, 5.25]})
        is_valid, error_info = rule.validation_fn(valid_data)
        self.assertTrue(is_valid)
        
        # Test with invalid data
        invalid_data = pd.DataFrame({"amount": [10.5, -20.0, 30.75, -5.25]})
        is_valid, error_info = rule.validation_fn(invalid_data)
        self.assertFalse(is_valid)
        self.assertIn("row_indices", error_info)
        self.assertEqual(len(error_info["row_indices"]), 2)  # Two negative values


if __name__ == "__main__":
    unittest.main()
