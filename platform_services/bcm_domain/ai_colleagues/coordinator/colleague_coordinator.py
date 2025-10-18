"""
Colleague Coordinator - Routes queries to appropriate AI Colleagues

Automatically determines which AI Colleague should handle each query
and orchestrates cross-colleague workflows
"""

import logging
from typing import Dict, Any, Optional, List
from enum import Enum

from intelligent_core.ai_foundation import RAGPipeline
from platform_services.bcm_domain.ai_colleagues import (
    BaseAIColleague,
    ComplianceCopilot,
    ProjectManagerAI,
    RiskAnalystAI,
    BIASpecialistAI,
    PlanGeneratorAI,
    IncidentAdvisorAI,
    ExerciseDesignerAI,
    AssistantContext,
    AssistantMessage
)

logger = logging.getLogger(__name__)


class ColleagueType(str, Enum):
    """Types of AI Colleagues"""
    COMPLIANCE = "compliance_copilot"
    PROJECT_MANAGER = "project_manager"
    RISK_ANALYST = "risk_analyst"
    BIA_SPECIALIST = "bia_specialist"
    PLAN_GENERATOR = "plan_generator"
    INCIDENT_ADVISOR = "incident_advisor"
    EXERCISE_DESIGNER = "exercise_designer"
    AUTO = "auto"  # Auto-detect best colleague


