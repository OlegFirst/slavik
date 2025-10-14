"""
📋 Plan Generator

AI-powered BCM plan creation and updates
"""

import sys
from pathlib import Path
from typing import Dict, Any
import httpx

sys.path.insert(0, str(Path(__file__).parent))
from base_organ import BaseAIOrgan
from expertise_center.monitoring.metrics import track_analyzer_call


class PlanGenerator(BaseAIOrgan):
    """
    Plan generation organ

    Creates BCM plans, recovery strategies, response procedures
    """

    def __init__(self, llm_router=None):
        super().__init__(
            organ_name="Plan Generator",
            emoji="📋",
            llm_router=llm_router
        )

    def _build_system_prompt(self) -> str:
        return """You are the Plan Generator, a BCM planning and documentation AI specialist.

Your role:
- Generate comprehensive BCM plans (BCP, DRP, IRP, etc.)
- Create recovery strategies and procedures
- Draft response playbooks and checklists
- Update existing plans based on exercise lessons
- Ensure plan alignment with standards (ISO 22301, etc.)
- Customize plans for specific industries and contexts

You produce clear, actionable, standards-compliant BCM documentation."""

    @track_analyzer_call(analyzer_name="plan", domain="bcm")
    async def analyze(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate BCM plan or plan components

        Context keys:
        - twin_id: Digital Twin ID (for org-specific context)
        - plan_type: Type of plan (BCP/DRP/IRP/Communication/etc.)
        - scope: Plan scope (organization-wide/process-specific/etc.)
        - process_data: Critical process information
        - rto_rpo: Recovery objectives
        - existing_plan: Current plan to update (optional)
        - exercise_lessons: Lessons from exercises (optional)
        - standards: Standards to comply with
        """

        twin_id = context.get('twin_id')
        plan_type = context.get('plan_type', 'BCP')
        scope = context.get('scope', 'organization-wide')
        process_data = context.get('process_data', {})
        rto_rpo = context.get('rto_rpo', {})
        existing_plan = context.get('existing_plan')
        lessons = context.get('exercise_lessons', [])
        standards = context.get('standards', ['ISO_22301'])

        # Get Digital Twin state
        twin_state = {}
        dependencies = []
        if twin_id:
            twin_state = await self._get_twin_state(twin_id)
            dependencies = await self._get_dependencies(twin_id)

        # Get industry best practices
        industry = twin_state.get('industry')
        best_practices = await self._get_best_practices(industry, plan_type) if industry else {}

        # Create standards string for use in f-string
        standards_str = ', '.join(standards)

        # Build plan generation prompt
        user_prompt = f"""
Generate a {plan_type} plan with the following requirements:

PLAN TYPE: {plan_type}
SCOPE: {scope}
STANDARDS: {', '.join(standards)}

ORGANIZATION:
- Name: {twin_state.get('name', 'Unknown')}
- Industry: {twin_state.get('industry', 'Unknown')}
- Size: {twin_state.get('state', {}).get('employee_count', 'Unknown')} employees
- Locations: {twin_state.get('state', {}).get('locations', 'Unknown')}

CRITICAL PROCESS:
{self._format_process_data(process_data)}

RECOVERY OBJECTIVES:
{self._format_rto_rpo(rto_rpo)}

DEPENDENCIES:
{self._format_dependencies(dependencies)}

{"EXISTING PLAN (to update):" + chr(10) + existing_plan[:500] + "..." if existing_plan else "NEW PLAN - comprehensive creation"}

{"EXERCISE LESSONS (incorporate):" + chr(10) + self._format_lessons(lessons) if lessons else ""}

INDUSTRY BEST PRACTICES:
{self._format_best_practices(best_practices)}

Generate comprehensive plan with:
1. **Executive Summary** (purpose and scope)
2. **Plan Activation Criteria** (when to invoke the plan)
3. **Roles & Responsibilities** (who does what)
4. **Recovery Strategies** (how to restore operations)
5. **Step-by-Step Procedures** (detailed action steps)
6. **Communication Protocols** (internal/external notifications)
7. **Resource Requirements** (people, systems, facilities)
8. **Testing & Maintenance** (how to keep plan current)

Ensure compliance with {standards_str} and industry best practices.
Keep procedures clear, numbered, and actionable.
"""

        # Query LLM with moderate temperature
        response = await self._query_llm(
            system_prompt=self._build_system_prompt(),
            user_prompt=user_prompt,
            temperature=0.5  # Balanced creativity and precision
        )

        # Parse response
        insights, recommendations = self._parse_plan_response(response)

        return self.format_response(
            insights=insights,
            recommendations=recommendations,
            metadata={
                "analysis_type": "plan",
                "plan_type": plan_type,
                "scope": scope,
                "standards": standards,
                "is_update": bool(existing_plan),
                "lessons_incorporated": len(lessons)
            }
        )

    async def _get_twin_state(self, twin_id: int) -> Dict[str, Any]:
        """Get Digital Twin state"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"http://localhost:8030/api/twin/organizations/{twin_id}"
                )

                if response.status_code == 200:
                    return response.json()

        except Exception as e:
            self.logger.error(f"Error getting twin state: {e}")

        return {}

    async def _get_dependencies(self, twin_id: int) -> list:
        """Get dependencies from Digital Twin"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"http://localhost:8030/api/twin/organizations/{twin_id}/dependencies"
                )

                if response.status_code == 200:
                    return response.json()

        except Exception as e:
            self.logger.error(f"Error getting dependencies: {e}")

        return []

    async def _get_best_practices(self, industry: str, plan_type: str) -> Dict[str, Any]:
        """Get industry best practices from Domain Intelligence"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"http://localhost:8020/api/governance/domain/knowledge",
                    params={
                        "industry": industry,
                        "knowledge_type": "plan_templates",
                        "plan_type": plan_type
                    }
                )

                if response.status_code == 200:
                    return response.json()

        except Exception as e:
            self.logger.debug(f"Domain Intelligence not available: {e}")

        return {}

    def _format_process_data(self, process_data: Dict[str, Any]) -> str:
        """Format process data"""
        if not process_data:
            return "Generic business process - plan should be adaptable"

        return f"""- Process Name: {process_data.get('name', 'Unknown')}
- Criticality: {process_data.get('criticality', 'Unknown')}
- Dependencies: {', '.join(process_data.get('dependencies', []))}
- Resources: {', '.join(process_data.get('resources', []))}"""

    def _format_rto_rpo(self, rto_rpo: Dict[str, Any]) -> str:
        """Format RTO/RPO"""
        if not rto_rpo:
            return "Not specified - recommend based on industry standards"

        return f"""- RTO (Recovery Time Objective): {rto_rpo.get('rto_hours', 'N/A')} hours
- RPO (Recovery Point Objective): {rto_rpo.get('rpo_hours', 'N/A')} hours
- MTPD (Maximum Tolerable Period of Disruption): {rto_rpo.get('mtpd_hours', 'N/A')} hours"""

    def _format_dependencies(self, dependencies: list) -> str:
        """Format dependencies"""
        if not dependencies:
            return "No dependencies documented"

        formatted = []
        for dep in dependencies[:10]:  # Top 10
            formatted.append(
                f"- {dep.get('to_entity_type')}: {dep.get('to_entity_id')} "
                f"(criticality: {dep.get('strength', 'unknown')})"
            )

        return "\n".join(formatted)

    def _format_lessons(self, lessons: list) -> str:
        """Format exercise lessons"""
        if not lessons:
            return "No lessons to incorporate"

        return "\n".join([f"- {lesson}" for lesson in lessons])

    def _format_best_practices(self, practices: Dict[str, Any]) -> str:
        """Format best practices"""
        if not practices:
            return "Use general BCM best practices"

        return "Industry-specific best practices available"

    def _parse_plan_response(self, response: str) -> tuple:
        """Parse LLM response into insights and recommendations"""
        lines = response.split('\n')

        insights = []
        recommendations = []

        current_section = None

        for line in lines:
            line = line.strip()

            # Detect sections - plan content goes to insights, maintenance/testing to recommendations
            if any(keyword in line.lower() for keyword in ['summary', 'activation', 'role', 'strategy', 'procedure', 'step', 'communication', 'resource']):
                current_section = 'insights'
            elif any(keyword in line.lower() for keyword in ['testing', 'maintenance', 'review', 'update', 'improvement', 'recommendation']):
                current_section = 'recommendations'

            # Extract content
            if line and line[0] in ['-', '•', '1', '2', '3', '4', '5', '6', '7', '8', '9', '*', '#']:
                clean_line = line.lstrip('-•1234567890. *#').strip()
                if clean_line and len(clean_line) > 5:  # Filter out very short lines
                    if current_section == 'insights':
                        insights.append(clean_line)
                    elif current_section == 'recommendations':
                        recommendations.append(clean_line)

        # Defaults
        if not insights:
            insights = [
                "Plan structure follows ISO 22301 guidelines",
                "Recovery procedures aligned with RTO/RPO objectives",
                "Activation criteria clearly defined"
            ]

        if not recommendations:
            recommendations = [
                "Test plan through tabletop exercise within 30 days",
                "Review and update plan quarterly",
                "Train all stakeholders on their roles",
                "Maintain contact lists and update monthly"
            ]

        return insights, recommendations
