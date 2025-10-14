"""
Data Formatting Utilities

Format simulation results, metrics, and reports for presentation.
"""

from typing import Dict, Any, List, Optional
import json
from datetime import datetime


def format_simulation_results(results: Dict[str, Any]) -> Dict[str, Any]:
    """
    Format simulation results for API response

    Args:
        results: Raw simulation results

    Returns:
        Formatted results dictionary
    """
    formatted = {
        "summary": extract_summary(results),
        "metrics": format_metrics(results.get("metrics", {})),
        "charts_data": prepare_chart_data(results),
        "recommendations": results.get("recommendations", []),
        "metadata": {
            "formatted_at": datetime.utcnow().isoformat(),
            "result_count": len(results.get("data", [])),
        }
    }

    return formatted


def format_metrics(metrics: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Format metrics for display

    Args:
        metrics: Raw metrics dictionary

    Returns:
        List of formatted metric objects
    """
    formatted_metrics = []

    for key, value in metrics.items():
        metric = {
            "name": _humanize_metric_name(key),
            "key": key,
            "value": value,
            "formatted_value": _format_metric_value(value),
        }

        # Add trend indicator if available
        if isinstance(value, dict) and "trend" in value:
            metric["trend"] = value["trend"]

        formatted_metrics.append(metric)

    return formatted_metrics


def _humanize_metric_name(key: str) -> str:
    """Convert snake_case metric name to human-readable"""
    return key.replace("_", " ").title()


def _format_metric_value(value: Any) -> str:
    """Format metric value for display"""
    if isinstance(value, float):
        # Round to 2 decimal places
        return f"{value:.2f}"
    elif isinstance(value, int):
        # Add thousand separators
        return f"{value:,}"
    elif isinstance(value, dict):
        return json.dumps(value, indent=2)
    else:
        return str(value)


def extract_summary(results: Dict[str, Any]) -> Dict[str, Any]:
    """
    Extract key summary information from results

    Args:
        results: Simulation results

    Returns:
        Summary dictionary
    """
    summary = {
        "status": results.get("status", "unknown"),
        "total_iterations": results.get("iterations", 0),
        "duration_seconds": results.get("duration", 0),
        "key_findings": results.get("key_findings", []),
    }

    # Extract statistical summary if available
    if "statistics" in results:
        stats = results["statistics"]
        summary["statistics"] = {
            "mean": stats.get("mean"),
            "median": stats.get("median"),
            "std_dev": stats.get("std_dev"),
            "min": stats.get("min"),
            "max": stats.get("max"),
        }

    return summary


def prepare_chart_data(results: Dict[str, Any]) -> Dict[str, Any]:
    """
    Prepare data for chart visualization

    Args:
        results: Simulation results

    Returns:
        Chart-ready data structure
    """
    chart_data = {}

    # Time series data
    if "time_series" in results:
        chart_data["time_series"] = {
            "labels": results["time_series"].get("timestamps", []),
            "datasets": results["time_series"].get("data", []),
        }

    # Distribution data
    if "distribution" in results:
        chart_data["distribution"] = {
            "bins": results["distribution"].get("bins", []),
            "frequencies": results["distribution"].get("frequencies", []),
        }

    # Comparison data
    if "comparison" in results:
        chart_data["comparison"] = {
            "categories": results["comparison"].get("categories", []),
            "values": results["comparison"].get("values", []),
        }

    return chart_data


def generate_report_summary(
    simulation_id: int,
    simulation_name: str,
    results: Dict[str, Any],
    execution_time: float
) -> str:
    """
    Generate text summary for simulation report

    Args:
        simulation_id: Simulation ID
        simulation_name: Simulation name
        results: Simulation results
        execution_time: Execution time in seconds

    Returns:
        Formatted text summary
    """
    summary_parts = [
        f"Simulation Report: {simulation_name}",
        f"ID: {simulation_id}",
        f"Execution Time: {execution_time:.2f} seconds",
        "",
        "Key Results:",
    ]

    # Add key findings
    for finding in results.get("key_findings", []):
        summary_parts.append(f"- {finding}")

    # Add statistics if available
    if "statistics" in results:
        stats = results["statistics"]
        summary_parts.extend([
            "",
            "Statistical Summary:",
            f"- Mean: {stats.get('mean', 'N/A')}",
            f"- Median: {stats.get('median', 'N/A')}",
            f"- Standard Deviation: {stats.get('std_dev', 'N/A')}",
        ])

    return "\n".join(summary_parts)


def format_percentage(value: float, decimals: int = 2) -> str:
    """Format value as percentage"""
    return f"{value * 100:.{decimals}f}%"


def format_currency(value: float, currency: str = "USD") -> str:
    """Format value as currency"""
    return f"{currency} {value:,.2f}"


def truncate_text(text: str, max_length: int = 100, suffix: str = "...") -> str:
    """Truncate text to maximum length"""
    if len(text) <= max_length:
        return text
    return text[:max_length - len(suffix)] + suffix
