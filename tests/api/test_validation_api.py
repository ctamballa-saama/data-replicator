"""
API tests for validation endpoints.
"""
import pytest
import pandas as pd
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock

from datareplicator.api.app import app
from datareplicator.data.registry import domain_registry
from datareplicator.validation.base import ValidationResult, ValidationSummary
from datareplicator.validation.service import validation_service


@pytest.fixture
def test_client():
    """Create a test client for the API."""
    return TestClient(app)


@pytest.fixture
def mock_domain():
    """Create a mock domain with test data."""
    domain = MagicMock()
    domain.name = "test_domain"
    domain.get_data.return_value = pd.DataFrame({
        "SUBJID": ["001", "002", "003"],
        "AGE": [35, 42, 28],
        "SEX": ["M", "F", "M"],
        "COUNTRY": ["USA", "CAN", "GBR"]
    })
    return domain


def test_list_validators(test_client):
    """Test listing available validators."""
    # Mock the validation service list_validators method
    with patch.object(validation_service, 'list_validators') as mock_list:
        mock_list.return_value = [
            {"id": "cdisc", "name": "CDISC Validator", "description": "Validates against CDISC standards"},
            {"id": "custom", "name": "Custom Validator", "description": "Custom validation rules"}
        ]
        
        response = test_client.get("/validation/validators")
        
        # Check the response
        assert response.status_code == 200
        validators = response.json()
        assert len(validators) == 2
        assert validators[0]["id"] == "cdisc"
        assert validators[1]["id"] == "custom"


def test_list_validation_rules(test_client):
    """Test listing validation rules."""
    # Mock the validation service list_rules method
    with patch.object(validation_service, 'list_rules') as mock_list:
        mock_list.return_value = [
            {"rule_id": "rule1", "description": "Test rule 1", "severity": "ERROR"},
            {"rule_id": "rule2", "description": "Test rule 2", "severity": "WARNING"}
        ]
        
        response = test_client.get("/validation/rules")
        
        # Check the response
        assert response.status_code == 200
        rules = response.json()
        assert len(rules) == 2
        assert rules[0]["rule_id"] == "rule1"
        assert rules[1]["rule_id"] == "rule2"


def test_list_validation_rules_with_validator(test_client):
    """Test listing validation rules for a specific validator."""
    # Mock the validation service list_rules method
    with patch.object(validation_service, 'list_rules') as mock_list:
        mock_list.return_value = [
            {"rule_id": "cdisc_rule1", "description": "CDISC rule 1", "severity": "ERROR"},
        ]
        
        response = test_client.get("/validation/rules?validator_id=cdisc")
        
        # Check the response
        assert response.status_code == 200
        rules = response.json()
        assert len(rules) == 1
        assert rules[0]["rule_id"] == "cdisc_rule1"


def test_list_validation_rules_with_nonexistent_validator(test_client):
    """Test listing validation rules for a non-existent validator."""
    # Mock the validation service list_rules method to raise a ValueError
    with patch.object(validation_service, 'list_rules') as mock_list:
        mock_list.side_effect = ValueError("Validator with ID 'nonexistent' does not exist")
        
        response = test_client.get("/validation/rules?validator_id=nonexistent")
        
        # Check the response
        assert response.status_code == 400
        assert "does not exist" in response.json()["detail"]


def test_validate_domain(test_client, mock_domain):
    """Test validating a domain."""
    # Mock the domain registry and validation service
    with patch.object(domain_registry, 'get_domain', return_value=mock_domain), \
         patch.object(validation_service, 'validate_domain') as mock_validate:
        
        # Create a mock validation summary
        summary = ValidationSummary("test_domain")
        
        # Add some validation results
        valid_result = ValidationResult(
            is_valid=True,
            rule_id="valid_rule",
            rule_description="Valid rule",
            severity="INFO"
        )
        summary.add_result(valid_result)
        
        error_result = ValidationResult(
            is_valid=False,
            rule_id="error_rule",
            rule_description="Error rule",
            field_name="AGE",
            error_message="Invalid age value",
            row_index=1,
            severity="ERROR"
        )
        summary.add_result(error_result)
        
        warning_result = ValidationResult(
            is_valid=False,
            rule_id="warning_rule",
            rule_description="Warning rule",
            field_name="COUNTRY",
            error_message="Unknown country code",
            row_index=2,
            severity="WARNING"
        )
        summary.add_result(warning_result)
        
        # Set up the mock to return our summary
        mock_validate.return_value = summary
        
        # Make the request
        response = test_client.post(
            "/validation/validate",
            json={"domain_name": "test_domain"}
        )
        
        # Check the response
        assert response.status_code == 200
        validation_response = response.json()
        assert validation_response["domain_name"] == "test_domain"
        assert validation_response["is_valid"] is False
        assert validation_response["error_count"] == 1
        assert validation_response["warning_count"] == 1
        assert validation_response["info_count"] == 0
        assert len(validation_response["results"]) == 3
        
        # Check that validation_service.validate_domain was called with correct args
        mock_validate.assert_called_once()
        args, kwargs = mock_validate.call_args
        assert kwargs["domain_name"] == "test_domain"
        assert kwargs["validator_ids"] is None


def test_validate_domain_with_specific_validators(test_client, mock_domain):
    """Test validating a domain with specific validators."""
    # Mock the domain registry and validation service
    with patch.object(domain_registry, 'get_domain', return_value=mock_domain), \
         patch.object(validation_service, 'validate_domain') as mock_validate:
        
        # Create a mock validation summary
        summary = ValidationSummary("test_domain")
        mock_validate.return_value = summary
        
        # Make the request with specific validators
        response = test_client.post(
            "/validation/validate",
            json={
                "domain_name": "test_domain",
                "validator_ids": ["cdisc", "custom"]
            }
        )
        
        # Check the response
        assert response.status_code == 200
        
        # Check that validation_service.validate_domain was called with correct args
        mock_validate.assert_called_once()
        args, kwargs = mock_validate.call_args
        assert kwargs["domain_name"] == "test_domain"
        assert kwargs["validator_ids"] == ["cdisc", "custom"]


def test_validate_nonexistent_domain(test_client):
    """Test validating a non-existent domain."""
    # Mock the domain registry
    with patch.object(domain_registry, 'get_domain', return_value=None):
        # Make the request
        response = test_client.post(
            "/validation/validate",
            json={"domain_name": "nonexistent_domain"}
        )
        
        # Check the response
        assert response.status_code == 404
        assert "not found" in response.json()["detail"]


def test_validate_domain_with_error(test_client, mock_domain):
    """Test validating a domain when an error occurs."""
    # Mock the domain registry and validation service
    with patch.object(domain_registry, 'get_domain', return_value=mock_domain), \
         patch.object(validation_service, 'validate_domain') as mock_validate:
        
        # Make the validation service raise an exception
        mock_validate.side_effect = Exception("Validation error")
        
        # Make the request
        response = test_client.post(
            "/validation/validate",
            json={"domain_name": "test_domain"}
        )
        
        # Check the response
        assert response.status_code == 500
        assert "Validation error" in response.json()["detail"]
