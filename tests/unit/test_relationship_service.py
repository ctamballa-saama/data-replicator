"""
Unit tests for the relationship analysis service.
"""
import pytest
import numpy as np
import pandas as pd
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Set

from datareplicator.core.config import DomainType
from datareplicator.data.models import DomainData
from datareplicator.analysis.relationships import (
    RelationshipType,
    RelationshipStrength,
    DomainRelationship,
    SubjectRelationship,
    VisitRelationship,
    TimeRelationship,
    DerivedRelationship,
    RelationshipGraph,
    RelationshipAnalysisService
)


class TestRelationshipModels:
    """Test cases for relationship models."""
    
    def test_domain_relationship(self):
        """Test the basic domain relationship model."""
        relationship = DomainRelationship(
            source_domain="DM",
            target_domain="LB",
            relationship_type=RelationshipType.SUBJECT,
            strength=RelationshipStrength.STRONG,
            join_variables=["USUBJID"],
            description="Demographics and lab results are related by subject"
        )
        
        assert relationship.source_domain == "DM"
        assert relationship.target_domain == "LB"
        assert relationship.relationship_type == RelationshipType.SUBJECT
        assert relationship.strength == RelationshipStrength.STRONG
        assert relationship.join_variables == ["USUBJID"]
        assert "related by subject" in relationship.description
    
    def test_subject_relationship(self):
        """Test the subject relationship model."""
        relationship = SubjectRelationship(
            source_domain="DM",
            target_domain="VS"
        )
        
        assert relationship.source_domain == "DM"
        assert relationship.target_domain == "VS"
        assert relationship.relationship_type == RelationshipType.SUBJECT
        assert relationship.join_variables == ["USUBJID"]
        assert "related by subject" in relationship.description
    
    def test_visit_relationship(self):
        """Test the visit relationship model."""
        relationship = VisitRelationship(
            source_domain="VS",
            target_domain="LB",
            visit_vars=["VISITNUM", "VISIT"]
        )
        
        assert relationship.source_domain == "VS"
        assert relationship.target_domain == "LB"
        assert relationship.relationship_type == RelationshipType.VISIT
        assert set(relationship.join_variables) == {"USUBJID", "VISITNUM", "VISIT"}
        assert "related by visit" in relationship.description
    
    def test_time_relationship(self):
        """Test the time relationship model."""
        relationship = TimeRelationship(
            source_domain="VS",
            target_domain="LB",
            time_vars_source=["VSDT"],
            time_vars_target=["LBDT"]
        )
        
        assert relationship.source_domain == "VS"
        assert relationship.target_domain == "LB"
        assert relationship.relationship_type == RelationshipType.TIME
        assert relationship.join_variables == ["USUBJID"]
        assert "related by time" in relationship.description
        assert relationship.metadata["time_vars_source"] == ["VSDT"]
        assert relationship.metadata["time_vars_target"] == ["LBDT"]
    
    def test_derived_relationship(self):
        """Test the derived relationship model."""
        relationship = DerivedRelationship(
            source_domain="VS",
            target_domain="DERIVE",
            derivation_rule="BMI = WEIGHT / (HEIGHT^2)"
        )
        
        assert relationship.source_domain == "VS"
        assert relationship.target_domain == "DERIVE"
        assert relationship.relationship_type == RelationshipType.DERIVED
        assert relationship.join_variables == ["USUBJID"]
        assert relationship.metadata["derivation_rule"] == "BMI = WEIGHT / (HEIGHT^2)"
    
    def test_relationship_graph(self):
        """Test the relationship graph model."""
        relationships = [
            SubjectRelationship(source_domain="DM", target_domain="VS"),
            SubjectRelationship(source_domain="DM", target_domain="LB"),
            VisitRelationship(source_domain="VS", target_domain="LB", visit_vars=["VISITNUM"])
        ]
        
        graph = RelationshipGraph(
            domains=["DM", "VS", "LB"],
            relationships=relationships
        )
        
        assert set(graph.domains) == {"DM", "VS", "LB"}
        assert len(graph.relationships) == 3
        
        # Test get_related_domains
        related_to_dm = graph.get_related_domains("DM")
        assert related_to_dm == {"VS", "LB"}
        
        # Test get_relationships_by_type
        subject_rels = graph.get_relationships_by_type(RelationshipType.SUBJECT)
        assert len(subject_rels) == 2
        
        visit_rels = graph.get_relationships_by_type(RelationshipType.VISIT)
        assert len(visit_rels) == 1
        
        # Test get_relationships_for_domain
        dm_rels = graph.get_relationships_for_domain("DM")
        assert len(dm_rels) == 2
        
        vs_rels = graph.get_relationships_for_domain("VS")
        assert len(vs_rels) == 2  # One with DM, one with LB


