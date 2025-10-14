"""
BIA Workflow Adapter
====================

Extracted from: /Users/MD/AI-Platform-ISO/SESSION_SUMMARY.md
Source lines: 2111-2290
Date extracted: 2025-10-04

Description:
-----------
Integration adapter that connects Workflow Intelligence Engine with BIA Service.
Manages:
- Starting BIA workflows
- Adding processes, dependencies, impacts, RTOs
- Getting AI advice
- Advancing stages
- Event publishing to Event Bus
- Active workflow management

This replaces the existing BIA state machine with the new Workflow Engine.

Dependencies:
- bia_workflow_extracted.py (BIAWorkflowEngine)
- case_library_extracted.py (CaseCollector, CaseRepository)
- context_builder_extracted.py (AIContextBuilder)
"""

from typing import Dict, Any, Optional


class BIAWorkflowAdapter:
    """
    Adapter интегрирующий Workflow Intelligence с BIA Service

    Заменяет существующий BIA state machine на Workflow Engine
    """

    def __init__(
        self,
        db_session,
        eventbus_client,
        vector_db_client=None
    ):
        self.db = db_session
        self.eventbus = eventbus_client

        # Case Library
        # Note: In production, import actual classes
        # from case_library_extracted import CaseCollector, CaseRepository
        self.case_collector = None  # CaseCollector(db_session, eventbus_client)
        self.case_repository = None  # CaseRepository(db_session, vector_db_client)

        # Active workflows
        self.workflows: Dict[str, Any] = {}  # Dict[str, BIAWorkflowEngine]

    async def start(self):
        """Запустить adapter"""
        # Start case collector
        if self.case_collector:
            await self.case_collector.start()

    async def start_bia(
        self,
        bia_id: str,
        org_context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Начать новый BIA workflow"""

        # Create workflow engine
        # Note: In production, import BIAWorkflowEngine
        # from bia_workflow_extracted import BIAWorkflowEngine
        # workflow = BIAWorkflowEngine(bia_id, org_context)

        # Setup event handlers
        # await self._setup_event_handlers(workflow)

        # Store workflow
        # self.workflows[bia_id] = workflow

        # Transition to first stage
        # await workflow.transition_to('identify_processes')

        return {
            'bia_id': bia_id,
            'status': 'started',
            'current_stage': 'identify_processes'  # workflow.current_state.name
        }

    async def add_process(
        self,
        bia_id: str,
        process: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Добавить процесс к BIA"""

        workflow = self._get_workflow(bia_id)

        try:
            await workflow.add_process(process)

            return {
                'status': 'success',
                'process_id': process.get('id'),
                'can_proceed': workflow.can_transition_to('analyze_dependencies')[0]
            }
        except Exception as e:
            return {
                'status': 'error',
                'error': str(e)
            }

    async def get_ai_advice(
        self,
        bia_id: str,
        org_context: Dict[str, Any],
        user_message: Optional[str] = None
    ) -> Dict[str, Any]:
        """Получить AI advice для текущей стадии"""

        workflow = self._get_workflow(bia_id)

        # Build context
        # Note: In production, import AIContextBuilder
        # from context_builder_extracted import AIContextBuilder
        # context_builder = AIContextBuilder(workflow, self.case_repository)
        # full_context = await context_builder.build_full_context(
        #     org_context, user_message
        # )

        # Mock response
        return {
            'workflow_id': bia_id,
            'current_stage': 'identify_processes',
            'advice': 'Mock AI advice'
        }

    async def try_advance_stage(
        self,
        bia_id: str
    ) -> Dict[str, Any]:
        """Попытаться перейти на следующую стадию"""

        workflow = self._get_workflow(bia_id)

        # Get available transitions
        available = workflow.get_available_transitions()

        if not available:
            return {
                'status': 'error',
                'message': 'No available transitions'
            }

        # Try to transition to next stage
        next_stage = available[0]
        can_transition, reason = workflow.can_transition_to(next_stage)

        if not can_transition:
            return {
                'status': 'blocked',
                'next_stage': next_stage,
                'reason': reason,
                'validation_errors': workflow.current_state.validation_errors
            }

        # Transition
        await workflow.transition_to(next_stage)

        return {
            'status': 'success',
            'new_stage': next_stage,
            'progress': workflow._calculate_progress()
        }

    async def _setup_event_handlers(self, workflow):
        """Setup event handlers для workflow"""

        # Publish all workflow events to EventBus
        async def publish_to_eventbus(event_data: Dict[str, Any]):
            await self.eventbus.publish(
                topic=f"bia.{event_data.get('type', 'event')}",
                data=event_data
            )

        # Register handlers
        workflow.on('state_changed', publish_to_eventbus)
        workflow.on('process_added', publish_to_eventbus)
        workflow.on('dependency_added', publish_to_eventbus)
        workflow.on('impact_assessed', publish_to_eventbus)
        workflow.on('rto_set', publish_to_eventbus)
        workflow.on('stage_completed', publish_to_eventbus)
        workflow.on('milestone_reached', publish_to_eventbus)

    def _get_workflow(self, bia_id: str):
        """Get workflow or raise error"""
        workflow = self.workflows.get(bia_id)
        if not workflow:
            raise ValueError(f"Workflow not found: {bia_id}")
        return workflow
