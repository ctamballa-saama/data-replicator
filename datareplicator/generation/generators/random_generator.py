"""
Random data generator implementation.

Generates synthetic data with random values based on specified constraints.
"""
import logging
import random
from datetime import datetime, timedelta
import uuid
from typing import Dict, List, Optional, Any, Union, Set

import pandas as pd
import numpy as np

from datareplicator.generation.generators.base import BaseGenerator
from datareplicator.generation.models.config import (
    GenerationMode, 
    DomainGenerationConfig, 
    VariableGenerationConfig,
    DataDistribution,
    ValueConstraint
)
from datareplicator.generation.models.results import (
    DomainGenerationResult,
    GenerationStatus
)


logger = logging.getLogger(__name__)


class RandomGenerator(BaseGenerator):
    """
    Generator for creating synthetic data with random values.
    
    Generates data according to specified constraints and distributions.
    """
    
    def __init__(self, config: DomainGenerationConfig, seed: Optional[int] = None):
        """
        Initialize the random generator.
        
        Args:
            config: Domain generation configuration
            seed: Random seed for reproducibility
        """
        super().__init__(config)
        self.seed = seed
        
        # Set random seed if provided
        if seed is not None:
            random.seed(seed)
            np.random.seed(seed)
    
    def generate(self) -> DomainGenerationResult:
        """
        Generate synthetic data using random values.
        
        Returns:
            DomainGenerationResult: Results of the generation process
        """
        try:
            # Update status to in progress
            self.result.status = GenerationStatus.IN_PROGRESS
            
            # Initialize empty dataframe for results
            data = {}
            
            # First, generate subject IDs if needed
            subject_ids = self._generate_subject_ids()
            
            # Generate data for each variable
            for variable in self.variables:
                var_name = variable.variable_name
                data[var_name] = self._generate_variable_data(variable, subject_ids)
            
            # Convert to pandas DataFrame
            df = pd.DataFrame(data)
            
            # Finalize and return result
            return self.finalize_result(df)
        
        except Exception as e:
            # Handle any errors
            logger.error(f"Error generating data for domain {self.domain_name}: {str(e)}")
            self.result.status = GenerationStatus.FAILED
            self.result.error_message = str(e)
            return self.result
    
    def _generate_subject_ids(self) -> List[str]:
        """
        Generate subject IDs for the dataset.
        
        Returns:
            List[str]: List of unique subject IDs
        """
        # Check if we need subject IDs (if USUBJID is defined in variables)
        needs_subjects = any(var.variable_name == "USUBJID" for var in self.variables)
        
        if not needs_subjects:
            return []
        
        # Generate the requested number of subject IDs
        subject_count = self.subject_count
        prefix = "SUBJ"
        
        subject_ids = [f"{prefix}{str(i+1).zfill(6)}" for i in range(subject_count)]
        return subject_ids
    
    def _generate_variable_data(self, variable: VariableGenerationConfig, subject_ids: List[str]) -> List[Any]:
        """
        Generate data for a specific variable.
        
        Args:
            variable: Variable generation configuration
            subject_ids: List of subject IDs (used for USUBJID variable)
            
        Returns:
            List[Any]: Generated values for the variable
        """
        var_name = variable.variable_name
        data_type = variable.data_type.lower()
        constraints = variable.constraints
        
        # Special handling for subject ID
        if var_name == "USUBJID" and subject_ids:
            # Repeat subject IDs as needed
            records_per_subject = max(1, self.record_count // len(subject_ids))
            remaining = self.record_count % len(subject_ids)
            
            values = []
            for subject_id in subject_ids:
                values.extend([subject_id] * records_per_subject)
            
            # Add remaining records for some subjects
            if remaining > 0:
                values.extend(subject_ids[:remaining])
            
            return values
        
        # Generate appropriate data based on type
        if data_type == "numeric":
            return self._generate_numeric_data(variable)
        elif data_type == "categorical":
            return self._generate_categorical_data(variable)
        elif data_type == "date":
            return self._generate_date_data(variable)
        elif data_type == "text":
            return self._generate_text_data(variable)
        else:
            # Default to text data for unknown types
            logger.warning(f"Unknown data type '{data_type}' for variable {var_name}, using text generator")
            return self._generate_text_data(variable)
    
    def _generate_numeric_data(self, variable: VariableGenerationConfig) -> List[Union[int, float, None]]:
        """
        Generate numeric data based on configuration.
        
        Args:
            variable: Variable configuration
            
        Returns:
            List[Union[int, float, None]]: List of numeric values
        """
        distribution = variable.distribution or DataDistribution.NORMAL
        constraints = variable.constraints or ValueConstraint()
        params = variable.distribution_params or {}
        
        # Set default min/max if not provided
        min_value = constraints.min_value if constraints.min_value is not None else 0.0
        max_value = constraints.max_value if constraints.max_value is not None else 100.0
        
        # Generate values based on distribution
        if distribution == DataDistribution.NORMAL:
            # Default parameters if not provided
            mean = params.get("mean", (min_value + max_value) / 2)
            std = params.get("std", (max_value - min_value) / 6)  # ~99.7% of values within range
            
            values = np.random.normal(mean, std, self.record_count)
            
            # Clip values to the constraints
            values = np.clip(values, min_value, max_value)
            
        elif distribution == DataDistribution.UNIFORM:
            values = np.random.uniform(min_value, max_value, self.record_count)
            
        elif distribution == DataDistribution.POISSON:
            lam = params.get("lambda", 5.0)
            values = np.random.poisson(lam, self.record_count)
            
        elif distribution == DataDistribution.EXPONENTIAL:
            scale = params.get("scale", 1.0)
            values = np.random.exponential(scale, self.record_count)
            
        elif distribution == DataDistribution.BINOMIAL:
            n = params.get("n", 10)
            p = params.get("p", 0.5)
            values = np.random.binomial(n, p, self.record_count)
            
        else:
            # Default to uniform distribution
            values = np.random.uniform(min_value, max_value, self.record_count)
        
        # Convert to list and apply constraints
        result = values.tolist()
        
        # Round to integers if needed (check if all min/max are integers)
        if (isinstance(min_value, int) and isinstance(max_value, int) and 
            params.get("integer", False)):
            result = [int(x) for x in result]
        
        # Apply null values if allowed
        if constraints.nullable and constraints.null_probability > 0:
            for i in range(len(result)):
                if random.random() < constraints.null_probability:
                    result[i] = None
        
        return result
    
    def _generate_categorical_data(self, variable: VariableGenerationConfig) -> List[Optional[str]]:
        """
        Generate categorical data based on configuration.
        
        Args:
            variable: Variable configuration
            
        Returns:
            List[Optional[str]]: List of categorical values
        """
        constraints = variable.constraints or ValueConstraint()
        params = variable.distribution_params or {}
        
        # Determine allowed values
        allowed_values = constraints.allowed_values
        
        if not allowed_values:
            # Default categories if none provided
            allowed_values = ["Category A", "Category B", "Category C", "Category D"]
        
        # Get probabilities if provided, otherwise use equal probabilities
        probabilities = params.get("probabilities", None)
        
        if probabilities and len(probabilities) == len(allowed_values):
            # Ensure probabilities sum to 1
            total = sum(probabilities)
            if total != 1.0:
                probabilities = [p / total for p in probabilities]
        else:
            # Equal probability for each value
            probabilities = [1.0 / len(allowed_values)] * len(allowed_values)
        
        # Generate values
        result = np.random.choice(allowed_values, size=self.record_count, p=probabilities).tolist()
        
        # Apply null values if allowed
        if constraints.nullable and constraints.null_probability > 0:
            for i in range(len(result)):
                if random.random() < constraints.null_probability:
                    result[i] = None
        
        return result
    
    def _generate_date_data(self, variable: VariableGenerationConfig) -> List[Optional[str]]:
        """
        Generate date data based on configuration.
        
        Args:
            variable: Variable configuration
            
        Returns:
            List[Optional[str]]: List of date values as strings
        """
        constraints = variable.constraints or ValueConstraint()
        params = variable.distribution_params or {}
        
        # Default date range if not provided
        default_start = datetime(2020, 1, 1)
        default_end = datetime(2023, 12, 31)
        
        # Parse min/max dates from constraints
        min_date = constraints.min_value
        max_date = constraints.max_value
        
        if isinstance(min_date, str):
            try:
                min_date = datetime.strptime(min_date, "%Y-%m-%d")
            except ValueError:
                min_date = default_start
        elif not isinstance(min_date, datetime):
            min_date = default_start
        
        if isinstance(max_date, str):
            try:
                max_date = datetime.strptime(max_date, "%Y-%m-%d")
            except ValueError:
                max_date = default_end
        elif not isinstance(max_date, datetime):
            max_date = default_end
        
        # Calculate range in days
        date_range = (max_date - min_date).days
        
        # Generate random dates
        result = []
        for _ in range(self.record_count):
            random_days = random.randint(0, date_range)
            date_value = min_date + timedelta(days=random_days)
            result.append(date_value.strftime("%Y-%m-%d"))
        
        # Apply null values if allowed
        if constraints.nullable and constraints.null_probability > 0:
            for i in range(len(result)):
                if random.random() < constraints.null_probability:
                    result[i] = None
        
        return result
    
    def _generate_text_data(self, variable: VariableGenerationConfig) -> List[Optional[str]]:
        """
        Generate text data based on configuration.
        
        Args:
            variable: Variable configuration
            
        Returns:
            List[Optional[str]]: List of text values
        """
        constraints = variable.constraints or ValueConstraint()
        params = variable.distribution_params or {}
        
        # Get format pattern if available
        pattern = constraints.format_pattern
        
        if pattern:
            # Generate values according to pattern
            result = []
            for _ in range(self.record_count):
                # Simple pattern replacement
                # {L} = random letter, {D} = random digit, {W} = random word
                text = ""
                for char in pattern:
                    if char == "L":
                        text += random.choice("ABCDEFGHIJKLMNOPQRSTUVWXYZ")
                    elif char == "D":
                        text += random.choice("0123456789")
                    else:
                        text += char
                result.append(text)
        else:
            # Generate random text of varying length
            min_length = params.get("min_length", 5)
            max_length = params.get("max_length", 20)
            
            # Sample words
            words = [
                "lorem", "ipsum", "dolor", "sit", "amet", "consectetur",
                "adipiscing", "elit", "sed", "do", "eiusmod", "tempor",
                "incididunt", "ut", "labore", "et", "dolore", "magna", "aliqua"
            ]
            
            result = []
            for _ in range(self.record_count):
                length = random.randint(min_length, max_length)
                text = " ".join(random.choice(words) for _ in range(length))
                result.append(text[:max_length])
        
        # Apply null values if allowed
        if constraints.nullable and constraints.null_probability > 0:
            for i in range(len(result)):
                if random.random() < constraints.null_probability:
                    result[i] = None
        
        return result
