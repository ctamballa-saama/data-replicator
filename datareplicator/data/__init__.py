"""
Data package initialization.

Exports data models, parsing, and domain management components.
"""
from datareplicator.data.models import (
    DataColumn,
    ParseError,
    DomainData,
    DataImportSummary,
)
from datareplicator.data.parsing import CSVParser
from datareplicator.data.domain import (
    DataDomain,
    DomainRegistry,
    domain_registry,
    DomainFactory,
    domain_factory,
)
from datareplicator.data.ingestion import DataIngestionService, ingestion_service

__all__ = [
    "DataColumn",
    "ParseError",
    "DomainData",
    "DataImportSummary",
    "CSVParser",
    "DataDomain",
    "DomainRegistry",
    "domain_registry",
    "DomainFactory",
    "domain_factory",
    "DataIngestionService",
    "ingestion_service",
]