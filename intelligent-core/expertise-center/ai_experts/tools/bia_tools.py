"""
BIA (Business Impact Analysis) Tools

Tools for analyzing business processes, dependencies, and impacts.
Used by BCM Advisor expert.
"""

from typing import Dict, Any, List
from .base_tool import BaseTool
import logging

logger = logging.getLogger(__name__)


class BIAAnalysisTool(BaseTool):
    """
    Business Impact Analysis Tool

    Analyzes business processes to determine:
    - Criticality levels
    - Recovery time objectives (RTO)
    - Recovery point objectives (RPO)
    - Impact over time
    """

    def __init__(self, db_session=None):
        super().__init__(
            name="bia_analysis",
            description="Analyze business process criticality, RTO/RPO requirements, and impact over time",
            parameters={
                "process_name": {
                    "type": "string",
                    "description": "Name of the business process to analyze"
                },
                "industry": {
                    "type": "string",
                    "description": "Industry context (e.g., healthcare, finance, manufacturing)"
                },
                "annual_revenue": {
                    "type": "number",
                    "description": "Annual revenue of the organization (optional)",
                },
                "process_description": {
                    "type": "string",
                    "description": "Brief description of what the process does"
                }
            },
            required_params=["process_name", "industry", "process_description"]
        )
        self.db_session = db_session

    async def execute(
        self,
        process_name: str,
        industry: str,
        process_description: str,
        annual_revenue: float = None
    ) -> Dict[str, Any]:
        """
        Execute BIA analysis

        Returns:
            Analysis results with criticality, RTO/RPO, and impact assessment
        """

        # Industry-specific criticality assessment
        criticality_matrix = {
            "healthcare": {
                "patient_care": "critical",
                "billing": "important",
                "administrative": "normal"
            },
            "finance": {
                "trading": "critical",
                "customer_service": "important",
                "reporting": "normal"
            },
            "manufacturing": {
                "production": "critical",
                "inventory": "important",
                "planning": "normal"
            }
        }

        # Determine criticality (simplified logic)
        criticality = "important"  # default
        if industry.lower() in criticality_matrix:
            for key, value in criticality_matrix[industry.lower()].items():
                if key in process_name.lower() or key in process_description.lower():
                    criticality = value
                    break

        # RTO/RPO based on criticality
        rto_rpo_mapping = {
            "critical": {"rto": "4 hours", "rpo": "1 hour"},
            "important": {"rto": "24 hours", "rpo": "8 hours"},
            "normal": {"rto": "72 hours", "rpo": "24 hours"}
        }

        recovery_objectives = rto_rpo_mapping.get(criticality, rto_rpo_mapping["important"])

        # Impact over time analysis
        impact_timeline = self._calculate_impact_timeline(
            criticality=criticality,
            annual_revenue=annual_revenue
        )

        result = {
            "process_name": process_name,
            "industry": industry,
            "criticality_level": criticality,
            "recovery_objectives": recovery_objectives,
            "impact_timeline": impact_timeline,
            "recommendations": self._generate_recommendations(criticality, industry)
        }

        # Publish event
        await self._publish_event('bia.analysis.completed', result)

        return result

    def _calculate_impact_timeline(
        self,
        criticality: str,
        annual_revenue: float = None
    ) -> List[Dict[str, Any]]:
        """Calculate financial/operational impact over time"""

        if annual_revenue:
            daily_revenue = annual_revenue / 365
        else:
            daily_revenue = 0

        # Impact multipliers based on criticality
        multipliers = {
            "critical": [0.1, 0.3, 0.6, 1.0, 1.5],  # 1h, 4h, 24h, 72h, 1week
            "important": [0.05, 0.1, 0.3, 0.6, 1.0],
            "normal": [0.01, 0.05, 0.1, 0.3, 0.5]
        }

        timeline_points = ["1 hour", "4 hours", "24 hours", "72 hours", "1 week"]
        multiplier_values = multipliers.get(criticality, multipliers["important"])

        impact_timeline = []
        for time_point, multiplier in zip(timeline_points, multiplier_values):
            financial_impact = daily_revenue * multiplier if annual_revenue else 0

            impact_timeline.append({
                "time_point": time_point,
                "operational_impact": self._get_operational_impact(multiplier),
                "financial_impact_usd": round(financial_impact, 2) if financial_impact else None,
                "severity": "high" if multiplier >= 0.6 else "medium" if multiplier >= 0.3 else "low"
            })

        return impact_timeline

    def _get_operational_impact(self, multiplier: float) -> str:
        """Describe operational impact"""
        if multiplier >= 1.0:
            return "Severe disruption to operations, customer impact, regulatory concerns"
        elif multiplier >= 0.6:
            return "Major disruption, significant customer impact"
        elif multiplier >= 0.3:
            return "Moderate disruption, some customer impact"
        else:
            return "Minor disruption, minimal customer impact"

    def _generate_recommendations(self, criticality: str, industry: str) -> List[str]:
        """Generate BIA recommendations"""

        recommendations = []

        if criticality == "critical":
            recommendations.extend([
                "Implement redundant systems and failover capabilities",
                "Establish 24/7 monitoring and incident response",
                "Create detailed recovery procedures with clear owners",
                "Conduct quarterly BC exercises for this process"
            ])
        elif criticality == "important":
            recommendations.extend([
                "Document recovery procedures with designated backups",
                "Establish monitoring during business hours",
                "Conduct semi-annual BC drills",
                "Identify alternate manual processes"
            ])
        else:
            recommendations.extend([
                "Document basic recovery steps",
                "Identify dependencies and workarounds",
                "Include in annual BC testing"
            ])

        # Industry-specific recommendations
        if industry.lower() == "healthcare":
            recommendations.append("Ensure patient safety protocols during outage")
        elif industry.lower() == "finance":
            recommendations.append("Maintain regulatory compliance during disruption")

        return recommendations


