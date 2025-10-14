"""
Analytics and Reporting

Advanced analytics engines and report generation for simulation results.
"""

from .report_generator import (
    generate_pdf_report,
    generate_html_report,
    generate_excel_report
)
from .trend_analyzer import (
    analyze_trends,
    detect_patterns,
    predict_outcomes
)

__all__ = [
    "generate_pdf_report",
    "generate_html_report",
    "generate_excel_report",
    "analyze_trends",
    "detect_patterns",
    "predict_outcomes",
]
