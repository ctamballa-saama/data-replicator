"""
Unit tests for the CSV parser module.
"""
import os
import pytest
from pathlib import Path

from datareplicator.core.config import DomainType
from datareplicator.data.parsing.csv_parser import CSVParser
from datareplicator.data.parsing.utils import is_valid_date, infer_column_type, get_pii_columns


class TestCSVParser:
    """Test cases for the CSV parser."""
    
    def test_detect_domain(self):
        """Test domain detection from sample files."""
        parser = CSVParser()
        
        # Test with sample files
        project_root = Path(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))
        data_dir = project_root / "data" / "sample"
        
        # Demographics file
        dm_path = data_dir / "dm.csv"
        assert parser.detect_domain(dm_path) == DomainType.DEMOGRAPHICS
        
        # Lab file
        lb_path = data_dir / "lb.csv"
        assert parser.detect_domain(lb_path) == DomainType.LABORATORY
        
        # Vital signs file
        vs_path = data_dir / "vs.csv"
        assert parser.detect_domain(vs_path) == DomainType.VITAL_SIGNS
    
    def test_parse_file_success(self):
        """Test successful parsing of a CSV file."""
        parser = CSVParser()
        
        # Test with sample files
        project_root = Path(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))
        data_dir = project_root / "data" / "sample"
        
        # Demographics file
        dm_path = data_dir / "dm.csv"
        summary = parser.parse_file(dm_path)
        
        assert summary.success is True
        assert summary.domain_type == DomainType.DEMOGRAPHICS
        assert summary.error_count == 0
        assert summary.row_count > 0
        assert summary.column_count > 0
        assert summary.subject_count > 0
    
    def test_parse_file_not_found(self):
        """Test parsing a non-existent file."""
        parser = CSVParser()
        
        # Test with non-existent file
        non_existent_file = Path("/non/existent/file.csv")
        summary = parser.parse_file(non_existent_file)
        
        assert summary.success is False
        assert summary.error_count == 1
        assert len(summary.errors) == 1
        assert summary.errors[0].error_type == "FileNotFoundError"


class TestParserUtils:
    """Test cases for parser utility functions."""
    
    def test_is_valid_date(self):
        """Test date validation function."""
        # Valid dates
        assert is_valid_date("2023-01-15") is True
        assert is_valid_date("20230115") is True
        assert is_valid_date("15Jan2023") is True
        
        # Invalid dates
        assert is_valid_date("not-a-date") is False
        assert is_valid_date("2023-13-01") is False  # Invalid month
    
    def test_infer_column_type(self):
        """Test column type inference."""
        # Numeric
        assert infer_column_type(["1", "2", "3.5", "4"]) == "numeric"
        
        # Date
        assert infer_column_type(["2023-01-01", "2023-02-01"]) == "date"
        
        # Categorical
        assert infer_column_type(["Male", "Female", "Male", "Female", "Male"]) == "categorical"
        
        # String
        assert infer_column_type(["Value1", "Value2", "Value3", "Value4", "Value5", 
                                 "Value6", "Value7", "Value8", "Value9", "Value10", 
                                 "Value11"]) == "string"
    
    def test_get_pii_columns(self):
        """Test PII column detection."""
        columns = [
            "USUBJID", "SUBJID", "AGE", "SEX", "NAME", "ADDRESS", "EMAIL", 
            "BIRTHDT", "RESULT", "SITEID", "COUNTRY"
        ]
        
        pii_columns = get_pii_columns(columns)
        
        # Known PII fields from constants
        assert "SUBJID" in pii_columns
        assert "SITEID" in pii_columns
        
        # PII-suggestive names
        assert "NAME" in pii_columns
        assert "ADDRESS" in pii_columns
        assert "EMAIL" in pii_columns
        assert "BIRTHDT" in pii_columns
        assert "COUNTRY" in pii_columns
        
        # Not PII
        assert "AGE" not in pii_columns
        assert "SEX" not in pii_columns
        assert "RESULT" not in pii_columns
