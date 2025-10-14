"""
DateTime Helper Utilities

Common date/time operations for simulations.
"""

from datetime import datetime, timedelta, timezone
from typing import Optional, Union
import re


def parse_duration(duration_str: str) -> timedelta:
    """
    Parse duration string to timedelta

    Supports formats:
    - "1h" (1 hour)
    - "30m" (30 minutes)
    - "2h30m" (2 hours 30 minutes)
    - "1d" (1 day)
    - "3600s" (3600 seconds)

    Args:
        duration_str: Duration string

    Returns:
        timedelta object

    Raises:
        ValueError: If format is invalid
    """
    if not duration_str:
        raise ValueError("Duration string cannot be empty")

    # Pattern: number followed by unit (d/h/m/s)
    pattern = r'(?:(\d+)d)?(?:(\d+)h)?(?:(\d+)m)?(?:(\d+)s)?'
    match = re.match(pattern, duration_str.lower())

    if not match:
        raise ValueError(f"Invalid duration format: {duration_str}")

    days, hours, minutes, seconds = match.groups()

    delta = timedelta(
        days=int(days or 0),
        hours=int(hours or 0),
        minutes=int(minutes or 0),
        seconds=int(seconds or 0)
    )

    if delta.total_seconds() == 0:
        raise ValueError("Duration must be greater than zero")

    return delta


def format_timestamp(dt: Optional[datetime] = None, iso_format: bool = True) -> str:
    """
    Format datetime to string

    Args:
        dt: Datetime object (defaults to now)
        iso_format: Use ISO 8601 format

    Returns:
        Formatted timestamp string
    """
    if dt is None:
        dt = datetime.now(timezone.utc)

    if iso_format:
        return dt.isoformat()
    else:
        return dt.strftime("%Y-%m-%d %H:%M:%S")


def calculate_elapsed_time(start: datetime, end: Optional[datetime] = None) -> float:
    """
    Calculate elapsed time in seconds

    Args:
        start: Start datetime
        end: End datetime (defaults to now)

    Returns:
        Elapsed time in seconds
    """
    if end is None:
        end = datetime.now(timezone.utc)

    # Ensure both are timezone-aware
    if start.tzinfo is None:
        start = start.replace(tzinfo=timezone.utc)
    if end.tzinfo is None:
        end = end.replace(tzinfo=timezone.utc)

    delta = end - start
    return delta.total_seconds()


def format_duration(seconds: float) -> str:
    """
    Format duration in seconds to human-readable string

    Args:
        seconds: Duration in seconds

    Returns:
        Human-readable duration (e.g., "2h 30m 15s")
    """
    if seconds < 0:
        return "0s"

    days = int(seconds // 86400)
    remaining = seconds % 86400
    hours = int(remaining // 3600)
    remaining = remaining % 3600
    minutes = int(remaining // 60)
    secs = int(remaining % 60)

    parts = []
    if days > 0:
        parts.append(f"{days}d")
    if hours > 0:
        parts.append(f"{hours}h")
    if minutes > 0:
        parts.append(f"{minutes}m")
    if secs > 0 or not parts:
        parts.append(f"{secs}s")

    return " ".join(parts)


def parse_timestamp(timestamp_str: str) -> datetime:
    """
    Parse timestamp string to datetime

    Supports ISO 8601 and common formats

    Args:
        timestamp_str: Timestamp string

    Returns:
        datetime object

    Raises:
        ValueError: If format is invalid
    """
    formats = [
        "%Y-%m-%dT%H:%M:%S.%fZ",
        "%Y-%m-%dT%H:%M:%SZ",
        "%Y-%m-%d %H:%M:%S",
        "%Y-%m-%d",
    ]

    for fmt in formats:
        try:
            dt = datetime.strptime(timestamp_str, fmt)
            return dt.replace(tzinfo=timezone.utc)
        except ValueError:
            continue

    # Try ISO format
    try:
        return datetime.fromisoformat(timestamp_str)
    except ValueError:
        raise ValueError(f"Unable to parse timestamp: {timestamp_str}")


def get_utc_now() -> datetime:
    """Get current UTC time"""
    return datetime.now(timezone.utc)


def is_future(dt: datetime) -> bool:
    """Check if datetime is in the future"""
    now = get_utc_now()
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt > now


def is_past(dt: datetime) -> bool:
    """Check if datetime is in the past"""
    return not is_future(dt)
