"""
Unit tests for utility functions
"""

import pytest
from datetime import datetime, timedelta
from utils.validators import (
    validate_simulation_params,
    validate_scenario_data,
    sanitize_input
)
from utils.datetime_helpers import (
    parse_duration,
    format_timestamp,
    calculate_elapsed_time
)
from utils.math_utils import (
    calculate_percentile,
    normalize_values,
    calculate_statistics
)


class TestValidators:
    """Test validation utilities"""

    def test_validate_what_if_params(self):
        """Test what-if parameter validation"""
        params = {
            "variable": "recovery_time",
            "values": [1, 2, 3, 4, 5]
        }
        result = validate_simulation_params(params, "what_if")
        assert result == params

    def test_validate_monte_carlo_params(self):
        """Test Monte Carlo parameter validation"""
        params = {
            "iterations": 1000,
            "variables": {
                "recovery_time": {"distribution": "normal", "mean": 4, "std": 1}
            }
        }
        result = validate_simulation_params(params, "monte_carlo")
        assert result == params

    def test_sanitize_input(self):
        """Test input sanitization"""
        malicious = "<script>alert('xss')</script>"
        clean = sanitize_input(malicious)
        assert "<" not in clean
        assert ">" not in clean


class TestDateTimeHelpers:
    """Test datetime utilities"""

    def test_parse_duration_hours(self):
        """Test parsing hour duration"""
        duration = parse_duration("2h")
        assert duration == timedelta(hours=2)

    def test_parse_duration_complex(self):
        """Test parsing complex duration"""
        duration = parse_duration("2h30m15s")
        assert duration == timedelta(hours=2, minutes=30, seconds=15)

    def test_format_timestamp(self):
        """Test timestamp formatting"""
        dt = datetime(2025, 10, 14, 12, 0, 0)
        formatted = format_timestamp(dt, iso_format=True)
        assert "2025-10-14" in formatted


class TestMathUtils:
    """Test mathematical utilities"""

    def test_calculate_percentile(self):
        """Test percentile calculation"""
        data = list(range(1, 101))  # 1 to 100
        p50 = calculate_percentile(data, 50)
        assert 49 <= p50 <= 51  # Median should be around 50

    def test_normalize_values(self):
        """Test value normalization"""
        values = [1, 2, 3, 4, 5]
        normalized = normalize_values(values, 0, 1)
        assert min(normalized) == 0
        assert max(normalized) == 1

    def test_calculate_statistics(self):
        """Test statistics calculation"""
        data = [1, 2, 3, 4, 5]
        stats = calculate_statistics(data)
        assert stats["mean"] == 3.0
        assert stats["median"] == 3.0
        assert stats["min"] == 1
        assert stats["max"] == 5
