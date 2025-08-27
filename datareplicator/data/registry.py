"""
Adapter module to expose domain registry to the FastAPI app.
"""
from datareplicator.domain_registry.service import domain_registry

# Re-export domain_registry for compatibility
domain_registry = domain_registry
