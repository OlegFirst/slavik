"""
Analytics Core
==============

Main analytics engine that coordinates all tools and clients.

This is the "brain" of Analytics Specialist - orchestrates analysis workflows.

ARCHITECTURE UPDATE:
Uses intelligent-core/shared/platform_client.py for automatic integration
with 3 key platform "brains":
1. AI Foundation (RAG, LLM, Embeddings)
2. Expertise Center (12 Tactical Assistants + 10 Analyzers)
3. Workflow Intelligence (Case Library + ML Analysis)
"""

import logging
import uuid
import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List, Optional

# Add intelligent-core to path for shared imports
intelligent_core_path = Path(__file__).parent.parent.parent.parent / "intelligent-core"
sys.path.insert(0, str(intelligent_core_path))

from shared.platform_client import get_platform_client, PlatformClient

from ..config import settings
from ..models import (
    AnalyticsInsight,
    AnalyticsRecommendation,
    AnalyticsReport,
    AnalysisType,
    CompetencyLevel,
    SeverityLevel,
    InsightCategory,
    PlatformHealthMetrics,
    MIOEventInsight,
)
from ..clients import (
    ProcessAnalyticsClient,
    MIOManagerClient,
    AIOrchestratorClient,
    PredictiveClient,
    CollectiveClient,
    CommunityIntelligenceClient,
    report_daily_health_check
)
from ..tools import (
    MetricsDiscoveryTool,
    DependencyMapperTool,
    ASTAnalyzerTool,
    APIMapperTool,
    ModuleScannerTool,
    DependencyValidatorTool,
    SecurityScannerTool,
)

logger = logging.getLogger(__name__)


