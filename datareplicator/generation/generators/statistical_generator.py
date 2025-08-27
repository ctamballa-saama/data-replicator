"""
Statistical data generator implementation.

Generates synthetic data based on statistical distributions from existing data.
"""
import logging
from typing import Dict, List, Optional, Any, Union, Set

import pandas as pd
import numpy as np
from scipy import stats

from datareplicator.generation.generators.base import BaseGenerator
from datareplicator.generation.models.config import (
    GenerationMode, 
    DomainGenerationConfig, 
    VariableGenerationConfig,
    DataDistribution
)
from datareplicator.generation.models.results import (
    DomainGenerationResult,
    GenerationStatus
)


logger = logging.getLogger(__name__)


class StatisticalGenerator(BaseGenerator):
    """
    Generator for creating synthetic data based on statistical distributions.
    
    Uses existing data to fit distributions and generate new data with similar characteristics.
    """
    
    def __init__(self, config: DomainGenerationConfig, source_data: pd.DataFrame = None, seed: Optional[int] = None):
        """
        Initialize the statistical generator.
        
        Args:
            config: Domain generation configuration
            source_data: Source data to use for statistical modeling
            seed: Random seed for reproducibility
        """
        super().__init__(config)
        self.source_data = source_data
        self.seed = seed
        self.fitted_distributions = {}
        
        # Set random seed if provided
        if seed is not None:
            np.random.seed(seed)
    
    def generate(self) -> DomainGenerationResult:
        """
        Generate synthetic data based on statistical distributions.
        
        Returns:
            DomainGenerationResult: Results of the generation process
        """
        try:
            # Update status to in progress
            self.result.status = GenerationStatus.IN_PROGRESS
            
            # Check for source data
            if self.source_data is None or self.source_data.empty:
                self.result.status = GenerationStatus.FAILED
                self.result.error_message = "Source data is required for statistical generation but was not provided"
                return self.result
            
            # First, fit distributions to source data
            self._fit_distributions()
            
            # Initialize data dictionary
            data = {}
            
            # Generate data for each variable
            for variable in self.variables:
                var_name = variable.variable_name
                data[var_name] = self._generate_variable_data(variable)
            
            # Convert to pandas DataFrame
            df = pd.DataFrame(data)
            
            # Finalize and return result
            return self.finalize_result(df)
        
        except Exception as e:
            # Handle any errors
            logger.error(f"Error generating statistical data for domain {self.domain_name}: {str(e)}")
            self.result.status = GenerationStatus.FAILED
            self.result.error_message = str(e)
            return self.result
    
    def _fit_distributions(self) -> None:
        """
        Fit statistical distributions to the source data.
        """
        for variable in self.variables:
            var_name = variable.variable_name
            if var_name in self.source_data.columns:
                data_type = variable.data_type.lower()
                
                if data_type == "numeric":
                    self._fit_numeric_distribution(var_name)
                elif data_type == "categorical":
                    self._fit_categorical_distribution(var_name)
                elif data_type == "date":
                    self._fit_date_distribution(var_name)
    
    def _fit_numeric_distribution(self, var_name: str) -> None:
        """
        Fit a statistical distribution to numeric data.
        
        Args:
            var_name: Variable name
        """
        # Get data, removing missing values
        values = self.source_data[var_name].dropna().values
        
        if len(values) == 0:
            return
        
        # Store basic statistics
        self.fitted_distributions[var_name] = {
            "type": "numeric",
            "mean": np.mean(values),
            "std": np.std(values),
            "min": np.min(values),
            "max": np.max(values),
            "median": np.median(values),
            "q1": np.percentile(values, 25),
            "q3": np.percentile(values, 75),
            "histogram": np.histogram(values, bins=10)
        }
        
        # Try to fit a kernel density estimate for better sampling
        try:
            kde = stats.gaussian_kde(values)
            self.fitted_distributions[var_name]["kde"] = kde
        except Exception as e:
            logger.warning(f"Could not fit KDE for {var_name}: {e}")
    
    def _fit_categorical_distribution(self, var_name: str) -> None:
        """
        Fit a distribution to categorical data.
        
        Args:
            var_name: Variable name
        """
        # Get value counts as probabilities
        value_counts = self.source_data[var_name].value_counts(dropna=True, normalize=True)
        
        self.fitted_distributions[var_name] = {
            "type": "categorical",
            "values": value_counts.index.tolist(),
            "probabilities": value_counts.values.tolist()
        }
    
    def _fit_date_distribution(self, var_name: str) -> None:
        """
        Fit a distribution to date data.
        
        Args:
            var_name: Variable name
        """
        # Convert to datetime and extract components
        try:
            dates = pd.to_datetime(self.source_data[var_name].dropna())
            
            if len(dates) == 0:
                return
            
            # Extract year, month, day distributions
            year_counts = dates.dt.year.value_counts(normalize=True)
            month_counts = dates.dt.month.value_counts(normalize=True)
            day_counts = dates.dt.day.value_counts(normalize=True)
            
            self.fitted_distributions[var_name] = {
                "type": "date",
                "min_date": dates.min().strftime("%Y-%m-%d"),
                "max_date": dates.max().strftime("%Y-%m-%d"),
                "years": year_counts.index.tolist(),
                "year_probs": year_counts.values.tolist(),
                "months": month_counts.index.tolist(),
                "month_probs": month_counts.values.tolist(),
                "days": day_counts.index.tolist(),
                "day_probs": day_counts.values.tolist()
            }
        except Exception as e:
            logger.warning(f"Error fitting date distribution for {var_name}: {e}")
    
    def _generate_variable_data(self, variable: VariableGenerationConfig) -> List[Any]:
        """
        Generate data for a variable based on fitted distributions.
        
        Args:
            variable: Variable configuration
            
        Returns:
            List[Any]: Generated values
        """
        var_name = variable.variable_name
        data_type = variable.data_type.lower()
        constraints = variable.constraints
        
        # If distribution not fitted, fall back to random generation
        if var_name not in self.fitted_distributions:
            logger.warning(f"No fitted distribution for {var_name}, using random generation")
            from datareplicator.generation.generators.random_generator import RandomGenerator
            random_gen = RandomGenerator(self.config, seed=self.seed)
            return random_gen._generate_variable_data(variable, [])
        
        # Generate based on data type
        if data_type == "numeric":
            return self._generate_numeric_from_distribution(var_name, constraints)
        elif data_type == "categorical":
            return self._generate_categorical_from_distribution(var_name, constraints)
        elif data_type == "date":
            return self._generate_date_from_distribution(var_name, constraints)
        else:
            logger.warning(f"Unsupported data type {data_type} for statistical generation")
            # Fall back to random generation
            from datareplicator.generation.generators.random_generator import RandomGenerator
            random_gen = RandomGenerator(self.config, seed=self.seed)
            return random_gen._generate_variable_data(variable, [])
    
    def _generate_numeric_from_distribution(self, var_name: str, constraints=None) -> List[float]:
        """
        Generate numeric data from fitted distribution.
        
        Args:
            var_name: Variable name
            constraints: Optional value constraints
            
        Returns:
            List[float]: Generated values
        """
        dist = self.fitted_distributions[var_name]
        
        # If we have a KDE, use it for sampling
        if "kde" in dist:
            values = dist["kde"].resample(self.record_count)[0]
        else:
            # Otherwise use normal distribution with fitted parameters
            values = np.random.normal(
                loc=dist["mean"],
                scale=dist["std"],
                size=self.record_count
            )
        
        # Apply min/max constraints
        min_val = dist["min"] if constraints is None or constraints.min_value is None else constraints.min_value
        max_val = dist["max"] if constraints is None or constraints.max_value is None else constraints.max_value
        values = np.clip(values, min_val, max_val)
        
        # Apply nullability if specified
        if constraints and constraints.nullable and constraints.null_probability > 0:
            mask = np.random.random(self.record_count) < constraints.null_probability
            values = [None if m else v for v, m in zip(values, mask)]
        else:
            values = values.tolist()
        
        return values
    
    def _generate_categorical_from_distribution(self, var_name: str, constraints=None) -> List[Any]:
        """
        Generate categorical data from fitted distribution.
        
        Args:
            var_name: Variable name
            constraints: Optional value constraints
            
        Returns:
            List[Any]: Generated values
        """
        dist = self.fitted_distributions[var_name]
        values = dist["values"]
        probabilities = dist["probabilities"]
        
        # Apply constraints on allowed values if specified
        if constraints and constraints.allowed_values:
            # Filter to only allowed values and renormalize probabilities
            allowed_indices = [i for i, v in enumerate(values) if v in constraints.allowed_values]
            if allowed_indices:
                values = [values[i] for i in allowed_indices]
                probabilities = [probabilities[i] for i in allowed_indices]
                probabilities = [p / sum(probabilities) for p in probabilities]
        
        # Generate values based on the distribution
        result = np.random.choice(values, size=self.record_count, p=probabilities).tolist()
        
        # Apply nullability if specified
        if constraints and constraints.nullable and constraints.null_probability > 0:
            for i in range(len(result)):
                if np.random.random() < constraints.null_probability:
                    result[i] = None
        
        return result
    
    def _generate_date_from_distribution(self, var_name: str, constraints=None) -> List[str]:
        """
        Generate date data from fitted distribution.
        
        Args:
            var_name: Variable name
            constraints: Optional value constraints
            
        Returns:
            List[str]: Generated date strings
        """
        import datetime as dt
        dist = self.fitted_distributions[var_name]
        
        # Generate dates by sampling year, month, day components
        years = np.random.choice(dist["years"], size=self.record_count, p=dist["year_probs"])
        months = np.random.choice(dist["months"], size=self.record_count, p=dist["month_probs"])
        days = np.random.choice(dist["days"], size=self.record_count, p=dist["day_probs"])
        
        # Create date strings, handling invalid dates
        result = []
        for year, month, day in zip(years, months, days):
            try:
                # Check if the date is valid (e.g., no February 30)
                date = dt.datetime(int(year), int(month), int(day))
                result.append(date.strftime("%Y-%m-%d"))
            except ValueError:
                # If invalid, use a valid day for that month
                try:
                    # Use the last day of the month
                    if month == 2:
                        # Handle February leap years
                        if year % 4 == 0 and (year % 100 != 0 or year % 400 == 0):
                            day = min(day, 29)
                        else:
                            day = min(day, 28)
                    elif month in [4, 6, 9, 11]:
                        day = min(day, 30)
                    else:
                        day = min(day, 31)
                    
                    date = dt.datetime(int(year), int(month), int(day))
                    result.append(date.strftime("%Y-%m-%d"))
                except ValueError:
                    # Fallback to middle of the month
                    date = dt.datetime(int(year), int(month), 15)
                    result.append(date.strftime("%Y-%m-%d"))
        
        # Apply nullability if specified
        if constraints and constraints.nullable and constraints.null_probability > 0:
            for i in range(len(result)):
                if np.random.random() < constraints.null_probability:
                    result[i] = None
        
        return result
