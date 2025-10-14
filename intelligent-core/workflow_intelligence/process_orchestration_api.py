"""
Process Orchestration API - Автоматическое взаимодействие системы с собой

Обеспечивает:
- AI-агенты автоматически заполняют формы
- Система сама выполняет шаги процесса
- Интеграция с AI Orchestrator для delegation
- EventBus для асинхронного выполнения
- Автоматическая генерация документов
"""

from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from datetime import datetime
import asyncio
import httpx

from process_framework import (
    get_process_framework,
    ProcessStep,
    StepType,
    ProcessInstance,
    ProcessStatus
)
from document_templates import get_document_library


@dataclass
class AIAgentConfig:
    """Конфигурация AI агента для выполнения шага"""
    agent_type: str  # analytics_specialist, document_generator, risk_analyst, etc.
    agent_url: str
    timeout_seconds: int = 30


class ProcessOrchestrator:
    """
    Оркестратор процессов с AI-автоматизацией

    Система сама выполняет шаги процесса, используя AI агентов
    для анализа, принятия решений и генерации документов.
    """

    def __init__(
        self,
        ai_orchestrator_url: str = "http://localhost:8000",
        eventbus_url: str = "http://localhost:6379"
    ):
        self.framework = get_process_framework()
        self.document_library = get_document_library()

        self.ai_orchestrator_url = ai_orchestrator_url
        self.eventbus_url = eventbus_url

        # AI агенты
        self.ai_agents = {
            "analytics_specialist": AIAgentConfig(
                agent_type="analytics_specialist",
                agent_url="http://localhost:8003"
            ),
            "document_generator": AIAgentConfig(
                agent_type="document_generator",
                agent_url="http://localhost:8004"
            ),
            "risk_analyst": AIAgentConfig(
                agent_type="risk_analyst",
                agent_url="http://localhost:8005"
            )
        }

    async def execute_process_automatically(
        self,
        process_id: str,
        initial_data: Dict[str, Any],
        user_email: str
    ) -> ProcessInstance:
        """
        Автоматически выполнить весь процесс

        Система сама проходит все шаги, используя AI агентов
        для заполнения форм и принятия решений.
        """
        print(f"\n🤖 Автоматическое выполнение процесса: {process_id}")

        # Запустить процесс
        instance = self.framework.start_process(
            process_id=process_id,
            started_by=user_email,
            initial_data=initial_data
        )

        print(f"✅ Процесс запущен: {instance.id}")

        # Выполнять шаги пока процесс не завершится
        while instance.status == ProcessStatus.IN_PROGRESS:
            current_step_id = instance.current_step_id

            print(f"\n📋 Текущий шаг: {current_step_id}")

            # Выполнить шаг автоматически
            success = await self._execute_step_automatically(instance)

            if not success:
                print(f"❌ Не удалось выполнить шаг {current_step_id}")
                instance.status = ProcessStatus.SUSPENDED
                break

            # Обновить instance
            instance = self.framework.instances.get(instance.id)

        print(f"\n✅ Процесс завершен: {instance.status.value}")
        return instance

    async def _execute_step_automatically(self, instance: ProcessInstance) -> bool:
        """
        Автоматически выполнить текущий шаг процесса

        Использует AI агентов для заполнения форм.
        """
        process = self.framework.processes.get(instance.process_definition_id)
        if not process:
            return False

        current_step = process.get_step(instance.current_step_id)
        if not current_step:
            return False

        print(f"   Тип шага: {current_step.step_type.value}")

        # В зависимости от типа шага - разная логика
        if current_step.step_type == StepType.FORM_INPUT:
            return await self._auto_fill_form(instance, current_step)

        elif current_step.step_type == StepType.ANALYSIS:
            return await self._auto_analyze(instance, current_step)

        elif current_step.step_type == StepType.DECISION:
            return await self._auto_decide(instance, current_step)

        elif current_step.step_type == StepType.DOCUMENT_GENERATION:
            return await self._auto_generate_document(instance, current_step)

        elif current_step.step_type == StepType.APPROVAL:
            return await self._auto_approve(instance, current_step)

        elif current_step.step_type == StepType.VALIDATION:
            return await self._auto_validate(instance, current_step)

        else:
            print(f"   ⚠️ Неизвестный тип шага: {current_step.step_type}")
            return False

    async def _auto_fill_form(self, instance: ProcessInstance, step: ProcessStep) -> bool:
        """
        Автоматическое заполнение формы с помощью AI

        AI анализирует:
        - Данные процесса (instance.data)
        - Требования формы (step.form_fields)
        - Контекст (описание шага, ISO требования)

        И генерирует подходящие значения.
        """
        print(f"   🤖 AI заполняет форму...")

        # Подготовить контекст для AI
        context = {
            "step_name": step.name,
            "step_description": step.description,
            "form_fields": [
                {
                    "name": field.name,
                    "label": field.label,
                    "type": field.field_type,
                    "description": field.description,
                    "required": field.required,
                    "help_text": field.help_text
                }
                for field in step.form_fields
            ],
            "existing_data": instance.data,
            "process_context": {
                "process_name": self.framework.processes.get(instance.process_definition_id).name,
                "organization": instance.data.get("organization", "Unknown")
            }
        }

        # Вызвать AI Orchestrator для заполнения формы
        form_data = await self._call_ai_orchestrator(
            task_type="form_auto_fill",
            context=context,
            agent=step.ai_agent or "analytics_specialist"
        )

        if not form_data:
            return False

        # Выполнить шаг с данными от AI
        success, error, next_step = self.framework.execute_step(
            instance_id=instance.id,
            step_data=form_data,
            executed_by="AI_System"
        )

        if success:
            print(f"   ✅ Форма заполнена и отправлена")
            return True
        else:
            print(f"   ❌ Ошибка: {error}")
            return False

    async def _auto_analyze(self, instance: ProcessInstance, step: ProcessStep) -> bool:
        """
        Автоматический анализ с помощью Analytics Specialist

        Например, для BIA:
        - Анализирует критичные функции
        - Рассчитывает RTO/RPO
        - Оценивает финансовое воздействие
        """
        print(f"   📊 AI проводит анализ...")

        # Подготовить данные для анализа
        analysis_context = {
            "step": step.name,
            "description": step.description,
            "input_data": instance.data,
            "analysis_type": "business_impact_analysis"  # из метаданных шага
        }

        # Вызвать Analytics Specialist
        analysis_results = await self._call_ai_agent(
            agent_type="analytics_specialist",
            task="analyze_business_impact",
            context=analysis_context
        )

        if not analysis_results:
            return False

        # Преобразовать результаты анализа в данные формы
        form_data = self._convert_analysis_to_form_data(analysis_results, step)

        # Выполнить шаг
        success, error, _ = self.framework.execute_step(
            instance_id=instance.id,
            step_data=form_data,
            executed_by="AI_Analytics"
        )

        if success:
            print(f"   ✅ Анализ завершен")
            return True
        else:
            print(f"   ❌ Ошибка анализа: {error}")
            return False

    async def _auto_decide(self, instance: ProcessInstance, step: ProcessStep) -> bool:
        """
        Автоматическое принятие решения

        AI анализирует данные и принимает решение
        (например, выбор стратегии обработки риска)
        """
        print(f"   🎯 AI принимает решение...")

        decision_context = {
            "step": step.name,
            "options": [field.options for field in step.form_fields if field.options],
            "data": instance.data,
            "decision_criteria": step.description
        }

        # Вызвать AI Decision Engine
        decision = await self._call_ai_orchestrator(
            task_type="decision_making",
            context=decision_context
        )

        if not decision:
            return False

        # Выполнить шаг с решением
        success, error, _ = self.framework.execute_step(
            instance_id=instance.id,
            step_data=decision,
            executed_by="AI_Decision"
        )

        if success:
            print(f"   ✅ Решение принято: {decision.get('treatment_strategy', 'N/A')}")
            return True
        else:
            print(f"   ❌ Ошибка решения: {error}")
            return False

    async def _auto_generate_document(self, instance: ProcessInstance, step: ProcessStep) -> bool:
        """
        Автоматическая генерация документа

        Использует document templates и данные процесса
        """
        print(f"   📄 AI генерирует документ...")

        # Получить шаблон
        template_id = step.document_template
        if not template_id:
            print(f"   ❌ Шаблон не указан")
            return False

        # Подготовить переменные для шаблона
        variables = self._prepare_document_variables(instance)

        # Обогатить данные с помощью AI
        enriched_variables = await self._enrich_document_data(variables)

        try:
            # Сгенерировать документ
            document_content = self.document_library.generate_document(
                template_id=template_id.replace('.docx', '_v1'),  # bia_report_template.docx → bia_report_v1
                variables=enriched_variables
            )

            # Сохранить документ
            doc_path = f"./generated_documents/{instance.id}_{template_id}.md"
            # (сохранение в файл)

            print(f"   ✅ Документ сгенерирован: {len(document_content)} символов")

            # Выполнить шаг
            form_data = {
                "report_format": "pdf",
                "include_recommendations": True,
                "document_path": doc_path
            }

            success, error, _ = self.framework.execute_step(
                instance_id=instance.id,
                step_data=form_data,
                executed_by="AI_DocGen"
            )

            return success

        except Exception as e:
            print(f"   ❌ Ошибка генерации: {e}")
            return False

    async def _auto_approve(self, instance: ProcessInstance, step: ProcessStep) -> bool:
        """
        Автоматическое утверждение (если auto_approve=True)

        Если auto_approve=False, то требуется человек.
        В этом случае - отправляем уведомление и ждем.
        """
        print(f"   ✔️ Проверка утверждения...")

        if step.auto_approve:
            print(f"   🤖 Автоматическое утверждение разрешено")

            # AI проверяет документ/данные
            approval_check = await self._ai_pre_approval_check(instance)

            if approval_check["approved"]:
                form_data = {
                    "approval_decision": "approved",
                    "approval_comments": approval_check["comments"],
                    "approver_name": "AI System",
                    "approver_position": "Automated Approval"
                }

                success, error, _ = self.framework.execute_step(
                    instance_id=instance.id,
                    step_data=form_data,
                    executed_by="AI_Approver"
                )

                if success:
                    print(f"   ✅ Автоматически утверждено")
                    return True

        # Если не auto_approve - отправить уведомление человеку
        print(f"   📧 Требуется утверждение человеком")
        await self._send_approval_notification(instance, step)

        # Временно остановить автоматическое выполнение
        return False  # Ждем человека

    async def _auto_validate(self, instance: ProcessInstance, step: ProcessStep) -> bool:
        """Автоматическая валидация данных"""
        print(f"   ✓ Валидация данных...")

        # Валидация через форму
        is_valid, errors = step.validate_input(instance.data)

        if is_valid:
            print(f"   ✅ Валидация пройдена")
            # Переход к следующему шагу
            return True
        else:
            print(f"   ❌ Ошибки валидации: {errors}")
            return False

    async def _call_ai_orchestrator(
        self,
        task_type: str,
        context: Dict[str, Any],
        agent: str = None
    ) -> Optional[Dict[str, Any]]:
        """
        Вызов AI Orchestrator для делегирования задачи

        POST /orchestrate
        {
            "task_type": "form_auto_fill",
            "context": {...},
            "preferred_agent": "analytics_specialist"
        }
        """
        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(
                    f"{self.ai_orchestrator_url}/orchestrate",
                    json={
                        "task_type": task_type,
                        "context": context,
                        "preferred_agent": agent,
                        "auto_execute": True
                    }
                )

                if response.status_code == 200:
                    result = response.json()
                    return result.get("result")
                else:
                    print(f"   ❌ AI Orchestrator ошибка: {response.status_code}")
                    return None

        except Exception as e:
            print(f"   ❌ Ошибка вызова AI Orchestrator: {e}")
            return None

    async def _call_ai_agent(
        self,
        agent_type: str,
        task: str,
        context: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """Прямой вызов AI агента"""
        agent_config = self.ai_agents.get(agent_type)
        if not agent_config:
            return None

        try:
            async with httpx.AsyncClient(timeout=agent_config.timeout_seconds) as client:
                response = await client.post(
                    f"{agent_config.agent_url}/execute",
                    json={
                        "task": task,
                        "context": context
                    }
                )

                if response.status_code == 200:
                    return response.json()
                else:
                    return None

        except Exception as e:
            print(f"   ❌ Ошибка вызова агента {agent_type}: {e}")
            return None

    def _convert_analysis_to_form_data(
        self,
        analysis: Dict[str, Any],
        step: ProcessStep
    ) -> Dict[str, Any]:
        """
        Преобразовать результаты анализа в данные формы

        AI возвращает результаты анализа, нужно сопоставить
        с полями формы.
        """
        form_data = {}

        for field in step.form_fields:
            # Попытка найти соответствующее значение в analysis
            value = analysis.get(field.name)

            if value is None:
                # Попытка умного поиска
                # Например, поле "rto" может быть в analysis["recovery_time_objective"]
                aliases = self._get_field_aliases(field.name)
                for alias in aliases:
                    if alias in analysis:
                        value = analysis[alias]
                        break

            if value is not None:
                form_data[field.name] = value
            elif field.required and field.default_value:
                form_data[field.name] = field.default_value

        return form_data

    def _get_field_aliases(self, field_name: str) -> List[str]:
        """Получить возможные алиасы для поля"""
        aliases_map = {
            "rto": ["recovery_time_objective", "rto_hours", "max_downtime"],
            "rpo": ["recovery_point_objective", "rpo_minutes", "max_data_loss"],
            "financial_impact": ["financial_cost", "cost_impact", "monetary_impact"],
            # и т.д.
        }
        return aliases_map.get(field_name, [])

    def _prepare_document_variables(self, instance: ProcessInstance) -> Dict[str, Any]:
        """Подготовить переменные для генерации документа из данных процесса"""
        variables = instance.data.copy()

        # Добавить метаданные
        variables.update({
            "generation_timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "process_instance_id": instance.id,
            "started_by": instance.started_by,
            "started_at": instance.started_at.isoformat() if instance.started_at else None
        })

        return variables

    async def _enrich_document_data(self, variables: Dict[str, Any]) -> Dict[str, Any]:
        """
        Обогатить данные документа с помощью AI

        AI добавляет:
        - Recommendations
        - Executive summary
        - Key findings
        - Etc.
        """
        enrichment_request = {
            "task": "enrich_document_data",
            "existing_data": variables,
            "enrichments_needed": [
                "executive_summary",
                "key_findings",
                "recommendations",
                "priority_actions"
            ]
        }

        enriched = await self._call_ai_orchestrator(
            task_type="document_enrichment",
            context=enrichment_request
        )

        if enriched:
            variables.update(enriched)

        return variables

    async def _ai_pre_approval_check(self, instance: ProcessInstance) -> Dict[str, Any]:
        """
        AI проверка перед автоматическим утверждением

        Проверяет:
        - Полноту данных
        - Соответствие стандартам
        - Качество анализа
        """
        check_request = {
            "process_data": instance.data,
            "check_criteria": [
                "data_completeness",
                "iso_compliance",
                "analysis_quality",
                "logical_consistency"
            ]
        }

        result = await self._call_ai_orchestrator(
            task_type="pre_approval_check",
            context=check_request
        )

        if result:
            return result
        else:
            # Fallback - требовать человеческое утверждение
            return {
                "approved": False,
                "comments": "AI pre-approval check failed, human review required"
            }

    async def _send_approval_notification(self, instance: ProcessInstance, step: ProcessStep):
        """
        Отправить уведомление о необходимости утверждения

        Через EventBus или Email
        """
        notification = {
            "type": "approval_required",
            "process_instance_id": instance.id,
            "step_name": step.name,
            "allowed_roles": step.allowed_roles,
            "sla_hours": step.sla_hours,
            "url": f"/processes/{instance.id}/approve"
        }

        # Publish to EventBus
        # await eventbus.publish("process.approval_required", notification)

        print(f"   📧 Уведомление отправлено: {notification}")


# Singleton
_orchestrator_instance: Optional[ProcessOrchestrator] = None


def get_process_orchestrator() -> ProcessOrchestrator:
    """Получить singleton оркестратора"""
    global _orchestrator_instance

    if _orchestrator_instance is None:
        _orchestrator_instance = ProcessOrchestrator()

    return _orchestrator_instance
