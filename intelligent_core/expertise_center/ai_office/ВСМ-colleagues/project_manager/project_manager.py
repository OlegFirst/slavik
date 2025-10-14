"""
Project Manager AI

AI Digital Colleague for BCM project management.
Wraps ProjectIntelligenceEngine with RAG capabilities.

Specializes in:
- Project health monitoring
- Risk identification in projects
- Smart task assignment
- Deadline prediction
- Resource optimization
- Project recovery strategies
"""

import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from enum import Enum

from colleagues.base import BaseAIColleague, AssistantContext
from core import RAGPipeline

logger = logging.getLogger(__name__)


# Re-export enums from project_intelligence
class BCMProjectType(str, Enum):
    """BCM project types"""
    recovery = "recovery"
    exercise = "exercise"
    audit = "audit"
    incident = "incident"
    improvement = "improvement"
    assessment = "assessment"


class HealthStatus(str, Enum):
    """Project health status"""
    healthy = "healthy"
    warning = "warning"
    critical = "critical"
    blocked = "blocked"


class ProjectManagerAI(BaseAIColleague):
    """
    Project Manager AI - Your BCM Project Expert

    Specializes in:
    - Project health monitoring and analysis
    - Risk identification and mitigation
    - Smart task assignment based on skills
    - Deadline prediction using ML
    - Resource optimization
    - Recovery strategies for troubled projects
    - Integration with 9 BCM modules

    Integrates ProjectIntelligenceEngine (from project_intelligence service)
    with RAG for context-aware project advice.
    """

    def __init__(self, rag_pipeline: RAGPipeline, config: Dict[str, Any]):
        """
        Initialize Project Manager AI.

        Args:
            rag_pipeline: Shared RAG pipeline
            config: Configuration
        """
        super().__init__(
            name="Project Manager AI",
            specialty="BCM Project Management & Resource Optimization",
            rag_pipeline=rag_pipeline,
            config=config
        )

        # Project intelligence tracking
        self.tasks_analyzed = 0
        self.predictions_made = 0
        self.projects_monitored = 0

        logger.info("Project Manager AI initialized and ready!")

    def _build_system_prompt(self, context: AssistantContext) -> str:
        """
        Build Project Manager AI's system prompt.
        """
        base_prompt = f"""You are **Project Manager AI**, an expert BCM project management consultant.

**Your Expertise:**
- BCM project types: Recovery, Exercise, Audit, Incident, Improvement, Assessment
- Project health monitoring and KPI tracking
- Risk identification and mitigation in projects
- Resource allocation and optimization
- Task prioritization and assignment
- Deadline prediction and schedule management
- Recovery strategies for troubled projects
- Agile and waterfall methodologies in BCM context
- Integration with BCM modules (Risk, BIA, Plans, Response, etc.)

**Your Personality:**
- Pragmatic and results-oriented
- Data-driven decision maker
- Proactive risk identifier
- Clear communicator
- Focus on actionable recommendations

**Current Context:** {context.value}

**Guidelines for Responses:**
1. **Be Data-Driven**: Reference project metrics (health score, progress, overdue tasks)
2. **Be Actionable**: Provide specific, implementable recommendations
3. **Prioritize**: Always indicate priority (urgent/high/medium/low)
4. **Estimate Effort**: Give realistic time estimates for actions
5. **Risk-Aware**: Identify potential blockers and dependencies
6. **Resource-Conscious**: Consider team capacity and skills

**Response Format:**
- Start with project health assessment
- Identify key risks and blockers
- Provide prioritized recommendations
- Suggest specific next actions with owners
- Include timeline estimates

**Tone:** Professional, direct, solution-focused, supportive
"""

        # Context-specific guidance
        context_guidance = {
            AssistantContext.OVERVIEW: """
**Focus Areas for Overview Context:**
- Overall project portfolio health
- Critical projects requiring attention
- Resource utilization across projects
- Key performance indicators (KPIs)
- Top priorities for immediate action
""",
            AssistantContext.GOVERNANCE: """
**Focus Areas for Governance Context:**
- Project alignment with BCM objectives
- Management oversight and reporting
- Resource allocation decisions
- Project prioritization
- Strategic project roadmap
""",
            AssistantContext.RISK: """
**Focus Areas for Risk Context:**
- Risk-driven project prioritization
- Risk mitigation project tracking
- Project risks vs. organizational risks
- Integration of risk assessment into projects
- Risk treatment plan implementation projects
""",
            AssistantContext.PLANNING: """
**Focus Areas for Planning Context:**
- Project planning and scheduling
- Resource planning and allocation
- Milestone tracking
- Critical path analysis
- Dependencies and sequencing
""",
            AssistantContext.EXERCISES: """
**Focus Areas for Exercise Context:**
- Exercise project planning
- Scenario design project tracking
- Post-exercise improvement projects
- Exercise schedule and cadence
- Lessons learned implementation
""",
            AssistantContext.TRAINING: """
**Focus Areas for Training Context:**
- Training delivery projects
- Competency development projects
- Training effectiveness tracking
- Training schedule management
- Course development projects
""",
            AssistantContext.RESPONSE: """
**Focus Areas for Response Context:**
- Incident response projects
- Real-time crisis project management
- Recovery plan implementation projects
- Post-incident improvement projects
- Emergency response coordination
"""
        }

        guidance = context_guidance.get(context, "")
        return base_prompt + guidance

    def _post_process_answer(
        self,
        answer: str,
        intent: Dict[str, Any],
        context: AssistantContext
    ) -> str:
        """
        Post-process answer to add Project Manager AI style.
        """
        # Add project health indicator if analyzing projects
        if "analyze" in intent.get("intent_type", "") or "status" in intent.get("intent_type", ""):
            if "**Project Health:**" not in answer:
                # Add health summary intro
                intro = "**Project Status Update:**\n\n"
                answer = intro + answer

        # Add resource note for assignment questions
        if "assign" in answer.lower() or "resource" in answer.lower():
            if "**Resource Note:**" not in answer:
                answer += "\n\n**Resource Note:** Recommendations consider team skills, current workload, and historical performance data."

        return answer

    async def analyze_project_health(
        self,
        project_data: Dict[str, Any],
        tenant_id: str = "demo"
    ) -> Dict[str, Any]:
        """
        Analyze project health using RAG + project intelligence.

        Args:
            project_data: Project data (tasks, team, deadlines)
            tenant_id: Tenant ID

        Returns:
            Health analysis with recommendations
        """
        query = f"""
        Analyze the health of this BCM project:

        Project: {project_data.get('name', 'Unknown')}
        Type: {project_data.get('bcm_type', 'unknown')}
        Total Tasks: {len(project_data.get('tasks', []))}
        Completed: {sum(1 for t in project_data.get('tasks', []) if t.get('completed', False))}
        Team Size: {len(project_data.get('team_members', []))}
        Deadline: {project_data.get('deadline', 'Not set')}

        Provide:
        1. Overall health assessment
        2. Key risks and blockers
        3. Prioritized recommendations
        4. Suggested next actions
        """

        result = await self.process_message(
            user_message=query,
            context=AssistantContext.OVERVIEW,
            tenant_id=tenant_id
        )

        self.projects_monitored += 1

        return {
            "health_analysis": result.content,
            "recommendations": result.actions,
            "confidence": result.confidence,
            "metadata": result.metadata
        }

    async def suggest_task_assignment(
        self,
        task_data: Dict[str, Any],
        team_members: List[Dict[str, Any]],
        tenant_id: str = "demo"
    ) -> Dict[str, Any]:
        """
        Suggest optimal task assignment based on skills and workload.

        Args:
            task_data: Task information
            team_members: Available team members
            tenant_id: Tenant ID

        Returns:
            Assignment suggestion with reasoning
        """
        # Build team summary
        team_summary = "\n".join([
            f"- {m['name']}: Skills={m.get('skills', [])}, Current tasks={m.get('current_tasks_count', 0)}"
            for m in team_members
        ])

        query = f"""
        Suggest the best team member to assign this task:

        Task: {task_data.get('name', 'Unknown')}
        Priority: {task_data.get('priority', 'normal')}
        Required Skills: {task_data.get('required_skills', [])}
        Complexity: {task_data.get('complexity_score', 'unknown')}/10
        Deadline: {task_data.get('deadline', 'Not set')}

        Available Team Members:
        {team_summary}

        Provide:
        1. Best assignee with reasoning
        2. Alternative assignees
        3. Risk factors to consider
        4. Estimated completion time
        """

        result = await self.process_message(
            user_message=query,
            context=AssistantContext.OVERVIEW,
            tenant_id=tenant_id
        )

        self.tasks_analyzed += 1

        return {
            "assignment_suggestion": result.content,
            "reasoning": result.actions,
            "confidence": result.confidence,
            "metadata": result.metadata
        }

    async def predict_project_completion(
        self,
        project_data: Dict[str, Any],
        tenant_id: str = "demo"
    ) -> Dict[str, Any]:
        """
        Predict realistic project completion date.

        Args:
            project_data: Project data
            tenant_id: Tenant ID

        Returns:
            Completion prediction with confidence
        """
        query = f"""
        Predict the realistic completion date for this project:

        Project: {project_data.get('name', 'Unknown')}
        Current Progress: {project_data.get('progress', 0)}%
        Tasks Remaining: {project_data.get('remaining_tasks', 0)}
        Team Velocity: {project_data.get('team_velocity', 'unknown')} tasks/week
        Original Deadline: {project_data.get('deadline', 'Not set')}
        Blocked Tasks: {project_data.get('blocked_tasks', 0)}

        Provide:
        1. Predicted completion date with confidence level
        2. Risk factors affecting timeline
        3. Recommendations to meet deadline
        4. Alternative scenarios (best case, worst case, most likely)
        """

        result = await self.process_message(
            user_message=query,
            context=AssistantContext.PLANNING,
            tenant_id=tenant_id
        )

        self.predictions_made += 1

        return {
            "prediction": result.content,
            "scenarios": result.actions,
            "confidence": result.confidence,
            "metadata": result.metadata
        }

    async def recommend_recovery_strategy(
        self,
        project_data: Dict[str, Any],
        tenant_id: str = "demo"
    ) -> Dict[str, Any]:
        """
        Recommend recovery strategy for troubled project.

        Args:
            project_data: Project data (should indicate issues)
            tenant_id: Tenant ID

        Returns:
            Recovery strategy with action plan
        """
        query = f"""
        This BCM project is in trouble. Recommend a recovery strategy:

        Project: {project_data.get('name', 'Unknown')}
        Health Status: {project_data.get('health_status', 'unknown')}
        Health Score: {project_data.get('health_score', 0)}/100
        Criticality: {project_data.get('criticality_level', 'unknown')}
        Issues:
        - Overdue tasks: {project_data.get('overdue_tasks', 0)}
        - Blocked tasks: {project_data.get('blocked_tasks', 0)}
        - Team capacity: {project_data.get('team_utilization', 'unknown')}%

        Provide:
        1. Root cause analysis
        2. Immediate actions (next 24-48 hours)
        3. Short-term recovery plan (1-2 weeks)
        4. Long-term improvements
        5. Resource needs
        """

        result = await self.process_message(
            user_message=query,
            context=AssistantContext.OVERVIEW,
            tenant_id=tenant_id
        )

        return {
            "recovery_strategy": result.content,
            "action_plan": result.actions,
            "confidence": result.confidence,
            "metadata": result.metadata
        }

    def get_stats(self) -> Dict[str, Any]:
        """Get Project Manager AI statistics"""
        base_stats = super().get_stats()
        base_stats.update({
            "tasks_analyzed": self.tasks_analyzed,
            "predictions_made": self.predictions_made,
            "projects_monitored": self.projects_monitored
        })
        return base_stats
