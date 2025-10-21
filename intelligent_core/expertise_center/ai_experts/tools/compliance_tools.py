"""
Compliance Tools

Tools for ISO 22301 compliance checking, gap analysis, and evidence validation.
Used by Compliance Auditor expert.
"""

from typing import Dict, Any, List
from .base_tool import BaseTool
import logging

logger = logging.getLogger(__name__)


class ComplianceCheckTool(BaseTool):
    """
    ISO 22301 Compliance Check Tool

    Checks compliance against ISO 22301:2019 clauses.
    Provides clause-by-clause assessment.
    """

    def __init__(self, db_session=None):
        super().__init__(
            name="compliance_check",
            description="Check compliance against ISO 22301:2019 standard clauses",
            parameters={
                "clause_number": {
                    "type": "string",
                    "description": "ISO 22301:2019 clause number (e.g., '8.2.2', '8.4')"
                },
                "evidence_provided": {
                    "type": "array",
                    "description": "List of evidence items provided",
                    "items": {"type": "string"}
                },
                "context": {
                    "type": "string",
                    "description": "Organization context (industry, size, maturity)"
                }
            },
            required_params=["clause_number"]
        )
        self.db_session = db_session

        # ISO 22301:2019 clause requirements
        self.clause_requirements = {
            "4.1": {
                "title": "Understanding the organization and its context",
                "requirements": [
                    "Internal and external issues identified",
                    "Issues relevant to BCMS purpose determined",
                    "Context monitoring process established"
                ]
            },
            "4.2": {
                "title": "Understanding the needs and expectations of interested parties",
                "requirements": [
                    "Interested parties identified",
                    "Requirements of interested parties determined",
                    "Stakeholder monitoring process established"
                ]
            },
            "8.2": {
                "title": "Business impact analysis and risk assessment",
                "requirements": [
                    "BIA process established and maintained",
                    "Impacts of disruptions assessed",
                    "Risk assessment process implemented",
                    "Risks identified and analyzed"
                ]
            },
            "8.2.2": {
                "title": "Business impact analysis",
                "requirements": [
                    "Critical activities identified",
                    "Impact over time assessed",
                    "Recovery time objectives defined",
                    "Dependencies mapped",
                    "Resources identified"
                ]
            },
            "8.4": {
                "title": "Business continuity procedures",
                "requirements": [
                    "BC procedures documented",
                    "Response structure defined",
                    "Procedures for critical activities created",
                    "Communication procedures established",
                    "Recovery procedures documented"
                ]
            },
            "9.1": {
                "title": "Monitoring, measurement, analysis and evaluation",
                "requirements": [
                    "Performance metrics defined",
                    "Monitoring methods established",
                    "Analysis frequency determined",
                    "Evaluation results documented"
                ]
            }
        }

    async def execute(
        self,
        clause_number: str,
        evidence_provided: List[str] = None,
        context: str = None
    ) -> Dict[str, Any]:
        """
        Execute compliance check

        Returns:
            Compliance assessment with status and recommendations
        """

        # Get clause requirements
        clause_info = self.clause_requirements.get(
            clause_number,
            {
                "title": "Unknown clause",
                "requirements": ["Requirements not defined for this clause"]
            }
        )

        # Assess compliance
        evidence_provided = evidence_provided or []
        assessment = self._assess_compliance(
            clause_info["requirements"],
            evidence_provided
        )

        # Generate recommendations
        recommendations = self._generate_recommendations(
            clause_number,
            assessment,
            context
        )

        result = {
            "clause_number": clause_number,
            "clause_title": clause_info["title"],
            "requirements": clause_info["requirements"],
            "evidence_provided": evidence_provided,
            "compliance_status": assessment["status"],
            "compliance_percentage": assessment["percentage"],
            "gaps_identified": assessment["gaps"],
            "recommendations": recommendations
        }

        await self._publish_event('compliance.check.completed', result)

        return result

    def _assess_compliance(
        self,
        requirements: List[str],
        evidence: List[str]
    ) -> Dict[str, Any]:
        """Assess compliance level"""

        if not evidence:
            return {
                "status": "non-compliant",
                "percentage": 0,
                "gaps": requirements
            }

        # Simple matching logic (in production, use NLP/semantic matching)
        met_requirements = []
        gaps = []

        for req in requirements:
            # Check if any evidence addresses this requirement
            req_keywords = req.lower().split()
            matched = False

            for ev in evidence:
                ev_keywords = ev.lower().split()
                # Simple keyword overlap check
                overlap = set(req_keywords) & set(ev_keywords)
                if len(overlap) >= 2:  # At least 2 matching keywords
                    matched = True
                    break

            if matched:
                met_requirements.append(req)
            else:
                gaps.append(req)

        percentage = (len(met_requirements) / len(requirements)) * 100

        if percentage >= 90:
            status = "compliant"
        elif percentage >= 70:
            status = "partially-compliant"
        elif percentage >= 40:
            status = "needs-improvement"
        else:
            status = "non-compliant"

        return {
            "status": status,
            "percentage": round(percentage, 1),
            "gaps": gaps
        }

    def _generate_recommendations(
        self,
        clause_number: str,
        assessment: Dict[str, Any],
        context: str = None
    ) -> List[str]:
        """Generate compliance recommendations"""

        recommendations = []

        if assessment["status"] == "compliant":
            recommendations.append(" Compliance achieved. Continue monitoring and maintaining evidence.")
            recommendations.append("Consider documenting lessons learned and best practices.")
        else:
            recommendations.append(f" Address {len(assessment['gaps'])} gap(s) to achieve compliance.")

            # Specific recommendations for each gap
            for gap in assessment["gaps"][:3]:  # Top 3 gaps
                recommendations.append(f"- {gap}")

        # Clause-specific recommendations
        if clause_number == "8.2.2":
            recommendations.append("BIA Documentation: Ensure impact timeline, RTO/RPO, and dependencies are documented.")
        elif clause_number == "8.4":
            recommendations.append("BC Procedures: Document step-by-step recovery procedures with clear roles.")
        elif clause_number == "9.1":
            recommendations.append("Performance Metrics: Define KPIs and establish monitoring processes.")

        return recommendations


