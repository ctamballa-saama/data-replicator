"""
Base generator class for synthetic data generation.

Provides the abstract interface for all data generators.
"""
import abc
import logging
import time
import uuid
from datetime import datetime
from typing import Dict, List, Optional, Any, Union

import pandas as pd

from datareplicator.generation.models.config import (
    GenerationMode, 
    DomainGenerationConfig, 
    VariableGenerationConfig
)
from datareplicator.generation.models.results import (
    GenerationStatus, 
    DomainGenerationResult,
    VariableGenerationStats,
    DataQualityCheck
)


logger = logging.getLogger(__name__)


class BaseGenerator(abc.ABC):
    """
    Abstract base class for all data generators.
    
    All specific generators should inherit from this class and implement
    the generate method according to their specific generation strategy.
    """
    
    def __init__(self, config: DomainGenerationConfig):
        """
        Initialize the generator with a domain configuration.
        
        Args:
            config: Domain generation configuration
        """
        self.config = config
        self.domain_name = config.domain_name
        self.domain_type = config.domain_type
        self.record_count = config.record_count
        self.subject_count = config.subject_count
        self.mode = config.mode
        self.variables = config.variables
        self.result = self._initialize_result()
    
    def _initialize_result(self) -> DomainGenerationResult:
        """
        Initialize the domain generation result object.
        
        Returns:
            DomainGenerationResult: Initial result object
        """
        result = DomainGenerationResult(
            domain_name=self.domain_name,
            domain_type=self.domain_type,
            config=self.config,
            status=GenerationStatus.PENDING,
            record_count=0,
            subject_count=0,
            start_time=datetime.now()
        )
        
        # Initialize variable stats
        for variable in self.variables:
            result.variable_stats[variable.variable_name] = VariableGenerationStats(
                variable_name=variable.variable_name,
                data_type=variable.data_type,
                generated_count=0
            )
        
        return result
    
    @abc.abstractmethod
    def generate(self) -> DomainGenerationResult:
        """
        Generate synthetic data according to the configuration.
        
        This method must be implemented by all concrete generator classes.
        
        Returns:
            DomainGenerationResult: Results of the generation process
        """
        pass
    
    def update_generation_stats(self, data: pd.DataFrame) -> None:
        """
        Update the generation statistics based on generated data.
        
        Args:
            data: Generated data as a pandas DataFrame
        """
        self.result.record_count = len(data)
        
        # Get subject count if subject ID column exists
        if "USUBJID" in data.columns:
            self.result.subject_count = data["USUBJID"].nunique()
        
        # Update variable stats
        for variable in self.variables:
            var_name = variable.variable_name
            if var_name in data.columns:
                stats = self.result.variable_stats[var_name]
                stats.generated_count = len(data)
                stats.missing_count = data[var_name].isna().sum()
                stats.unique_count = data[var_name].nunique()
                
                # Type-specific stats
                if variable.data_type.lower() == "numeric":
                    if not data[var_name].empty and not all(data[var_name].isna()):
                        stats.min_value = data[var_name].min()
                        stats.max_value = data[var_name].max()
                        stats.distribution_stats = {
                            "mean": data[var_name].mean(),
                            "std": data[var_name].std(),
                            "median": data[var_name].median()
                        }
                elif variable.data_type.lower() == "categorical":
                    if not data[var_name].empty:
                        value_counts = data[var_name].value_counts(normalize=True)
                        stats.distribution_stats = {
                            "top_values": value_counts[:10].to_dict()
                        }
                elif variable.data_type.lower() == "date":
                    if not data[var_name].empty and not all(data[var_name].isna()):
                        try:
                            date_series = pd.to_datetime(data[var_name])
                            stats.min_value = date_series.min().strftime("%Y-%m-%d")
                            stats.max_value = date_series.max().strftime("%Y-%m-%d")
                            stats.distribution_stats = {
                                "year_counts": date_series.dt.year.value_counts().to_dict()
                            }
                        except Exception as e:
                            logger.warning(f"Error calculating date stats for {var_name}: {e}")
    
    def perform_quality_checks(self, data: pd.DataFrame) -> List[DataQualityCheck]:
        """
        Perform data quality checks on the generated data.
        
        Args:
            data: Generated data as a pandas DataFrame
            
        Returns:
            List[DataQualityCheck]: Results of quality checks
        """
        quality_checks = []
        
        # Perform checks for each variable
        for variable in self.variables:
            var_name = variable.variable_name
            if var_name in data.columns:
                var_stats = self.result.variable_stats[var_name]
                
                # Check for missing values
                missing_count = data[var_name].isna().sum()
                if missing_count > 0:
                    # Check if missing values are expected
                    constraints = variable.constraints
                    expected_missing = constraints and constraints.nullable
                    
                    if not expected_missing or missing_count > self.record_count * 0.5:  # Arbitrary threshold of 50%
                        quality_checks.append(
                            DataQualityCheck(
                                check_name=f"{var_name}_missing_values",
                                check_type="missing_values",
                                variable_name=var_name,
                                passed=expected_missing,
                                issue_count=missing_count,
                                description=f"{missing_count} missing values found for {var_name}"
                            )
                        )
                
                # Check for duplicates if uniqueness is required
                constraints = variable.constraints
                if constraints and constraints.unique:
                    duplicate_count = len(data) - data[var_name].nunique()
                    if duplicate_count > 0:
                        quality_checks.append(
                            DataQualityCheck(
                                check_name=f"{var_name}_duplicate_values",
                                check_type="duplicate_values",
                                variable_name=var_name,
                                passed=False,
                                issue_count=duplicate_count,
                                description=f"{duplicate_count} duplicate values found for {var_name} (should be unique)"
                            )
                        )
                
                # Check value ranges for numeric variables
                if variable.data_type.lower() == "numeric" and constraints:
                    if constraints.min_value is not None:
                        below_min = (data[var_name] < constraints.min_value).sum()
                        if below_min > 0:
                            quality_checks.append(
                                DataQualityCheck(
                                    check_name=f"{var_name}_below_minimum",
                                    check_type="out_of_range",
                                    variable_name=var_name,
                                    passed=False,
                                    issue_count=below_min,
                                    description=f"{below_min} values below minimum ({constraints.min_value}) for {var_name}"
                                )
                            )
                    
                    if constraints.max_value is not None:
                        above_max = (data[var_name] > constraints.max_value).sum()
                        if above_max > 0:
                            quality_checks.append(
                                DataQualityCheck(
                                    check_name=f"{var_name}_above_maximum",
                                    check_type="out_of_range",
                                    variable_name=var_name,
                                    passed=False,
                                    issue_count=above_max,
                                    description=f"{above_max} values above maximum ({constraints.max_value}) for {var_name}"
                                )
                            )
        
        return quality_checks
    
    def calculate_quality_score(self, quality_checks: List[DataQualityCheck]) -> float:
        """
        Calculate a quality score based on quality checks.
        
        Args:
            quality_checks: List of quality check results
            
        Returns:
            float: Quality score between 0 and 100
        """
        if not quality_checks:
            return 100.0  # Perfect score if no issues
        
        # Start with perfect score and subtract for issues
        score = 100.0
        
        # Calculate total records for percentage calculations
        total_records = self.result.record_count
        if total_records == 0:
            return 0.0  # No data generated
        
        for check in quality_checks:
            if not check.passed:
                # Calculate impact based on issue count
                impact = check.issue_count / total_records
                
                # Different penalties based on issue type
                if check.check_type == "missing_values":
                    score -= 20 * impact
                elif check.check_type == "duplicate_values":
                    score -= 15 * impact
                elif check.check_type == "out_of_range":
                    score -= 10 * impact
                elif check.check_type == "invalid_format":
                    score -= 5 * impact
                else:
                    score -= 5 * impact
        
        # Ensure score is between 0 and 100
        return max(0.0, min(100.0, score))
    
    def finalize_result(self, data: pd.DataFrame, output_file: Optional[str] = None) -> DomainGenerationResult:
        """
        Finalize the generation result by updating stats and performing quality checks.
        
        Args:
            data: Generated data as a pandas DataFrame
            output_file: Path to the output file if data was saved
            
        Returns:
            DomainGenerationResult: Final result object
        """
        end_time = datetime.now()
        
        # Update basic stats
        self.update_generation_stats(data)
        
        # Perform quality checks
        quality_checks = self.perform_quality_checks(data)
        
        # Update variable stats with quality checks
        for check in quality_checks:
            if check.variable_name and check.variable_name in self.result.variable_stats:
                self.result.variable_stats[check.variable_name].quality_checks.append(check)
        
        # Calculate quality score
        quality_score = self.calculate_quality_score(quality_checks)
        
        # Update result object
        self.result.status = GenerationStatus.COMPLETED
        self.result.end_time = end_time
        self.result.duration_seconds = (end_time - self.result.start_time).total_seconds()
        self.result.quality_score = quality_score
        
        if output_file:
            self.result.output_file = output_file
        
        return self.result
