import os
import sys
import pytest


def test_project_structure():
    """Test that the project directory structure exists."""
    # Get the project root directory
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
    
    # Define expected directories
    expected_dirs = [
        "datareplicator",
        "datareplicator/core",
        "datareplicator/data",
        "datareplicator/analysis",
        "datareplicator/generation",
        "datareplicator/validation",
        "datareplicator/export",
        "datareplicator/api",
        "datareplicator/ui",
    ]
    
    # Check if directories exist
    for dir_path in expected_dirs:
        full_path = os.path.join(project_root, dir_path)
        assert os.path.isdir(full_path), f"Directory {dir_path} does not exist"
        
        # Check for __init__.py in each package directory
        init_file = os.path.join(full_path, "__init__.py")
        assert os.path.isfile(init_file), f"__init__.py missing in {dir_path}"


def test_project_import():
    """Test that the datareplicator package can be imported."""
    try:
        import datareplicator
        assert True
    except ImportError:
        assert False, "Failed to import datareplicator package"
