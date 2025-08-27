"""
Relationship analysis models for the DataReplicator application.

These models define the structure of relationships between clinical data domains.
"""
from enum import Enum
from typing import Dict, List, Optional, Any, Set, Union

from pydantic import BaseModel, Field


class RelationshipType(str, Enum):
    """Types of relationships between domains."""
    
    SUBJECT = "subject"
    VISIT = "visit"
    TIME = "time"
    PARENT_CHILD = "parent_child"
    DERIVED = "derived"
    CUSTOM = "custom"


class RelationshipStrength(str, Enum):
    """Strength of relationships between domains."""
    
    STRONG = "strong"
    MODERATE = "moderate"
    WEAK = "weak"
    UNKNOWN = "unknown"


class DomainRelationship(BaseModel):
    """Represents a relationship between two clinical data domains."""
    
    source_domain: str
    target_domain: str
    relationship_type: RelationshipType
    strength: RelationshipStrength = RelationshipStrength.UNKNOWN
    join_variables: List[str]
    description: str
    metadata: Optional[Dict[str, Any]] = None


class SubjectRelationship(DomainRelationship):
    """Relationship where domains are linked by subject ID."""
    
    def __init__(self, source_domain: str, target_domain: str, **data):
        """Initialize a subject relationship."""
        super().__init__(
            source_domain=source_domain,
            target_domain=target_domain,
            relationship_type=RelationshipType.SUBJECT,
            join_variables=["USUBJID"],
            description=f"Domains {source_domain} and {target_domain} are related by subject",
            **data
        )


class VisitRelationship(DomainRelationship):
    """Relationship where domains are linked by visit information."""
    
    def __init__(self, source_domain: str, target_domain: str, visit_vars: List[str], **data):
        """Initialize a visit relationship."""
        super().__init__(
            source_domain=source_domain,
            target_domain=target_domain,
            relationship_type=RelationshipType.VISIT,
            join_variables=["USUBJID"] + visit_vars,
            description=f"Domains {source_domain} and {target_domain} are related by visit",
            **data
        )


class TimeRelationship(DomainRelationship):
    """Relationship where domains are linked by time/date variables."""
    
    def __init__(self, source_domain: str, target_domain: str, 
                time_vars_source: List[str], time_vars_target: List[str], **data):
        """Initialize a time relationship."""
        super().__init__(
            source_domain=source_domain,
            target_domain=target_domain,
            relationship_type=RelationshipType.TIME,
            join_variables=["USUBJID"],  # Basic join by subject
            description=f"Domains {source_domain} and {target_domain} are related by time",
            metadata={
                "time_vars_source": time_vars_source,
                "time_vars_target": time_vars_target
            },
            **data
        )


class DerivedRelationship(DomainRelationship):
    """Relationship where one domain is derived from another."""
    
    def __init__(self, source_domain: str, target_domain: str, derivation_rule: str, **data):
        """Initialize a derived relationship."""
        super().__init__(
            source_domain=source_domain,
            target_domain=target_domain,
            relationship_type=RelationshipType.DERIVED,
            join_variables=["USUBJID"],  # Basic join by subject
            description=f"Domain {target_domain} is derived from {source_domain}",
            metadata={
                "derivation_rule": derivation_rule
            },
            **data
        )


class RelationshipGraph(BaseModel):
    """Graph of relationships between clinical data domains."""
    
    domains: List[str]
    relationships: List[DomainRelationship]
    
    def get_related_domains(self, domain: str) -> Set[str]:
        """
        Get domains related to the specified domain.
        
        Args:
            domain: Domain to find relationships for
            
        Returns:
            Set of related domain names
        """
        related = set()
        
        for rel in self.relationships:
            if rel.source_domain == domain:
                related.add(rel.target_domain)
            elif rel.target_domain == domain:
                related.add(rel.source_domain)
        
        return related
    
    def get_relationships_by_type(self, rel_type: RelationshipType) -> List[DomainRelationship]:
        """
        Get all relationships of a specific type.
        
        Args:
            rel_type: Relationship type to filter by
            
        Returns:
            List of relationships of the specified type
        """
        return [r for r in self.relationships if r.relationship_type == rel_type]
    
    def get_relationships_for_domain(self, domain: str) -> List[DomainRelationship]:
        """
        Get all relationships involving the specified domain.
        
        Args:
            domain: Domain to find relationships for
            
        Returns:
            List of relationships involving the domain
        """
        return [r for r in self.relationships 
                if r.source_domain == domain or r.target_domain == domain]
