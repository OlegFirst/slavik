"""
BIA Engine Client

Client for Business Impact Analysis Engine service
"""

import httpx
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime

logger = logging.getLogger(__name__)


class BIAEngineClient:
    """Client for BIA Engine service"""

    def __init__(self, base_url: str, timeout: int = 30):
        """
        Initialize BIA Engine client

        Args:
            base_url: BIA Engine service URL (e.g. http://bia-engine:8001)
            timeout: Request timeout in seconds
        """
        self.base_url = base_url.rstrip('/')
        self.timeout = timeout
        self.client = httpx.AsyncClient(timeout=timeout)

    async def close(self):
        """Close HTTP client"""
        await self.client.aclose()

    async def health_check(self) -> Dict[str, Any]:
        """
        Check BIA Engine service health

        Returns:
            Health status dict
        """
        try:
            response = await self.client.get(f"{self.base_url}/health")
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"BIA Engine health check failed: {e}")
            return {'status': 'unavailable', 'error': str(e)}

    async def analyze_organization(
        self,
        organization_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Run BIA analysis on organization

        Args:
            organization_data: Organization data including:
                - name: Organization name
                - processes: List of business processes
                - dependencies: Process dependencies
                - recovery_objectives: RTO/RPO targets

        Returns:
            BIA analysis result with:
                - criticality_scores: Process criticality
                - rto_rpo: Calculated recovery objectives
                - impact_matrix: Impact analysis matrix
                - recommendations: BIA recommendations
        """
        try:
            logger.info(f"Running BIA analysis for: {organization_data.get('name')}")

            response = await self.client.post(
                f"{self.base_url}/api/v1/analyze",
                json=organization_data
            )
            response.raise_for_status()

            result = response.json()
            logger.info(f"BIA analysis completed: {result.get('status')}")

            return result

        except httpx.HTTPStatusError as e:
            logger.error(f"BIA analysis HTTP error: {e.response.status_code} - {e.response.text}")
            raise Exception(f"BIA Engine returned error: {e.response.status_code}")
        except Exception as e:
            logger.error(f"BIA analysis failed: {e}")
            raise

    async def calculate_rto_rpo(
        self,
        process_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Calculate RTO/RPO for specific process

        Args:
            process_data: Process data including:
                - process_name: Process name
                - criticality: Criticality level (1-5)
                - dependencies: List of dependent processes
                - financial_impact: Daily financial impact

        Returns:
            RTO/RPO calculation result:
                - rto_hours: Recovery Time Objective
                - rpo_hours: Recovery Point Objective
                - justification: Calculation rationale
        """
        try:
            response = await self.client.post(
                f"{self.base_url}/api/v1/rto-rpo",
                json=process_data
            )
            response.raise_for_status()
            return response.json()

        except Exception as e:
            logger.error(f"RTO/RPO calculation failed: {e}")
            raise

    async def analyze_dependencies(
        self,
        processes: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Analyze process dependencies

        Args:
            processes: List of processes with dependencies

        Returns:
            Dependency analysis with:
                - dependency_graph: Process dependency graph
                - critical_paths: Critical dependency paths
                - single_points_of_failure: SPOFs identified
        """
        try:
            response = await self.client.post(
                f"{self.base_url}/api/v1/dependencies",
                json={'processes': processes}
            )
            response.raise_for_status()
            return response.json()

        except Exception as e:
            logger.error(f"Dependency analysis failed: {e}")
            raise

    async def calculate_financial_impact(
        self,
        downtime_scenarios: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Calculate financial impact of downtime scenarios

        Args:
            downtime_scenarios: List of scenarios with:
                - duration_hours: Downtime duration
                - affected_processes: Affected processes
                - revenue_per_hour: Hourly revenue impact

        Returns:
            Financial impact analysis:
                - total_impact: Total financial impact
                - breakdown: Impact breakdown by scenario
                - cumulative_impact: Cumulative impact over time
        """
        try:
            response = await self.client.post(
                f"{self.base_url}/api/v1/financial-impact",
                json={'scenarios': downtime_scenarios}
            )
            response.raise_for_status()
            return response.json()

        except Exception as e:
            logger.error(f"Financial impact calculation failed: {e}")
            raise

    async def generate_bia_report(
        self,
        analysis_id: str,
        format: str = "json"
    ) -> Dict[str, Any]:
        """
        Generate BIA report

        Args:
            analysis_id: BIA analysis ID
            format: Report format (json, pdf, html)

        Returns:
            BIA report data or download URL
        """
        try:
            response = await self.client.get(
                f"{self.base_url}/api/v1/report/{analysis_id}",
                params={'format': format}
            )
            response.raise_for_status()

            if format == 'json':
                return response.json()
            else:
                return {
                    'format': format,
                    'download_url': f"{self.base_url}/api/v1/report/{analysis_id}/download",
                    'content': response.content
                }

        except Exception as e:
            logger.error(f"Report generation failed: {e}")
            raise


class BIAEngineError(Exception):
    """BIA Engine specific error"""
    pass
