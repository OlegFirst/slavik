"""
KPI Calculation Functions
Based on: bcm_kpi/models/models.py (lines 186-252)
"""

from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
from enum import Enum

class PerformanceStatus(str, Enum):
    """KPI performance status"""
    EXCELLENT = "excellent"
    GOOD = "good"
    WARNING = "warning"
    CRITICAL = "critical"
    NO_DATA = "no_data"

class TrendDirection(str, Enum):
    """KPI trend direction"""
    IMPROVING = "improving"
    STABLE = "stable"
    DECLINING = "declining"
    NO_DATA = "no_data"

def calculate_kpi_status(
    value: float,
    target_value: float,
    warning_threshold: float,
    critical_threshold: float,
    performance_direction: str
) -> PerformanceStatus:
    """
    Calculate KPI performance status based on thresholds

    Based on: bcm_kpi lines 186-228

    Args:
        value: Current measured value
        target_value: Target value for excellent performance
        warning_threshold: Value below which performance is warning
        critical_threshold: Value below which performance is critical
        performance_direction: 'higher_better', 'lower_better', or 'target_value'

    Returns:
        PerformanceStatus enum
    """
    if value is None:
        return PerformanceStatus.NO_DATA

    if performance_direction == 'higher_better':
        if value >= target_value:
            return PerformanceStatus.EXCELLENT
        elif value >= warning_threshold:
            return PerformanceStatus.GOOD
        elif value >= critical_threshold:
            return PerformanceStatus.WARNING
        else:
            return PerformanceStatus.CRITICAL

    elif performance_direction == 'lower_better':
        if value <= target_value:
            return PerformanceStatus.EXCELLENT
        elif value <= warning_threshold:
            return PerformanceStatus.GOOD
        elif value <= critical_threshold:
            return PerformanceStatus.WARNING
        else:
            return PerformanceStatus.CRITICAL

    else:  # target_value
        deviation = abs(value - target_value)
        tolerance_5_pct = target_value * 0.05
        tolerance_10_pct = target_value * 0.10
        tolerance_20_pct = target_value * 0.20

        if deviation <= tolerance_5_pct:
            return PerformanceStatus.EXCELLENT
        elif deviation <= tolerance_10_pct:
            return PerformanceStatus.GOOD
        elif deviation <= tolerance_20_pct:
            return PerformanceStatus.WARNING
        else:
            return PerformanceStatus.CRITICAL

def calculate_kpi_trend(measurements: List[Dict]) -> TrendDirection:
    """
    Calculate trend based on recent measurements

    Based on: bcm_kpi lines 230-252

    Args:
        measurements: List of {measurement_date, value} sorted by date descending

    Returns:
        TrendDirection enum
    """
    if len(measurements) < 2:
        return TrendDirection.NO_DATA

    # Take last 3 measurements for trend analysis
    recent_measurements = measurements[:min(3, len(measurements))]

    if len(recent_measurements) >= 2:
        # Calculate average of 2 most recent
        recent_avg = sum(m['value'] for m in recent_measurements[:2]) / 2

        # Calculate average of older measurements
        older_measurements = recent_measurements[1:]
        older_avg = sum(m['value'] for m in older_measurements) / len(older_measurements)

        # Calculate percentage difference
        if older_avg != 0:
            diff_pct = (recent_avg - older_avg) / older_avg * 100
        else:
            diff_pct = 0

        # Determine trend
        if diff_pct > 5:
            return TrendDirection.IMPROVING
        elif diff_pct < -5:
            return TrendDirection.DECLINING
        else:
            return TrendDirection.STABLE

    return TrendDirection.NO_DATA

def calculate_performance_threshold(
    measurements: List[float],
    percentile: float = 90
) -> float:
    """
    Calculate performance threshold based on historical data

    Args:
        measurements: List of measurement values
        percentile: Percentile for threshold (default 90th percentile)

    Returns:
        Threshold value
    """
    if not measurements:
        return 0.0

    sorted_measurements = sorted(measurements)
    index = int(len(sorted_measurements) * (percentile / 100))
    return sorted_measurements[min(index, len(sorted_measurements) - 1)]