class GapAnalysisTool(BaseTool):
    """
    Gap Analysis Tool

    Performs comprehensive gap analysis against ISO 22301.
    Identifies missing elements and prioritizes remediation.
    """

    def __init__(self, db_session=None):
        super().__init__(
            name="gap_analysis",
            description="Perform comprehensive gap analysis against ISO 22301 requirements",
            parameters={
                "module": {
                    "type": "string",
                    "description": "BCM module to analyze (e.g., 'BIA', 'Strategy', 'Planning')"
                },
                "current_state": {
                    "type": "object",
                    "description": "Current implementation state",
                    "properties": {
                        "completed_steps": {"type": "array", "items": {"type": "string"}},
                        "in_progress_steps": {"type": "array", "items": {"type": "string"}},
                        "not_started_steps": {"type": "array", "items": {"type": "string"}}
                    }
                },
                "maturity_level": {
                    "type": "string",
                    "description": "Current BCM maturity level (1-5)"
                }
            },
            required_params=["module", "current_state"]
        )
        self.db_session = db_session

    async def execute(
        self,
        module: str,
        current_state: Dict[str, Any],
        maturity_level: str = "1"
    ) -> Dict[str, Any]:
        """
        Execute gap analysis

        Returns:
            Comprehensive gap analysis with prioritized actions
        """

        # Define expected deliverables per module
        expected_deliverables = {
            "BIA": [
                "Critical activities identified",
                "Impact over time assessed",
                "RTO/RPO defined",
                "Dependencies mapped",
                "Resource requirements documented"
            ],
            "Strategy": [
                "Recovery strategies defined",
                "Strategy options evaluated",
                "Selected strategies documented",
                "Resource allocation planned",
                "Budget approved"
            ],
            "Planning": [
                "BC plans documented",
                "Response procedures defined",
                "Communication plans created",
                "Recovery procedures documented",
                "Testing schedule established"
            ],
            "Testing": [
                "Test plan developed",
                "Test scenarios defined",
                "Tests executed",
                "Results documented",
                "Improvements identified"
            ]
        }

        expected = expected_deliverables.get(module, [])
        completed = current_state.get("completed_steps", [])
        in_progress = current_state.get("in_progress_steps", [])

        # Identify gaps
        gaps = [item for item in expected if item not in completed and item not in in_progress]

        # Calculate completion percentage
        total_items = len(expected)
        completed_items = len(completed)
        completion_percentage = (completed_items / total_items * 100) if total_items > 0 else 0

        # Prioritize gaps
        prioritized_gaps = self._prioritize_gaps(gaps, module, maturity_level)

        # Generate action plan
        action_plan = self._generate_action_plan(prioritized_gaps, maturity_level)

        result = {
            "module": module,
            "expected_deliverables": expected,
            "completed_deliverables": completed,
            "in_progress_deliverables": in_progress,
            "identified_gaps": gaps,
            "completion_percentage": round(completion_percentage, 1),
            "maturity_level": maturity_level,
            "prioritized_gaps": prioritized_gaps,
            "action_plan": action_plan,
            "estimated_effort_days": self._estimate_effort(gaps, maturity_level)
        }

        await self._publish_event('gap.analysis.completed', result)

        return result

    def _prioritize_gaps(
        self,
        gaps: List[str],
        module: str,
        maturity_level: str
    ) -> List[Dict[str, Any]]:
        """Prioritize gaps based on criticality and dependencies"""

        priority_keywords = {
            "high": ["critical", "rto", "rpo", "impact", "risk"],
            "medium": ["strategy", "plan", "procedure", "communication"],
            "low": ["documentation", "review", "update"]
        }

        prioritized = []

        for gap in gaps:
            gap_lower = gap.lower()
            priority = "low"

            for pri, keywords in priority_keywords.items():
                if any(keyword in gap_lower for keyword in keywords):
                    priority = pri
                    break

            prioritized.append({
                "gap": gap,
                "priority": priority,
                "recommended_action": self._recommend_action(gap, maturity_level)
            })

        # Sort by priority
        priority_order = {"high": 0, "medium": 1, "low": 2}
        prioritized.sort(key=lambda x: priority_order[x["priority"]])

        return prioritized

    def _recommend_action(self, gap: str, maturity_level: str) -> str:
        """Recommend action for gap"""

        if "identified" in gap.lower():
            return "Conduct identification workshop with stakeholders"
        elif "assessed" in gap.lower() or "defined" in gap.lower():
            return "Perform assessment using templates and tools"
        elif "mapped" in gap.lower():
            return "Create visual map using process mapping tools"
        elif "documented" in gap.lower():
            return "Document findings using standard templates"
        elif "planned" in gap.lower():
            return "Develop plan with clear milestones and owners"
        else:
            return "Complete this deliverable using best practices"

    def _generate_action_plan(
        self,
        prioritized_gaps: List[Dict[str, Any]],
        maturity_level: str
    ) -> List[Dict[str, str]]:
        """Generate phased action plan"""

        action_plan = []

        # Phase 1: High priority gaps
        high_priority = [g for g in prioritized_gaps if g["priority"] == "high"]
        if high_priority:
            action_plan.append({
                "phase": "Phase 1 (Immediate)",
                "timeline": "Weeks 1-2",
                "actions": [g["gap"] for g in high_priority],
                "focus": "Address critical compliance gaps"
            })

        # Phase 2: Medium priority gaps
        medium_priority = [g for g in prioritized_gaps if g["priority"] == "medium"]
        if medium_priority:
            action_plan.append({
                "phase": "Phase 2 (Short-term)",
                "timeline": "Weeks 3-6",
                "actions": [g["gap"] for g in medium_priority],
                "focus": "Build core capabilities"
            })

        # Phase 3: Low priority gaps
        low_priority = [g for g in prioritized_gaps if g["priority"] == "low"]
        if low_priority:
            action_plan.append({
                "phase": "Phase 3 (Medium-term)",
                "timeline": "Weeks 7-12",
                "actions": [g["gap"] for g in low_priority],
                "focus": "Complete documentation and refinement"
            })

        return action_plan

    def _estimate_effort(self, gaps: List[str], maturity_level: str) -> int:
        """Estimate effort in days"""

        # Base effort per gap
        effort_per_gap = {
            "1": 3,  # Low maturity = more effort
            "2": 2,
            "3": 1.5,
            "4": 1,
            "5": 0.5
        }

        days_per_gap = effort_per_gap.get(maturity_level, 2)
        total_days = len(gaps) * days_per_gap

        return round(total_days)


