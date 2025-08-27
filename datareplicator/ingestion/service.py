"""
Service for handling data ingestion operations.
"""
import os
import pandas as pd
import uuid
from typing import Dict, List, Any, Optional
from fastapi import UploadFile

from datareplicator.config.settings import settings


class IngestionService:
    """Service for ingesting data from CSV files."""
    
    def __init__(self):
        """Initialize the ingestion service."""
        self.upload_dir = settings.UPLOAD_DIR
        # Create upload directory if it doesn't exist
        os.makedirs(self.upload_dir, exist_ok=True)
    
    async def ingest_file(self, file: UploadFile, domain_name: Optional[str] = None) -> Dict[str, Any]:
        """
        Process an uploaded CSV file and extract its data.
        
        Args:
            file: The uploaded CSV file
            domain_name: Optional name for the domain, if not provided, the filename will be used
            
        Returns:
            Dict with ingestion details
        """
        # Generate unique filename if domain name not provided
        if not domain_name:
            domain_name = file.filename.split('.')[0] if file.filename else f"domain_{uuid.uuid4().hex[:8]}"
            
        # Save file temporarily
        file_path = os.path.join(self.upload_dir, f"{domain_name}_{uuid.uuid4().hex}.csv")
        with open(file_path, 'wb') as f:
            content = await file.read()
            f.write(content)
            
        # Parse the CSV file
        try:
            df = pd.read_csv(file_path)
            record_count = len(df)
            variable_count = len(df.columns)
            variables = list(df.columns)
            
            # Get sample data (first 5 rows)
            sample_data = df.head(5).to_dict('records')
            
            # Pass to domain registry
            from datareplicator.domain_registry.service import domain_registry
            domain_registry.register_domain(
                domain_name=domain_name,
                file_path=file_path,
                record_count=record_count,
                variable_count=variable_count,
                variables=variables,
                sample_data=sample_data
            )
            
            return {
                "success": True,
                "domain_name": domain_name,
                "record_count": record_count,
                "variable_count": variable_count,
                "variables": variables
            }
            
        except Exception as e:
            # Clean up the file in case of error
            if os.path.exists(file_path):
                os.remove(file_path)
            return {
                "success": False,
                "error": str(e)
            }


# Create singleton instance
ingestion_service = IngestionService()
