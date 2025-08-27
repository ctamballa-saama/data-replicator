"""
Constants used throughout the DataReplicator application.
"""
from enum import Enum, auto
from typing import Dict, List, Set


class DomainType(str, Enum):
    """
    Enum representing clinical data domains.
    
    Based on CDISC standard domains.
    """
    DEMOGRAPHICS = "DM"  # Demographics
    ADVERSE_EVENTS = "AE"  # Adverse Events
    CONCOMITANT_MEDS = "CM"  # Concomitant Medications
    EXPOSURE = "EX"  # Exposure
    LABORATORY = "LB"  # Laboratory Test Results
    MEDICAL_HISTORY = "MH"  # Medical History
    VITAL_SIGNS = "VS"  # Vital Signs
    QUESTIONNAIRES = "QS"  # Questionnaires
    ECG = "EG"  # ECG Test Results
    SUBJECT_VISITS = "SV"  # Subject Visits
    DISPOSITION = "DS"  # Disposition


class ValidationSeverity(str, Enum):
    """
    Enum representing validation error severity levels.
    """
    ERROR = "ERROR"
    WARNING = "WARNING"
    INFO = "INFO"


class UserRole(str, Enum):
    """
    Enum representing user roles within the application.
    """
    ADMIN = "admin"
    USER = "user"
    VIEWER = "viewer"


# CDISC common variables
USUBJID_VAR = "USUBJID"  # Unique subject identifier
SUBJID_VAR = "SUBJID"    # Subject identifier
STUDYID_VAR = "STUDYID"  # Study identifier
DOMAIN_VAR = "DOMAIN"    # Domain identifier

# Key identifiers for linking domains
KEY_VARS: Dict[str, List[str]] = {
    DomainType.DEMOGRAPHICS: [USUBJID_VAR],
    DomainType.ADVERSE_EVENTS: [USUBJID_VAR, "AESEQ"],
    DomainType.LABORATORY: [USUBJID_VAR, "LBSEQ"],
    DomainType.VITAL_SIGNS: [USUBJID_VAR, "VSSEQ"],
    # Add other domains as needed
}

# Required variables for each domain
REQUIRED_VARS: Dict[str, List[str]] = {
    DomainType.DEMOGRAPHICS: [USUBJID_VAR, SUBJID_VAR, STUDYID_VAR, DOMAIN_VAR, "SEX", "AGE"],
    DomainType.LABORATORY: [USUBJID_VAR, STUDYID_VAR, DOMAIN_VAR, "LBSEQ", "LBTESTCD", "LBTEST", "LBORRES"],
    DomainType.VITAL_SIGNS: [USUBJID_VAR, STUDYID_VAR, DOMAIN_VAR, "VSSEQ", "VSTESTCD", "VSTEST", "VSORRES"],
    # Add other domains as needed
}

# PII fields that should be completely randomized
PII_FIELDS: Set[str] = {
    SUBJID_VAR,  # Subject ID
    "INITIALS",  # Subject initials
    "BIRTHDT",   # Birth date
    "SITEID",    # Site identifier
    "INVID",     # Investigator identifier
    "INVNAM",    # Investigator name
}

# Default file encoding for CSV files
DEFAULT_ENCODING = "utf-8"

# Default delimiter for CSV files
DEFAULT_CSV_DELIMITER = ","
