"""
Case Library Search Tool

Tool for searching and retrieving relevant case studies and best practices.
Used by all expert agents to provide real-world examples.
"""

from typing import Dict, Any, List, Optional
from .base_tool import BaseTool
import logging

logger = logging.getLogger(__name__)


class CaseSearchTool(BaseTool):
    """
    Case Library Search Tool

    Searches case library for relevant examples based on:
    - Industry similarity
    - Organization size
    - Challenge type
    - Module/phase
    - Success factors
    """

    def __init__(self, case_library=None, db_session=None):
        super().__init__(
            name="case_search",
            description="Search case library for relevant examples and best practices",
            parameters={
                "query": {
                    "type": "string",
                    "description": "Search query describing the challenge or topic"
                },
                "industry": {
                    "type": "string",
                    "description": "Industry to filter cases (optional)"
                },
                "org_size": {
                    "type": "string",
                    "description": "Organization size filter: 'small', 'medium', 'large' (optional)"
                },
                "module": {
                    "type": "string",
                    "description": "BCM module filter: 'BIA', 'Strategy', 'Planning', 'Testing' (optional)"
                },
                "success_only": {
                    "type": "boolean",
                    "description": "Return only successful cases (default: false)"
                },
                "max_results": {
                    "type": "integer",
                    "description": "Maximum number of results to return (default: 5)"
                }
            },
            required_params=["query"]
        )
        self.case_library = case_library
        self.db_session = db_session

        # Mock case library for development
        self.mock_cases = self._initialize_mock_cases()

    def _initialize_mock_cases(self) -> List[Dict[str, Any]]:
        """Initialize mock case library"""

        return [
            {
                "id": "CASE-001",
                "title": "Healthcare Provider BIA Implementation",
                "industry": "healthcare",
                "org_size": "medium",
                "module": "BIA",
                "success": True,
                "summary": "Regional healthcare provider successfully implemented BIA identifying 15 critical processes with defined RTO/RPO objectives.",
                "key_challenge": "Balancing patient care priorities with operational continuity",
                "solution": "Categorized processes into patient-critical, operational-critical, and administrative. Patient-critical processes received RTO of 4 hours.",
                "outcome": "Comprehensive BIA completed in 6 weeks. Successfully used during COVID-19 response.",
                "lessons_learned": [
                    "Involve clinical staff early in BIA process",
                    "Use patient impact as primary criticality criterion",
                    "Document regulatory requirements for each process"
                ],
                "metrics": {
                    "timeline_weeks": 6,
                    "processes_analyzed": 15,
                    "stakeholders_engaged": 25
                }
            },
            {
                "id": "CASE-002",
                "title": "Financial Services ISO 22301 Certification",
                "industry": "finance",
                "org_size": "large",
                "module": "full-iso22301",
                "success": True,
                "summary": "Investment firm achieved ISO 22301 certification covering 500+ employees across 3 sites.",
                "key_challenge": "Complex regulatory environment and multiple interconnected systems",
                "solution": "Phased approach: BIA first quarter, Strategy second quarter, Implementation/Testing third quarter, Certification fourth quarter.",
                "outcome": "ISO 22301 certification achieved. No critical audit findings.",
                "lessons_learned": [
                    "Engage compliance team from start",
                    "Map BCM to existing GRC framework",
                    "Conduct internal audit before external certification"
                ],
                "metrics": {
                    "timeline_weeks": 48,
                    "investment_usd": 280000,
                    "processes_covered": 42
                }
            },
            {
                "id": "CASE-003",
                "title": "Manufacturing Recovery Strategy Development",
                "industry": "manufacturing",
                "org_size": "medium",
                "module": "Strategy",
                "success": True,
                "summary": "Automotive parts manufacturer developed recovery strategies for supply chain disruption.",
                "key_challenge": "Single-source suppliers for critical components",
                "solution": "Multi-tier supplier redundancy, safety stock optimization, and alternate production sites identified.",
                "outcome": "Reduced supply chain vulnerability by 60%. Successfully navigated chip shortage.",
                "lessons_learned": [
                    "Map entire supply chain, not just Tier 1",
                    "Build relationships with alternate suppliers proactively",
                    "Balance inventory costs against disruption risk"
                ],
                "metrics": {
                    "timeline_weeks": 10,
                    "suppliers_evaluated": 150,
                    "alternate_sources_identified": 32
                }
            },
            {
                "id": "CASE-004",
                "title": "Small Business BC Plan Development",
                "industry": "retail",
                "org_size": "small",
                "module": "Planning",
                "success": True,
                "summary": "Small retail chain (8 stores) developed practical BC plans on limited budget.",
                "key_challenge": "Limited resources and BCM expertise",
                "solution": "Leveraged templates, focused on top 5 critical processes, used tabletop exercises instead of full simulations.",
                "outcome": "Usable BC plans completed in 8 weeks for $12,000 total cost.",
                "lessons_learned": [
                    "Templates and frameworks accelerate development",
                    "Focus on essential processes first",
                    "Tabletop exercises provide good value for small organizations"
                ],
                "metrics": {
                    "timeline_weeks": 8,
                    "investment_usd": 12000,
                    "critical_processes": 5
                }
            },
            {
                "id": "CASE-005",
                "title": "Technology Company Crisis Response Testing",
                "industry": "technology",
                "org_size": "large",
                "module": "Testing",
                "success": True,
                "summary": "SaaS provider conducted comprehensive BC testing program including cyber incident scenario.",
                "key_challenge": "Testing without disrupting 24/7 customer operations",
                "solution": "Phased testing: desk exercises, component tests, then full rehearsal during maintenance window.",
                "outcome": "Identified 12 plan improvements. 95% of recovery objectives met in full test.",
                "lessons_learned": [
                    "Test with actual staff who would respond",
                    "Include communications testing in all scenarios",
                    "Document gaps immediately while fresh"
                ],
                "metrics": {
                    "timeline_weeks": 12,
                    "tests_conducted": 8,
                    "participants": 45,
                    "improvements_identified": 12
                }
            },
            {
                "id": "CASE-006",
                "title": "Healthcare Pandemic Response Plan",
                "industry": "healthcare",
                "org_size": "large",
                "module": "Planning",
                "success": True,
                "summary": "Hospital system successfully activated pandemic response plan during COVID-19.",
                "key_challenge": "Unprecedented scale and duration of disruption",
                "solution": "Flexible plan allowing for extended activation, clear decision framework for resource allocation.",
                "outcome": "Maintained critical care throughout pandemic. Plan activated for 18+ months.",
                "lessons_learned": [
                    "Plan for extended disruptions, not just short-term",
                    "Build flexibility into plans",
                    "Regular plan reviews during extended activation"
                ],
                "metrics": {
                    "activation_duration_months": 18,
                    "plan_updates": 6,
                    "critical_services_maintained": "100%"
                }
            },
            {
                "id": "CASE-007",
                "title": "Financial Services Dependency Mapping",
                "industry": "finance",
                "org_size": "medium",
                "module": "BIA",
                "success": True,
                "summary": "Credit union mapped complex dependencies across digital banking platform.",
                "key_challenge": "Interconnected systems with cascading failure potential",
                "solution": "Visual dependency mapping workshops with IT and business stakeholders. Used process flow diagrams.",
                "outcome": "Identified 8 single points of failure. Implemented redundancy for top 5.",
                "lessons_learned": [
                    "Visual tools improve stakeholder understanding",
                    "Include IT architecture team in BIA",
                    "Test assumptions about dependencies"
                ],
                "metrics": {
                    "dependencies_mapped": 125,
                    "single_points_of_failure": 8,
                    "redundancy_implemented": 5
                }
            },
            {
                "id": "CASE-008",
                "title": "Retail Supply Chain Risk Assessment",
                "industry": "retail",
                "org_size": "medium",
                "module": "BIA",
                "success": False,
                "summary": "Retail chain conducted BIA but failed to account for just-in-time inventory dependencies.",
                "key_challenge": "Underestimated vulnerability of JIT supply chain",
                "solution_attempted": "Standard BIA focused on internal processes, didn't deep-dive on suppliers.",
                "outcome": "BIA completed but missed critical supply chain risks. Faced stockouts during disruption.",
                "lessons_learned": [
                    "Extend BIA beyond organizational boundaries",
                    "Analyze supplier dependencies in detail",
                    "Consider geographic concentration risk"
                ],
                "improvement_actions": [
                    "Conducted supplementary supply chain risk assessment",
                    "Diversified supplier base",
                    "Increased safety stock for critical items"
                ]
            },
            {
                "id": "CASE-009",
                "title": "Tech Startup Rapid BC Implementation",
                "industry": "technology",
                "org_size": "small",
                "module": "full-iso22301",
                "success": True,
                "summary": "Fast-growing startup implemented BC program in 12 weeks to meet customer requirements.",
                "key_challenge": "Speed requirement while maintaining quality and limited internal resources",
                "solution": "Used consultant for framework and methodology, internal team for execution. Focused on cloud-native resilience.",
                "outcome": "BC program operational in 12 weeks. Won enterprise contracts requiring BC certification.",
                "lessons_learned": [
                    "Strategic consultant engagement accelerates timelines",
                    "Cloud services simplify BC implementation",
                    "BC capability is competitive advantage"
                ],
                "metrics": {
                    "timeline_weeks": 12,
                    "investment_usd": 45000,
                    "consultant_days": 15
                }
            },
            {
                "id": "CASE-010",
                "title": "Manufacturing Facility Relocation BC Strategy",
                "industry": "manufacturing",
                "org_size": "large",
                "module": "Strategy",
                "success": True,
                "summary": "Manufacturer developed BC strategy for planned facility relocation without production interruption.",
                "key_challenge": "Maintaining production during 6-month phased relocation",
                "solution": "Parallel operations strategy with gradual cutover. Detailed dependency mapping and sequencing plan.",
                "outcome": "Zero lost production days during relocation. On-time, on-budget completion.",
                "lessons_learned": [
                    "BC planning applicable to change management",
                    "Detailed sequencing critical for complex transitions",
                    "Test in small batches before full cutover"
                ],
                "metrics": {
                    "planning_weeks": 16,
                    "relocation_duration_months": 6,
                    "production_lost_days": 0
                }
            }
        ]

    async def execute(
        self,
        query: str,
        industry: Optional[str] = None,
        org_size: Optional[str] = None,
        module: Optional[str] = None,
        success_only: bool = False,
        max_results: int = 5
    ) -> Dict[str, Any]:
        """
        Execute case search

        Returns:
            Relevant cases with similarity scores and key insights
        """

        # Use real case library if available, otherwise use mock
        if self.case_library:
            cases = await self._search_real_library(
                query, industry, org_size, module, success_only
            )
        else:
            cases = self._search_mock_library(
                query, industry, org_size, module, success_only
            )

        # Limit results
        cases = cases[:max_results]

        # Extract insights
        insights = self._extract_insights(cases)

        result = {
            "query": query,
            "filters": {
                "industry": industry,
                "org_size": org_size,
                "module": module,
                "success_only": success_only
            },
            "total_results": len(cases),
            "cases": cases,
            "key_insights": insights,
            "common_success_factors": self._identify_success_factors(cases),
            "common_pitfalls": self._identify_pitfalls(cases)
        }

        await self._publish_event('case.search.completed', {
            'query': query,
            'results_count': len(cases)
        })

        return result

    async def _search_real_library(
        self,
        query: str,
        industry: Optional[str],
        org_size: Optional[str],
        module: Optional[str],
        success_only: bool
    ) -> List[Dict[str, Any]]:
        """Search real case library (database or API)"""

        # TODO: Implement real search using database or vector similarity
        # This would use embeddings for semantic search

        # Placeholder: return empty for now
        logger.warning("Real case library not implemented, using mock data")
        return self._search_mock_library(query, industry, org_size, module, success_only)

    def _search_mock_library(
        self,
        query: str,
        industry: Optional[str],
        org_size: Optional[str],
        module: Optional[str],
        success_only: bool
    ) -> List[Dict[str, Any]]:
        """Search mock case library"""

        results = []
        query_lower = query.lower()

        for case in self.mock_cases:
            # Apply filters
            if industry and case.get("industry") != industry.lower():
                continue

            if org_size and case.get("org_size") != org_size.lower():
                continue

            if module:
                case_module = case.get("module", "")
                if module.lower() not in case_module.lower():
                    continue

            if success_only and not case.get("success", False):
                continue

            # Calculate relevance score (simple keyword matching)
            relevance_score = self._calculate_relevance(case, query_lower)

            if relevance_score > 0:
                case_with_score = case.copy()
                case_with_score["relevance_score"] = relevance_score
                results.append(case_with_score)

        # Sort by relevance
        results.sort(key=lambda x: x["relevance_score"], reverse=True)

        return results

    def _calculate_relevance(self, case: Dict[str, Any], query: str) -> float:
        """Calculate relevance score"""

        score = 0.0

        # Check title
        if any(word in case.get("title", "").lower() for word in query.split()):
            score += 3.0

        # Check summary
        if any(word in case.get("summary", "").lower() for word in query.split()):
            score += 2.0

        # Check key challenge
        if any(word in case.get("key_challenge", "").lower() for word in query.split()):
            score += 2.5

        # Check solution
        solution = case.get("solution", "") or case.get("solution_attempted", "")
        if any(word in solution.lower() for word in query.split()):
            score += 2.0

        # Check lessons learned
        lessons = case.get("lessons_learned", [])
        for lesson in lessons:
            if any(word in lesson.lower() for word in query.split()):
                score += 1.0

        return score

    def _extract_insights(self, cases: List[Dict[str, Any]]) -> List[str]:
        """Extract key insights from cases"""

        if not cases:
            return ["No relevant cases found. Consider broadening search criteria."]

        insights = []

        # Timeline insights
        timelines = [
            c.get("metrics", {}).get("timeline_weeks")
            for c in cases
            if c.get("metrics", {}).get("timeline_weeks")
        ]

        if timelines:
            avg_timeline = sum(timelines) / len(timelines)
            insights.append(
                f"Similar organizations completed this in {round(avg_timeline, 1)} weeks on average"
            )

        # Investment insights
        investments = [
            c.get("metrics", {}).get("investment_usd")
            for c in cases
            if c.get("metrics", {}).get("investment_usd")
        ]

        if investments:
            avg_investment = sum(investments) / len(investments)
            insights.append(
                f"Average investment for similar scope: ${round(avg_investment, 0):,}"
            )

        # Success rate
        successful = sum(1 for c in cases if c.get("success", False))
        if cases:
            success_rate = (successful / len(cases)) * 100
            insights.append(f"Success rate for similar initiatives: {round(success_rate)}%")

        return insights

    def _identify_success_factors(self, cases: List[Dict[str, Any]]) -> List[str]:
        """Identify common success factors"""

        successful_cases = [c for c in cases if c.get("success", False)]

        if not successful_cases:
            return []

        # Extract all lessons learned from successful cases
        all_lessons = []
        for case in successful_cases:
            lessons = case.get("lessons_learned", [])
            all_lessons.extend(lessons)

        # Find common themes (simplified - just return first few)
        return all_lessons[:3] if all_lessons else []

    def _identify_pitfalls(self, cases: List[Dict[str, Any]]) -> List[str]:
        """Identify common pitfalls from failed cases"""

        failed_cases = [c for c in cases if not c.get("success", False)]

        if not failed_cases:
            return []

        pitfalls = []

        for case in failed_cases:
            # Extract lessons from failures
            lessons = case.get("lessons_learned", [])
            pitfalls.extend(lessons)

            # Extract improvement actions
            improvements = case.get("improvement_actions", [])
            pitfalls.extend(improvements)

        return pitfalls[:3] if pitfalls else []


