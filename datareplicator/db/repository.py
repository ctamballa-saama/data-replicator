"""
Repository pattern implementation for DataReplicator.

This module provides a repository pattern for database operations.
"""
import logging
from typing import Generic, TypeVar, Type, List, Optional, Dict, Any, Union
from abc import ABC, abstractmethod

from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from pydantic import BaseModel

from datareplicator.db.connection import Base

# Configure logging
logger = logging.getLogger(__name__)

# Generic type for ORM models
T = TypeVar('T', bound=Base)

# Generic type for Pydantic schemas
P = TypeVar('P', bound=BaseModel)


class Repository(Generic[T, P], ABC):
    """Abstract base repository interface."""
    
    @abstractmethod
    def create(self, obj_in: Union[P, Dict[str, Any]]) -> T:
        """Create a new record."""
        pass
    
    @abstractmethod
    def get(self, id: Any) -> Optional[T]:
        """Get a record by ID."""
        pass
    
    @abstractmethod
    def get_by_attribute(self, attr_name: str, attr_value: Any) -> List[T]:
        """Get records by attribute."""
        pass
    
    @abstractmethod
    def list(self, skip: int = 0, limit: int = 100) -> List[T]:
        """List records."""
        pass
    
    @abstractmethod
    def update(self, id: Any, obj_in: Union[P, Dict[str, Any]]) -> Optional[T]:
        """Update a record."""
        pass
    
    @abstractmethod
    def delete(self, id: Any) -> bool:
        """Delete a record."""
        pass


class SQLAlchemyRepository(Repository[T, P], Generic[T, P]):
    """SQLAlchemy implementation of the Repository interface."""
    
    def __init__(self, model: Type[T], schema: Type[P], session: Session):
        """
        Initialize the repository.
        
        Args:
            model: SQLAlchemy model class
            schema: Pydantic schema class
            session: SQLAlchemy session
        """
        self.model = model
        self.schema = schema
        self.session = session
    
    def create(self, obj_in: Union[P, Dict[str, Any]]) -> T:
        """
        Create a new record.
        
        Args:
            obj_in: Input object (Pydantic model or dictionary)
            
        Returns:
            Created ORM model instance
        """
        try:
            # Convert to dictionary if Pydantic model
            if isinstance(obj_in, BaseModel):
                obj_data = obj_in.dict(exclude_unset=True)
            else:
                obj_data = obj_in
            
            # Create model instance
            db_obj = self.model(**obj_data)
            
            # Add to session and commit
            self.session.add(db_obj)
            self.session.commit()
            self.session.refresh(db_obj)
            
            return db_obj
        except SQLAlchemyError as e:
            self.session.rollback()
            logger.error(f"Error creating {self.model.__name__}: {str(e)}")
            raise
    
    def get(self, id: Any) -> Optional[T]:
        """
        Get a record by ID.
        
        Args:
            id: Record ID
            
        Returns:
            ORM model instance if found, None otherwise
        """
        return self.session.query(self.model).filter(self.model.id == id).first()
    
    def get_by_attribute(self, attr_name: str, attr_value: Any) -> List[T]:
        """
        Get records by attribute.
        
        Args:
            attr_name: Attribute name
            attr_value: Attribute value
            
        Returns:
            List of ORM model instances
        """
        return self.session.query(self.model).filter(
            getattr(self.model, attr_name) == attr_value
        ).all()
    
    def list(self, skip: int = 0, limit: int = 100) -> List[T]:
        """
        List records.
        
        Args:
            skip: Number of records to skip
            limit: Maximum number of records to return
            
        Returns:
            List of ORM model instances
        """
        return self.session.query(self.model).offset(skip).limit(limit).all()
    
    def update(self, id: Any, obj_in: Union[P, Dict[str, Any]]) -> Optional[T]:
        """
        Update a record.
        
        Args:
            id: Record ID
            obj_in: Input object (Pydantic model or dictionary)
            
        Returns:
            Updated ORM model instance if found, None otherwise
        """
        try:
            db_obj = self.session.query(self.model).filter(self.model.id == id).first()
            if not db_obj:
                return None
            
            # Convert to dictionary if Pydantic model
            if isinstance(obj_in, BaseModel):
                update_data = obj_in.dict(exclude_unset=True)
            else:
                update_data = obj_in
            
            # Update attributes
            for key, value in update_data.items():
                if hasattr(db_obj, key):
                    setattr(db_obj, key, value)
            
            # Commit changes
            self.session.commit()
            self.session.refresh(db_obj)
            
            return db_obj
        except SQLAlchemyError as e:
            self.session.rollback()
            logger.error(f"Error updating {self.model.__name__} with ID {id}: {str(e)}")
            raise
    
    def delete(self, id: Any) -> bool:
        """
        Delete a record.
        
        Args:
            id: Record ID
            
        Returns:
            True if deleted, False if not found
        """
        try:
            db_obj = self.session.query(self.model).filter(self.model.id == id).first()
            if not db_obj:
                return False
            
            # Delete the object
            self.session.delete(db_obj)
            self.session.commit()
            
            return True
        except SQLAlchemyError as e:
            self.session.rollback()
            logger.error(f"Error deleting {self.model.__name__} with ID {id}: {str(e)}")
            raise
