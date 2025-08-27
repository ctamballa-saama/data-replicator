"""
Domain Registry Service for managing clinical data domains.
"""
import pandas as pd
from typing import Dict, List, Any, Optional


class Domain:
    """Represents a clinical data domain."""
    
    def __init__(
        self, 
        name: str, 
        file_path: str,
        record_count: int,
        variable_count: int,
        variables: List[str],
        sample_data: List[Dict[str, Any]],
        description: Optional[str] = None
    ):
        """Initialize a domain."""
        self.name = name
        self.file_path = file_path
        self.record_count = record_count
        self.variable_count = variable_count
        self.variables = variables
        self.sample_data = sample_data
        # Ensure description is always set to a string value
        self.description = str(description) if description else f"Clinical data domain for {name}"
        self.dataframe = None
    
    def load_data(self) -> pd.DataFrame:
        """Load the domain data as a pandas DataFrame."""
        import os
        import logging
        logger = logging.getLogger(__name__)
        
        if self.dataframe is None:
            # First try to use the sample_data that was provided during registration
            if self.sample_data and len(self.sample_data) > 0:
                try:
                    # Convert the list of dictionaries to a pandas DataFrame
                    self.dataframe = pd.DataFrame(self.sample_data)
                    logger.info(f"Created DataFrame from sample data for domain {self.name}, {len(self.dataframe)} rows loaded")
                    return self.dataframe
                except Exception as e:
                    logger.error(f"Failed to create DataFrame from sample data: {e}")
            
            # If no sample data or error occurred, try to load from CSV file
            try:
                # Try multiple possible file locations
                possible_paths = [
                    self.file_path,                                      # As provided
                    os.path.join(os.getcwd(), self.file_path),           # Current working directory
                    os.path.join(os.path.dirname(__file__), '..', '..', self.file_path)  # Project root from module
                ]
                
                for path in possible_paths:
                    try:
                        if os.path.exists(path):
                            self.dataframe = pd.read_csv(path)
                            logger.info(f"Successfully loaded data from {path}, {len(self.dataframe)} rows found")
                            return self.dataframe
                    except Exception as e:
                        logger.error(f"Error loading from {path}: {e}")
            except Exception as e:
                logger.error(f"Error trying to load CSV files: {e}")
            
            # If still no dataframe, create an empty one
            logger.warning(f"No data found for domain {self.name}. Using empty dataframe.")
            self.dataframe = pd.DataFrame(columns=self.variables)
            
        return self.dataframe
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert domain to dictionary."""
        return {
            "name": self.name,
            "file_path": self.file_path,
            "record_count": self.record_count,
            "variable_count": self.variable_count,
            "variables": self.variables,
            "sample_data": self.sample_data
        }


class DomainRegistry:
    """Registry for managing clinical data domains."""
    
    def __init__(self):
        """Initialize the domain registry."""
        self.domains: Dict[str, Domain] = {}
    
    def register_domain(
        self, 
        domain_name: str, 
        file_path: str,
        record_count: int,
        variable_count: int,
        variables: List[str],
        sample_data: List[Dict[str, Any]],
        description: Optional[str] = None
    ) -> Domain:
        """
        Register a new domain in the registry.
        
        Args:
            domain_name: Name of the domain
            file_path: Path to the domain data file
            record_count: Number of records in the domain
            variable_count: Number of variables in the domain
            variables: List of variable names
            sample_data: Sample data from the domain
            description: Description of the domain
            
        Returns:
            The registered domain
        """
        domain = Domain(
            name=domain_name,
            file_path=file_path,
            record_count=record_count,
            variable_count=variable_count,
            variables=variables,
            sample_data=sample_data,
            description=description
        )
        self.domains[domain_name] = domain
        return domain
    
    def get_domain(self, domain_name: str) -> Optional[Domain]:
        """
        Get a domain by name.
        
        Args:
            domain_name: Name of the domain
            
        Returns:
            The domain if found, None otherwise
        """
        return self.domains.get(domain_name)
    
    def list_domains(self) -> List[Dict[str, Any]]:
        """
        List all registered domains.
        
        Returns:
            List of domain dictionaries
        """
        return [domain.to_dict() for domain in self.domains.values()]
    
    def get_domain_data(self, domain_name: str) -> Optional[pd.DataFrame]:
        """
        Get the data for a domain.
        
        Args:
            domain_name: Name of the domain
            
        Returns:
            DataFrame with domain data if found, None otherwise
        """
        domain = self.get_domain(domain_name)
        if domain:
            return domain.load_data()
        return None


# Create singleton instance
domain_registry = DomainRegistry()

# Add some sample domains for development/testing
def add_sample_domains():
    """Add some sample domains for development."""
    # Sample Demographics domain
    domain_registry.register_domain(
        domain_name="Demographics",
        file_path="sample_data_demographics.csv",
        record_count=20,
        variable_count=5,
        variables=["SUBJID", "AGE", "GENDER", "RACE", "COUNTRY"],
        sample_data=[
            {"SUBJID": "001", "AGE": 45, "GENDER": "M", "RACE": "White", "COUNTRY": "USA"},
            {"SUBJID": "002", "AGE": 36, "GENDER": "F", "RACE": "Black", "COUNTRY": "USA"},
            {"SUBJID": "003", "AGE": 52, "GENDER": "M", "RACE": "Asian", "COUNTRY": "Japan"}
        ],
        description="Patient demographic information including age, gender, race, and country"
    )
    
    # Sample Vitals domain
    domain_registry.register_domain(
        domain_name="Vitals",
        file_path="sample_data_vitals.csv",
        record_count=60,
        variable_count=6,
        variables=["SUBJID", "VISITNUM", "VISITDT", "WEIGHT", "HEIGHT", "BMI"],
        sample_data=[
            {"SUBJID": "001", "VISITNUM": 1, "VISITDT": "2023-01-15", "WEIGHT": 75.5, "HEIGHT": 180.0, "BMI": 23.3},
            {"SUBJID": "001", "VISITNUM": 2, "VISITDT": "2023-02-15", "WEIGHT": 75.0, "HEIGHT": 180.0, "BMI": 23.1},
            {"SUBJID": "002", "VISITNUM": 1, "VISITDT": "2023-01-17", "WEIGHT": 65.2, "HEIGHT": 165.0, "BMI": 24.0}
        ],
        description="Patient vital signs measurements including weight, height, and BMI across visits"
    )
    
    # Sample Labs domain
    domain_registry.register_domain(
        domain_name="Labs",
        file_path="sample_data_labs.csv",
        record_count=120,
        variable_count=7,
        variables=["SUBJID", "VISITNUM", "LBTEST", "LBRESULT", "LBUNIT", "LBREFLO", "LBREFHI"],
        sample_data=[
            {"SUBJID": "001", "VISITNUM": 1, "LBTEST": "Glucose", "LBRESULT": 95, "LBUNIT": "mg/dL", "LBREFLO": 70, "LBREFHI": 110},
            {"SUBJID": "001", "VISITNUM": 1, "LBTEST": "HbA1c", "LBRESULT": 5.2, "LBUNIT": "%", "LBREFLO": 4.0, "LBREFHI": 5.7},
            {"SUBJID": "002", "VISITNUM": 1, "LBTEST": "Glucose", "LBRESULT": 105, "LBUNIT": "mg/dL", "LBREFLO": 70, "LBREFHI": 110}
        ],
        description="Laboratory test results including glucose, HbA1c, and cholesterol measurements"
    )

# Add sample domains for development
add_sample_domains()
