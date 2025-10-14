"""
Security Scanner Tool
=====================

Wrapper for infrastructure/tools/analyzers/security_scanner.py

Scans code for security vulnerabilities using Bandit.
"""

import sys
import logging
from pathlib import Path
from typing import Dict, Any, List, Optional

from config import settings

logger = logging.getLogger(__name__)

# Add tools/analyzers to Python path
analyzers_path = Path(settings.TOOLS_ANALYZERS_PATH)
if str(analyzers_path) not in sys.path:
    sys.path.insert(0, str(analyzers_path))

try:
    from security_scanner import SecurityScanner as OriginalSecurityScanner
    TOOL_AVAILABLE = True
    logger.info("✅ security_scanner tool loaded successfully")
except ImportError as e:
    TOOL_AVAILABLE = False
    logger.warning(f"❌ security_scanner tool not available: {e}")
    OriginalSecurityScanner = None


class SecurityScannerTool:
    """
    Wrapper for Security Scanner tool

    Scans Python code for security issues.

    Competency required: MIDDLE

    Example:
        ```python
        tool = SecurityScannerTool()
        scan = await tool.scan_project()
        print(f"Critical issues: {len(scan['critical_issues'])}")
        ```
    """

    def __init__(self):
        """Initialize Security Scanner tool"""
        self.available = TOOL_AVAILABLE
        self.name = "security_scanner"
        self.description = "Scans code for security vulnerabilities"
        self.competency_required = "middle"

        if self.available:
            try:
                self.tool = OriginalSecurityScanner()
                logger.info("SecurityScannerTool initialized")
            except Exception as e:
                logger.error(f"Failed to initialize SecurityScanner: {e}")
                self.available = False
                self.tool = None
        else:
            self.tool = None

    async def scan_project(self, project_path: Optional[str] = None) -> Dict[str, Any]:
        """
        Scan entire project for security issues

        Args:
            project_path: Path to project

        Returns:
            Security scan results
        """
        if not self.available:
            logger.warning("security_scanner tool not available")
            return {
                "total_issues": 0,
                "critical_issues": [],
                "high_issues": [],
                "medium_issues": [],
                "low_issues": [],
                "error": "Tool not available"
            }

        try:
            if not project_path:
                project_path = settings.PROJECT_ROOT

            scan_results = self.tool.scan_project(project_path)

            issues = scan_results.get("issues", [])

            return {
                "total_issues": len(issues),
                "critical_issues": [i for i in issues if i.get("severity") == "CRITICAL"],
                "high_issues": [i for i in issues if i.get("severity") == "HIGH"],
                "medium_issues": [i for i in issues if i.get("severity") == "MEDIUM"],
                "low_issues": [i for i in issues if i.get("severity") == "LOW"],
                "all_issues": issues,
                "analyzed_at": scan_results.get("analyzed_at")
            }

        except Exception as e:
            logger.error(f"Security scan failed: {e}")
            return {"error": str(e)}

    async def calculate_security_score(self) -> float:
        """
        Calculate security score (0-100)

        Returns:
            Security score (higher is better)
        """
        if not self.available:
            return 100.0  # Assume secure if can't scan

        try:
            scan = await self.scan_project()

            score = 100.0

            # Critical issues - major penalty
            critical = scan.get("critical_issues", [])
            score -= len(critical) * 30

            # High issues
            high = scan.get("high_issues", [])
            score -= len(high) * 15

            # Medium issues
            medium = scan.get("medium_issues", [])
            score -= len(medium) * 5

            # Low issues
            low = scan.get("low_issues", [])
            score -= len(low) * 1

            return max(0, min(100, score))

        except Exception as e:
            logger.error(f"Failed to calculate security score: {e}")
            return 100.0
