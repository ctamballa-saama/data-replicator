"""
Database connection management for DataReplicator.

This module provides SQLAlchemy connection management and session handling.
"""
import os
import logging
from typing import Generator

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session

from datareplicator.config.settings import settings

# Configure logging
logger = logging.getLogger(__name__)

# Create Base class for declarative models
Base = declarative_base()

# Create engine based on configuration
def get_engine(echo: bool = False):
    """
    Create a SQLAlchemy engine using the application settings.
    
    Args:
        echo: Whether to echo SQL statements
        
    Returns:
        SQLAlchemy engine
    """
    # Get database URL from settings
    database_url = os.environ.get(
        "DATABASE_URL", 
        settings.database_url or "sqlite:///./data/datareplicator.db"
    )
    
    # Create directory for SQLite database if needed
    if database_url.startswith("sqlite"):
        db_path = database_url.split("sqlite:///")[1]
        db_dir = os.path.dirname(os.path.abspath(db_path))
        os.makedirs(db_dir, exist_ok=True)
    
    # Create engine
    logger.info(f"Creating database engine with URL: {database_url}")
    return create_engine(
        database_url, 
        echo=echo,
        # For SQLite, enable foreign keys
        connect_args={"check_same_thread": False} if database_url.startswith("sqlite") else {}
    )

# Session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False)


def init_db(engine):
    """
    Initialize the database connection.
    
    Args:
        engine: SQLAlchemy engine
    """
    SessionLocal.configure(bind=engine)


def get_session() -> Generator[Session, None, None]:
    """
    Get a database session.
    
    Yields:
        Database session
    """
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()


def create_db_and_tables():
    """Create all database tables."""
    engine = get_engine()
    init_db(engine)
    Base.metadata.create_all(bind=engine)
    logger.info("Created database tables")