class BestPracticeLibraryTool(BaseTool):
    """
    Best Practice Library Tool

    Retrieves best practices and guidelines for specific BCM topics.
    """

    def __init__(self, db_session=None):
        super().__init__(
            name="best_practice_library",
            description="Retrieve best practices and guidelines for BCM topics",
            parameters={
                "topic": {
                    "type": "string",
                    "description": "BCM topic (e.g., 'BIA', 'testing', 'communication', 'recovery')"
                },
                "industry_specific": {
                    "type": "boolean",
                    "description": "Return industry-specific practices (default: false)"
                },
                "industry": {
                    "type": "string",
                    "description": "Industry for industry-specific practices"
                }
            },
            required_params=["topic"]
        )
        self.db_session = db_session

        # Best practices library
        self.best_practices = self._initialize_best_practices()

    def _initialize_best_practices(self) -> Dict[str, List[str]]:
        """Initialize best practices library"""

        return {
            "bia": [
                "Engage business process owners directly - they understand true criticality",
                "Use consistent impact categories (financial, operational, reputational, regulatory)",
                "Document dependencies comprehensively - they're often underestimated",
                "Define RTO/RPO based on impact thresholds, not arbitrary numbers",
                "Review and validate BIA annually or after significant changes",
                "Consider seasonal variations in criticality",
                "Map dependencies beyond first tier - cascading impacts matter"
            ],
            "testing": [
                "Test with the people who would actually respond, not just managers",
                "Start with tabletop exercises before full simulations",
                "Test one scenario thoroughly rather than many superficially",
                "Document lessons learned immediately after test",
                "Include communications in every test scenario",
                "Test at different times of day/week to validate availability assumptions",
                "Make testing educational, not punitive"
            ],
            "communication": [
                "Establish clear escalation criteria and notification triggers",
                "Prepare message templates in advance for common scenarios",
                "Test notification systems regularly (quarterly minimum)",
                "Have backup communication channels identified",
                "Define communication roles clearly (who says what to whom)",
                "Consider stakeholder-specific needs (employees, customers, regulators)",
                "Practice crisis communication before you need it"
            ],
            "recovery": [
                "Prioritize critical processes based on BIA findings",
                "Document recovery procedures step-by-step",
                "Identify required resources (people, systems, facilities) explicitly",
                "Define recovery success criteria and validation steps",
                "Build in flexibility - plans never execute exactly as written",
                "Consider manual workarounds for technology dependencies",
                "Test recovery procedures to validate feasibility"
            ],
            "strategy": [
                "Develop multiple options for each critical process",
                "Balance cost against risk reduction",
                "Consider recovery time requirements when evaluating options",
                "Involve finance in strategy evaluation (cost-benefit analysis)",
                "Don't overlook simple solutions - they're often most reliable",
                "Build strategies that address most likely scenarios first",
                "Document strategy decisions and rationale for future reference"
            ],
            "governance": [
                "Secure executive sponsorship - BC needs leadership support",
                "Define clear roles and responsibilities (RACI matrix helpful)",
                "Establish regular BC steering committee meetings",
                "Integrate BC into enterprise risk management",
                "Set measurable BC objectives aligned with business goals",
                "Report BC program status regularly to leadership",
                "Allocate appropriate budget and resources"
            ]
        }

    async def execute(
        self,
        topic: str,
        industry_specific: bool = False,
        industry: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Execute best practice retrieval

        Returns:
            Relevant best practices for the topic
        """

        topic_lower = topic.lower()

        # Find matching topic
        practices = []
        matched_topic = None

        for key, values in self.best_practices.items():
            if key in topic_lower or topic_lower in key:
                practices = values
                matched_topic = key
                break

        if not practices:
            # Return general practices
            practices = [
                "Follow ISO 22301 standard for comprehensive BCM framework",
                "Engage stakeholders throughout the BCM lifecycle",
                "Document decisions and maintain evidence",
                "Test plans regularly and update based on findings",
                "Integrate BC with business operations, not separate program"
            ]
            matched_topic = "general"

        # Add industry-specific practices if requested
        industry_practices = []
        if industry_specific and industry:
            industry_practices = self._get_industry_practices(matched_topic, industry)

        result = {
            "topic": topic,
            "matched_topic": matched_topic,
            "best_practices": practices,
            "industry_specific_practices": industry_practices if industry_specific else None,
            "sources": [
                "ISO 22301:2019",
                "BCI Good Practice Guidelines",
                "NIST SP 800-34",
                "Real-world case studies"
            ]
        }

        await self._publish_event('best.practice.retrieved', {
            'topic': topic,
            'practices_count': len(practices)
        })

        return result

    def _get_industry_practices(self, topic: str, industry: str) -> List[str]:
        """Get industry-specific practices"""

        industry_specifics = {
            "healthcare": {
                "bia": [
                    "Prioritize patient care continuity above all else",
                    "Consider HIPAA compliance in recovery strategies",
                    "Account for medical equipment dependencies"
                ],
                "recovery": [
                    "Maintain patient safety protocols during disruption",
                    "Coordinate with public health authorities",
                    "Ensure medication and supply availability"
                ]
            },
            "finance": {
                "bia": [
                    "Consider regulatory reporting deadlines",
                    "Map transaction processing dependencies",
                    "Account for market hours and trading windows"
                ],
                "recovery": [
                    "Maintain regulatory compliance during disruption",
                    "Ensure secure access to financial systems",
                    "Coordinate with regulatory bodies"
                ]
            },
            "manufacturing": {
                "bia": [
                    "Map supply chain dependencies in detail",
                    "Consider production line interdependencies",
                    "Account for inventory and JIT manufacturing"
                ],
                "recovery": [
                    "Identify alternate production sites",
                    "Maintain supplier relationships",
                    "Consider safety stock strategies"
                ]
            }
        }

        industry_data = industry_specifics.get(industry.lower(), {})
        return industry_data.get(topic, [])
