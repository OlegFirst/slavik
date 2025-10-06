"""
Strategic Planning Tools

Tools for long-term BCM program planning, timeline prediction, and resource planning.
Used by Strategic Planner expert.
"""

from typing import Dict, Any, List
from .base_tool import BaseTool
import logging
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class TimelinePredictorTool(BaseTool):
    """
    Timeline Prediction Tool

    Predicts implementation timelines for BCM program phases based on:
    - Organization size and complexity
    - Current maturity level
    - Available resources
    - Industry benchmarks
    """

    def __init__(self, db_session=None):
        super().__init__(
            name="timeline_predictor",
            description="Predict implementation timeline for BCM program phases",
            parameters={
                "program_scope": {
                    "type": "string",
                    "description": "Scope of BCM program (e.g., 'full-iso22301', 'bia-only', 'strategy-planning')"
                },
                "org_size": {
                    "type": "string",
                    "description": "Organization size: 'small' (<50), 'medium' (50-500), 'large' (>500)"
                },
                "maturity_level": {
                    "type": "integer",
                    "description": "Current BCM maturity level (1-5)"
                },
                "resource_availability": {
                    "type": "string",
                    "description": "Resource availability: 'limited', 'moderate', 'full'"
                },
                "complexity_factors": {
                    "type": "array",
                    "description": "Complexity factors (e.g., 'multiple-sites', 'regulated', 'complex-it')",
                    "items": {"type": "string"}
                }
            },
            required_params=["program_scope", "org_size", "maturity_level"]
        )
        self.db_session = db_session

    async def execute(
        self,
        program_scope: str,
        org_size: str,
        maturity_level: int,
        resource_availability: str = "moderate",
        complexity_factors: List[str] = None
    ) -> Dict[str, Any]:
        """
        Execute timeline prediction

        Returns:
            Predicted timeline with phases, milestones, and critical path
        """

        # Base timeline for different scopes (in weeks)
        base_timelines = {
            "full-iso22301": {
                "small": 16,
                "medium": 24,
                "large": 36
            },
            "bia-only": {
                "small": 4,
                "medium": 6,
                "large": 8
            },
            "strategy-planning": {
                "small": 6,
                "medium": 10,
                "large": 14
            },
            "testing-improvement": {
                "small": 8,
                "medium": 12,
                "large": 16
            }
        }

        # Get base timeline
        scope_timelines = base_timelines.get(
            program_scope,
            base_timelines["full-iso22301"]
        )
        base_weeks = scope_timelines.get(org_size, scope_timelines["medium"])

        # Adjust for maturity level
        maturity_multiplier = {
            1: 1.3,  # Starting from scratch = longer
            2: 1.1,
            3: 1.0,
            4: 0.9,
            5: 0.8   # High maturity = faster
        }
        adjusted_weeks = base_weeks * maturity_multiplier.get(maturity_level, 1.0)

        # Adjust for resource availability
        resource_multiplier = {
            "limited": 1.4,
            "moderate": 1.0,
            "full": 0.7
        }
        adjusted_weeks *= resource_multiplier.get(resource_availability, 1.0)

        # Adjust for complexity factors
        complexity_factors = complexity_factors or []
        complexity_addition = len(complexity_factors) * 2  # 2 weeks per complexity factor
        total_weeks = adjusted_weeks + complexity_addition

        # Generate phased timeline
        phases = self._generate_phases(program_scope, total_weeks, org_size)

        # Identify milestones
        milestones = self._identify_milestones(phases)

        # Calculate critical path
        critical_path = self._calculate_critical_path(phases)

        # Calculate completion date
        start_date = datetime.now()
        completion_date = start_date + timedelta(weeks=total_weeks)

        result = {
            "program_scope": program_scope,
            "org_size": org_size,
            "maturity_level": maturity_level,
            "base_timeline_weeks": round(base_weeks, 1),
            "adjusted_timeline_weeks": round(total_weeks, 1),
            "estimated_completion_date": completion_date.strftime("%Y-%m-%d"),
            "phases": phases,
            "milestones": milestones,
            "critical_path": critical_path,
            "risk_factors": self._identify_risk_factors(
                complexity_factors,
                resource_availability,
                maturity_level
            )
        }

        await self._publish_event('timeline.prediction.completed', result)

        return result

    def _generate_phases(
        self,
        scope: str,
        total_weeks: float,
        org_size: str
    ) -> List[Dict[str, Any]]:
        """Generate phased timeline"""

        # Phase templates
        phase_templates = {
            "full-iso22301": [
                {"name": "Setup & Assessment", "percentage": 0.15},
                {"name": "BIA & Risk Assessment", "percentage": 0.25},
                {"name": "Strategy Development", "percentage": 0.20},
                {"name": "Plan Development", "percentage": 0.20},
                {"name": "Implementation & Testing", "percentage": 0.15},
                {"name": "Review & Certification Prep", "percentage": 0.05}
            ],
            "bia-only": [
                {"name": "Preparation", "percentage": 0.20},
                {"name": "Data Collection", "percentage": 0.30},
                {"name": "Analysis", "percentage": 0.30},
                {"name": "Documentation & Review", "percentage": 0.20}
            ],
            "strategy-planning": [
                {"name": "Strategy Assessment", "percentage": 0.25},
                {"name": "Option Development", "percentage": 0.35},
                {"name": "Evaluation & Selection", "percentage": 0.25},
                {"name": "Documentation", "percentage": 0.15}
            ]
        }

        template = phase_templates.get(scope, phase_templates["full-iso22301"])

        phases = []
        cumulative_weeks = 0

        for phase in template:
            duration_weeks = total_weeks * phase["percentage"]
            start_week = cumulative_weeks
            end_week = cumulative_weeks + duration_weeks

            phases.append({
                "phase_name": phase["name"],
                "duration_weeks": round(duration_weeks, 1),
                "start_week": round(start_week, 1),
                "end_week": round(end_week, 1),
                "key_deliverables": self._get_phase_deliverables(phase["name"])
            })

            cumulative_weeks = end_week

        return phases

    def _get_phase_deliverables(self, phase_name: str) -> List[str]:
        """Get key deliverables for each phase"""

        deliverables = {
            "Setup & Assessment": [
                "Project charter approved",
                "Stakeholder engagement plan",
                "Current state assessment completed"
            ],
            "BIA & Risk Assessment": [
                "Critical processes identified",
                "Impact analysis completed",
                "Risk assessment report",
                "RTO/RPO defined"
            ],
            "Strategy Development": [
                "Recovery strategies defined",
                "Strategy options evaluated",
                "Budget approved",
                "Implementation roadmap"
            ],
            "Plan Development": [
                "BC plans documented",
                "Response procedures created",
                "Communication plans",
                "Resource allocation plans"
            ],
            "Implementation & Testing": [
                "Plans implemented",
                "Training completed",
                "Tests executed",
                "Test results documented"
            ],
            "Review & Certification Prep": [
                "Internal audit completed",
                "Gap remediation",
                "Documentation review",
                "Certification application"
            ],
            "Preparation": [
                "Scope defined",
                "Templates prepared",
                "Stakeholders identified"
            ],
            "Data Collection": [
                "Interviews conducted",
                "Data gathered",
                "Dependencies mapped"
            ],
            "Analysis": [
                "Impact assessed",
                "Criticality determined",
                "RTO/RPO set"
            ],
            "Documentation & Review": [
                "BIA report completed",
                "Findings reviewed",
                "Recommendations documented"
            ]
        }

        return deliverables.get(phase_name, ["Phase deliverables to be defined"])

    def _identify_milestones(self, phases: List[Dict[str, Any]]) -> List[Dict[str, str]]:
        """Identify key milestones"""

        milestones = []

        for phase in phases:
            # Each phase end is a milestone
            milestones.append({
                "milestone": f"{phase['phase_name']} Complete",
                "week": str(round(phase['end_week'], 1)),
                "significance": "Phase completion gate"
            })

        # Add critical milestones
        if len(phases) >= 3:
            mid_point = len(phases) // 2
            milestones.insert(mid_point, {
                "milestone": "Mid-Program Review",
                "week": str(round(phases[mid_point - 1]['end_week'], 1)),
                "significance": "Program health check and adjustment"
            })

        return milestones

    def _calculate_critical_path(self, phases: List[Dict[str, Any]]) -> List[str]:
        """Calculate critical path activities"""

        critical_path = []

        # First phase is always critical
        if phases:
            critical_path.append(f"Week {round(phases[0]['start_week'], 1)}-{round(phases[0]['end_week'], 1)}: {phases[0]['phase_name']}")

        # Middle phases with longest duration are critical
        if len(phases) > 2:
            middle_phases = phases[1:-1]
            longest_phase = max(middle_phases, key=lambda x: x['duration_weeks'])
            critical_path.append(
                f"Week {round(longest_phase['start_week'], 1)}-{round(longest_phase['end_week'], 1)}: {longest_phase['phase_name']} (longest phase)"
            )

        # Last phase is always critical
        if len(phases) > 1:
            last_phase = phases[-1]
            critical_path.append(
                f"Week {round(last_phase['start_week'], 1)}-{round(last_phase['end_week'], 1)}: {last_phase['phase_name']}"
            )

        return critical_path

    def _identify_risk_factors(
        self,
        complexity_factors: List[str],
        resource_availability: str,
        maturity_level: int
    ) -> List[Dict[str, str]]:
        """Identify timeline risk factors"""

        risks = []

        if resource_availability == "limited":
            risks.append({
                "risk": "Limited resource availability",
                "impact": "May cause timeline delays",
                "mitigation": "Consider phased approach or external support"
            })

        if maturity_level <= 2:
            risks.append({
                "risk": "Low BCM maturity",
                "impact": "Learning curve may extend timeline",
                "mitigation": "Invest in training and expert guidance"
            })

        if complexity_factors and len(complexity_factors) >= 3:
            risks.append({
                "risk": "High complexity",
                "impact": f"{len(complexity_factors)} complexity factors identified",
                "mitigation": "Break down into manageable sub-projects"
            })

        return risks


