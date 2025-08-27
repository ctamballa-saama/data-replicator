"""
Data analysis models for the DataReplicator application.

These models define the structure of statistical analysis results.
"""
from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional, Any, Union, Tuple

from pydantic import BaseModel, Field


class StatType(str, Enum):
    """Types of statistics that can be calculated."""
    
    MEAN = "mean"
    MEDIAN = "median"
    STD_DEV = "std_dev"
    MIN = "min"
    MAX = "max"
    Q1 = "q1"
    Q3 = "q3"
    RANGE = "range"
    COUNT = "count"
    MISSING = "missing"
    FREQUENCY = "frequency"
    PERCENTAGE = "percentage"
    SUM = "sum"
    VARIANCE = "variance"


class NumericStats(BaseModel):
    """Statistics for numeric variables."""
    
    variable_name: str
    data_type: str = "numeric"
    n: int
    n_missing: int = 0
    mean: float
    median: float
    std_dev: float
    min: float
    max: float
    q1: float
    q3: float
    range: float
    variance: Optional[float] = None
    skewness: Optional[float] = None
    kurtosis: Optional[float] = None
    histogram: Optional[List[Tuple[float, int]]] = None  # (bin_edge, count)
    outliers: Optional[List[float]] = None


class CategoricalStats(BaseModel):
    """Statistics for categorical variables."""
    
    variable_name: str
    data_type: str = "categorical"
    n: int
    n_missing: int = 0
    n_unique: int
    frequencies: Dict[str, int]
    percentages: Dict[str, float]
    mode: str
    mode_count: int
    mode_percentage: float


class DateStats(BaseModel):
    """Statistics for date variables."""
    
    variable_name: str
    data_type: str = "date"
    n: int
    n_missing: int = 0
    min_date: str
    max_date: str
    range_days: int
    year_frequencies: Dict[int, int]
    month_frequencies: Dict[int, int]
    weekday_frequencies: Dict[int, int]


class VariableStats(BaseModel):
    """Statistics for a variable, which can be numeric, categorical, or date."""
    
    variable_name: str
    data_type: str
    stats: Union[NumericStats, CategoricalStats, DateStats]


class DomainStats(BaseModel):
    """Statistics for a clinical data domain."""
    
    domain_type: str
    domain_name: str
    record_count: int
    subject_count: int
    variable_count: int
    variables_by_type: Dict[str, List[str]]
    variable_stats: Dict[str, VariableStats]
    correlations: Optional[Dict[str, Dict[str, float]]] = None
    
    class Config:
        """Pydantic configuration."""
        
        arbitrary_types_allowed = True


class AnalysisResult(BaseModel):
    """Result of a statistical analysis."""
    
    analysis_id: str
    analysis_type: str
    timestamp: datetime = Field(default_factory=datetime.now)
    result_data: Any
    metadata: Optional[Dict[str, Any]] = None


class StatsOverview(BaseModel):
    """Overview of statistics across all domains."""
    
    domain_count: int
    total_record_count: int
    total_subject_count: int
    total_variable_count: int
    domains: List[str]
    variables_by_domain: Dict[str, List[str]]
    variables_by_type: Dict[str, List[str]]
    domain_stats: Dict[str, DomainStats]
