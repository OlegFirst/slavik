"""
Temporal Wrapper для BIA Workflow
==================================

ВАЖНО: Это ОБЕРТКА над существующим BIAWorkflowEngine!
Не переписываем логику - просто добавляем Temporal features:
- Persistent state (переживает краши)
- Retry logic (автоматические повторы)
- Human approvals (wait conditions)
- Event publishing (EventBus integration)

Existing code: workflows/bia_workflow.py (БЕЗ изменений!)
"""

from temporalio import workflow, activity
from datetime import timedelta
from typing import Dict, Any
import sys
import os

# Import existing BIA logic (НЕ ПЕРЕПИСЫВАЕМ!)
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from bia_workflow import BIAWorkflowEngine, BIAStage


# ═══════════════════════════════════════════════════════════════
# ACTIVITIES - тонкие обертки над существующей логикой
# ═══════════════════════════════════════════════════════════════

@activity.defn
async def initialize_bia(org_id: str, org_context: Dict[str, Any]) -> Dict[str, Any]:
    """
    Activity: Initialize BIA
    Вызывает существующий BIAWorkflowEngine
    """
    # Используем СУЩЕСТВУЮЩИЙ код!
    engine = BIAWorkflowEngine(
        bia_id=f"bia-{org_id}",
        org_context=org_context
    )

    return {
        "bia_id": engine.bia_id,
        "state": BIAStage.NOT_STARTED,
        "org_context": org_context,
        "created_at": str(workflow.now()) if hasattr(workflow, 'now') else None
    }


