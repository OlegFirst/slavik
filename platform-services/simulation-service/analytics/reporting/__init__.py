"""
Report Generation

Generate reports in various formats (PDF, HTML, Excel).
"""

from typing import Dict, Any, Optional
from datetime import datetime


def generate_executive_summary(results: Dict[str, Any]) -> str:
    """
    Generate executive summary from simulation results

    Args:
        results: Simulation results

    Returns:
        Executive summary text
    """
    summary_parts = [
        "# Executive Summary",
        "",
        f"**Simulation**: {results.get('simulation_name', 'Unknown')}",
        f"**Execution Date**: {datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}",
        f"**Status**: {results.get('status', 'unknown').upper()}",
        "",
        "## Key Findings",
        ""
    ]

    # Add key findings
    for finding in results.get('key_findings', []):
        summary_parts.append(f"- {finding}")

    # Add statistics
    if 'statistics' in results:
        stats = results['statistics']
        summary_parts.extend([
            "",
            "## Statistical Summary",
            "",
            f"- **Mean**: {stats.get('mean', 'N/A')}",
            f"- **Median**: {stats.get('median', 'N/A')}",
            f"- **Standard Deviation**: {stats.get('std_dev', 'N/A')}",
            f"- **Range**: {stats.get('min', 'N/A')} - {stats.get('max', 'N/A')}",
        ])

    # Add recommendations
    if 'recommendations' in results:
        summary_parts.extend([
            "",
            "## Recommendations",
            ""
        ])
        for rec in results['recommendations']:
            summary_parts.append(f"- {rec}")

    return "\n".join(summary_parts)


def format_for_html(results: Dict[str, Any]) -> str:
    """Format results as HTML"""
    html_template = """
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <title>Simulation Report</title>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 40px; }}
            h1 {{ color: #333; }}
            .stat {{ display: inline-block; margin: 10px; padding: 15px;
                    background: #f5f5f5; border-radius: 5px; }}
            .finding {{ margin: 10px 0; padding: 10px; background: #e8f4f8; }}
        </style>
    </head>
    <body>
        <h1>Simulation Report: {simulation_name}</h1>
        <p><strong>Status:</strong> {status}</p>
        <p><strong>Duration:</strong> {duration} seconds</p>

        <h2>Statistics</h2>
        <div class="stats-container">
            {statistics_html}
        </div>

        <h2>Key Findings</h2>
        {findings_html}
    </body>
    </html>
    """

    stats_html = ""
    if 'statistics' in results:
        for key, value in results['statistics'].items():
            stats_html += f'<div class="stat"><strong>{key}:</strong> {value}</div>'

    findings_html = ""
    for finding in results.get('key_findings', []):
        findings_html += f'<div class="finding">{finding}</div>'

    return html_template.format(
        simulation_name=results.get('simulation_name', 'Unknown'),
        status=results.get('status', 'unknown'),
        duration=results.get('duration', 0),
        statistics_html=stats_html,
        findings_html=findings_html
    )


__all__ = [
    "generate_executive_summary",
    "format_for_html",
]
