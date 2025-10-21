"""
 Workflow Intelligence Adapter

Bridges workflow_intelligence's CaseCollector events with knowledge-system's centralized storage.

Architecture:
- Subscribes to same events as workflow_intelligence collector
- Transforms their WorkflowCase model to our standardized format
- Saves to centralized data/ structure
- No disruption to existing workflow_intelligence functionality
"""

from typing import Dict, Any, Optional
from datetime import datetime
import logging
from pathlib import Path

logger = logging.getLogger(__name__)


class WorkflowIntelligenceAdapter:
    """
    Adapter that connects workflow_intelligence case collection to knowledge-system

    Listens to workflow completion events and saves cases to centralized storage.
    """

    def __init__(
        self,
        workflow_engine,
        case_collector_path: Optional[Path] = None
    ):
        """
        Args:
            workflow_engine: WorkflowEngine instance from workflow_intelligence
            case_collector_path: Path to data/cases/ directory
        """
        self.workflow_engine = workflow_engine

        # Setup path to centralized storage
        if case_collector_path is None:
            project_root = Path(__file__).parents[3]
            case_collector_path = project_root / "data" / "cases" / "workflow_cases"

        self.cases_path = Path(case_collector_path)
        self.cases_path.mkdir(parents=True, exist_ok=True)

        # Subscribe to events
        self._subscribe_to_events()

        logger.info(
            f"WorkflowIntelligenceAdapter initialized for module: {workflow_engine.module}"
        )

    def _subscribe_to_events(self):
        """Subscribe to workflow completion events"""
        event_bus = self.workflow_engine.event_bus

        # Main event: workflow completed
        event_bus.subscribe(
            f"{self.workflow_engine.module}.workflow.completed",
            self._on_workflow_completed
        )

        logger.info(f"Subscribed to {self.workflow_engine.module}.workflow.completed")

    async def _on_workflow_completed(self, event):
        """
        Handle workflow completion - transform and save to knowledge-system

        This runs in parallel with workflow_intelligence's own collector.
        """
        workflow_id = event.workflow_id

        logger.info(f"Adapter: Workflow completed, collecting for knowledge-system: {workflow_id}")

        try:
            # Get workflow context
            context = await self.workflow_engine.get_context(workflow_id)

            # Transform to knowledge-system format
            case_data = await self._transform_to_knowledge_format(context)

            # Save to centralized storage
            await self._save_to_knowledge_system(case_data)

            logger.info(
                f"Adapter: Case saved to knowledge-system: {case_data['case_id']}",
                extra={
                    "workflow_id": workflow_id,
                    "module": case_data['module'],
                    "file_path": case_data.get('_file_path')
                }
            )

        except Exception as e:
            logger.error(
                f"Adapter: Failed to save case to knowledge-system for {workflow_id}: {e}",
                exc_info=True
            )

    async def _transform_to_knowledge_format(self, context) -> Dict[str, Any]:
        """
        Transform workflow_intelligence context to knowledge-system format

        Maps their WorkflowCase structure to our standardized case format.
        """
        workflow_data = context.workflow_data
        module = context.module

        # Generate case ID
        case_id = self._generate_case_id(context)

        # Organization context (anonymized)
        organization_context = {
            "industry": workflow_data.get("industry", "unknown"),
            "size": workflow_data.get("org_size", "medium"),
            "org_type": workflow_data.get("org_type", "company"),
            "maturity_level": workflow_data.get("maturity_level", "basic"),
            "region": workflow_data.get("region")
        }

        # Metrics
        metrics = self._extract_metrics(context, workflow_data)

        # Journey summary (simplified from their detailed journey)
        journey_summary = self._extract_journey_summary(context)

        # Decisions made during workflow
        decisions = workflow_data.get("decisions", [])

        # Final variables/outputs
        final_variables = {
            "current_stage": context.current_stage,
            "completed_steps": len(context.completed_steps),
            "started_at": context.started_at.isoformat() if context.started_at else None,
            "completed_at": datetime.utcnow().isoformat()
        }

        # Add module-specific outputs
        if module == "bia":
            final_variables.update({
                "processes": workflow_data.get("processes", []),
                "critical_processes_count": len([
                    p for p in workflow_data.get("processes", [])
                    if p.get("tier") in [1, 2]
                ])
            })
        elif module == "risk":
            final_variables.update({
                "risks": workflow_data.get("risks", []),
                "high_risks_count": len([
                    r for r in workflow_data.get("risks", [])
                    if r.get("severity") == "high"
                ])
            })

        # Outcome
        outcome = "success" if context.current_stage in ["completed", "approved", "archived"] else "incomplete"

        case_data = {
            "case_id": case_id,
            "workflow_id": context.workflow_id,
            "module": module,
            "outcome": outcome,
            "organization_context": organization_context,
            "metrics": metrics,
            "decisions": decisions,
            "final_variables": final_variables,
            "journey_summary": journey_summary,
            "collected_at": datetime.utcnow().isoformat(),
            "source": "workflow_intelligence_adapter",
            "version": "1.0"
        }

        return case_data

    def _extract_metrics(self, context, workflow_data: Dict) -> Dict[str, Any]:
        """Extract metrics from workflow context"""
        metrics = {
            "total_steps": len(context.completed_steps),
            "completed_successfully": context.current_stage in ["completed", "approved", "archived"]
        }

        # Duration
        if context.started_at:
            duration = datetime.utcnow() - context.started_at
            metrics["total_duration_days"] = duration.total_seconds() / 86400
            metrics["total_duration_hours"] = duration.total_seconds() / 3600

        # Module-specific metrics
        if context.module == "bia":
            metrics["processes_identified"] = len(workflow_data.get("processes", []))
            metrics["critical_processes"] = len([
                p for p in workflow_data.get("processes", [])
                if p.get("tier") in [1, 2]
            ])
        elif context.module == "risk":
            metrics["risks_identified"] = len(workflow_data.get("risks", []))
            metrics["high_risks"] = len([
                r for r in workflow_data.get("risks", [])
                if r.get("severity") == "high"
            ])

        # User feedback
        if "user_satisfaction" in workflow_data:
            metrics["user_satisfaction"] = workflow_data["user_satisfaction"]

        if "certification_ready" in workflow_data:
            metrics["certification_ready"] = workflow_data["certification_ready"]

        return metrics

    def _extract_journey_summary(self, context) -> list:
        """Extract simplified journey from completed steps"""
        journey = []

        # Group steps by stage
        steps_by_stage = {}
        for step in context.completed_steps:
            stage = step.get("to_state") or step.get("from_state")
            if stage not in steps_by_stage:
                steps_by_stage[stage] = []
            steps_by_stage[stage].append(step)

        # Create summary for each stage
        for stage, steps in steps_by_stage.items():
            if not steps:
                continue

            stage_summary = {
                "stage": stage,
                "actions_count": len(steps),
                "started_at": steps[0]["timestamp"],
                "completed_at": steps[-1]["timestamp"]
            }

            # Calculate duration
            try:
                started = datetime.fromisoformat(steps[0]["timestamp"])
                completed = datetime.fromisoformat(steps[-1]["timestamp"])
                duration = (completed - started).total_seconds() / 3600
                stage_summary["duration_hours"] = round(duration, 2)
            except:
                stage_summary["duration_hours"] = 0

            journey.append(stage_summary)

        return journey

    def _generate_case_id(self, context) -> str:
        """Generate unique case ID"""
        timestamp = datetime.utcnow().strftime("%Y%m%d%H%M%S")
        return f"{context.module}_{context.workflow_id[:12]}_{timestamp}"

    async def _save_to_knowledge_system(self, case_data: Dict[str, Any]):
        """
        Save case to centralized knowledge-system storage

        Saves to: data/cases/workflow_cases/{module}/{case_id}.json
        """
        import json

        module = case_data["module"]
        case_id = case_data["case_id"]

        # Create module directory
        module_path = self.cases_path / module
        module_path.mkdir(parents=True, exist_ok=True)

        # Save case file
        case_file = module_path / f"{case_id}.json"
        case_file.write_text(
            json.dumps(case_data, indent=2, default=str, ensure_ascii=False)
        )

        # Add file path to case data for logging
        case_data["_file_path"] = str(case_file)

        logger.info(f"Case saved to: {case_file}")

        # TODO: Also save to PostgreSQL when repository is available
        # TODO: Index in vector DB for semantic search

        return case_file


# ============================================================================
# INTEGRATION HELPER
# ============================================================================

def integrate_with_workflow_engine(workflow_engine) -> WorkflowIntelligenceAdapter:
    """
    Helper function to integrate adapter with existing workflow engine

    Usage:
        from learning_knowledge.integrations.workflow_intelligence_adapter import integrate_with_workflow_engine

        adapter = integrate_with_workflow_engine(workflow_engine)

    Returns:
        WorkflowIntelligenceAdapter instance
    """
    adapter = WorkflowIntelligenceAdapter(workflow_engine)
    logger.info(f"Knowledge-system adapter integrated with {workflow_engine.module}")
    return adapter