class DependencyMapperTool(BaseTool):
    """
    Dependency Mapping Tool

    Maps dependencies for business processes:
    - Upstream dependencies (what this process relies on)
    - Downstream dependencies (what relies on this process)
    - Critical dependencies
    """

    def __init__(self, db_session=None):
        super().__init__(
            name="dependency_mapper",
            description="Map upstream and downstream dependencies for a business process",
            parameters={
                "process_name": {
                    "type": "string",
                    "description": "Name of the process to map dependencies for"
                },
                "process_type": {
                    "type": "string",
                    "description": "Type of process (e.g., 'core', 'support', 'management')"
                },
                "known_dependencies": {
                    "type": "array",
                    "description": "List of known dependencies (optional)",
                    "items": {"type": "string"}
                }
            },
            required_params=["process_name", "process_type"]
        )
        self.db_session = db_session

    async def execute(
        self,
        process_name: str,
        process_type: str,
        known_dependencies: List[str] = None
    ) -> Dict[str, Any]:
        """
        Execute dependency mapping

        Returns:
            Dependency map with upstream/downstream/critical dependencies
        """

        # Common dependency patterns by process type
        dependency_patterns = {
            "core": {
                "upstream": ["IT Infrastructure", "Data Systems", "Staff", "Facilities"],
                "downstream": ["Customer Service", "Reporting", "Billing"]
            },
            "support": {
                "upstream": ["IT Infrastructure", "Vendor Services"],
                "downstream": ["Core Processes", "Management Processes"]
            },
            "management": {
                "upstream": ["Data Systems", "Reporting Tools"],
                "downstream": ["Decision Making", "Strategic Planning"]
            }
        }

        pattern = dependency_patterns.get(process_type.lower(), dependency_patterns["support"])

        # Build dependency map
        upstream = pattern["upstream"].copy()
        downstream = pattern["downstream"].copy()

        # Add known dependencies
        if known_dependencies:
            upstream.extend([d for d in known_dependencies if d not in upstream])

        # Identify critical dependencies
        critical_dependencies = self._identify_critical_dependencies(upstream, downstream)

        result = {
            "process_name": process_name,
            "process_type": process_type,
            "upstream_dependencies": upstream,
            "downstream_dependencies": downstream,
            "critical_dependencies": critical_dependencies,
            "dependency_analysis": self._analyze_dependencies(upstream, downstream)
        }

        await self._publish_event('dependency.mapping.completed', result)

        return result

    def _identify_critical_dependencies(
        self,
        upstream: List[str],
        downstream: List[str]
    ) -> List[Dict[str, str]]:
        """Identify critical dependencies"""

        critical = []
        critical_keywords = ["IT Infrastructure", "Data Systems", "Staff", "Facilities"]

        for dep in upstream:
            if any(keyword in dep for keyword in critical_keywords):
                critical.append({
                    "dependency": dep,
                    "type": "upstream",
                    "reason": "Essential for process operation"
                })

        return critical

    def _analyze_dependencies(self, upstream: List[str], downstream: List[str]) -> str:
        """Analyze dependency complexity"""

        total_deps = len(upstream) + len(downstream)

        if total_deps > 10:
            return "High complexity: Many dependencies require coordinated recovery planning"
        elif total_deps > 5:
            return "Medium complexity: Moderate dependency management needed"
        else:
            return "Low complexity: Straightforward dependency structure"


