"""
Domain registry for managing clinical data domains.

Provides a centralized registry for domain classes and instances.
"""
import logging
from typing import Dict, List, Optional, Type, Set

from datareplicator.core.config import DomainType
from datareplicator.data.domain.domain_models import (
    DataDomain, 
    DemographicsDomain,
    LaboratoryDomain,
    VitalSignsDomain
)
from datareplicator.data.models import DomainData


logger = logging.getLogger(__name__)


class DomainRegistry:
    """
    Registry for clinical data domains.
    
    Manages domain classes and their relationships.
    """
    
    def __init__(self):
        """Initialize the domain registry."""
        self._domains: Dict[DomainType, DataDomain] = {}
        self._initialize_domains()
    
    def _initialize_domains(self):
        """Initialize and register built-in domain classes."""
        # Register built-in domains
        self.register_domain(DemographicsDomain())
        self.register_domain(LaboratoryDomain())
        self.register_domain(VitalSignsDomain())
    
    def register_domain(self, domain: DataDomain):
        """
        Register a domain in the registry.
        
        Args:
            domain: Domain instance to register
        """
        self._domains[domain.domain_type] = domain
        logger.info(f"Registered domain: {domain.domain_name} ({domain.domain_type})")
    
    def get_domain(self, domain_type: DomainType) -> Optional[DataDomain]:
        """
        Get a domain by type.
        
        Args:
            domain_type: Domain type to look up
            
        Returns:
            DataDomain instance or None if not found
        """
        return self._domains.get(domain_type)
    
    def get_all_domains(self) -> List[DataDomain]:
        """
        Get all registered domains.
        
        Returns:
            List of all domain instances
        """
        return list(self._domains.values())
    
    def get_domain_types(self) -> Set[DomainType]:
        """
        Get all registered domain types.
        
        Returns:
            Set of domain types
        """
        return set(self._domains.keys())
    
    def detect_relationships(self, domain_data_map: Dict[DomainType, DomainData]) -> Dict[str, List[str]]:
        """
        Detect relationships between domains based on shared key variables.
        
        Args:
            domain_data_map: Dictionary mapping domain types to domain data
            
        Returns:
            Dictionary mapping relationship names to lists of related domains
        """
        relationships = {}
        
        # Detect subject-level relationships
        subject_domains = []
        for domain_type, data in domain_data_map.items():
            domain = self.get_domain(domain_type)
            if domain and "USUBJID" in data.columns:
                subject_domains.append(domain_type.value)
        
        if subject_domains:
            relationships["subject_level"] = subject_domains
        
        # Detect visit-level relationships
        visit_domains = []
        for domain_type, data in domain_data_map.items():
            if "VISITNUM" in data.columns or "VISIT" in data.columns:
                visit_domains.append(domain_type.value)
        
        if visit_domains:
            relationships["visit_level"] = visit_domains
        
        # Detect time-based relationships (domains with date variables)
        time_domains = []
        for domain_type, data in domain_data_map.items():
            domain = self.get_domain(domain_type)
            if domain and any(date_var in data.columns for date_var in domain.date_variables):
                time_domains.append(domain_type.value)
        
        if time_domains:
            relationships["time_based"] = time_domains
        
        return relationships


# Create a singleton instance of the domain registry
domain_registry = DomainRegistry()
