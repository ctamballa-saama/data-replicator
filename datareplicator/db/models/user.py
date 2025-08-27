"""
User model for DataReplicator.

This module provides the SQLAlchemy ORM model for user data.
"""
import uuid
from datetime import datetime
from typing import List, Optional
from sqlalchemy import Column, String, Boolean, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from datareplicator.db.connection import Base


class User(Base):
    """User model for authentication and authorization."""
    
    __tablename__ = "users"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String, unique=True, index=True, nullable=False)
    username = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    full_name = Column(String)
    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    domains = relationship("Domain", back_populates="owner", cascade="all, delete-orphan")
    jobs = relationship("Job", back_populates="owner", cascade="all, delete-orphan")
    exports = relationship("Export", back_populates="owner", cascade="all, delete-orphan")
    
    def __repr__(self) -> str:
        """String representation of the User model."""
        return f"<User {self.username} ({self.email})>"
