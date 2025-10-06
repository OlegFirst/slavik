"""
Scenario AI Client

Client for AI-powered Scenario Orchestrator service
"""

import httpx
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime
from enum import Enum

logger = logging.getLogger(__name__)


class ScenarioType(str, Enum):
    """Scenario types"""
    CYBERATTACK = "cyberattack"
    PANDEMIC = "pandemic"
    NATURAL_DISASTER = "natural_disaster"
    SUPPLY_CHAIN = "supply_chain_disruption"
    FINANCIAL_CRISIS = "financial_crisis"
    DATA_BREACH = "data_breach"
    INFRASTRUCTURE_FAILURE = "infrastructure_failure"
    CUSTOM = "custom"


class RiskLevel(str, Enum):
    """Risk levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class ScenarioAIClient:
    """Client for Scenario AI / Orchestrator service"""

    def __init__(self, base_url: str, timeout: int = 60):
        """
        Initialize Scenario AI client

        Args:
            base_url: Scenario AI service URL (e.g. http://scenario-ai:8002)
            timeout: Request timeout in seconds (higher for AI generation)
        """
        self.base_url = base_url.rstrip('/')
        self.timeout = timeout
        self.client = httpx.AsyncClient(timeout=timeout)

    async def close(self):
        """Close HTTP client"""
        await self.client.aclose()

    async def health_check(self) -> Dict[str, Any]:
        """
        Check Scenario AI service health

        Returns:
            Health status dict
        """
        try:
            response = await self.client.get(f"{self.base_url}/health")
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Scenario AI health check failed: {e}")
            return {'status': 'unavailable', 'error': str(e)}

    async def generate_scenario(
        self,
        context: Dict[str, Any],
        scenario_type: Optional[str] = None,
        risk_level: str = "medium"
    ) -> Dict[str, Any]:
        """
        Generate AI-powered BCM scenario based on organization context

        Args:
            context: Organization context including:
                - industry: Industry sector
                - company_size: Number of employees
                - annual_revenue: Annual revenue
                - geographic_locations: List of locations
                - current_maturity: BCM maturity level
                - risk_profile: Risk assessment data
            scenario_type: Optional scenario type to generate
            risk_level: Desired risk level (low/medium/high/critical)

        Returns:
            Generated scenario with:
                - scenario_id: Unique scenario ID
                - scenario_type: Type of scenario
                - description: Detailed scenario description
                - parameters: Simulation parameters
                - timeline: Expected timeline
                - impact_estimates: Estimated impacts
                - mitigation_strategies: Recommended mitigations
                - references: Similar real-world incidents
        """
        try:
            logger.info(f"Generating AI scenario for: {context.get('industry')} / {scenario_type}")

            payload = {
                'context': context,
                'risk_level': risk_level
            }

            if scenario_type:
                payload['scenario_type'] = scenario_type

            response = await self.client.post(
                f"{self.base_url}/api/v1/scenarios/generate",
                json=payload
            )
            response.raise_for_status()

            result = response.json()
            logger.info(f"AI scenario generated: {result.get('scenario_id')}")

            return result

        except httpx.HTTPStatusError as e:
            logger.error(f"Scenario generation HTTP error: {e.response.status_code} - {e.response.text}")
            raise Exception(f"Scenario AI returned error: {e.response.status_code}")
        except Exception as e:
            logger.error(f"Scenario generation failed: {e}")
            raise

    async def analyze_scenario(
        self,
        scenario_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Analyze existing scenario for improvements

        Args:
            scenario_data: Scenario to analyze

        Returns:
            Analysis with improvement suggestions
        """
        try:
            response = await self.client.post(
                f"{self.base_url}/api/v1/scenarios/analyze",
                json=scenario_data
            )
            response.raise_for_status()
            return response.json()

        except Exception as e:
            logger.error(f"Scenario analysis failed: {e}")
            raise

    async def optimize_scenario(
        self,
        scenario_id: str,
        optimization_goals: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Optimize scenario parameters for better results

        Args:
            scenario_id: Scenario to optimize
            optimization_goals: Goals like 'realism', 'training_value', 'complexity'

        Returns:
            Optimized scenario
        """
        try:
            payload = {'scenario_id': scenario_id}
            if optimization_goals:
                payload['goals'] = optimization_goals

            response = await self.client.post(
                f"{self.base_url}/api/v1/scenarios/optimize",
                json=payload
            )
            response.raise_for_status()
            return response.json()

        except Exception as e:
            logger.error(f"Scenario optimization failed: {e}")
            raise

    async def get_recommendations(
        self,
        scenario_result: Dict[str, Any],
        organization_context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Get AI recommendations based on scenario results

        Args:
            scenario_result: Simulation results
            organization_context: Organization context

        Returns:
            AI-generated recommendations:
                - immediate_actions: Urgent actions
                - short_term: Short-term improvements
                - long_term: Long-term strategic changes
                - priority_order: Prioritized action plan
        """
        try:
            response = await self.client.post(
                f"{self.base_url}/api/v1/scenarios/recommend",
                json={
                    'scenario_result': scenario_result,
                    'context': organization_context
                }
            )
            response.raise_for_status()
            return response.json()

        except Exception as e:
            logger.error(f"Recommendations generation failed: {e}")
            raise

    async def generate_scenario_variants(
        self,
        base_scenario: Dict[str, Any],
        num_variants: int = 3
    ) -> List[Dict[str, Any]]:
        """
        Generate variants of a base scenario

        Args:
            base_scenario: Base scenario to create variants from
            num_variants: Number of variants to generate

        Returns:
            List of scenario variants
        """
        try:
            response = await self.client.post(
                f"{self.base_url}/api/v1/scenarios/variants",
                json={
                    'base_scenario': base_scenario,
                    'num_variants': num_variants
                }
            )
            response.raise_for_status()
            return response.json().get('variants', [])

        except Exception as e:
            logger.error(f"Variant generation failed: {e}")
            raise

    async def get_historical_scenarios(
        self,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Get historical scenarios from database

        Args:
            filters: Filters like industry, scenario_type, date_range

        Returns:
            List of historical scenarios
        """
        try:
            params = filters or {}
            response = await self.client.get(
                f"{self.base_url}/api/v1/scenarios/history",
                params=params
            )
            response.raise_for_status()
            return response.json().get('scenarios', [])

        except Exception as e:
            logger.error(f"Historical scenarios fetch failed: {e}")
            raise

    async def train_on_results(
        self,
        scenario_id: str,
        actual_results: Dict[str, Any],
        feedback: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Train AI model on actual scenario results

        Args:
            scenario_id: Scenario ID
            actual_results: Actual results from simulation/exercise
            feedback: User feedback on scenario quality

        Returns:
            Training confirmation
        """
        try:
            response = await self.client.post(
                f"{self.base_url}/api/v1/scenarios/train",
                json={
                    'scenario_id': scenario_id,
                    'actual_results': actual_results,
                    'feedback': feedback
                }
            )
            response.raise_for_status()
            return response.json()

        except Exception as e:
            logger.error(f"Training submission failed: {e}")
            raise


class ScenarioAIError(Exception):
    """Scenario AI specific error"""
    pass