class ColleagueCoordinator:
    """
    Coordinates queries between AI Colleagues

    Features:
    - Auto-routing based on intent analysis
    - Cross-colleague workflows (e.g., Risk → BIA → Plans)
    - EventBus integration for learning
    - Query delegation and aggregation
    """

    def __init__(self, rag_pipeline: RAGPipeline, colleagues: Dict[str, BaseAIColleague]):
        """
        Initialize coordinator

        Args:
            rag_pipeline: RAG Pipeline for intent analysis
            colleagues: Dictionary of initialized AI colleagues
        """
        self.rag = rag_pipeline
        self.colleagues = colleagues
        self.routing_stats = {
            "total_queries": 0,
            "auto_routed": 0,
            "manual_routed": 0,
            "workflows_executed": 0,
            "routing_accuracy": {}
        }

        # Intent to Colleague mapping
        self.intent_to_colleague = {
            # Compliance & Standards
            "query_compliance": ColleagueType.COMPLIANCE,
            "analyze_gap": ColleagueType.COMPLIANCE,
            "explain_standard": ColleagueType.COMPLIANCE,

            # Risk Management
            "analyze_risk": ColleagueType.RISK_ANALYST,
            "assess_threat": ColleagueType.RISK_ANALYST,
            "query_risk": ColleagueType.RISK_ANALYST,

            # Business Impact Analysis
            "analyze_bia": ColleagueType.BIA_SPECIALIST,
            "query_bia": ColleagueType.BIA_SPECIALIST,
            "assess_criticality": ColleagueType.BIA_SPECIALIST,

            # Plans & Recovery
            "create_plan": ColleagueType.PLAN_GENERATOR,
            "query_plan": ColleagueType.PLAN_GENERATOR,
            "generate_recovery_strategy": ColleagueType.PLAN_GENERATOR,

            # Incidents
            "handle_incident": ColleagueType.INCIDENT_ADVISOR,
            "query_incident": ColleagueType.INCIDENT_ADVISOR,
            "escalate": ColleagueType.INCIDENT_ADVISOR,

            # Exercises & Testing
            "design_exercise": ColleagueType.EXERCISE_DESIGNER,
            "query_exercise": ColleagueType.EXERCISE_DESIGNER,
            "create_scenario": ColleagueType.EXERCISE_DESIGNER,

            # Projects
            "query_project": ColleagueType.PROJECT_MANAGER,
            "analyze_project_health": ColleagueType.PROJECT_MANAGER,
            "optimize_resources": ColleagueType.PROJECT_MANAGER
        }

        logger.info(f"ColleagueCoordinator initialized with {len(colleagues)} colleagues")

    async def route_query(
        self,
        query: str,
        tenant_id: str,
        colleague_type: ColleagueType = ColleagueType.AUTO,
        context: Optional[AssistantContext] = None,
        conversation_history: Optional[List] = None
    ) -> Dict[str, Any]:
        """
        Route query to appropriate colleague(s)

        Args:
            query: User query
            tenant_id: Tenant identifier
            colleague_type: Specific colleague or AUTO for auto-routing
            context: Optional context override
            conversation_history: Optional conversation history

        Returns:
            Response with answer, colleague used, confidence, actions
        """
        self.routing_stats["total_queries"] += 1

        try:
            # Step 1: Determine which colleague to use
            if colleague_type == ColleagueType.AUTO:
                colleague_type, routing_confidence = await self._auto_route(query, conversation_history)
                self.routing_stats["auto_routed"] += 1
                logger.info(f"Auto-routed to {colleague_type.value} (confidence: {routing_confidence:.2f})")
            else:
                self.routing_stats["manual_routed"] += 1
                routing_confidence = 1.0
                logger.info(f"Manual routing to {colleague_type.value}")

            # Step 2: Get the colleague
            colleague = self.colleagues.get(colleague_type.value)
            if not colleague:
                raise ValueError(f"Colleague {colleague_type.value} not available")

            # Step 3: Determine context if not provided
            if context is None:
                context = self._determine_context(colleague_type)

            # Step 4: Process query through colleague
            result = await colleague.process_message(
                user_message=query,
                context=context,
                tenant_id=tenant_id
            )

            # Step 5: Check if workflow should be triggered
            workflow_suggestions = self._check_workflow_trigger(colleague_type, result)

            # Update routing stats
            if colleague_type.value not in self.routing_stats["routing_accuracy"]:
                self.routing_stats["routing_accuracy"][colleague_type.value] = {
                    "count": 0,
                    "avg_confidence": 0.0
                }

            stats = self.routing_stats["routing_accuracy"][colleague_type.value]
            stats["count"] += 1
            stats["avg_confidence"] = (
                (stats["avg_confidence"] * (stats["count"] - 1) + result.confidence) / stats["count"]
            )

            return {
                "success": True,
                "answer": result.content,
                "colleague": colleague.name,
                "colleague_type": colleague_type.value,
                "confidence": result.confidence,
                "routing_confidence": routing_confidence,
                "phase": result.phase.value if result.phase else None,
                "context": result.context.value if result.context else None,
                "actions": [
                    {
                        "id": action.id,
                        "title": action.title,
                        "description": action.description,
                        "priority": action.priority,
                        "type": action.action_type.value
                    }
                    for action in result.actions
                ],
                "workflow_suggestions": workflow_suggestions,
                "metadata": result.metadata
            }

        except Exception as e:
            logger.error(f"Error routing query: {str(e)}", exc_info=True)
            return {
                "success": False,
                "error": str(e),
                "colleague": None,
                "answer": f"Error routing query: {str(e)}"
            }

    async def _auto_route(
        self,
        query: str,
        conversation_history: Optional[List]
    ) -> tuple[ColleagueType, float]:
        """
        Automatically determine best colleague for query

        Args:
            query: User query
            conversation_history: Optional conversation history

        Returns:
            (ColleagueType, confidence_score)
        """
        # Use RAG intent analyzer
        intent_result = self.rag.intent_analyzer.analyze(query, conversation_history)

        # Map intent to colleague
        colleague_type = self.intent_to_colleague.get(
            intent_result.intent_type,
            ColleagueType.COMPLIANCE  # Default to Compliance Copilot
        )

        # Calculate routing confidence based on intent confidence
        routing_confidence = intent_result.confidence

        # Keyword-based fallback for better accuracy
        query_lower = query.lower()

        keyword_patterns = {
            ColleagueType.RISK_ANALYST: ["risk", "threat", "vulnerability", "fair", "lef", "loss event"],
            ColleagueType.BIA_SPECIALIST: ["bia", "rto", "rpo", "critical", "impact", "recovery time", "mtd"],
            ColleagueType.PLAN_GENERATOR: ["plan", "bcp", "drp", "recovery strategy", "continuity plan"],
            ColleagueType.INCIDENT_ADVISOR: ["incident", "crisis", "emergency", "ransomware", "outage", "breach"],
            ColleagueType.EXERCISE_DESIGNER: ["exercise", "drill", "test", "tabletop", "scenario", "simulation"],
            ColleagueType.PROJECT_MANAGER: ["project", "task", "deadline", "resource", "milestone", "health"],
            ColleagueType.COMPLIANCE: ["iso", "22301", "compliance", "standard", "clause", "requirement", "audit"]
        }

        # Check keyword matches
        max_matches = 0
        keyword_colleague = None

        for col_type, keywords in keyword_patterns.items():
            matches = sum(1 for kw in keywords if kw in query_lower)
            if matches > max_matches:
                max_matches = matches
                keyword_colleague = col_type

        # If keyword match is strong, use it (boost confidence)
        if max_matches >= 2 and keyword_colleague:
            return keyword_colleague, min(routing_confidence + 0.2, 1.0)

        return colleague_type, routing_confidence

    def _determine_context(self, colleague_type: ColleagueType) -> AssistantContext:
        """
        Determine appropriate AssistantContext for colleague type

        Args:
            colleague_type: Type of colleague

        Returns:
            AssistantContext enum value
        """
        context_mapping = {
            ColleagueType.COMPLIANCE: AssistantContext.COMPLIANCE,
            ColleagueType.PROJECT_MANAGER: AssistantContext.OVERVIEW,
            ColleagueType.RISK_ANALYST: AssistantContext.RISK,
            ColleagueType.BIA_SPECIALIST: AssistantContext.BIA,
            ColleagueType.PLAN_GENERATOR: AssistantContext.PLAN,
            ColleagueType.INCIDENT_ADVISOR: AssistantContext.INCIDENT,
            ColleagueType.EXERCISE_DESIGNER: AssistantContext.EXERCISE
        }

        return context_mapping.get(colleague_type, AssistantContext.OVERVIEW)

    def _check_workflow_trigger(
        self,
        colleague_type: ColleagueType,
        result: AssistantMessage
    ) -> List[Dict[str, Any]]:
        """
        Check if a cross-colleague workflow should be suggested

        Args:
            colleague_type: Current colleague type
            result: Result from colleague

        Returns:
            List of workflow suggestions
        """
        suggestions = []

        # Define workflow patterns
        workflows = {
            ColleagueType.RISK_ANALYST: {
                "next_colleague": ColleagueType.BIA_SPECIALIST,
                "trigger_keywords": ["critical", "high priority", "tier 1"],
                "suggestion": "High-priority risks identified. Consider BIA analysis for critical processes."
            },
            ColleagueType.BIA_SPECIALIST: {
                "next_colleague": ColleagueType.PLAN_GENERATOR,
                "trigger_keywords": ["rto", "rpo", "tier 1", "critical"],
                "suggestion": "Critical processes analyzed. Generate recovery plans based on RTO/RPO."
            },
            ColleagueType.PLAN_GENERATOR: {
                "next_colleague": ColleagueType.EXERCISE_DESIGNER,
                "trigger_keywords": ["plan created", "strategy defined", "recovery"],
                "suggestion": "Recovery plans ready. Design exercises to test effectiveness."
            },
            ColleagueType.EXERCISE_DESIGNER: {
                "next_colleague": ColleagueType.COMPLIANCE,
                "trigger_keywords": ["lessons learned", "gap identified"],
                "suggestion": "Exercise complete. Review compliance gaps identified."
            }
        }

        if colleague_type in workflows:
            workflow = workflows[colleague_type]
            content_lower = result.content.lower()

            # Check if trigger keywords present
            if any(kw in content_lower for kw in workflow["trigger_keywords"]):
                suggestions.append({
                    "next_colleague": workflow["next_colleague"].value,
                    "reason": workflow["suggestion"],
                    "confidence": 0.8
                })

                logger.info(f"Workflow trigger: {colleague_type.value} → {workflow['next_colleague'].value}")

        return suggestions

    async def execute_workflow(
        self,
        workflow_name: str,
        initial_query: str,
        tenant_id: str
    ) -> Dict[str, Any]:
        """
        Execute a predefined cross-colleague workflow

        Args:
            workflow_name: Name of workflow (e.g., "risk_to_plans")
            initial_query: Initial query
            tenant_id: Tenant identifier

        Returns:
            Workflow execution results
        """
        self.routing_stats["workflows_executed"] += 1

        workflows = {
            "risk_to_plans": [
                ColleagueType.RISK_ANALYST,
                ColleagueType.BIA_SPECIALIST,
                ColleagueType.PLAN_GENERATOR
            ],
            "incident_to_exercise": [
                ColleagueType.INCIDENT_ADVISOR,
                ColleagueType.EXERCISE_DESIGNER
            ],
            "compliance_to_project": [
                ColleagueType.COMPLIANCE,
                ColleagueType.PROJECT_MANAGER
            ]
        }

        if workflow_name not in workflows:
            return {
                "success": False,
                "error": f"Unknown workflow: {workflow_name}"
            }

        colleague_sequence = workflows[workflow_name]
        results = []
        current_query = initial_query

        logger.info(f"Executing workflow: {workflow_name} with {len(colleague_sequence)} steps")

        for colleague_type in colleague_sequence:
            result = await self.route_query(
                query=current_query,
                tenant_id=tenant_id,
                colleague_type=colleague_type
            )

            results.append({
                "colleague": colleague_type.value,
                "answer": result.get("answer"),
                "actions": result.get("actions", [])
            })

            # Use answer as input for next colleague
            current_query = f"Based on previous analysis: {result.get('answer', '')[:500]}. What are your recommendations?"

        return {
            "success": True,
            "workflow": workflow_name,
            "steps": len(colleague_sequence),
            "results": results
        }

    def get_stats(self) -> Dict[str, Any]:
        """Get coordinator statistics"""
        return {
            "coordinator": "ColleagueCoordinator",
            "colleagues_available": len(self.colleagues),
            "colleagues": list(self.colleagues.keys()),
            "routing_stats": self.routing_stats,
            "intent_mappings": len(self.intent_to_colleague)
        }

    def get_available_colleagues(self) -> List[Dict[str, str]]:
        """Get list of available colleagues"""
        return [
            {
                "type": col_type,
                "name": colleague.name,
                "specialty": colleague.specialty
            }
            for col_type, colleague in self.colleagues.items()
        ]
