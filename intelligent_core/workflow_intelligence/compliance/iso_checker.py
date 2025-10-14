"""
ISO 22301 Compliance Checker

Validates workflow compliance with ISO 22301 requirements
"""

from typing import Dict, Any, List
from dataclasses import dataclass


@dataclass
class ComplianceRequirement:
    """ISO 22301 requirement"""
    requirement_id: str
    description: str
    mandatory: bool = True
    evidence_required: List[str] = None


@dataclass
class ComplianceGap:
    """Gap in compliance"""
    requirement_id: str
    description: str
    current_status: str
    recommendation: str
    severity: str = "medium"  # low, medium, high, critical


class ISO22301Checker:
    """
    ISO 22301 Compliance Checker

    Validates workflows against ISO 22301:2019 requirements
    """

    # ISO 22301 Requirements mapping
    REQUIREMENTS = {
        '8.2.2': [  # BIA
            ComplianceRequirement(
                '8.2.2-1',
                'Identify critical activities and resources',
                mandatory=True,
                evidence_required=['critical_activities_list', 'resource_inventory']
            ),
            ComplianceRequirement(
                '8.2.2-2',
                'Determine impacts over time',
                mandatory=True,
                evidence_required=['impact_analysis', 'rto_rpo_defined']
            ),
            ComplianceRequirement(
                '8.2.2-3',
                'Define recovery priorities',
                mandatory=True,
                evidence_required=['priority_matrix', 'mtpd_defined']
            ),
        ],
        '8.3': [  # Planning
            ComplianceRequirement(
                '8.3-1',
                'Establish objectives for BCMS',
                mandatory=True,
                evidence_required=['objectives_documented', 'measurable_targets']
            ),
            ComplianceRequirement(
                '8.3-2',
                'Plan actions to achieve objectives',
                mandatory=True,
                evidence_required=['action_plan', 'responsibilities_assigned']
            ),
        ],
        '8.4': [  # Plans
            ComplianceRequirement(
                '8.4-1',
                'Establish incident response procedures',
                mandatory=True,
                evidence_required=['response_procedures', 'contact_lists']
            ),
            ComplianceRequirement(
                '8.4-2',
                'Document recovery strategies',
                mandatory=True,
                evidence_required=['recovery_strategies', 'workarounds']
            ),
        ],
    }

    async def check_compliance(
        self,
        workflow_context: Dict[str, Any],
        iso_clause: str
    ) -> Dict[str, Any]:
        """
        Check workflow compliance with ISO clause

        Args:
            workflow_context: Current workflow context
            iso_clause: ISO clause to check (e.g., "8.2.2")

        Returns:
            {
                "compliant": bool,
                "compliance_percentage": float,
                "gaps": [ComplianceGap, ...],
                "recommendations": [...]
            }
        """

        requirements = self.REQUIREMENTS.get(iso_clause, [])

        if not requirements:
            return {
                "compliant": True,
                "compliance_percentage": 100.0,
                "gaps": [],
                "recommendations": [],
                "note": f"No requirements defined for clause {iso_clause}"
            }

        gaps = []

        for req in requirements:
            # Check if requirement is met
            is_met = self._check_requirement(workflow_context, req)

            if not is_met:
                gaps.append(ComplianceGap(
                    requirement_id=req.requirement_id,
                    description=req.description,
                    current_status="not_met",
                    recommendation=f"Complete: {req.description}",
                    severity="high" if req.mandatory else "medium"
                ))

        total_requirements = len(requirements)
        met_requirements = total_requirements - len(gaps)
        compliance_percentage = (met_requirements / total_requirements * 100) if total_requirements > 0 else 100

        return {
            "iso_clause": iso_clause,
            "compliant": len(gaps) == 0,
            "compliance_percentage": compliance_percentage,
            "total_requirements": total_requirements,
            "met_requirements": met_requirements,
            "gaps": [
                {
                    "requirement_id": gap.requirement_id,
                    "description": gap.description,
                    "status": gap.current_status,
                    "recommendation": gap.recommendation,
                    "severity": gap.severity
                }
                for gap in gaps
            ],
            "recommendations": self._generate_recommendations(gaps)
        }

    def _check_requirement(
        self,
        context: Dict[str, Any],
        requirement: ComplianceRequirement
    ) -> bool:
        """
        Check if requirement is met

        Args:
            context: Workflow context
            requirement: Compliance requirement

        Returns:
            True if met, False otherwise
        """

        if not requirement.evidence_required:
            return True

        # Check if all required evidence exists in context
        context_data = context.get('data', {})

        for evidence in requirement.evidence_required:
            if evidence not in context_data or not context_data[evidence]:
                return False

        return True

    def _generate_recommendations(self, gaps: List[ComplianceGap]) -> List[str]:
        """Generate recommendations based on gaps"""

        if not gaps:
            return ["All ISO requirements are met. Continue monitoring compliance."]

        recommendations = []

        # Group by severity
        critical_gaps = [g for g in gaps if g.severity == "critical"]
        high_gaps = [g for g in gaps if g.severity == "high"]

        if critical_gaps:
            recommendations.append(
                f"URGENT: Address {len(critical_gaps)} critical compliance gaps immediately"
            )

        if high_gaps:
            recommendations.append(
                f"Address {len(high_gaps)} high-priority gaps within this workflow"
            )

        # Specific recommendations
        for gap in gaps[:3]:  # Top 3
            recommendations.append(gap.recommendation)

        return recommendations
