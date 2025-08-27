"""
Utility functions for data parsing.

Contains helper functions for common parsing and validation tasks.
"""
import re
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional, Set, Tuple, Union

from datareplicator.core.config import constants, DomainType
from datareplicator.data.models import ParseError


logger = logging.getLogger(__name__)


def is_valid_date(date_str: str, formats: List[str] = None) -> bool:
    """
    Check if a string is a valid date in any of the given formats.
    
    Args:
        date_str: The date string to validate
        formats: List of date formats to try (default: ISO formats)
        
    Returns:
        bool: True if valid date, False otherwise
    """
    if not formats:
        formats = ["%Y-%m-%d", "%Y%m%d", "%d%b%Y", "%d-%b-%Y"]
    
    for fmt in formats:
        try:
            datetime.strptime(date_str, fmt)
            return True
        except ValueError:
            continue
    
    return False


def infer_column_type(values: List[Any]) -> str:
    """
    Infer the data type of a column based on its values.
    
    Args:
        values: List of values from the column
        
    Returns:
        str: Inferred data type ("numeric", "date", "categorical", or "string")
    """
    # Filter out None and empty values
    non_empty_values = [v for v in values if v is not None and str(v).strip()]
    
    if not non_empty_values:
        return "string"
    
    # Check if all values are numeric
    try:
        all_numeric = all(isinstance(float(str(v).strip()), float) for v in non_empty_values)
        if all_numeric:
            return "numeric"
    except ValueError:
        pass
    
    # Check if all values are dates
    if all(is_valid_date(str(v)) for v in non_empty_values):
        return "date"
    
    # Check if it's categorical (limited set of distinct values)
    unique_values = set(str(v).strip() for v in non_empty_values)
    if len(unique_values) <= min(10, len(non_empty_values) * 0.5):
        return "categorical"
    
    # Default to string
    return "string"


def detect_delimiter(file_path: Path) -> str:
    """
    Detect the delimiter used in a CSV file.
    
    Args:
        file_path: Path to the CSV file
        
    Returns:
        str: Detected delimiter (comma, tab, or semicolon)
    """
    with open(file_path, 'r', encoding=constants.DEFAULT_ENCODING) as f:
        first_line = f.readline().strip()
    
    # Count potential delimiters
    comma_count = first_line.count(',')
    tab_count = first_line.count('\t')
    semicolon_count = first_line.count(';')
    
    # Return the most frequent delimiter
    counts = {
        ',': comma_count,
        '\t': tab_count,
        ';': semicolon_count
    }
    
    # Default to comma if no delimiters found
    return max(counts, key=counts.get) if any(counts.values()) else ','


def validate_subject_id(subject_id: str) -> Tuple[bool, Optional[str]]:
    """
    Validate a subject identifier according to CDISC standards.
    
    Args:
        subject_id: The subject identifier to validate
        
    Returns:
        Tuple[bool, Optional[str]]: (is_valid, error_message)
    """
    # Basic validation - non-empty and no special characters except hyphen and underscore
    if not subject_id or not subject_id.strip():
        return False, "Subject ID cannot be empty"
    
    if not re.match(r'^[A-Za-z0-9\-_]+$', subject_id):
        return False, "Subject ID contains invalid characters"
    
    return True, None


def get_pii_columns(columns: List[str]) -> Set[str]:
    """
    Identify columns that likely contain PII (Personally Identifiable Information).
    
    Args:
        columns: List of column names
        
    Returns:
        Set[str]: Set of column names identified as containing PII
    """
    pii_columns = set()
    
    # Add known PII fields from constants
    pii_columns.update(column for column in columns if column in constants.PII_FIELDS)
    
    # Add columns with PII-suggestive names
    pii_keywords = [
        "name", "address", "email", "phone", "birth", "ssn", "social", "zip",
        "postal", "license", "patient", "city", "state", "country", "initial"
    ]
    
    for column in columns:
        col_lower = column.lower()
        if any(keyword in col_lower for keyword in pii_keywords):
            pii_columns.add(column)
    
    return pii_columns
