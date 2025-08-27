"""
Generator service for synthetic data generation.

Provides a high-level interface for configuring and executing data generation tasks.
"""
import logging
from typing import Dict, List, Optional, Union, Any
from concurrent.futures import ThreadPoolExecutor

import pandas as pd

from datareplicator.data.models import DomainData
from datareplicator.domain_registry.service import Domain
from datareplicator.data.registry import domain_registry
from datareplicator.analysis.statistics import stats_service
from datareplicator.analysis.relationships import relationship_service

from datareplicator.generation.models.config import (
    GenerationMode,
    GenerationConfig,
    DomainGenerationConfig
)
from datareplicator.generation.models.results import (
    GenerationStatus,
    DomainGenerationResult,
    GenerationJobResult
)
from datareplicator.generation.generators import (
    BaseGenerator,
    RandomGenerator,
    StatisticalGenerator
)


logger = logging.getLogger(__name__)


class GeneratorService:
    """
    Service for managing and executing data generation tasks.
    
    Provides methods to configure, run, and monitor synthetic data generation.
    """
    
    def __init__(self):
        """Initialize the generator service."""
        self.active_jobs: Dict[str, GenerationJobResult] = {}
    
    def create_generator(self, domain_config: DomainGenerationConfig, 
                        source_data: Optional[Union[pd.DataFrame, DomainData]] = None,
                        seed: Optional[int] = None) -> BaseGenerator:
        """
        Create appropriate generator based on configuration.
        
        Args:
            domain_config: Domain generation configuration
            source_data: Source data for statistical generation
            seed: Random seed for reproducibility
            
        Returns:
            BaseGenerator: Configured generator instance
        """
        generation_mode = domain_config.generation_mode
        
        if generation_mode == GenerationMode.RANDOM:
            return RandomGenerator(domain_config, seed=seed)
        
        elif generation_mode == GenerationMode.STATISTICAL:
            if source_data is None:
                # Try to get source data from registry
                domain_name = domain_config.domain_name
                if domain_name in domain_registry.domains:
                    source_data = domain_registry.get_domain_data(domain_name)
            
            return StatisticalGenerator(domain_config, source_data=source_data, 
                                      stats_service=stats_service, seed=seed)
        
        else:
            logger.warning(f"Unsupported generation mode: {generation_mode}, falling back to random")
            return RandomGenerator(domain_config, seed=seed)
    
    def generate_domain_data(self, domain_config: DomainGenerationConfig,
                           source_data: Optional[Union[pd.DataFrame, DomainData]] = None,
                           seed: Optional[int] = None) -> DomainGenerationResult:
        """
        Generate synthetic data for a single domain.
        
        Args:
            domain_config: Domain generation configuration
            source_data: Source data for statistical generation
            seed: Random seed for reproducibility
            
        Returns:
            DomainGenerationResult: Results of generation process
        """
        try:
            # Create appropriate generator
            generator = self.create_generator(domain_config, source_data, seed)
            
            # Generate data
            result = generator.generate()
            
            # Register generated domain if requested
            if domain_config.register_domain and result.status == GenerationStatus.COMPLETED:
                # Create domain object
                domain = Domain(
                    name=domain_config.domain_name,
                    description=f"Generated domain: {domain_config.domain_name}",
                    variables=domain_config.variables
                )
                
                # Create domain data object
                domain_data = DomainData(
                    domain_name=domain_config.domain_name,
                    data=result.data.to_dict(orient='records')
                )
                
                # Register domain and data
                domain_registry.register_domain(domain)
                domain_registry.register_domain_data(domain_data)
            
            return result
        
        except Exception as e:
            logger.error(f"Error generating domain data for {domain_config.domain_name}: {str(e)}")
            result = DomainGenerationResult(
                domain_name=domain_config.domain_name,
                status=GenerationStatus.FAILED,
                error_message=str(e),
                record_count=0
            )
            return result
    
    def generate_data(self, config: GenerationConfig, 
                     job_id: Optional[str] = None) -> GenerationJobResult:
        """
        Generate synthetic data for multiple domains according to configuration.
        
        Args:
            config: Generation job configuration
            job_id: Optional job identifier
            
        Returns:
            GenerationJobResult: Results of the generation job
        """
        # Create a job result to track progress
        job_result = GenerationJobResult(
            job_id=job_id or f"job_{len(self.active_jobs) + 1}",
            status=GenerationStatus.IN_PROGRESS,
            domain_results={},
            start_time=pd.Timestamp.now()
        )
        
        # Store in active jobs
        self.active_jobs[job_result.job_id] = job_result
        
        try:
            # Get master seed for job
            seed = config.seed
            
            # Process domains sequentially or in parallel
            if config.parallel_execution and len(config.domain_configs) > 1:
                # Execute domains in parallel
                with ThreadPoolExecutor(max_workers=min(len(config.domain_configs), 4)) as executor:
                    future_to_domain = {
                        executor.submit(
                            self.generate_domain_data, 
                            domain_config, 
                            seed=seed + i if seed is not None else None
                        ): domain_config.domain_name 
                        for i, domain_config in enumerate(config.domain_configs)
                    }
                    
                    for future in future_to_domain:
                        domain_name = future_to_domain[future]
                        try:
                            domain_result = future.result()
                            job_result.domain_results[domain_name] = domain_result
                        except Exception as e:
                            logger.error(f"Error generating domain {domain_name}: {str(e)}")
                            job_result.domain_results[domain_name] = DomainGenerationResult(
                                domain_name=domain_name,
                                status=GenerationStatus.FAILED,
                                error_message=str(e),
                                record_count=0
                            )
            else:
                # Execute domains sequentially
                for i, domain_config in enumerate(config.domain_configs):
                    domain_name = domain_config.domain_name
                    try:
                        # Use domain-specific seed if master seed provided
                        domain_seed = seed + i if seed is not None else None
                        
                        # Generate data for this domain
                        domain_result = self.generate_domain_data(
                            domain_config, seed=domain_seed
                        )
                        
                        job_result.domain_results[domain_name] = domain_result
                    except Exception as e:
                        logger.error(f"Error generating domain {domain_name}: {str(e)}")
                        job_result.domain_results[domain_name] = DomainGenerationResult(
                            domain_name=domain_name,
                            status=GenerationStatus.FAILED,
                            error_message=str(e),
                            record_count=0
                        )
            
            # Update relationships between generated domains if needed
            if config.preserve_relationships and len(job_result.domain_results) > 1:
                self._apply_domain_relationships(job_result, config)
            
            # Update job status
            all_completed = all(
                result.status == GenerationStatus.COMPLETED 
                for result in job_result.domain_results.values()
            )
            
            job_result.status = GenerationStatus.COMPLETED if all_completed else GenerationStatus.PARTIAL
            job_result.end_time = pd.Timestamp.now()
            
            return job_result
        
        except Exception as e:
            logger.error(f"Error in generation job {job_result.job_id}: {str(e)}")
            job_result.status = GenerationStatus.FAILED
            job_result.error_message = str(e)
            job_result.end_time = pd.Timestamp.now()
            return job_result
    
    def _apply_domain_relationships(self, job_result: GenerationJobResult, config: GenerationConfig) -> None:
        """
        Apply relationships between generated domains.
        
        Args:
            job_result: Current job result with generated data
            config: Generation configuration
        """
        try:
            # Build dictionary of generated dataframes
            domain_dataframes = {}
            for domain_name, result in job_result.domain_results.items():
                if result.status == GenerationStatus.COMPLETED and result.data is not None:
                    domain_dataframes[domain_name] = result.data
            
            if len(domain_dataframes) <= 1:
                return
            
            # Get relationship graph if available
            relationship_graph = relationship_service.get_relationship_graph()
            
            if not relationship_graph or not relationship_graph.relationships:
                logger.warning("No relationships found in relationship graph")
                return
            
            # Process subject and visit relationships first (foreign key relationships)
            for rel in relationship_graph.relationships:
                source_domain = rel.source_domain
                target_domain = rel.target_domain
                
                # Skip if either domain is not in our generated data
                if source_domain not in domain_dataframes or target_domain not in domain_dataframes:
                    continue
                
                # Handle subject and visit relationships
                if rel.relationship_type in ["subject", "visit"]:
                    source_df = domain_dataframes[source_domain]
                    target_df = domain_dataframes[target_domain]
                    
                    source_key = rel.source_variable
                    target_key = rel.target_variable
                    
                    # Ensure both dataframes have the key columns
                    if source_key in source_df.columns and target_key in target_df.columns:
                        # Get unique values from source
                        source_values = source_df[source_key].unique().tolist()
                        
                        # Update target values to match source if possible
                        if len(source_values) > 0:
                            # Replace target values with valid source values
                            for i, value in enumerate(target_df[target_key]):
                                if i < len(target_df):
                                    src_idx = i % len(source_values)
                                    target_df.at[i, target_key] = source_values[src_idx]
                            
                            # Update the result data
                            job_result.domain_results[target_domain].data = target_df
            
            # TODO: Handle more complex relationships (time, derived) if needed
        
        except Exception as e:
            logger.error(f"Error applying domain relationships: {str(e)}")
    
    def get_job_status(self, job_id: str) -> Optional[GenerationJobResult]:
        """
        Get status of a generation job.
        
        Args:
            job_id: Job identifier
            
        Returns:
            Optional[GenerationJobResult]: Job result if found
        """
        return self.active_jobs.get(job_id)
    
    def clear_job(self, job_id: str) -> bool:
        """
        Clear a completed job from active jobs.
        
        Args:
            job_id: Job identifier
            
        Returns:
            bool: True if job was cleared
        """
        if job_id in self.active_jobs:
            # Only clear completed or failed jobs
            status = self.active_jobs[job_id].status
            if status in [GenerationStatus.COMPLETED, GenerationStatus.FAILED, GenerationStatus.PARTIAL]:
                del self.active_jobs[job_id]
                return True
        return False


# Create singleton instance
generator_service = GeneratorService()
