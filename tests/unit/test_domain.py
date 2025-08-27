"""
Unit tests for the domain management module.
"""
import pytest
from pathlib import Path

from datareplicator.core.config import DomainType
from datareplicator.data.domain import (
    DataDomain,
    DomainRegistry,
    domain_registry,
    DomainFactory,
    domain_factory,
    DemographicsDomain,
    LaboratoryDomain,
    VitalSignsDomain
)
from datareplicator.data.models import DomainData


class TestDomainModels:
    """Test cases for domain model classes."""
    
    def test_data_domain(self):
        """Test the base DataDomain class."""
        # Test creation of a custom domain
        custom_domain = DataDomain(
            domain_type="CUSTOM",
            domain_name="Custom Domain",
            description="A custom domain for testing",
            key_variables=["USUBJID"],
            required_variables=["USUBJID", "STUDYID", "DOMAIN"]
        )
        
        assert custom_domain.domain_type == "CUSTOM"
        assert custom_domain.domain_name == "Custom Domain"
        assert "USUBJID" in custom_domain.key_variables
        assert len(custom_domain.required_variables) == 3
    
    def test_demographics_domain(self):
        """Test the DemographicsDomain class."""
        domain = DemographicsDomain()
        
        assert domain.domain_type == DomainType.DEMOGRAPHICS
        assert domain.domain_name == "Demographics"
        assert domain.key_variables == ["USUBJID"]
        assert "SEX" in domain.required_variables
        assert "AGE" in domain.required_variables
        assert "RFSTDTC" in domain.date_variables
        assert "SEX" in domain.categorical_variables
        assert "M" in domain.categorical_variables["SEX"]
        assert "F" in domain.categorical_variables["SEX"]
    
    def test_laboratory_domain(self):
        """Test the LaboratoryDomain class."""
        domain = LaboratoryDomain()
        
        assert domain.domain_type == DomainType.LABORATORY
        assert domain.domain_name == "Laboratory Results"
        assert "USUBJID" in domain.key_variables
        assert "LBSEQ" in domain.key_variables
        assert "LBTESTCD" in domain.required_variables
        assert "LBCAT" in domain.categorical_variables
        assert "CHEMISTRY" in domain.categorical_variables["LBCAT"]


class TestDomainRegistry:
    """Test cases for the domain registry."""
    
    def test_domain_registry_initialization(self):
        """Test that domain registry is properly initialized."""
        # The domain registry should be initialized with built-in domains
        assert domain_registry is not None
        
        # Get all domain types
        domain_types = domain_registry.get_domain_types()
        assert DomainType.DEMOGRAPHICS in domain_types
        assert DomainType.LABORATORY in domain_types
        assert DomainType.VITAL_SIGNS in domain_types
        
        # Get all domains
        domains = domain_registry.get_all_domains()
        assert len(domains) >= 3  # At least the three built-in domains
    
    def test_get_domain(self):
        """Test getting domains from the registry."""
        # Get a specific domain
        dm_domain = domain_registry.get_domain(DomainType.DEMOGRAPHICS)
        assert dm_domain is not None
        assert dm_domain.domain_type == DomainType.DEMOGRAPHICS
        
        lb_domain = domain_registry.get_domain(DomainType.LABORATORY)
        assert lb_domain is not None
        assert lb_domain.domain_type == DomainType.LABORATORY
        
        # Try to get a non-existent domain
        non_existent = domain_registry.get_domain("NON_EXISTENT")
        assert non_existent is None
    
    def test_detect_relationships(self):
        """Test relationship detection between domains."""
        # Create sample domain data
        dm_data = DomainData(
            domain_type=DomainType.DEMOGRAPHICS,
            domain_name="Demographics",
            file_path=Path("dummy/path"),
            columns=["STUDYID", "DOMAIN", "USUBJID", "SUBJID", "SEX", "AGE", "VISITNUM"],
            data=[]
        )
        
        lb_data = DomainData(
            domain_type=DomainType.LABORATORY,
            domain_name="Laboratory Results",
            file_path=Path("dummy/path"),
            columns=["STUDYID", "DOMAIN", "USUBJID", "LBSEQ", "LBTESTCD", "VISITNUM", "LBDTC"],
            data=[]
        )
        
        # Create domain data map
        domain_data_map = {
            DomainType.DEMOGRAPHICS: dm_data,
            DomainType.LABORATORY: lb_data
        }
        
        # Detect relationships
        relationships = domain_registry.detect_relationships(domain_data_map)
        
        # Check that subject-level relationship is detected
        assert "subject_level" in relationships
        assert "DM" in relationships["subject_level"]
        assert "LB" in relationships["subject_level"]
        
        # Check that visit-level relationship is detected
        assert "visit_level" in relationships
        assert "DM" in relationships["visit_level"]
        assert "LB" in relationships["visit_level"]
        
        # Check that time-based relationship is detected for lab only
        assert "time_based" in relationships
        assert "LB" in relationships["time_based"]
        assert "DM" not in relationships["time_based"]