def aggregate_measurements(
    measurements: List[Dict],
    aggregation_type: str = 'average'
) -> Optional[float]:
    """
    Aggregate measurements over a period

    Args:
        measurements: List of {measurement_date, value}
        aggregation_type: 'average', 'sum', 'min', 'max', 'latest'

    Returns:
        Aggregated value or None
    """
    if not measurements:
        return None

    values = [m['value'] for m in measurements]

    if aggregation_type == 'average':
        return sum(values) / len(values)
    elif aggregation_type == 'sum':
        return sum(values)
    elif aggregation_type == 'min':
        return min(values)
    elif aggregation_type == 'max':
        return max(values)
    elif aggregation_type == 'latest':
        return measurements[0]['value']  # Assuming sorted descending
    else:
        return sum(values) / len(values)  # Default to average

def get_kpi_summary(measurements: List[Dict], kpi_config: Dict) -> Dict:
    """
    Generate comprehensive KPI summary

    Args:
        measurements: List of measurements
        kpi_config: KPI configuration with target, thresholds, direction

    Returns:
        Dict with current_value, status, trend, statistics
    """
    if not measurements:
        return {
            'current_value': None,
            'status': PerformanceStatus.NO_DATA.value,
            'trend': TrendDirection.NO_DATA.value,
            'measurement_count': 0,
        }

    # Latest value
    current_value = measurements[0]['value']

    # Calculate status
    status = calculate_kpi_status(
        current_value,
        kpi_config.get('target_value', 100),
        kpi_config.get('warning_threshold', 70),
        kpi_config.get('critical_threshold', 50),
        kpi_config.get('performance_direction', 'higher_better')
    )

    # Calculate trend
    trend = calculate_kpi_trend(measurements)

    # Statistics
    values = [m['value'] for m in measurements]

    return {
        'current_value': current_value,
        'status': status.value,
        'trend': trend.value,
        'measurement_count': len(measurements),
        'average': sum(values) / len(values),
        'min': min(values),
        'max': max(values),
        'last_measurement_date': measurements[0]['measurement_date'],
    }

# BCI GPG Recommended KPIs
BCI_RECOMMENDED_KPIS = [
    {
        'kpi_code': 'bia_coverage',
        'kpi_name': '% Critical Processes with BC Plans',
        'target_value': 100,
        'warning_threshold': 80,
        'critical_threshold': 60,
        'performance_direction': 'higher_better',
        'measurement_unit': '%',
    },
    {
        'kpi_code': 'plan_currency',
        'kpi_name': '% Plans Reviewed in Last 12 Months',
        'target_value': 100,
        'warning_threshold': 80,
        'critical_threshold': 60,
        'performance_direction': 'higher_better',
        'measurement_unit': '%',
    },
    {
        'kpi_code': 'exercise_completion',
        'kpi_name': '% Critical Processes Tested Annually',
        'target_value': 100,
        'warning_threshold': 75,
        'critical_threshold': 50,
        'performance_direction': 'higher_better',
        'measurement_unit': '%',
    },
    {
        'kpi_code': 'rto_achievement',
        'kpi_name': '% RTO Objectives Achieved in Tests',
        'target_value': 95,
        'warning_threshold': 85,
        'critical_threshold': 70,
        'performance_direction': 'higher_better',
        'measurement_unit': '%',
    },
    {
        'kpi_code': 'training_completion',
        'kpi_name': '% BC Team Trained in Last 12 Months',
        'target_value': 100,
        'warning_threshold': 90,
        'critical_threshold': 75,
        'performance_direction': 'higher_better',
        'measurement_unit': '%',
    },
    {
        'kpi_code': 'incident_response_time',
        'kpi_name': 'Average Incident Response Time',
        'target_value': 15,  # minutes
        'warning_threshold': 30,
        'critical_threshold': 60,
        'performance_direction': 'lower_better',
        'measurement_unit': 'minutes',
    },
    {
        'kpi_code': 'capa_on_time',
        'kpi_name': '% Corrective Actions Completed On Time',
        'target_value': 90,
        'warning_threshold': 75,
        'critical_threshold': 60,
        'performance_direction': 'higher_better',
        'measurement_unit': '%',
    },
    {
        'kpi_code': 'audit_closure',
        'kpi_name': 'Audit Findings Closure Rate',
        'target_value': 100,
        'warning_threshold': 85,
        'critical_threshold': 70,
        'performance_direction': 'higher_better',
        'measurement_unit': '%',
    },
]