class EvidenceValidatorTool(BaseTool):
    """
    Evidence Validation Tool

    Validates evidence quality and completeness for ISO 22301 compliance.
    """

    def __init__(self, db_session=None):
        super().__init__(
            name="evidence_validator",
            description="Validate quality and completeness of compliance evidence",
            parameters={
                "evidence_type": {
                    "type": "string",
                    "description": "Type of evidence (e.g., 'document', 'record', 'procedure', 'test_result')"
                },
                "evidence_items": {
                    "type": "array",
                    "description": "List of evidence items to validate",
                    "items": {"type": "string"}
                },
                "clause_number": {
                    "type": "string",
                    "description": "Related ISO 22301 clause number"
                }
            },
            required_params=["evidence_type", "evidence_items"]
        )
        self.db_session = db_session

    async def execute(
        self,
        evidence_type: str,
        evidence_items: List[str],
        clause_number: str = None
    ) -> Dict[str, Any]:
        """
        Execute evidence validation

        Returns:
            Validation results with quality score and recommendations
        """

        # Validate each evidence item
        validation_results = []
        for item in evidence_items:
            result = self._validate_evidence_item(item, evidence_type)
            validation_results.append(result)

        # Calculate overall quality score
        quality_scores = [r["quality_score"] for r in validation_results]
        overall_score = sum(quality_scores) / len(quality_scores) if quality_scores else 0

        # Determine validation status
        if overall_score >= 80:
            status = "valid"
        elif overall_score >= 60:
            status = "acceptable"
        elif overall_score >= 40:
            status = "needs-improvement"
        else:
            status = "insufficient"

        # Generate recommendations
        recommendations = self._generate_evidence_recommendations(
            validation_results,
            evidence_type,
            status
        )

        result = {
            "evidence_type": evidence_type,
            "clause_number": clause_number,
            "total_items": len(evidence_items),
            "validation_results": validation_results,
            "overall_quality_score": round(overall_score, 1),
            "validation_status": status,
            "recommendations": recommendations
        }

        await self._publish_event('evidence.validation.completed', result)

        return result

    def _validate_evidence_item(
        self,
        item: str,
        evidence_type: str
    ) -> Dict[str, Any]:
        """Validate individual evidence item"""

        # Quality criteria
        criteria = {
            "document": {
                "completeness": ["version", "date", "author", "approver"],
                "clarity": ["purpose", "scope", "content"],
                "traceability": ["reference", "links"]
            },
            "record": {
                "completeness": ["date", "time", "responsible", "result"],
                "accuracy": ["data", "measurements"],
                "retention": ["storage", "period"]
            },
            "procedure": {
                "completeness": ["steps", "roles", "resources"],
                "clarity": ["sequence", "decisions", "outputs"],
                "usability": ["format", "access"]
            },
            "test_result": {
                "completeness": ["scenario", "date", "participants", "results"],
                "objectivity": ["metrics", "observations"],
                "actionability": ["issues", "improvements"]
            }
        }

        item_criteria = criteria.get(evidence_type, criteria["document"])

        # Check criteria (simplified - keyword matching)
        item_lower = item.lower()
        scores = []

        for category, keywords in item_criteria.items():
            matched = sum(1 for kw in keywords if kw in item_lower)
            category_score = (matched / len(keywords)) * 100
            scores.append(category_score)

        quality_score = sum(scores) / len(scores) if scores else 0

        issues = []
        if quality_score < 80:
            for category, keywords in item_criteria.items():
                missing = [kw for kw in keywords if kw not in item_lower]
                if missing:
                    issues.append(f"Missing {category}: {', '.join(missing)}")

        return {
            "evidence_item": item,
            "quality_score": round(quality_score, 1),
            "issues_identified": issues
        }

    def _generate_evidence_recommendations(
        self,
        validation_results: List[Dict[str, Any]],
        evidence_type: str,
        status: str
    ) -> List[str]:
        """Generate evidence improvement recommendations"""

        recommendations = []

        if status == "valid":
            recommendations.append(" Evidence quality is good. Maintain documentation standards.")
        else:
            # Identify common issues
            all_issues = []
            for result in validation_results:
                all_issues.extend(result.get("issues_identified", []))

            if all_issues:
                recommendations.append(f" Address {len(all_issues)} quality issue(s):")

                # Summarize most common issues
                issue_categories = {}
                for issue in all_issues:
                    category = issue.split(":")[0] if ":" in issue else issue
                    issue_categories[category] = issue_categories.get(category, 0) + 1

                for category, count in sorted(issue_categories.items(), key=lambda x: x[1], reverse=True)[:3]:
                    recommendations.append(f"- {category} (affects {count} items)")

        # Type-specific recommendations
        if evidence_type == "document":
            recommendations.append("Document Best Practice: Include version control, approval signatures, review dates")
        elif evidence_type == "procedure":
            recommendations.append("Procedure Best Practice: Use flowcharts, define decision points, specify roles clearly")
        elif evidence_type == "test_result":
            recommendations.append("Test Results Best Practice: Include pass/fail criteria, actual vs expected, lessons learned")

        return recommendations