class TestDomainFactory:
    """Test cases for the domain factory."""
    
    def test_domain_factory_initialization(self):
        """Test that domain factory is properly initialized."""
        assert domain_factory is not None
        assert domain_factory.registry is domain_registry
    
    def test_create_domain(self):
        """Test creating domains with the factory."""
        # Create domains by type
        dm_domain = domain_factory.create_domain(DomainType.DEMOGRAPHICS)
        assert dm_domain is not None
        assert dm_domain.domain_type == DomainType.DEMOGRAPHICS
        
        lb_domain = domain_factory.create_domain(DomainType.LABORATORY)
        assert lb_domain is not None
        assert lb_domain.domain_type == DomainType.LABORATORY
        
        # Try to create a non-existent domain
        non_existent = domain_factory.create_domain("NON_EXISTENT")
        assert non_existent is None
    
    def test_create_domain_for_data(self):
        """Test creating a domain for domain data."""
        # Create domain data
        dm_data = DomainData(
            domain_type=DomainType.DEMOGRAPHICS,
            domain_name="Demographics",
            file_path=Path("dummy/path"),
            columns=["STUDYID", "DOMAIN", "USUBJID", "SUBJID", "SEX", "AGE"],
            data=[]
        )
        
        # Create domain for data
        domain = domain_factory.create_domain_for_data(dm_data)
        assert domain is not None
        assert domain.domain_type == DomainType.DEMOGRAPHICS
        
        # Try with unknown domain type
        unknown_data = DomainData(
            domain_type="Unknown",
            domain_name="Unknown",
            file_path=Path("dummy/path"),
            columns=["COL1", "COL2"],
            data=[]
        )
        
        domain = domain_factory.create_domain_for_data(unknown_data)
        assert domain is None
    
    def test_get_domain_metadata(self):
        """Test getting domain metadata."""
        # Get metadata for demographics domain
        metadata = domain_factory.get_domain_metadata(DomainType.DEMOGRAPHICS)
        assert metadata is not None
        assert metadata["domain_type"] == DomainType.DEMOGRAPHICS
        assert metadata["domain_name"] == "Demographics"
        assert "description" in metadata
        assert "key_variables" in metadata
        assert "required_variables" in metadata
        
        # Try with non-existent domain
        empty_metadata = domain_factory.get_domain_metadata("NON_EXISTENT")
        assert empty_metadata == {}
    
    def test_list_available_domains(self):
        """Test listing all available domains."""
        domains = domain_factory.list_available_domains()
        assert len(domains) >= 3  # At least the three built-in domains
        
        # Check that all domains have the required metadata
        for domain in domains:
            assert "domain_type" in domain
            assert "domain_name" in domain
            assert "description" in domain
            assert "key_variables" in domain
            assert "required_variables" in domain
