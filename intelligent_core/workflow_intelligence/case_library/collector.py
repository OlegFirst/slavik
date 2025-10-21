"""
 CASE COLLECTOR - Автоматический сбор успешных workflows

Слушает события workflow, собирает данные, создаёт cases для обучения.

Philosophy: Every workflow completion is a learning opportunity.
"""

from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import logging
import asyncio

from .models import (
    WorkflowCase,
    WorkflowStepRecord,
    OrganizationContext,
    WorkflowMetrics,
    ChallengeResolution,
    AIInteraction,
    CaseCollectionConfig,
    extract_features_for_ml
)

logger = logging.getLogger(__name__)


# ============================================================================
# CASE COLLECTOR
# ============================================================================

class CaseCollector:
    """
    Автоматически собирает cases из завершённых workflows

    Подписывается на события и создаёт WorkflowCase для Case Library.
    """

    def __init__(
        self,
        workflow_engine,
        case_repository,
        llm_client=None,  # Для AI анализа patterns
        config: CaseCollectionConfig = None
    ):
        """
        Args:
            workflow_engine: WorkflowEngine instance
            case_repository: CaseRepository для сохранения
            llm_client: LLM для анализа success patterns (optional)
            config: Настройки сбора
        """
        self.workflow_engine = workflow_engine
        self.repository = case_repository
        self.llm_client = llm_client
        self.config = config or CaseCollectionConfig()

        # Подписываемся на события
        self._subscribe_to_events()

        logger.info(f"Case Collector initialized for module: {workflow_engine.module}")

    def _subscribe_to_events(self):
        """Подписка на workflow события"""
        event_bus = self.workflow_engine.event_bus

        # Workflow завершён - главное событие!
        event_bus.subscribe(
            f"{self.workflow_engine.module}.workflow.completed",
            self._on_workflow_completed
        )

        # Step completed - собираем данные пошагово
        event_bus.subscribe(
            f"{self.workflow_engine.module}.stage.changed",
            self._on_stage_changed
        )

        # AI interactions
        event_bus.subscribe(
            f"{self.workflow_engine.module}.ai.interaction",
            self._on_ai_interaction
        )

    # ========================================================================
    # EVENT HANDLERS
    # ========================================================================

    async def _on_workflow_completed(self, event):
        """
        Когда workflow завершён - создаём case

        Это главный метод сбора!
        """
        workflow_id = event.workflow_id

        logger.info(f"Workflow completed, collecting case: {workflow_id}")

        try:
            # Создать case
            case = await self.create_case(workflow_id)

            if case:
                # Сохранить в repository
                await self.repository.save(case)

                logger.info(
                    f"Case collected successfully: {case.case_id}",
                    extra={
                        "workflow_id": workflow_id,
                        "module": case.module,
                        "duration_days": case.metrics.total_duration_days
                    }
                )

                # Триггерить ML retraining (async)
                asyncio.create_task(self._trigger_ml_retraining())

        except Exception as e:
            logger.error(f"Failed to collect case for {workflow_id}: {e}", exc_info=True)

    async def _on_stage_changed(self, event):
        """Когда стадия меняется - записываем в temporary storage"""
        # Сохраняем interim data для последующего сбора
        # Это позволит нам иметь полную историю даже если workflow прервётся
        pass

    async def _on_ai_interaction(self, event):
        """Когда AI взаимодействует - записываем"""
        # Сохраняем AI interaction data
        pass

    # ========================================================================
    # CASE CREATION
    # ========================================================================

    async def create_case(self, workflow_id: str) -> Optional[WorkflowCase]:
        """
        Создать case из завершённого workflow

        Returns:
            WorkflowCase или None если не подходит для сбора
        """
        # Загрузить workflow context
        context = await self.workflow_engine.get_context(workflow_id)
        workflow_data = context.workflow_data

        # Проверить фильтры качества
        if not await self._passes_quality_filters(context):
            logger.info(f"Workflow {workflow_id} didn't pass quality filters, skipping")
            return None

        # Проверить consent (если требуется)
        if self.config.require_consent:
            if not workflow_data.get("case_collection_consent", False):
                logger.info(f"No consent for case collection: {workflow_id}")
                return None

        # Собрать journey
        journey = await self._build_journey(context)

        # Создать organization context (anonymized!)
        org_context = await self._create_org_context(workflow_data)

        # Создать metrics
        metrics = await self._create_metrics(context, journey)

        # Извлечь success patterns (через AI если доступен)
        success_patterns = await self._extract_success_patterns(journey, workflow_data)

        # Извлечь lessons learned
        lessons_learned = await self._extract_lessons_learned(journey, workflow_data)

        # Извлечь best practices
        best_practices = await self._extract_best_practices(journey, workflow_data)

        # Создать case
        case = WorkflowCase(
            case_id=self._generate_case_id(context),
            module=context.module,
            workflow_name=self.workflow_engine.module + "_process",
            organization_context=org_context,
            journey=journey,
            metrics=metrics,
            success_patterns=success_patterns,
            lessons_learned=lessons_learned,
            best_practices=best_practices,
            features=extract_features_for_ml(
                WorkflowCase(
                    case_id="temp",
                    module=context.module,
                    workflow_name="temp",
                    organization_context=org_context,
                    journey=journey,
                    metrics=metrics,
                    success_patterns=success_patterns,
                    lessons_learned=lessons_learned,
                    best_practices=best_practices
                )
            ),
            anonymized=self.config.anonymize_data,
            consent_given=True
        )

        return case

    # ========================================================================
    # HELPERS
    # ========================================================================

    async def _passes_quality_filters(self, context) -> bool:
        """Проверить фильтры качества"""

        # Minimum duration
        if context.started_at:
            duration = datetime.utcnow() - context.started_at
            if duration.total_seconds() / 3600 < self.config.min_duration_hours:
                return False

        # Minimum steps
        if len(context.completed_steps) < self.config.min_steps:
            return False

        # Successful completion
        if self.config.require_successful_completion:
            # Проверить что workflow действительно завершён успешно
            # (не просто остановлен)
            if not self._is_successfully_completed(context):
                return False

        return True

    def _is_successfully_completed(self, context) -> bool:
        """Проверить что workflow завершён успешно"""
        # Например, проверить финальную стадию
        final_states = ["completed", "approved", "archived"]
        return context.current_stage in final_states

    async def _build_journey(self, context) -> List[WorkflowStepRecord]:
        """Построить journey из completed_steps"""
        journey = []

        # Группируем steps по stages
        steps_by_stage = self._group_steps_by_stage(context.completed_steps)

        for stage, steps in steps_by_stage.items():
            if not steps:
                continue

            started_at = steps[0]["timestamp"]
            completed_at = steps[-1]["timestamp"]

            duration_hours = (
                datetime.fromisoformat(completed_at) -
                datetime.fromisoformat(started_at)
            ).total_seconds() / 3600

            # Собрать actions
            actions = [
                {
                    "action": step["action"],
                    "data": step.get("data", {}),
                    "timestamp": step["timestamp"]
                }
                for step in steps
            ]

            # Собрать challenges (из workflow data если есть)
            challenges = await self._extract_challenges_for_stage(stage, context.workflow_data)

            # Собрать AI interactions (из workflow data)
            ai_interactions = await self._extract_ai_interactions_for_stage(
                stage,
                context.workflow_data
            )

            step_record = WorkflowStepRecord(
                stage=stage,
                started_at=datetime.fromisoformat(started_at),
                completed_at=datetime.fromisoformat(completed_at),
                duration_hours=duration_hours,
                actions_taken=actions,
                challenges=challenges,
                ai_interactions=ai_interactions,
                step_metrics={}
            )

            journey.append(step_record)

        return journey

    def _group_steps_by_stage(self, completed_steps: List[Dict]) -> Dict[str, List]:
        """Группировка steps по stages"""
        by_stage = {}

        for step in completed_steps:
            # Используем to_state как stage
            stage = step.get("to_state") or step.get("from_state")
            if stage not in by_stage:
                by_stage[stage] = []
            by_stage[stage].append(step)

        return by_stage

    async def _extract_challenges_for_stage(
        self,
        stage: str,
        workflow_data: Dict
    ) -> List[ChallengeResolution]:
        """Извлечь challenges для стадии"""
        challenges = []

        # Если в workflow_data есть записи о проблемах
        if "challenges" in workflow_data:
            stage_challenges = [
                c for c in workflow_data["challenges"]
                if c.get("stage") == stage
            ]

            for c in stage_challenges:
                challenges.append(ChallengeResolution(
                    type=c.get("type", "unknown"),
                    description=c.get("description", ""),
                    resolution=c.get("resolution", ""),
                    time_to_resolve_hours=c.get("time_to_resolve_hours", 0),
                    ai_assisted=c.get("ai_assisted", False)
                ))

        return challenges

    async def _extract_ai_interactions_for_stage(
        self,
        stage: str,
        workflow_data: Dict
    ) -> List[AIInteraction]:
        """Извлечь AI interactions для стадии"""
        interactions = []

        # Если есть записи AI interactions в workflow_data
        if "ai_interactions" in workflow_data:
            stage_interactions = [
                i for i in workflow_data["ai_interactions"]
                if i.get("stage") == stage
            ]

            for i in stage_interactions:
                interactions.append(AIInteraction(
                    type=i.get("type", "suggest"),
                    prompt_summary=i.get("prompt_summary", ""),
                    response_summary=i.get("response_summary", ""),
                    accepted=i.get("accepted", False),
                    helpful_rating=i.get("helpful_rating")
                ))

        return interactions

    async def _create_org_context(self, workflow_data: Dict) -> OrganizationContext:
        """Создать anonymized organization context"""

        # Если есть organization_id, загрузить данные
        org_id = workflow_data.get("organization_id")

        if org_id and hasattr(self, "_org_repository"):
            org = await self._org_repository.get(org_id)

            return OrganizationContext(
                industry=org.get("industry", "unknown"),
                size=org.get("size", "medium"),
                org_type=org.get("org_type", "company"),
                maturity_level=org.get("bcm_maturity", "basic"),
                region=org.get("region")
            )

        # Иначе из workflow_data (если есть)
        return OrganizationContext(
            industry=workflow_data.get("industry", "unknown"),
            size=workflow_data.get("org_size", "medium"),
            org_type=workflow_data.get("org_type", "company"),
            maturity_level=workflow_data.get("maturity_level", "basic")
        )

    async def _create_metrics(
        self,
        context,
        journey: List[WorkflowStepRecord]
    ) -> WorkflowMetrics:
        """Создать метрики"""

        # Duration
        if context.started_at:
            duration = datetime.utcnow() - context.started_at
            duration_days = duration.total_seconds() / 86400
        else:
            duration_days = 0

        # AI usage
        ai_used = sum(
            len([i for i in step.ai_interactions if i.accepted])
            for step in journey
        )

        ai_rejected = sum(
            len([i for i in step.ai_interactions if not i.accepted])
            for step in journey
        )

        # Module-specific metrics
        workflow_data = context.workflow_data
        module_metrics = {}

        if context.module == "bia":
            module_metrics = {
                "processes_identified": len(workflow_data.get("processes", [])),
                "critical_processes": len([
                    p for p in workflow_data.get("processes", [])
                    if p.get("tier") in [1, 2]
                ])
            }

        metrics = WorkflowMetrics(
            total_duration_days=duration_days,
            total_steps=len(journey),
            ai_recommendations_used=ai_used,
            ai_recommendations_rejected=ai_rejected,
            user_satisfaction=workflow_data.get("user_satisfaction"),
            completed_successfully=True,
            certification_ready=workflow_data.get("certification_ready", False),
            **module_metrics
        )

        return metrics

    async def _extract_success_patterns(
        self,
        journey: List[WorkflowStepRecord],
        workflow_data: Dict
    ) -> List[str]:
        """
        Извлечь success patterns через AI анализ

        Если LLM доступен, используем AI для анализа.
        Иначе - простая эвристика.
        """
        if self.llm_client:
            return await self._ai_extract_patterns(journey, workflow_data)
        else:
            return self._heuristic_extract_patterns(journey, workflow_data)

    async def _ai_extract_patterns(
        self,
        journey: List[WorkflowStepRecord],
        workflow_data: Dict
    ) -> List[str]:
        """AI анализ patterns"""

        # Подготовить данные для промпта
        journey_summary = "\n".join([
            f"Stage {i+1}: {step.stage} ({step.duration_hours:.1f}h) - "
            f"{len(step.actions_taken)} actions, "
            f"{len(step.ai_interactions)} AI interactions"
            for i, step in enumerate(journey)
        ])

        prompt = f"""
Analyze this workflow journey and identify success patterns:

{journey_summary}

Challenges faced:
{self._format_challenges(journey)}

Identify:
1. Actions that significantly accelerated progress
2. AI recommendations that were valuable
3. Best practices demonstrated
4. Effective problem-solving approaches

Format as bullet points (max 5 patterns).
"""

        try:
            response = await self.llm_client.generate(
                prompt=prompt,
                max_tokens=500,
                temperature=0.3
            )

            # Parse bullet points
            patterns = [
                line.strip().lstrip("- •")
                for line in response.text.split("\n")
                if line.strip() and (line.strip().startswith("-") or line.strip().startswith("•"))
            ]

            return patterns[:5]  # Max 5

        except Exception as e:
            logger.error(f"AI pattern extraction failed: {e}")
            return self._heuristic_extract_patterns(journey, workflow_data)

    def _heuristic_extract_patterns(
        self,
        journey: List[WorkflowStepRecord],
        workflow_data: Dict
    ) -> List[str]:
        """Эвристическое извлечение patterns"""
        patterns = []

        # Pattern 1: Early AI usage
        if journey and len(journey[0].ai_interactions) > 0:
            saved_time = sum(
                step.duration_hours
                for step in journey[:2]
                if len(step.ai_interactions) > 0
            )
            patterns.append(
                f"Used AI early in process - potentially saved {saved_time:.1f} hours"
            )

        # Pattern 2: Challenges resolved quickly
        quick_resolutions = [
            c for step in journey
            for c in step.challenges
            if c.time_to_resolve_hours < 24
        ]
        if len(quick_resolutions) > 0:
            patterns.append(
                f"Resolved {len(quick_resolutions)} challenges within 24 hours"
            )

        # Pattern 3: Consistent progress
        if journey:
            avg_step_duration = sum(s.duration_hours for s in journey) / len(journey)
            max_step_duration = max(s.duration_hours for s in journey)
            if max_step_duration < avg_step_duration * 2:
                patterns.append("Maintained consistent progress throughout workflow")

        return patterns

    async def _extract_lessons_learned(
        self,
        journey: List[WorkflowStepRecord],
        workflow_data: Dict
    ) -> List[str]:
        """Извлечь lessons learned"""

        lessons = []

        # Если есть explicit feedback
        if "lessons_learned" in workflow_data:
            lessons.extend(workflow_data["lessons_learned"])

        # Из challenges
        for step in journey:
            for challenge in step.challenges:
                if challenge.time_to_resolve_hours > 24:
                    lessons.append(
                        f"Lesson: {challenge.description} - {challenge.resolution}"
                    )

        return lessons[:5]  # Max 5

    async def _extract_best_practices(
        self,
        journey: List[WorkflowStepRecord],
        workflow_data: Dict
    ) -> List[str]:
        """Извлечь best practices"""

        practices = []

        # Если есть explicit feedback
        if "best_practices" in workflow_data:
            practices.extend(workflow_data["best_practices"])

        # Эвристика: что было сделано правильно
        # (например, использование templates, вовлечение stakeholders, etc)

        # Template usage
        if "used_templates" in workflow_data and workflow_data["used_templates"]:
            practices.append("Used industry-standard templates")

        # Stakeholder involvement
        if "stakeholders_involved" in workflow_data:
            practices.append("Involved key stakeholders early")

        return practices

    def _format_challenges(self, journey: List[WorkflowStepRecord]) -> str:
        """Форматировать challenges для промпта"""
        challenges = []
        for step in journey:
            for c in step.challenges:
                challenges.append(
                    f"- {c.type}: {c.description} (resolved in {c.time_to_resolve_hours:.1f}h)"
                )

        return "\n".join(challenges) if challenges else "No challenges recorded"

    def _generate_case_id(self, context) -> str:
        """Генерировать уникальный case ID"""
        timestamp = datetime.utcnow().strftime("%Y%m%d%H%M%S")
        return f"case-{context.module}-{timestamp}-{context.workflow_id[:8]}"

    async def _trigger_ml_retraining(self):
        """Триггерить переобучение ML моделей"""
        # Опционально: если есть ML predictor
        if hasattr(self, "ml_predictor"):
            try:
                await self.ml_predictor.schedule_retraining()
                logger.info("ML retraining scheduled")
            except Exception as e:
                logger.error(f"Failed to schedule ML retraining: {e}")


