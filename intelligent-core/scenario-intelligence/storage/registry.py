"""
Scenario Registry - быстрый индекс всех сценариев

В памяти (для MVP), потом можно перенести в PostgreSQL/Redis
"""

import logging
from typing import Dict, Any, List, Optional
import asyncio

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ScenarioRegistry:
    """
    Registry всех сценариев для быстрого поиска

    В production - PostgreSQL или Redis
    Сейчас - in-memory для простоты
    """

    def __init__(self):
        # In-memory storage
        self.scenarios = {}  # scenario_id -> scenario
        self.index_by_level = {}  # level -> [scenario_ids]
        self.index_by_type = {}  # type -> [scenario_ids]
        self.index_by_module = {}  # module -> [scenario_ids]

    async def register(self, scenario: Dict[str, Any]) -> bool:
        """
        Зарегистрировать сценарий

        Args:
            scenario: Сценарий (с или без обертки 'scenario')

        Returns:
            True если успешно
        """

        # Handle both formats
        if 'scenario' in scenario:
            scenario = scenario['scenario']

        meta = scenario.get('meta', {})
        scenario_id = meta.get('id')

        if not scenario_id:
            logger.error("Scenario без ID, невозможно зарегистрировать")
            return False

        # Сохранить сценарий
        self.scenarios[scenario_id] = scenario

        # Индексировать
        level = meta.get('level')
        if level:
            if level not in self.index_by_level:
                self.index_by_level[level] = []
            if scenario_id not in self.index_by_level[level]:
                self.index_by_level[level].append(scenario_id)

        scenario_type = meta.get('type')
        if scenario_type:
            if scenario_type not in self.index_by_type:
                self.index_by_type[scenario_type] = []
            if scenario_id not in self.index_by_type[scenario_type]:
                self.index_by_type[scenario_type].append(scenario_id)

        module = scenario.get('ownership', {}).get('module')
        if module:
            if module not in self.index_by_module:
                self.index_by_module[module] = []
            if scenario_id not in self.index_by_module[module]:
                self.index_by_module[module].append(scenario_id)

        logger.info(f"✅ Registered scenario: {scenario_id} (level {level}, type {scenario_type})")

        return True

    async def get_scenario_by_id(self, scenario_id: str) -> Optional[Dict[str, Any]]:
        """
        Получить сценарий по ID

        Args:
            scenario_id: ID сценария

        Returns:
            Сценарий или None
        """

        return self.scenarios.get(scenario_id)

    async def get_scenario(
        self,
        scenario_id: str,
        level: Optional[int] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Получить сценарий по ID и опционально level

        Args:
            scenario_id: ID сценария
            level: Уровень (опционально)

        Returns:
            Сценарий или None
        """

        scenario = self.scenarios.get(scenario_id)

        if scenario and level is not None:
            # Проверить level
            if scenario.get('meta', {}).get('level') == level:
                return scenario
            else:
                return None

        return scenario

    async def find_scenarios(
        self,
        level: Optional[int] = None,
        type: Optional[str] = None,
        module: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Найти сценарии по фильтрам

        Args:
            level: Уровень
            type: Тип
            module: Модуль

        Returns:
            Список сценариев
        """

        # Получить candidate IDs
        candidate_ids = set(self.scenarios.keys())

        # Фильтровать по level
        if level is not None:
            if level in self.index_by_level:
                candidate_ids &= set(self.index_by_level[level])
            else:
                return []

        # Фильтровать по type
        if type:
            if type in self.index_by_type:
                candidate_ids &= set(self.index_by_type[type])
            else:
                return []

        # Фильтровать по module
        if module:
            if module in self.index_by_module:
                candidate_ids &= set(self.index_by_module[module])
            else:
                return []

        # Вернуть сценарии
        return [self.scenarios[sid] for sid in candidate_ids]

    async def list_all(self) -> List[Dict[str, Any]]:
        """Получить все сценарии"""

        return list(self.scenarios.values())

    async def get_statistics(self) -> Dict[str, Any]:
        """Получить статистику по сценариям"""

        stats = {
            'total_scenarios': len(self.scenarios),
            'by_level': {
                level: len(scenario_ids)
                for level, scenario_ids in self.index_by_level.items()
            },
            'by_type': {
                type: len(scenario_ids)
                for type, scenario_ids in self.index_by_type.items()
            },
            'by_module': {
                module: len(scenario_ids)
                for module, scenario_ids in self.index_by_module.items()
            }
        }

        return stats


# Global registry instance
global_registry = ScenarioRegistry()


# Test
async def main():
    """Test Registry"""

    registry = ScenarioRegistry()

    # Тестовый сценарий
    test_scenario = {
        'meta': {
            'id': 'test-vault-store',
            'level': 1,
            'type': 'functional'
        },
        'ownership': {
            'module': 'vault'
        },
        'description': {
            'title': 'Test Vault Store'
        }
    }

    # Register
    await registry.register(test_scenario)

    # Get by ID
    scenario = await registry.get_scenario_by_id('test-vault-store')
    print(f"\n✅ Found scenario: {scenario['meta']['id']}")

    # Find by filters
    scenarios = await registry.find_scenarios(level=1, type='functional')
    print(f"✅ Found {len(scenarios)} scenarios by filters")

    # Statistics
    stats = await registry.get_statistics()
    print(f"✅ Statistics: {stats}")


if __name__ == "__main__":
    asyncio.run(main())
