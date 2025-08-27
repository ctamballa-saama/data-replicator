"""
Adapter module to expose ingestion service to the FastAPI app.
"""
from datareplicator.ingestion.service import ingestion_service

# Re-export ingestion_service for compatibility
ingestion_service = ingestion_service
