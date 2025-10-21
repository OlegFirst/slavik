"""
Unified Workflow Engine (with ACE learning!)

Объединяет BPMN Orchestration + Workflow Intelligence в единый интерфейс
"""

from typing import Dict, List, Optional, Any
from datetime import datetime
import os
import logging
import sys

# Add platform root for ACE integration
sys.path.insert(0, '/Users/MD/AI-Platform-ISO')
from shared.ace_integration import ACEIntegration

from ..bpmn.engine_persistent import BPMNEnginePersistent
from ..bpmn.models import VisualState
from ..persistence.database import DatabaseManager

logger = logging.getLogger(__name__)


class UnifiedWorkflowEngine:
    """
    Unified Workflow Engine - Production Version

    Объединяет:
    - BPMN Orchestration (visual process modeling) - PostgreSQL
    - Workflow Intelligence (AI recommendations + learning)
    - Event synchronization for real-time integration

    Usage:
        # Initialize with database
        workflow = await UnifiedWorkflowEngine.create(
            tenant_id="acme-corp",
            module="bia",
            database_url=os.getenv("DATABASE_URL")
        )

        # Start from BPMN
        instance_id = await workflow.start_process_from_bpmn(
            bpmn_xml=bpmn_content,
            process_name="BIA Assessment"
        )

        # Get visual state
        state = await workflow.get_visual_state(instance_id)

        # Complete tasks with AI recommendations
        await workflow.complete_task(task_id, variables)
    """

    def __init__(
        self,
        tenant_id: str,
        module: str,
        db_manager: DatabaseManager,
        workflow_intelligence_enabled: bool = True
    ):
        """
        Initialize Unified Workflow Engine

        Args:
            tenant_id: Tenant identifier
            module: BCM module (bia, risk, compliance, etc)
            db_manager: DatabaseManager instance
            workflow_intelligence_enabled: Enable AI integration
        """
        # ACE Integration for continuous learning
        self.ace = ACEIntegration(module_name="workflow_engine")

        self.tenant_id = tenant_id
        self.module = module
        self.db_manager = db_manager
        self.workflow_intelligence_enabled = workflow_intelligence_enabled

        # Initialize BPMN Engine with PostgreSQL
        self.bpmn_engine = BPMNEnginePersistent(
            db_manager=db_manager,
            tenant_id=tenant_id
        )

        # Workflow Intelligence (optional integration)
        self.workflow_engine = None
        self.ai_advisor = None

        # Setup event synchronization
        self._setup_event_sync()

        logger.info(
            f"UnifiedWorkflowEngine initialized for {module} "
            f"(tenant={tenant_id}, wi_enabled={workflow_intelligence_enabled})"
        )

    @classmethod
    async def create(
        cls,
        tenant_id: str,
        module: str,
        database_url: Optional[str] = None,
        workflow_intelligence_enabled: bool = True
    ) -> "UnifiedWorkflowEngine":
        """
        Create and initialize UnifiedWorkflowEngine with database

        Args:
            tenant_id: Tenant identifier
            module: BCM module
            database_url: Database URL (defaults to DATABASE_URL env var)
            workflow_intelligence_enabled: Enable AI integration

        Returns:
            Initialized UnifiedWorkflowEngine
        """
        # Initialize database
        db_manager = DatabaseManager(database_url=database_url)
        await db_manager.connect()

        # Create engine
        engine = cls(
            tenant_id=tenant_id,
            module=module,
            db_manager=db_manager,
            workflow_intelligence_enabled=workflow_intelligence_enabled
        )

        # Initialize Workflow Intelligence if enabled
        if workflow_intelligence_enabled:
            await engine._init_workflow_intelligence()

        return engine

    async def _init_workflow_intelligence(self):
        """
        Initialize Workflow Intelligence integration

        Sets up:
        - Case Library for similar cases
        - ContextAdvisor for AI recommendations
        - Event bus subscribers
        """
        try:
            # Import Workflow Intelligence components
            import sys
            import os
            wi_path = os.path.join(
                os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
                '..'
            )
            if wi_path not in sys.path:
                sys.path.insert(0, wi_path)

            from workflow_intelligence.ai.context_advisor import ContextAdvisor
            from workflow_intelligence.case_library.repository import CaseRepository
            from workflow_intelligence.case_library.collector import CaseCollector
            from workflow_intelligence.core.workflow_engine import InMemoryStorageAdapter

            # Initialize Case Library Repository
            # For now: in-memory (TODO: PostgreSQL adapter)
            storage = InMemoryStorageAdapter()
            self.case_repository = CaseRepository(storage_adapter=storage)

            # Initialize Case Collector (learns from workflows)
            # We'll create a simple wrapper that converts BPMN events to workflow events
            class BPMNWorkflowEngineWrapper:
                """Wrapper to make BPMNEngine compatible with CaseCollector"""
                def __init__(self, bpmn_engine, module):
                    self.bpmn_engine = bpmn_engine
                    self.module = module
                    # Simple in-memory event bus for case collector
                    from collections import defaultdict
                    self._subscribers = defaultdict(list)

                def subscribe(self, event_type, handler):
                    self._subscribers[event_type].append(handler)

                async def publish(self, event_type, event_data):
                    for handler in self._subscribers.get(event_type, []):
                        await handler(event_data)

                @property
                def event_bus(self):
                    return self

            # Create wrapper
            wrapper = BPMNWorkflowEngineWrapper(self.bpmn_engine, self.module)

            # Initialize Case Collector
            self.case_collector = CaseCollector(
                workflow_engine=wrapper,
                case_repository=self.case_repository,
                llm_client=None  # TODO: Add LLM client for pattern analysis
            )

            # Initialize AI Advisor
            self.ai_advisor = ContextAdvisor(
                workflow_engine=wrapper,
                case_library=self.case_repository,
                ml_predictor=None,  # TODO: Add ML Predictor
                llm_client=None  # TODO: Add LLM client
            )

            logger.info(" Workflow Intelligence enabled (Case Library + AI Advisor)")

        except ImportError as e:
            logger.warning(
                f"️ Workflow Intelligence not available: {e}. "
                "AI recommendations will use rule-based fallback."
            )
            self.workflow_intelligence_enabled = False
            self.ai_advisor = None
            self.case_repository = None
            self.case_collector = None

    def _setup_event_sync(self):
        """
        Setup event synchronization between BPMN and Workflow Intelligence

        Events flow:
        BPMN Engine → UnifiedEngine handlers → Workflow Intelligence → AI Advisor
        """

        @self.bpmn_engine.on_event("bpmn.instance.started")
        async def on_bpmn_instance_started(event):
            logger.info(f"BPMN instance started: {event['data']['instance_id']}")

            # Track in Workflow Intelligence if enabled
            if self.workflow_engine:
                try:
                    await self.workflow_engine.start(
                        workflow_id=event['data']['instance_id'],
                        initial_data=event['data'].get('variables', {}),
                        tenant_id=self.tenant_id,
                        metadata={'source': 'bpmn', 'process_id': event['data']['process_id']}
                    )
                except Exception as e:
                    logger.error(f"Failed to track workflow start: {e}", exc_info=True)

        @self.bpmn_engine.on_event("bpmn.task.created")
        async def on_bpmn_task_created(event):
            logger.info(f"BPMN task created: {event['data']['task_id']}")

            # Get AI recommendations if enabled
            if self.ai_advisor and self.workflow_intelligence_enabled:
                try:
                    recommendations = await self._get_task_recommendations(
                        instance_id=event['data']['instance_id'],
                        task_id=event['data']['task_id'],
                        activity_id=event['data']['activity_id'],
                        task_name=event['data']['name']
                    )

                    # Inject recommendations into BPMN task
                    if recommendations:
                        await self.bpmn_engine.update_task(
                            task_id=event['data']['task_id'],
                            data={"ai_recommendations": recommendations}
                        )

                except Exception as e:
                    logger.error(f"Failed to generate AI recommendations: {e}", exc_info=True)

        @self.bpmn_engine.on_event("bpmn.task.completed")
        async def on_bpmn_task_completed(event):
            logger.info(f"BPMN task completed: {event['data']['task_id']}")

            # Track action in Workflow Intelligence
            if self.workflow_engine:
                try:
                    await self.workflow_engine.execute_action(
                        workflow_id=event['data']['instance_id'],
                        action=f"task_completed_{event['data']['activity_id']}",
                        action_data=event['data'].get('variables', {}),
                        user_id=event['data'].get('completed_by')
                    )
                except Exception as e:
                    logger.error(f"Failed to track task completion: {e}", exc_info=True)

        @self.bpmn_engine.on_event("bpmn.instance.completed")
        async def on_bpmn_instance_completed(event):
            logger.info(f"BPMN instance completed: {event['data']['instance_id']}")

            # Complete in Workflow Intelligence
            if self.workflow_engine:
                try:
                    await self.workflow_engine.complete(
                        workflow_id=event['data']['instance_id']
                    )
                except Exception as e:
                    logger.error(f"Failed to track workflow completion: {e}", exc_info=True)

            # Collect case for Case Library (self-learning)
            if self.workflow_intelligence_enabled:
                await self._collect_case_for_learning(event['data'])

    # ========== AI RECOMMENDATION METHODS ==========

    async def _get_task_recommendations(
        self,
        instance_id: str,
        task_id: str,
        activity_id: str,
        task_name: str
    ) -> List[Dict[str, Any]]:
        """
        Get AI recommendations for a task (with ACE learning!)

        Returns:
            List of recommendations with actions, reasons, and priorities
        """

        # Use ACE for continuous learning of recommendation patterns!
        result = await self.ace.execute_with_learning(
            task_type=f"task_recommendation_{self.module}_{activity_id}",
            base_context={
                "instance_id": instance_id,
                "task_id": task_id,
                "activity_id": activity_id,
                "task_name": task_name,
                "module": self.module
            },
            execute_fn=self._get_task_recommendations_impl,
            instance_id=instance_id,
            task_id=task_id,
            activity_id=activity_id,
            task_name=task_name
        )

        return result.get('recommendations', [])

    async def _get_task_recommendations_impl(
        self,
        context: Dict[str, Any],
        instance_id: str,
        task_id: str,
        activity_id: str,
        task_name: str
    ) -> Dict[str, Any]:
        """Internal task recommendation implementation (called by ACE)"""

        # ACE provides enhanced context!
        strategies = context.get('playbook_strategies', [])
        if strategies:
            logger.info(f" ACE enhanced recommendations with {len(strategies)} strategies")

        recommendations = []

        # Get instance data for context
        instance = await self.bpmn_engine.get_instance(instance_id)
        if not instance:
            return {
                'recommendations': [],
                'effectiveness': 0.0
            }

        # Try AI Advisor first (if Workflow Intelligence enabled)
        if self.workflow_intelligence_enabled and self.ai_advisor:
            try:
                # Get AI-powered contextual advice
                advice = await self.ai_advisor.suggest_next_steps(
                    workflow_id=instance_id,
                    current_state={
                        "task_id": task_id,
                        "activity_id": activity_id,
                        "task_name": task_name,
                        "module": self.module,
                        "variables": instance.variables
                    }
                )

                # Convert AI advice to recommendation format
                for suggestion in advice:
                    recommendations.append({
                        "action": suggestion.get("action", "ai_suggestion"),
                        "message": suggestion.get("action_label", suggestion.get("message", "")),
                        "reason": suggestion.get("reason", ""),
                        "priority": suggestion.get("priority", "medium"),
                        "ai_powered": True,
                        "confidence": suggestion.get("confidence_score"),
                        "similar_cases": suggestion.get("similar_cases_count")
                    })

                if recommendations:
                    logger.info(f" AI Advisor provided {len(recommendations)} recommendations for task {task_id}")
                    # High effectiveness for AI recommendations
                    avg_confidence = sum(r.get('confidence', 0.7) for r in recommendations) / len(recommendations)
                    return {
                        'recommendations': recommendations,
                        'effectiveness': avg_confidence
                    }

            except Exception as e:
                logger.warning(f"️ AI Advisor failed, falling back to rule-based: {e}")

        # Fallback: Rule-based recommendations
        recommendations = await self._get_rule_based_recommendations(
            instance, activity_id, task_name
        )

        # Lower effectiveness for rule-based
        return {
            'recommendations': recommendations,
            'effectiveness': 0.6
        }

    async def _get_rule_based_recommendations(
        self,
        instance,
        activity_id: str,
        task_name: str
    ) -> List[Dict[str, Any]]:
        """
        Fallback rule-based recommendations when AI Advisor unavailable
        """
        recommendations = []

        # Example: BIA module recommendations
        if self.module == "bia":
            if "rto" in activity_id.lower():
                recommendations.append({
                    "action": "suggest_rto",
                    "message": "AI can suggest RTO/RPO targets based on industry benchmarks",
                    "priority": "high",
                    "ai_powered": False
                })

            if "impact" in activity_id.lower():
                recommendations.append({
                    "action": "analyze_impact",
                    "message": "Use AI to analyze business impact scenarios",
                    "priority": "medium",
                    "ai_powered": False
                })

        # Risk module recommendations
        elif self.module == "risk":
            if "assessment" in activity_id.lower():
                recommendations.append({
                    "action": "ai_risk_analysis",
                    "message": "AI can identify hidden risk factors based on similar organizations",
                    "priority": "high",
                    "ai_powered": False
                })

        # Compliance module recommendations
        elif self.module == "compliance":
            if "audit" in activity_id.lower():
                recommendations.append({
                    "action": "compliance_check",
                    "message": "Run automated compliance checks against ISO 22301 requirements",
                    "priority": "high",
                    "ai_powered": False
                })

        # Generic recommendations based on task type
        if not recommendations:
            recommendations.append({
                "action": "get_ai_help",
                "message": f"Need help with '{task_name}'? Ask AI for guidance",
                "priority": "low",
                "ai_powered": False
            })

        return recommendations

    async def _collect_case_for_learning(self, completion_data: Dict[str, Any]):
        """
        Collect completed workflow as a case for Case Library

        This enables self-learning from successful workflows
        """
        if not self.workflow_intelligence_enabled or not self.case_collector:
            return

        try:
            # Get full instance data
            instance_id = completion_data['instance_id']
            instance = await self.bpmn_engine.get_instance(instance_id)

            if not instance:
                logger.warning(f"Cannot collect case: instance {instance_id} not found")
                return

            # Get process definition
            process = await self.bpmn_engine.get_process(instance.process_id)

            # Calculate workflow metrics
            from datetime import datetime
            started_at = instance.started_at if hasattr(instance, 'started_at') else datetime.now()
            completed_at = instance.completed_at if hasattr(instance, 'completed_at') else datetime.now()
            duration_days = (completed_at - started_at).days if started_at and completed_at else 0

            # Collect case using CaseCollector
            case = await self.case_collector.collect_from_completion(
                workflow_id=instance_id,
                module=self.module,
                outcome='success',
                organization_context=instance.variables.get('org_context', {}),
                metrics={
                    'duration_days': max(duration_days, 1),  # Minimum 1 day
                    'total_tasks': len(instance.variables.get('completed_tasks', [])),
                    'status': instance.status
                },
                decisions=instance.variables.get('decisions', []),
                final_variables=instance.variables
            )

            logger.info(f" Case collected for learning: {case.id} (module={self.module}, duration={duration_days}d)")

        except Exception as e:
            logger.warning(f"️ Failed to collect case for learning: {e}")

    # ========== UNIFIED API ==========

    async def start_process_from_bpmn(
        self,
        bpmn_xml: str,
        initial_variables: Dict[str, Any] = None,
        started_by: Optional[str] = None,
        process_name: Optional[str] = None,
        created_by: Optional[str] = None,
        description: Optional[str] = None,
        version: str = "1.0"
    ) -> str:
        """
        Start process from BPMN visual model

        Args:
            bpmn_xml: BPMN 2.0 XML content
            initial_variables: Initial process variables
            started_by: User who started the process
            process_name: Optional process name
            created_by: User who deployed the process
            description: Process description
            version: Process version

        Returns:
            str: Instance ID
        """
        # Get AI startup advice if enabled
        if self.ai_advisor and self.workflow_intelligence_enabled:
            try:
                startup_advice = await self._get_startup_recommendations(
                    initial_variables or {}
                )

                # Enrich with AI
                enriched_vars = {
                    **(initial_variables or {}),
                    "ai_startup_advice": startup_advice
                }
                initial_variables = enriched_vars
            except Exception as e:
                logger.error(f"Failed to get startup advice: {e}", exc_info=True)

        # Deploy BPMN process
        process_id = await self.bpmn_engine.deploy_process(
            bpmn_xml=bpmn_xml,
            tenant_id=self.tenant_id,
            name=process_name or f"{self.module}_process",
            module=self.module,
            description=description,
            version=version,
            created_by=created_by
        )

        # Start instance
        instance_id = await self.bpmn_engine.start_process(
            process_id=process_id,
            tenant_id=self.tenant_id,
            variables=initial_variables or {},
            started_by=started_by
        )

        return instance_id

    async def _get_startup_recommendations(
        self,
        variables: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Get AI recommendations for starting a workflow"""

        recommendations = {
            "message": f"Starting {self.module} workflow",
            "tips": [],
            "estimated_duration": None
        }

        # Add module-specific tips
        if self.module == "bia":
            recommendations["tips"] = [
                "Identify all critical business processes first",
                "Involve key stakeholders from each department",
                "Gather historical incident data if available"
            ]
            recommendations["estimated_duration"] = "7-14 days"

        elif self.module == "risk":
            recommendations["tips"] = [
                "Start with asset inventory",
                "Consider both internal and external threats",
                "Involve IT, security, and business teams"
            ]
            recommendations["estimated_duration"] = "5-10 days"

        return recommendations

    async def start_process_from_template(
        self,
        template_name: str,
        initial_variables: Dict[str, Any] = None,
        started_by: Optional[str] = None
    ) -> str:
        """
        Start from predefined template (YAML)

        Phase 1: Placeholder
        Phase 2: Use Workflow Intelligence

        Args:
            template_name: Template name (e.g., "bia_standard")
            initial_variables: Initial variables
            started_by: User who started

        Returns:
            str: Workflow ID
        """
        # TODO Phase 2: Use Workflow Intelligence
        # workflow_id = await self.workflow_engine.start(
        #     workflow_definition=template_name,
        #     initial_data=initial_variables
        # )
        # return workflow_id

        raise NotImplementedError(
            "Template-based workflows will be implemented in Phase 2 "
            "with Workflow Intelligence integration"
        )

    async def get_visual_state(
        self,
        workflow_id: str
    ) -> VisualState:
        """
        Get visual state for UI with AI recommendations

        Returns data for:
        - BPMN diagram rendering (bpmn-js)
        - Active tasks with AI recommendations
        - Progress and predictions
        - Process analytics

        Args:
            workflow_id: Instance ID

        Returns:
            VisualState: Visual state data with AI enhancements
        """
        # Get BPMN instance
        instance = await self.bpmn_engine.get_instance(workflow_id)
        if not instance:
            raise ValueError(f"Instance {workflow_id} not found")

        return await self._get_bpmn_visual_state(workflow_id, instance)

    async def _get_bpmn_visual_state(
        self,
        instance_id: str,
        instance=None
    ) -> VisualState:
        """Get visual state for BPMN process with AI recommendations"""

        if not instance:
            instance = await self.bpmn_engine.get_instance(instance_id)
            if not instance:
                raise ValueError(f"Instance {instance_id} not found")

        # Get process definition
        process = await self.bpmn_engine.get_process(instance.process_id)

        # Get active tasks
        tasks = await self.bpmn_engine.get_active_tasks(instance_id)

        # Get AI predictions if enabled
        predictions = None
        if self.workflow_intelligence_enabled:
            predictions = await self._get_workflow_predictions(instance)

        # Prepare task data with AI recommendations
        active_tasks = []
        for task in tasks:
            task_data = {
                "id": task.id,
                "activity_id": task.activity_id,
                "name": task.name,
                "assignee": task.assignee,
                "status": task.status.value,
                "created_at": task.created_at.isoformat() if task.created_at else None,
                "ai_recommendations": task.ai_recommendations or []
            }

            # Add AI tip summary
            if task.ai_recommendations:
                task_data["ai_tip"] = task.ai_recommendations[0].get("message", "")
            else:
                task_data["ai_tip"] = f"Work on: {task.name}"

            # Add AI predicted duration if available
            if task.ai_predicted_duration_hours:
                task_data["estimated_hours"] = task.ai_predicted_duration_hours

            active_tasks.append(task_data)

        # Calculate progress
        progress_percentage = await self._calculate_progress(instance)

        return VisualState(
            type="bpmn",
            bpmn_xml=process.bpmn_xml,
            current_activities=instance.current_activities,
            active_tasks=active_tasks,
            workflow_context={
                "instance_id": instance.id,
                "process_id": instance.process_id,
                "status": instance.status.value,
                "started_at": instance.started_at.isoformat() if instance.started_at else None,
                "started_by": instance.started_by,
                "variables": instance.variables,
                "progress_percentage": progress_percentage
            },
            predictions=predictions,
            visualization_hints={
                "highlight": instance.current_activities,
                "show_ai_overlay": self.workflow_intelligence_enabled,
                "module": self.module
            }
        )

    async def _get_workflow_predictions(
        self,
        instance
    ) -> Optional[Dict[str, Any]]:
        """Get AI predictions for workflow outcome"""

        try:
            predictions = {
                "estimated_completion_date": None,
                "success_probability": None,
                "risk_level": None,
                "estimated_duration_days": None
            }

            # Try ML Predictor first (if available)
            if self.ai_advisor and hasattr(self.ai_advisor, 'ml_predictor') and self.ai_advisor.ml_predictor:
                try:
                    # Get ML-based predictions
                    ml_predictions = await self.ai_advisor.ml_predictor.predict_outcome(
                        workflow_id=instance.id,
                        module=self.module,
                        current_state=instance.variables,
                        organization_context=instance.variables.get('org_context', {})
                    )

                    predictions.update({
                        "success_probability": ml_predictions.get("success_probability"),
                        "risk_level": ml_predictions.get("risk_level"),
                        "estimated_duration_days": ml_predictions.get("estimated_duration_days")
                    })

                    # Calculate completion date from ML duration
                    if instance.started_at and ml_predictions.get("estimated_duration_days"):
                        from datetime import timedelta
                        completion_date = instance.started_at + timedelta(days=ml_predictions["estimated_duration_days"])
                        predictions["estimated_completion_date"] = completion_date.isoformat()

                    logger.info(f" ML Predictor provided predictions for instance {instance.id}")
                    return predictions

                except Exception as e:
                    logger.warning(f"️ ML Predictor failed, using rule-based: {e}")

            # Fallback: Rule-based predictions
            predictions.update({
                "success_probability": 0.85,  # Default optimistic
                "risk_level": "low"
            })

            # Estimate completion based on progress
            if instance.started_at:
                from datetime import datetime
                elapsed = datetime.utcnow() - instance.started_at
                progress = await self._calculate_progress(instance)

                if progress > 0:
                    estimated_total_duration = elapsed / (progress / 100)
                    estimated_completion = instance.started_at + estimated_total_duration
                    predictions["estimated_completion_date"] = estimated_completion.isoformat()
                    predictions["estimated_duration_days"] = estimated_total_duration.days

            return predictions

        except Exception as e:
            logger.error(f"Failed to get predictions: {e}", exc_info=True)
            return None

    async def _calculate_progress(self, instance) -> float:
        """Calculate workflow progress percentage"""

        try:
            # Get process definition to count total activities
            process = await self.bpmn_engine.get_process(instance.process_id)

            # Parse BPMN to count activities
            from ..bpmn.parser import BPMNParser
            root = BPMNParser.parse_bpmn_xml(process.bpmn_xml)

            # Count total user tasks
            total_tasks = len(BPMNParser.find_user_tasks(root))
            if total_tasks == 0:
                return 0.0

            # Count completed tasks (all tasks minus active tasks)
            active_tasks = await self.bpmn_engine.get_active_tasks(instance.id)
            completed_count = max(0, total_tasks - len(active_tasks))

            # Calculate percentage
            progress = (completed_count / total_tasks) * 100

            return min(100.0, max(0.0, progress))

        except Exception as e:
            logger.error(f"Failed to calculate progress: {e}", exc_info=True)
            return 0.0

    async def _get_template_visual_state(self, workflow_id: str) -> VisualState:
        """Get visual state for template-based workflow"""
        # TODO Phase 2: Implement with Workflow Intelligence
        raise NotImplementedError("Template workflows in Phase 2")

    async def complete_task(
        self,
        task_id: str,
        variables: Dict[str, Any] = None,
        completed_by: Optional[str] = None
    ):
        """
        Complete task and advance workflow

        Args:
            task_id: Task ID
            variables: Variables to merge into process
            completed_by: User who completed the task
        """
        await self.bpmn_engine.complete_task(
            task_id=task_id,
            variables=variables,
            completed_by=completed_by
        )

    async def assign_task(
        self,
        task_id: str,
        assignee: str
    ):
        """
        Assign task to user

        Args:
            task_id: Task ID
            assignee: User identifier
        """
        await self.bpmn_engine.assign_task(task_id=task_id, assignee=assignee)

    async def get_active_tasks_for_user(
        self,
        assignee: str,
        status=None
    ) -> List[Dict[str, Any]]:
        """
        Get active tasks assigned to user with AI recommendations

        Args:
            assignee: User identifier
            status: Optional task status filter

        Returns:
            List of tasks with AI recommendations and metadata
        """
        from ..bpmn.models import TaskStatus

        # Get tasks from BPMN engine
        tasks = await self.bpmn_engine.get_tasks_for_assignee(
            tenant_id=self.tenant_id,
            assignee=assignee,
            status=status or TaskStatus.ACTIVE
        )

        # Enrich with AI and instance data
        enriched_tasks = []
        for task in tasks:
            task_data = task.dict()

            # Get instance for context
            try:
                instance = await self.bpmn_engine.get_instance(task.process_instance_id)
                if instance:
                    task_data["process_name"] = instance.process_id  # TODO: get actual name
                    task_data["instance_status"] = instance.status.value

                    # Add progress
                    task_data["progress_percentage"] = await self._calculate_progress(instance)

            except Exception as e:
                logger.error(f"Failed to get instance data for task {task.id}: {e}")

            # AI recommendations are already in task.ai_recommendations

            enriched_tasks.append(task_data)

        return enriched_tasks

    async def get_process_analytics(
        self,
        process_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get process analytics and statistics

        Args:
            process_id: Optional process ID filter

        Returns:
            Analytics data
        """
        analytics = {
            "total_instances": 0,
            "active_instances": 0,
            "completed_instances": 0,
            "avg_duration_hours": 0,
            "success_rate": 0,
            "module": self.module
        }

        # TODO: Implement with database queries
        # This would query process_analytics table created in migration 036

        return analytics

    async def terminate_process(
        self,
        workflow_id: str,
        reason: Optional[str] = None
    ):
        """
        Terminate process instance

        Args:
            workflow_id: Instance ID
            reason: Termination reason
        """
        await self.bpmn_engine.terminate_instance(
            instance_id=workflow_id,
            reason=reason
        )

    async def list_processes(
        self,
        module: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        List deployed BPMN processes

        Args:
            module: Optional module filter

        Returns:
            List of process definitions
        """
        processes = await self.bpmn_engine.list_processes(
            tenant_id=self.tenant_id,
            module=module or self.module
        )

        return [p.dict() for p in processes]

    async def list_instances(
        self,
        status=None
    ) -> List[Dict[str, Any]]:
        """
        List process instances

        Args:
            status: Optional status filter

        Returns:
            List of instances with metadata
        """
        instances = await self.bpmn_engine.list_instances(
            tenant_id=self.tenant_id,
            status=status
        )

        return [i.dict() for i in instances]

    async def close(self):
        """
        Close database connections and cleanup resources

        Call this when shutting down the engine
        """
        if self.db_manager:
            await self.db_manager.close()
            logger.info("UnifiedWorkflowEngine closed")

    async def __aenter__(self):
        """Async context manager entry"""
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        await self.close()
