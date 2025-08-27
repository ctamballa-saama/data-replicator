"""
Utility functions for sampling and generating data values.

Provides reusable functions for generating and transforming values
using various statistical distributions and patterns.
"""
import random
import string
from typing import List, Dict, Any, Optional, Union, Tuple
from datetime import datetime, timedelta

import numpy as np
import pandas as pd
from scipy import stats


def sample_numeric(
    distribution: str = "normal",
    params: Dict[str, Any] = None,
    min_value: Optional[float] = None,
    max_value: Optional[float] = None,
    count: int = 1,
    as_integer: bool = False,
    seed: Optional[int] = None,
) -> np.ndarray:
    """
    Sample numeric values from a specified distribution.
    
    Args:
        distribution: Distribution name (normal, uniform, poisson, etc.)
        params: Distribution parameters
        min_value: Minimum allowed value
        max_value: Maximum allowed value
        count: Number of values to generate
        as_integer: Whether to convert to integers
        seed: Random seed for reproducibility
        
    Returns:
        np.ndarray: Array of sampled values
    """
    if seed is not None:
        np.random.seed(seed)
    
    params = params or {}
    
    if distribution == "normal":
        mean = params.get("mean", 0.0)
        std = params.get("std", 1.0)
        values = np.random.normal(mean, std, count)
    
    elif distribution == "uniform":
        low = params.get("low", 0.0) if min_value is None else min_value
        high = params.get("high", 1.0) if max_value is None else max_value
        values = np.random.uniform(low, high, count)
    
    elif distribution == "poisson":
        lam = params.get("lambda", 5.0)
        values = np.random.poisson(lam, count)
    
    elif distribution == "exponential":
        scale = params.get("scale", 1.0)
        values = np.random.exponential(scale, count)
    
    elif distribution == "gamma":
        shape = params.get("shape", 1.0)
        scale = params.get("scale", 1.0)
        values = np.random.gamma(shape, scale, count)
    
    elif distribution == "beta":
        alpha = params.get("alpha", 1.0)
        beta = params.get("beta", 1.0)
        values = np.random.beta(alpha, beta, count)
    
    elif distribution == "lognormal":
        mean = params.get("mean", 0.0)
        sigma = params.get("sigma", 1.0)
        values = np.random.lognormal(mean, sigma, count)
    
    elif distribution == "binomial":
        n = params.get("n", 10)
        p = params.get("p", 0.5)
        values = np.random.binomial(n, p, count)
    
    else:
        # Default to uniform
        low = params.get("low", 0.0) if min_value is None else min_value
        high = params.get("high", 1.0) if max_value is None else max_value
        values = np.random.uniform(low, high, count)
    
    # Apply min/max constraints
    if min_value is not None:
        values = np.maximum(values, min_value)
    if max_value is not None:
        values = np.minimum(values, max_value)
    
    # Convert to integers if requested
    if as_integer:
        values = np.round(values).astype(int)
    
    return values


def sample_categorical(
    categories: List[Any],
    probabilities: Optional[List[float]] = None,
    count: int = 1,
    seed: Optional[int] = None,
) -> np.ndarray:
    """
    Sample categorical values with specified probabilities.
    
    Args:
        categories: List of possible categories/values
        probabilities: Probability for each category (must sum to 1)
        count: Number of values to generate
        seed: Random seed for reproducibility
        
    Returns:
        np.ndarray: Array of sampled values
    """
    if seed is not None:
        np.random.seed(seed)
    
    # If probabilities not provided, use uniform distribution
    if probabilities is None:
        probabilities = [1.0 / len(categories)] * len(categories)
    
    # Ensure probabilities sum to 1
    total = sum(probabilities)
    if abs(total - 1.0) > 1e-10:
        probabilities = [p / total for p in probabilities]
    
    return np.random.choice(categories, size=count, p=probabilities)


