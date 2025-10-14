"""
Call Engine - BPMN Call Activity Implementation

Обрабатывает синхронные вызовы других сценариев
"""

import asyncio
import logging
from typing import Dict, Any, List, Optional

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class CallEngine:
    """
    Движок для синхронных вызовов сценариев (BPMN Call Activity)

    Поддерживает:
    - Последовательные вызовы
    - Параллельные вызовы (parallel: true)
    - Input/Output mapping
    - Timeout handling
    """

    def __init__(self):
        self._registry = None

    @property
    def registry(self):
        """Lazy load Registry"""
        if self._registry is None:
            from storage.registry import ScenarioRegistry
            self._registry = ScenarioRegistry()
        return self._registry

    async def execute_calls(
        self,
        calls: List[Dict[str, Any]],
        context: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Выполнить список вызовов

        Args:
            calls: Список вызовов [{'scenario_id': ..., 'params': ...}]
            context: Контекст выполнения

        Returns:
            Список результатов
        """

        if not calls:
            return []

        # Разделить на параллельные и последовательные
        parallel_calls = [c for c in calls if c.get('parallel', False)]
        sequential_calls = [c for c in calls if not c.get('parallel', False)]

        results = []

        # Выполнить параллельные вызовы
        if parallel_calls:
            logger.info(f"    📞 Executing {len(parallel_calls)} calls in parallel...")

            parallel_results = await asyncio.gather(*[
                self._execute_single_call(call, context)
                for call in parallel_calls
            ], return_exceptions=True)

            # Обработать исключения
            for i, result in enumerate(parallel_results):
                if isinstance(result, Exception):
                    logger.error(f"    ❌ Parallel call {i} failed: {result}")
                    results.append({
                        'status': 'error',
                        'error': str(result),
                        'call_index': i
                    })
                else:
                    results.append(result)

        # Выполнить последовательные вызовы
        if sequential_calls:
            logger.info(f"    📞 Executing {len(sequential_calls)} calls sequentially...")

            for call in sequential_calls:
                call_result = await self._execute_single_call(call, context)
                results.append(call_result)

                # Обновить контекст для следующего вызова
                if call_result.get('status') == 'success' and 'output' in call_result:
                    context.update(call_result['output'])

        return results

    async def _execute_single_call(
        self,
        call: Dict[str, Any],
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Выполнить один вызов сценария
        """

        scenario_id = call.get('scenario_id')
        level = call.get('level')
        params = call.get('params', {})
        timeout = call.get('timeout', 30)
        wait_for = call.get('wait_for', 'completion')

        logger.info(f"      🔗 Calling scenario: {scenario_id} (level {level})")

        # Загрузить вызываемый сценарий
        try:
            called_scenario = await self.registry.get_scenario(scenario_id, level)

            if not called_scenario:
                return {
                    'scenario_id': scenario_id,
                    'status': 'error',
                    'error': f"Scenario {scenario_id} (level {level}) not found"
                }

        except Exception as e:
            logger.error(f"      ❌ Failed to load scenario {scenario_id}: {e}")
            return {
                'scenario_id': scenario_id,
                'status': 'error',
                'error': f"Failed to load: {str(e)}"
            }

        # Input mapping
        call_params = params.copy()
        if 'input_mapping' in call:
            mapped_params = self._map_params(call['input_mapping'], context)
            call_params.update(mapped_params)

        # Выполнить вызванный сценарий (рекурсия!)
        try:
            # Динамический импорт чтобы избежать circular import
            from .scenario_engine import ScenarioEngine
            engine = ScenarioEngine()

            # Запустить с timeout
            result = await asyncio.wait_for(
                engine.execute_scenario(called_scenario, call_params),
                timeout=timeout
            )

            # Output mapping
            output = result
            if 'output_mapping' in call:
                output = self._map_params(call['output_mapping'], result)

            return {
                'scenario_id': scenario_id,
                'status': 'success',
                'output': output,
                'duration': result.get('duration')
            }

        except asyncio.TimeoutError:
            logger.error(f"      ⏱️  Timeout after {timeout}s")
            return {
                'scenario_id': scenario_id,
                'status': 'timeout',
                'error': f"Timeout after {timeout}s"
            }

        except Exception as e:
            logger.error(f"      ❌ Execution failed: {e}")
            return {
                'scenario_id': scenario_id,
                'status': 'error',
                'error': str(e)
            }

    def _map_params(
        self,
        mapping: Dict[str, str],
        source: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Map параметров из source в новый dict согласно mapping

        Example:
            mapping = {'new_name': '{{old_name}}', 'id': '{{response.data.id}}'}
            source = {'old_name': 'value', 'response': {'data': {'id': 123}}}
            -> {'new_name': 'value', 'id': 123}
        """

        mapped = {}

        for target_key, source_path in mapping.items():
            if isinstance(source_path, str) and source_path.startswith("{{") and source_path.endswith("}}"):
                # Variable substitution
                path = source_path[2:-2].strip()
                value = self._get_from_dict(path, source)
                mapped[target_key] = value
            else:
                mapped[target_key] = source_path

        return mapped

    def _get_from_dict(
        self,
        path: str,
        data: Dict[str, Any]
    ) -> Any:
        """
        Получить значение из dict по пути 'response.data.id'
        """

        parts = path.split('.')
        value = data

        for part in parts:
            if isinstance(value, dict):
                value = value.get(part)
                if value is None:
                    return None
            else:
                return None

        return value


# Test
async def main():
    """Test Call Engine"""

    from storage.registry import ScenarioRegistry

    # Create mock registry
    registry = ScenarioRegistry()

    # Тестовые сценарии
    test_scenario_l1 = {
        'meta': {
            'id': 'test-level1-scenario',
            'level': 1,
            'type': 'functional'
        },
        'execution': {
            'steps': [
                {
                    'id': 'step1',
                    'action': 'test.action',
                    'params': {'message': 'From Level 1'}
                }
            ]
        }
    }

    # Register в mock registry
    await registry.register(test_scenario_l1)

    # Тест Call Engine
    call_engine = CallEngine()

    calls = [
        {
            'scenario_id': 'test-level1-scenario',
            'level': 1,
            'params': {'input': 'test'},
            'timeout': 10
        }
    ]

    results = await call_engine.execute_calls(calls, {})

    print("\n" + "="*60)
    print("CALL ENGINE TEST RESULT:")
    print("="*60)
    import json
    print(json.dumps(results, indent=2, default=str))


if __name__ == "__main__":
    asyncio.run(main())
