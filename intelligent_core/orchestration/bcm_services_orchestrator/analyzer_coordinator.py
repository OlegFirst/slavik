"""
Analyzer Coordinator
===================

Routes analysis requests to appropriate BCM Analyzers (formerly "Organs").

Analyzers are stateless, AI-powered analytical engines:
- Compliance Analyzer (ISO 22301 gap analysis)
- Risk Analyzer (FAIR-based risk quantification)
- Impact Analyzer (BIA impact assessment)
- Governance Analyzer (policy adherence)
- Emergency Analyzer (crisis response)
- Performance Analyzer (metrics analysis)
- Learning Analyzer (pattern extraction)
- Lifecycle Analyzer (BCM maturity)
- Plan Analyzer (recovery plan quality)
- Scenario Analyzer (exercise design)

Based on ColleagueCoordinator pattern but adapted for stateless analyzers.
"""

import logging
from typing import Dict, Any, Optional, List
from enum import Enum
from datetime import datetime

logger = logging.getLogger(__name__)


class AnalyzerType(str, Enum):
    """Types of BCM Analyzers"""
    COMPLIANCE = "compliance_analyzer"
    RISK = "risk_analyzer"
    IMPACT = "impact_analyzer"
    GOVERNANCE = "governance_analyzer"
    EMERGENCY = "emergency_analyzer"
    PERFORMANCE = "performance_analyzer"
    LEARNING = "learning_analyzer"
    LIFECYCLE = "lifecycle_analyzer"
    PLAN = "plan_analyzer"
    SCENARIO = "scenario_analyzer"
    AUTO = "auto"  # Auto-detect best analyzer


