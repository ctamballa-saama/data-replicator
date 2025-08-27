"""
Relationship analysis service implementation.

Provides methods to analyze and model relationships between clinical data domains.
"""
import logging
import uuid
from datetime import datetime
from typing import Dict, List, Optional, Any, Set, Tuple, Union

import pandas as pd
import numpy as np
from scipy import stats

from datareplicator.core.config import DomainType, constants
from datareplicator.data.models import DomainData
from datareplicator.data.domain import domain_registry
from datareplicator.analysis.relationships.models import (
    RelationshipType,
    RelationshipStrength,
    DomainRelationship,
    SubjectRelationship,
    VisitRelationship,
    TimeRelationship,
    DerivedRelationship,
    RelationshipGraph
)


logger = logging.getLogger(__name__)


class RelationshipAnalysisService:
    """
    Service for analyzing relationships between clinical data domains.
    
    Detects and models various types of relationships between domains.
    """
    
    def __init__(self):
        """Initialize the relationship analysis service."""
        self.domain_registry = domain_registry
        self.cached_relationships = {}
    
    def detect_subject_relationships(self, domain_data_map: Dict[DomainType, DomainData]) -> List[SubjectRelationship]:
        """
        Detect subject-level relationships between domains.
        
        Args:
            domain_data_map: Dictionary mapping domain types to domain data
            
        Returns:
            List of subject relationships
        """
        relationships = []
        
        # Find domains with subject IDs
        subject_domains = []
        for domain_type, data in domain_data_map.items():
            if constants.USUBJID_VAR in data.columns:
                subject_domains.append(str(domain_type))
        
        # Create relationships between all domains with subject IDs
        for i, source_domain in enumerate(subject_domains):
            for target_domain in subject_domains[i+1:]:
                # Create a subject relationship
                relationship = SubjectRelationship(
                    source_domain=source_domain,
                    target_domain=target_domain
                )
                
                # Calculate the strength of the relationship
                source_data = domain_data_map[source_domain]
                target_data = domain_data_map[target_domain]
                
                source_subjects = self._get_subject_ids(source_data)
                target_subjects = self._get_subject_ids(target_data)
                
                # Calculate overlap ratio
                if source_subjects and target_subjects:
                    common_subjects = source_subjects.intersection(target_subjects)
                    overlap_ratio = len(common_subjects) / min(len(source_subjects), len(target_subjects))
                    
                    # Set strength based on overlap ratio
                    if overlap_ratio > 0.8:
                        relationship.strength = RelationshipStrength.STRONG
                    elif overlap_ratio > 0.5:
                        relationship.strength = RelationshipStrength.MODERATE
                    else:
                        relationship.strength = RelationshipStrength.WEAK
                
                relationships.append(relationship)
        
        return relationships
    
    def detect_visit_relationships(self, domain_data_map: Dict[DomainType, DomainData]) -> List[VisitRelationship]:
        """
        Detect visit-level relationships between domains.
        
        Args:
            domain_data_map: Dictionary mapping domain types to domain data
            
        Returns:
            List of visit relationships
        """
        relationships = []
        visit_vars = ["VISITNUM", "VISIT", "VISITDY"]
        
        # Find domains with visit variables
        visit_domains = {}
        for domain_type, data in domain_data_map.items():
            domain_visit_vars = [var for var in visit_vars if var in data.columns]
            if domain_visit_vars and constants.USUBJID_VAR in data.columns:
                visit_domains[str(domain_type)] = domain_visit_vars
        
        # Create relationships between all domains with visit variables
        domain_names = list(visit_domains.keys())
        for i, source_domain in enumerate(domain_names):
            for target_domain in domain_names[i+1:]:
                # Get common visit variables
                common_visit_vars = set(visit_domains[source_domain]).intersection(
                    set(visit_domains[target_domain])
                )
                
                if common_visit_vars:
                    # Create a visit relationship
                    relationship = VisitRelationship(
                        source_domain=source_domain,
                        target_domain=target_domain,
                        visit_vars=list(common_visit_vars)
                    )
                    
                    # Set to moderate strength by default
                    relationship.strength = RelationshipStrength.MODERATE
                    
                    relationships.append(relationship)
        
        return relationships
    
    def detect_time_relationships(self, domain_data_map: Dict[DomainType, DomainData]) -> List[TimeRelationship]:
        """
        Detect time-based relationships between domains.
        
        Args:
            domain_data_map: Dictionary mapping domain types to domain data
            
        Returns:
            List of time relationships
        """
        relationships = []
        
        # Find domains with date variables
        date_domains = {}
        for domain_type, data in domain_data_map.items():
            # Get domain from registry
            domain = self.domain_registry.get_domain(domain_type)
            if not domain:
                continue
            
            # Check for date variables in the domain
            domain_date_vars = []
            for var in data.columns:
                if domain.date_variables and var in domain.date_variables:
                    domain_date_vars.append(var)
            
            if domain_date_vars and constants.USUBJID_VAR in data.columns:
                date_domains[str(domain_type)] = domain_date_vars
        
        # Create time relationships between domains with date variables
        domain_names = list(date_domains.keys())
        for i, source_domain in enumerate(domain_names):
            for target_domain in domain_names[i+1:]:
                # Create a time relationship
                relationship = TimeRelationship(
                    source_domain=source_domain,
                    target_domain=target_domain,
                    time_vars_source=date_domains[source_domain],
                    time_vars_target=date_domains[target_domain]
                )
                
                # Set to moderate strength by default
                relationship.strength = RelationshipStrength.MODERATE
                
                relationships.append(relationship)
        
        return relationships
    
    def detect_derived_relationships(self, domain_data_map: Dict[DomainType, DomainData]) -> List[DerivedRelationship]:
        """
        Detect derived relationships between domains based on domain knowledge.
        
        Args:
            domain_data_map: Dictionary mapping domain types to domain data
            
        Returns:
            List of derived relationships
        """
        relationships = []
        
        # Known derived relationships based on CDISC standards
        known_derivations = [
            # Example: BMI is derived from VS (height and weight)
            {"source": "VS", "target": "DERIVE", "rule": "BMI = WEIGHT / (HEIGHT^2)"},
            # Example: Adverse Events often reference concomitant medications
            {"source": "CM", "target": "AE", "rule": "AECONTRT references CM"},
            # Example: Lab results often reference lab reference ranges
            {"source": "LB", "target": "LBREF", "rule": "LB references LBREF for normal ranges"}
        ]
        
        # Create derived relationships for domains that exist in the data
        domain_names = [str(domain_type) for domain_type in domain_data_map.keys()]
        
        for derivation in known_derivations:
            if derivation["source"] in domain_names and derivation["target"] in domain_names:
                relationship = DerivedRelationship(
                    source_domain=derivation["source"],
                    target_domain=derivation["target"],
                    derivation_rule=derivation["rule"]
                )
                
                # Set to strong strength for known derivations
                relationship.strength = RelationshipStrength.STRONG
                
                relationships.append(relationship)
        
        return relationships
    
    def create_relationship_graph(self, domain_data_map: Dict[DomainType, DomainData]) -> RelationshipGraph:
        """
        Create a complete relationship graph for all domains.
        
        Args:
            domain_data_map: Dictionary mapping domain types to domain data
            
        Returns:
            RelationshipGraph: Graph of all detected relationships
        """
        if not domain_data_map:
            logger.warning("No domain data to analyze relationships")
            return RelationshipGraph(domains=[], relationships=[])
        
        # Detect all types of relationships
        subject_relationships = self.detect_subject_relationships(domain_data_map)
        visit_relationships = self.detect_visit_relationships(domain_data_map)
        time_relationships = self.detect_time_relationships(domain_data_map)
        derived_relationships = self.detect_derived_relationships(domain_data_map)
        
        # Combine all relationships
        all_relationships = []
        all_relationships.extend(subject_relationships)
        all_relationships.extend(visit_relationships)
        all_relationships.extend(time_relationships)
        all_relationships.extend(derived_relationships)
        
        # Get all domain names
        domains = set()
        for rel in all_relationships:
            domains.add(rel.source_domain)
            domains.add(rel.target_domain)
        
        # Create the relationship graph
        graph = RelationshipGraph(
            domains=list(domains),
            relationships=all_relationships
        )
        
        return graph
    
    def analyze_relationship_strength(self, domain_data_map: Dict[DomainType, DomainData], 
                                     relationship: DomainRelationship) -> RelationshipStrength:
        """
        Analyze the strength of a relationship based on data overlap.
        
        Args:
            domain_data_map: Dictionary mapping domain types to domain data
            relationship: Relationship to analyze
            
        Returns:
            RelationshipStrength: Calculated relationship strength
        """
        # Get domain data
        source_type = next((dt for dt in domain_data_map.keys() 
                          if str(dt) == relationship.source_domain), None)
        target_type = next((dt for dt in domain_data_map.keys() 
                          if str(dt) == relationship.target_domain), None)
        
        if not source_type or not target_type:
            return RelationshipStrength.UNKNOWN
        
        source_data = domain_data_map[source_type]
        target_data = domain_data_map[target_type]
        
        # For subject relationship, check overlap of subject IDs
        if relationship.relationship_type == RelationshipType.SUBJECT:
            source_subjects = self._get_subject_ids(source_data)
            target_subjects = self._get_subject_ids(target_data)
            
            if source_subjects and target_subjects:
                common_subjects = source_subjects.intersection(target_subjects)
                overlap_ratio = len(common_subjects) / min(len(source_subjects), len(target_subjects))
                
                if overlap_ratio > 0.8:
                    return RelationshipStrength.STRONG
                elif overlap_ratio > 0.5:
                    return RelationshipStrength.MODERATE
                else:
                    return RelationshipStrength.WEAK
        
        # For visit relationship, check overlap of visits
        elif relationship.relationship_type == RelationshipType.VISIT:
            # Check if required variables exist in both domains
            visit_vars = [var for var in relationship.join_variables if var != "USUBJID"]
            
            if not all(var in source_data.columns for var in visit_vars) or \
               not all(var in target_data.columns for var in visit_vars):
                return RelationshipStrength.WEAK
            
            # For simplicity, check first visit variable
            if visit_vars:
                visit_var = visit_vars[0]
                source_visits = set(record.get(visit_var) for record in source_data.data 
                                if visit_var in record and record.get(visit_var) is not None)
                target_visits = set(record.get(visit_var) for record in target_data.data 
                                if visit_var in record and record.get(visit_var) is not None)
                
                if source_visits and target_visits:
                    common_visits = source_visits.intersection(target_visits)
                    overlap_ratio = len(common_visits) / min(len(source_visits), len(target_visits))
                    
                    if overlap_ratio > 0.7:
                        return RelationshipStrength.STRONG
                    elif overlap_ratio > 0.3:
                        return RelationshipStrength.MODERATE
                    else:
                        return RelationshipStrength.WEAK
        
        return RelationshipStrength.UNKNOWN
    
    def _get_subject_ids(self, domain_data: DomainData) -> Set[str]:
        """
        Get all unique subject IDs from a domain.
        
        Args:
            domain_data: Domain data
            
        Returns:
            Set of subject IDs
        """
        subject_ids = set()
        
        if constants.USUBJID_VAR in domain_data.columns:
            for record in domain_data.data:
                if constants.USUBJID_VAR in record and record[constants.USUBJID_VAR] is not None:
                    subject_ids.add(str(record[constants.USUBJID_VAR]))
        
        return subject_ids


# Create a singleton instance of the relationship analysis service
relationship_service = RelationshipAnalysisService()
