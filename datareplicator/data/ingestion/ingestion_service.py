"""
Data ingestion service implementation.

Provides a unified service for ingesting and processing clinical data files.
"""
import logging
import os
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple, Union, Any

from datareplicator.core.config import DomainType, settings
from datareplicator.data.models import DataImportSummary, DomainData
from datareplicator.data.parsing import CSVParser
from datareplicator.data.domain import domain_registry, domain_factory


logger = logging.getLogger(__name__)


class DataIngestionService:
    """
    Service for ingesting and processing clinical data files.
    
    Integrates file parsing and domain management components.
    """
    
    def __init__(self):
        """Initialize the data ingestion service."""
        self.csv_parser = CSVParser()
        self.domain_registry = domain_registry
        self.domain_factory = domain_factory
        self.imported_data: Dict[DomainType, DomainData] = {}
    
    def ingest_file(self, file_path: Union[str, Path]) -> DataImportSummary:
        """
        Ingest a single data file.
        
        Args:
            file_path: Path to the data file to ingest
            
        Returns:
            DataImportSummary: Summary of the import operation
        """
        # Convert string path to Path if needed
        if isinstance(file_path, str):
            file_path = Path(file_path)
        
        # Check if file exists
        if not file_path.exists():
            logger.error(f"File not found: {file_path}")
            summary = DataImportSummary(
                success=False,
                file_path=file_path,
                domain_type="Unknown",
                error_count=1,
                errors=[{
                    "error_type": "FileNotFoundError",
                    "message": f"File not found: {file_path}"
                }]
            )
            return summary
        
        # Parse the file
        summary = self.csv_parser.parse_file(file_path)
        
        # If parsing was successful, process the domain data
        if summary.success and summary.domain_data:
            # Get the appropriate domain for validation
            domain = self.domain_factory.create_domain_for_data(summary.domain_data)
            
            if domain:
                # Validate the data with domain-specific rules
                validation_errors = domain.validate_data(summary.domain_data)
                
                if validation_errors:
                    summary.errors.extend(validation_errors)
                    summary.error_count += len(validation_errors)
                    
                    # Set success to False if there are validation errors
                    if summary.error_count > 0:
                        summary.success = False
                
                # Store the imported data if it's valid
                if summary.success:
                    self.imported_data[domain.domain_type] = summary.domain_data
            else:
                logger.warning(f"No domain found for {summary.domain_type}")
        
        return summary
    
    def ingest_directory(self, directory_path: Union[str, Path]) -> Dict[str, DataImportSummary]:
        """
        Ingest all supported data files in a directory.
        
        Args:
            directory_path: Path to the directory containing data files
            
        Returns:
            Dict mapping filenames to import summaries
        """
        # Convert string path to Path if needed
        if isinstance(directory_path, str):
            directory_path = Path(directory_path)
        
        # Check if directory exists
        if not directory_path.exists() or not directory_path.is_dir():
            logger.error(f"Directory not found or not a directory: {directory_path}")
            return {}
        
        # Process all CSV files in the directory
        results = {}
        for file_path in directory_path.glob("*.csv"):
            summary = self.ingest_file(file_path)
            results[file_path.name] = summary
        
        return results
    
    def get_imported_domains(self) -> List[str]:
        """
        Get a list of all imported domain types.
        
        Returns:
            List of domain type names
        """
        return [domain_type.value for domain_type in self.imported_data.keys()]
    
    def get_domain_data(self, domain_type: DomainType) -> Optional[DomainData]:
        """
        Get the imported data for a specific domain.
        
        Args:
            domain_type: Domain type to get data for
            
        Returns:
            DomainData or None if the domain hasn't been imported
        """
        return self.imported_data.get(domain_type)
    
    def clear_imported_data(self):
        """Clear all imported data."""
        self.imported_data.clear()
        logger.info("Cleared all imported data")
    
    def get_subject_ids(self) -> Set[str]:
        """
        Get all unique subject IDs across all imported domains.
        
        Returns:
            Set of unique subject IDs
        """
        subject_ids = set()
        
        for domain_data in self.imported_data.values():
            # Check if the domain data has USUBJID column
            if "USUBJID" in domain_data.columns:
                # Extract all unique subject IDs from the data
                for record in domain_data.data:
                    if "USUBJID" in record and record["USUBJID"]:
                        subject_ids.add(record["USUBJID"])
        
        return subject_ids
    
    def get_data_overview(self) -> Dict[str, Any]:
        """
        Get an overview of all imported data.
        
        Returns:
            Dictionary with data overview statistics
        """
        if not self.imported_data:
            return {"status": "No data imported"}
        
        # Get basic statistics
        overview = {
            "domain_count": len(self.imported_data),
            "domains": self.get_imported_domains(),
            "subject_count": len(self.get_subject_ids()),
            "total_records": sum(len(data.data) for data in self.imported_data.values()),
            "domain_details": {}
        }
        
        # Add domain-specific details
        for domain_type, domain_data in self.imported_data.items():
            overview["domain_details"][domain_type.value] = {
                "record_count": len(domain_data.data),
                "column_count": len(domain_data.columns),
                "columns": domain_data.columns
            }
        
        # Detect relationships between domains
        overview["relationships"] = self.domain_registry.detect_relationships(self.imported_data)
        
        return overview


# Create a singleton instance of the data ingestion service
ingestion_service = DataIngestionService()