class TestRelationshipAnalysisService:
    """Test cases for the relationship analysis service."""
    
    @pytest.fixture
    def domain_data_map(self) -> Dict[DomainType, DomainData]:
        """Fixture to create test domain data."""
        # Demographics domain
        dm_data = DomainData(
            domain_type=DomainType.DEMOGRAPHICS,
            domain_name="Demographics",
            file_path=Path("dummy/path"),
            columns=["USUBJID", "SEX", "AGE", "RACE", "COUNTRY"],
            data=[
                {"USUBJID": "SUBJ001", "SEX": "M", "AGE": 45, "RACE": "WHITE", "COUNTRY": "USA"},
                {"USUBJID": "SUBJ002", "SEX": "F", "AGE": 52, "RACE": "BLACK OR AFRICAN AMERICAN", "COUNTRY": "USA"},
                {"USUBJID": "SUBJ003", "SEX": "M", "AGE": 38, "RACE": "ASIAN", "COUNTRY": "JPN"}
            ]
        )
        
        # Laboratory domain with visit information
        lb_data = DomainData(
            domain_type=DomainType.LABORATORY,
            domain_name="Laboratory Results",
            file_path=Path("dummy/path"),
            columns=["USUBJID", "VISITNUM", "VISIT", "LBTEST", "LBORRES", "LBDTC"],
            data=[
                {"USUBJID": "SUBJ001", "VISITNUM": 1, "VISIT": "SCREENING", "LBTEST": "Glucose", "LBORRES": 5.2, "LBDTC": "2023-01-15"},
                {"USUBJID": "SUBJ001", "VISITNUM": 2, "VISIT": "BASELINE", "LBTEST": "Glucose", "LBORRES": 5.0, "LBDTC": "2023-02-01"},
                {"USUBJID": "SUBJ002", "VISITNUM": 1, "VISIT": "SCREENING", "LBTEST": "Glucose", "LBORRES": 4.8, "LBDTC": "2023-01-16"},
                {"USUBJID": "SUBJ003", "VISITNUM": 1, "VISIT": "SCREENING", "LBTEST": "Glucose", "LBORRES": 5.5, "LBDTC": "2023-01-17"}
            ]
        )
        
        # Vital signs domain with visit information
        vs_data = DomainData(
            domain_type=DomainType.VITAL_SIGNS,
            domain_name="Vital Signs",
            file_path=Path("dummy/path"),
            columns=["USUBJID", "VISITNUM", "VISIT", "VSTEST", "VSORRES", "VSDTC"],
            data=[
                {"USUBJID": "SUBJ001", "VISITNUM": 1, "VISIT": "SCREENING", "VSTEST": "Blood Pressure", "VSORRES": "120/80", "VSDTC": "2023-01-15"},
                {"USUBJID": "SUBJ001", "VISITNUM": 2, "VISIT": "BASELINE", "VSTEST": "Blood Pressure", "VSORRES": "122/82", "VSDTC": "2023-02-01"},
                {"USUBJID": "SUBJ002", "VISITNUM": 1, "VISIT": "SCREENING", "VSTEST": "Blood Pressure", "VSORRES": "118/76", "VSDTC": "2023-01-16"}
            ]
        )
        
        return {
            DomainType.DEMOGRAPHICS: dm_data,
            DomainType.LABORATORY: lb_data,
            DomainType.VITAL_SIGNS: vs_data
        }
    
    def test_initialization(self):
        """Test service initialization."""
        service = RelationshipAnalysisService()
        
        assert service.domain_registry is not None
        assert service.cached_relationships == {}
    
    def test_detect_subject_relationships(self, domain_data_map):
        """Test detecting subject relationships."""
        service = RelationshipAnalysisService()
        
        relationships = service.detect_subject_relationships(domain_data_map)
        
        # Should have relationships between DM-LB, DM-VS, and LB-VS
        assert len(relationships) == 3
        
        # Check relationship properties
        for rel in relationships:
            assert rel.relationship_type == RelationshipType.SUBJECT
            assert rel.join_variables == ["USUBJID"]
            assert rel.strength in [RelationshipStrength.STRONG, RelationshipStrength.MODERATE, RelationshipStrength.WEAK]
            
            # Both source and target domains should be in the domain map
            source = rel.source_domain
            target = rel.target_domain
            assert any(str(dt) == source for dt in domain_data_map.keys())
            assert any(str(dt) == target for dt in domain_data_map.keys())
    
    def test_detect_visit_relationships(self, domain_data_map):
        """Test detecting visit relationships."""
        service = RelationshipAnalysisService()
        
        relationships = service.detect_visit_relationships(domain_data_map)
        
        # Should have relationship between LB-VS (both have VISITNUM, VISIT)
        assert len(relationships) == 1
        
        # Check the relationship properties
        rel = relationships[0]
        assert rel.relationship_type == RelationshipType.VISIT
        assert "USUBJID" in rel.join_variables
        assert "VISITNUM" in rel.join_variables
        assert "VISIT" in rel.join_variables
        
        # Source and target should be LB and VS (in either order)
        domains = {rel.source_domain, rel.target_domain}
        assert domains == {str(DomainType.LABORATORY), str(DomainType.VITAL_SIGNS)}
    
    def test_detect_time_relationships(self, domain_data_map):
        """Test detecting time relationships."""
        service = RelationshipAnalysisService()
        
        # Mock the domain registry to identify date variables
        service.domain_registry.get_domain = lambda dt: type('MockDomain', (), {
            'date_variables': ['LBDTC'] if dt == DomainType.LABORATORY else 
                             ['VSDTC'] if dt == DomainType.VITAL_SIGNS else []
        })
        
        relationships = service.detect_time_relationships(domain_data_map)
        
        # Should have relationship between LB-VS (both have date variables)
        assert len(relationships) == 1
        
        # Check the relationship properties
        rel = relationships[0]
        assert rel.relationship_type == RelationshipType.TIME
        assert rel.join_variables == ["USUBJID"]
        
        # Check that time variables are captured in metadata
        assert "time_vars_source" in rel.metadata
        assert "time_vars_target" in rel.metadata
        
        # Source and target should be LB and VS (in either order)
        domains = {rel.source_domain, rel.target_domain}
        assert domains == {str(DomainType.LABORATORY), str(DomainType.VITAL_SIGNS)}
    
    def test_create_relationship_graph(self, domain_data_map):
        """Test creating a complete relationship graph."""
        service = RelationshipAnalysisService()
        
        # Mock the domain registry for time relationships
        service.domain_registry.get_domain = lambda dt: type('MockDomain', (), {
            'date_variables': ['LBDTC'] if dt == DomainType.LABORATORY else 
                             ['VSDTC'] if dt == DomainType.VITAL_SIGNS else []
        })
        
        # Create the relationship graph
        graph = service.create_relationship_graph(domain_data_map)
        
        # Check the graph properties
        assert len(graph.domains) == 3
        assert set(graph.domains) == {str(DomainType.DEMOGRAPHICS), 
                                     str(DomainType.LABORATORY),
                                     str(DomainType.VITAL_SIGNS)}
        
        # Should have subject, visit, and time relationships
        assert len(graph.get_relationships_by_type(RelationshipType.SUBJECT)) == 3
        assert len(graph.get_relationships_by_type(RelationshipType.VISIT)) == 1
        assert len(graph.get_relationships_by_type(RelationshipType.TIME)) == 1
        
        # Check relationships for each domain
        dm_rels = graph.get_relationships_for_domain(str(DomainType.DEMOGRAPHICS))
        assert len(dm_rels) == 2  # Subject relationships with LB and VS
        
        lb_rels = graph.get_relationships_for_domain(str(DomainType.LABORATORY))
        assert len(lb_rels) >= 3  # Subject with DM, visit and time with VS
        
        vs_rels = graph.get_relationships_for_domain(str(DomainType.VITAL_SIGNS))
        assert len(vs_rels) >= 3  # Subject with DM, visit and time with LB
    
    def test_get_subject_ids(self, domain_data_map):
        """Test extracting subject IDs from domain data."""
        service = RelationshipAnalysisService()
        
        dm_data = domain_data_map[DomainType.DEMOGRAPHICS]
        subject_ids = service._get_subject_ids(dm_data)
        
        assert subject_ids == {"SUBJ001", "SUBJ002", "SUBJ003"}
    
    def test_analyze_relationship_strength(self, domain_data_map):
        """Test analyzing relationship strength."""
        service = RelationshipAnalysisService()
        
        # Test subject relationship strength
        subject_rel = SubjectRelationship(
            source_domain=str(DomainType.DEMOGRAPHICS),
            target_domain=str(DomainType.LABORATORY)
        )
        
        strength = service.analyze_relationship_strength(domain_data_map, subject_rel)
        assert strength == RelationshipStrength.STRONG  # All subjects are shared
        
        # Test visit relationship strength
        visit_rel = VisitRelationship(
            source_domain=str(DomainType.LABORATORY),
            target_domain=str(DomainType.VITAL_SIGNS),
            visit_vars=["VISITNUM", "VISIT"]
        )
        
        strength = service.analyze_relationship_strength(domain_data_map, visit_rel)
        assert strength in [RelationshipStrength.STRONG, RelationshipStrength.MODERATE]  # Most visits are shared
