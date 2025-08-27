"""
Job model for DataReplicator.

This module provides the SQLAlchemy ORM model for data generation jobs.
"""
import uuid
from datetime import datetime
from typing import List, Optional, Dict, Any
from sqlalchemy import Column, String, Integer, Float, DateTime, ForeignKey, Text, Boolean
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from sqlalchemy.ext.mutable import MutableDict

from datareplicator.db.connection import Base


class Job(Base):
    """Job model for data generation tasks."""
    
    __tablename__ = "jobs"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    job_id = Column(String, nullable=False, unique=True, index=True)  # Custom job ID (e.g., gen_Demographics_random)
    
    # Job information
    name = Column(String)
    description = Column(String)
    
    # Job configuration
    domain_name = Column(String, nullable=False, index=True)
    generation_mode = Column(String, nullable=False)  # random, statistical, etc.
    record_count = Column(Integer, default=100)
    preserve_relationships = Column(Boolean, default=True)
    
    # Job configuration details (stored as JSON)
    config = Column(MutableDict.as_mutable(JSONB), default=dict)
    
    # Job status
    status = Column(String, default="pending")  # pending, running, completed, failed
    progress = Column(Float, default=0.0)
    quality_score = Column(Float)
    error_message = Column(Text)
    
    # Result information
    result_file = Column(String)  # Path to the generated file
    result_summary = Column(MutableDict.as_mutable(JSONB), default=dict)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    started_at = Column(DateTime)
    completed_at = Column(DateTime)
    
    # Relationships
    domain_id = Column(UUID(as_uuid=True), ForeignKey("domains.id"))
    domain = relationship("Domain", back_populates="jobs")
    owner_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    owner = relationship("User", back_populates="jobs")
    
    def __repr__(self) -> str:
        """String representation of the Job model."""
        return f"<Job {self.job_id} ({self.domain_name}, {self.status})>"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the job to a dictionary."""
        return {
            "id": str(self.id),
            "job_id": self.job_id,
            "name": self.name,
            "description": self.description,
            "domain_name": self.domain_name,
            "generation_mode": self.generation_mode,
            "record_count": self.record_count,
            "preserve_relationships": self.preserve_relationships,
            "config": self.config,
            "status": self.status,
            "progress": self.progress,
            "quality_score": self.quality_score,
            "error_message": self.error_message,
            "result_file": self.result_file,
            "result_summary": self.result_summary,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "domain_id": str(self.domain_id) if self.domain_id else None,
            "owner_id": str(self.owner_id) if self.owner_id else None
        }
    
    def update_status(self, status: str, error_message: Optional[str] = None) -> None:
        """
        Update the job status.
        
        Args:
            status: New status
            error_message: Optional error message for failed jobs
        """
        self.status = status
        if error_message:
            self.error_message = error_message
        
        # Update timestamps based on status
        now = datetime.utcnow()
        if status == "running" and not self.started_at:
            self.started_at = now
        elif status in ["completed", "failed"]:
            self.completed_at = now
        
        # Update progress for completed jobs
        if status == "completed":
            self.progress = 100.0
