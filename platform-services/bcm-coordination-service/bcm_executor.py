"""
BCM Executor - Координатор BCM-специфичных задач
================================================

Координирует выполнение BCM анализов через:
- BCM Services Orchestrator (координация 10 анализаторов)
- Platform Services (BIA, Risk, etc.)
- Expertise Center (tactical assistants)

Функции:
- Execute BIA analysis
- Execute Risk analysis
- Execute Compliance checks
- Coordinate batch analyses
- Route to appropriate BCM analyzers

ВОПРОСЫ ДЛЯ ОБСУЖДЕНИЯ:
========================

1. Архитектура координации:
   - Двухуровневая (ядро → офис → специалисты)?
   - Прямая (ядро → специалисты)?
   - Автономный офис?

2. Связь с intelligent-core/orchestration/bcm-services-orchestrator:
   - Как должны взаимодействовать?
   - Кто принимает решения?
   - Кто роутит задачи?

3. Место размещения:
   - platform-services/bcm-coordination-service/?
   - Или другое место?
"""

import logging
import httpx
from typing import Dict, Optional, List
from pathlib import Path
import sys

logger = logging.getLogger(__name__)

# Add intelligent-core to path for imports
INTELLIGENT_CORE = Path(__file__).parent.parent.parent / 'intelligent-core'
sys.path.insert(0, str(INTELLIGENT_CORE))


