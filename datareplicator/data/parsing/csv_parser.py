"""
CSV Parser for clinical data files.

Handles parsing, validation, and processing of CSV files for clinical domains.
"""
import csv
import logging
from pathlib import Path
from typing import Dict, List, Optional, Any, Set, Tuple

import pandas as pd

from datareplicator.core.config import settings, constants, DomainType
from datareplicator.data.models import DomainData, DataColumn, ParseError, DataImportSummary


logger = logging.getLogger(__name__)


class CSVParser:
    """
    Parser for clinical data CSV files.
    
    Handles reading, validation, and processing of CSV files.
    """
    
    def __init__(self):
        """Initialize the CSV parser."""
        self.encoding = constants.DEFAULT_ENCODING
        self.delimiter = constants.DEFAULT_CSV_DELIMITER
    
    def detect_domain(self, file_path: Path) -> Optional[DomainType]:
        """
        Detect the clinical domain of a CSV file based on its content.
        
        Args:
            file_path: Path to the CSV file
            
        Returns:
            DomainType or None if domain cannot be detected
        """
        try:
            # Read just the header and a few rows to detect the domain
            df = pd.read_csv(
                file_path, 
                encoding=self.encoding,
                delimiter=self.delimiter,
                nrows=5
            )
            
            # Check if DOMAIN column exists and use its value
            if "DOMAIN" in df.columns and not df["DOMAIN"].empty:
                domain_code = df["DOMAIN"].iloc[0]
                try:
                    return DomainType(domain_code)
                except ValueError:
                    logger.warning(f"Unknown domain code: {domain_code}")
                    return None
                
            # Try to infer domain from filename
            filename = file_path.stem.lower()
            for domain_type in DomainType:
                if domain_type.value.lower() == filename:
                    return domain_type
                
            # Try to infer from column names
            columns = set(df.columns)
            # Check domain-specific required variables
            domain_matches = []
            for domain, required_vars in constants.REQUIRED_VARS.items():
                if all(var in columns for var in required_vars):
                    domain_matches.append(domain)
            
            if len(domain_matches) == 1:
                return DomainType(domain_matches[0])
            elif len(domain_matches) > 1:
                logger.warning(f"Multiple domain matches for {file_path}: {domain_matches}")
                
            return None
            
        except Exception as e:
            logger.error(f"Error detecting domain for {file_path}: {e}")
            return None
    
    def parse_file(self, file_path: Path) -> DataImportSummary:
        """
        Parse a CSV file and return a domain data object.
        
        Args:
            file_path: Path to the CSV file
            
        Returns:
            DataImportSummary: Summary of the import results
        """
        if not file_path.exists():
            error = ParseError(
                file_path=file_path,
                error_message=f"File not found: {file_path}",
                error_type="FileNotFoundError"
            )
            return DataImportSummary(
                file_path=file_path,
                success=False,
                errors=[error],
                error_count=1
            )
        
        try:
            # First, detect the domain
            domain_type = self.detect_domain(file_path)
            
            # Read the CSV file
            df = pd.read_csv(
                file_path, 
                encoding=self.encoding,
                delimiter=self.delimiter
            )
            
            # Check for empty DataFrame
            if df.empty:
                error = ParseError(
                    file_path=file_path,
                    error_message="File is empty or contains only headers",
                    error_type="EmptyFileError"
                )
                return DataImportSummary(
                    file_path=file_path,
                    domain_type=domain_type,
                    success=False,
                    errors=[error],
                    error_count=1
                )
            
            # Create domain data object
            domain_data = DomainData(
                domain_type=domain_type if domain_type else "Unknown",
                domain_name=domain_type.value if domain_type else "Unknown",
                file_path=file_path,
                columns=list(df.columns),
                data=df.to_dict('records'),
                errors=[]
            )
            
            # Validate domain data
            errors = self._validate_domain_data(domain_data)
            
            # Count unique subjects
            subject_count = 0
            if constants.USUBJID_VAR in df.columns:
                subject_count = df[constants.USUBJID_VAR].nunique()
            
            # Create summary
            summary = DataImportSummary(
                file_path=file_path,
                domain_type=domain_type,
                domain_name=domain_type.value if domain_type else "Unknown",
                row_count=len(df),
                column_count=len(df.columns),
                error_count=len(errors),
                subject_count=subject_count,
                success=len(errors) == 0,
                errors=errors
            )
            
            return summary
            
        except pd.errors.ParserError as e:
            error = ParseError(
                file_path=file_path,
                error_message=f"CSV parsing error: {str(e)}",
                error_type="ParserError"
            )
            return DataImportSummary(
                file_path=file_path,
                success=False,
                errors=[error],
                error_count=1
            )
        except Exception as e:
            error = ParseError(
                file_path=file_path,
                error_message=f"Unexpected error: {str(e)}",
                error_type=type(e).__name__
            )
            return DataImportSummary(
                file_path=file_path,
                success=False,
                errors=[error],
                error_count=1
            )
    
    def _validate_domain_data(self, domain_data: DomainData) -> List[ParseError]:
        """
        Validate domain data for consistency and required fields.
        
        Args:
            domain_data: The domain data to validate
            
        Returns:
            List of parse errors found during validation
        """
        errors = []
        
        # Skip validation if domain is unknown
        if domain_data.domain_type == "Unknown":
            return errors
        
        # Check for required variables
        if domain_data.domain_type.value in constants.REQUIRED_VARS:
            required_vars = constants.REQUIRED_VARS[domain_data.domain_type.value]
            for var in required_vars:
                if var not in domain_data.columns:
                    errors.append(ParseError(
                        file_path=domain_data.file_path,
                        error_message=f"Required variable {var} missing for domain {domain_data.domain_type.value}",
                        error_type="MissingRequiredVariable"
                    ))
        
        # Validate USUBJID format if present
        if constants.USUBJID_VAR in domain_data.columns:
            # Check for duplicate USUBJIDs where that shouldn't be allowed
            if domain_data.domain_type == DomainType.DEMOGRAPHICS:
                # Get all USUBJIDs
                usubjids = [row.get(constants.USUBJID_VAR) for row in domain_data.data]
                # Find duplicates
                seen = set()
                duplicates = {x for x in usubjids if x in seen or seen.add(x)}
                
                # Add errors for each duplicate
                for duplicate in duplicates:
                    errors.append(ParseError(
                        file_path=domain_data.file_path,
                        error_message=f"Duplicate USUBJID found: {duplicate}",
                        error_type="DuplicateUSUBJID"
                    ))
        
        return errors
