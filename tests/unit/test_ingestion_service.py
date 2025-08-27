"""
Unit tests for the data ingestion service.
"""
import os
import pytest
from pathlib import Path
from unittest.mock import MagicMock, patch

from datareplicator.core.config import DomainType
from datareplicator.data.models import DataImportSummary, DomainData, ParseError
from datareplicator.data.ingestion import DataIngestionService


class TestIngestionService:
    """Test cases for the data ingestion service."""
    
    def test_initialization(self):
        """Test service initialization."""
        service = DataIngestionService()
        
        assert service.csv_parser is not None
        assert service.domain_registry is not None
        assert service.domain_factory is not None
        assert service.imported_data == {}
    
    @patch('datareplicator.data.parsing.csv_parser.CSVParser.parse_file')
    def test_ingest_file_success(self, mock_parse_file):
        """Test successful file ingestion."""
        # Set up the mock
        mock_domain_data = DomainData(
            domain_type=DomainType.DEMOGRAPHICS,
            domain_name="Demographics",
            file_path=Path("dummy/path/dm.csv"),
            columns=["STUDYID", "DOMAIN", "USUBJID", "SUBJID", "SEX", "AGE"],
            data=[
                {"USUBJID": "SUBJ001", "SUBJID": "001", "STUDYID": "STUDY1", "DOMAIN": "DM", "SEX": "M", "AGE": 45},
                {"USUBJID": "SUBJ002", "SUBJID": "002", "STUDYID": "STUDY1", "DOMAIN": "DM", "SEX": "F", "AGE": 52}
            ]
        )
        
        mock_summary = DataImportSummary(
            success=True,
            file_path=Path("dummy/path/dm.csv"),
            domain_type=DomainType.DEMOGRAPHICS,
            domain_data=mock_domain_data,
            row_count=2,
            column_count=6,
            subject_count=2,
            error_count=0,
            errors=[]
        )
        
        mock_parse_file.return_value = mock_summary
        
        # Create the service and ingest a file
        service = DataIngestionService()
        summary = service.ingest_file(Path("dummy/path/dm.csv"))
        
        # Verify the results
        assert summary.success is True
        assert summary.domain_type == DomainType.DEMOGRAPHICS
        assert summary.row_count == 2
        assert summary.column_count == 6
        assert summary.subject_count == 2
        assert summary.error_count == 0
        
        # Verify that the data was stored in the service
        assert DomainType.DEMOGRAPHICS in service.imported_data
        assert len(service.imported_data[DomainType.DEMOGRAPHICS].data) == 2
    
    def test_ingest_file_not_found(self):
        """Test ingesting a non-existent file."""
        service = DataIngestionService()
        summary = service.ingest_file(Path("/non/existent/file.csv"))
        
        assert summary.success is False
        assert summary.error_count == 1
        assert summary.errors[0]["error_type"] == "FileNotFoundError"
    
    @patch('datareplicator.data.ingestion.ingestion_service.DataIngestionService.ingest_file')
    def test_ingest_directory(self, mock_ingest_file):
        """Test ingesting all files in a directory."""
        # Set up mocks
        mock_summaries = {
            "dm.csv": DataImportSummary(
                success=True,
                file_path=Path("dummy/path/dm.csv"),
                domain_type=DomainType.DEMOGRAPHICS,
                row_count=2,
                column_count=6,
                subject_count=2,
                error_count=0,
                errors=[]
            ),
            "lb.csv": DataImportSummary(
                success=True,
                file_path=Path("dummy/path/lb.csv"),
                domain_type=DomainType.LABORATORY,
                row_count=10,
                column_count=8,
                subject_count=2,
                error_count=0,
                errors=[]
            )
        }
        
        # Configure mock to return different summaries based on file path
        def mock_ingest_side_effect(file_path):
            return mock_summaries.get(file_path.name)
        
        mock_ingest_file.side_effect = mock_ingest_side_effect
        
        # Test with a real directory path but mock the file ingestion
        project_root = Path(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))
        data_dir = project_root / "data" / "sample"
        
        # Create the service and ingest the directory
        service = DataIngestionService()
        
        # Patch glob to return our test files
        with patch('pathlib.Path.glob', return_value=[data_dir / "dm.csv", data_dir / "lb.csv"]):
            with patch('pathlib.Path.exists', return_value=True):
                with patch('pathlib.Path.is_dir', return_value=True):
                    results = service.ingest_directory(data_dir)
        
        # Verify the results
        assert len(results) == 2
        assert "dm.csv" in results
        assert "lb.csv" in results
        assert results["dm.csv"].success is True
        assert results["lb.csv"].success is True
    
    def test_get_imported_domains(self):
        """Test getting a list of imported domains."""
        # Create a service with some mock data
        service = DataIngestionService()
        service.imported_data = {
            DomainType.DEMOGRAPHICS: DomainData(
                domain_type=DomainType.DEMOGRAPHICS,
                domain_name="Demographics",
                file_path=Path("dummy/path"),
                columns=[],
                data=[]
            ),
            DomainType.LABORATORY: DomainData(
                domain_type=DomainType.LABORATORY,
                domain_name="Laboratory",
                file_path=Path("dummy/path"),
                columns=[],
                data=[]
            )
        }
        
        # Get the imported domains
        domains = service.get_imported_domains()
        
        assert len(domains) == 2
        assert "DM" in domains
        assert "LB" in domains
    
    def test_get_subject_ids(self):
        """Test getting all unique subject IDs."""
        # Create a service with some mock data
        service = DataIngestionService()
        
        # Add demographics data
        service.imported_data[DomainType.DEMOGRAPHICS] = DomainData(
            domain_type=DomainType.DEMOGRAPHICS,
            domain_name="Demographics",
            file_path=Path("dummy/path"),
            columns=["USUBJID", "SEX", "AGE"],
            data=[
                {"USUBJID": "SUBJ001", "SEX": "M", "AGE": 45},
                {"USUBJID": "SUBJ002", "SEX": "F", "AGE": 52}
            ]
        )
        
        # Add laboratory data
        service.imported_data[DomainType.LABORATORY] = DomainData(
            domain_type=DomainType.LABORATORY,
            domain_name="Laboratory",
            file_path=Path("dummy/path"),
            columns=["USUBJID", "LBTESTCD", "LBORRES"],
            data=[
                {"USUBJID": "SUBJ001", "LBTESTCD": "GLUC", "LBORRES": "5.2"},
                {"USUBJID": "SUBJ002", "LBTESTCD": "GLUC", "LBORRES": "4.8"},
                {"USUBJID": "SUBJ003", "LBTESTCD": "GLUC", "LBORRES": "5.0"}
            ]
        )
        
        # Get the subject IDs
        subject_ids = service.get_subject_ids()
        
        assert len(subject_ids) == 3
        assert "SUBJ001" in subject_ids
        assert "SUBJ002" in subject_ids
        assert "SUBJ003" in subject_ids
    
    def test_get_data_overview(self):
        """Test getting an overview of imported data."""
        # Create a service with some mock data
        service = DataIngestionService()
        
        # Add demographics data
        service.imported_data[DomainType.DEMOGRAPHICS] = DomainData(
            domain_type=DomainType.DEMOGRAPHICS,
            domain_name="Demographics",
            file_path=Path("dummy/path"),
            columns=["USUBJID", "SEX", "AGE", "VISITNUM"],
            data=[
                {"USUBJID": "SUBJ001", "SEX": "M", "AGE": 45, "VISITNUM": 1},
                {"USUBJID": "SUBJ002", "SEX": "F", "AGE": 52, "VISITNUM": 1}
            ]
        )
        
        # Add laboratory data
        service.imported_data[DomainType.LABORATORY] = DomainData(
            domain_type=DomainType.LABORATORY,
            domain_name="Laboratory",
            file_path=Path("dummy/path"),
            columns=["USUBJID", "LBTESTCD", "LBORRES", "VISITNUM", "LBDTC"],
            data=[
                {"USUBJID": "SUBJ001", "LBTESTCD": "GLUC", "LBORRES": "5.2", "VISITNUM": 1, "LBDTC": "2023-01-01"},
                {"USUBJID": "SUBJ002", "LBTESTCD": "GLUC", "LBORRES": "4.8", "VISITNUM": 1, "LBDTC": "2023-01-01"},
                {"USUBJID": "SUBJ003", "LBTESTCD": "GLUC", "LBORRES": "5.0", "VISITNUM": 1, "LBDTC": "2023-01-02"}
            ]
        )
        
        # Get the data overview
        overview = service.get_data_overview()
        
        # Verify the overview
        assert overview["domain_count"] == 2
        assert "DM" in overview["domains"]
        assert "LB" in overview["domains"]
        assert overview["subject_count"] == 3
        assert overview["total_records"] == 5
        assert "domain_details" in overview
        assert "DM" in overview["domain_details"]
        assert "LB" in overview["domain_details"]
        assert overview["domain_details"]["DM"]["record_count"] == 2
        assert overview["domain_details"]["LB"]["record_count"] == 3
        assert "relationships" in overview
        assert "subject_level" in overview["relationships"]
        assert "visit_level" in overview["relationships"]
        assert "time_based" in overview["relationships"]
