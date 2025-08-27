"""
Domain factory for creating domain instances.

Provides methods to create appropriate domain instances for given data.
"""
import logging
from typing import Optional, Dict, Any, List

from datareplicator.core.config import DomainType
from datareplicator.data.domain.domain_registry import domain_registry
from datareplicator.data.domain.domain_models import DataDomain
from datareplicator.data.models import DomainData


logger = logging.getLogger(__name__)


class DomainFactory:
    """
    Factory for creating domain instances.
    
    Creates appropriate domain instances based on domain data.
    """
    
    def __init__(self):
        """Initialize the domain factory."""
        self.registry = domain_registry
    
    def create_domain(self, domain_type: DomainType) -> Optional[DataDomain]:
        """
        Create a domain instance for the specified domain type.
        
        Args:
            domain_type: Domain type to create
            
        Returns:
            DataDomain instance or None if domain type is not supported
        """
        return self.registry.get_domain(domain_type)
    
    def create_domain_for_data(self, domain_data: DomainData) -> Optional[DataDomain]:
        """
        Create an appropriate domain instance for the given domain data.
        
        Args:
            domain_data: Domain data to create a domain for
            
        Returns:
            DataDomain instance or None if domain type is not supported
        """
        if not domain_data.domain_type or domain_data.domain_type == "Unknown":
            logger.warning("Cannot create domain for unknown domain type")
            return None
            
        return self.create_domain(domain_data.domain_type)
    
    def get_domain_metadata(self, domain_type: DomainType) -> Dict[str, Any]:
        """
        Get metadata for a specific domain.
        
        Args:
            domain_type: Domain type to get metadata for
            
        Returns:
            Dictionary of domain metadata or empty dict if domain type is not supported
        """
        domain = self.create_domain(domain_type)
        if not domain:
            return {}
            
        return {
            "domain_type": domain.domain_type,
            "domain_name": domain.domain_name,
            "description": domain.description,
            "key_variables": domain.key_variables,
            "required_variables": domain.required_variables,
            "date_variables": domain.date_variables,
            "categorical_variables": domain.categorical_variables,
        }
    
    def list_available_domains(self) -> List[Dict[str, Any]]:
        """
        List all available domains with metadata.
        
        Returns:
            List of domain metadata dictionaries
        """
        return [self.get_domain_metadata(domain_type) 
                for domain_type in self.registry.get_domain_types()]


# Create a singleton instance of the domain factory
domain_factory = DomainFactory()