class BCMExecutor:
    """
    Исполнитель BCM-специфичных задач.

    Интегрируется с:
    1. BCM Services Orchestrator (intelligent-core/orchestration/bcm-services-orchestrator)
       - Координирует 10 BCM анализаторов
       - Provides ISO clause mapping
       - Manages BCM workflows

    2. Platform Services (platform-services/bia-service, etc.)
       - Executes actual BIA, Risk analysis
       - Stores results in database

    3. Expertise Center (intelligent-core/expertise-center)
       - Tactical assistants for domain expertise

    Возможности:
    - Route analysis requests to appropriate analyzer
    - Execute single analysis (BIA, Risk, Compliance, etc.)
    - Execute batch analyses (Risk → Impact → Plan pipeline)
    - Coordinate with platform services
    - ISO 22301 clause-based routing
    """

    def __init__(
        self,
        bcm_orchestrator_url: str = "http://localhost:8070",
        platform_services_url: str = "http://localhost:8000",
        workspace_root: str = "/Users/MD/AI-Platform-ISO"
    ):
        """
        Initialize BCM Executor.

        Args:
            bcm_orchestrator_url: BCM Services Orchestrator endpoint
            platform_services_url: Platform services base URL
            workspace_root: Workspace root directory
        """
        self.bcm_orchestrator_url = bcm_orchestrator_url
        self.platform_services_url = platform_services_url
        self.workspace_root = Path(workspace_root)
        self.client = httpx.AsyncClient(timeout=60.0)

        # Import AnalyzerCoordinator for direct coordination
        try:
            from orchestration.bcm_services_orchestrator.analyzer_coordinator import (
                AnalyzerCoordinator,
                AnalyzerType
            )
            self.AnalyzerType = AnalyzerType
            self.coordinator_available = True
            logger.info("✅ BCM AnalyzerCoordinator available for direct coordination")
        except ImportError as e:
            logger.warning(f"⚠️  BCM AnalyzerCoordinator not available: {e}")
            self.coordinator_available = False

    # ========================================================================
    # High-Level BCM Task Execution
    # ========================================================================

    async def execute_bcm_task(self, task: Dict) -> Dict:
        """
        Execute BCM-specific task.

        Args:
            task: Task dict with 'action' and 'parameters'

        Supported actions:
        - 'bia_analysis': Execute BIA
        - 'risk_analysis': Execute Risk analysis
        - 'compliance_check': Execute ISO compliance check
        - 'batch_analysis': Execute multiple analyses in sequence
        - 'route_analysis': Auto-route to best analyzer

        Returns:
            Execution result
        """
        action = task.get('action')
        params = task.get('parameters', {})

        logger.info(f"🔍 Executing BCM task: {action}")

        try:
            if action == 'bia_analysis':
                return await self.execute_bia(params)

            elif action == 'risk_analysis':
                return await self.execute_risk_analysis(params)

            elif action == 'compliance_check':
                return await self.execute_compliance_check(params)

            elif action == 'batch_analysis':
                return await self.execute_batch_analysis(params)

            elif action == 'route_analysis':
                return await self.route_to_analyzer(params)

            else:
                return {
                    'success': False,
                    'error': f'Unknown BCM action: {action}'
                }

        except Exception as e:
            logger.error(f"❌ BCM task execution failed: {e}")
            return {
                'success': False,
                'error': str(e)
            }

    # ========================================================================
    # Specific BCM Analyses
    # ========================================================================

    async def execute_bia(self, params: Dict) -> Dict:
        """
        Execute Business Impact Analysis.

        Args:
            params: BIA parameters
                - tenant_id: Organization ID
                - scope: Analysis scope
                - processes: List of processes to analyze

        Returns:
            BIA result
        """
        tenant_id = params.get('tenant_id')
        scope = params.get('scope', 'full')

        logger.info(f"📊 Executing BIA for tenant: {tenant_id}")

        try:
            # Option 1: Use BCM Orchestrator
            if self.bcm_orchestrator_url:
                response = await self.client.post(
                    f"{self.bcm_orchestrator_url}/api/v1/analyze",
                    json={
                        'analyzer_type': 'impact_analyzer',
                        'input_data': {
                            'type': 'bia_analysis',
                            'tenant_id': tenant_id,
                            'scope': scope,
                            'processes': params.get('processes', [])
                        },
                        'tenant_id': tenant_id
                    }
                )

                if response.status_code == 200:
                    result = response.json()
                    logger.info("✅ BIA analysis completed")
                    return {
                        'success': True,
                        'analysis_type': 'bia',
                        'result': result
                    }

            # Option 2: Call platform service directly
            response = await self.client.post(
                f"{self.platform_services_url}/bia/analyze",
                json={
                    'tenant_id': tenant_id,
                    'scope': scope,
                    'processes': params.get('processes', [])
                }
            )

            if response.status_code == 200:
                return {
                    'success': True,
                    'analysis_type': 'bia',
                    'result': response.json()
                }
            else:
                return {
                    'success': False,
                    'error': f'BIA service returned {response.status_code}'
                }

        except Exception as e:
            logger.error(f"❌ BIA execution failed: {e}")
            return {
                'success': False,
                'error': str(e)
            }

    async def execute_risk_analysis(self, params: Dict) -> Dict:
        """
        Execute Risk Analysis (FAIR-based).

        Args:
            params: Risk analysis parameters
                - tenant_id: Organization ID
                - scenario: Risk scenario
                - assets: Assets to analyze

        Returns:
            Risk analysis result
        """
        tenant_id = params.get('tenant_id')
        scenario = params.get('scenario')

        logger.info(f"⚠️  Executing Risk Analysis: {scenario}")

        try:
            # Use BCM Orchestrator → Risk Analyzer
            response = await self.client.post(
                f"{self.bcm_orchestrator_url}/api/v1/analyze",
                json={
                    'analyzer_type': 'risk_analyzer',
                    'input_data': {
                        'type': 'risk_assessment',
                        'scenario': scenario,
                        'assets': params.get('assets', []),
                        'threat_actors': params.get('threat_actors', [])
                    },
                    'tenant_id': tenant_id
                }
            )

            if response.status_code == 200:
                result = response.json()
                logger.info("✅ Risk analysis completed")
                return {
                    'success': True,
                    'analysis_type': 'risk',
                    'result': result
                }
            else:
                return {
                    'success': False,
                    'error': f'Risk analysis failed: {response.status_code}'
                }

        except Exception as e:
            logger.error(f"❌ Risk analysis failed: {e}")
            return {
                'success': False,
                'error': str(e)
            }

    async def execute_compliance_check(self, params: Dict) -> Dict:
        """
        Execute ISO 22301 Compliance Check.

        Args:
            params: Compliance check parameters
                - tenant_id: Organization ID
                - standard: Standard to check (default: ISO_22301)
                - clauses: Specific clauses to check

        Returns:
            Compliance check result
        """
        tenant_id = params.get('tenant_id')
        standard = params.get('standard', 'ISO_22301')
        clauses = params.get('clauses', [])

        logger.info(f"📋 Executing Compliance Check: {standard}")

        try:
            response = await self.client.post(
                f"{self.bcm_orchestrator_url}/api/v1/analyze",
                json={
                    'analyzer_type': 'compliance_analyzer',
                    'input_data': {
                        'type': 'compliance_gap',
                        'standard': standard,
                        'clauses': clauses,
                        'current_controls': params.get('current_controls', {})
                    },
                    'tenant_id': tenant_id
                }
            )

            if response.status_code == 200:
                result = response.json()
                logger.info("✅ Compliance check completed")
                return {
                    'success': True,
                    'analysis_type': 'compliance',
                    'result': result
                }
            else:
                return {
                    'success': False,
                    'error': f'Compliance check failed: {response.status_code}'
                }

        except Exception as e:
            logger.error(f"❌ Compliance check failed: {e}")
            return {
                'success': False,
                'error': str(e)
            }

    # ========================================================================
    # Batch & Routing
    # ========================================================================

    async def execute_batch_analysis(self, params: Dict) -> Dict:
        """
        Execute multiple analyses in sequence.

        Example pipeline: Risk → Impact → Plan

        Args:
            params: Batch parameters
                - tenant_id: Organization ID
                - analyzer_sequence: List of analyzer types
                - input_data: Initial input data

        Returns:
            Batch analysis result
        """
        tenant_id = params.get('tenant_id')
        analyzer_sequence = params.get('analyzer_sequence', [])
        input_data = params.get('input_data', {})

        logger.info(f"🔄 Executing batch analysis: {len(analyzer_sequence)} analyzers")

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
                logger.info("✅ Batch analysis completed")
                return {
                    'success': True,
                    'analysis_type': 'batch',
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

    async def route_to_analyzer(self, params: Dict) -> Dict:
        """
        Auto-route analysis to best analyzer.

        Args:
            params: Routing parameters
                - tenant_id: Organization ID
                - input_data: Analysis input (type auto-detected)

        Returns:
            Analysis result with routing info
        """
        tenant_id = params.get('tenant_id')
        input_data = params.get('input_data', {})

        logger.info("🎯 Auto-routing analysis to best analyzer")

        try:
            response = await self.client.post(
                f"{self.bcm_orchestrator_url}/api/v1/analyze",
                json={
                    'analyzer_type': 'auto',  # Auto-detect
                    'input_data': input_data,
                    'tenant_id': tenant_id
                }
            )

            if response.status_code == 200:
                result = response.json()
                logger.info(f"✅ Routed to {result.get('analyzer')}")
                return {
                    'success': True,
                    'analysis_type': 'auto_routed',
                    'result': result
                }
            else:
                return {
                    'success': False,
                    'error': f'Routing failed: {response.status_code}'
                }

        except Exception as e:
            logger.error(f"❌ Routing failed: {e}")
            return {
                'success': False,
                'error': str(e)
            }

    # ========================================================================
    # ISO Clause Mapping
    # ========================================================================

    async def analyze_by_iso_clause(self, clause: str, tenant_id: str) -> Dict:
        """
        Execute analysis for specific ISO 22301 clause.

        Maps clauses to appropriate analyzers:
        - 4.x (Context) → Governance Analyzer
        - 6.x (Risk) → Risk Analyzer
        - 8.x (BIA) → Impact Analyzer
        - 9.x (Performance) → Performance Analyzer

        Args:
            clause: ISO 22301 clause (e.g., "8.2.2")
            tenant_id: Organization ID

        Returns:
            Clause analysis result
        """
        logger.info(f"📖 Analyzing ISO 22301 clause: {clause}")

        # Map clause to analyzer
        clause_prefix = clause.split('.')[0]

        analyzer_mapping = {
            '4': 'governance_analyzer',  # Context of the organization
            '5': 'governance_analyzer',  # Leadership
            '6': 'risk_analyzer',        # Planning (Risk assessment)
            '7': 'governance_analyzer',  # Support
            '8': 'impact_analyzer',      # Operation (BIA)
            '9': 'performance_analyzer', # Performance evaluation
            '10': 'learning_analyzer'    # Improvement
        }

        analyzer_type = analyzer_mapping.get(clause_prefix, 'compliance_analyzer')

        try:
            response = await self.client.post(
                f"{self.bcm_orchestrator_url}/api/v1/analyze",
                json={
                    'analyzer_type': analyzer_type,
                    'input_data': {
                        'type': 'iso_audit',
                        'clause': clause,
                        'standard': 'ISO_22301'
                    },
                    'tenant_id': tenant_id
                }
            )

            if response.status_code == 200:
                result = response.json()
                logger.info(f"✅ ISO clause {clause} analysis completed")
                return {
                    'success': True,
                    'clause': clause,
                    'analyzer': analyzer_type,
                    'result': result
                }
            else:
                return {
                    'success': False,
                    'error': f'ISO clause analysis failed: {response.status_code}'
                }

        except Exception as e:
            logger.error(f"❌ ISO clause analysis failed: {e}")
            return {
                'success': False,
                'error': str(e)
            }

    # ========================================================================
    # Health & Stats
    # ========================================================================

    async def health_check(self) -> Dict:
        """
        Check health of BCM components.

        Returns:
            Health status
        """
        try:
            # Check BCM Orchestrator
            response = await self.client.get(
                f"{self.bcm_orchestrator_url}/health",
                timeout=5.0
            )
            bcm_healthy = response.status_code == 200

            return {
                'success': True,
                'bcm_orchestrator': {
                    'healthy': bcm_healthy,
                    'url': self.bcm_orchestrator_url
                },
                'coordinator_available': self.coordinator_available
            }

        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }

    async def get_available_analyzers(self) -> Dict:
        """
        Get list of available BCM analyzers.

        Returns:
            Analyzers list
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

    async def close(self):
        """Close HTTP client."""
        await self.client.aclose()
