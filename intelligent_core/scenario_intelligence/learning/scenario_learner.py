"""
Scenario Learner - учится на результатах выполнения сценариев

Записывает executions, собирает статистику, создает embeddings для pattern detection
"""

import logging
from typing import Dict, Any, Optional, List
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ScenarioLearner:
    """
    Учится на результатах выполнения сценариев

    Функции:
    - Записывает каждое выполнение
    - Создает embeddings для pattern detection
    - Собирает статистику
    """

    def __init__(self):
        # In-memory storage для MVP
        # В production - PostgreSQL + Qdrant
        self.executions = []
        self.statistics = {}  # scenario_id -> stats

    async def record_execution(
        self,
        scenario_id: str,
        scenario: Dict[str, Any],
        result: Dict[str, Any],
        context: Dict[str, Any]
    ):
        """
        Записать результат выполнения сценария

        Args:
            scenario_id: ID сценария
            scenario: Полный сценарий
            result: Результат выполнения
            context: Контекст выполнения
        """

        execution_record = {
            'scenario_id': scenario_id,
            'executed_at': datetime.utcnow().isoformat(),
            'context': context,
            'result': result,
            'success': result.get('status') == 'success',
            'duration': result.get('duration', 0),
            'errors': result.get('errors', [])
        }

        # Сохранить execution
        self.executions.append(execution_record)

        # Обновить статистику
        await self._update_statistics(scenario_id, result)

        logger.info(f"   Recorded execution: {scenario_id} ({result.get('status')})")

        # TODO: В production
        # - Сохранить в PostgreSQL
        # - Создать embeddings и сохранить в Qdrant
        # - Отправить метрики в Prometheus

    async def _update_statistics(
        self,
        scenario_id: str,
        result: Dict[str, Any]
    ):
        """
        Обновить статистику использования сценария
        """

        if scenario_id not in self.statistics:
            self.statistics[scenario_id] = {
                'total_executions': 0,
                'successful_executions': 0,
                'failed_executions': 0,
                'total_duration': 0,
                'avg_duration': 0,
                'last_executed_at': None
            }

        stats = self.statistics[scenario_id]
        stats['total_executions'] += 1

        if result.get('status') == 'success':
            stats['successful_executions'] += 1
        else:
            stats['failed_executions'] += 1

        duration = result.get('duration', 0)
        stats['total_duration'] += duration
        stats['avg_duration'] = stats['total_duration'] / stats['total_executions']
        stats['last_executed_at'] = datetime.utcnow().isoformat()

        logger.debug(f"     Stats updated: {scenario_id} - {stats['total_executions']} executions")

    async def get_statistics(self, scenario_id: str) -> Dict[str, Any]:
        """
        Получить статистику по сценарию

        Args:
            scenario_id: ID сценария

        Returns:
            Статистика
        """

        return self.statistics.get(scenario_id, {})

    async def get_all_statistics(self) -> Dict[str, Any]:
        """Получить статистику по всем сценариям"""

        return self.statistics

    async def get_recent_executions(
        self,
        scenario_id: Optional[str] = None,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Получить последние executions

        Args:
            scenario_id: Фильтр по scenario_id (опционально)
            limit: Максимум результатов

        Returns:
            Список executions
        """

        executions = self.executions

        if scenario_id:
            executions = [e for e in executions if e['scenario_id'] == scenario_id]

        # Сортировать по времени (newest first)
        executions = sorted(
            executions,
            key=lambda e: e['executed_at'],
            reverse=True
        )

        return executions[:limit]


# Global learner instance
global_learner = ScenarioLearner()