class AnalyzerCoordinator:
    """
    Coordinates analysis requests between BCM Analyzers.

    Features:
    - Auto-routing based on analysis type detection
    - Batch analysis (multiple analyzers in sequence)
    - EventBus integration for audit trail
    - Caching for repeated analyses

    Example:
        ```python
        coordinator = AnalyzerCoordinator(analyzers)
        result = await coordinator.route_analysis(
            analysis_type=AnalyzerType.AUTO,
            input_data={
                'type': 'compliance_gap',
                'standard': 'ISO_22301',
                'current_controls': {...}
            },
            tenant_id='org-123'
        )
        ```
    """

    def __init__(self, analyzers: Dict[str, Any], event_bus=None):
        """
        Initialize analyzer coordinator.

        Args:
            analyzers: Dictionary of initialized analyzer instances
            event_bus: Optional EventBus for audit trail
        """
        self.analyzers = analyzers
        self.event_bus = event_bus
        self.routing_stats = {
            "total_analyses": 0,
            "auto_routed": 0,
            "manual_routed": 0,
            "batch_analyses": 0,
            "routing_accuracy": {}
        }

        # Input type to Analyzer mapping
        self.type_to_analyzer = {
            # Compliance & Standards
            "compliance_gap": AnalyzerType.COMPLIANCE,
            "iso_audit": AnalyzerType.COMPLIANCE,
            "standard_check": AnalyzerType.COMPLIANCE,
            "gap_analysis": AnalyzerType.COMPLIANCE,

            # Risk Management
            "risk_assessment": AnalyzerType.RISK,
            "threat_analysis": AnalyzerType.RISK,
            "vulnerability_scan": AnalyzerType.RISK,
            "fair_analysis": AnalyzerType.RISK,

            # Business Impact Analysis
            "impact_assessment": AnalyzerType.IMPACT,
            "bia_analysis": AnalyzerType.IMPACT,
            "criticality_scoring": AnalyzerType.IMPACT,
            "dependency_mapping": AnalyzerType.IMPACT,

            # Governance
            "policy_check": AnalyzerType.GOVERNANCE,
            "control_effectiveness": AnalyzerType.GOVERNANCE,
            "governance_review": AnalyzerType.GOVERNANCE,

            # Emergency Response
            "crisis_analysis": AnalyzerType.EMERGENCY,
            "incident_severity": AnalyzerType.EMERGENCY,
            "emergency_response": AnalyzerType.EMERGENCY,

            # Performance & Metrics
            "kpi_analysis": AnalyzerType.PERFORMANCE,
            "metrics_review": AnalyzerType.PERFORMANCE,
            "trend_analysis": AnalyzerType.PERFORMANCE,

            # Learning & Patterns
            "pattern_extraction": AnalyzerType.LEARNING,
            "lessons_learned": AnalyzerType.LEARNING,
            "cross_module_learning": AnalyzerType.LEARNING,

            # Lifecycle & Maturity
            "maturity_assessment": AnalyzerType.LIFECYCLE,
            "lifecycle_stage": AnalyzerType.LIFECYCLE,

            # Plans & Recovery
            "plan_quality": AnalyzerType.PLAN,
            "recovery_strategy": AnalyzerType.PLAN,

            # Scenarios & Exercises
            "scenario_design": AnalyzerType.SCENARIO,
            "exercise_planning": AnalyzerType.SCENARIO,
        }

        logger.info(f"AnalyzerCoordinator initialized with {len(analyzers)} analyzers")

    async def route_analysis(
        self,
        analysis_type: AnalyzerType = AnalyzerType.AUTO,
        input_data: Dict[str, Any] = None,
        tenant_id: str = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Route analysis request to appropriate analyzer.

        Args:
            analysis_type: Specific analyzer or AUTO for auto-routing
            input_data: Analysis input data
            tenant_id: Tenant identifier
            metadata: Optional metadata

        Returns:
            Analysis result with insights, recommendations, confidence
        """
        self.routing_stats["total_analyses"] += 1
        start_time = datetime.utcnow()

        try:
            # Step 1: Determine which analyzer to use
            if analysis_type == AnalyzerType.AUTO:
                analysis_type, routing_confidence = self._auto_route(input_data)
                self.routing_stats["auto_routed"] += 1
                logger.info(f"Auto-routed to {analysis_type.value} (confidence: {routing_confidence:.2f})")
            else:
                self.routing_stats["manual_routed"] += 1
                routing_confidence = 1.0
                logger.info(f"Manual routing to {analysis_type.value}")

            # Step 2: Get the analyzer
            analyzer = self.analyzers.get(analysis_type.value)
            if not analyzer:
                raise ValueError(f"Analyzer {analysis_type.value} not available")

            # Step 3: Execute analysis
            result = await analyzer.analyze(
                input_data=input_data,
                tenant_id=tenant_id,
                metadata=metadata
            )

            # Step 4: Publish audit event
            if self.event_bus:
                await self._publish_analysis_event(
                    analyzer_type=analysis_type,
                    input_data=input_data,
                    result=result,
                    tenant_id=tenant_id
                )

            # Update routing stats
            if analysis_type.value not in self.routing_stats["routing_accuracy"]:
                self.routing_stats["routing_accuracy"][analysis_type.value] = {
                    "count": 0,
                    "avg_confidence": 0.0,
                    "avg_duration_ms": 0.0
                }

            stats = self.routing_stats["routing_accuracy"][analysis_type.value]
            stats["count"] += 1

            duration_ms = (datetime.utcnow() - start_time).total_seconds() * 1000
            stats["avg_duration_ms"] = (
                (stats["avg_duration_ms"] * (stats["count"] - 1) + duration_ms) / stats["count"]
            )

            confidence = result.get("confidence", 0.0)
            stats["avg_confidence"] = (
                (stats["avg_confidence"] * (stats["count"] - 1) + confidence) / stats["count"]
            )

            return {
                "success": True,
                "analyzer": analysis_type.value,
                "routing_confidence": routing_confidence,
                "duration_ms": duration_ms,
                **result  # includes: insights, recommendations, confidence, metadata
            }

        except Exception as e:
            logger.error(f"Error routing analysis: {str(e)}", exc_info=True)
            return {
                "success": False,
                "error": str(e),
                "analyzer": None
            }

    def _auto_route(
        self,
        input_data: Dict[str, Any]
    ) -> tuple[AnalyzerType, float]:
        """
        Automatically determine best analyzer for input data.

        Args:
            input_data: Analysis input data

        Returns:
            (AnalyzerType, confidence_score)
        """
        # Check explicit 'type' field
        data_type = input_data.get("type", "").lower()
        if data_type in self.type_to_analyzer:
            return self.type_to_analyzer[data_type], 1.0

        # Keyword-based routing
        input_str = str(input_data).lower()

        keyword_patterns = {
            AnalyzerType.RISK: ["risk", "threat", "vulnerability", "fair", "lef", "loss"],
            AnalyzerType.IMPACT: ["bia", "impact", "rto", "rpo", "critical", "mtd", "dependency"],
            AnalyzerType.COMPLIANCE: ["iso", "22301", "compliance", "audit", "standard", "clause", "gap"],
            AnalyzerType.EMERGENCY: ["crisis", "incident", "emergency", "ransomware", "breach", "disaster"],
            AnalyzerType.PERFORMANCE: ["kpi", "metric", "performance", "trend", "analytics"],
            AnalyzerType.LEARNING: ["pattern", "lesson", "learning", "cross-module"],
            AnalyzerType.LIFECYCLE: ["maturity", "lifecycle", "stage", "readiness"],
            AnalyzerType.PLAN: ["plan", "recovery", "strategy", "bcp", "drp"],
            AnalyzerType.SCENARIO: ["scenario", "exercise", "drill", "tabletop", "simulation"],
            AnalyzerType.GOVERNANCE: ["policy", "control", "governance", "framework"]
        }

        # Count keyword matches
        max_matches = 0
        best_analyzer = AnalyzerType.COMPLIANCE  # Default

        for analyzer_type, keywords in keyword_patterns.items():
            matches = sum(1 for kw in keywords if kw in input_str)
            if matches > max_matches:
                max_matches = matches
                best_analyzer = analyzer_type

        confidence = min(0.5 + (max_matches * 0.15), 1.0)
        return best_analyzer, confidence

    async def batch_analysis(
        self,
        analyzer_sequence: List[AnalyzerType],
        input_data: Dict[str, Any],
        tenant_id: str = None
    ) -> Dict[str, Any]:
        """
        Execute multiple analyzers in sequence.

        Each analyzer receives output from previous analyzer.

        Args:
            analyzer_sequence: List of analyzers to execute
            input_data: Initial input data
            tenant_id: Tenant identifier

        Returns:
            Batch analysis results

        Example:
            ```python
            # Risk → Impact → Plan analysis pipeline
            result = await coordinator.batch_analysis(
                analyzer_sequence=[
                    AnalyzerType.RISK,
                    AnalyzerType.IMPACT,
                    AnalyzerType.PLAN
                ],
                input_data={'scenario': 'ransomware_attack'},
                tenant_id='org-123'
            )
            ```
        """
        self.routing_stats["batch_analyses"] += 1
        results = []
        current_data = input_data

        logger.info(f"Executing batch analysis: {len(analyzer_sequence)} analyzers")

        for analyzer_type in analyzer_sequence:
            result = await self.route_analysis(
                analysis_type=analyzer_type,
                input_data=current_data,
                tenant_id=tenant_id
            )

            results.append({
                "analyzer": analyzer_type.value,
                "insights": result.get("insights", []),
                "recommendations": result.get("recommendations", []),
                "confidence": result.get("confidence", 0.0)
            })

            # Pass insights to next analyzer
            current_data = {
                **input_data,
                "previous_analysis": result.get("insights", []),
                "previous_recommendations": result.get("recommendations", [])
            }

        return {
            "success": True,
            "batch_type": "sequential",
            "steps": len(analyzer_sequence),
            "results": results
        }

    async def _publish_analysis_event(
        self,
        analyzer_type: AnalyzerType,
        input_data: Dict[str, Any],
        result: Dict[str, Any],
        tenant_id: str
    ):
        """Publish analysis event to EventBus for audit trail."""
        try:
            event_data = {
                "analyzer": analyzer_type.value,
                "input_type": input_data.get("type"),
                "confidence": result.get("confidence"),
                "insights_count": len(result.get("insights", [])),
                "recommendations_count": len(result.get("recommendations", [])),
                "timestamp": datetime.utcnow().isoformat()
            }

            await self.event_bus.publish({
                "type": f"bcm.analyzer.{analyzer_type.value}.completed",
                "data": event_data,
                "tenant_id": tenant_id
            })
        except Exception as e:
            logger.warning(f"Failed to publish analysis event: {e}")

    def get_stats(self) -> Dict[str, Any]:
        """Get coordinator statistics."""
        return {
            "coordinator": "AnalyzerCoordinator",
            "analyzers_available": len(self.analyzers),
            "analyzers": list(self.analyzers.keys()),
            "routing_stats": self.routing_stats,
            "type_mappings": len(self.type_to_analyzer)
        }

    def get_available_analyzers(self) -> List[Dict[str, str]]:
        """Get list of available analyzers."""
        return [
            {
                "type": analyzer_type,
                "name": analyzer.__class__.__name__,
                "description": getattr(analyzer, 'description', 'N/A')
            }
            for analyzer_type, analyzer in self.analyzers.items()
        ]