class ResourcePlannerTool(BaseTool):
    """
    Resource Planning Tool

    Plans resource requirements for BCM program including:
    - Staff time allocation
    - Budget estimation
    - External support needs
    - Tool/technology requirements
    """

    def __init__(self, db_session=None):
        super().__init__(
            name="resource_planner",
            description="Plan resource requirements for BCM program implementation",
            parameters={
                "program_scope": {
                    "type": "string",
                    "description": "Scope of BCM program"
                },
                "org_size": {
                    "type": "string",
                    "description": "Organization size: 'small', 'medium', 'large'"
                },
                "timeline_weeks": {
                    "type": "number",
                    "description": "Expected program timeline in weeks"
                },
                "internal_capability": {
                    "type": "string",
                    "description": "Internal BCM capability: 'none', 'basic', 'advanced'"
                },
                "budget_range": {
                    "type": "string",
                    "description": "Budget range: 'tight', 'moderate', 'flexible'"
                }
            },
            required_params=["program_scope", "org_size", "timeline_weeks"]
        )
        self.db_session = db_session

    async def execute(
        self,
        program_scope: str,
        org_size: str,
        timeline_weeks: float,
        internal_capability: str = "basic",
        budget_range: str = "moderate"
    ) -> Dict[str, Any]:
        """
        Execute resource planning

        Returns:
            Comprehensive resource plan with staff, budget, and tools
        """

        # Calculate staff requirements
        staff_plan = self._calculate_staff_requirements(
            program_scope,
            org_size,
            timeline_weeks,
            internal_capability
        )

        # Estimate budget
        budget_estimate = self._estimate_budget(
            program_scope,
            org_size,
            timeline_weeks,
            internal_capability,
            budget_range
        )

        # Identify tool/technology needs
        tools_needed = self._identify_tool_needs(program_scope, org_size)

        # Recommend external support
        external_support = self._recommend_external_support(
            internal_capability,
            program_scope,
            budget_range
        )

        result = {
            "program_scope": program_scope,
            "org_size": org_size,
            "timeline_weeks": timeline_weeks,
            "staff_requirements": staff_plan,
            "budget_estimate": budget_estimate,
            "tools_and_technology": tools_needed,
            "external_support_recommendations": external_support,
            "resource_optimization_tips": self._get_optimization_tips(budget_range)
        }

        await self._publish_event('resource.planning.completed', result)

        return result

    def _calculate_staff_requirements(
        self,
        scope: str,
        org_size: str,
        timeline_weeks: float,
        capability: str
    ) -> Dict[str, Any]:
        """Calculate staff time requirements"""

        # Base effort in person-days
        base_effort = {
            "full-iso22301": {
                "small": 60,
                "medium": 120,
                "large": 240
            },
            "bia-only": {
                "small": 15,
                "medium": 25,
                "large": 40
            },
            "strategy-planning": {
                "small": 25,
                "medium": 40,
                "large": 70
            }
        }

        scope_effort = base_effort.get(scope, base_effort["full-iso22301"])
        total_days = scope_effort.get(org_size, scope_effort["medium"])

        # Adjust for capability
        capability_multiplier = {
            "none": 1.3,
            "basic": 1.0,
            "advanced": 0.8
        }
        total_days *= capability_multiplier.get(capability, 1.0)

        # Role breakdown
        roles = {
            "Program Lead": {
                "percentage": 0.30,
                "days": round(total_days * 0.30, 1),
                "description": "BCM program coordination and stakeholder management"
            },
            "Subject Matter Experts": {
                "percentage": 0.40,
                "days": round(total_days * 0.40, 1),
                "description": "BIA, risk assessment, strategy development"
            },
            "Process Owners": {
                "percentage": 0.20,
                "days": round(total_days * 0.20, 1),
                "description": "Process input, validation, plan development"
            },
            "Support Staff": {
                "percentage": 0.10,
                "days": round(total_days * 0.10, 1),
                "description": "Documentation, coordination, administration"
            }
        }

        return {
            "total_effort_days": round(total_days, 1),
            "role_breakdown": roles,
            "average_weekly_commitment": round(total_days / timeline_weeks, 1),
            "peak_resource_periods": self._identify_peak_periods(timeline_weeks)
        }

    def _estimate_budget(
        self,
        scope: str,
        org_size: str,
        timeline_weeks: float,
        capability: str,
        budget_range: str
    ) -> Dict[str, Any]:
        """Estimate program budget"""

        # Base budget (USD)
        base_budgets = {
            "full-iso22301": {
                "small": 50000,
                "medium": 120000,
                "large": 300000
            },
            "bia-only": {
                "small": 15000,
                "medium": 30000,
                "large": 60000
            },
            "strategy-planning": {
                "small": 25000,
                "medium": 50000,
                "large": 100000
            }
        }

        scope_budgets = base_budgets.get(scope, base_budgets["full-iso22301"])
        base_budget = scope_budgets.get(org_size, scope_budgets["medium"])

        # Budget breakdown
        budget_breakdown = {
            "External Consulting": {
                "percentage": 0.40 if capability == "none" else 0.20 if capability == "basic" else 0.10,
                "amount": 0
            },
            "Software/Tools": {
                "percentage": 0.20,
                "amount": 0
            },
            "Training": {
                "percentage": 0.15,
                "amount": 0
            },
            "Testing & Exercises": {
                "percentage": 0.10,
                "amount": 0
            },
            "Documentation & Templates": {
                "percentage": 0.05,
                "amount": 0
            },
            "Certification (if applicable)": {
                "percentage": 0.10,
                "amount": 0
            }
        }

        # Calculate amounts
        for category in budget_breakdown.values():
            category["amount"] = round(base_budget * category["percentage"], 2)

        total_budget = sum(cat["amount"] for cat in budget_breakdown.values())

        return {
            "estimated_total_budget_usd": round(total_budget, 2),
            "budget_range_assessment": budget_range,
            "breakdown": budget_breakdown,
            "cost_saving_opportunities": self._identify_cost_savings(capability, budget_range),
            "budget_confidence": "moderate" if budget_range == "moderate" else "low" if budget_range == "tight" else "high"
        }

    def _identify_tool_needs(self, scope: str, org_size: str) -> List[Dict[str, str]]:
        """Identify required tools and technology"""

        tools = [
            {
                "category": "BCM Platform",
                "tool": "AI-Platform-ISO (this platform)",
                "priority": "Essential",
                "estimated_cost": "Included"
            },
            {
                "category": "Documentation",
                "tool": "Document management system",
                "priority": "High",
                "estimated_cost": "$2,000-5,000/year"
            },
            {
                "category": "Communication",
                "tool": "Mass notification system",
                "priority": "High" if org_size in ["medium", "large"] else "Medium",
                "estimated_cost": "$5,000-15,000/year"
            },
            {
                "category": "Collaboration",
                "tool": "Project management tool (e.g., Asana, Monday)",
                "priority": "Medium",
                "estimated_cost": "$1,000-3,000/year"
            }
        ]

        if scope == "full-iso22301":
            tools.append({
                "category": "Compliance Tracking",
                "tool": "GRC platform",
                "priority": "Medium",
                "estimated_cost": "$10,000-30,000/year"
            })

        return tools

    def _recommend_external_support(
        self,
        capability: str,
        scope: str,
        budget_range: str
    ) -> Dict[str, Any]:
        """Recommend external support needs"""

        if capability == "none" or (capability == "basic" and scope == "full-iso22301"):
            recommendation = "Strongly recommended"
            support_areas = [
                "Program setup and methodology",
                "BIA facilitation and analysis",
                "Strategy development",
                "Certification preparation"
            ]
            estimated_days = 30 if scope == "full-iso22301" else 10
        elif capability == "basic":
            recommendation = "Recommended for specific phases"
            support_areas = [
                "Complex BIA scenarios",
                "Strategy evaluation",
                "Certification preparation"
            ]
            estimated_days = 15
        else:
            recommendation = "Optional - advisory only"
            support_areas = [
                "Quality assurance review",
                "Certification audit support"
            ]
            estimated_days = 5

        return {
            "recommendation": recommendation,
            "support_areas": support_areas,
            "estimated_consultant_days": estimated_days,
            "estimated_cost_usd": round(estimated_days * 1500, 2),  # $1500/day typical rate
            "value_proposition": self._get_consultant_value(capability, budget_range)
        }

    def _get_consultant_value(self, capability: str, budget_range: str) -> str:
        """Describe value proposition of consultants"""

        if capability == "none":
            return "Critical for success - provides methodology, experience, and accelerates timeline by 30-40%"
        elif capability == "basic":
            return "Valuable for complex areas - reduces risk and improves quality"
        else:
            return "Nice to have - provides validation and best practice insights"

    def _identify_peak_periods(self, timeline_weeks: float) -> List[str]:
        """Identify periods of peak resource demand"""

        mid_point = timeline_weeks / 2

        return [
            f"Weeks 1-3: Program kickoff and planning",
            f"Weeks {round(mid_point - 2, 1)}-{round(mid_point + 2, 1)}: BIA/Analysis phase (peak demand)",
            f"Weeks {round(timeline_weeks - 4, 1)}-{round(timeline_weeks, 1)}: Testing and finalization"
        ]

    def _identify_cost_savings(self, capability: str, budget_range: str) -> List[str]:
        """Identify cost-saving opportunities"""

        savings = []

        if capability in ["basic", "advanced"]:
            savings.append("Leverage internal expertise to reduce consulting costs")

        if budget_range == "tight":
            savings.append("Use free/open-source tools where possible")
            savings.append("Implement in phases to spread costs")
            savings.append("Leverage platform AI assistants instead of external consultants for routine tasks")

        savings.append("Join industry peer groups for shared learning")
        savings.append("Use templates and frameworks from this platform")

        return savings

    def _get_optimization_tips(self, budget_range: str) -> List[str]:
        """Get resource optimization tips"""

        tips = [
            "Assign dedicated program lead (even part-time) rather than dividing responsibilities",
            "Schedule BIA interviews efficiently to minimize disruption",
            "Use AI assistants for initial drafts and analysis",
            "Batch similar activities to maintain momentum"
        ]

        if budget_range == "tight":
            tips.extend([
                "Prioritize essential compliance over nice-to-have features",
                "Consider phased implementation to spread costs",
                "Maximize use of platform automation and AI tools"
            ])
        elif budget_range == "flexible":
            tips.extend([
                "Invest in training for long-term capability building",
                "Consider certification to validate program maturity",
                "Build comprehensive testing program from start"
            ])

        return tips


