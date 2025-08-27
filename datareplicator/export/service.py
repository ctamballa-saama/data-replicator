"""
Data export service for DataReplicator.

This module provides functionality for exporting data in various formats.
"""
import os
import logging
import pandas as pd
import numpy as np
import json
import datetime
from typing import Dict, List, Any, Optional, Union, BinaryIO, TextIO
import xml.etree.ElementTree as ET
import xml.dom.minidom

from datareplicator.export.models import ExportConfig, ExportResult, ExportMetadata, ExportFormat
from datareplicator.data.registry import domain_registry

# Configure logging
logger = logging.getLogger(__name__)


class ExportService:
    """Service for exporting data in various formats."""
    
    def __init__(self, export_dir: str = "exported_data"):
        """
        Initialize the export service.
        
        Args:
            export_dir: Directory to store exported files
        """
        self.export_dir = export_dir
        
        # Create export directory if it doesn't exist
        os.makedirs(self.export_dir, exist_ok=True)
    
    def export_domain(self, config: ExportConfig) -> ExportResult:
        """
        Export a domain according to the specified configuration.
        
        Args:
            config: Export configuration
            
        Returns:
            Result of the export operation
        """
        try:
            # Get the domain data
            domain_name = config.domain_name
            if not domain_registry.has_domain(domain_name):
                return ExportResult(
                    success=False,
                    format=config.format,
                    domain_name=domain_name,
                    error_message=f"Domain '{domain_name}' not found"
                )
            
            domain = domain_registry.get_domain(domain_name)
            data = domain.data
            
            # Apply field selection if specified
            if config.fields:
                # Get intersection of requested fields and available columns
                available_fields = [f for f in config.fields if f in data.columns]
                if not available_fields:
                    return ExportResult(
                        success=False,
                        format=config.format,
                        domain_name=domain_name,
                        error_message=f"None of the requested fields exist in domain '{domain_name}'"
                    )
                data = data[available_fields]
            
            # Apply filter if specified
            if config.filter_query:
                try:
                    data = data.query(config.filter_query)
                except Exception as e:
                    return ExportResult(
                        success=False,
                        format=config.format,
                        domain_name=domain_name,
                        error_message=f"Filter query error: {str(e)}"
                    )
            
            # Apply column mappings if specified
            if config.column_mappings:
                data = data.rename(columns={
                    k: v for k, v in config.column_mappings.items() if k in data.columns
                })
            
            # Create metadata
            metadata = ExportMetadata(
                created_at=datetime.datetime.now().isoformat(),
                source_domain=domain_name,
                record_count=len(data),
                format=config.format
            )
            
            # Generate file name if not provided
            if not config.file_name:
                timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
                extension = self._get_extension(config.format)
                file_name = f"{domain_name}_export_{timestamp}{extension}"
            else:
                file_name = config.file_name
                
                # Add extension if not present
                if not any(file_name.endswith(ext) for ext in ['.csv', '.json', '.xml', '.sas7bdat', '.xlsx']):
                    extension = self._get_extension(config.format)
                    file_name = f"{file_name}{extension}"
            
            # Full path for the export file
            file_path = os.path.join(self.export_dir, file_name)
            
            # Export based on format
            if config.format == ExportFormat.CSV:
                self._export_csv(data, file_path, config)
            elif config.format == ExportFormat.JSON:
                self._export_json(data, file_path, config, metadata)
            elif config.format == ExportFormat.XML:
                self._export_xml(data, file_path, config, metadata)
            elif config.format == ExportFormat.EXCEL:
                self._export_excel(data, file_path, config)
            elif config.format == ExportFormat.SAS:
                self._export_sas(data, file_path, config)
            else:
                return ExportResult(
                    success=False,
                    format=config.format,
                    domain_name=domain_name,
                    error_message=f"Unsupported export format: {config.format}"
                )
            
            # Get file size
            file_size = os.path.getsize(file_path)
            
            # Return success result
            return ExportResult(
                success=True,
                file_path=file_path,
                file_size=file_size,
                record_count=len(data),
                format=config.format,
                domain_name=domain_name,
                metadata=metadata
            )
            
        except Exception as e:
            logger.error(f"Error exporting domain {config.domain_name}: {str(e)}")
            return ExportResult(
                success=False,
                format=config.format,
                domain_name=config.domain_name,
                error_message=f"Export error: {str(e)}"
            )
    
    def _get_extension(self, format: ExportFormat) -> str:
        """Get the file extension for a format."""
        extensions = {
            ExportFormat.CSV: ".csv",
            ExportFormat.JSON: ".json",
            ExportFormat.XML: ".xml",
            ExportFormat.SAS: ".sas7bdat",
            ExportFormat.EXCEL: ".xlsx"
        }
        return extensions.get(format, ".txt")
    
    def _export_csv(self, data: pd.DataFrame, file_path: str, config: ExportConfig) -> None:
        """Export data as CSV."""
        data.to_csv(
            file_path,
            index=False,
            header=config.include_header,
            encoding=config.encoding,
            sep=config.delimiter,
            quotechar=config.quotechar,
            decimal=config.decimal,
            date_format=config.date_format
        )
        
        # Compress if requested
        if config.compress and config.compression_type:
            self._compress_file(file_path, config.compression_type)
    
    def _export_json(
        self, 
        data: pd.DataFrame, 
        file_path: str, 
        config: ExportConfig,
        metadata: ExportMetadata
    ) -> None:
        """Export data as JSON."""
        # Convert DataFrame to records
        records = data.replace({np.nan: None}).to_dict(orient="records")
        
        # Create output structure
        output = {
            "data": records
        }
        
        # Add metadata if requested
        if config.include_metadata:
            output["metadata"] = metadata.dict()
        
        # Write to file
        with open(file_path, "w", encoding=config.encoding) as f:
            json.dump(output, f, indent=2, default=str)
        
        # Compress if requested
        if config.compress and config.compression_type:
            self._compress_file(file_path, config.compression_type)
    
    def _export_xml(
        self, 
        data: pd.DataFrame, 
        file_path: str, 
        config: ExportConfig,
        metadata: ExportMetadata
    ) -> None:
        """Export data as XML."""
        # Create root element
        root = ET.Element("DataExport")
        
        # Add metadata if requested
        if config.include_metadata:
            meta_elem = ET.SubElement(root, "Metadata")
            for key, value in metadata.dict().items():
                if value is not None:
                    if isinstance(value, dict):
                        sub_elem = ET.SubElement(meta_elem, key)
                        for k, v in value.items():
                            if v is not None:
                                ET.SubElement(sub_elem, k).text = str(v)
                    else:
                        ET.SubElement(meta_elem, key).text = str(value)
        
        # Add data
        data_elem = ET.SubElement(root, "Data")
        
        # Convert NaN to None for cleaner XML
        clean_data = data.replace({np.nan: None})
        
        # Add each record
        for _, row in clean_data.iterrows():
            record = ET.SubElement(data_elem, "Record")
            for col, val in row.items():
                if val is not None:
                    ET.SubElement(record, col).text = str(val)
        
        # Create XML string with pretty formatting
        xml_str = ET.tostring(root, encoding="unicode")
        pretty_xml = xml.dom.minidom.parseString(xml_str).toprettyxml(indent="  ")
        
        # Write to file
        with open(file_path, "w", encoding=config.encoding) as f:
            f.write(pretty_xml)
        
        # Compress if requested
        if config.compress and config.compression_type:
            self._compress_file(file_path, config.compression_type)
    
    def _export_excel(self, data: pd.DataFrame, file_path: str, config: ExportConfig) -> None:
        """Export data as Excel."""
        # Ensure we have openpyxl
        try:
            import openpyxl
        except ImportError:
            raise ImportError("openpyxl is required for Excel export. Install it with 'pip install openpyxl'")
        
        # Create Excel writer
        with pd.ExcelWriter(file_path) as writer:
            data.to_excel(
                writer,
                sheet_name=config.sheet_name or "Data",
                index=False,
                header=config.include_header
            )
        
        # Compress if requested
        if config.compress and config.compression_type:
            self._compress_file(file_path, config.compression_type)
    
    def _export_sas(self, data: pd.DataFrame, file_path: str, config: ExportConfig) -> None:
        """Export data as SAS."""
        # Ensure we have pyreadstat
        try:
            import pyreadstat
        except ImportError:
            raise ImportError("pyreadstat is required for SAS export. Install it with 'pip install pyreadstat'")
        
        # Convert to SAS format
        pyreadstat.write_sas7bdat(data, file_path)
        
        # Compress if requested
        if config.compress and config.compression_type:
            self._compress_file(file_path, config.compression_type)
    
    def _compress_file(self, file_path: str, compression_type: str) -> None:
        """Compress a file using the specified compression type."""
        import shutil
        
        if compression_type.lower() == "zip":
            import zipfile
            base_name = os.path.splitext(file_path)[0]
            with zipfile.ZipFile(f"{base_name}.zip", "w", zipfile.ZIP_DEFLATED) as zip_file:
                zip_file.write(file_path, os.path.basename(file_path))
            # Remove original file
            os.remove(file_path)
        elif compression_type.lower() == "gzip":
            import gzip
            with open(file_path, "rb") as f_in:
                with gzip.open(f"{file_path}.gz", "wb") as f_out:
                    shutil.copyfileobj(f_in, f_out)
            # Remove original file
            os.remove(file_path)
        else:
            logger.warning(f"Unsupported compression type: {compression_type}")
    
    def list_exports(self) -> List[Dict[str, Any]]:
        """
        List all exported files.
        
        Returns:
            List of export information dictionaries
        """
        exports = []
        
        if not os.path.exists(self.export_dir):
            return exports
        
        for file_name in os.listdir(self.export_dir):
            file_path = os.path.join(self.export_dir, file_name)
            if os.path.isfile(file_path):
                # Get file info
                file_size = os.path.getsize(file_path)
                modified_time = os.path.getmtime(file_path)
                
                # Determine format from extension
                extension = os.path.splitext(file_name)[1].lower()
                format_map = {
                    ".csv": ExportFormat.CSV,
                    ".json": ExportFormat.JSON,
                    ".xml": ExportFormat.XML,
                    ".sas7bdat": ExportFormat.SAS,
                    ".xlsx": ExportFormat.EXCEL
                }
                format_str = format_map.get(extension, "unknown")
                
                # Extract domain name from file name
                parts = file_name.split("_")
                domain_name = parts[0] if parts else "unknown"
                
                exports.append({
                    "file_name": file_name,
                    "file_path": file_path,
                    "file_size": file_size,
                    "format": format_str,
                    "domain_name": domain_name,
                    "created_at": datetime.datetime.fromtimestamp(modified_time).isoformat()
                })
        
        return exports


# Create a singleton instance for the application
export_service = ExportService()
