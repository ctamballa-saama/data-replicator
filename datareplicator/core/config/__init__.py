"""
Configuration package initialization.
Exports key configuration components.
"""
from datareplicator.core.config.constants import (
    DomainType,
    ValidationSeverity,
    UserRole,
    USUBJID_VAR,
    SUBJID_VAR,
    STUDYID_VAR,
    DOMAIN_VAR,
    KEY_VARS,
    REQUIRED_VARS,
    PII_FIELDS,
)
from datareplicator.core.config.settings import Settings, get_settings

# Create a singleton instance of settings
settings = get_settings()

__all__ = [
    "settings",
    "Settings",
    "get_settings",
    "DomainType",
    "ValidationSeverity",
    "UserRole",
    "USUBJID_VAR",
    "SUBJID_VAR", 
    "STUDYID_VAR",
    "DOMAIN_VAR",
    "KEY_VARS",
    "REQUIRED_VARS",
    "PII_FIELDS",
]
