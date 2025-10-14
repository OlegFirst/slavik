"""
Data Validation Utilities

Provides validation functions for simulation parameters, scenarios, and inputs.
"""

import re
from typing import Dict, Any, Optional, List
from pydantic import BaseModel, ValidationError
import logging

logger = logging.getLogger(__name__)


def validate_simulation_params(params: Dict[str, Any], simulation_type: str) -> Dict[str, Any]:
    """
    Validate simulation parameters based on simulation type

    Args:
        params: Parameter dictionary
        simulation_type: Type of simulation (what_if, monte_carlo, etc.)

    Returns:
        Validated and sanitized parameters

    Raises:
        ValueError: If parameters are invalid
    """
    if not isinstance(params, dict):
        raise ValueError("Parameters must be a dictionary")

    # Type-specific validation
    validators = {
        "what_if": _validate_what_if_params,
        "monte_carlo": _validate_monte_carlo_params,
        "scenario": _validate_scenario_params,
        "bia": _validate_bia_params,
        "jaamsim": _validate_jaamsim_params,
    }

    validator = validators.get(simulation_type)
    if not validator:
        raise ValueError(f"Unknown simulation type: {simulation_type}")

    return validator(params)


def _validate_what_if_params(params: Dict[str, Any]) -> Dict[str, Any]:
    """Validate what-if simulation parameters"""
    required = ["variable", "values"]
    for field in required:
        if field not in params:
            raise ValueError(f"Missing required parameter: {field}")

    if not isinstance(params["values"], list):
        raise ValueError("'values' must be a list")

    return params


def _validate_monte_carlo_params(params: Dict[str, Any]) -> Dict[str, Any]:
    """Validate Monte Carlo simulation parameters"""
    required = ["iterations", "variables"]
    for field in required:
        if field not in params:
            raise ValueError(f"Missing required parameter: {field}")

    if not isinstance(params["iterations"], int) or params["iterations"] < 100:
        raise ValueError("'iterations' must be an integer >= 100")

    if not isinstance(params["variables"], dict):
        raise ValueError("'variables' must be a dictionary")

    return params


def _validate_scenario_params(params: Dict[str, Any]) -> Dict[str, Any]:
    """Validate BCM scenario parameters"""
    required = ["scenario_id"]
    for field in required:
        if field not in params:
            raise ValueError(f"Missing required parameter: {field}")

    return params


def _validate_bia_params(params: Dict[str, Any]) -> Dict[str, Any]:
    """Validate BIA simulation parameters"""
    required = ["arrival_rate", "service_rate"]
    for field in required:
        if field not in params:
            raise ValueError(f"Missing required parameter: {field}")

    if params["arrival_rate"] <= 0 or params["service_rate"] <= 0:
        raise ValueError("Rates must be positive numbers")

    return params


def _validate_jaamsim_params(params: Dict[str, Any]) -> Dict[str, Any]:
    """Validate JaamSim simulation parameters"""
    required = ["model_file", "duration"]
    for field in required:
        if field not in params:
            raise ValueError(f"Missing required parameter: {field}")

    return params


def validate_scenario_data(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Validate scenario data structure

    Args:
        data: Scenario data dictionary

    Returns:
        Validated scenario data

    Raises:
        ValueError: If data is invalid
    """
    required_fields = ["title", "category"]
    for field in required_fields:
        if field not in data:
            raise ValueError(f"Missing required field: {field}")

    # Validate category
    valid_categories = [
        "cyber", "pandemic", "disaster", "supply_chain",
        "data_breach", "power_outage", "natural_disaster"
    ]
    if data["category"] not in valid_categories:
        raise ValueError(f"Invalid category. Must be one of: {valid_categories}")

    # Validate complexity if provided
    if "complexity" in data:
        complexity = data["complexity"]
        if not isinstance(complexity, int) or complexity < 1 or complexity > 5:
            raise ValueError("Complexity must be an integer between 1 and 5")

    return data


def sanitize_input(value: str, max_length: int = 1000) -> str:
    """
    Sanitize user input to prevent injection attacks

    Args:
        value: Input string
        max_length: Maximum allowed length

    Returns:
        Sanitized string
    """
    if not isinstance(value, str):
        value = str(value)

    # Trim to max length
    value = value[:max_length]

    # Remove potentially dangerous characters
    value = re.sub(r'[<>\"\'%;()&+]', '', value)

    # Trim whitespace
    value = value.strip()

    return value


def validate_tenant_id(tenant_id: str) -> bool:
    """
    Validate tenant ID format

    Args:
        tenant_id: Tenant identifier

    Returns:
        True if valid, False otherwise
    """
    if not tenant_id:
        return False

    # Tenant ID should be alphanumeric with hyphens/underscores
    pattern = r'^[a-zA-Z0-9_-]+$'
    return bool(re.match(pattern, tenant_id))


def validate_json_structure(data: Any, required_keys: List[str]) -> bool:
    """
    Validate JSON structure has required keys

    Args:
        data: Data to validate
        required_keys: List of required keys

    Returns:
        True if valid, False otherwise
    """
    if not isinstance(data, dict):
        return False

    return all(key in data for key in required_keys)