class ImpactCalculatorTool(BaseTool):
    """
    Impact Calculator Tool

    Calculates various types of impact:
    - Financial impact
    - Operational impact
    - Reputational impact
    - Regulatory impact
    """

    def __init__(self, db_session=None):
        super().__init__(
            name="impact_calculator",
            description="Calculate financial, operational, reputational, and regulatory impact of process disruption",
            parameters={
                "process_name": {
                    "type": "string",
                    "description": "Name of the disrupted process"
                },
                "outage_duration_hours": {
                    "type": "number",
                    "description": "Expected outage duration in hours"
                },
                "annual_revenue": {
                    "type": "number",
                    "description": "Annual revenue (optional)"
                },
                "customer_facing": {
                    "type": "boolean",
                    "description": "Whether the process is customer-facing"
                },
                "regulated": {
                    "type": "boolean",
                    "description": "Whether the process is subject to regulatory requirements"
                }
            },
            required_params=["process_name", "outage_duration_hours"]
        )
        self.db_session = db_session

    async def execute(
        self,
        process_name: str,
        outage_duration_hours: float,
        annual_revenue: float = None,
        customer_facing: bool = False,
        regulated: bool = False
    ) -> Dict[str, Any]:
        """
        Calculate comprehensive impact

        Returns:
            Multi-dimensional impact assessment
        """

        # Financial impact
        financial_impact = self._calculate_financial_impact(
            outage_duration_hours,
            annual_revenue
        )

        # Operational impact
        operational_impact = self._calculate_operational_impact(
            outage_duration_hours,
            customer_facing
        )

        # Reputational impact
        reputational_impact = self._calculate_reputational_impact(
            outage_duration_hours,
            customer_facing
        )

        # Regulatory impact
        regulatory_impact = self._calculate_regulatory_impact(
            outage_duration_hours,
            regulated
        )

        # Overall severity
        severity = self._calculate_overall_severity(
            financial_impact,
            operational_impact,
            reputational_impact,
            regulatory_impact
        )

        result = {
            "process_name": process_name,
            "outage_duration_hours": outage_duration_hours,
            "financial_impact": financial_impact,
            "operational_impact": operational_impact,
            "reputational_impact": reputational_impact,
            "regulatory_impact": regulatory_impact,
            "overall_severity": severity,
            "mitigation_priority": self._get_mitigation_priority(severity)
        }

        await self._publish_event('impact.calculation.completed', result)

        return result

    def _calculate_financial_impact(
        self,
        hours: float,
        annual_revenue: float = None
    ) -> Dict[str, Any]:
        """Calculate financial impact"""

        if annual_revenue:
            hourly_revenue = annual_revenue / (365 * 24)
            direct_loss = hourly_revenue * hours

            # Recovery costs (estimated at 20% of direct loss)
            recovery_cost = direct_loss * 0.2

            return {
                "direct_revenue_loss_usd": round(direct_loss, 2),
                "recovery_costs_usd": round(recovery_cost, 2),
                "total_financial_impact_usd": round(direct_loss + recovery_cost, 2),
                "severity": "high" if direct_loss > 100000 else "medium" if direct_loss > 10000 else "low"
            }
        else:
            return {
                "direct_revenue_loss_usd": None,
                "recovery_costs_usd": None,
                "total_financial_impact_usd": None,
                "severity": "unknown"
            }

    def _calculate_operational_impact(
        self,
        hours: float,
        customer_facing: bool
    ) -> Dict[str, Any]:
        """Calculate operational impact"""

        if hours >= 72:
            severity = "critical"
            description = "Severe operational disruption, widespread impact"
        elif hours >= 24:
            severity = "high"
            description = "Major operational disruption, significant impact"
        elif hours >= 4:
            severity = "medium"
            description = "Moderate operational disruption"
        else:
            severity = "low"
            description = "Minor operational disruption"

        if customer_facing:
            severity = "critical" if severity in ["critical", "high"] else "high"
            description += ", direct customer impact"

        return {
            "severity": severity,
            "description": description,
            "estimated_staff_affected": self._estimate_staff_affected(hours)
        }

    def _calculate_reputational_impact(
        self,
        hours: float,
        customer_facing: bool
    ) -> Dict[str, Any]:
        """Calculate reputational impact"""

        if not customer_facing:
            return {
                "severity": "low",
                "description": "Minimal reputational impact (internal process)",
                "recovery_time_days": 0
            }

        if hours >= 24:
            severity = "high"
            description = "Significant reputational damage, media attention likely"
            recovery_days = 30
        elif hours >= 4:
            severity = "medium"
            description = "Moderate reputational impact, customer complaints expected"
            recovery_days = 14
        else:
            severity = "low"
            description = "Minor reputational impact, limited customer awareness"
            recovery_days = 7

        return {
            "severity": severity,
            "description": description,
            "recovery_time_days": recovery_days
        }

    def _calculate_regulatory_impact(
        self,
        hours: float,
        regulated: bool
    ) -> Dict[str, Any]:
        """Calculate regulatory impact"""

        if not regulated:
            return {
                "severity": "none",
                "description": "No regulatory requirements",
                "reporting_required": False
            }

        if hours >= 24:
            severity = "high"
            description = "Regulatory reporting required, potential fines"
            reporting = True
        elif hours >= 4:
            severity = "medium"
            description = "May require regulatory notification"
            reporting = True
        else:
            severity = "low"
            description = "Below regulatory reporting threshold"
            reporting = False

        return {
            "severity": severity,
            "description": description,
            "reporting_required": reporting
        }

    def _calculate_overall_severity(
        self,
        financial: Dict,
        operational: Dict,
        reputational: Dict,
        regulatory: Dict
    ) -> str:
        """Calculate overall severity"""

        severity_scores = {
            "critical": 4,
            "high": 3,
            "medium": 2,
            "low": 1,
            "none": 0,
            "unknown": 0
        }

        scores = [
            severity_scores.get(financial.get("severity", "unknown"), 0),
            severity_scores.get(operational.get("severity", "unknown"), 0),
            severity_scores.get(reputational.get("severity", "unknown"), 0),
            severity_scores.get(regulatory.get("severity", "unknown"), 0)
        ]

        avg_score = sum(scores) / len(scores)

        if avg_score >= 3.5:
            return "critical"
        elif avg_score >= 2.5:
            return "high"
        elif avg_score >= 1.5:
            return "medium"
        else:
            return "low"

    def _get_mitigation_priority(self, severity: str) -> str:
        """Get mitigation priority"""

        priorities = {
            "critical": "P1 - Immediate action required",
            "high": "P2 - Action required within 24 hours",
            "medium": "P3 - Action required within 1 week",
            "low": "P4 - Address in normal planning cycle"
        }

        return priorities.get(severity, "P3 - Action required within 1 week")

    def _estimate_staff_affected(self, hours: float) -> str:
        """Estimate staff affected"""

        if hours >= 72:
            return "100+ staff"
        elif hours >= 24:
            return "50-100 staff"
        elif hours >= 4:
            return "10-50 staff"
        else:
            return "<10 staff"
