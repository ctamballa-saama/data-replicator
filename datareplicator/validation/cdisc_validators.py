"""
CDISC-specific validators for DataReplicator.

This module provides validators that enforce CDISC standards for clinical trial data.
"""
import pandas as pd
import numpy as np
import re
from typing import Dict, Any, Tuple, List, Optional, Union

from datareplicator.validation.base import BaseValidator, ValidationResult, ValidationRule, CompositeValidator


class CDISCDataTypeValidator(BaseValidator):
    """Validator to ensure data types conform to CDISC standards."""
    
    def __init__(self):
        super().__init__(
            name="CDISC Data Type Validator",
            description="Validates that data types conform to CDISC standards"
        )
        # Map of CDISC variable naming conventions to expected data types
        self.cdisc_type_mapping = {
            "DT": "date",
            "TM": "time",
            "STDY": "numeric",
            "STDM": "numeric",
            "STDF": "numeric",
            "AGE": "numeric",
            "DUR": "numeric",
            "WGHT": "numeric",
            "HGHT": "numeric",
            "TEMP": "numeric",
            "FLAG": "categorical",
            "STAT": "categorical",
            "REASON": "text"
        }
    
    def validate(self, data: pd.DataFrame) -> ValidationResult:
        """Validate that column data types match CDISC conventions."""
        # Check each column name against CDISC suffixes
        for column in data.columns:
            # Extract potential CDISC suffix (last part after last delimiter)
            parts = column.split("_")
            if len(parts) > 1:
                suffix = parts[-1]
                
                # Check if this is a known CDISC suffix
                if suffix in self.cdisc_type_mapping:
                    expected_type = self.cdisc_type_mapping[suffix]
                    
                    # Validate data type
                    is_valid = self._validate_column_type(data[column], expected_type)
                    
                    if not is_valid:
                        actual_type = self._detect_column_type(data[column])
                        return ValidationResult(
                            is_valid=False,
                            rule_id=f"{self.rule_id}.DataType",
                            rule_description=f"Column data type must match CDISC convention for suffix '{suffix}'",
                            field_name=column,
                            error_message=f"Expected {expected_type} data type for column with suffix '{suffix}', found {actual_type}",
                            severity="ERROR"
                        )
        
        # If all columns passed validation
        return ValidationResult(
            is_valid=True,
            rule_id=f"{self.rule_id}.DataType",
            rule_description="Data types match CDISC conventions",
            severity="INFO"
        )
    
    def _validate_column_type(self, column: pd.Series, expected_type: str) -> bool:
        """Validate that a column's data type matches the expected type."""
        actual_type = self._detect_column_type(column)
        return actual_type == expected_type
    
    def _detect_column_type(self, column: pd.Series) -> str:
        """Detect the data type of a column."""
        # Remove NaN values for type detection
        non_na = column.dropna()
        
        # Empty column or all NaN
        if len(non_na) == 0:
            return "unknown"
        
        # Check if all values are dates
        if pd.api.types.is_datetime64_dtype(non_na):
            return "date"
        
        # Check if values look like times
        if all(isinstance(x, str) and re.match(r'^\d{2}:\d{2}(:\d{2})?$', x) for x in non_na):
            return "time"
        
        # Check if numeric
        if pd.api.types.is_numeric_dtype(non_na):
            return "numeric"
        
        # Check if categorical (few unique values)
        if len(non_na.unique()) / len(non_na) < 0.1 or len(non_na.unique()) < 10:
            return "categorical"
        
        # Default to text
        return "text"


class CDISCNamingValidator(BaseValidator):
    """Validator to ensure variable names conform to CDISC naming conventions."""
    
    def __init__(self):
        super().__init__(
            name="CDISC Naming Validator",
            description="Validates that variable names conform to CDISC conventions"
        )
    
    def validate(self, data: pd.DataFrame) -> ValidationResult:
        """Validate that column names follow CDISC conventions."""
        invalid_columns = []
        
        for column in data.columns:
            # Check CDISC naming rules (8 characters, uppercase, alphanumeric)
            if not self._is_valid_cdisc_name(column):
                invalid_columns.append(column)
        
        if invalid_columns:
            return ValidationResult(
                is_valid=False,
                rule_id=f"{self.rule_id}.Naming",
                rule_description="Column names must follow CDISC naming conventions",
                field_name=", ".join(invalid_columns),
                error_message=f"Column names do not follow CDISC naming convention: {', '.join(invalid_columns)}",
                severity="WARNING"
            )
        
        # If all columns passed validation
        return ValidationResult(
            is_valid=True,
            rule_id=f"{self.rule_id}.Naming",
            rule_description="Column names follow CDISC conventions",
            severity="INFO"
        )
    
    def _is_valid_cdisc_name(self, name: str) -> bool:
        """Check if a name follows CDISC conventions."""
        # SDTM variable naming conventions
        # Names should be 8 characters or less
        # Names should be uppercase
        # Names can contain letters, numbers, and underscores
        # Allow for non-strict CDISC names for broader compatibility
        
        # Check if strict CDISC (8 chars, uppercase, alphanumeric)
        strict_pattern = re.compile(r'^[A-Z][A-Z0-9_]{0,7}$')
        if strict_pattern.match(name):
            return True
        
        # Check if extended CDISC-like (mixed case, with underscores as delimiters)
        extended_pattern = re.compile(r'^[A-Za-z][A-Za-z0-9_]*$')
        return extended_pattern.match(name) is not None