# ============================================================================
# BATCH COLLECTOR (для миграции существующих данных)
# ============================================================================

class BatchCaseCollector:
    """Сбор cases из уже завершённых workflows (миграция)"""

    def __init__(self, workflow_engine, case_repository, llm_client=None):
        self.workflow_engine = workflow_engine
        self.repository = case_repository
        self.llm_client = llm_client
        self.collector = CaseCollector(workflow_engine, case_repository, llm_client)

    async def collect_from_date_range(
        self,
        start_date: datetime,
        end_date: datetime,
        module: Optional[str] = None
    ) -> int:
        """
        Собрать cases из завершённых workflows за период

        Returns:
            Количество собранных cases
        """
        # Получить завершённые workflows за период
        workflows = await self.workflow_engine.storage.list_workflows(
            module=module,
            completed_after=start_date,
            completed_before=end_date,
            status="completed"
        )

        collected_count = 0

        for workflow in workflows:
            try:
                case = await self.collector.create_case(workflow["workflow_id"])
                if case:
                    await self.repository.save(case)
                    collected_count += 1
                    logger.info(f"Migrated case: {case.case_id}")

            except Exception as e:
                logger.error(
                    f"Failed to migrate workflow {workflow['workflow_id']}: {e}",
                    exc_info=True
                )

        logger.info(f"Batch collection completed: {collected_count} cases collected")

        return collected_count
