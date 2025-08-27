"""
Synthetic data generation service.
"""
import os
import uuid
import pandas as pd
from typing import Dict, List, Any, Optional
import time
from datetime import datetime

from datareplicator.domain_registry.service import domain_registry


class GenerationJob:
    """Represents a synthetic data generation job."""
    
    def __init__(
        self,
        job_id: str,
        domain_name: str,
        record_count: int,
        generation_mode: str,
        preserve_relationships: bool,
        seed: Optional[int] = None
    ):
        """Initialize a generation job."""
        self.job_id = job_id
        self.domain_name = domain_name
        self.record_count = record_count
        self.generation_mode = generation_mode
        self.preserve_relationships = preserve_relationships
        self.seed = seed
        self.status = "pending"
        self.created_at = datetime.now().isoformat()
        self.completed_at = None
        self.result_file = None
        self.error = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert job to dictionary."""
        return {
            "job_id": self.job_id,
            "domain_name": self.domain_name,
            "record_count": self.record_count,
            "generation_mode": self.generation_mode,
            "preserve_relationships": self.preserve_relationships,
            "seed": self.seed,
            "status": self.status,
            "created_at": self.created_at,
            "completed_at": self.completed_at,
            "result_file": self.result_file,
            "error": self.error
        }


class GenerationService:
    """Service for generating synthetic clinical data."""
    
    def __init__(self):
        """Initialize the generation service."""
        self.jobs: Dict[str, GenerationJob] = {}
        # Use a directory within the project for easier access during development
        self.upload_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "generated_data")
        # Create upload directory if it doesn't exist
        os.makedirs(self.upload_dir, exist_ok=True)
        print(f"Generation service initialized with upload directory: {self.upload_dir}")
    
    def create_job(
        self,
        domain_name: str,
        record_count: int,
        generation_mode: str = "statistical",
        preserve_relationships: bool = True,
        seed: Optional[int] = None
    ) -> GenerationJob:
        """
        Create a new generation job.
        
        Args:
            domain_name: Name of the domain to generate data for
            record_count: Number of records to generate
            generation_mode: Mode of generation ("random" or "statistical")
            preserve_relationships: Whether to preserve relationships
            seed: Random seed for generation
            
        Returns:
            The created job
        """
        job_id = f"job_{uuid.uuid4().hex[:8]}"
        job = GenerationJob(
            job_id=job_id,
            domain_name=domain_name,
            record_count=record_count,
            generation_mode=generation_mode,
            preserve_relationships=preserve_relationships,
            seed=seed
        )
        self.jobs[job_id] = job
        return job
    
    async def start_job(self, job_id: str) -> None:
        """
        Start a generation job asynchronously.
        
        Args:
            job_id: ID of the job to start
        """
        import os
        import time
        import pandas as pd
        
        job = self.jobs.get(job_id)
        if not job:
            print(f"Job {job_id} not found")
            return
        
        print(f"Starting job {job_id} for domain {job.domain_name}")
        job.status = "running"
        
        try:
            # Get the domain data
            domain = domain_registry.get_domain(job.domain_name)
            if not domain:
                print(f"Domain {job.domain_name} not found")
                job.status = "failed"
                job.error = f"Domain {job.domain_name} not found"
                return
            
            # Load the domain data
            df = domain.load_data() if domain else None
            if df is None:
                print(f"Failed to load data for domain {job.domain_name}")
                job.status = "failed"
                job.error = f"Failed to load data for domain {job.domain_name}"
                return
            
            print(f"Loaded domain data for {job.domain_name} with {len(df)} rows")
            
            # Add a short delay to simulate processing
            time.sleep(1)
            
            # Generate data based on the specified mode
            if job.generation_mode == "random":
                print(f"Generating random data for {job.domain_name} with {job.record_count} records")
                generated_df = self._generate_random_data(df, job.record_count)
            else:
                print(f"Generating statistical data for {job.domain_name} with {job.record_count} records")
                generated_df = self._generate_statistical_data(df, job.record_count)
            
            # Make sure the upload directory exists
            os.makedirs(self.upload_dir, exist_ok=True)
            
            # Create a standardized filename that will be consistent for frontend downloads
            result_file = os.path.join(self.upload_dir, f"{job.domain_name}_{job_id}.csv")
            
            # Save the generated data
            print(f"Saving generated data to {result_file}")
            generated_df.to_csv(result_file, index=False)
            
            # Verify the file was created
            if not os.path.exists(result_file):
                print(f"Error: File {result_file} was not created")
                job.status = "failed"
                job.error = f"Failed to save generated data"
                return
                
            # Also save to a location with just the domain name for simpler access
            # This will overwrite previous generations for the same domain
            domain_file = os.path.join(self.upload_dir, f"{job.domain_name}.csv")
            generated_df.to_csv(domain_file, index=False)
            
            # Update job status
            job.status = "completed"
            job.completed_at = datetime.now().isoformat()
            job.result_file = result_file
            print(f"Job {job_id} completed successfully. File saved to {result_file}")
            
        except Exception as e:
            print(f"Error in job {job_id}: {str(e)}")
            job.status = "failed"
            job.error = str(e)
    
    def get_job(self, job_id: str) -> Optional[GenerationJob]:
        """
        Get a job by ID.
        
        Args:
            job_id: ID of the job
            
        Returns:
            The job if found, None otherwise
        """
        return self.jobs.get(job_id)
    
    def list_jobs(self) -> List[Dict[str, Any]]:
        """
        List all jobs.
        
        Returns:
            List of job dictionaries
        """
        return [job.to_dict() for job in self.jobs.values()]
    
    def get_generated_data(self, job_id: str) -> Optional[pd.DataFrame]:
        """
        Get the generated data for a job.
        
        Args:
            job_id: ID of the job
            
        Returns:
            DataFrame with generated data if available, None otherwise
        """
        job = self.jobs.get(job_id)
        if job and job.status == "completed" and job.result_file:
            try:
                return pd.read_csv(job.result_file)
            except:
                pass
        return None
    
    def _generate_random_data(self, df: pd.DataFrame, record_count: int) -> pd.DataFrame:
        """
        Generate random data based on original data.
        
        Args:
            df: Original DataFrame
            record_count: Number of records to generate
            
        Returns:
            DataFrame with generated data
        """
        import numpy as np
        import random
        from datetime import datetime, timedelta
        
        # If we have data to base generation on, use it as a template
        if len(df) > 0:
            result = df.sample(n=record_count, replace=True).copy()
            
            # Add noise to numeric columns to make data look different
            for col in result.select_dtypes(include=['number']).columns:
                # Add larger noise for more variation (20% of standard deviation)
                noise = result[col].std() * 0.2 * np.random.randn(len(result))
                result[col] = result[col] + noise
            
            # Shuffle categorical data
            for col in result.select_dtypes(include=['object', 'category']).columns:
                if col.lower() not in ['id', 'patient_id', 'subject_id', 'identifier']:
                    # Get unique values from the column
                    unique_values = df[col].dropna().unique().tolist()
                    if len(unique_values) > 1:
                        # Randomly assign values from the list of unique values
                        result[col] = [random.choice(unique_values) for _ in range(len(result))]
            
            # Handle date columns if any
            date_cols = [col for col in df.columns if df[col].dtype == 'datetime64[ns]']
            for col in date_cols:
                # Generate random dates within 2 years of the original dates
                min_date = df[col].min()
                max_date = df[col].max()
                date_range = (max_date - min_date).days
                # Generate random dates
                random_days = np.random.randint(-365, 365, size=len(result))
                result[col] = result[col] + pd.to_timedelta(random_days, unit='d')
        else:
            # If no data to base on, create sample data with common clinical fields
            data = {
                'PatientID': [f'P{1000 + i}' for i in range(record_count)],
                'Age': np.random.randint(18, 80, size=record_count),
                'Gender': np.random.choice(['Male', 'Female', 'Other'], size=record_count),
                'Weight_kg': np.random.normal(70, 15, size=record_count).round(1),
                'Height_cm': np.random.normal(170, 15, size=record_count).round(1),
                'BloodPressure_Systolic': np.random.normal(120, 15, size=record_count).round().astype(int),
                'BloodPressure_Diastolic': np.random.normal(80, 10, size=record_count).round().astype(int),
                'HeartRate_bpm': np.random.normal(75, 10, size=record_count).round().astype(int),
                'BodyTemp_C': np.random.normal(36.8, 0.4, size=record_count).round(1),
                'CholesterolLevel_mg_dL': np.random.normal(190, 30, size=record_count).round().astype(int),
            }
            result = pd.DataFrame(data)
            
        return result
    
    def _generate_statistical_data(self, df: pd.DataFrame, record_count: int) -> pd.DataFrame:
        """
        Generate data preserving statistical properties of the original data.
        
        Creates data that maintains the same distribution, correlations, and other
        statistical properties as the original dataset.
        
        Args:
            df: Original DataFrame
            record_count: Number of records to generate
            
        Returns:
            DataFrame with generated data
        """
        # In a real implementation, this would use more sophisticated statistical methods
        # For this demo, we'll use a slightly enhanced version of random generation
        if len(df) > 0:
            # Create empty result DataFrame with same columns
            result = pd.DataFrame(columns=df.columns)
            
            # For each column, generate values based on column type
            for col in df.columns:
                if pd.api.types.is_numeric_dtype(df[col]):
                    # Numeric column: sample from normal distribution matching mean and std
                    mean = df[col].mean()
                    std = df[col].std()
                    if pd.isna(std) or std == 0:
                        std = 0.1 * mean if mean != 0 else 1.0
                    result[col] = pd.np.random.normal(mean, std, size=record_count)
                    
                elif pd.api.types.is_datetime64_dtype(df[col]):
                    # Date column: sample from existing dates
                    result[col] = pd.np.random.choice(df[col], size=record_count)
                    
                else:
                    # Categorical/text: sample based on frequency distribution
                    value_counts = df[col].value_counts(normalize=True)
                    result[col] = pd.np.random.choice(
                        value_counts.index, 
                        size=record_count, 
                        p=value_counts.values
                    )
            
            return result
        else:
            return pd.DataFrame()


# Create singleton instance
generator_service = GenerationService()
