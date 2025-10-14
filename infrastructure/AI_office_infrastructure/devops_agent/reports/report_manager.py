#!/usr/bin/env python3
"""
Report Manager for DevOps Agent

Manages report persistence, history, and HTML generation
"""

import json
from pathlib import Path
from typing import Dict, List
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class ReportManager:
    """Manages DevOps Agent reports"""

    def __init__(self, project_root: str):
        self.project_root = Path(project_root)
        self.reports_dir = self.project_root / "infrastructure/devops-reports"
        self.reports_dir.mkdir(parents=True, exist_ok=True)

        # Create subdirectories
        (self.reports_dir / "json").mkdir(exist_ok=True)
        (self.reports_dir / "html").mkdir(exist_ok=True)

        logger.info(f"📁 ReportManager initialized: {self.reports_dir}")

    def save_report(self, report: Dict) -> Dict:
        """
        Save report to disk (JSON + HTML)

        Returns:
            Paths to saved files
        """
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")

        # 1. Save JSON
        json_path = self.reports_dir / "json" / f"report_{timestamp}.json"
        with open(json_path, 'w') as f:
            json.dump(report, f, indent=2)

        # 2. Generate and save HTML
        html_path = self.reports_dir / "html" / f"report_{timestamp}.html"
        self._generate_html(report, html_path)

        # 3. Update latest symlinks
        self._update_latest_links(json_path, html_path)

        # 4. Cleanup old reports (keep last 30)
        self._cleanup_old_reports(limit=30)

        logger.info(f"✅ Report saved: {json_path.name}")

        return {
            "json_path": str(json_path),
            "html_path": str(html_path),
            "timestamp": timestamp
        }

    def _generate_html(self, report: Dict, output_path: Path):
        """Generate HTML dashboard from report"""

        scan_results = report.get("analysis", {}).get("scan_results", {})
        ai_analysis = report.get("analysis", {}).get("ai_analysis", {})
        stats = report.get("statistics", {})

        html_content = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>DevOps Agent Report - {report.get('timestamp')}</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
            background: #f5f5f5;
        }}
        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            border-radius: 10px;
            margin-bottom: 20px;
        }}
        .stats {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 15px;
            margin-bottom: 20px;
        }}
        .stat-card {{
            background: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        .stat-value {{
            font-size: 2em;
            font-weight: bold;
            color: #667eea;
        }}
        .stat-label {{
            color: #666;
            margin-top: 5px;
        }}
        .section {{
            background: white;
            padding: 20px;
            border-radius: 8px;
            margin-bottom: 20px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        .section-title {{
            font-size: 1.5em;
            margin-bottom: 15px;
            color: #333;
        }}
        .recommendation {{
            background: #f8f9fa;
            padding: 15px;
            margin: 10px 0;
            border-left: 4px solid #667eea;
            border-radius: 4px;
        }}
        .priority-high {{ border-left-color: #dc3545; }}
        .priority-medium {{ border-left-color: #ffc107; }}
        .priority-low {{ border-left-color: #28a745; }}
        .footer {{
            text-align: center;
            color: #666;
            margin-top: 30px;
            padding-top: 20px;
            border-top: 1px solid #ddd;
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>🤖 DevOps Agent Report</h1>
        <p>Generated: {report.get('timestamp')}</p>
        <p>Agent: {report.get('agent_name', 'DevOps Agent AI')}</p>
    </div>

    <div class="stats">
        <div class="stat-card">
            <div class="stat-value">{stats.get('scans_completed', 0)}</div>
            <div class="stat-label">Total Scans</div>
        </div>
        <div class="stat-card">
            <div class="stat-value">{stats.get('issues_detected', 0)}</div>
            <div class="stat-label">Issues Detected</div>
        </div>
        <div class="stat-card">
            <div class="stat-value">{stats.get('fixes_applied', 0)}</div>
            <div class="stat-label">Fixes Applied</div>
        </div>
        <div class="stat-card">
            <div class="stat-value">{scan_results.get('events', {}).get('critical_gaps', 0)}</div>
            <div class="stat-label">Critical Event Gaps</div>
        </div>
    </div>

    <div class="section">
        <h2 class="section-title">📊 Scan Results</h2>

        <h3>Event Architecture</h3>
        <ul>
            <li>Schema Events: {scan_results.get('events', {}).get('schema_events', 0)}</li>
            <li>Code Events: {scan_results.get('events', {}).get('code_events', 0)}</li>
            <li>Gaps Found: {scan_results.get('events', {}).get('gaps_found', 0)}</li>
            <li>Potential Events: {scan_results.get('events', {}).get('potential_events', 0)}</li>
        </ul>

        <h3>Containers</h3>
        <ul>
            <li>Missing Dockerfiles: {scan_results.get('containers', {}).get('missing_dockerfiles', 0)}</li>
            <li>Services Analyzed: {scan_results.get('containers', {}).get('services_analyzed', 0)}</li>
            <li>Issues Found: {scan_results.get('containers', {}).get('issues_found', 0)}</li>
        </ul>

        <h3>Deployments</h3>
        <ul>
            <li>Total Services: {scan_results.get('deployments', {}).get('total_services', 0)}</li>
            <li>Healthy: {scan_results.get('deployments', {}).get('healthy_services', 0)}</li>
            <li>Port Conflicts: {scan_results.get('deployments', {}).get('port_conflicts', 0)}</li>
        </ul>
    </div>

    <div class="section">
        <h2 class="section-title">🧠 AI Analysis</h2>
        <p><strong>Risk Level:</strong> {ai_analysis.get('risk_level', 'unknown').upper()}</p>
        <p><strong>Auto-fix Approved:</strong> {'✅ Yes' if ai_analysis.get('auto_fix_approved') else '❌ No'}</p>

        <h3>Recommendations</h3>
        {''.join([
            f'<div class="recommendation priority-{rec.get("priority", "low")}">'
            f'<strong>{rec.get("category", "N/A").upper()}</strong>: {rec.get("action", "N/A")}'
            f'</div>'
            for rec in ai_analysis.get('ai_recommendations', [])[:10]
        ])}
    </div>

    <div class="footer">
        <p>🤖 Generated by DevOps Agent - AI Digital Colleague</p>
        <p>Built with ❤️ for self-evolving platforms</p>
    </div>
</body>
</html>
"""

        with open(output_path, 'w') as f:
            f.write(html_content)

    def _update_latest_links(self, json_path: Path, html_path: Path):
        """Update symlinks to latest reports"""

        # JSON latest
        latest_json = self.reports_dir / "latest.json"
        if latest_json.exists():
            latest_json.unlink()
        latest_json.symlink_to(json_path)

        # HTML latest
        latest_html = self.reports_dir / "latest.html"
        if latest_html.exists():
            latest_html.unlink()
        latest_html.symlink_to(html_path)

    def _cleanup_old_reports(self, limit: int = 30):
        """Keep only last N reports"""

        # Cleanup JSON
        json_reports = sorted(
            (self.reports_dir / "json").glob("report_*.json"),
            key=lambda p: p.stat().st_mtime
        )
        for old_report in json_reports[:-limit]:
            old_report.unlink()

        # Cleanup HTML
        html_reports = sorted(
            (self.reports_dir / "html").glob("report_*.html"),
            key=lambda p: p.stat().st_mtime
        )
        for old_report in html_reports[:-limit]:
            old_report.unlink()

    def get_history(self, limit: int = 30) -> List[Dict]:
        """Get report history"""

        reports = sorted(
            (self.reports_dir / "json").glob("report_*.json"),
            key=lambda p: p.stat().st_mtime,
            reverse=True
        )[:limit]

        history = []
        for report_path in reports:
            try:
                with open(report_path) as f:
                    history.append(json.load(f))
            except Exception as e:
                logger.error(f"Failed to load {report_path}: {e}")

        return history

    def get_latest(self) -> Dict:
        """Get latest report"""
        latest_path = self.reports_dir / "latest.json"

        if not latest_path.exists():
            return {}

        with open(latest_path) as f:
            return json.load(f)
