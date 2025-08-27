"""
Tests for the configuration module.
"""
import os
import pytest
from pathlib import Path
from unittest.mock import patch

from datareplicator.core.config.settings import Settings, get_settings
from datareplicator.core.config.constants import DomainType, ValidationSeverity, UserRole
from datareplicator.core.config import settings


class TestSettings:
    """Test cases for settings module."""
    
    def test_default_settings(self):
        """Test default settings values."""
        s = Settings()
        assert s.APP_NAME == "DataReplicator"
        assert s.API_HOST == "127.0.0.1"
        assert s.API_PORT == 8000
        assert s.DATABASE_URL == "sqlite:///datareplicator.db"
        assert s.DEFAULT_TARGET_SUBJECTS == 100
    
    def test_env_override(self):
        """Test environment variable overrides."""
        with patch.dict(os.environ, {"APP_NAME": "TestApp", "API_PORT": "9000", "DEBUG": "True"}):
            s = Settings()
            assert s.APP_NAME == "TestApp"
            assert s.API_PORT == 9000
            assert s.DEBUG is True
    
    def test_directory_creation(self):
        """Test directory creation for paths."""
        test_upload_dir = Path("./test_uploads")
        test_output_dir = Path("./test_output")
        
        try:
            with patch.dict(os.environ, {
                "UPLOAD_DIR": str(test_upload_dir),
                "OUTPUT_DIR": str(test_output_dir)
            }):
                s = Settings()
                assert s.UPLOAD_DIR.exists()
                assert s.OUTPUT_DIR.exists()
        finally:
            # Clean up test directories
            if test_upload_dir.exists():
                test_upload_dir.rmdir()
            if test_output_dir.exists():
                test_output_dir.rmdir()
    
    def test_settings_singleton(self):
        """Test that the settings singleton is working."""
        assert settings is not None
        assert settings.APP_NAME == "DataReplicator"
        # Make sure we get the same instance
        assert id(settings) == id(get_settings())


class TestConstants:
    """Test cases for constants module."""
    
    def test_domain_type_enum(self):
        """Test DomainType enum values."""
        assert DomainType.DEMOGRAPHICS == "DM"
        assert DomainType.LABORATORY == "LB"
        assert DomainType.VITAL_SIGNS == "VS"
        
        # Test string comparison works
        assert DomainType.DEMOGRAPHICS == "DM"
        assert "DM" == DomainType.DEMOGRAPHICS
    
    def test_validation_severity_enum(self):
        """Test ValidationSeverity enum values."""
        assert ValidationSeverity.ERROR == "ERROR"
        assert ValidationSeverity.WARNING == "WARNING"
        assert ValidationSeverity.INFO == "INFO"
    
    def test_user_role_enum(self):
        """Test UserRole enum values."""
        assert UserRole.ADMIN == "admin"
        assert UserRole.USER == "user"
        assert UserRole.VIEWER == "viewer"
