"""
Data domain models for the DataReplicator application.

These models represent clinical data domains and their properties.
"""
from pathlib import Path
from typing import Dict, List, Optional, Any, Set, ClassVar

from pydantic import BaseModel, Field

from datareplicator.core.config import DomainType, constants
from datareplicator.data.models import DomainData, DataColumn


class DataDomain(BaseModel):
    """
    Base class representing a clinical data domain.
    
    Encapsulates domain-specific metadata and processing rules.
    """
    domain_type: DomainType
    domain_name: str
    description: str
    key_variables: List[str]
    required_variables: List[str]
    date_variables: List[str] = Field(default_factory=list)
    categorical_variables: Dict[str, List[str]] = Field(default_factory=dict)
    variable_metadata: Dict[str, DataColumn] = Field(default_factory=dict)
    
    # Class variables for domain registration
    _domain_classes: ClassVar[Dict[DomainType, "DataDomain"]] = {}
    
    class Config:
        """Pydantic configuration for DataDomain."""
        arbitrary_types_allowed = True
    
    @classmethod
    def register(cls, domain_class: "DataDomain"):
        """
        Register a domain class in the domain registry.
        
        Args:
            domain_class: Domain class to register
        """
        cls._domain_classes[domain_class.domain_type] = domain_class
    
    @classmethod
    def get_domain_class(cls, domain_type: DomainType) -> Optional["DataDomain"]:
        """
        Get a domain class by domain type.
        
        Args:
            domain_type: Domain type to look up
            
        Returns:
            DataDomain subclass or None if not found
        """
        return cls._domain_classes.get(domain_type)
    
    def validate_data(self, data: DomainData) -> List[Dict[str, Any]]:
        """
        Validate domain-specific data.
        
        Args:
            data: Domain data to validate
            
        Returns:
            List of validation errors
        """
        errors = []
        
        # Check domain type matches
        if data.domain_type != self.domain_type:
            errors.append({
                "error_type": "DomainTypeMismatch",
                "message": f"Domain type mismatch: expected {self.domain_type}, got {data.domain_type}"
            })
        
        # Check required variables
        for var in self.required_variables:
            if var not in data.columns:
                errors.append({
                    "error_type": "MissingRequiredVariable",
                    "message": f"Required variable {var} is missing"
                })
        
        return errors
    
    def get_subject_data(self, data: DomainData) -> Dict[str, List[Dict[str, Any]]]:
        """
        Organize data by subject.
        
        Args:
            data: Domain data to organize
            
        Returns:
            Dict mapping subject IDs to lists of records
        """
        result = {}
        
        # Check if USUBJID is present
        if constants.USUBJID_VAR not in data.columns:
            return result
        
        # Group records by USUBJID
        for record in data.data:
            usubjid = record.get(constants.USUBJID_VAR)
            if usubjid:
                if usubjid not in result:
                    result[usubjid] = []
                result[usubjid].append(record)
        
        return result


class DemographicsDomain(DataDomain):
    """Demographics (DM) domain implementation."""
    
    def __init__(self):
        """Initialize demographics domain."""
        super().__init__(
            domain_type=DomainType.DEMOGRAPHICS,
            domain_name="Demographics",
            description="Subject demographics and characteristics",
            key_variables=[constants.USUBJID_VAR],
            required_variables=[
                constants.USUBJID_VAR, 
                constants.SUBJID_VAR, 
                constants.STUDYID_VAR, 
                constants.DOMAIN_VAR,
                "SEX", 
                "AGE"
            ],
            date_variables=["RFSTDTC", "RFENDTC", "DTHDTC"],
            categorical_variables={
                "SEX": ["M", "F", "U", "UNDIFFERENTIATED"],
                "RACE": [
                    "WHITE", 
                    "BLACK OR AFRICAN AMERICAN", 
                    "ASIAN", 
                    "AMERICAN INDIAN OR ALASKA NATIVE",
                    "NATIVE HAWAIIAN OR OTHER PACIFIC ISLANDER", 
                    "OTHER", 
                    "UNKNOWN", 
                    "NOT REPORTED"
                ],
                "ETHNIC": ["HISPANIC OR LATINO", "NOT HISPANIC OR LATINO", "UNKNOWN", "NOT REPORTED"]
            }
        )
    
    def validate_data(self, data: DomainData) -> List[Dict[str, Any]]:
        """
        Validate demographics data with domain-specific rules.
        
        Args:
            data: Demographics data to validate
            
        Returns:
            List of validation errors
        """
        errors = super().validate_data(data)
        
        # Demographics should have one record per subject
        if constants.USUBJID_VAR in data.columns:
            # Get all USUBJIDs
            usubjids = [row.get(constants.USUBJID_VAR) for row in data.data]
            # Check for duplicates
            if len(usubjids) != len(set(usubjids)):
                errors.append({
                    "error_type": "DuplicateSubjects",
                    "message": "Demographics domain should have only one record per subject"
                })
        
        return errors


class LaboratoryDomain(DataDomain):
    """Laboratory Results (LB) domain implementation."""
    
    def __init__(self):
        """Initialize laboratory domain."""
        super().__init__(
            domain_type=DomainType.LABORATORY,
            domain_name="Laboratory Results",
            description="Laboratory test results",
            key_variables=[constants.USUBJID_VAR, "LBSEQ"],
            required_variables=[
                constants.USUBJID_VAR, 
                constants.STUDYID_VAR, 
                constants.DOMAIN_VAR,
                "LBSEQ", 
                "LBTESTCD", 
                "LBTEST", 
                "LBORRES"
            ],
            date_variables=["LBDTC"],
            categorical_variables={
                "LBCAT": [
                    "CHEMISTRY", 
                    "HEMATOLOGY", 
                    "URINALYSIS", 
                    "COAGULATION",
                    "SEROLOGY", 
                    "MICROBIOLOGY", 
                    "IMMUNOLOGY"
                ],
                "LBBLFL": ["Y", "N"]
            }
        )


class VitalSignsDomain(DataDomain):
    """Vital Signs (VS) domain implementation."""
    
    def __init__(self):
        """Initialize vital signs domain."""
        super().__init__(
            domain_type=DomainType.VITAL_SIGNS,
            domain_name="Vital Signs",
            description="Vital signs measurements",
            key_variables=[constants.USUBJID_VAR, "VSSEQ"],
            required_variables=[
                constants.USUBJID_VAR, 
                constants.STUDYID_VAR, 
                constants.DOMAIN_VAR,
                "VSSEQ", 
                "VSTESTCD", 
                "VSTEST", 
                "VSORRES"
            ],
            date_variables=["VSDTC"],
            categorical_variables={
                "VSTESTCD": ["SYSBP", "DIABP", "PULSE", "TEMP", "RESP", "HEIGHT", "WEIGHT", "BMI"],
                "VSBLFL": ["Y", "N"]
            }
        )
