"""
Integration with expertise-center
Использует 14 AI-специалистов для консультаций
"""

import sys
from pathlib import Path
from typing import Dict, Any, List, Optional
import logging

# Add expertise-center to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "expertise-center"))

try:
    from domains.bcm.specialists.bcm_advisor import BCMAdvisor
    from domains.bcm.specialists.strategic_planner import StrategicPlanner
    from domains.bcm.specialists.compliance_auditor import ComplianceAuditor
    from domains.bcm.analyzers.risk_analyzer import RiskAnalyzer
    from domains.bcm.analyzers.performance_analyzer import PerformanceAnalyzer
    from domains.bcm.tactical_assistants.risk_analyst import RiskAnalyst
    EXPERTISE_AVAILABLE = True
except ImportError as e:
    logging.warning(f"️  Expertise Center not available: {e}")
    EXPERTISE_AVAILABLE = False

logger = logging.getLogger(__name__)


class ExpertiseIntegration:
    """
    Интеграция с Expertise Center

    ЧТО ИСПОЛЬЗУЕТ (УЖЕ СУЩЕСТВУЕТ):
    - BCMAdvisor: стратегические рекомендации
    - StrategicPlanner: долгосрочное планирование
    - RiskAnalyzer: анализ рисков платформы
    - PerformanceAnalyzer: анализ производительности
    - ComplianceAuditor: проверка соответствия ISO 22301

    ЧТО ДЕЛАЕТ:
    - НЕ дублирует логику анализа
    - КОНСУЛЬТИРУЕТСЯ с существующими AI-специалистами
    - ОБЪЕДИНЯЕТ их рекомендации
    """

    def __init__(self):
        if EXPERTISE_AVAILABLE:
            try:
                self.bcm_advisor = BCMAdvisor()
                self.strategic_planner = StrategicPlanner()
                self.risk_analyzer = RiskAnalyzer()
                self.performance_analyzer = PerformanceAnalyzer()
                self.compliance_auditor = ComplianceAuditor()
                self.risk_analyst = RiskAnalyst()
                logger.info(" Expertise integration initialized (14 AI specialists available)")
            except Exception as e:
                logger.error(f" Failed to initialize some specialists: {e}")
                EXPERTISE_AVAILABLE = False

        if not EXPERTISE_AVAILABLE:
            logger.warning("️  Running without Expertise Center (fallback mode)")
            self.bcm_advisor = None

    async def get_strategic_insights(
        self,
        cycle_results: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Получить стратегические insights от BCM Advisor

        ИСПОЛЬЗУЕТ: BCMAdvisor (УЖЕ СУЩЕСТВУЕТ)
        НЕ: Hardcoded правила
        """
        if not self.bcm_advisor:
            return self._fallback_strategic_insights(cycle_results)

        try:
            # Подготовить контекст для BCM Advisor
            context = {
                "platform_metrics": {
                    "rto_compliance": cycle_results.get("rto_compliance_rate"),
                    "health_score": cycle_results.get("platform_health_score"),
                    "cycle_duration": cycle_results.get("duration_seconds")
                },
                "bia_analysis": cycle_results.get("bia_results"),
                "risk_assessment": cycle_results.get("risk_results"),
                "recent_patterns": cycle_results.get("detected_patterns", []),
                "improvements_history": cycle_results.get("improvements_applied", [])
            }

            # КОНСУЛЬТАЦИЯ С BCM ADVISOR
            insights = await self.bcm_advisor.analyze(context)

            logger.info(f" Received strategic insights from BCM Advisor")

            return {
                "source": "BCM Advisor (AI)",
                "insights": insights.get("insights", []),
                "recommendations": insights.get("recommendations", []),
                "priority_actions": insights.get("priority_actions", []),
                "confidence": insights.get("confidence", 0.8)
            }

        except Exception as e:
            logger.error(f" BCM Advisor consultation failed: {e}")
            return self._fallback_strategic_insights(cycle_results)

    async def assess_platform_risks(
        self,
        platform_state: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Оценка рисков платформы через Risk Analyzer

        ИСПОЛЬЗУЕТ: RiskAnalyzer + RiskAnalyst (УЖЕ СУЩЕСТВУЮТ)
        НЕ: Свою логику risk assessment
        """
        if not self.risk_analyzer:
            return self._fallback_risk_assessment(platform_state)

        try:
            # КОНСУЛЬТАЦИЯ С RISK ANALYZER
            risk_analysis = await self.risk_analyzer.analyze({
                "services": platform_state.get("services", []),
                "dependencies": platform_state.get("dependencies", {}),
                "recent_incidents": platform_state.get("recent_incidents", []),
                "resource_utilization": platform_state.get("resource_metrics", {})
            })

            # ДОПОЛНИТЕЛЬНАЯ КОНСУЛЬТАЦИЯ С RISK ANALYST
            if self.risk_analyst:
                tactical_risks = await self.risk_analyst.analyze_risks({
                    "current_state": platform_state,
                    "strategic_risks": risk_analysis.get("risks", [])
                })

                # Объединить стратегические и тактические риски
                all_risks = risk_analysis.get("risks", []) + tactical_risks.get("tactical_risks", [])
            else:
                all_risks = risk_analysis.get("risks", [])

            logger.info(f" Identified {len(all_risks)} platform risks")

            return {
                "source": "Risk Analyzer + Risk Analyst (AI)",
                "risks": all_risks,
                "critical_count": len([r for r in all_risks if r.get("severity") == "critical"]),
                "mitigation_plan": risk_analysis.get("mitigation_recommendations", []),
                "confidence": risk_analysis.get("confidence", 0.85)
            }

        except Exception as e:
            logger.error(f" Risk assessment failed: {e}")
            return self._fallback_risk_assessment(platform_state)

    async def analyze_performance(
        self,
        metrics: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Анализ производительности через Performance Analyzer

        ИСПОЛЬЗУЕТ: PerformanceAnalyzer (УЖЕ СУЩЕСТВУЕТ)
        """
        if not self.performance_analyzer:
            return {"status": "unavailable"}

        try:
            # КОНСУЛЬТАЦИЯ С PERFORMANCE ANALYZER
            analysis = await self.performance_analyzer.analyze({
                "cycle_metrics": metrics.get("cycle_performance", {}),
                "service_metrics": metrics.get("service_performance", {}),
                "resource_metrics": metrics.get("resource_utilization", {}),
                "sla_metrics": metrics.get("sla_compliance", {})
            })

            logger.info(f" Performance analysis completed")

            return {
                "source": "Performance Analyzer (AI)",
                "bottlenecks": analysis.get("bottlenecks", []),
                "optimization_opportunities": analysis.get("optimizations", []),
                "performance_score": analysis.get("overall_score", 0),
                "recommendations": analysis.get("recommendations", [])
            }

        except Exception as e:
            logger.error(f" Performance analysis failed: {e}")
            return {"status": "error", "error": str(e)}

    async def check_compliance(
        self,
        bcm_implementation: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Проверка соответствия ISO 22301 через Compliance Auditor

        ИСПОЛЬЗУЕТ: ComplianceAuditor (УЖЕ СУЩЕСТВУЕТ)
        """
        if not self.compliance_auditor:
            return {"status": "unavailable"}

        try:
            # КОНСУЛЬТАЦИЯ С COMPLIANCE AUDITOR
            audit_result = await self.compliance_auditor.audit({
                "bcm_processes": bcm_implementation.get("processes", []),
                "documentation": bcm_implementation.get("documentation", {}),
                "testing_results": bcm_implementation.get("test_results", {}),
                "recovery_procedures": bcm_implementation.get("recovery_procedures", [])
            })

            logger.info(f" ISO 22301 compliance check completed")

            return {
                "source": "Compliance Auditor (AI)",
                "compliance_score": audit_result.get("compliance_percentage", 0),
                "gaps": audit_result.get("gaps", []),
                "recommendations": audit_result.get("recommendations", []),
                "next_audit_date": audit_result.get("next_audit", None)
            }

        except Exception as e:
            logger.error(f" Compliance check failed: {e}")
            return {"status": "error", "error": str(e)}

    async def plan_improvements(
        self,
        current_state: Dict[str, Any],
        desired_state: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Планирование улучшений через Strategic Planner

        ИСПОЛЬЗУЕТ: StrategicPlanner (УЖЕ СУЩЕСТВУЕТ)
        """
        if not self.strategic_planner:
            return {"status": "unavailable"}

        try:
            # КОНСУЛЬТАЦИЯ СО STRATEGIC PLANNER
            plan = await self.strategic_planner.create_plan({
                "current_state": current_state,
                "desired_state": desired_state,
                "constraints": {
                    "timeline": "3_months",
                    "resources": "current_team",
                    "risk_tolerance": "low"
                }
            })

            logger.info(f" Improvement plan created with {len(plan.get('initiatives', []))} initiatives")

            return {
                "source": "Strategic Planner (AI)",
                "initiatives": plan.get("initiatives", []),
                "roadmap": plan.get("roadmap", []),
                "success_metrics": plan.get("kpis", []),
                "estimated_timeline": plan.get("timeline", "unknown")
            }

        except Exception as e:
            logger.error(f" Strategic planning failed: {e}")
            return {"status": "error", "error": str(e)}

    async def get_comprehensive_analysis(
        self,
        cycle_results: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Комплексный анализ от ВСЕХ специалистов

        ОБЪЕДИНЯЕТ консультации:
        - BCM Advisor (стратегия)
        - Risk Analyzer (риски)
        - Performance Analyzer (производительность)
        - Compliance Auditor (соответствие)
        - Strategic Planner (план улучшений)
        """
        logger.info(" Consulting ALL AI specialists for comprehensive analysis...")

        # Параллельные консультации
        strategic = await self.get_strategic_insights(cycle_results)
        risks = await self.assess_platform_risks(cycle_results.get("bia_results", {}))
        performance = await self.analyze_performance(cycle_results)
        compliance = await self.check_compliance(cycle_results)

        # Планирование на основе всех рекомендаций
        all_recommendations = (
            strategic.get("recommendations", []) +
            risks.get("mitigation_plan", []) +
            performance.get("recommendations", []) +
            compliance.get("recommendations", [])
        )

        improvement_plan = await self.plan_improvements(
            current_state={"analysis": [strategic, risks, performance, compliance]},
            desired_state={"target": "optimal_bcm_state"}
        )

        return {
            "comprehensive_analysis": {
                "strategic": strategic,
                "risks": risks,
                "performance": performance,
                "compliance": compliance,
                "improvement_plan": improvement_plan
            },
            "total_recommendations": len(all_recommendations),
            "priority_actions": self._prioritize_actions(all_recommendations),
            "consulted_specialists": [
                "BCM Advisor",
                "Risk Analyzer",
                "Performance Analyzer",
                "Compliance Auditor",
                "Strategic Planner"
            ]
        }

    def _prioritize_actions(self, recommendations: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Приоритизация действий на основе всех рекомендаций"""
        # Сортировка по важности и срочности
        prioritized = sorted(
            recommendations,
            key=lambda r: (
                r.get("severity", "low") == "critical",
                r.get("impact", 0),
                -r.get("effort", 100)
            ),
            reverse=True
        )

        return prioritized[:10]  # Top 10

    def _fallback_strategic_insights(self, cycle_results: Dict[str, Any]) -> Dict[str, Any]:
        """Упрощенные insights если BCM Advisor недоступен"""
        insights = []

        rto_rate = cycle_results.get("rto_compliance_rate", 100)
        if rto_rate < 95:
            insights.append({
                "type": "rto_compliance",
                "description": f"RTO compliance at {rto_rate}% (target: 95%+)",
                "recommendation": "Review recovery procedures and optimize critical paths",
                "priority": "high"
            })

        health_score = cycle_results.get("platform_health_score", 100)
        if health_score < 90:
            insights.append({
                "type": "platform_health",
                "description": f"Platform health score at {health_score}% (target: 90%+)",
                "recommendation": "Investigate degraded services and address root causes",
                "priority": "high"
            })

        return {
            "source": "Fallback (basic rules)",
            "insights": insights,
            "recommendations": [i["recommendation"] for i in insights],
            "confidence": 0.6
        }

    def _fallback_risk_assessment(self, platform_state: Dict[str, Any]) -> Dict[str, Any]:
        """Упрощенная оценка рисков"""
        risks = []

        # Простые проверки
        services = platform_state.get("services", [])
        unhealthy_services = [s for s in services if s.get("status") != "healthy"]

        if unhealthy_services:
            risks.append({
                "type": "service_degradation",
                "severity": "high" if len(unhealthy_services) > 2 else "medium",
                "affected_services": [s.get("name") for s in unhealthy_services],
                "recommendation": "Immediate investigation required"
            })

        return {
            "source": "Fallback (basic rules)",
            "risks": risks,
            "critical_count": len([r for r in risks if r.get("severity") == "high"]),
            "confidence": 0.5
        }


# Export
__all__ = ["ExpertiseIntegration"]
