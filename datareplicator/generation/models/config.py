"""
Data generation configuration models.

These models define the configuration parameters for synthetic data generation.
"""
from enum import Enum
from typing import Dict, List, Optional, Any, Union
from pathlib import Path
from datetime import datetime, date

from pydantic import BaseModel, Field, validator


class GenerationMode(str, Enum):
    """Modes for generating synthetic data."""
    
    RANDOM = "random"         # Generate completely random data
    STATISTICAL = "statistical"   # Generate data based on statistical distributions
    COPY = "copy"             # Copy data from source with modifications
    RELATIONAL = "relational"  # Generate data maintaining relationships
    DERIVED = "derived"       # Generate data derived from existing data


class DataDistribution(str, Enum):
    """Types of statistical distributions for data generation."""
    
    NORMAL = "normal"
    UNIFORM = "uniform"
    BINOMIAL = "binomial"
    EXPONENTIAL = "exponential"
    POISSON = "poisson"
    CATEGORICAL = "categorical"
    CUSTOM = "custom"


class ValueConstraint(BaseModel):
    """Constraints for generated values."""
    
    min_value: Optional[Union[int, float, str, date]] = None
    max_value: Optional[Union[int, float, str, date]] = None
    allowed_values: Optional[List[Any]] = None
    format_pattern: Optional[str] = None
    unique: bool = False
    nullable: bool = False
    null_probability: float = 0.0  # Probability of generating NULL values if nullable=True
    
    @validator('null_probability')
    def validate_null_probability(cls, v):
        """Validate null probability is between 0 and 1."""
        if v < 0 or v > 1:
            raise ValueError("null_probability must be between 0 and 1")
        return v


class VariableGenerationConfig(BaseModel):
    """Configuration for generating a single variable (column)."""
    
    variable_name: str
    data_type: str  # numeric, categorical, date, text
    distribution: Optional[DataDistribution] = None
    distribution_params: Optional[Dict[str, Any]] = None
    constraints: Optional[ValueConstraint] = None
    source_variable: Optional[str] = None  # For copying or deriving values
    transform_expression: Optional[str] = None  # For transforming source values
    description: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


class DomainGenerationConfig(BaseModel):
    """Configuration for generating a domain (dataset)."""
    
    domain_name: str
    domain_type: str
    record_count: int
    subject_count: int
    mode: GenerationMode = GenerationMode.RANDOM
    variables: List[VariableGenerationConfig]
    source_domain: Optional[str] = None  # For copying or deriving data
    relationships: Optional[List[str]] = None  # References to other domains
    retention_policy: Optional[Dict[str, Any]] = None
    description: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


class GenerationConfig(BaseModel):
    """Overall configuration for data generation."""
    
    project_name: str
    description: Optional[str] = None
    domains: List[DomainGenerationConfig]
    output_directory: Optional[Path] = None
    seed: Optional[int] = None  # For reproducibility
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    version: str = "1.0"
    metadata: Optional[Dict[str, Any]] = None
