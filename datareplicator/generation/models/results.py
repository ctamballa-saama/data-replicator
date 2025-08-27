"""
Data generation result models.

These models define the structure of generation outputs and related metadata.
"""
from enum import Enum
from typing import Dict, List, Optional, Any, Union
from pathlib import Path
from datetime import datetime

from pydantic import BaseModel, Field

from datareplicator.generation.models.config import GenerationMode, DomainGenerationConfig


class GenerationStatus(str, Enum):
    """Status of a data generation task."""
    
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class DataQualityIssue(str, Enum):
    """Types of data quality issues that can be detected."""
    
    MISSING_VALUES = "missing_values"
    DUPLICATE_VALUES = "duplicate_values"
    OUT_OF_RANGE = "out_of_range"
    INVALID_FORMAT = "invalid_format"
    RELATIONSHIP_VIOLATION = "relationship_violation"
    DISTRIBUTION_DEVIATION = "distribution_deviation"
    PATTERN_VIOLATION = "pattern_violation"
    CUSTOM = "custom"


class DataQualityCheck(BaseModel):
    """Results of a data quality check on generated data."""
    
    check_name: str
    check_type: DataQualityIssue
    variable_name: Optional[str] = None
    passed: bool
    issue_count: int = 0
    description: str
    details: Optional[Dict[str, Any]] = None


class VariableGenerationStats(BaseModel):
    """Statistics about generated variable data."""
    
    variable_name: str
    data_type: str
    generated_count: int
    missing_count: int = 0
    unique_count: Optional[int] = None
    min_value: Optional[Any] = None
    max_value: Optional[Any] = None
    distribution_stats: Optional[Dict[str, Any]] = None
    quality_checks: List[DataQualityCheck] = Field(default_factory=list)
    metadata: Optional[Dict[str, Any]] = None


class DomainGenerationResult(BaseModel):
    """Results of generating a single domain."""
    
    domain_name: str
    domain_type: str
    config: DomainGenerationConfig
    status: GenerationStatus
    record_count: int
    subject_count: int
    start_time: datetime
    end_time: Optional[datetime] = None
    duration_seconds: Optional[float] = None
    output_file: Optional[Path] = None
    variable_stats: Dict[str, VariableGenerationStats] = Field(default_factory=dict)
    error_message: Optional[str] = None
    warnings: List[str] = Field(default_factory=list)
    quality_score: Optional[float] = None  # 0-100 score based on quality checks
    metadata: Optional[Dict[str, Any]] = None


class GenerationJobResult(BaseModel):
    """Results of a data generation job with tracking capabilities."""
    
    job_id: str
    project_name: str
    status: GenerationStatus
    start_time: datetime
    end_time: Optional[datetime] = None
    duration_seconds: Optional[float] = None
    domain_results: Dict[str, DomainGenerationResult] = Field(default_factory=dict)
    total_records: int = 0
    total_subjects: int = 0
    output_directory: Optional[Path] = None
    error_message: Optional[str] = None
    warnings: List[str] = Field(default_factory=list)
    overall_quality_score: Optional[float] = None
    metadata: Optional[Dict[str, Any]] = None
    
    def add_domain_result(self, domain_result: DomainGenerationResult):
        """Add a domain generation result to the overall results."""
        self.domain_results[domain_result.domain_name] = domain_result
        self.total_records += domain_result.record_count
        self.total_subjects = max(self.total_subjects, domain_result.subject_count)
        
        # Update status based on domain result
        if domain_result.status == GenerationStatus.FAILED and self.status != GenerationStatus.FAILED:
            self.status = GenerationStatus.FAILED
            self.error_message = f"Failed to generate {domain_result.domain_name}: {domain_result.error_message}"
            
        # Add any warnings from the domain result
        self.warnings.extend(domain_result.warnings)
        
    def calculate_quality_score(self) -> float:
        """Calculate the overall quality score based on domain quality scores."""
        if not self.domain_results:
            return 0.0
            
        valid_scores = []
        for domain_result in self.domain_results.values():
            if domain_result.quality_score is not None:
                valid_scores.append(domain_result.quality_score)
                
        if not valid_scores:
            return 0.0
            
        self.overall_quality_score = sum(valid_scores) / len(valid_scores)
        return self.overall_quality_score


class GenerationResult(BaseModel):
    """Overall results of a data generation job."""
    
    job_id: str
    project_name: str
    status: GenerationStatus
    start_time: datetime
    end_time: Optional[datetime] = None
    duration_seconds: Optional[float] = None
    domain_results: Dict[str, DomainGenerationResult] = Field(default_factory=dict)
    total_records: int = 0
    total_subjects: int = 0
    output_directory: Optional[Path] = None
    error_message: Optional[str] = None
    warnings: List[str] = Field(default_factory=list)
    overall_quality_score: Optional[float] = None
    metadata: Optional[Dict[str, Any]] = None
    
    def add_domain_result(self, domain_result: DomainGenerationResult) -> None:
        """
        Add a domain generation result to the overall results.
        
        Args:
            domain_result: The domain generation result to add
        """
        self.domain_results[domain_result.domain_name] = domain_result
        self.total_records += domain_result.record_count
        self.total_subjects += domain_result.subject_count
        
        # Update status based on domain results
        if domain_result.status == GenerationStatus.FAILED:
            self.status = GenerationStatus.FAILED
        elif self.status != GenerationStatus.FAILED:
            # Only set to COMPLETED if all domains are completed
            if all(dr.status == GenerationStatus.COMPLETED for dr in self.domain_results.values()):
                self.status = GenerationStatus.COMPLETED
            else:
                self.status = GenerationStatus.IN_PROGRESS
    
    def calculate_quality_score(self) -> float:
        """
        Calculate the overall quality score based on domain quality scores.
        
        Returns:
            float: Overall quality score (0-100)
        """
        if not self.domain_results:
            return 0.0
        
        # Average of domain quality scores
        domain_scores = [dr.quality_score for dr in self.domain_results.values() 
                        if dr.quality_score is not None]
        
        if not domain_scores:
            return 0.0
        
        self.overall_quality_score = sum(domain_scores) / len(domain_scores)
        return self.overall_quality_score