class MaturityAssessmentTool(BaseTool):
    """
    BCM Maturity Assessment Tool

    Assesses current BCM program maturity level (1-5) and identifies improvement opportunities.
    """

    def __init__(self, db_session=None):
        super().__init__(
            name="maturity_assessment",
            description="Assess BCM program maturity level and identify improvement opportunities",
            parameters={
                "current_capabilities": {
                    "type": "array",
                    "description": "List of current BCM capabilities",
                    "items": {"type": "string"}
                },
                "program_age_months": {
                    "type": "integer",
                    "description": "Age of BCM program in months"
                },
                "recent_achievements": {
                    "type": "array",
                    "description": "Recent program achievements",
                    "items": {"type": "string"}
                }
            },
            required_params=["current_capabilities"]
        )
        self.db_session = db_session

        # Maturity level criteria
        self.maturity_criteria = {
            1: {
                "level": "Initial/Ad-hoc",
                "characteristics": [
                    "No formal BCM program",
                    "Reactive approach to disruptions",
                    "Limited documentation",
                    "No defined processes"
                ]
            },
            2: {
                "level": "Developing",
                "characteristics": [
                    "Basic BIA completed",
                    "Some BC plans exist",
                    "Limited testing",
                    "Informal governance"
                ]
            },
            3: {
                "level": "Defined",
                "characteristics": [
                    "Comprehensive BIA",
                    "Documented BC plans",
                    "Regular testing",
                    "Defined governance structure",
                    "ISO 22301 alignment started"
                ]
            },
            4: {
                "level": "Managed",
                "characteristics": [
                    "ISO 22301 certified",
                    "Regular testing and exercises",
                    "Continuous improvement process",
                    "Integration with enterprise risk",
                    "Performance metrics tracked"
                ]
            },
            5: {
                "level": "Optimized",
                "characteristics": [
                    "Fully integrated with business",
                    "Continuous monitoring",
                    "Predictive capabilities",
                    "Industry leadership",
                    "Innovation in BC practices"
                ]
            }
        }

    async def execute(
        self,
        current_capabilities: List[str],
        program_age_months: int = 0,
        recent_achievements: List[str] = None
    ) -> Dict[str, Any]:
        """
        Execute maturity assessment

        Returns:
            Maturity level assessment with improvement roadmap
        """

        # Assess current maturity level
        maturity_level = self._assess_maturity_level(
            current_capabilities,
            program_age_months
        )

        # Get maturity details
        current_maturity = self.maturity_criteria[maturity_level]
        next_maturity = self.maturity_criteria.get(maturity_level + 1)

        # Identify gaps to next level
        gaps = self._identify_maturity_gaps(
            current_capabilities,
            maturity_level
        )

        # Create improvement roadmap
        roadmap = self._create_improvement_roadmap(
            maturity_level,
            gaps
        )

        result = {
            "current_maturity_level": maturity_level,
            "maturity_label": current_maturity["level"],
            "characteristics": current_maturity["characteristics"],
            "program_age_months": program_age_months,
            "next_level": next_maturity["level"] if next_maturity else "Maximum maturity achieved",
            "gaps_to_next_level": gaps,
            "improvement_roadmap": roadmap,
            "strengths": self._identify_strengths(current_capabilities, maturity_level),
            "estimated_time_to_next_level_months": self._estimate_advancement_time(maturity_level, gaps)
        }

        await self._publish_event('maturity.assessment.completed', result)

        return result

    def _assess_maturity_level(
        self,
        capabilities: List[str],
        program_age: int
    ) -> int:
        """Assess maturity level based on capabilities"""

        # Keyword mapping to maturity levels
        level_keywords = {
            1: [],  # Default if nothing matches
            2: ["bia", "basic", "plan", "identified"],
            3: ["comprehensive", "documented", "tested", "governance", "iso"],
            4: ["certified", "metrics", "integrated", "continuous", "improvement"],
            5: ["optimized", "predictive", "automated", "leadership", "innovation"]
        }

        # Score each level
        capabilities_lower = [c.lower() for c in capabilities]
        level_scores = {}

        for level, keywords in level_keywords.items():
            if keywords:
                matches = sum(1 for cap in capabilities_lower for kw in keywords if kw in cap)
                level_scores[level] = matches
            else:
                level_scores[level] = 0

        # Determine level (conservative approach)
        assessed_level = 1

        for level in [5, 4, 3, 2]:
            if level_scores.get(level, 0) >= 2:  # At least 2 matching capabilities
                assessed_level = level
                break

        # Adjust for program age (new programs unlikely to be high maturity)
        if program_age < 6 and assessed_level > 2:
            assessed_level = 2
        elif program_age < 12 and assessed_level > 3:
            assessed_level = 3

        return assessed_level

    def _identify_maturity_gaps(
        self,
        capabilities: List[str],
        current_level: int
    ) -> List[str]:
        """Identify gaps to next maturity level"""

        if current_level >= 5:
            return []

        next_level = current_level + 1
        next_level_characteristics = self.maturity_criteria[next_level]["characteristics"]

        # Simplified gap identification
        capabilities_lower = [c.lower() for c in capabilities]
        gaps = []

        for characteristic in next_level_characteristics:
            # Check if capability is present
            char_keywords = characteristic.lower().split()
            matched = any(
                any(kw in cap for kw in char_keywords)
                for cap in capabilities_lower
            )

            if not matched:
                gaps.append(characteristic)

        return gaps

    def _create_improvement_roadmap(
        self,
        current_level: int,
        gaps: List[str]
    ) -> List[Dict[str, Any]]:
        """Create improvement roadmap"""

        if not gaps:
            return [{
                "phase": "Maintain and Optimize",
                "timeline": "Ongoing",
                "actions": ["Continue current practices", "Seek optimization opportunities"],
                "priority": "Maintenance"
            }]

        roadmap = []

        # Prioritize gaps
        high_priority = gaps[:2] if len(gaps) >= 2 else gaps
        medium_priority = gaps[2:4] if len(gaps) > 2 else []
        low_priority = gaps[4:] if len(gaps) > 4 else []

        if high_priority:
            roadmap.append({
                "phase": "Phase 1: Critical Improvements",
                "timeline": "Months 1-3",
                "actions": high_priority,
                "priority": "High"
            })

        if medium_priority:
            roadmap.append({
                "phase": "Phase 2: Enhancement",
                "timeline": "Months 4-6",
                "actions": medium_priority,
                "priority": "Medium"
            })

        if low_priority:
            roadmap.append({
                "phase": "Phase 3: Optimization",
                "timeline": "Months 7-12",
                "actions": low_priority,
                "priority": "Low"
            })

        return roadmap

    def _identify_strengths(
        self,
        capabilities: List[str],
        maturity_level: int
    ) -> List[str]:
        """Identify program strengths"""

        strengths = []

        # Check current level characteristics
        current_chars = self.maturity_criteria[maturity_level]["characteristics"]

        capabilities_lower = [c.lower() for c in capabilities]

        for char in current_chars:
            char_keywords = char.lower().split()
            matched = any(
                any(kw in cap for kw in char_keywords)
                for cap in capabilities_lower
            )

            if matched:
                strengths.append(char)

        if not strengths:
            strengths = ["Program is making progress toward formal BCM capability"]

        return strengths

    def _estimate_advancement_time(
        self,
        current_level: int,
        gaps: List[str]
    ) -> int:
        """Estimate months to next level"""

        if current_level >= 5 or not gaps:
            return 0

        # Base time by level transition
        base_months = {
            1: 6,   # 1 -> 2
            2: 9,   # 2 -> 3
            3: 12,  # 3 -> 4
            4: 18   # 4 -> 5
        }

        base = base_months.get(current_level, 12)

        # Adjust for number of gaps
        gap_adjustment = len(gaps) * 1.5  # 1.5 months per gap

        total = base + gap_adjustment

        return round(total)
