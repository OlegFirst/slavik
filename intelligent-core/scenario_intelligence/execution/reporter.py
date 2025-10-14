"""
Execution Reporter - Generates reports from execution results

Responsibilities:
- Generate comprehensive execution reports
- Support multiple output formats (JSON, HTML)
- Aggregate statistics
- Export capabilities
"""

import json
import logging
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, asdict
from datetime import datetime

from .executor import ExecutionResult
from .validator import ValidationReport

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class ExecutionReport:
    """Complete execution report"""
    report_id: str
    report_type: str  # 'single', 'batch', 'workflow'
    generated_at: str

    # Results
    executions: List[Dict[str, Any]]  # ExecutionResult.to_dict()
    validations: List[Dict[str, Any]]  # ValidationReport.to_dict()

    # Summary
    summary: Dict[str, Any]

    # Metadata
    metadata: Optional[Dict[str, Any]] = None

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class ExecutionReporter:
    """
    Generates execution reports

    Supports:
    - Single scenario reports
    - Batch execution reports
    - Workflow reports
    - JSON and HTML export
    """

    def generate_report(
        self,
        results: List[ExecutionResult],
        validations: Optional[List[ValidationReport]] = None,
        report_type: str = 'batch',
        metadata: Optional[Dict[str, Any]] = None
    ) -> ExecutionReport:
        """
        Generate comprehensive execution report

        Args:
            results: List of execution results
            validations: Optional validation reports
            report_type: Type of report ('single', 'batch', 'workflow')
            metadata: Additional metadata

        Returns:
            ExecutionReport
        """
        logger.info(f"📊 Generating {report_type} report for {len(results)} execution(s)")

        report_id = f"report-{datetime.utcnow().strftime('%Y%m%d-%H%M%S')}"

        # Convert results to dicts
        executions_dict = [r.to_dict() for r in results]

        # Convert validations to dicts
        validations_dict = []
        if validations:
            validations_dict = [v.to_dict() for v in validations]

        # Generate summary
        summary = self._generate_summary(results, validations)

        report = ExecutionReport(
            report_id=report_id,
            report_type=report_type,
            generated_at=datetime.utcnow().isoformat(),
            executions=executions_dict,
            validations=validations_dict,
            summary=summary,
            metadata=metadata or {}
        )

        logger.info(f"  ✅ Report generated: {report_id}")
        logger.info(f"     Status: {summary['overall_status']}")
        logger.info(f"     Success Rate: {summary['success_rate']:.1%}")

        return report

    def _generate_summary(
        self,
        results: List[ExecutionResult],
        validations: Optional[List[ValidationReport]] = None
    ) -> Dict[str, Any]:
        """Generate summary statistics"""

        total_executions = len(results)

        # Execution statistics
        successful = len([r for r in results if r.status == 'success'])
        failed = len([r for r in results if r.status == 'failed'])
        partial = len([r for r in results if r.status == 'partial'])

        success_rate = successful / total_executions if total_executions > 0 else 0

        # Timing statistics
        durations = [r.duration_seconds for r in results]
        total_duration = sum(durations)
        avg_duration = total_duration / total_executions if total_executions > 0 else 0
        min_duration = min(durations) if durations else 0
        max_duration = max(durations) if durations else 0

        # Step statistics
        total_steps = sum(r.summary.get('total_steps', 0) for r in results)
        successful_steps = sum(r.summary.get('successful_steps', 0) for r in results)
        failed_steps = sum(r.summary.get('failed_steps', 0) for r in results)

        # Validation statistics
        validation_stats = {}
        if validations:
            valid_count = len([v for v in validations if v.is_valid])
            validation_stats = {
                'total_validated': len(validations),
                'valid': valid_count,
                'invalid': len(validations) - valid_count,
                'validation_rate': valid_count / len(validations) if validations else 0,
                'total_issues': sum(v.summary.get('total_issues', 0) for v in validations),
                'total_errors': sum(v.summary.get('errors', 0) for v in validations),
                'total_warnings': sum(v.summary.get('warnings', 0) for v in validations)
            }

        # Overall status
        if failed == total_executions:
            overall_status = 'failed'
        elif successful == total_executions:
            overall_status = 'success'
        else:
            overall_status = 'partial'

        return {
            'total_executions': total_executions,
            'successful': successful,
            'failed': failed,
            'partial': partial,
            'success_rate': success_rate,
            'overall_status': overall_status,

            'timing': {
                'total_duration': total_duration,
                'avg_duration': avg_duration,
                'min_duration': min_duration,
                'max_duration': max_duration
            },

            'steps': {
                'total': total_steps,
                'successful': successful_steps,
                'failed': failed_steps,
                'success_rate': successful_steps / total_steps if total_steps > 0 else 0
            },

            'validation': validation_stats
        }

    def export_to_json(self, report: ExecutionReport, pretty: bool = True) -> str:
        """
        Export report to JSON

        Args:
            report: Execution report
            pretty: Pretty print JSON

        Returns:
            JSON string
        """
        indent = 2 if pretty else None
        return json.dumps(report.to_dict(), indent=indent, default=str)

    def export_to_html(self, report: ExecutionReport) -> str:
        """
        Export report to HTML

        Args:
            report: Execution report

        Returns:
            HTML string
        """
        summary = report.summary

        # Build HTML
        html = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Execution Report - {report.report_id}</title>
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            margin: 20px;
            background-color: #f5f5f5;
        }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background-color: white;
            padding: 30px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        h1 {{
            color: #333;
            border-bottom: 3px solid #4CAF50;
            padding-bottom: 10px;
        }}
        h2 {{
            color: #666;
            margin-top: 30px;
        }}
        .summary {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin: 20px 0;
        }}
        .metric {{
            background: #f9f9f9;
            padding: 20px;
            border-radius: 5px;
            border-left: 4px solid #4CAF50;
        }}
        .metric.warning {{
            border-left-color: #FF9800;
        }}
        .metric.error {{
            border-left-color: #f44336;
        }}
        .metric-label {{
            font-size: 12px;
            color: #888;
            text-transform: uppercase;
        }}
        .metric-value {{
            font-size: 28px;
            font-weight: bold;
            color: #333;
            margin-top: 5px;
        }}
        .status-badge {{
            display: inline-block;
            padding: 5px 15px;
            border-radius: 20px;
            font-size: 14px;
            font-weight: bold;
        }}
        .status-success {{
            background-color: #4CAF50;
            color: white;
        }}
        .status-failed {{
            background-color: #f44336;
            color: white;
        }}
        .status-partial {{
            background-color: #FF9800;
            color: white;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
        }}
        th, td {{
            padding: 12px;
            text-align: left;
            border-bottom: 1px solid #ddd;
        }}
        th {{
            background-color: #4CAF50;
            color: white;
        }}
        tr:hover {{
            background-color: #f5f5f5;
        }}
        .footer {{
            margin-top: 40px;
            padding-top: 20px;
            border-top: 1px solid #ddd;
            color: #888;
            font-size: 12px;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>Scenario Execution Report</h1>

        <div style="margin-bottom: 20px;">
            <strong>Report ID:</strong> {report.report_id}<br>
            <strong>Type:</strong> {report.report_type}<br>
            <strong>Generated:</strong> {report.generated_at}<br>
            <strong>Status:</strong> <span class="status-badge status-{summary['overall_status']}">{summary['overall_status'].upper()}</span>
        </div>

        <h2>Summary</h2>
        <div class="summary">
            <div class="metric">
                <div class="metric-label">Total Executions</div>
                <div class="metric-value">{summary['total_executions']}</div>
            </div>
            <div class="metric">
                <div class="metric-label">Successful</div>
                <div class="metric-value">{summary['successful']}</div>
            </div>
            <div class="metric {'warning' if summary['partial'] > 0 else ''}">
                <div class="metric-label">Partial</div>
                <div class="metric-value">{summary['partial']}</div>
            </div>
            <div class="metric {'error' if summary['failed'] > 0 else ''}">
                <div class="metric-label">Failed</div>
                <div class="metric-value">{summary['failed']}</div>
            </div>
            <div class="metric">
                <div class="metric-label">Success Rate</div>
                <div class="metric-value">{summary['success_rate']:.1%}</div>
            </div>
            <div class="metric">
                <div class="metric-label">Avg Duration</div>
                <div class="metric-value">{summary['timing']['avg_duration']:.2f}s</div>
            </div>
        </div>

        <h2>Execution Details</h2>
        <table>
            <thead>
                <tr>
                    <th>Scenario ID</th>
                    <th>Status</th>
                    <th>Duration</th>
                    <th>Steps</th>
                    <th>Success Rate</th>
                </tr>
            </thead>
            <tbody>
"""

        # Add execution rows
        for exec_dict in report.executions:
            status = exec_dict['status']
            summary_data = exec_dict['summary']
            total_steps = summary_data.get('total_steps', 0)
            success_steps = summary_data.get('successful_steps', 0)
            step_success_rate = (success_steps / total_steps * 100) if total_steps > 0 else 0

            html += f"""
                <tr>
                    <td>{exec_dict['scenario_id']}</td>
                    <td><span class="status-badge status-{status}">{status.upper()}</span></td>
                    <td>{exec_dict['duration_seconds']:.2f}s</td>
                    <td>{success_steps}/{total_steps}</td>
                    <td>{step_success_rate:.1f}%</td>
                </tr>
"""

        html += """
            </tbody>
        </table>
"""

        # Add validation summary if available
        if report.validations:
            html += """
        <h2>Validation Summary</h2>
        <table>
            <thead>
                <tr>
                    <th>Scenario ID</th>
                    <th>Status</th>
                    <th>Issues</th>
                    <th>Errors</th>
                    <th>Warnings</th>
                </tr>
            </thead>
            <tbody>
"""
            for val_dict in report.validations:
                val_summary = val_dict['summary']
                html += f"""
                <tr>
                    <td>{val_dict['scenario_id']}</td>
                    <td><span class="status-badge status-{val_dict['validation_status']}">{val_dict['validation_status'].upper()}</span></td>
                    <td>{val_summary.get('total_issues', 0)}</td>
                    <td>{val_summary.get('errors', 0)}</td>
                    <td>{val_summary.get('warnings', 0)}</td>
                </tr>
"""
            html += """
            </tbody>
        </table>
"""

        # Footer
        html += f"""
        <div class="footer">
            Generated by Scenario Intelligence Execution Engine<br>
            Report ID: {report.report_id}<br>
            Timestamp: {report.generated_at}
        </div>
    </div>
</body>
</html>
"""

        return html

    def save_report(self, report: ExecutionReport, filepath: str, format: str = 'json'):
        """
        Save report to file

        Args:
            report: Execution report
            filepath: Output file path
            format: 'json' or 'html'
        """
        if format == 'json':
            content = self.export_to_json(report)
        elif format == 'html':
            content = self.export_to_html(report)
        else:
            raise ValueError(f"Unsupported format: {format}")

        with open(filepath, 'w') as f:
            f.write(content)

        logger.info(f"  💾 Report saved: {filepath}")


# Test
if __name__ == "__main__":
    from datetime import datetime

    # Mock data for testing
    mock_result = ExecutionResult(
        scenario_id='test-scenario-1',
        status='success',
        started_at=datetime.utcnow().isoformat(),
        completed_at=datetime.utcnow().isoformat(),
        duration_seconds=2.5,
        steps=[],
        context={},
        summary={'total_steps': 5, 'successful_steps': 5, 'failed_steps': 0}
    )

    from .validator import ValidationReport, ValidationIssue

    mock_validation = ValidationReport(
        scenario_id='test-scenario-1',
        is_valid=True,
        validation_status='passed',
        issues=[],
        summary={'total_issues': 0, 'errors': 0, 'warnings': 0},
        validated_at=datetime.utcnow().isoformat()
    )

    reporter = ExecutionReporter()
    report = reporter.generate_report(
        results=[mock_result],
        validations=[mock_validation],
        report_type='single'
    )

    print("\n" + "="*60)
    print("EXECUTION REPORT:")
    print("="*60)
    print(f"Report ID: {report.report_id}")
    print(f"Type: {report.report_type}")
    print(f"Status: {report.summary['overall_status']}")
    print(f"Success Rate: {report.summary['success_rate']:.1%}")
    print("\nJSON Export:")
    print(reporter.export_to_json(report)[:500] + "...")