def sample_dates(
    start_date: Union[str, datetime],
    end_date: Union[str, datetime],
    count: int = 1,
    distribution: str = "uniform",
    params: Dict[str, Any] = None,
    seed: Optional[int] = None,
) -> List[str]:
    """
    Sample dates within a specified range.
    
    Args:
        start_date: Start date (inclusive)
        end_date: End date (inclusive)
        count: Number of dates to generate
        distribution: Distribution name for sampling
        params: Distribution parameters
        seed: Random seed for reproducibility
        
    Returns:
        List[str]: Sampled dates in ISO format (YYYY-MM-DD)
    """
    if seed is not None:
        random.seed(seed)
        np.random.seed(seed)
    
    # Convert string dates to datetime objects
    if isinstance(start_date, str):
        start_date = datetime.fromisoformat(start_date.replace('Z', '+00:00'))
    if isinstance(end_date, str):
        end_date = datetime.fromisoformat(end_date.replace('Z', '+00:00'))
    
    # Calculate date range in days
    days_range = (end_date - start_date).days
    if days_range < 0:
        raise ValueError("End date must be after start date")
    
    # Sample days from the range
    if distribution == "uniform":
        days = np.random.randint(0, days_range + 1, count)
    elif distribution == "normal":
        # Normal distribution centered in the middle of the range
        params = params or {}
        mean = params.get("mean", days_range / 2)
        std = params.get("std", days_range / 6)  # ~99.7% within range
        days = np.random.normal(mean, std, count)
        days = np.clip(np.round(days), 0, days_range).astype(int)
    else:
        # Default to uniform
        days = np.random.randint(0, days_range + 1, count)
    
    # Convert to dates
    result = [(start_date + timedelta(days=int(day))).strftime("%Y-%m-%d") for day in days]
    return result


def generate_correlated_variables(
    base_values: np.ndarray,
    correlation: float,
    target_mean: float = 0.0,
    target_std: float = 1.0,
    as_integer: bool = False,
    min_value: Optional[float] = None,
    max_value: Optional[float] = None,
    seed: Optional[int] = None
) -> np.ndarray:
    """
    Generate correlated variable values based on existing values.
    
    Args:
        base_values: Existing values to correlate with
        correlation: Desired correlation coefficient (-1 to 1)
        target_mean: Mean for the new variable
        target_std: Standard deviation for the new variable
        as_integer: Whether to convert to integers
        min_value: Minimum allowed value
        max_value: Maximum allowed value
        seed: Random seed for reproducibility
        
    Returns:
        np.ndarray: Correlated values
    """
    if seed is not None:
        np.random.seed(seed)
    
    # Normalize base values
    base_normalized = (base_values - np.mean(base_values)) / np.std(base_values)
    
    # Generate uncorrelated values
    noise = np.random.normal(0, 1, len(base_values))
    
    # Combine to achieve target correlation
    correlated = correlation * base_normalized + np.sqrt(1 - correlation**2) * noise
    
    # Scale to target mean and standard deviation
    result = correlated * target_std + target_mean
    
    # Apply min/max constraints
    if min_value is not None:
        result = np.maximum(result, min_value)
    if max_value is not None:
        result = np.minimum(result, max_value)
    
    # Convert to integers if requested
    if as_integer:
        result = np.round(result).astype(int)
    
    return result


def generate_id_values(
    count: int,
    prefix: str = "",
    suffix: str = "",
    pattern: str = None,
    start_num: int = 1,
    width: int = 6,
    seed: Optional[int] = None
) -> List[str]:
    """
    Generate ID values with consistent pattern.
    
    Args:
        count: Number of IDs to generate
        prefix: String prefix for IDs
        suffix: String suffix for IDs
        pattern: Pattern with placeholders ({D}=digit, {L}=letter, {H}=hex)
        start_num: Starting number for sequential IDs
        width: Width for numeric portion (zero-padded)
        seed: Random seed for reproducibility
        
    Returns:
        List[str]: Generated ID values
    """
    if seed is not None:
        random.seed(seed)
    
    result = []
    
    if pattern:
        # Generate IDs according to pattern
        for _ in range(count):
            id_value = ""
            for char in pattern:
                if char == "D":
                    id_value += random.choice("0123456789")
                elif char == "L":
                    id_value += random.choice("ABCDEFGHIJKLMNOPQRSTUVWXYZ")
                elif char == "H":
                    id_value += random.choice("0123456789ABCDEF")
                else:
                    id_value += char
            result.append(id_value)
    else:
        # Generate sequential IDs
        for i in range(count):
            num = start_num + i
            id_value = f"{prefix}{str(num).zfill(width)}{suffix}"
            result.append(id_value)
    
    return result


