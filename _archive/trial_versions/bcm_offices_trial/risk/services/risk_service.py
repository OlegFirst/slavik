"""
Risk Service - Main Service for Risk Office

Orchestrates all components:
- RiskWorkflow (state machine)
- RiskExpert (business logic)
- RiskSpecialist (dialogue)
- RiskOrgan (LLM)
- RiskTools (DB)
- EventBus (events)
"""

import sys
from pathlib import Path
from typing import Dict, Any, List, Optional

# Add paths
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "workflow_intelligence"))
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "ai-orchestration/muscles/ai_organs"))

# Import components
from ..workflow.risk_workflow import RiskWorkflow
from ..ai.expert import RiskExpert
from ..ai.specialist import RiskSpecialist
from ..ai.organ import RiskOrgan
from ..tools.risk_tools import RiskTools

# Import infrastructure
from workflow_intelligence.core.case_library.repository import CaseLibraryRepository
from base_organ import BaseAIOrgan


class RiskService:
    """
    Risk Service - complete risk management service

    Provides:
    - Risk assessment workflows
    - AI-powered risk analysis
    - FAIR methodology
    - Treatment planning
    - Event-driven integration

    Example:
        >>> service = RiskService(db_session, llm_router, event_bus)
        >>> response = await service.chat(
        ...     "Identify risks for our payment processing",
        ...     context={'process_id': 'proc_123', 'org_context': {...}}
        ... )
    """

    def __init__(
        self,
        db_session,
        llm_router=None,
        event_bus=None,
        org_context: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize Risk Service

        Args:
            db_session: Database session (Supabase)
            llm_router: LLM router for AI analysis
            event_bus: EventBus for publishing events
            org_context: Organization context (industry, size, etc)
        """
        self.db = db_session
        self.event_bus = event_bus
        self.org_context = org_context or {}

        # Initialize tools
        self.tools = RiskTools(db_session)

        # Initialize case library
        self.case_repository = CaseLibraryRepository(db_session)

        # Initialize workflow
        self.workflow = RiskWorkflow(
            risk_workflow_id=f"risk_{self.org_context.get('org_id', 'unknown')}",
            org_context=self.org_context
        )

        # Initialize organ (LLM)
        self.organ = RiskOrgan(llm_router=llm_router)

        # Initialize expert (business logic)
        self.expert = RiskExpert(
            tools=self.tools,
            organ=self.organ,
            workflow=self.workflow,
            case_repository=self.case_repository
        )

        # Initialize specialist (dialogue)
        self.specialist = RiskSpecialist(
            expert=self.expert,
            workflow=self.workflow,
            knowledge_sources=[self.case_repository]
        )

        # Event subscribers
        if self.event_bus:
            self._setup_event_subscribers()

    # ========================================================================
    # MAIN INTERFACE
    # ========================================================================

    async def chat(
        self,
        message: str,
        context: Dict[str, Any],
        history: Optional[List[Dict]] = None
    ) -> Dict[str, Any]:
        """
        Chat interface - main entry point for users

        Args:
            message: User message
            context: Context with process_id, org_context, etc
            history: Conversation history

        Returns:
            Conversational response with action results
        """
        # Merge org context
        context['org_context'] = {**self.org_context, **context.get('org_context', {})}

        # Delegate to specialist
        return await self.specialist.chat(message, context, history)

    # ========================================================================
    # DIRECT API (for non-conversational use)
    # ========================================================================

    async def identify_risks(
        self,
        process_id: str,
        user_input: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Identify risks for a process

        Args:
            process_id: Process to analyze
            user_input: Optional user description

        Returns:
            Identified risks
        """
        return await self.expert.identify_risks(
            process_id=process_id,
            org_context=self.org_context,
            user_input=user_input
        )

    async def analyze_likelihood(self, risk_ids: List[str]) -> Dict[str, Any]:
        """Analyze likelihood for risks"""
        return await self.expert.analyze_likelihood(
            risk_ids=risk_ids,
            org_context=self.org_context
        )

    async def calculate_impact(self, risk_ids: List[str]) -> Dict[str, Any]:
        """Calculate impact for risks"""
        return await self.expert.calculate_impact(
            risk_ids=risk_ids,
            org_context=self.org_context
        )

    async def fair_analysis(self, risk_ids: List[str]) -> Dict[str, Any]:
        """Perform FAIR analysis"""
        return await self.expert.fair_analysis(
            risk_ids=risk_ids,
            org_context=self.org_context
        )

    async def plan_treatments(self, risk_ids: List[str]) -> Dict[str, Any]:
        """Plan risk treatments"""
        return await self.expert.plan_treatments(
            risk_ids=risk_ids,
            org_context=self.org_context
        )

    # ========================================================================
    # WORKFLOW OPERATIONS
    # ========================================================================

    async def get_workflow_status(self) -> Dict[str, Any]:
        """Get current workflow status"""
        return await self.expert.get_workflow_status()

    async def get_available_actions(self) -> List[Dict[str, Any]]:
        """Get available actions for current workflow stage"""
        return self.workflow.get_available_actions()

    async def identify_gaps(self) -> List[Dict[str, str]]:
        """Identify gaps in current workflow stage"""
        return self.workflow.identify_gaps()

    # ========================================================================
    # RISK OPERATIONS
    # ========================================================================

    async def get_risk_summary(self, risk_id: str) -> Optional[Dict[str, Any]]:
        """Get complete risk summary"""
        return await self.tools.get_risk_summary(risk_id)

    async def get_assessment_summary(self, assessment_id: str) -> Optional[Dict[str, Any]]:
        """Get complete assessment summary"""
        return await self.tools.get_assessment_summary(assessment_id)

    # ========================================================================
    # EVENT HANDLING
    # ========================================================================

    def _setup_event_subscribers(self):
        """Setup EventBus subscribers for risk events"""
        if not self.event_bus:
            return

        # Subscribe to BIA process events
        self.event_bus.subscribe(
            topic='bia.process.created',
            handler=self._on_process_created
        )

        # Subscribe to governance policy events
        self.event_bus.subscribe(
            topic='governance.policy.updated',
            handler=self._on_policy_updated
        )

    async def _on_process_created(self, event: Dict[str, Any]):
        """
        Handle BIA process created event

        When a new critical process is identified, automatically trigger risk assessment
        """
        process_data = event.get('data', {})
        process_id = process_data.get('process_id')
        criticality = process_data.get('criticality')

        # Auto-trigger risk assessment for critical processes
        if criticality in ['critical', 'high'] and process_id:
            await self.identify_risks(
                process_id=process_id,
                user_input=f"Automatic risk assessment for critical process: {process_data.get('name')}"
            )

            # Publish event
            if self.event_bus:
                await self.event_bus.publish(
                    topic='risk.assessment.auto_triggered',
                    data={
                        'process_id': process_id,
                        'trigger': 'bia.process.created',
                        'criticality': criticality
                    }
                )

    async def _on_policy_updated(self, event: Dict[str, Any]):
        """
        Handle governance policy updated event

        When risk appetite or policies change, re-evaluate treatment plans
        """
        policy_data = event.get('data', {})
        policy_type = policy_data.get('policy_type')

        if policy_type == 'risk_appetite':
            # Re-evaluate all active risks
            # (implementation depends on how we track active assessments)
            pass

    # ========================================================================
    # HEALTH CHECK
    # ========================================================================

    async def health_check(self) -> Dict[str, Any]:
        """
        Health check for Risk Service

        Returns:
            Service health status
        """
        health = {
            "service": "risk",
            "status": "healthy",
            "components": {}
        }

        # Check DB
        try:
            if self.db:
                result = await self.db.table('risk.identified_risks').select('id').limit(1).execute()
                health["components"]["database"] = "healthy"
            else:
                health["components"]["database"] = "not_configured"
        except Exception as e:
            health["components"]["database"] = f"error: {e}"
            health["status"] = "degraded"

        # Check LLM
        try:
            if self.organ.llm_router:
                # Simple test query
                test_response = await self.organ._query_llm(
                    system_prompt="You are a test.",
                    user_prompt="Respond with 'OK'",
                    temperature=0.0
                )
                health["components"]["llm"] = "healthy" if test_response else "error"
            else:
                health["components"]["llm"] = "not_configured"
        except Exception as e:
            health["components"]["llm"] = f"error: {e}"
            health["status"] = "degraded"

        # Check EventBus
        health["components"]["eventbus"] = "configured" if self.event_bus else "not_configured"

        # Check Workflow
        health["components"]["workflow"] = {
            "current_state": self.workflow.current_state.name,
            "status": "active"
        }

        return health

    # ========================================================================
    # ADMIN OPERATIONS
    # ========================================================================

    async def reset_workflow(self) -> bool:
        """
        Reset workflow to initial state

        Returns:
            True if successful
        """
        try:
            # Reset to NOT_STARTED
            self.workflow = RiskWorkflow(
                risk_workflow_id=f"risk_{self.org_context.get('org_id', 'unknown')}",
                org_context=self.org_context
            )

            # Reinitialize expert with new workflow
            self.expert = RiskExpert(
                tools=self.tools,
                organ=self.organ,
                workflow=self.workflow,
                case_repository=self.case_repository
            )

            return True

        except Exception as e:
            print(f"Error resetting workflow: {e}")
            return False
