"""
Dependency Validator Tool
=========================

Wrapper for infrastructure/tools/analyzers/dependency_validator.py

Validates dependencies in requirements.txt files.
"""

import sys
import logging
from pathlib import Path
from typing import Dict, Any, List, Optional

from ..config import settings

logger = logging.getLogger(__name__)

# Add tools/analyzers to Python path
analyzers_path = Path(settings.TOOLS_ANALYZERS_PATH)
if str(analyzers_path) not in sys.path:
    sys.path.insert(0, str(analyzers_path))

try:
    from dependency_validator import DependencyValidator as OriginalDependencyValidator
    TOOL_AVAILABLE = True
    logger.info("✅ dependency_validator tool loaded successfully")
except ImportError as e:
    TOOL_AVAILABLE = False
    logger.warning(f"❌ dependency_validator tool not available: {e}")
    OriginalDependencyValidator = None


class DependencyValidatorTool:
    """
    Wrapper for Dependency Validator tool

    Validates dependencies, checks for outdated packages, security vulnerabilities.

    Competency required: MIDDLE

    Example:
        ```python
        tool = DependencyValidatorTool()
        validation = await tool.validate_all_dependencies()
        print(f"Issues found: {len(validation['issues'])}")
        ```
    """

    def __init__(self):
        """Initialize Dependency Validator tool"""
        self.available = TOOL_AVAILABLE
        self.name = "dependency_validator"
        self.description = "Validates dependencies and checks for issues"
        self.competency_required = "middle"

        if self.available:
            try:
                self.tool = OriginalDependencyValidator()
                logger.info("DependencyValidatorTool initialized")
            except Exception as e:
                logger.error(f"Failed to initialize DependencyValidator: {e}")
                self.available = False
                self.tool = None
        else:
            self.tool = None

    async def validate_all_dependencies(self) -> Dict[str, Any]:
        """
        Validate all requirements.txt files

        Returns:
            Validation results with issues
        """
        if not self.available:
            logger.warning("dependency_validator tool not available")
            return {
                "total_files": 0,
                "issues": [],
                "error": "Tool not available"
            }

        try:
            validation = self.tool.validate_all()

            return {
                "total_files": len(validation.get("files", [])),
                "total_dependencies": validation.get("total_dependencies", 0),
                "issues": validation.get("issues", []),
                "outdated_packages": validation.get("outdated", []),
                "security_vulnerabilities": validation.get("vulnerabilities", []),
                "analyzed_at": validation.get("analyzed_at")
            }

        except Exception as e:
            logger.error(f"Dependency validation failed: {e}")
            return {"error": str(e)}

    async def calculate_health_score(self) -> float:
        """
        Calculate dependency health score (0-100)

        Returns:
            Health score
        """
        if not self.available:
            return 0.0

        try:
            validation = await self.validate_all_dependencies()

            score = 100.0

            # Issues penalty
            issues = validation.get("issues", [])
            score -= min(len(issues) * 10, 40)

            # Outdated packages penalty
            outdated = validation.get("outdated_packages", [])
            score -= min(len(outdated) * 5, 30)

            # Security vulnerabilities penalty (critical)
            vulns = validation.get("security_vulnerabilities", [])
            score -= min(len(vulns) * 20, 50)

            return max(0, min(100, score))

        except Exception as e:
            logger.error(f"Failed to calculate health score: {e}")
            return 0.0
