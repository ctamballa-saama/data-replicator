"""
Export model for DataReplicator.

This module provides the SQLAlchemy ORM model for data exports.
"""
import uuid
from datetime import datetime
from typing import List, Optional, Dict, Any
from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, Text, Boolean
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from sqlalchemy.ext.mutable import MutableDict

from datareplicator.db.connection import Base


class Export(Base):
    """Export model for tracking data exports."""
    
    __tablename__ = "exports"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Export information
    name = Column(String)
    description = Column(String)
    format = Column(String, nullable=False)  # csv, json, xml, etc.
    
    # File information
    file_path = Column(String)
    file_name = Column(String)
    file_size = Column(Integer)  # Size in bytes
    
    # Data information
    record_count = Column(Integer)
    
    # Export configuration (stored as JSON)
    config = Column(MutableDict.as_mutable(JSONB), default=dict)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    is_public = Column(Boolean, default=False)
    
    # Relationships
    domain_id = Column(UUID(as_uuid=True), ForeignKey("domains.id"))
    domain = relationship("Domain", back_populates="exports")
    owner_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    owner = relationship("User", back_populates="exports")
    
    def __repr__(self) -> str:
        """String representation of the Export model."""
        return f"<Export {self.name} ({self.format}, {self.record_count} records)>"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the export to a dictionary."""
        return {
            "id": str(self.id),
            "name": self.name,
            "description": self.description,
            "format": self.format,
            "file_path": self.file_path,
            "file_name": self.file_name,
            "file_size": self.file_size,
            "record_count": self.record_count,
            "config": self.config,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "is_public": self.is_public,
            "domain_id": str(self.domain_id) if self.domain_id else None,
            "owner_id": str(self.owner_id) if self.owner_id else None
        }
