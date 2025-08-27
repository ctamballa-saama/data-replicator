"""
Data export models for DataReplicator.

This module provides models for data export configuration and results.
"""
from enum import Enum
from typing import Dict, List, Optional, Any, Union
from pydantic import BaseModel, Field


class ExportFormat(str, Enum):
    """Supported export formats."""
    CSV = "csv"
    JSON = "json"
    XML = "xml"
    SAS = "sas"
    EXCEL = "excel"


class ExportMetadata(BaseModel):
    """Metadata for exported data."""
    created_at: str = Field(..., description="Timestamp when the export was created")
    creator: Optional[str] = Field(None, description="User who created the export")
    source_domain: str = Field(..., description="Source domain name")
    record_count: int = Field(..., description="Number of records in the export")
    format: ExportFormat = Field(..., description="Format of the export")
    description: Optional[str] = Field(None, description="Description of the export")
    tags: List[str] = Field(default_factory=list, description="Tags for the export")
    generation_parameters: Optional[Dict[str, Any]] = Field(
        None, description="Parameters used to generate the data"
    )


class ExportConfig(BaseModel):
    """Configuration for data export."""
    domain_name: str = Field(..., description="Domain name to export")
    format: ExportFormat = Field(ExportFormat.CSV, description="Export format")
    file_name: Optional[str] = Field(None, description="Output file name")
    include_metadata: bool = Field(True, description="Whether to include metadata in the export")
    filter_query: Optional[str] = Field(None, description="SQL-like query to filter data")
    fields: Optional[List[str]] = Field(None, description="Fields to include in the export")
    column_mappings: Optional[Dict[str, str]] = Field(None, description="Custom column name mappings")
    encoding: str = Field("utf-8", description="File encoding")
    compress: bool = Field(False, description="Whether to compress the output")
    compression_type: Optional[str] = Field(None, description="Type of compression (zip, gzip, etc.)")
    include_header: bool = Field(True, description="Whether to include header row in CSV/Excel")
    date_format: Optional[str] = Field(None, description="Format for date values")
    delimiter: str = Field(",", description="Delimiter for CSV format")
    quotechar: str = Field("\"", description="Quote character for CSV format")
    sheet_name: Optional[str] = Field("Data", description="Sheet name for Excel format")
    decimal: str = Field(".", description="Decimal separator")
    
    class Config:
        """Pydantic config."""
        use_enum_values = True


class ExportResult(BaseModel):
    """Result of a data export operation."""
    success: bool = Field(..., description="Whether the export succeeded")
    file_path: Optional[str] = Field(None, description="Path to the exported file")
    file_size: Optional[int] = Field(None, description="Size of the exported file in bytes")
    record_count: Optional[int] = Field(None, description="Number of records exported")
    format: ExportFormat = Field(..., description="Format of the export")
    domain_name: str = Field(..., description="Domain name that was exported")
    error_message: Optional[str] = Field(None, description="Error message if export failed")
    metadata: Optional[ExportMetadata] = Field(None, description="Metadata for the export")
    
    class Config:
        """Pydantic config."""
        use_enum_values = True