def generate_text_values(
    count: int,
    min_length: int = 5,
    max_length: int = 20,
    word_list: List[str] = None,
    pattern: str = None,
    seed: Optional[int] = None
) -> List[str]:
    """
    Generate text values with specified characteristics.
    
    Args:
        count: Number of text values to generate
        min_length: Minimum text length
        max_length: Maximum text length
        word_list: List of words to sample from
        pattern: Pattern with placeholders ({L}=letter, {D}=digit, {W}=word)
        seed: Random seed for reproducibility
        
    Returns:
        List[str]: Generated text values
    """
    if seed is not None:
        random.seed(seed)
    
    # Default word list if not provided
    if word_list is None:
        word_list = [
            "lorem", "ipsum", "dolor", "sit", "amet", "consectetur",
            "adipiscing", "elit", "sed", "do", "eiusmod", "tempor",
            "incididunt", "ut", "labore", "et", "dolore", "magna", "aliqua"
        ]
    
    result = []
    
    if pattern:
        # Generate text according to pattern
        for _ in range(count):
            text = ""
            i = 0
            while i < len(pattern):
                if pattern[i:i+3] == "{L}":
                    text += random.choice(string.ascii_letters)
                    i += 3
                elif pattern[i:i+3] == "{D}":
                    text += random.choice(string.digits)
                    i += 3
                elif pattern[i:i+3] == "{W}":
                    text += random.choice(word_list)
                    i += 3
                else:
                    text += pattern[i]
                    i += 1
            result.append(text)
    else:
        # Generate random text of varying length
        for _ in range(count):
            length = random.randint(min_length, max_length)
            words = []
            current_length = 0
            
            while current_length < length:
                word = random.choice(word_list)
                if current_length + len(word) + (1 if words else 0) <= max_length:
                    words.append(word)
                    current_length += len(word) + (1 if current_length > 0 else 0)
                else:
                    break
            
            result.append(" ".join(words))
    
    return result


def apply_missing_values(
    data: Union[List, np.ndarray],
    probability: float = 0.1,
    seed: Optional[int] = None
) -> List:
    """
    Apply missing values (None) to data with specified probability.
    
    Args:
        data: Input data
        probability: Probability of each value becoming NULL
        seed: Random seed for reproducibility
        
    Returns:
        List: Data with missing values
    """
    if seed is not None:
        random.seed(seed)
    
    result = list(data)
    for i in range(len(result)):
        if random.random() < probability:
            result[i] = None
    
    return result


def sample_from_distribution(
    data: Union[List, np.ndarray],
    count: int = 1,
    seed: Optional[int] = None
) -> np.ndarray:
    """
    Sample from empirical distribution of provided data.
    
    Args:
        data: Data to sample from (non-parametric)
        count: Number of samples to generate
        seed: Random seed for reproducibility
        
    Returns:
        np.ndarray: Sampled values
    """
    if seed is not None:
        np.random.seed(seed)
    
    # Remove any None/NaN values
    clean_data = [x for x in data if x is not None and not (isinstance(x, float) and np.isnan(x))]
    
    if len(clean_data) == 0:
        raise ValueError("No valid data points to sample from")
    
    # Simple random sampling with replacement
    indices = np.random.randint(0, len(clean_data), count)
    return np.array([clean_data[i] for i in indices])


def create_dependent_categorical(
    base_values: List[Any],
    conditional_probabilities: Dict[Any, Dict[Any, float]],
    count: int = None,
    seed: Optional[int] = None
) -> List[Any]:
    """
    Create dependent categorical variable based on another variable.
    
    Args:
        base_values: Values of the independent variable
        conditional_probabilities: Mapping {base_value: {result_value: probability}}
        count: Number of values to generate (defaults to length of base_values)
        seed: Random seed for reproducibility
        
    Returns:
        List[Any]: Dependent categorical values
    """
    if seed is not None:
        random.seed(seed)
    
    count = count or len(base_values)
    result = []
    
    for i in range(min(count, len(base_values))):
        base = base_values[i]
        
        # Get conditional distribution for this base value
        if base in conditional_probabilities:
            dist = conditional_probabilities[base]
            categories = list(dist.keys())
            probabilities = list(dist.values())
            
            # Normalize probabilities
            total = sum(probabilities)
            if abs(total - 1.0) > 1e-10:
                probabilities = [p / total for p in probabilities]
            
            # Sample from conditional distribution
            value = random.choices(categories, weights=probabilities, k=1)[0]
        else:
            # If no mapping exists, choose a random value
            all_categories = set()
            for dist in conditional_probabilities.values():
                all_categories.update(dist.keys())
            value = random.choice(list(all_categories)) if all_categories else None
        
        result.append(value)
    
    # Fill remaining values if count > len(base_values)
    if count > len(base_values):
        # Choose random mappings for the extra values
        all_categories = set()
        for dist in conditional_probabilities.values():
            all_categories.update(dist.keys())
        
        for _ in range(count - len(base_values)):
            result.append(random.choice(list(all_categories)) if all_categories else None)
    
    return result