class AnalyticsCore:
    """
    Core analytics engine - FULLY INTEGRATED with platform

    Coordinates all analysis tools and clients to provide comprehensive
    platform intelligence.

    INTEGRATIONS:
    - ✅ Process Analytics (process mining)
    - ✅ MIO Manager (coordination & reporting)
    - ✅ AI Orchestrator (decision context)
    - ✅ Predictive Service (ML predictions)
    - ✅ Collective AI (collective intelligence)
    - ✅ Community Intelligence (knowledge sharing)

    Responsibilities:
    - Orchestrate analysis across multiple tools
    - Generate ML-powered insights
    - Report to MIO Manager
    - Provide context to AI Orchestrator
    - Contribute to Collective intelligence
    - Share anonymized insights with Community

    Example:
        ```python
        core = AnalyticsCore()
        await core.initialize()

        # Daily health check with full integration
        report = await core.analyze_platform_health()
        print(f"Health score: {report.overall_health_score}/100")

        # Automatically reports to all integrated services
        await core.report_to_mio(report)
        ```
    """

    def __init__(self):
        """
        Initialize Analytics Core with AUTOMATIC platform integration

        Uses shared platform_client for:
        - AI Foundation (RAG, LLM, Embeddings)
        - Expertise Center (12 Tactical Assistants)
        - Workflow Intelligence (Case Library)

        Plus specialized Analytics clients:
        - Process Analytics (process mining)
        - MIO Manager (coordination)
        - Predictive Service (ML predictions)
        - Collective AI (collective intelligence)
        - Community Intelligence (knowledge sharing)
        """
        # ===============================================
        # PLATFORM CLIENT - Automatic Integration
        # ===============================================
        self.platform: PlatformClient = get_platform_client()

        # ===============================================
        # ANALYTICS-SPECIFIC CLIENTS
        # ===============================================

        # Core Clients (always available)
        self.pa_client = ProcessAnalyticsClient()
        self.mio_client = MIOManagerClient()

        # AI Orchestrator integration
        self.orchestrator_client = AIOrchestratorClient()

        # Predictive Service integration (middle+)
        self.predictive_client = None
        if settings.COMPETENCY_LEVEL in ['middle', 'senior', 'expert']:
            self.predictive_client = PredictiveClient()

        # Collective AI integration (senior+)
        self.collective_client = None
        if settings.COMPETENCY_LEVEL in ['senior', 'expert']:
            self.collective_client = CollectiveClient()

        # Community Intelligence integration (all levels)
        self.community_client = CommunityIntelligenceClient()

        # Tools (based on competency level)
        self.competency = CompetencyLevel(settings.COMPETENCY_LEVEL)
        self.tools = self._initialize_tools()

        # State
        self.initialized = False
        self.last_analysis: Optional[AnalyticsReport] = None

        # Integration status (will be validated in initialize())
        self.integration_status = {
            # Platform "brains" (auto via platform_client)
            'ai_foundation': False,          # RAG, LLM, Embeddings
            'expertise_center': False,       # 12 Tactical Assistants
            'workflow_intelligence': False,  # Case Library + ML

            # Analytics-specific clients
            'process_analytics': True,
            'mio_manager': True,
            'ai_orchestrator': True,
            'predictive': self.predictive_client is not None,
            'collective': self.collective_client is not None,
            'community': True
        }

        total_integrations = len(self.integration_status)
        logger.info(
            f"AnalyticsCore configured with competency: {self.competency}, "
            f"tools: {list(self.tools.keys())}, "
            f"potential integrations: {total_integrations} "
            f"(call initialize() to validate)"
        )

    def _initialize_tools(self) -> Dict[str, Any]:
        """
        Initialize tools based on competency level

        Junior: metrics_discovery, module_scanner, ast_analyzer
        Middle: + dependency_mapper, api_mapper, dependency_validator
        Senior: + security_scanner
        Expert: + all advanced tools

        Returns:
            Dict of available tools
        """
        tools = {}

        # Junior tools (always available)
        tools["metrics_discovery"] = MetricsDiscoveryTool()
        tools["module_scanner"] = ModuleScannerTool()
        tools["ast_analyzer"] = ASTAnalyzerTool()

        # Middle tools
        if self.competency in [CompetencyLevel.MIDDLE, CompetencyLevel.SENIOR, CompetencyLevel.EXPERT]:
            tools["dependency_mapper"] = DependencyMapperTool()
            tools["api_mapper"] = APIMapperTool()
            tools["dependency_validator"] = DependencyValidatorTool()

        # Senior tools
        if self.competency in [CompetencyLevel.SENIOR, CompetencyLevel.EXPERT]:
            tools["security_scanner"] = SecurityScannerTool()

        # Expert tools
        if self.competency == CompetencyLevel.EXPERT:
            # Placeholder for future advanced tools
            pass

        logger.info(f"Initialized {len(tools)} tools for {self.competency} level")
        return tools

    async def initialize(self) -> None:
        """
        Initialize core and verify connectivity

        Checks health of ALL integrated services including:
        - Platform Client (AI Foundation, Expertise Center, Workflow Intelligence)
        - Analytics-specific clients (Process Analytics, MIO, etc.)
        """
        logger.info("🔄 Initializing AnalyticsCore with FULL platform integration...")

        health_checks = {}

        # ============================================================
        # PLATFORM CLIENT - Check 3 key "brains"
        # ============================================================
        logger.info("📡 Checking Platform Client integration...")
        try:
            platform_health = await self.platform.health_check()

            health_checks['ai_foundation'] = platform_health.get('ai_foundation', False)
            health_checks['expertise_center'] = platform_health.get('expertise_center', False)
            health_checks['workflow_intelligence'] = platform_health.get('workflow_intelligence', False)

            if platform_health.get('ai_foundation'):
                logger.info("  ✅ AI Foundation (RAG, LLM, Embeddings)")
            else:
                logger.warning("  ⚠️  AI Foundation unavailable")

            if platform_health.get('expertise_center'):
                logger.info("  ✅ Expertise Center (12 Tactical Assistants)")
            else:
                logger.warning("  ⚠️  Expertise Center unavailable")

            if platform_health.get('workflow_intelligence'):
                logger.info("  ✅ Workflow Intelligence (Case Library)")
            else:
                logger.warning("  ⚠️  Workflow Intelligence unavailable")

        except Exception as e:
            logger.error(f"❌ Platform Client check failed: {e}")
            health_checks['ai_foundation'] = False
            health_checks['expertise_center'] = False
            health_checks['workflow_intelligence'] = False

        # ============================================================
        # ANALYTICS-SPECIFIC CLIENTS
        # ============================================================
        logger.info("🔍 Checking Analytics-specific clients...")

        # Check Process Analytics
        try:
            pa_health = await self.pa_client.health_check()
            health_checks['process_analytics'] = pa_health.get('status') == 'healthy'
            logger.info(f"  ✅ Process Analytics: {pa_health.get('status')}")
        except Exception as e:
            health_checks['process_analytics'] = False
            logger.warning(f"  ⚠️  Process Analytics: {e}")

        # Check MIO Manager
        try:
            mio_health = await self.mio_client.health_check()
            health_checks['mio_manager'] = mio_health.get('status') == 'healthy'
            logger.info(f"  ✅ MIO Manager: {mio_health.get('status')}")
        except Exception as e:
            health_checks['mio_manager'] = False
            logger.warning(f"  ⚠️  MIO Manager: {e}")

        # Check AI Orchestrator
        try:
            orch_health = await self.orchestrator_client.health_check()
            health_checks['ai_orchestrator'] = orch_health.get('status') == 'healthy'
            logger.info(f"  ✅ AI Orchestrator: {orch_health.get('status')}")
        except Exception as e:
            health_checks['ai_orchestrator'] = False
            logger.warning(f"  ⚠️  AI Orchestrator: {e}")

        # Check Predictive Service (if available)
        if self.predictive_client:
            try:
                pred_health = await self.predictive_client.health_check()
                health_checks['predictive'] = pred_health.get('status') == 'healthy'
                logger.info(f"  ✅ Predictive Service: {pred_health.get('status')}")
            except Exception as e:
                health_checks['predictive'] = False
                logger.warning(f"  ⚠️  Predictive Service: {e}")

        # Check Collective (if available)
        if self.collective_client:
            try:
                coll_health = await self.collective_client.health_check()
                health_checks['collective'] = coll_health.get('status') == 'healthy'
                logger.info(f"  ✅ Collective AI: {coll_health.get('status')}")
            except Exception as e:
                health_checks['collective'] = False
                logger.warning(f"  ⚠️  Collective AI: {e}")

        # Check Community Intelligence
        try:
            comm_health = await self.community_client.health_check()
            health_checks['community'] = comm_health.get('status') == 'healthy'
            logger.info(f"  ✅ Community Intelligence: {comm_health.get('status')}")
        except Exception as e:
            health_checks['community'] = False
            logger.warning(f"  ⚠️  Community Intelligence: {e}")

        # ============================================================
        # SUMMARY
        # ============================================================
        healthy_count = sum(health_checks.values())
        total_count = len(health_checks)

        # Platform "brains" count
        platform_count = sum([
            health_checks.get('ai_foundation', False),
            health_checks.get('expertise_center', False),
            health_checks.get('workflow_intelligence', False)
        ])

        self.initialized = True
        self.integration_status = health_checks

        logger.info("=" * 60)
        logger.info(f"🎯 AnalyticsCore Initialization Complete:")
        logger.info(f"   Platform Brains: {platform_count}/3 healthy")
        logger.info(f"   Analytics Clients: {healthy_count - platform_count}/{total_count - 3} healthy")
        logger.info(f"   Total: {healthy_count}/{total_count} integrations")
        logger.info("=" * 60)

        if platform_count < 3:
            logger.warning(
                "⚠️  Some platform 'brains' unavailable. "
                "Consider starting AI Foundation, Expertise Center, or Workflow Intelligence."
            )

        if healthy_count < total_count:
            logger.warning(
                f"⚠️  {total_count - healthy_count} integration(s) unavailable. "
                f"Analytics will work with reduced capabilities."
            )
        else:
            logger.info("✅ ALL integrations healthy - FULL capabilities available!")

    # ========================================================================
    # PLATFORM HEALTH ANALYSIS
    # ========================================================================

    async def analyze_platform_health(self) -> AnalyticsReport:
        """
        Comprehensive platform health analysis

        Combines insights from:
        - Process analytics (bottlenecks, patterns)
        - Metrics coverage
        - Dependencies (if middle+)

        Returns:
            Complete analytics report

        Example:
            ```python
            report = await core.analyze_platform_health()
            print(f"Found {len(report.insights)} insights")
            print(f"Health: {report.overall_health_score}/100")
            ```
        """
        logger.info("Starting platform health analysis...")

        insights = []
        recommendations = []

        # 1. Process Analytics
        process_insights = await self._analyze_processes()
        insights.extend(process_insights["insights"])
        recommendations.extend(process_insights["recommendations"])

        # 2. Metrics Coverage
        metrics_insights = await self._analyze_metrics_coverage()
        insights.extend(metrics_insights["insights"])
        recommendations.extend(metrics_insights["recommendations"])

        # 3. Dependencies (if middle+)
        if "dependency_mapper" in self.tools:
            dep_insights = await self._analyze_dependencies()
            insights.extend(dep_insights["insights"])
            recommendations.extend(dep_insights["recommendations"])

        # Calculate overall health score
        health_score = self._calculate_overall_health_score(insights)

        # Generate report
        report = AnalyticsReport(
            id=f"report_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            analysis_type=AnalysisType.PLATFORM_HEALTH,
            generated_by=self.competency,
            summary=self._generate_summary(insights, recommendations),
            overall_health_score=health_score,
            insights=insights,
            recommendations=recommendations,
            metadata={
                "total_insights": len(insights),
                "critical_count": len([i for i in insights if i.severity == SeverityLevel.CRITICAL]),
                "high_count": len([i for i in insights if i.severity == SeverityLevel.HIGH]),
                "tools_used": list(self.tools.keys())
            }
        )

        self.last_analysis = report

        logger.info(
            f"✅ Platform health analysis complete: "
            f"score={health_score:.1f}/100, "
            f"insights={len(insights)}, "
            f"critical={report.metadata['critical_count']}"
        )

        return report

    async def _analyze_processes(self) -> Dict[str, Any]:
        """Analyze processes from process-analytics"""
        insights = []
        recommendations = []

        try:
            # Get all processes
            processes = await self.pa_client.get_all_processes()

            for process_id in processes:
                # Comprehensive analysis
                analysis = await self.pa_client.comprehensive_analysis(process_id)

                # Bottlenecks
                for bottleneck in analysis.get("bottlenecks", []):
                    insight = AnalyticsInsight(
                        id=f"insight_{uuid.uuid4().hex[:8]}",
                        category=InsightCategory.BOTTLENECK,
                        severity=SeverityLevel.HIGH if bottleneck.get("impact_score", 0) > 7 else SeverityLevel.MEDIUM,
                        title=f"Bottleneck in {process_id}",
                        description=f"Step '{bottleneck.get('step_name')}' takes {bottleneck.get('avg_duration_minutes', 0):.1f} minutes on average",
                        affected_components=[process_id],
                        impact=f"Impact score: {bottleneck.get('impact_score', 0)}/10",
                        evidence=bottleneck
                    )
                    insights.append(insight)

                    # Recommendation
                    rec = AnalyticsRecommendation(
                        id=f"rec_{uuid.uuid4().hex[:8]}",
                        related_insight_id=insight.id,
                        action_type="optimize",
                        title=f"Optimize {bottleneck.get('step_name')}",
                        description=f"Allocate additional resources or optimize logic",
                        priority=SeverityLevel.HIGH,
                        estimated_effort="medium",
                        expected_impact="50% reduction in bottleneck duration",
                        automated=False
                    )
                    recommendations.append(rec)

                # Deviations
                for deviation in analysis.get("deviations", []):
                    insight = AnalyticsInsight(
                        id=f"insight_{uuid.uuid4().hex[:8]}",
                        category=InsightCategory.QUALITY_ISSUE,
                        severity=SeverityLevel.MEDIUM,
                        title=f"Process deviation in {process_id}",
                        description=f"Deviation type: {deviation.get('type')}",
                        affected_components=[process_id],
                        impact=f"Frequency: {deviation.get('frequency', 0)} times",
                        evidence=deviation
                    )
                    insights.append(insight)

        except Exception as e:
            logger.error(f"Process analysis failed: {e}")

        return {"insights": insights, "recommendations": recommendations}

    async def _analyze_metrics_coverage(self) -> Dict[str, Any]:
        """Analyze metrics coverage using MetricsDiscoveryTool"""
        insights = []
        recommendations = []

        try:
            tool = self.tools.get("metrics_discovery")
            if not tool or not tool.available:
                logger.warning("Metrics discovery tool not available")
                return {"insights": insights, "recommendations": recommendations}

            # Generate insights from tool
            tool_insights = await tool.generate_insights()

            for ti in tool_insights:
                insight = AnalyticsInsight(
                    id=f"insight_{uuid.uuid4().hex[:8]}",
                    category=InsightCategory.IMPROVEMENT_OPPORTUNITY,
                    severity=SeverityLevel(ti.get("severity", "low")),
                    title=ti.get("message", "Metrics coverage issue"),
                    description=ti.get("message", ""),
                    affected_components=ti.get("affected_modules", []),
                    impact=f"Category: {ti.get('category')}",
                    evidence=ti
                )
                insights.append(insight)

                rec = AnalyticsRecommendation(
                    id=f"rec_{uuid.uuid4().hex[:8]}",
                    related_insight_id=insight.id,
                    action_type="improve",
                    title=ti.get("recommendation", "Improve metrics coverage"),
                    description=ti.get("recommendation", ""),
                    priority=SeverityLevel(ti.get("severity", "low")),
                    estimated_effort="low",
                    expected_impact="Better observability",
                    automated=False
                )
                recommendations.append(rec)

        except Exception as e:
            logger.error(f"Metrics coverage analysis failed: {e}")

        return {"insights": insights, "recommendations": recommendations}

    async def _analyze_dependencies(self) -> Dict[str, Any]:
        """Analyze dependencies using DependencyMapperTool"""
        insights = []
        recommendations = []

        try:
            tool = self.tools.get("dependency_mapper")
            if not tool or not tool.available:
                return {"insights": insights, "recommendations": recommendations}

            # Generate insights from tool
            tool_insights = await tool.generate_insights()

            for ti in tool_insights:
                insight = AnalyticsInsight(
                    id=f"insight_{uuid.uuid4().hex[:8]}",
                    category=InsightCategory.DEPENDENCY_CONFLICT if "conflict" in ti.get("category", "") else InsightCategory.QUALITY_ISSUE,
                    severity=SeverityLevel(ti.get("severity", "low")),
                    title=ti.get("message", "Dependency issue"),
                    description=ti.get("message", ""),
                    affected_components=ti.get("affected_services", []),
                    impact=f"Category: {ti.get('category')}",
                    evidence=ti
                )
                insights.append(insight)

                rec = AnalyticsRecommendation(
                    id=f"rec_{uuid.uuid4().hex[:8]}",
                    related_insight_id=insight.id,
                    action_type="fix",
                    title=ti.get("recommendation", "Fix dependency issue"),
                    description=ti.get("recommendation", ""),
                    priority=SeverityLevel(ti.get("severity", "low")),
                    estimated_effort="medium",
                    expected_impact="Improved stability",
                    automated=False
                )
                recommendations.append(rec)

        except Exception as e:
            logger.error(f"Dependency analysis failed: {e}")

        return {"insights": insights, "recommendations": recommendations}

    def _calculate_overall_health_score(self, insights: List[AnalyticsInsight]) -> float:
        """
        Calculate overall platform health score (0-100)

        Factors:
        - Critical issues: -20 points each
        - High severity: -10 points each
        - Medium severity: -5 points each
        - Low severity: -2 points each

        Args:
            insights: List of all insights

        Returns:
            Health score 0-100
        """
        score = 100.0

        for insight in insights:
            if insight.severity == SeverityLevel.CRITICAL:
                score -= 20
            elif insight.severity == SeverityLevel.HIGH:
                score -= 10
            elif insight.severity == SeverityLevel.MEDIUM:
                score -= 5
            elif insight.severity == SeverityLevel.LOW:
                score -= 2

        return max(0, min(100, score))

    def _generate_summary(self, insights: List[AnalyticsInsight], recommendations: List[AnalyticsRecommendation]) -> str:
        """Generate executive summary"""
        critical_count = len([i for i in insights if i.severity == SeverityLevel.CRITICAL])
        high_count = len([i for i in insights if i.severity == SeverityLevel.HIGH])

        bottleneck_count = len([i for i in insights if i.category == InsightCategory.BOTTLENECK])
        conflict_count = len([i for i in insights if i.category == InsightCategory.DEPENDENCY_CONFLICT])

        summary_parts = []

        if critical_count > 0:
            summary_parts.append(f"{critical_count} critical issues")
        if high_count > 0:
            summary_parts.append(f"{high_count} high severity issues")
        if bottleneck_count > 0:
            summary_parts.append(f"{bottleneck_count} bottlenecks")
        if conflict_count > 0:
            summary_parts.append(f"{conflict_count} dependency conflicts")

        if summary_parts:
            return f"Found: {', '.join(summary_parts)}. {len(recommendations)} recommendations provided."
        else:
            return "Platform health is good. No critical issues detected."

    # ========================================================================
    # MIO MANAGER INTEGRATION
    # ========================================================================

    async def report_to_mio(self, report: AnalyticsReport) -> Dict[str, Any]:
        """
        Report analytics insights to MIO Manager

        Args:
            report: Analytics report to send

        Returns:
            MIO Manager response

        Example:
            ```python
            report = await core.analyze_platform_health()
            response = await core.report_to_mio(report)
            print(f"Reported to MIO: {response['status']}")
            ```
        """
        try:
            # Prepare critical issues
            critical_issues = [
                {
                    "title": insight.title,
                    "affected_components": insight.affected_components,
                    "impact": insight.impact
                }
                for insight in report.critical_insights
            ]

            # Prepare recommendations
            recommendations_data = [
                {
                    "action": rec.action_type,
                    "title": rec.title,
                    "priority": rec.priority.value,
                    "automated": rec.automated
                }
                for rec in report.recommendations[:5]  # Top 5 recommendations
            ]

            # Use convenience function
            response = await report_daily_health_check(
                mio_client=self.mio_client,
                health_score=report.overall_health_score,
                critical_issues=critical_issues,
                recommendations=recommendations_data,
                metadata={
                    "report_id": report.id,
                    "generated_by": report.generated_by.value,
                    "total_insights": len(report.insights)
                }
            )

            logger.info(f"✅ Reported to MIO Manager: {response.get('status')}")
            return response

        except Exception as e:
            logger.error(f"Failed to report to MIO: {e}")
            return {"status": "error", "error": str(e)}

    # ========================================================================
    # INCIDENT INVESTIGATION
    # ========================================================================

    async def investigate_incident(self, incident_id: str) -> AnalyticsReport:
        """
        Investigate a specific incident

        Args:
            incident_id: Incident identifier

        Returns:
            Investigation report

        Example:
            ```python
            report = await core.investigate_incident("inc_001")
            print(f"Root cause: {report.summary}")
            ```
        """
        logger.info(f"Investigating incident: {incident_id}")

        insights = []
        recommendations = []

        # TODO: Implement incident-specific analysis
        # For now, return basic report

        report = AnalyticsReport(
            id=f"incident_{incident_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            analysis_type=AnalysisType.INCIDENT_INVESTIGATION,
            generated_by=self.competency,
            summary=f"Investigation of incident {incident_id} in progress",
            overall_health_score=None,
            insights=insights,
            recommendations=recommendations,
            metadata={"incident_id": incident_id}
        )

        return report

    # ========================================================================
    # CONTEXT FOR AI ORCHESTRATOR
    # ========================================================================

    async def get_platform_insights(
        self,
        context_type: Optional[str] = None,
        timeframe_days: int = 7
    ) -> Dict[str, Any]:
        """
        Get platform insights for AI Orchestrator

        Provides context to help AI Orchestrator make better decisions.

        Args:
            context_type: Type of context needed
            timeframe_days: Timeframe for analysis

        Returns:
            Platform insights

        Example:
            ```python
            # AI Orchestrator queries this
            insights = await analytics.get_platform_insights()
            # Uses insights in decision-making
            ```
        """
        if not self.last_analysis:
            # No analysis yet, run one
            await self.analyze_platform_health()

        if not self.last_analysis:
            return {"error": "No analysis available"}

        return {
            "health_score": self.last_analysis.overall_health_score,
            "critical_insights": [
                {
                    "category": i.category.value,
                    "title": i.title,
                    "affected_components": i.affected_components,
                    "impact": i.impact
                }
                for i in self.last_analysis.critical_insights
            ],
            "recommendations": [
                {
                    "action_type": r.action_type,
                    "title": r.title,
                    "priority": r.priority.value,
                    "automated": r.automated
                }
                for r in self.last_analysis.recommendations[:10]
            ],
            "last_analysis_at": self.last_analysis.generated_at.isoformat(),
            "competency_level": self.competency.value
        }
