#!/usr/bin/env python3
"""
BCM Orchestrator Client - Интеграция с BCM Services Orchestrator
================================================================

Подключает MIO Manager к intelligent-core/orchestration/bcm-services-orchestrator для:
- Координации 10 BCM анализаторов
- ISO 22301 clause mapping
- BCM-специфичных workflow

ВОПРОСЫ ДЛЯ ОБСУЖДЕНИЯ:
========================

1. Должен ли MIO Manager напрямую вызывать BCM Orchestrator?
   - Или через другой слой?
   - Или это задача другого компонента?

2. Является ли BCM частью инфраструктуры?
   - Или это доменный функционал?
   - Где правильное место для этого клиента?
"""

import httpx
from typing import Dict, Optional, List
import logging

logger = logging.getLogger(__name__)


class BCMOrchestratorClient:
    """
    Client для взаимодействия с BCM Services Orchestrator.

    BCM Services Orchestrator координирует 10 специализированных анализаторов:
    1. Compliance Analyzer (ISO 22301 gap analysis)
    2. Risk Analyzer (FAIR-based risk quantification)
    3. Impact Analyzer (BIA impact assessment)
    4. Governance Analyzer (policy adherence)
    5. Emergency Analyzer (crisis response)
    6. Performance Analyzer (metrics analysis)
    7. Learning Analyzer (pattern extraction)
    8. Lifecycle Analyzer (BCM maturity)
    9. Plan Analyzer (recovery plan quality)
    10. Scenario Analyzer (exercise design)
    """

    def __init__(self, bcm_orchestrator_url: str = "http://localhost:8070"):
        self.bcm_orchestrator_url = bcm_orchestrator_url
        self.client = httpx.AsyncClient(timeout=60.0)

    # ========================================================================
    # Analysis Routing
    # ========================================================================

    async def analyze(
        self,
        analyzer_type: str,
        input_data: Dict,
        tenant_id: str,
        metadata: Optional[Dict] = None
    ) -> Dict:
        """
        Route analysis to specific analyzer.

        Args:
            analyzer_type: Analyzer type (compliance, risk, impact, etc.) or 'auto'
            input_data: Analysis input data
            tenant_id: Organization ID
            metadata: Optional metadata

        Returns:
            Analysis result with insights and recommendations
        """
        logger.info(f"🔍 Routing analysis to {analyzer_type}")

        try:
            response = await self.client.post(
                f"{self.bcm_orchestrator_url}/api/v1/analyze",
                json={
                    'analyzer_type': analyzer_type,
                    'input_data': input_data,
                    'tenant_id': tenant_id,
                    'metadata': metadata or {}
                }
            )

            if response.status_code == 200:
                result = response.json()
                logger.info(f"✅ Analysis completed by {result.get('analyzer')}")
                return {
                    'success': True,
                    'result': result
                }
            else:
                return {
                    'success': False,
                    'error': f'Analysis failed: {response.status_code}'
                }

        except Exception as e:
            logger.error(f"❌ Analysis request failed: {e}")
            return {
                'success': False,
                'error': str(e)
            }

    async def batch_analyze(
        self,
        analyzer_sequence: List[str],
        input_data: Dict,
        tenant_id: str
    ) -> Dict:
        """
        Execute batch analysis (multiple analyzers in sequence).

        Example pipeline: risk → impact → plan

        Args:
            analyzer_sequence: List of analyzer types
            input_data: Initial input data
            tenant_id: Organization ID

        Returns:
            Batch analysis results
        """
        logger.info(f"🔄 Batch analysis: {len(analyzer_sequence)} analyzers")

        try:
            response = await self.client.post(
                f"{self.bcm_orchestrator_url}/api/v1/analyze/batch",
                json={
                    'analyzer_sequence': analyzer_sequence,
                    'input_data': input_data,
                    'tenant_id': tenant_id
                }
            )

            if response.status_code == 200:
                result = response.json()
                logger.info(f"✅ Batch analysis completed: {result.get('steps')} steps")
                return {
                    'success': True,
                    'result': result
                }
            else:
                return {
                    'success': False,
                    'error': f'Batch analysis failed: {response.status_code}'
                }

        except Exception as e:
            logger.error(f"❌ Batch analysis failed: {e}")
            return {
                'success': False,
                'error': str(e)
            }

    # ========================================================================
    # Specific Analyses
    # ========================================================================

    async def check_compliance(
        self,
        tenant_id: str,
        standard: str = "ISO_22301",
        clauses: Optional[List[str]] = None
    ) -> Dict:
        """
        Execute ISO compliance check.

        Args:
            tenant_id: Organization ID
            standard: Standard to check
            clauses: Specific clauses (optional)

        Returns:
            Compliance gaps and recommendations
        """
        return await self.analyze(
            analyzer_type='compliance_analyzer',
            input_data={
                'type': 'compliance_gap',
                'standard': standard,
                'clauses': clauses or []
            },
            tenant_id=tenant_id
        )

    async def assess_risk(
        self,
        tenant_id: str,
        scenario: str,
        assets: List[Dict]
    ) -> Dict:
        """
        Execute FAIR-based risk assessment.

        Args:
            tenant_id: Organization ID
            scenario: Risk scenario
            assets: Assets to analyze

        Returns:
            Risk quantification and mitigation recommendations
        """
        return await self.analyze(
            analyzer_type='risk_analyzer',
            input_data={
                'type': 'risk_assessment',
                'scenario': scenario,
                'assets': assets
            },
            tenant_id=tenant_id
        )

    async def analyze_impact(
        self,
        tenant_id: str,
        processes: List[Dict],
        scope: str = "full"
    ) -> Dict:
        """
        Execute Business Impact Analysis.

        Args:
            tenant_id: Organization ID
            processes: Business processes
            scope: Analysis scope

        Returns:
            Impact assessment with RTO/RPO recommendations
        """
        return await self.analyze(
            analyzer_type='impact_analyzer',
            input_data={
                'type': 'bia_analysis',
                'processes': processes,
                'scope': scope
            },
            tenant_id=tenant_id
        )

    async def check_governance(
        self,
        tenant_id: str,
        policies: List[Dict]
    ) -> Dict:
        """
        Check governance and policy adherence.

        Args:
            tenant_id: Organization ID
            policies: Policies to check

        Returns:
            Governance assessment
        """
        return await self.analyze(
            analyzer_type='governance_analyzer',
            input_data={
                'type': 'policy_check',
                'policies': policies
            },
            tenant_id=tenant_id
        )

    async def analyze_emergency(
        self,
        tenant_id: str,
        incident: Dict
    ) -> Dict:
        """
        Analyze emergency/crisis situation.

        Args:
            tenant_id: Organization ID
            incident: Incident details

        Returns:
            Crisis analysis and response recommendations
        """
        return await self.analyze(
            analyzer_type='emergency_analyzer',
            input_data={
                'type': 'crisis_analysis',
                'incident': incident
            },
            tenant_id=tenant_id
        )

    async def analyze_performance(
        self,
        tenant_id: str,
        metrics: Dict,
        period: str = "last_30_days"
    ) -> Dict:
        """
        Analyze BCM performance metrics.

        Args:
            tenant_id: Organization ID
            metrics: Metrics to analyze
            period: Analysis period

        Returns:
            Performance analysis and trends
        """
        return await self.analyze(
            analyzer_type='performance_analyzer',
            input_data={
                'type': 'kpi_analysis',
                'metrics': metrics,
                'period': period
            },
            tenant_id=tenant_id
        )

    async def extract_patterns(
        self,
        tenant_id: str,
        data: Dict
    ) -> Dict:
        """
        Extract learning patterns.

        Args:
            tenant_id: Organization ID
            data: Historical data

        Returns:
            Extracted patterns and lessons learned
        """
        return await self.analyze(
            analyzer_type='learning_analyzer',
            input_data={
                'type': 'pattern_extraction',
                'data': data
            },
            tenant_id=tenant_id
        )

    async def assess_maturity(
        self,
        tenant_id: str,
        organization_data: Dict
    ) -> Dict:
        """
        Assess BCM maturity level.

        Args:
            tenant_id: Organization ID
            organization_data: Organization state

        Returns:
            Maturity assessment and roadmap
        """
        return await self.analyze(
            analyzer_type='lifecycle_analyzer',
            input_data={
                'type': 'maturity_assessment',
                'organization': organization_data
            },
            tenant_id=tenant_id
        )

    async def analyze_plan(
        self,
        tenant_id: str,
        plan: Dict
    ) -> Dict:
        """
        Analyze recovery plan quality.

        Args:
            tenant_id: Organization ID
            plan: Recovery plan

        Returns:
            Plan quality assessment
        """
        return await self.analyze(
            analyzer_type='plan_analyzer',
            input_data={
                'type': 'plan_quality',
                'plan': plan
            },
            tenant_id=tenant_id
        )

    async def design_scenario(
        self,
        tenant_id: str,
        requirements: Dict
    ) -> Dict:
        """
        Design exercise scenario.

        Args:
            tenant_id: Organization ID
            requirements: Scenario requirements

        Returns:
            Scenario design
        """
        return await self.analyze(
            analyzer_type='scenario_analyzer',
            input_data={
                'type': 'scenario_design',
                'requirements': requirements
            },
            tenant_id=tenant_id
        )

    # ========================================================================
    # ISO Clause Mapping
    # ========================================================================

    async def analyze_by_clause(
        self,
        tenant_id: str,
        clause: str
    ) -> Dict:
        """
        Analyze specific ISO 22301 clause.

        Automatically routes to appropriate analyzer based on clause:
        - 4.x (Context) → Governance
        - 6.x (Risk) → Risk
        - 8.x (BIA) → Impact
        - 9.x (Performance) → Performance

        Args:
            tenant_id: Organization ID
            clause: ISO clause (e.g., "8.2.2")

        Returns:
            Clause-specific analysis
        """
        logger.info(f"📖 Analyzing ISO clause {clause}")

        return await self.analyze(
            analyzer_type='auto',  # Auto-route based on clause
            input_data={
                'type': 'iso_audit',
                'clause': clause,
                'standard': 'ISO_22301'
            },
            tenant_id=tenant_id
        )

    # ========================================================================
    # Analyzer Info
    # ========================================================================

    async def get_available_analyzers(self) -> Dict:
        """
        Get list of available analyzers.

        Returns:
            Analyzers list with descriptions
        """
        try:
            response = await self.client.get(
                f"{self.bcm_orchestrator_url}/api/v1/analyzers"
            )

            if response.status_code == 200:
                return {
                    'success': True,
                    'analyzers': response.json()
                }
            else:
                return {
                    'success': False,
                    'error': f'Failed to get analyzers: {response.status_code}'
                }

        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }

    async def get_stats(self) -> Dict:
        """
        Get coordinator statistics.

        Returns:
            Routing stats and performance metrics
        """
        try:
            response = await self.client.get(
                f"{self.bcm_orchestrator_url}/api/v1/stats"
            )

            if response.status_code == 200:
                return {
                    'success': True,
                    'stats': response.json()
                }
            else:
                return {
                    'success': False,
                    'error': f'Failed to get stats: {response.status_code}'
                }

        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }

    # ========================================================================
    # Health Check
    # ========================================================================

    async def health_check(self) -> bool:
        """Check BCM Orchestrator availability."""
        try:
            response = await self.client.get(
                f"{self.bcm_orchestrator_url}/health",
                timeout=5.0
            )
            return response.status_code == 200
        except Exception:
            return False

    async def close(self):
        """Close HTTP client."""
        await self.client.aclose()
