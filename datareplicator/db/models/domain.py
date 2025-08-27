"""
Domain model for DataReplicator.

This module provides the SQLAlchemy ORM model for domain data.
"""
import uuid
import json
from datetime import datetime
from typing import List, Optional, Dict, Any
from sqlalchemy import Column, String, Integer, Float, DateTime, ForeignKey, Text, Boolean
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from sqlalchemy.ext.mutable import MutableDict

from datareplicator.db.connection import Base


class Domain(Base):
    """Domain model for clinical data domains."""
    
    __tablename__ = "domains"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False, index=True)
    description = Column(String)
    
    # Data statistics
    record_count = Column(Integer, default=0)
    variable_count = Column(Integer, default=0)
    
    # Source information
    source_file = Column(String)
    source_format = Column(String)
    
    # Schema information (stored as JSON)
    schema = Column(MutableDict.as_mutable(JSONB), default=dict)
    
    # Sample data (stored as JSON)
    sample_data = Column(MutableDict.as_mutable(JSONB), default=dict)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_active = Column(Boolean, default=True)
    
    # Relationships
    owner_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    owner = relationship("User", back_populates="domains")
    jobs = relationship("Job", back_populates="domain", cascade="all, delete-orphan")
    exports = relationship("Export", back_populates="domain", cascade="all, delete-orphan")
    
    # Relationships with other domains
    relationships_data = Column(MutableDict.as_mutable(JSONB), default=dict)
    
    def __repr__(self) -> str:
        """String representation of the Domain model."""
        return f"<Domain {self.name} ({self.record_count} records, {self.variable_count} variables)>"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the domain to a dictionary."""
        return {
            "id": str(self.id),
            "name": self.name,
            "description": self.description,
            "record_count": self.record_count,
            "variable_count": self.variable_count,
            "source_file": self.source_file,
            "source_format": self.source_format,
            "schema": self.schema,
            "sample_data": self.sample_data,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "is_active": self.is_active,
            "owner_id": str(self.owner_id) if self.owner_id else None,
            "relationships_data": self.relationships_data
        }
    
    def update_relationships(self, relationships: Dict[str, Any]) -> None:
        """
        Update relationship data for the domain.
        
        Args:
            relationships: Dictionary containing relationship information
        """
        self.relationships_data = relationships