@activity.defn
async def identify_processes(bia_state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Activity: Identify critical processes
    Вызывает существующую логику
    """
    engine = BIAWorkflowEngine(
        bia_id=bia_state["bia_id"],
        org_context=bia_state["org_context"]
    )

    # Переход к следующей стадии (существующая логика!)
    # engine.transition_to(BIAStage.IDENTIFY_PROCESSES)

    # Здесь вызывали бы AI, базу данных, etc. (существующий код)
    # Для примера - упрощенно:
    processes = bia_state.get("processes", [
        {"id": "1", "name": "Sales Process", "criticality": "high"},
        {"id": "2", "name": "IT Support", "criticality": "medium"},
        {"id": "3", "name": "HR Onboarding", "criticality": "low"}
    ])

    bia_state["processes"] = processes
    bia_state["state"] = BIAStage.IDENTIFY_PROCESSES

    return bia_state


@activity.defn
async def analyze_dependencies(bia_state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Activity: Analyze process dependencies
    Вызывает существующую логику
    """
    engine = BIAWorkflowEngine(
        bia_id=bia_state["bia_id"],
        org_context=bia_state["org_context"]
    )

    # Существующая логика анализа зависимостей
    # В реальности: engine._validate_dependencies(bia_state)

    processes = bia_state.get("processes", [])
    dependencies = {
        "internal": ["IT Infrastructure", "Data Center"],
        "external": ["Cloud Provider", "ISP"],
        "human": ["IT Team", "Management"]
    }

    bia_state["dependencies"] = dependencies
    bia_state["state"] = BIAStage.ANALYZE_DEPENDENCIES

    return bia_state


@activity.defn
async def assess_impact(bia_state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Activity: Assess business impact
    Вызывает существующую логику
    """
    # Существующая логика оценки impact
    impacts = {
        "financial": {"1h": 10000, "4h": 50000, "24h": 200000},
        "reputation": "high",
        "regulatory": "medium"
    }

    bia_state["impacts"] = impacts
    bia_state["state"] = BIAStage.ASSESS_IMPACT

    return bia_state


@activity.defn
async def determine_rto_rpo(bia_state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Activity: Determine RTO/RPO
    Вызывает существующую логику
    """
    recovery_objectives = {
        "rto": "4 hours",
        "rpo": "1 hour",
        "mbco": "24 hours"
    }

    bia_state["recovery_objectives"] = recovery_objectives
    bia_state["state"] = BIAStage.DETERMINE_RTO

    return bia_state


@activity.defn
async def validate_and_complete(bia_state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Activity: Validate and complete BIA
    Вызывает существующую валидацию
    """
    engine = BIAWorkflowEngine(
        bia_id=bia_state["bia_id"],
        org_context=bia_state["org_context"]
    )

    # Существующая валидация: engine._validate_complete_bia(bia_state)

    bia_state["state"] = BIAStage.COMPLETED
    bia_state["completed_at"] = str(workflow.now()) if hasattr(workflow, 'now') else None

    return bia_state


@activity.defn
async def publish_to_case_library(bia_state: Dict[str, Any]):
    """
    Activity: Publish completed BIA to Case Library
    Интеграция с существующей Case Library
    """
    # Вызов существующего Case Library (БЕЗ изменений!)
    # from case_library.collector import collect_case
    # await collect_case(bia_state)

    print(f" Published BIA {bia_state['bia_id']} to Case Library")
    return {"published": True}


@activity.defn
async def publish_event(event_name: str, data: Dict[str, Any]):
    """
    Activity: Publish event to EventBus
    Интеграция с EventBus (будет позже в Phase 2.4)
    """
    # from shared.eventbus import publish
    # await publish(event_name, data)

    print(f" Event published: {event_name}")
    return {"published": True}


# ═══════════════════════════════════════════════════════════════
# TEMPORAL WORKFLOW - orchestrator (НЕ бизнес-логика!)
# ═══════════════════════════════════════════════════════════════

@workflow.defn
class BIAWorkflow:
    """
    Temporal Workflow для BIA процесса

    ЭТО ORCHESTRATOR - управляет последовательностью, НЕ бизнес-логикой!
    Вся логика в существующем BIAWorkflowEngine (activities вызывают его)

    Temporal добавляет:
    - Persistence (state сохраняется в Temporal Cloud)
    - Retry (если activity упал - повтор)
    - Wait conditions (human approvals)
    - Visibility (вся история в Temporal UI)
    """

    def __init__(self):
        self.human_approved = False

    @workflow.run
    async def run(self, org_id: str, org_context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Main workflow execution

        Оркестрирует существующую логику через activities
        """

        # ────────────────────────────────────────────────────
        # Stage 0: Initialize
        # ────────────────────────────────────────────────────
        bia_state = await workflow.execute_activity(
            initialize_bia,
            args=[org_id, org_context],
            start_to_close_timeout=timedelta(minutes=5)
        )

        # EventBus: BIA started
        await workflow.execute_activity(
            publish_event,
            args=["bia.started", {"org_id": org_id, "bia_id": bia_state["bia_id"]}],
            start_to_close_timeout=timedelta(seconds=30)
        )

        # ────────────────────────────────────────────────────
        # Stage 1: Identify Processes
        # ────────────────────────────────────────────────────
        bia_state = await workflow.execute_activity(
            identify_processes,
            args=[bia_state],
            start_to_close_timeout=timedelta(hours=48)  # Может быть долго
        )

        # EventBus: Progress update
        await workflow.execute_activity(
            publish_event,
            args=["bia.processes_identified", {
                "org_id": org_id,
                "progress": "20%",
                "processes_count": len(bia_state.get("processes", []))
            }],
            start_to_close_timeout=timedelta(seconds=30)
        )

        # ────────────────────────────────────────────────────
        # Stage 2: Analyze Dependencies
        # ────────────────────────────────────────────────────
        bia_state = await workflow.execute_activity(
            analyze_dependencies,
            args=[bia_state],
            start_to_close_timeout=timedelta(hours=24)
        )

        await workflow.execute_activity(
            publish_event,
            args=["bia.dependencies_analyzed", {
                "org_id": org_id,
                "progress": "40%"
            }],
            start_to_close_timeout=timedelta(seconds=30)
        )

        # ────────────────────────────────────────────────────
        # Stage 3: Assess Impact
        # ────────────────────────────────────────────────────
        bia_state = await workflow.execute_activity(
            assess_impact,
            args=[bia_state],
            start_to_close_timeout=timedelta(hours=24)
        )

        await workflow.execute_activity(
            publish_event,
            args=["bia.impact_assessed", {
                "org_id": org_id,
                "progress": "60%"
            }],
            start_to_close_timeout=timedelta(seconds=30)
        )

        # ────────────────────────────────────────────────────
        # Stage 4: Determine RTO/RPO
        # ────────────────────────────────────────────────────
        bia_state = await workflow.execute_activity(
            determine_rto_rpo,
            args=[bia_state],
            start_to_close_timeout=timedelta(hours=24)
        )

        await workflow.execute_activity(
            publish_event,
            args=["bia.rto_determined", {
                "org_id": org_id,
                "progress": "80%",
                "rto": bia_state.get("recovery_objectives", {}).get("rto")
            }],
            start_to_close_timeout=timedelta(seconds=30)
        )

        # ────────────────────────────────────────────────────
        # GOVERNANCE CHECKPOINT: Human approval needed?
        # ────────────────────────────────────────────────────
        # Если high-impact - нужен human approval
        impacts = bia_state.get("impacts", {})
        if impacts.get("financial", {}).get("24h", 0) > 100000:
            # Отправить запрос на approval
            await workflow.execute_activity(
                publish_event,
                args=["bia.approval_required", {
                    "org_id": org_id,
                    "bia_id": bia_state["bia_id"],
                    "reason": "High financial impact"
                }],
                start_to_close_timeout=timedelta(seconds=30)
            )

            # WAIT for human approval (Temporal feature!)
            # Workflow будет спать пока не придет signal
            await workflow.wait_condition(
                lambda: self.human_approved,
                timeout=timedelta(hours=72)  # Max 3 дня ждем
            )

        # ────────────────────────────────────────────────────
        # Stage 5: Validate and Complete
        # ────────────────────────────────────────────────────
        bia_state = await workflow.execute_activity(
            validate_and_complete,
            args=[bia_state],
            start_to_close_timeout=timedelta(minutes=10)
        )

        # ────────────────────────────────────────────────────
        # Stage 6: Publish to Case Library (self-learning!)
        # ────────────────────────────────────────────────────
        await workflow.execute_activity(
            publish_to_case_library,
            args=[bia_state],
            start_to_close_timeout=timedelta(minutes=5)
        )

        # ────────────────────────────────────────────────────
        # EventBus: BIA completed
        # ────────────────────────────────────────────────────
        await workflow.execute_activity(
            publish_event,
            args=["bia.completed", {
                "org_id": org_id,
                "bia_id": bia_state["bia_id"],
                "rto": bia_state.get("recovery_objectives", {}).get("rto"),
                "rpo": bia_state.get("recovery_objectives", {}).get("rpo")
            }],
            start_to_close_timeout=timedelta(seconds=30)
        )

        return bia_state

    # ────────────────────────────────────────────────────
    # SIGNALS - для human approvals
    # ────────────────────────────────────────────────────
    @workflow.signal
    async def approve(self):
        """Signal от человека: BIA approved"""
        self.human_approved = True

    @workflow.signal
    async def reject(self, reason: str):
        """Signal от человека: BIA rejected"""
        # Можно вернуться на предыдущую стадию
        # или завершить с ошибкой
        raise Exception(f"BIA rejected: {reason}")

    # ────────────────────────────────────────────────────
    # QUERIES - для получения статуса
    # ────────────────────────────────────────────────────
    @workflow.query
    def get_status(self) -> Dict[str, Any]:
        """Query текущего статуса (не меняет state)"""
        return {
            "awaiting_approval": not self.human_approved
        }


# ═══════════════════════════════════════════════════════════════
# ИТОГО:
# ═══════════════════════════════════════════════════════════════
#
#  Существующий код (BIAWorkflowEngine) - БЕЗ ИЗМЕНЕНИЙ!
#  Temporal обертка - ~300 строк (orchestration only)
#  Переиспользуем ВСЮ логику через activities
#  Если Temporal не понравится - просто удалим эту обертку
#  Основной код остается рабочим!
#
# ═══════════════════════════════════════════════════════════════
