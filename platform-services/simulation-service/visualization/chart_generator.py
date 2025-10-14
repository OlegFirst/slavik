"""
Chart Generation Utilities

Generate chart configurations for visualization libraries (Chart.js, Plotly, etc.)
"""

from typing import Dict, Any, List, Optional
from datetime import datetime


def generate_time_series_chart(
    data: List[Dict[str, Any]],
    x_field: str = "timestamp",
    y_field: str = "value",
    title: Optional[str] = None
) -> Dict[str, Any]:
    """
    Generate time series chart configuration

    Args:
        data: List of data points
        x_field: Field name for X-axis (timestamps)
        y_field: Field name for Y-axis (values)
        title: Chart title

    Returns:
        Chart.js compatible configuration
    """
    labels = [point[x_field] for point in data]
    values = [point[y_field] for point in data]

    return {
        "type": "line",
        "data": {
            "labels": labels,
            "datasets": [{
                "label": y_field.replace("_", " ").title(),
                "data": values,
                "borderColor": "rgb(75, 192, 192)",
                "backgroundColor": "rgba(75, 192, 192, 0.2)",
                "tension": 0.1
            }]
        },
        "options": {
            "responsive": True,
            "plugins": {
                "title": {
                    "display": bool(title),
                    "text": title or "Time Series"
                },
                "legend": {
                    "display": True,
                    "position": "top"
                }
            },
            "scales": {
                "x": {
                    "display": True,
                    "title": {
                        "display": True,
                        "text": x_field.replace("_", " ").title()
                    }
                },
                "y": {
                    "display": True,
                    "title": {
                        "display": True,
                        "text": y_field.replace("_", " ").title()
                    }
                }
            }
        }
    }


def generate_distribution_chart(
    data: List[float],
    bins: int = 20,
    title: Optional[str] = None
) -> Dict[str, Any]:
    """
    Generate histogram/distribution chart

    Args:
        data: List of values
        bins: Number of bins for histogram
        title: Chart title

    Returns:
        Chart configuration
    """
    # Calculate histogram bins
    min_val = min(data)
    max_val = max(data)
    bin_width = (max_val - min_val) / bins

    bin_counts = [0] * bins
    bin_labels = []

    for i in range(bins):
        bin_start = min_val + i * bin_width
        bin_end = bin_start + bin_width
        bin_labels.append(f"{bin_start:.2f}-{bin_end:.2f}")

        count = sum(1 for v in data if bin_start <= v < bin_end)
        bin_counts[i] = count

    return {
        "type": "bar",
        "data": {
            "labels": bin_labels,
            "datasets": [{
                "label": "Frequency",
                "data": bin_counts,
                "backgroundColor": "rgba(54, 162, 235, 0.6)",
                "borderColor": "rgb(54, 162, 235)",
                "borderWidth": 1
            }]
        },
        "options": {
            "responsive": True,
            "plugins": {
                "title": {
                    "display": bool(title),
                    "text": title or "Distribution"
                },
                "legend": {
                    "display": False
                }
            },
            "scales": {
                "x": {
                    "title": {
                        "display": True,
                        "text": "Value Range"
                    }
                },
                "y": {
                    "title": {
                        "display": True,
                        "text": "Frequency"
                    },
                    "beginAtZero": True
                }
            }
        }
    }


def generate_comparison_chart(
    categories: List[str],
    datasets: List[Dict[str, Any]],
    title: Optional[str] = None
) -> Dict[str, Any]:
    """
    Generate comparison bar chart

    Args:
        categories: Category labels
        datasets: List of dataset configs with 'label' and 'data'
        title: Chart title

    Returns:
        Chart configuration
    """
    colors = [
        "rgba(255, 99, 132, 0.6)",
        "rgba(54, 162, 235, 0.6)",
        "rgba(255, 206, 86, 0.6)",
        "rgba(75, 192, 192, 0.6)",
        "rgba(153, 102, 255, 0.6)"
    ]

    for i, dataset in enumerate(datasets):
        dataset["backgroundColor"] = colors[i % len(colors)]
        dataset["borderColor"] = colors[i % len(colors)].replace("0.6", "1")
        dataset["borderWidth"] = 1

    return {
        "type": "bar",
        "data": {
            "labels": categories,
            "datasets": datasets
        },
        "options": {
            "responsive": True,
            "plugins": {
                "title": {
                    "display": bool(title),
                    "text": title or "Comparison"
                },
                "legend": {
                    "display": True,
                    "position": "top"
                }
            },
            "scales": {
                "y": {
                    "beginAtZero": True
                }
            }
        }
    }


def generate_execution_dashboard(execution_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Generate complete execution dashboard

    Args:
        execution_data: Execution data including progress, metrics, results

    Returns:
        Dashboard configuration with multiple charts
    """
    dashboard = {
        "title": f"Simulation Execution: {execution_data.get('simulation_name', 'Unknown')}",
        "execution_id": execution_data.get("id"),
        "status": execution_data.get("status"),
        "progress": execution_data.get("progress", 0),
        "charts": []
    }

    # Progress gauge
    dashboard["charts"].append({
        "id": "progress",
        "type": "gauge",
        "title": "Execution Progress",
        "value": execution_data.get("progress", 0),
        "max": 100,
        "unit": "%"
    })

    # Metrics over time (if available)
    if "metrics_history" in execution_data:
        dashboard["charts"].append(
            generate_time_series_chart(
                data=execution_data["metrics_history"],
                x_field="timestamp",
                y_field="value",
                title="Metrics Over Time"
            )
        )

    # Results distribution (if available)
    if "results" in execution_data and "distribution_data" in execution_data["results"]:
        dashboard["charts"].append(
            generate_distribution_chart(
                data=execution_data["results"]["distribution_data"],
                title="Results Distribution"
            )
        )

    # Summary statistics
    if "statistics" in execution_data.get("results", {}):
        stats = execution_data["results"]["statistics"]
        dashboard["statistics"] = {
            "mean": stats.get("mean"),
            "median": stats.get("median"),
            "std_dev": stats.get("std_dev"),
            "min": stats.get("min"),
            "max": stats.get("max")
        }

    return dashboard


def generate_monte_carlo_visualization(results: Dict[str, Any]) -> Dict[str, Any]:
    """
    Generate Monte Carlo specific visualizations

    Args:
        results: Monte Carlo simulation results

    Returns:
        Visualization configuration
    """
    iterations = results.get("iterations", [])

    return {
        "charts": [
            {
                "id": "convergence",
                "title": "Convergence Analysis",
                "config": generate_time_series_chart(
                    data=[
                        {"iteration": i, "value": val}
                        for i, val in enumerate(iterations)
                    ],
                    x_field="iteration",
                    y_field="value",
                    title="Monte Carlo Convergence"
                )
            },
            {
                "id": "distribution",
                "title": "Results Distribution",
                "config": generate_distribution_chart(
                    data=iterations,
                    bins=30,
                    title="Monte Carlo Results Distribution"
                )
            }
        ],
        "statistics": results.get("statistics", {})
    }
