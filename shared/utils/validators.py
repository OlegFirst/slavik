"""
Common Validators
=================

Reusable validation functions for BCM Platform.

Features:
- Email validation
- URL validation
- Date range validation
- Tenant ID validation
"""

import re
from datetime import datetime, date
from typing import Optional
from urllib.parse import urlparse


def validate_email(email: str) -> bool:
    """
    Validate email address format.

    Args:
        email: Email address to validate

    Returns:
        bool: True if valid email format

    Example:
        ```python
        if not validate_email(user_email):
            raise ValidationException("Invalid email format")
        ```
    """
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))


def validate_url(url: str) -> bool:
    """
    Validate URL format.

    Args:
        url: URL to validate

    Returns:
        bool: True if valid URL

    Example:
        ```python
        if not validate_url(callback_url):
            raise ValidationException("Invalid URL format")
        ```
    """
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except Exception:
        return False


def validate_tenant_id(tenant_id: str) -> bool:
    """
    Validate tenant ID format.

    Args:
        tenant_id: Tenant identifier

    Returns:
        bool: True if valid tenant ID

    Example:
        ```python
        if not validate_tenant_id(tenant_id):
            raise ValidationException("Invalid tenant ID")
        ```
    """
    # Tenant ID should be alphanumeric, 3-50 characters
    pattern = r'^[a-zA-Z0-9_-]{3,50}$'
    return bool(re.match(pattern, tenant_id))


def validate_date_range(
    start_date: datetime,
    end_date: datetime,
    max_days: Optional[int] = None
) -> bool:
    """
    Validate date range.

    Args:
        start_date: Start date
        end_date: End date
        max_days: Maximum allowed days in range (optional)

    Returns:
        bool: True if valid date range

    Example:
        ```python
        if not validate_date_range(start_date, end_date, max_days=365):
            raise ValidationException("Invalid date range")
        ```
    """
    # End date must be after start date
    if end_date <= start_date:
        return False

    # Check max days if specified
    if max_days:
        delta = (end_date - start_date).days
        if delta > max_days:
            return False

    return True


def validate_phone_number(phone: str) -> bool:
    """
    Validate phone number format.

    Args:
        phone: Phone number

    Returns:
        bool: True if valid phone format

    Example:
        ```python
        if not validate_phone_number(contact_number):
            raise ValidationException("Invalid phone number")
        ```
    """
    # Simple validation: 10-15 digits, optional + prefix
    pattern = r'^\+?[0-9]{10,15}$'
    return bool(re.match(pattern, phone))


def validate_iso_clause(clause: str) -> bool:
    """
    Validate ISO 22301 clause format.

    Args:
        clause: ISO clause (e.g., "4.1", "8.2.3")

    Returns:
        bool: True if valid clause format

    Example:
        ```python
        if not validate_iso_clause(clause_number):
            raise ValidationException("Invalid ISO clause format")
        ```
    """
    # Format: X.Y or X.Y.Z where X, Y, Z are numbers
    pattern = r'^\d+\.\d+(\.\d+)?$'
    return bool(re.match(pattern, clause))


def sanitize_filename(filename: str) -> str:
    """
    Sanitize filename to prevent path traversal.

    Args:
        filename: Original filename

    Returns:
        str: Sanitized filename

    Example:
        ```python
        safe_name = sanitize_filename(uploaded_file.filename)
        ```
    """
    # Remove path separators and special characters
    sanitized = re.sub(r'[^\w\s.-]', '', filename)
    # Remove leading/trailing dots and spaces
    sanitized = sanitized.strip('. ')
    # Limit length
    if len(sanitized) > 255:
        sanitized = sanitized[:255]
    return sanitized


def validate_kpi_threshold(
    performance_direction: str,
    target: float,
    warning: float,
    critical: float
) -> tuple[bool, Optional[str]]:
    """
    Validate KPI threshold configuration.

    Args:
        performance_direction: "higher_better", "lower_better", or "target_value"
        target: Target value
        warning: Warning threshold
        critical: Critical threshold

    Returns:
        tuple: (is_valid, error_message)

    Example:
        ```python
        valid, error = validate_kpi_threshold(
            "higher_better",
            target=95.0,
            warning=90.0,
            critical=85.0
        )
        if not valid:
            raise ValidationException(error)
        ```
    """
    if performance_direction == "higher_better":
        if not (critical < warning < target):
            return False, "For higher_better: critical < warning < target"

    elif performance_direction == "lower_better":
        if not (target < warning < critical):
            return False, "For lower_better: target < warning < critical"

    elif performance_direction == "target_value":
        # For target_value, warning and critical are tolerances
        if warning < 0 or critical < 0:
            return False, "Tolerances must be positive"
        if critical <= warning:
            return False, "Critical tolerance must be greater than warning"

    else:
        return False, f"Invalid performance_direction: {performance_direction}"

    return True, None


def validate_json_structure(data: dict, required_fields: list[str]) -> tuple[bool, Optional[str]]:
    """
    Validate JSON structure has required fields.

    Args:
        data: JSON data
        required_fields: List of required field names

    Returns:
        tuple: (is_valid, error_message)

    Example:
        ```python
        valid, error = validate_json_structure(
            json_data,
            ["tenant_id", "exercise_type", "planned_date"]
        )
        if not valid:
            raise ValidationException(error)
        ```
    """
    missing_fields = [field for field in required_fields if field not in data]

    if missing_fields:
        return False, f"Missing required fields: {', '.join(missing_fields)}"

    return True, None
