"""
Mathematical Utilities

Statistical and mathematical operations for simulation analysis.
"""

from typing import List, Dict, Any, Tuple, Optional
import statistics
import math


def calculate_percentile(data: List[float], percentile: float) -> float:
    """
    Calculate percentile value from data

    Args:
        data: List of numeric values
        percentile: Percentile to calculate (0-100)

    Returns:
        Percentile value

    Raises:
        ValueError: If data is empty or percentile is invalid
    """
    if not data:
        raise ValueError("Data list cannot be empty")

    if not 0 <= percentile <= 100:
        raise ValueError("Percentile must be between 0 and 100")

    sorted_data = sorted(data)
    n = len(sorted_data)

    if percentile == 0:
        return sorted_data[0]
    if percentile == 100:
        return sorted_data[-1]

    # Linear interpolation
    index = (percentile / 100) * (n - 1)
    lower_index = int(math.floor(index))
    upper_index = int(math.ceil(index))

    if lower_index == upper_index:
        return sorted_data[lower_index]

    lower_value = sorted_data[lower_index]
    upper_value = sorted_data[upper_index]
    fraction = index - lower_index

    return lower_value + (upper_value - lower_value) * fraction


def normalize_values(values: List[float], min_val: float = 0.0, max_val: float = 1.0) -> List[float]:
    """
    Normalize values to specified range

    Args:
        values: List of values to normalize
        min_val: Minimum value in output range
        max_val: Maximum value in output range

    Returns:
        List of normalized values
    """
    if not values:
        return []

    data_min = min(values)
    data_max = max(values)

    if data_max == data_min:
        # All values are the same
        return [min_val] * len(values)

    normalized = []
    for value in values:
        norm_value = ((value - data_min) / (data_max - data_min)) * (max_val - min_val) + min_val
        normalized.append(norm_value)

    return normalized


def calculate_statistics(data: List[float]) -> Dict[str, float]:
    """
    Calculate comprehensive statistics for dataset

    Args:
        data: List of numeric values

    Returns:
        Dictionary with statistical measures
    """
    if not data:
        return {
            "count": 0,
            "mean": 0.0,
            "median": 0.0,
            "std_dev": 0.0,
            "variance": 0.0,
            "min": 0.0,
            "max": 0.0,
            "range": 0.0,
        }

    return {
        "count": len(data),
        "mean": statistics.mean(data),
        "median": statistics.median(data),
        "std_dev": statistics.stdev(data) if len(data) > 1 else 0.0,
        "variance": statistics.variance(data) if len(data) > 1 else 0.0,
        "min": min(data),
        "max": max(data),
        "range": max(data) - min(data),
        "p25": calculate_percentile(data, 25),
        "p50": calculate_percentile(data, 50),
        "p75": calculate_percentile(data, 75),
        "p95": calculate_percentile(data, 95),
        "p99": calculate_percentile(data, 99),
    }


def calculate_confidence_interval(
    data: List[float],
    confidence_level: float = 0.95
) -> Tuple[float, float]:
    """
    Calculate confidence interval for data

    Args:
        data: List of numeric values
        confidence_level: Confidence level (0-1)

    Returns:
        Tuple of (lower_bound, upper_bound)
    """
    if len(data) < 2:
        raise ValueError("Need at least 2 data points for confidence interval")

    mean = statistics.mean(data)
    std_dev = statistics.stdev(data)
    n = len(data)

    # Using normal distribution approximation
    # For more accurate results, use t-distribution
    z_score = 1.96 if confidence_level == 0.95 else 2.576  # 95% or 99%
    margin_of_error = z_score * (std_dev / math.sqrt(n))

    return (mean - margin_of_error, mean + margin_of_error)


def calculate_correlation(x: List[float], y: List[float]) -> float:
    """
    Calculate Pearson correlation coefficient

    Args:
        x: First variable values
        y: Second variable values

    Returns:
        Correlation coefficient (-1 to 1)

    Raises:
        ValueError: If lists have different lengths or less than 2 points
    """
    if len(x) != len(y):
        raise ValueError("Lists must have same length")

    if len(x) < 2:
        raise ValueError("Need at least 2 data points")

    n = len(x)
    mean_x = statistics.mean(x)
    mean_y = statistics.mean(y)

    numerator = sum((x[i] - mean_x) * (y[i] - mean_y) for i in range(n))

    sum_sq_x = sum((x[i] - mean_x) ** 2 for i in range(n))
    sum_sq_y = sum((y[i] - mean_y) ** 2 for i in range(n))
    denominator = math.sqrt(sum_sq_x * sum_sq_y)

    if denominator == 0:
        return 0.0

    return numerator / denominator


def moving_average(data: List[float], window_size: int) -> List[float]:
    """
    Calculate moving average

    Args:
        data: Time series data
        window_size: Size of moving window

    Returns:
        List of moving averages
    """
    if window_size < 1:
        raise ValueError("Window size must be at least 1")

    if len(data) < window_size:
        return []

    averages = []
    for i in range(len(data) - window_size + 1):
        window = data[i:i + window_size]
        averages.append(statistics.mean(window))

    return averages


def weighted_average(values: List[float], weights: List[float]) -> float:
    """
    Calculate weighted average

    Args:
        values: List of values
        weights: List of weights

    Returns:
        Weighted average

    Raises:
        ValueError: If lists have different lengths
    """
    if len(values) != len(weights):
        raise ValueError("Values and weights must have same length")

    if not values:
        return 0.0

    total_weight = sum(weights)
    if total_weight == 0:
        return 0.0

    weighted_sum = sum(v * w for v, w in zip(values, weights))
    return weighted_sum / total_weight


def exponential_smoothing(data: List[float], alpha: float = 0.3) -> List[float]:
    """
    Apply exponential smoothing to time series

    Args:
        data: Time series data
        alpha: Smoothing factor (0-1)

    Returns:
        Smoothed series
    """
    if not 0 <= alpha <= 1:
        raise ValueError("Alpha must be between 0 and 1")

    if not data:
        return []

    smoothed = [data[0]]
    for i in range(1, len(data)):
        smoothed_value = alpha * data[i] + (1 - alpha) * smoothed[-1]
        smoothed.append(smoothed_value)

    return smoothed