class CDISCMissingValueValidator(BaseValidator):
    """Validator to ensure missing values are handled correctly per CDISC standards."""
    
    def __init__(self):
        super().__init__(
            name="CDISC Missing Value Validator",
            description="Validates that missing values are handled correctly per CDISC standards"
        )
    
    def validate(self, data: pd.DataFrame) -> ValidationResult:
        """Validate that missing values are handled correctly."""
        # CDISC has specific rules for missing values
        invalid_missings = []
        
        for column in data.columns:
            # Check for invalid missing value indicators
            if self._has_invalid_missing_indicators(data[column]):
                invalid_missings.append(column)
        
        if invalid_missings:
            return ValidationResult(
                is_valid=False,
                rule_id=f"{self.rule_id}.MissingValues",
                rule_description="Missing values must use standard CDISC missing value indicators",
                field_name=", ".join(invalid_missings),
                error_message=f"Invalid missing value indicators found in columns: {', '.join(invalid_missings)}",
                severity="WARNING"
            )
        
        # If all columns passed validation
        return ValidationResult(
            is_valid=True,
            rule_id=f"{self.rule_id}.MissingValues",
            rule_description="Missing values use standard CDISC indicators",
            severity="INFO"
        )
    
    def _has_invalid_missing_indicators(self, column: pd.Series) -> bool:
        """Check for invalid missing value indicators in a column."""
        # Valid CDISC missing indicators
        valid_indicators = [None, np.nan, "", "NA", "N/A", "NULL", "UNKNOWN", "UNK", "MISSING"]
        
        # Convert to strings for text comparison, keeping NaN as is
        non_na_values = [str(x).upper() if not pd.isna(x) else x for x in column]
        
        # Check for values that look like missing indicators but aren't standard
        suspicious_patterns = ["MISS", "NONE", "NIL", "?", "--", "-999"]
        
        for value in non_na_values:
            if pd.isna(value):
                continue  # Skip proper NaN values
                
            if (value not in [str(x).upper() if not pd.isna(x) else x for x in valid_indicators] and 
                any(pattern in value for pattern in suspicious_patterns)):
                return True
        
        return False


class CDISCValidator(CompositeValidator):
    """Composite validator that implements all CDISC validation rules."""
    
    def __init__(self):
        super().__init__(
            name="CDISC Validator",
            description="Validates data against CDISC standards"
        )
        
        # Add individual CDISC validators
        self.data_type_validator = CDISCDataTypeValidator()
        self.naming_validator = CDISCNamingValidator()
        self.missing_validator = CDISCMissingValueValidator()
        
        # Create rules from validators
        self.add_rule(ValidationRule(
            rule_id="CDISC.DataType",
            description="Data types must conform to CDISC standards",
            validation_fn=self._validate_data_types
        ))
        
        self.add_rule(ValidationRule(
            rule_id="CDISC.Naming",
            description="Variable names must conform to CDISC conventions",
            validation_fn=self._validate_naming,
            severity="WARNING"
        ))
        
        self.add_rule(ValidationRule(
            rule_id="CDISC.MissingValues",
            description="Missing values must use standard CDISC indicators",
            validation_fn=self._validate_missing_values,
            severity="WARNING"
        ))
    
    def _validate_data_types(self, data: pd.DataFrame) -> Tuple[bool, Dict[str, Any]]:
        """Validate data types against CDISC standards."""
        result = self.data_type_validator.validate(data)
        return result.is_valid, {
            'field_name': result.field_name,
            'error_message': result.error_message
        }
    
    def _validate_naming(self, data: pd.DataFrame) -> Tuple[bool, Dict[str, Any]]:
        """Validate variable names against CDISC conventions."""
        result = self.naming_validator.validate(data)
        return result.is_valid, {
            'field_name': result.field_name,
            'error_message': result.error_message
        }
    
    def _validate_missing_values(self, data: pd.DataFrame) -> Tuple[bool, Dict[str, Any]]:
        """Validate missing value handling against CDISC standards."""
        result = self.missing_validator.validate(data)
        return result.is_valid, {
            'field_name': result.field_name,
            'error_message': result.error_message
        }
