"""
Dependency Mapper Tool
======================

Wrapper for infrastructure/tools/analyzers/dependency_mapper.py

This tool maps dependencies between services and modules.
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
    from dependency_mapper import DependencyMapper as OriginalDependencyMapper
    TOOL_AVAILABLE = True
    logger.info("✅ dependency_mapper tool loaded successfully")
except ImportError as e:
    TOOL_AVAILABLE = False
    logger.warning(f"❌ dependency_mapper tool not available: {e}")
    OriginalDependencyMapper = None


class DependencyMapperTool:
    """
    Wrapper for DependencyMapper tool

    Maps dependencies between services, detects conflicts, circular dependencies.

    Competency required: MIDDLE

    Example:
        ```python
        tool = DependencyMapperTool()
        analysis = await tool.analyze_dependencies()
        print(f"Found {len(analysis['conflicts'])} conflicts")
        ```
    """

    def __init__(self):
        """Initialize Dependency Mapper tool"""
        self.available = TOOL_AVAILABLE
        self.name = "dependency_mapper"
        self.description = "Maps service dependencies and detects conflicts"
        self.competency_required = "middle"

        if self.available:
            try:
                self.tool = OriginalDependencyMapper()
                logger.info("DependencyMapperTool initialized")
            except Exception as e:
                logger.error(f"Failed to initialize DependencyMapper: {e}")
                self.available = False
                self.tool = None
        else:
            self.tool = None

    async def analyze_dependencies(self) -> Dict[str, Any]:
        """
        Analyze all dependencies in the platform

        Returns:
            Complete dependency analysis including conflicts and circular deps

        Example:
            ```python
            analysis = await tool.analyze_dependencies()

            print(f"Total services: {analysis['total_services']}")
            print(f"Conflicts: {len(analysis['conflicts'])}")
            print(f"Circular deps: {len(analysis['circular_dependencies'])}")
            ```
        """
        if not self.available:
            logger.warning("dependency_mapper tool not available")
            return {
                "total_services": 0,
                "total_dependencies": 0,
                "conflicts": [],
                "circular_dependencies": [],
                "missing_dependencies": [],
                "error": "Tool not available"
            }

        try:
            # Map all dependencies
            dependency_map = self.tool.map_all_dependencies()

            # Detect conflicts
            conflicts = self.tool.detect_conflicts(dependency_map)

            # Detect circular dependencies
            circular_deps = self.tool.detect_circular_dependencies(dependency_map)

            # Detect missing dependencies
            missing_deps = self.tool.detect_missing_dependencies(dependency_map)

            result = {
                "total_services": len(dependency_map),
                "total_dependencies": sum(
                    len(deps.get("dependencies", []))
                    for deps in dependency_map.values()
                ),
                "conflicts": conflicts,
                "circular_dependencies": circular_deps,
                "missing_dependencies": missing_deps,
                "dependency_map": dependency_map,
                "analyzed_at": self.tool._get_timestamp()
            }

            logger.info(
                f"Dependency analysis complete: "
                f"{result['total_services']} services, "
                f"{len(conflicts)} conflicts, "
                f"{len(circular_deps)} circular deps"
            )

            return result

        except Exception as e:
            logger.error(f"Dependency analysis failed: {e}")
            return {
                "total_services": 0,
                "total_dependencies": 0,
                "conflicts": [],
                "circular_dependencies": [],
                "error": str(e)
            }

    async def get_service_dependencies(self, service_name: str) -> Dict[str, Any]:
        """
        Get dependencies for a specific service

        Args:
            service_name: Name of service

        Returns:
            Service dependency details

        Example:
            ```python
            deps = await tool.get_service_dependencies("workflow_intelligence")
            print(f"Dependencies: {deps['dependencies']}")
            ```
        """
        if not self.available:
            return {"error": "Tool not available"}

        try:
            dependency_map = self.tool.map_all_dependencies()

            if service_name in dependency_map:
                return dependency_map[service_name]
            else:
                return {
                    "service": service_name,
                    "error": "Service not found",
                    "dependencies": []
                }

        except Exception as e:
            logger.error(f"Failed to get dependencies for {service_name}: {e}")
            return {"error": str(e)}

    async def calculate_health_score(self) -> float:
        """
        Calculate dependency health score (0-100)

        Factors:
        - Conflicts (penalty)
        - Circular dependencies (penalty)
        - Missing dependencies (penalty)

        Returns:
            Health score 0-100

        Example:
            ```python
            score = await tool.calculate_health_score()
            print(f"Dependency health: {score}/100")
            ```
        """
        if not self.available:
            return 0.0

        try:
            analysis = await self.analyze_dependencies()

            score = 100.0

            # Conflicts penalty (up to -40 points)
            conflict_count = len(analysis.get("conflicts", []))
            score -= min(conflict_count * 20, 40)

            # Circular dependencies penalty (up to -30 points)
            circular_count = len(analysis.get("circular_dependencies", []))
            score -= min(circular_count * 15, 30)

            # Missing dependencies penalty (up to -30 points)
            missing_count = len(analysis.get("missing_dependencies", []))
            score -= min(missing_count * 10, 30)

            return max(0, min(100, score))

        except Exception as e:
            logger.error(f"Failed to calculate health score: {e}")
            return 0.0

    async def generate_insights(self) -> List[Dict[str, Any]]:
        """
        Generate insights from dependency analysis

        Returns:
            List of insights about dependency health

        Example:
            ```python
            insights = await tool.generate_insights()
            for insight in insights:
                print(f"{insight['severity']}: {insight['message']}")
            ```
        """
        if not self.available:
            return []

        try:
            analysis = await self.analyze_dependencies()
            insights = []

            # Conflicts
            conflicts = analysis.get("conflicts", [])
            if len(conflicts) > 0:
                insights.append({
                    "severity": "high" if len(conflicts) > 2 else "medium",
                    "category": "dependency_conflict",
                    "message": f"Found {len(conflicts)} dependency conflicts",
                    "details": conflicts,
                    "recommendation": "Resolve version conflicts to avoid runtime issues",
                    "affected_services": [c.get("service") for c in conflicts]
                })

            # Circular dependencies
            circular = analysis.get("circular_dependencies", [])
            if len(circular) > 0:
                insights.append({
                    "severity": "critical",
                    "category": "circular_dependency",
                    "message": f"Found {len(circular)} circular dependencies",
                    "details": circular,
                    "recommendation": "Break circular dependencies to improve modularity",
                    "affected_services": [item for cycle in circular for item in cycle]
                })

            # Missing dependencies
            missing = analysis.get("missing_dependencies", [])
            if len(missing) > 0:
                insights.append({
                    "severity": "medium",
                    "category": "missing_dependency",
                    "message": f"Found {len(missing)} missing dependencies",
                    "details": missing,
                    "recommendation": "Add missing dependencies to requirements files"
                })

            # Health score
            health_score = await self.calculate_health_score()
            if health_score < 70:
                insights.append({
                    "severity": "high",
                    "category": "dependency_health",
                    "message": f"Low dependency health score: {health_score:.1f}/100",
                    "recommendation": "Address conflicts and circular dependencies"
                })

            return insights

        except Exception as e:
            logger.error(f"Failed to generate insights: {e}")
            return []
