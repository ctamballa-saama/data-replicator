"""
DataSource model for DataReplicator.

This module provides the SQLAlchemy ORM model for data sources.
"""
import uuid
from datetime import datetime
from typing import List, Optional, Dict, Any
from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, Text, Boolean
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from sqlalchemy.ext.mutable import MutableDict

from datareplicator.db.connection import Base


class DataSource(Base):
    """DataSource model for tracking data sources."""
    
    __tablename__ = "data_sources"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Source information
    name = Column(String, nullable=False)
    description = Column(String)
    type = Column(String, nullable=False)  # file, database, API, etc.
    
    # Connection information (stored as JSON, potentially encrypted)
    connection_info = Column(MutableDict.as_mutable(JSONB), default=dict)
    
    # Status and metadata
    is_active = Column(Boolean, default=True)
    last_accessed = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Additional metadata (stored as JSON)
    metadata = Column(MutableDict.as_mutable(JSONB), default=dict)
    
    # For file sources
    file_path = Column(String)
    file_format = Column(String)  # csv, json, xml, sas, etc.
    file_size = Column(Integer)  # Size in bytes
    
    # For database sources
    database_type = Column(String)  # postgresql, mysql, oracle, etc.
    table_name = Column(String)
    
    # Owner
    owner_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    
    def __repr__(self) -> str:
        """String representation of the DataSource model."""
        return f"<DataSource {self.name} ({self.type})>"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the data source to a dictionary."""
        return {
            "id": str(self.id),
            "name": self.name,
            "description": self.description,
            "type": self.type,
            "connection_info": {k: v for k, v in self.connection_info.items() if k != "password"},  # Exclude sensitive info
            "is_active": self.is_active,
            "last_accessed": self.last_accessed.isoformat() if self.last_accessed else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "metadata": self.metadata,
            "file_path": self.file_path,
            "file_format": self.file_format,
            "file_size": self.file_size,
            "database_type": self.database_type,
            "table_name": self.table_name,
            "owner_id": str(self.owner_id) if self.owner_id else None
        }
