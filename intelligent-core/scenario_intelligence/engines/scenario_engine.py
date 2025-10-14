"""
Scenario Engine - Main Orchestrator

Оркестрирует выполнение всех типов сценариев через подчиненные движки
"""

import asyncio
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime
import copy
import uuid

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Import EventBus integration
try:
    from integrations.eventbus_client import get_eventbus_client
    from events.scenario_events import create_scenario_executed_event
    EVENTBUS_AVAILABLE = True
except ImportError:
    EVENTBUS_AVAILABLE = False
    logger.warning("EventBus integration not available for ScenarioEngine")


class ScenarioEngine:
    """
    Главный движок исполнения сценариев

    Координирует:
    - Call Engine (BPMN Call Activity)
    - Event Engine (Event Storming)
    - Chaos Engine (Netflix)
    - Compliance Engine (ISO)
    """

    def __init__(self, eventbus_client=None):
        # Lazy loading подчиненных движков
        self._call_engine = None
        self._event_engine = None
        self._chaos_engine = None
        self._compliance_engine = None

        # EventBus integration
        self.eventbus_client = eventbus_client
        if self.eventbus_client is None and EVENTBUS_AVAILABLE:
            try:
                self.eventbus_client = get_eventbus_client()
            except Exception as e:
                logger.warning(f"Could not get global EventBus client: {e}")

        # Для хранения результатов
        self.execution_context = {}

    @property
    def call_engine(self):
        """Lazy load Call Engine"""
        if self._call_engine is None:
            from .call_engine import CallEngine
            self._call_engine = CallEngine()
        return self._call_engine

    @property
    def event_engine(self):
        """Lazy load Event Engine"""
        if self._event_engine is None:
            from .event_engine import EventEngine
            self._event_engine = EventEngine()
        return self._event_engine

    @property
    def chaos_engine(self):
        """Lazy load Chaos Engine"""
        if self._chaos_engine is None:
            from .chaos_engine import ChaosEngine
            self._chaos_engine = ChaosEngine()
        return self._chaos_engine

    @property
    def compliance_engine(self):
        """Lazy load Compliance Engine"""
        if self._compliance_engine is None:
            from .compliance_engine import ComplianceEngine
            self._compliance_engine = ComplianceEngine()
        return self._compliance_engine

    async def execute_scenario(
        self,
        scenario: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Главный метод - выполнить сценарий любого типа/уровня

        Args:
            scenario: Сценарий в формате YAML
            context: Контекст выполнения

        Returns:
            Результаты выполнения
        """

        # Handle both formats: {"scenario": {...}} and direct {...}
        if 'scenario' in scenario:
            scenario = scenario['scenario']

        context = context or {}
        start_time = datetime.utcnow()

        # Extract metadata
        meta = scenario.get('meta', {})
        scenario_id = meta.get('id', 'unknown')
        scenario_level = meta.get('level', 0)
        scenario_type = meta.get('type', 'unknown')

        logger.info(f"🎬 Executing scenario: {scenario_id} (Level {scenario_level}, Type: {scenario_type})")

        try:
            # 1. Выполнить шаги сценария
            execution_result = await self._execute_steps(scenario, context)

            # 2. Обработать Call Activity (синхронные вызовы других сценариев)
            if 'integration' in scenario and 'calls' in scenario.get('integration', {}):
                logger.info(f"  📞 Processing Call Activity...")
                call_results = await self.call_engine.execute_calls(
                    scenario['integration']['calls'],
                    {**context, **execution_result.get('context', {})}
                )
                execution_result['call_results'] = call_results

            # 3. Обработать Events (асинхронные события)
            if 'integration' in scenario and 'events' in scenario.get('integration', {}):
                events_config = scenario['integration']['events']

                if 'emits' in events_config:
                    logger.info(f"  📡 Emitting events...")
                    await self.event_engine.emit_events(
                        events_config['emits'],
                        {**context, **execution_result.get('context', {})}
                    )

            # 4. Если это chaos сценарий - запустить chaos engine
            if 'chaos' in scenario:
                logger.info(f"  💥 Executing Chaos Experiment...")
                chaos_result = await self.chaos_engine.execute_chaos(
                    scenario['chaos'],
                    {**context, **execution_result.get('context', {})}
                )
                execution_result['chaos_result'] = chaos_result

            # 5. Проверить compliance
            if 'compliance' in scenario:
                logger.info(f"  ✅ Checking Compliance...")
                compliance_result = await self.compliance_engine.check_compliance(
                    scenario['compliance'],
                    execution_result
                )
                execution_result['compliance'] = compliance_result

            # 6. Отправить результаты в learning system
            await self._send_to_learning(scenario, execution_result, context)

            # Calculate duration
            end_time = datetime.utcnow()
            duration = (end_time - start_time).total_seconds()

            result = {
                'scenario_id': scenario_id,
                'status': 'success',
                'result': execution_result,
                'duration': duration,
                'executed_at': start_time.isoformat(),
                'completed_at': end_time.isoformat()
            }

            # 7. Publish EventBus event
            await self._publish_execution_event(
                scenario_id=scenario_id,
                execution_id=str(uuid.uuid4()),
                status='success',
                duration_ms=duration * 1000,
                steps_executed=execution_result.get('steps_executed', 0),
                steps_failed=0
            )

            return result

        except Exception as e:
            logger.error(f"❌ Scenario {scenario_id} failed: {e}", exc_info=True)

            end_time = datetime.utcnow()
            duration = (end_time - start_time).total_seconds()

            result = {
                'scenario_id': scenario_id,
                'status': 'error',
                'error': str(e),
                'duration': duration,
                'executed_at': start_time.isoformat(),
                'completed_at': end_time.isoformat()
            }

            # Publish failure event
            await self._publish_execution_event(
                scenario_id=scenario_id,
                execution_id=str(uuid.uuid4()),
                status='failed',
                duration_ms=duration * 1000,
                steps_executed=0,
                steps_failed=1,
                error=str(e)
            )

            return result
            }

    async def _execute_steps(
        self,
        scenario: Dict[str, Any],
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Выполнить шаги из execution.steps
        """

        steps = scenario.get('execution', {}).get('steps', [])

        if not steps:
            logger.warning("  ⚠️  No execution steps defined")
            return {'steps': [], 'context': context}

        results = []
        local_context = copy.deepcopy(context)

        for step in steps:
            step_id = step.get('id', 'unknown')
            action = step.get('action', 'unknown')

            logger.info(f"  ▶️  Step: {step_id} (action: {action})")

            try:
                # Выполнить action
                step_result = await self._execute_action(step, local_context)

                # Обработать on_error (BPMN Boundary Events)
                if step_result.get('error') and 'on_error' in step:
                    logger.warning(f"    ⚠️  Error detected, handling...")
                    step_result = await self._handle_error(
                        step['on_error'],
                        step_result,
                        local_context
                    )

                # Обработать вложенные calls
                if 'calls' in step:
                    logger.info(f"    📞 Step has nested calls...")
                    call_results = await self.call_engine.execute_calls(
                        step['calls'],
                        local_context
                    )
                    step_result['call_results'] = call_results

                results.append({
                    'step_id': step_id,
                    'status': 'success' if not step_result.get('error') else 'error',
                    'result': step_result
                })

                # Обновить контекст для следующих шагов
                local_context[f"steps.{step_id}"] = step_result

                # Validate expectations
                if 'expect' in step:
                    self._validate_expectations(step['expect'], step_result)

            except Exception as e:
                logger.error(f"    ❌ Step {step_id} failed: {e}")
                results.append({
                    'step_id': step_id,
                    'status': 'error',
                    'error': str(e)
                })

                # Stop execution on error (можно сделать опциональным)
                if step.get('stop_on_error', True):
                    break

        return {
            'steps': results,
            'context': local_context
        }

    async def _execute_action(
        self,
        step: Dict[str, Any],
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Выполнить конкретный action
        """

        action = step.get('action')
        params = step.get('params', {})

        # Resolve variables like {{user_id}}
        resolved_params = self._resolve_params(params, context)

        # Симуляция выполнения (в реальности - вызов сервисов)
        # TODO: Интеграция с реальными сервисами

        logger.info(f"    🔧 Executing action: {action}")
        logger.debug(f"       Params: {resolved_params}")

        # Для тестирования - возвращаем mock результат
        return {
            'status': 200,
            'action': action,
            'params': resolved_params,
            'simulated': True,
            'timestamp': datetime.utcnow().isoformat()
        }

    def _resolve_params(
        self,
        params: Dict[str, Any],
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Resolve переменных вида {{variable}} из контекста
        """

        if not params:
            return {}

        resolved = {}

        for key, value in params.items():
            if isinstance(value, str) and value.startswith("{{") and value.endswith("}}"):
                # Variable substitution
                var_path = value[2:-2].strip()
                resolved_value = self._get_from_context(var_path, context)
                resolved[key] = resolved_value if resolved_value is not None else value
            elif isinstance(value, dict):
                resolved[key] = self._resolve_params(value, context)
            elif isinstance(value, list):
                resolved[key] = [
                    self._resolve_params(item, context) if isinstance(item, dict) else item
                    for item in value
                ]
            else:
                resolved[key] = value

        return resolved

    def _get_from_context(
        self,
        path: str,
        context: Dict[str, Any]
    ) -> Any:
        """
        Получить значение из контекста по пути вида 'steps.step1.result.id'
        """

        parts = path.split('.')
        value = context

        for part in parts:
            if isinstance(value, dict):
                value = value.get(part)
                if value is None:
                    return None
            else:
                return None

        return value

    def _validate_expectations(
        self,
        expectations: Dict[str, Any],
        result: Dict[str, Any]
    ):
        """
        Validate результата против ожиданий
        """

        # Проверить status
        if 'status' in expectations:
            expected_status = expectations['status']
            actual_status = result.get('status')

            if actual_status != expected_status:
                logger.warning(f"    ⚠️  Expected status {expected_status}, got {actual_status}")

        # Проверить наличие полей
        if 'response_contains' in expectations:
            for field in expectations['response_contains']:
                if field not in result:
                    logger.warning(f"    ⚠️  Expected field '{field}' not in response")

    async def _handle_error(
        self,
        error_handlers: List[Dict[str, Any]],
        error_result: Dict[str, Any],
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Обработать ошибку через BPMN Boundary Events
        """

        error_type = error_result.get('error_type', 'unknown')

        for handler in error_handlers:
            handler_type = handler.get('type')

            if handler_type == error_type or handler_type == 'any':
                action = handler.get('action')

                logger.info(f"    🔧 Handling error with action: {action}")

                if action == 'retry':
                    max_retries = handler.get('max_retries', 3)
                    # TODO: Implement retry logic
                    return error_result

                elif action == 'use_fallback':
                    fallback_value = handler.get('fallback_value')
                    return {
                        'status': 200,
                        'fallback': True,
                        'value': fallback_value
                    }

                elif action == 'abort':
                    raise Exception(f"Error handler aborted execution: {error_type}")

        return error_result

    async def _publish_execution_event(
        self,
        scenario_id: str,
        execution_id: str,
        status: str,
        duration_ms: float,
        steps_executed: int = 0,
        steps_failed: int = 0,
        error: Optional[str] = None
    ):
        """
        Publish scenario execution event to EventBus

        Args:
            scenario_id: Scenario ID
            execution_id: Unique execution ID
            status: Execution status (success, failed, timeout)
            duration_ms: Duration in milliseconds
            steps_executed: Number of steps executed
            steps_failed: Number of steps failed
            error: Error message if failed
        """
        if not self.eventbus_client or not EVENTBUS_AVAILABLE:
            return

        try:
            event = create_scenario_executed_event(
                scenario_id=scenario_id,
                execution_id=execution_id,
                status=status,
                duration_ms=duration_ms,
                steps_executed=steps_executed,
                steps_failed=steps_failed,
                error=error,
                metadata={
                    "executed_at": datetime.utcnow().isoformat()
                }
            )
            await self.eventbus_client.publish_scenario_executed(event)
        except Exception as e:
            logger.warning(f"Failed to publish execution event: {e}")

    async def _send_to_learning(
        self,
        scenario: Dict[str, Any],
        result: Dict[str, Any],
        context: Dict[str, Any]
    ):
        """
        Отправить результаты в learning system
        """

        try:
            from learning.scenario_learner import ScenarioLearner
            learner = ScenarioLearner()

            await learner.record_execution(
                scenario_id=scenario['meta']['id'],
                scenario=scenario,
                result=result,
                context=context
            )
        except Exception as e:
            logger.warning(f"  ⚠️  Failed to send to learning system: {e}")


# Test
async def main():
    """Test Scenario Engine"""

    # Простой тестовый сценарий
    test_scenario = {
        'meta': {
            'id': 'test-simple-scenario',
            'version': '1.0.0',
            'level': 1,
            'type': 'functional'
        },
        'description': {
            'title': 'Test Simple Scenario',
            'summary': 'Test scenario execution'
        },
        'execution': {
            'steps': [
                {
                    'id': 'step1',
                    'action': 'test.action',
                    'params': {
                        'message': 'Hello World'
                    },
                    'expect': {
                        'status': 200
                    }
                },
                {
                    'id': 'step2',
                    'action': 'test.action2',
                    'params': {
                        'previous_result': '{{steps.step1.result}}'
                    }
                }
            ]
        }
    }

    engine = ScenarioEngine()
    result = await engine.execute_scenario(test_scenario)

    print("\n" + "="*60)
    print("SCENARIO EXECUTION RESULT:")
    print("="*60)
    import json
    print(json.dumps(result, indent=2, default=str))


if __name__ == "__main__":
    asyncio.run(main())
