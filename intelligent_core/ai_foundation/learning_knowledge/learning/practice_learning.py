"""
Practice Learning Engine - Learning Through DOING

This module enables the platform to learn from PRACTICE, not theory:
- Measures effectiveness of self-applied BCM
- Learns from real incidents and recoveries
- Improves based on actual outcomes
- Continuously refines strategies

"The best way to become an expert is to practice, not to study."
"""

import logging
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
import statistics

logger = logging.getLogger(__name__)


@dataclass
class PracticeMetrics:
    """Metrics from practicing BCM on the platform"""
    timestamp: str
    metric_type: str
    target_value: Any
    actual_value: Any
    success: bool
    deviation_percentage: float
    context: Dict[str, Any]


@dataclass
class LearningInsight:
    """Insight learned from practice"""
    insight_id: str
    timestamp: str
    category: str
    observation: str
    recommendation: str
    confidence: float
    evidence: List[Dict[str, Any]]


class PracticeLearningEngine:
    """
    Engine for learning through practical application

    The platform learns by:
    1. Applying BCM to itself
    2. Measuring actual outcomes vs targets
    3. Identifying what works and what doesn't
    4. Adjusting strategies based on real data
    5. Repeating the cycle

    This is PRACTICAL learning - learning by DOING.
    """

    def __init__(self):
        self.practice_metrics: List[PracticeMetrics] = []
        self.learning_insights: List[LearningInsight] = []
        self.improvement_history: List[Dict[str, Any]] = []

        logger.info("PracticeLearningEngine initialized")

    async def learn_from_self_application(
        self,
        application_results: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Learn from the platform's self-application of BCM

        Args:
            application_results: Results from SystemBCM.execute_full_cycle()

        Returns:
            Learning results with insights and improvements
        """
        logger.info(" Learning from Self_Application: Analyzing practice results")

        learning_results = {
            "learning_timestamp": datetime.utcnow().isoformat(),
            "input_data": application_results,
            "metrics_analyzed": 0,
            "insights_generated": [],
            "improvements_identified": [],
            "confidence_scores": {}
        }

        # Extract metrics from each phase
        if "phases" in application_results:
            # BIA Phase
            if "bia" in application_results["phases"]:
                bia_insights = await self._learn_from_bia(
                    application_results["phases"]["bia"]["results"]
                )
                learning_results["insights_generated"].extend(bia_insights)
                learning_results["metrics_analyzed"] += 1

            # Risk Assessment Phase
            if "risk_assessment" in application_results["phases"]:
                risk_insights = await self._learn_from_risk_assessment(
                    application_results["phases"]["risk_assessment"]["results"]
                )
                learning_results["insights_generated"].extend(risk_insights)
                learning_results["metrics_analyzed"] += 1

            # Recovery Setup Phase
            if "recovery_setup" in application_results["phases"]:
                recovery_insights = await self._learn_from_recovery_setup(
                    application_results["phases"]["recovery_setup"]["results"]
                )
                learning_results["insights_generated"].extend(recovery_insights)
                learning_results["metrics_analyzed"] += 1

            # Priority Application Phase
            if "priority_application" in application_results["phases"]:
                priority_insights = await self._learn_from_priorities(
                    application_results["phases"]["priority_application"]["results"]
                )
                learning_results["insights_generated"].extend(priority_insights)
                learning_results["metrics_analyzed"] += 1

        # Generate improvements based on insights
        improvements = await self._generate_improvements(
            learning_results["insights_generated"]
        )
        learning_results["improvements_identified"] = improvements

        # Calculate confidence scores
        learning_results["confidence_scores"] = {
            "overall_confidence": self._calculate_overall_confidence(
                learning_results["insights_generated"]
            ),
            "ready_to_apply": len(improvements) > 0
        }

        logger.info(
            f" Learning Complete: "
            f"{learning_results['metrics_analyzed']} phases analyzed, "
            f"{len(learning_results['insights_generated'])} insights, "
            f"{len(improvements)} improvements identified"
        )

        return learning_results

    async def _learn_from_bia(self, bia_results: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Learn insights from BIA execution"""
        insights = []

        # Check if all critical processes have auto-recovery
        critical_without_auto_recovery = [
            p for p in bia_results.get("critical_processes", [])
            if not p.get("auto_recovery_enabled")
        ]

        if critical_without_auto_recovery:
            insights.append({
                "category": "bia_optimization",
                "observation": f"{len(critical_without_auto_recovery)} critical processes lack auto-recovery",
                "recommendation": "Enable auto-recovery for all tier-1 critical processes",
                "confidence": 0.9,
                "evidence": critical_without_auto_recovery
            })
            logger.info(f"   Insight: {len(critical_without_auto_recovery)} processes need auto-recovery")

        # Check for circular dependencies
        dependencies = bia_results.get("dependencies_identified", [])
        if dependencies:
            # Simple check for potential circular dependencies
            services = set()
            for dep in dependencies:
                from_svc = dep.get("from_service")
                to_svcs = dep.get("to_services", [])
                if from_svc in to_svcs:
                    insights.append({
                        "category": "architecture_risk",
                        "observation": f"Potential circular dependency: {from_svc}",
                        "recommendation": "Review and break circular dependencies",
                        "confidence": 0.7,
                        "evidence": [dep]
                    })

        # Check RTO/RPO alignment
        rto_targets = []
        for process in bia_results.get("critical_processes", []):
            rto = process.get("rto", "")
            if rto:
                # Simple RTO parsing (assumes format like "30s", "1m", "5m")
                if 's' in rto:
                    seconds = int(rto.replace('s', ''))
                elif 'm' in rto:
                    seconds = int(rto.replace('m', '')) * 60
                else:
                    seconds = 300  # default 5 minutes

                rto_targets.append(seconds)

        if rto_targets:
            avg_rto = statistics.mean(rto_targets)
            if avg_rto > 300:  # >5 minutes average
                insights.append({
                    "category": "performance_target",
                    "observation": f"Average RTO is {avg_rto:.0f}s - relatively high",
                    "recommendation": "Consider optimizing recovery procedures to reduce RTO",
                    "confidence": 0.6,
                    "evidence": {"average_rto_seconds": avg_rto}
                })

        return insights

    async def _learn_from_risk_assessment(self, risk_results: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Learn insights from risk assessment"""
        insights = []

        # Check high-priority risks
        high_risks = risk_results.get("high_priority_risks", [])
        if high_risks:
            for risk in high_risks:
                if risk.get("residual_risk") in ["high", "medium-high"]:
                    insights.append({
                        "category": "unmitigated_risk",
                        "observation": f"High risk with high residual: {risk['name']}",
                        "recommendation": f"Implement additional controls for: {risk['name']}",
                        "confidence": 0.85,
                        "evidence": risk
                    })
                    logger.warning(f"  ️  Unmitigated high risk: {risk['name']}")

        # Check mitigation coverage
        mitigations = risk_results.get("mitigations_to_implement", [])
        preventive_count = sum(1 for m in mitigations if m.get("type") == "preventive")
        detective_count = sum(1 for m in mitigations if m.get("type") == "detective")
        corrective_count = sum(1 for m in mitigations if m.get("type") == "corrective")

        total_mitigations = len(mitigations)
        if total_mitigations > 0:
            preventive_ratio = preventive_count / total_mitigations

            if preventive_ratio < 0.3:  # Less than 30% preventive
                insights.append({
                    "category": "mitigation_strategy",
                    "observation": f"Only {preventive_ratio:.1%} of mitigations are preventive",
                    "recommendation": "Focus more on preventive controls to reduce risk occurrence",
                    "confidence": 0.75,
                    "evidence": {
                        "preventive": preventive_count,
                        "detective": detective_count,
                        "corrective": corrective_count
                    }
                })

        return insights

    async def _learn_from_recovery_setup(self, recovery_results: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Learn insights from recovery setup"""
        insights = []

        # Check automation coverage
        total_procedures = len(recovery_results.get("procedures_configured", []))
        auto_enabled = len(recovery_results.get("auto_recovery_enabled", []))
        manual_required = len(recovery_results.get("manual_approval_required", []))

        if total_procedures > 0:
            automation_ratio = auto_enabled / total_procedures

            if automation_ratio < 0.7:  # Less than 70% automated
                insights.append({
                    "category": "automation_gap",
                    "observation": f"Only {automation_ratio:.1%} of procedures are automated",
                    "recommendation": "Increase automation coverage for faster recovery",
                    "confidence": 0.8,
                    "evidence": {
                        "total": total_procedures,
                        "automated": auto_enabled,
                        "manual": manual_required
                    }
                })
                logger.info(f"   Automation gap: {automation_ratio:.1%} coverage")

        return insights

    async def _learn_from_priorities(self, priority_results: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Learn insights from resource priority application"""
        insights = []

        # Check tier distribution
        tiers = priority_results.get("tiers_configured", [])
        services = priority_results.get("services_prioritized", [])

        if services:
            tier_1_count = sum(1 for s in services if "tier_1" in s.get("tier", ""))
            tier_2_count = sum(1 for s in services if "tier_2" in s.get("tier", ""))
            tier_3_count = sum(1 for s in services if "tier_3" in s.get("tier", ""))

            total = len(services)
            tier_1_ratio = tier_1_count / total

            if tier_1_ratio > 0.6:  # More than 60% in tier 1
                insights.append({
                    "category": "resource_allocation",
                    "observation": f"{tier_1_ratio:.1%} of services are tier-1 critical",
                    "recommendation": "Review if all tier-1 services are truly critical",
                    "confidence": 0.65,
                    "evidence": {
                        "tier_1": tier_1_count,
                        "tier_2": tier_2_count,
                        "tier_3": tier_3_count
                    }
                })

            if tier_3_count == 0:
                insights.append({
                    "category": "resource_allocation",
                    "observation": "No tier-3 optional services defined",
                    "recommendation": "Identify optional services that can be paused under load",
                    "confidence": 0.7,
                    "evidence": {"tier_distribution": [tier_1_count, tier_2_count, tier_3_count]}
                })

        return insights

    async def _generate_improvements(self, insights: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Generate actionable improvements from insights"""
        improvements = []

        for idx, insight in enumerate(insights):
            # Only generate improvements for high-confidence insights
            if insight.get("confidence", 0) >= 0.7:
                improvement = {
                    "improvement_id": f"imp_{datetime.utcnow().timestamp()}_{idx}",
                    "category": insight["category"],
                    "description": insight["recommendation"],
                    "priority": self._calculate_improvement_priority(insight),
                    "confidence": insight["confidence"],
                    "estimated_impact": self._estimate_impact(insight),
                    "source_insight": insight["observation"]
                }
                improvements.append(improvement)

                logger.info(
                    f"   Improvement: {improvement['description']} "
                    f"(priority={improvement['priority']}, impact={improvement['estimated_impact']})"
                )

        return improvements

    def _calculate_improvement_priority(self, insight: Dict[str, Any]) -> str:
        """Calculate priority for improvement"""
        category = insight.get("category", "")
        confidence = insight.get("confidence", 0)

        # Critical categories
        if category in ["unmitigated_risk", "architecture_risk"]:
            return "critical"
        # High confidence improvements
        elif confidence >= 0.85:
            return "high"
        # Medium confidence or optimization
        elif confidence >= 0.7:
            return "medium"
        else:
            return "low"

    def _estimate_impact(self, insight: Dict[str, Any]) -> str:
        """Estimate impact of implementing improvement"""
        category = insight.get("category", "")

        impact_map = {
            "unmitigated_risk": "high",
            "architecture_risk": "high",
            "automation_gap": "medium-high",
            "bia_optimization": "medium",
            "mitigation_strategy": "medium",
            "resource_allocation": "low-medium",
            "performance_target": "low"
        }

        return impact_map.get(category, "low")

    def _calculate_overall_confidence(self, insights: List[Dict[str, Any]]) -> float:
        """Calculate overall confidence in learning results"""
        if not insights:
            return 0.0

        confidences = [i.get("confidence", 0) for i in insights]
        return statistics.mean(confidences)

    async def measure_effectiveness(
        self,
        metric_type: str,
        target_value: Any,
        actual_value: Any,
        context: Optional[Dict[str, Any]] = None
    ) -> PracticeMetrics:
        """
        Measure effectiveness of applied BCM practices

        Args:
            metric_type: Type of metric (e.g., "rto", "availability", "recovery_success_rate")
            target_value: Expected/target value
            actual_value: Actual measured value
            context: Additional context

        Returns:
            PracticeMetrics with measurement results
        """
        logger.info(f" Measuring {metric_type}: target={target_value}, actual={actual_value}")

        # Calculate deviation
        try:
            if isinstance(target_value, (int, float)) and isinstance(actual_value, (int, float)):
                deviation = ((actual_value - target_value) / target_value) * 100
                success = abs(deviation) <= 20  # Within 20% tolerance
            else:
                deviation = 0.0
                success = str(target_value) == str(actual_value)
        except:
            deviation = 0.0
            success = False

        metrics = PracticeMetrics(
            timestamp=datetime.utcnow().isoformat(),
            metric_type=metric_type,
            target_value=target_value,
            actual_value=actual_value,
            success=success,
            deviation_percentage=deviation,
            context=context or {}
        )

        self.practice_metrics.append(metrics)

        status = "" if success else ""
        logger.info(
            f"  {status} {metric_type}: "
            f"{'SUCCESS' if success else 'DEVIATION'} "
            f"(deviation={deviation:.1f}%)"
        )

        return metrics

    async def improve_based_on_practice(
        self,
        improvements: List[Dict[str, Any]],
        apply_immediately: bool = False
    ) -> Dict[str, Any]:
        """
        Improve platform based on practice learnings

        Args:
            improvements: List of improvements to apply
            apply_immediately: Whether to apply immediately or queue for approval

        Returns:
            Improvement application results
        """
        logger.info(f" Applying {len(improvements)} improvements based on practice")

        results = {
            "timestamp": datetime.utcnow().isoformat(),
            "improvements_count": len(improvements),
            "applied": [],
            "queued": [],
            "failed": []
        }

        for improvement in improvements:
            improvement_id = improvement.get("improvement_id", "unknown")
            priority = improvement.get("priority", "medium")

            try:
                if apply_immediately and priority in ["critical", "high"]:
                    # Apply immediately
                    await self._apply_improvement(improvement)
                    results["applied"].append(improvement_id)
                    logger.info(f"   Applied: {improvement['description']}")
                else:
                    # Queue for review
                    results["queued"].append(improvement_id)
                    logger.info(f"   Queued: {improvement['description']}")

                # Record in history
                self.improvement_history.append({
                    "timestamp": datetime.utcnow().isoformat(),
                    "improvement": improvement,
                    "status": "applied" if improvement_id in results["applied"] else "queued"
                })

            except Exception as e:
                logger.error(f"   Failed to apply {improvement_id}: {e}")
                results["failed"].append({
                    "improvement_id": improvement_id,
                    "error": str(e)
                })

        logger.info(
            f" Improvements processed: "
            f"{len(results['applied'])} applied, "
            f"{len(results['queued'])} queued, "
            f"{len(results['failed'])} failed"
        )

        return results

    async def _apply_improvement(self, improvement: Dict[str, Any]):
        """
        Apply a specific improvement

        In production, this would:
        - Update configuration
        - Adjust resource limits
        - Enable/disable features
        - Update monitoring rules
        """
        # Simulate application
        import asyncio
        await asyncio.sleep(0.1)

        logger.debug(f"Applied improvement: {improvement.get('improvement_id')}")

    def get_learning_summary(self) -> Dict[str, Any]:
        """Get summary of learning from practice"""
        return {
            "total_metrics_collected": len(self.practice_metrics),
            "total_insights_generated": len(self.learning_insights),
            "total_improvements_made": len(self.improvement_history),
            "recent_metrics": [asdict(m) for m in self.practice_metrics[-10:]],
            "recent_insights": self.learning_insights[-10:],
            "recent_improvements": self.improvement_history[-10:]
        }


# CLI entry point for testing
if __name__ == "__main__":
    import sys
    import json
    import asyncio

    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )

    async def main():
        engine = PracticeLearningEngine()

        # Example: Learn from BIA execution
        sample_bia_results = {
            "target": "AI-Platform-ISO",
            "phases": {
                "bia": {
                    "results": {
                        "critical_processes": [
                            {
                                "process_id": "cp_001",
                                "name": "Event Bus",
                                "criticality": "tier_1_critical",
                                "rto": "30s",
                                "rpo": "0s",
                                "auto_recovery_enabled": True
                            },
                            {
                                "process_id": "cp_002",
                                "name": "API Gateway",
                                "criticality": "tier_1_critical",
                                "rto": "1m",
                                "rpo": "0s",
                                "auto_recovery_enabled": False
                            }
                        ],
                        "dependencies_identified": [],
                        "recovery_targets_set": []
                    }
                }
            }
        }

        results = await engine.learn_from_self_application(sample_bia_results)
        print(json.dumps(results, indent=2))

    asyncio.run(main())
