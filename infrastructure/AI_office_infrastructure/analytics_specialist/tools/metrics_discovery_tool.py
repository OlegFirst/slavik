"""
Metrics Discovery Tool
======================

Wrapper for infrastructure/tools/analyzers/metrics_discovery.py

This tool discovers Prometheus metrics across the platform.
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
    from metrics_discovery import MetricsDiscovery as OriginalMetricsDiscovery
    TOOL_AVAILABLE = True
    logger.info("✅ metrics_discovery tool loaded successfully")
except ImportError as e:
    TOOL_AVAILABLE = False
    logger.warning(f"❌ metrics_discovery tool not available: {e}")
    OriginalMetricsDiscovery = None


class MetricsDiscoveryTool:
    """
    Wrapper for MetricsDiscovery tool

    Discovers and analyzes Prometheus metrics across the platform.

    Competency required: JUNIOR

    Example:
        ```python
        tool = MetricsDiscoveryTool()
        metrics = await tool.discover_all_metrics()
        print(f"Found {metrics['total_modules']} modules with metrics")
        ```
    """

    def __init__(self):
        """Initialize Metrics Discovery tool"""
        self.available = TOOL_AVAILABLE
        self.name = "metrics_discovery"
        self.description = "Discovers Prometheus metrics across platform"
        self.competency_required = "junior"

        if self.available:
            try:
                self.tool = OriginalMetricsDiscovery()
                logger.info("MetricsDiscoveryTool initialized")
            except Exception as e:
                logger.error(f"Failed to initialize MetricsDiscovery: {e}")
                self.available = False
                self.tool = None
        else:
            self.tool = None

    async def discover_all_metrics(self) -> Dict[str, Any]:
        """
        Discover all Prometheus metrics in the platform

        Returns:
            Dict containing:
            - total_modules: Number of modules with metrics
            - total_metrics: Total metrics found
            - modules: List of module details
            - prometheus_config: Generated prometheus scrape config

        Example:
            ```python
            result = await tool.discover_all_metrics()
            print(f"Total metrics: {result['total_metrics']}")

            for module in result['modules']:
                print(f"Module: {module['name']}, Metrics: {module['metrics_count']}")
            ```
        """
        if not self.available:
            logger.warning("metrics_discovery tool not available")
            return {
                "total_modules": 0,
                "total_metrics": 0,
                "modules": [],
                "error": "Tool not available"
            }

        try:
            # Run discovery
            modules_with_metrics = self.tool.scan_for_metrics()

            # Count metrics
            total_metrics = sum(m.get("metrics_count", 0) for m in modules_with_metrics)

            # Generate prometheus config
            prometheus_config = self.tool.generate_prometheus_jobs(modules_with_metrics)

            result = {
                "total_modules": len(modules_with_metrics),
                "total_metrics": total_metrics,
                "modules": modules_with_metrics,
                "prometheus_config": prometheus_config,
                "discovered_at": self.tool._get_timestamp()
            }

            logger.info(
                f"Metrics discovery complete: "
                f"{result['total_modules']} modules, "
                f"{result['total_metrics']} metrics"
            )

            return result

        except Exception as e:
            logger.error(f"Metrics discovery failed: {e}")
            return {
                "total_modules": 0,
                "total_metrics": 0,
                "modules": [],
                "error": str(e)
            }

    async def discover_module_metrics(self, module_name: str) -> Dict[str, Any]:
        """
        Discover metrics for a specific module

        Args:
            module_name: Name of module (e.g., "ai-foundation", "workflow_intelligence")

        Returns:
            Module metrics details

        Example:
            ```python
            metrics = await tool.discover_module_metrics("ai-foundation")
            print(f"Found {metrics['metrics_count']} metrics")
            ```
        """
        if not self.available:
            return {"error": "Tool not available"}

        try:
            all_modules = self.tool.scan_for_metrics()

            # Find specific module
            for module in all_modules:
                if module.get("module_name") == module_name:
                    return module

            return {
                "module_name": module_name,
                "error": "Module not found",
                "metrics_count": 0
            }

        except Exception as e:
            logger.error(f"Failed to discover metrics for {module_name}: {e}")
            return {"error": str(e)}

    async def check_metrics_coverage(self) -> Dict[str, Any]:
        """
        Check which modules have metrics coverage

        Returns:
            Coverage analysis

        Example:
            ```python
            coverage = await tool.check_metrics_coverage()
            print(f"Coverage: {coverage['coverage_percentage']}%")
            ```
        """
        if not self.available:
            return {"error": "Tool not available"}

        try:
            # Discover all modules with metrics
            modules_with_metrics = self.tool.scan_for_metrics()

            # For now, we consider all scanned modules
            # In future, could compare against expected modules list
            total_scanned = len(modules_with_metrics)
            with_metrics = len([m for m in modules_with_metrics if m.get("metrics_count", 0) > 0])
            without_metrics = total_scanned - with_metrics

            coverage_percentage = (with_metrics / total_scanned * 100) if total_scanned > 0 else 0

            return {
                "total_modules_scanned": total_scanned,
                "modules_with_metrics": with_metrics,
                "modules_without_metrics": without_metrics,
                "coverage_percentage": round(coverage_percentage, 1),
                "details": modules_with_metrics
            }

        except Exception as e:
            logger.error(f"Failed to check metrics coverage: {e}")
            return {"error": str(e)}

    async def generate_insights(self) -> List[Dict[str, Any]]:
        """
        Generate insights from metrics discovery

        Returns:
            List of insights about metrics coverage

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
            coverage = await self.check_metrics_coverage()

            insights = []

            # Check coverage percentage
            if coverage.get("coverage_percentage", 0) < 50:
                insights.append({
                    "severity": "high",
                    "category": "metrics_coverage",
                    "message": f"Low metrics coverage: {coverage['coverage_percentage']}%",
                    "recommendation": "Add /metrics endpoints to modules without metrics",
                    "affected_modules": [
                        m["module_name"]
                        for m in coverage.get("details", [])
                        if m.get("metrics_count", 0) == 0
                    ]
                })
            elif coverage.get("coverage_percentage", 0) < 80:
                insights.append({
                    "severity": "medium",
                    "category": "metrics_coverage",
                    "message": f"Medium metrics coverage: {coverage['coverage_percentage']}%",
                    "recommendation": "Consider adding metrics to remaining modules"
                })
            else:
                insights.append({
                    "severity": "low",
                    "category": "metrics_coverage",
                    "message": f"Good metrics coverage: {coverage['coverage_percentage']}%",
                    "recommendation": "Maintain current coverage"
                })

            return insights

        except Exception as e:
            logger.error(f"Failed to generate insights: {e}")
            return []
