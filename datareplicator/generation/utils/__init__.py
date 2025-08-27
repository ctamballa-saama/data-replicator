"""
Utility functions for synthetic data generation.
"""

from datareplicator.generation.utils.sampling import (
    sample_numeric,
    sample_categorical,
    sample_dates,
    generate_correlated_variables,
    generate_id_values,
    generate_text_values,
    apply_missing_values,
    sample_from_distribution,
    create_dependent_categorical
)

# Export utility functions
__all__ = [
    'sample_numeric',
    'sample_categorical',
    'sample_dates',
    'generate_correlated_variables',
    'generate_id_values',
    'generate_text_values',
    'apply_missing_values',
    'sample_from_distribution',
    'create_dependent_categorical'
]
