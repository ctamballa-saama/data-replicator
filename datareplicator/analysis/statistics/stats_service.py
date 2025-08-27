"""
Descriptive statistics service implementation.

Provides methods to calculate descriptive statistics for clinical data.
"""
import logging
import uuid
from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple, Union
import numpy as np
import pandas as pd
from scipy import stats

from datareplicator.core.config import DomainType, constants
from datareplicator.data.models import DomainData
from datareplicator.data.domain import domain_registry
from datareplicator.analysis.models import (
    StatType,
    NumericStats,
    CategoricalStats,
    DateStats,
    VariableStats,
    DomainStats,
    AnalysisResult,
    StatsOverview
)
from datareplicator.data.parsing.utils import is_valid_date, infer_column_type


logger = logging.getLogger(__name__)


class DescriptiveStatsService:
    """
    Service for calculating descriptive statistics.
    
    Analyzes clinical data to generate statistical summaries.
    """
    
    def __init__(self):
        """Initialize the descriptive statistics service."""
        self.domain_registry = domain_registry
        self.cached_stats = {}
    
    def calculate_numeric_stats(self, data: List[Any]) -> NumericStats:
        """
        Calculate statistics for a numeric variable.
        
        Args:
            data: List of numeric values
            
        Returns:
            NumericStats: Statistics for the numeric variable
        """
        # Convert to numeric, ignoring non-numeric values
        numeric_data = pd.to_numeric(pd.Series(data), errors='coerce')
        
        # Filter out NaN values
        clean_data = numeric_data.dropna()
        
        # Calculate basic statistics
        n = len(clean_data)
        n_missing = len(numeric_data) - n
        
        if n == 0:
            # Return empty stats if no valid numeric data
            return NumericStats(
                variable_name="",
                n=0,
                n_missing=n_missing,
                mean=0.0,
                median=0.0,
                std_dev=0.0,
                min=0.0,
                max=0.0,
                q1=0.0,
                q3=0.0,
                range=0.0
            )
        
        # Calculate statistics
        mean = clean_data.mean()
        median = clean_data.median()
        std_dev = clean_data.std()
        min_val = clean_data.min()
        max_val = clean_data.max()
        q1 = clean_data.quantile(0.25)
        q3 = clean_data.quantile(0.75)
        range_val = max_val - min_val
        variance = clean_data.var()
        
        # Calculate advanced statistics
        skewness = stats.skew(clean_data) if n > 2 else None
        kurtosis = stats.kurtosis(clean_data) if n > 3 else None
        
        # Create histogram
        if n >= 5:
            hist, bin_edges = np.histogram(clean_data, bins='auto')
            histogram = [(float(bin_edges[i]), int(hist[i])) for i in range(len(hist))]
        else:
            histogram = None
        
        # Detect outliers (values more than 1.5 IQR from Q1 or Q3)
        iqr = q3 - q1
        lower_bound = q1 - 1.5 * iqr
        upper_bound = q3 + 1.5 * iqr
        outliers = clean_data[(clean_data < lower_bound) | (clean_data > upper_bound)].tolist()
        
        # Create the stats object
        return NumericStats(
            variable_name="",  # Will be set by the caller
            n=n,
            n_missing=n_missing,
            mean=float(mean),
            median=float(median),
            std_dev=float(std_dev),
            min=float(min_val),
            max=float(max_val),
            q1=float(q1),
            q3=float(q3),
            range=float(range_val),
            variance=float(variance),
            skewness=float(skewness) if skewness is not None else None,
            kurtosis=float(kurtosis) if kurtosis is not None else None,
            histogram=histogram,
            outliers=[float(x) for x in outliers] if outliers else None
        )
    
    def calculate_categorical_stats(self, data: List[Any]) -> CategoricalStats:
        """
        Calculate statistics for a categorical variable.
        
        Args:
            data: List of categorical values
            
        Returns:
            CategoricalStats: Statistics for the categorical variable
        """
        # Convert to series and handle missing values
        cat_data = pd.Series(data)
        
        # Count missing values (None, NaN, empty string)
        missing_mask = cat_data.isna() | (cat_data == '')
        clean_data = cat_data[~missing_mask]
        
        n = len(clean_data)
        n_missing = len(cat_data) - n
        
        if n == 0:
            # Return empty stats if no valid categorical data
            return CategoricalStats(
                variable_name="",
                n=0,
                n_missing=n_missing,
                n_unique=0,
                frequencies={},
                percentages={},
                mode="",
                mode_count=0,
                mode_percentage=0.0
            )
        
        # Calculate frequencies
        value_counts = clean_data.value_counts()
        n_unique = len(value_counts)
        
        # Calculate mode
        mode_value = value_counts.index[0]
        mode_count = value_counts[0]
        mode_percentage = (mode_count / n) * 100.0
        
        # Calculate frequencies and percentages
        frequencies = {str(k): int(v) for k, v in value_counts.items()}
        percentages = {str(k): float((v / n) * 100.0) for k, v in value_counts.items()}
        
        # Create the stats object
        return CategoricalStats(
            variable_name="",  # Will be set by the caller
            n=n,
            n_missing=n_missing,
            n_unique=n_unique,
            frequencies=frequencies,
            percentages=percentages,
            mode=str(mode_value),
            mode_count=int(mode_count),
            mode_percentage=float(mode_percentage)
        )
    
    def calculate_date_stats(self, data: List[Any]) -> DateStats:
        """
        Calculate statistics for a date variable.
        
        Args:
            data: List of date values
            
        Returns:
            DateStats: Statistics for the date variable
        """
        # Try to parse dates with multiple formats
        date_formats = ["%Y-%m-%d", "%Y%m%d", "%d%b%Y", "%d-%b-%Y"]
        
        dates = []
        for val in data:
            if not val or pd.isna(val):
                continue
                
            for fmt in date_formats:
                try:
                    dates.append(datetime.strptime(str(val), fmt))
                    break
                except ValueError:
                    continue
        
        # Convert to pandas datetime series
        date_series = pd.Series(dates)
        
        n = len(date_series)
        n_missing = len(data) - n
        
        if n == 0:
            # Return empty stats if no valid date data
            return DateStats(
                variable_name="",
                n=0,
                n_missing=n_missing,
                min_date="",
                max_date="",
                range_days=0,
                year_frequencies={},
                month_frequencies={},
                weekday_frequencies={}
            )
        
        # Calculate basic statistics
        min_date = min(date_series).strftime("%Y-%m-%d")
        max_date = max(date_series).strftime("%Y-%m-%d")
        range_days = (max(date_series) - min(date_series)).days
        
        # Calculate frequencies
        year_freq = date_series.dt.year.value_counts().to_dict()
        month_freq = date_series.dt.month.value_counts().to_dict()
        weekday_freq = date_series.dt.dayofweek.value_counts().to_dict()
        
        # Convert to proper types for serialization
        year_frequencies = {int(k): int(v) for k, v in year_freq.items()}
        month_frequencies = {int(k): int(v) for k, v in month_freq.items()}
        weekday_frequencies = {int(k): int(v) for k, v in weekday_freq.items()}
        
        # Create the stats object
        return DateStats(
            variable_name="",  # Will be set by the caller
            n=n,
            n_missing=n_missing,
            min_date=min_date,
            max_date=max_date,
            range_days=range_days,
            year_frequencies=year_frequencies,
            month_frequencies=month_frequencies,
            weekday_frequencies=weekday_frequencies
        )
    
    def analyze_variable(self, variable_name: str, data: List[Any]) -> VariableStats:
        """
        Analyze a variable and calculate appropriate statistics.
        
        Args:
            variable_name: Name of the variable
            data: List of values for the variable
            
        Returns:
            VariableStats: Statistics for the variable
        """
        # Determine the data type
        data_type = infer_column_type(data)
        
        # Calculate statistics based on the data type
        if data_type == "numeric":
            stats_obj = self.calculate_numeric_stats(data)
            stats_obj.variable_name = variable_name
            
        elif data_type == "date":
            stats_obj = self.calculate_date_stats(data)
            stats_obj.variable_name = variable_name
            
        else:  # categorical or string
            stats_obj = self.calculate_categorical_stats(data)
            stats_obj.variable_name = variable_name
            data_type = "categorical"  # Treat string as categorical
        
        # Create the variable stats object
        return VariableStats(
            variable_name=variable_name,
            data_type=data_type,
            stats=stats_obj
        )
    
    def analyze_domain(self, domain_data: DomainData) -> DomainStats:
        """
        Analyze a clinical data domain and calculate statistics for all variables.
        
        Args:
            domain_data: Domain data to analyze
            
        Returns:
            DomainStats: Statistics for the domain
        """
        # Get domain type and name
        domain_type = domain_data.domain_type
        domain_name = domain_data.domain_name
        
        # Get record and variable counts
        record_count = len(domain_data.data)
        variables = domain_data.columns
        variable_count = len(variables)
        
        # Get unique subject count
        subject_ids = set()
        if constants.USUBJID_VAR in variables:
            for record in domain_data.data:
                if constants.USUBJID_VAR in record and record[constants.USUBJID_VAR]:
                    subject_ids.add(record[constants.USUBJID_VAR])
        
        subject_count = len(subject_ids)
        
        # Group variables by type
        variables_by_type = {"numeric": [], "categorical": [], "date": []}
        variable_stats = {}
        
        # Create a pandas DataFrame for easier analysis
        df = pd.DataFrame(domain_data.data)
        
        # Analyze each variable
        for variable in variables:
            # Extract the column data
            column_data = [record.get(variable) for record in domain_data.data]
            
            # Analyze the variable
            var_stats = self.analyze_variable(variable, column_data)
            
            # Store the results
            variable_stats[variable] = var_stats
            variables_by_type[var_stats.data_type].append(variable)
        
        # Calculate correlations for numeric variables
        correlations = None
        if len(variables_by_type["numeric"]) >= 2:
            # Create a dataframe with only numeric variables
            numeric_vars = variables_by_type["numeric"]
            numeric_df = df[numeric_vars].apply(pd.to_numeric, errors='coerce')
            
            # Calculate correlation matrix
            corr_matrix = numeric_df.corr().round(3)
            
            # Convert to dictionary format
            correlations = {}
            for var1 in numeric_vars:
                correlations[var1] = {}
                for var2 in numeric_vars:
                    if not pd.isna(corr_matrix.loc[var1, var2]):
                        correlations[var1][var2] = float(corr_matrix.loc[var1, var2])
        
        # Create the domain stats object
        return DomainStats(
            domain_type=str(domain_type),
            domain_name=domain_name,
            record_count=record_count,
            subject_count=subject_count,
            variable_count=variable_count,
            variables_by_type=variables_by_type,
            variable_stats=variable_stats,
            correlations=correlations
        )
    
    def analyze_all_domains(self, domain_data_map: Dict[DomainType, DomainData]) -> StatsOverview:
        """
        Analyze all clinical data domains and create a statistics overview.
        
        Args:
            domain_data_map: Dictionary mapping domain types to domain data
            
        Returns:
            StatsOverview: Overview of statistics for all domains
        """
        if not domain_data_map:
            logger.warning("No domain data to analyze")
            return StatsOverview(
                domain_count=0,
                total_record_count=0,
                total_subject_count=0,
                total_variable_count=0,
                domains=[],
                variables_by_domain={},
                variables_by_type={},
                domain_stats={}
            )
        
        # Initialize counters and containers
        domain_count = len(domain_data_map)
        total_record_count = 0
        all_subject_ids = set()
        all_variables = set()
        domains = []
        variables_by_domain = {}
        variables_by_type = {"numeric": [], "categorical": [], "date": []}
        domain_stats = {}
        
        # Analyze each domain
        for domain_type, domain_data in domain_data_map.items():
            # Get domain name
            domain_name = str(domain_type)
            
            # Analyze the domain
            stats = self.analyze_domain(domain_data)
            
            # Update domain stats
            domain_stats[domain_name] = stats
            
            # Update counters and containers
            total_record_count += stats.record_count
            domains.append(domain_name)
            variables_by_domain[domain_name] = domain_data.columns
            
            # Collect all variables by type
            for data_type, vars_list in stats.variables_by_type.items():
                variables_by_type[data_type].extend(vars_list)
            
            # Collect subject IDs
            if constants.USUBJID_VAR in domain_data.columns:
                for record in domain_data.data:
                    if constants.USUBJID_VAR in record and record[constants.USUBJID_VAR]:
                        all_subject_ids.add(record[constants.USUBJID_VAR])
            
            # Add to all variables
            all_variables.update(domain_data.columns)
        
        # Create the overview object
        return StatsOverview(
            domain_count=domain_count,
            total_record_count=total_record_count,
            total_subject_count=len(all_subject_ids),
            total_variable_count=len(all_variables),
            domains=domains,
            variables_by_domain=variables_by_domain,
            variables_by_type=variables_by_type,
            domain_stats=domain_stats
        )
    
    def create_analysis_result(self, analysis_type: str, result_data: Any, 
                              metadata: Optional[Dict[str, Any]] = None) -> AnalysisResult:
        """
        Create an analysis result object.
        
        Args:
            analysis_type: Type of analysis
            result_data: Result data from the analysis
            metadata: Optional metadata about the analysis
            
        Returns:
            AnalysisResult: Analysis result object
        """
        analysis_id = str(uuid.uuid4())
        timestamp = datetime.now()
        
        return AnalysisResult(
            analysis_id=analysis_id,
            analysis_type=analysis_type,
            timestamp=timestamp,
            result_data=result_data,
            metadata=metadata
        )


# Create a singleton instance of the descriptive statistics service
stats_service = DescriptiveStatsService()
