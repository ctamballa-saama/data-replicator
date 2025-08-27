"""
Data models for the DataReplicator application.

These models represent the structure of clinical data used throughout the application.
"""
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional, Any, Union, Set

from pydantic import BaseModel, Field, validator

from datareplicator.core.config.constants import DomainType


class DataColumn(BaseModel):
    """
    Represents a column in a clinical data domain.
    
    Contains metadata about the column's properties and constraints.
    """
    name: str
    data_type: str = "string"
    description: Optional[str] = None
    required: bool = False
    unique: bool = False
    min_value: Optional[float] = None
    max_value: Optional[float] = None
    allowed_values: Optional[List[str]] = None
    is_pii: bool = False
    
    class Config:
        """Pydantic configuration for DataColumn."""
        frozen = True  # Make instances immutable


class ParseError(BaseModel):
    """
    Represents an error that occurred during parsing.
    """
    file_path: Path
    line_number: Optional[int] = None
    column_name: Optional[str] = None
    error_message: str
    error_type: str = "ParseError"


class DomainData(BaseModel):
    """
    Represents the parsed data for a single clinical domain.
    
    Contains both the raw data and metadata about the structure.
    """
    domain_type: DomainType
    domain_name: str
    file_path: Path
    columns: List[str]
    data: List[Dict[str, Any]]
    column_metadata: Dict[str, DataColumn] = Field(default_factory=dict)
    errors: List[ParseError] = Field(default_factory=list)
    row_count: int = 0
    
    class Config:
        """Pydantic configuration for DomainData."""
        arbitrary_types_allowed = True
    
    @validator("row_count", always=True)
    def set_row_count(cls, v: int, values: Dict[str, Any]) -> int:
        """Calculate row count from data."""
        if "data" in values:
            return len(values["data"])
        return v


class DataImportSummary(BaseModel):
    """
    Summarizes the results of a data import operation.
    """
    file_path: Path
    domain_type: Optional[DomainType] = None
    domain_name: Optional[str] = None
    row_count: int = 0
    column_count: int = 0
    error_count: int = 0
    subject_count: int = 0
    success: bool = True
    errors: List[ParseError] = Field(default_factory=list)
    
    class Config:
        """Pydantic configuration for DataImportSummary."""
        arbitrary_types_allowed = True
