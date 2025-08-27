"""
Unit tests for the descriptive statistics service.
"""
import pytest
import numpy as np
import pandas as pd
from pathlib import Path
from datetime import datetime

from datareplicator.core.config import DomainType
from datareplicator.data.models import DomainData
from datareplicator.analysis.statistics import DescriptiveStatsService
from datareplicator.analysis.models import (
    NumericStats, 
    CategoricalStats, 
    DateStats,
    VariableStats,
    DomainStats
)


class TestDescriptiveStatsService:
    """Test cases for the descriptive statistics service."""
    
    def test_initialization(self):
        """Test service initialization."""
        service = DescriptiveStatsService()
        
        assert service.domain_registry is not None
        assert service.cached_stats == {}
    
    def test_calculate_numeric_stats(self):
        """Test calculating statistics for numeric data."""
        service = DescriptiveStatsService()
        
        # Test with valid numeric data
        data = [10, 20, 30, 40, 50, 60, 70, 80, 90, 100]
        stats = service.calculate_numeric_stats(data)
        
        assert stats.n == 10
        assert stats.n_missing == 0
        assert stats.mean == 55.0
        assert stats.median == 55.0
        assert stats.min == 10.0
        assert stats.max == 100.0
        assert stats.std_dev == pytest.approx(30.277, 0.001)
        assert stats.q1 == 32.5
        assert stats.q3 == 77.5
        assert stats.range == 90.0
        assert stats.variance == pytest.approx(916.667, 0.001)
        assert stats.outliers == []  # No outliers in this dataset
        
        # Test with missing values
        data_with_missing = [10, None, 30, np.nan, 50, 60, 'invalid', 80, 90, 100]
        stats = service.calculate_numeric_stats(data_with_missing)
        
        assert stats.n == 7
        assert stats.n_missing == 3
        assert stats.mean == pytest.approx(60.0)
        
        # Test with empty data
        empty_stats = service.calculate_numeric_stats([])
        assert empty_stats.n == 0
        assert empty_stats.mean == 0.0
        
        # Test with outliers
        outlier_data = [10, 20, 30, 40, 50, 200]
        outlier_stats = service.calculate_numeric_stats(outlier_data)
        assert len(outlier_stats.outliers) == 1
        assert outlier_stats.outliers[0] == 200.0
    
    def test_calculate_categorical_stats(self):
        """Test calculating statistics for categorical data."""
        service = DescriptiveStatsService()
        
        # Test with valid categorical data
        data = ['A', 'B', 'A', 'C', 'B', 'A', 'D', 'A', 'A']
        stats = service.calculate_categorical_stats(data)
        
        assert stats.n == 9
        assert stats.n_missing == 0
        assert stats.n_unique == 4
        assert stats.mode == 'A'
        assert stats.mode_count == 5
        assert stats.mode_percentage == pytest.approx(55.56, 0.01)
        assert stats.frequencies['A'] == 5
        assert stats.frequencies['B'] == 2
        assert stats.frequencies['C'] == 1
        assert stats.frequencies['D'] == 1
        
        # Test with missing values
        data_with_missing = ['A', None, 'A', '', np.nan, 'B', 'A', 'B', 'C']
        stats = service.calculate_categorical_stats(data_with_missing)
        
        assert stats.n == 6
        assert stats.n_missing == 3
        assert stats.mode == 'A'
        assert stats.mode_count == 3
        
        # Test with empty data
        empty_stats = service.calculate_categorical_stats([])
        assert empty_stats.n == 0
        assert empty_stats.n_unique == 0
        assert empty_stats.frequencies == {}
    
    def test_calculate_date_stats(self):
        """Test calculating statistics for date data."""
        service = DescriptiveStatsService()
        
        # Test with valid date data
        data = ['2023-01-01', '2023-01-15', '2023-02-01', '2023-02-15', '2023-03-01']
        stats = service.calculate_date_stats(data)
        
        assert stats.n == 5
        assert stats.n_missing == 0
        assert stats.min_date == '2023-01-01'
        assert stats.max_date == '2023-03-01'
        assert stats.range_days == 59
        assert 2023 in stats.year_frequencies
        assert stats.year_frequencies[2023] == 5
        
        # Test with different date formats
        mixed_formats = ['2023-01-01', '20230115', '01Feb2023', '15-Feb-2023', '01Mar2023']
        stats = service.calculate_date_stats(mixed_formats)
        
        assert stats.n == 5
        assert stats.min_date == '2023-01-01'
        assert stats.max_date == '2023-03-01'
        
        # Test with missing values
        data_with_missing = ['2023-01-01', None, '2023-02-01', '', '2023-03-01']
        stats = service.calculate_date_stats(data_with_missing)
        
        assert stats.n == 3
        assert stats.n_missing == 2
        assert stats.min_date == '2023-01-01'
        assert stats.max_date == '2023-03-01'
        
        # Test with empty data
        empty_stats = service.calculate_date_stats([])
        assert empty_stats.n == 0
        assert empty_stats.min_date == ''
        assert empty_stats.max_date == ''
    
    def test_analyze_variable(self):
        """Test analyzing a variable to produce appropriate statistics."""
        service = DescriptiveStatsService()
        
        # Test with numeric data
        numeric_data = [10, 20, 30, 40, 50, 60]
        var_stats = service.analyze_variable("AGE", numeric_data)
        
        assert var_stats.variable_name == "AGE"
        assert var_stats.data_type == "numeric"
        assert isinstance(var_stats.stats, NumericStats)
        assert var_stats.stats.n == 6
        assert var_stats.stats.mean == 35.0
        
        # Test with categorical data
        cat_data = ['M', 'F', 'M', 'F', 'M', 'F', 'M']
        var_stats = service.analyze_variable("SEX", cat_data)
        
        assert var_stats.variable_name == "SEX"
        assert var_stats.data_type == "categorical"
        assert isinstance(var_stats.stats, CategoricalStats)
        assert var_stats.stats.n == 7
        assert var_stats.stats.n_unique == 2
        assert var_stats.stats.frequencies['M'] == 4
        
        # Test with date data
        date_data = ['2023-01-01', '2023-02-01', '2023-03-01']
        var_stats = service.analyze_variable("VISIT_DATE", date_data)
        
        assert var_stats.variable_name == "VISIT_DATE"
        assert var_stats.data_type == "date"
        assert isinstance(var_stats.stats, DateStats)
        assert var_stats.stats.n == 3
        assert var_stats.stats.min_date == '2023-01-01'
        assert var_stats.stats.max_date == '2023-03-01'
    
    def test_analyze_domain(self):
        """Test analyzing a domain to produce domain statistics."""
        service = DescriptiveStatsService()
        
        # Create a test domain data object
        domain_data = DomainData(
            domain_type=DomainType.DEMOGRAPHICS,
            domain_name="Demographics",
            file_path=Path("dummy/path"),
            columns=["USUBJID", "SEX", "AGE", "RACE", "COUNTRY", "BIRTHDT"],
            data=[
                {"USUBJID": "SUBJ001", "SEX": "M", "AGE": 45, "RACE": "WHITE", "COUNTRY": "USA", "BIRTHDT": "1978-05-15"},
                {"USUBJID": "SUBJ002", "SEX": "F", "AGE": 52, "RACE": "BLACK OR AFRICAN AMERICAN", "COUNTRY": "USA", "BIRTHDT": "1971-08-23"},
                {"USUBJID": "SUBJ003", "SEX": "M", "AGE": 38, "RACE": "ASIAN", "COUNTRY": "JPN", "BIRTHDT": "1985-11-07"},
                {"USUBJID": "SUBJ004", "SEX": "F", "AGE": 61, "RACE": "WHITE", "COUNTRY": "USA", "BIRTHDT": "1962-03-18"},
                {"USUBJID": "SUBJ005", "SEX": "M", "AGE": 57, "RACE": "WHITE", "COUNTRY": "CAN", "BIRTHDT": "1966-09-30"}
            ]
        )
        
        # Analyze the domain
        domain_stats = service.analyze_domain(domain_data)
        
        # Verify domain metadata
        assert domain_stats.domain_type == str(DomainType.DEMOGRAPHICS)
        assert domain_stats.domain_name == "Demographics"
        assert domain_stats.record_count == 5
        assert domain_stats.subject_count == 5
        assert domain_stats.variable_count == 6
        
        # Verify variables by type
        assert "AGE" in domain_stats.variables_by_type["numeric"]
        assert "SEX" in domain_stats.variables_by_type["categorical"]
        assert "RACE" in domain_stats.variables_by_type["categorical"]
        assert "BIRTHDT" in domain_stats.variables_by_type["date"]
        
        # Verify variable stats
        assert "AGE" in domain_stats.variable_stats
        assert "SEX" in domain_stats.variable_stats
        assert "BIRTHDT" in domain_stats.variable_stats
        
        # Check numeric stats
        age_stats = domain_stats.variable_stats["AGE"].stats
        assert age_stats.n == 5
        assert age_stats.mean == 50.6
        
        # Check categorical stats
        sex_stats = domain_stats.variable_stats["SEX"].stats
        assert sex_stats.n == 5
        assert sex_stats.n_unique == 2
        assert sex_stats.frequencies["M"] == 3
        assert sex_stats.frequencies["F"] == 2
        
        # Check date stats
        birth_stats = domain_stats.variable_stats["BIRTHDT"].stats
        assert birth_stats.n == 5
        assert birth_stats.min_date <= "1962-03-18"
        assert birth_stats.max_date >= "1985-11-07"
        
        # Check correlations
        assert domain_stats.correlations is None  # Only one numeric variable
    
    def test_analyze_all_domains(self):
        """Test analyzing all domains to produce an overview."""
        service = DescriptiveStatsService()
        
        # Create test domain data objects
        dm_data = DomainData(
            domain_type=DomainType.DEMOGRAPHICS,
            domain_name="Demographics",
            file_path=Path("dummy/path"),
            columns=["USUBJID", "SEX", "AGE", "RACE"],
            data=[
                {"USUBJID": "SUBJ001", "SEX": "M", "AGE": 45, "RACE": "WHITE"},
                {"USUBJID": "SUBJ002", "SEX": "F", "AGE": 52, "RACE": "BLACK OR AFRICAN AMERICAN"},
                {"USUBJID": "SUBJ003", "SEX": "M", "AGE": 38, "RACE": "ASIAN"}
            ]
        )
        
        lb_data = DomainData(
            domain_type=DomainType.LABORATORY,
            domain_name="Laboratory Results",
            file_path=Path("dummy/path"),
            columns=["USUBJID", "LBTEST", "LBORRES", "LBSTNRLO", "LBSTNRHI", "LBDTC"],
            data=[
                {"USUBJID": "SUBJ001", "LBTEST": "Glucose", "LBORRES": 5.2, "LBSTNRLO": 3.9, "LBSTNRHI": 5.8, "LBDTC": "2023-01-15"},
                {"USUBJID": "SUBJ002", "LBTEST": "Glucose", "LBORRES": 4.8, "LBSTNRLO": 3.9, "LBSTNRHI": 5.8, "LBDTC": "2023-01-16"},
                {"USUBJID": "SUBJ003", "LBTEST": "Glucose", "LBORRES": 5.5, "LBSTNRLO": 3.9, "LBSTNRHI": 5.8, "LBDTC": "2023-01-17"},
                {"USUBJID": "SUBJ001", "LBTEST": "Hemoglobin", "LBORRES": 14.5, "LBSTNRLO": 13.5, "LBSTNRHI": 17.5, "LBDTC": "2023-01-15"},
                {"USUBJID": "SUBJ002", "LBTEST": "Hemoglobin", "LBORRES": 13.8, "LBSTNRLO": 12.0, "LBSTNRHI": 15.5, "LBDTC": "2023-01-16"}
            ]
        )
        
        # Create domain data map
        domain_data_map = {
            DomainType.DEMOGRAPHICS: dm_data,
            DomainType.LABORATORY: lb_data
        }
        
        # Analyze all domains
        overview = service.analyze_all_domains(domain_data_map)
        
        # Verify overview metadata
        assert overview.domain_count == 2
        assert overview.total_record_count == 8
        assert overview.total_subject_count == 3
        assert overview.total_variable_count >= 9  # Accounting for unique columns
        
        # Verify domains
        assert "DM" in overview.domains
        assert "LB" in overview.domains
        
        # Verify variables by domain
        assert "USUBJID" in overview.variables_by_domain["DM"]
        assert "LBTEST" in overview.variables_by_domain["LB"]
        
        # Verify domain stats
        assert "DM" in overview.domain_stats
        assert "LB" in overview.domain_stats
        assert overview.domain_stats["DM"].record_count == 3
        assert overview.domain_stats["LB"].record_count == 5
        
        # Test with empty domain data map
        empty_overview = service.analyze_all_domains({})
        assert empty_overview.domain_count == 0
        assert empty_overview.total_record_count == 0
        assert empty_overview.total_subject_count == 0
