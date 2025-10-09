"""
Wishlist System - Управление желаниями и потребностями системы

Философия:
- Система имеет желания и потребности
- Желания конкурируют за ресурсы
- Устаревшие желания автоматически удаляются
- Конфликты разрешаются автоматически

Интеграция:
- Survival Instinct создает желания при дисбалансе
- Memory System влияет на приоритеты (успешные действия = выше приоритет)
- Resource Tracker определяет что можно выполнить
"""

import asyncio
import logging
import time
import uuid
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
import json

logger = logging.getLogger(__name__)


class NeedType(Enum):
    """Тип потребности"""
    SURVIVAL = "survival"      # Критично для работы
    EFFICIENCY = "efficiency"  # Оптимизация
    LEARNING = "learning"      # Обучение
    GROWTH = "growth"         # Расширение возможностей


@dataclass
class ResourceCost:
    """Стоимость в ресурсах"""
    cpu_percent: float = 0.0
    memory_mb: float = 0.0
    time_seconds: float = 0.0
    disk_io_mb: float = 0.0

    def total_value(self) -> float:
        """Общая стоимость в условных единицах"""
        return (
            self.cpu_percent * 0.3 +
            self.memory_mb * 0.0001 +  # 1MB = 0.0001
            self.time_seconds * 0.2 +
            self.disk_io_mb * 0.0002
        )

    def can_afford_with(self, available: 'ResourceCost') -> bool:
        """Можем ли позволить при доступных ресурсах"""
        return (
            self.cpu_percent <= available.cpu_percent and
            self.memory_mb <= available.memory_mb and
            self.time_seconds <= available.time_seconds and
            self.disk_io_mb <= available.disk_io_mb
        )

    def __add__(self, other: 'ResourceCost') -> 'ResourceCost':
        return ResourceCost(
            cpu_percent=self.cpu_percent + other.cpu_percent,
            memory_mb=self.memory_mb + other.memory_mb,
            time_seconds=self.time_seconds + other.time_seconds,
            disk_io_mb=self.disk_io_mb + other.disk_io_mb
        )


@dataclass
class WishlistItem:
    """
    Элемент wishlist - желание или потребность системы
    """
    id: str
    description: str
    need_type: NeedType
    urgency: float  # 0-1
    resource_cost: ResourceCost
    parent_id: Optional[str] = None
    children: List[str] = field(default_factory=list)
    dependencies: List[str] = field(default_factory=list)
    status: str = "pending"  # pending, active, completed, obsolete
    created_at: float = field(default_factory=time.time)
    deadline: Optional[float] = None
    context: Dict[str, Any] = field(default_factory=dict)

    def calculate_priority(self, available_resources: ResourceCost) -> float:
        """
        Рассчитать приоритет

        Учитывает:
        - Urgency (срочность)
        - Доступность ресурсов
        - Близость deadline
        """
        priority = self.urgency

        # Штраф если ресурсов нет
        if not self.resource_cost.can_afford_with(available_resources):
            priority *= 0.3

        # Бонус если deadline близко
        if self.deadline:
            time_remaining = self.deadline - time.time()
            if time_remaining < 3600:  # Меньше часа
                priority *= 1.5
            elif time_remaining < 0:  # Просрочено
                priority *= 2.0

        return min(priority, 1.0)

    def is_obsolete(self, max_age_seconds: float = 86400.0) -> bool:
        """Проверка устаревания (по умолчанию 24 часа)"""
        age = time.time() - self.created_at
        return age > max_age_seconds and self.status == "pending"

    def to_dict(self) -> Dict[str, Any]:
        return {
            'id': self.id,
            'description': self.description,
            'need_type': self.need_type.value,
            'urgency': self.urgency,
            'resource_cost': {
                'cpu_percent': self.resource_cost.cpu_percent,
                'memory_mb': self.resource_cost.memory_mb,
                'time_seconds': self.resource_cost.time_seconds,
                'disk_io_mb': self.resource_cost.disk_io_mb
            },
            'parent_id': self.parent_id,
            'children': self.children,
            'dependencies': self.dependencies,
            'status': self.status,
            'created_at': self.created_at,
            'deadline': self.deadline,
            'context': self.context
        }


class ConflictResolver:
    """
    Разрешение конфликтов в wishlist

    Типы конфликтов:
    1. Циклические зависимости
    2. Конфликты ресурсов
    3. Конфликты deadline
    """

    def detect_conflicts(
        self,
        items: Dict[str, WishlistItem],
        available_resources: ResourceCost
    ) -> List[Dict[str, Any]]:
        """Обнаружить все конфликты"""
        conflicts = []

        # 1. Циклические зависимости
        circular = self._detect_circular_dependencies(items)
        conflicts.extend(circular)

        # 2. Конфликты ресурсов
        resource_conflicts = self._detect_resource_conflicts(items, available_resources)
        conflicts.extend(resource_conflicts)

        # 3. Конфликты deadline
        deadline_conflicts = self._detect_deadline_conflicts(items)
        conflicts.extend(deadline_conflicts)

        return conflicts

    def _detect_circular_dependencies(
        self,
        items: Dict[str, WishlistItem]
    ) -> List[Dict[str, Any]]:
        """Найти циклические зависимости"""
        conflicts = []

        for item_id, item in items.items():
            for dep_id in item.dependencies:
                if dep_id in items:
                    dep_item = items[dep_id]
                    if item_id in dep_item.dependencies:
                        conflicts.append({
                            'type': 'circular_dependency',
                            'items': [item_id, dep_id],
                            'description': f"Циклическая зависимость: {item.description} <-> {dep_item.description}"
                        })

        return conflicts

    def _detect_resource_conflicts(
        self,
        items: Dict[str, WishlistItem],
        available_resources: ResourceCost
    ) -> List[Dict[str, Any]]:
        """Найти конфликты ресурсов"""
        conflicts = []

        # Получить все urgent items
        urgent_items = [
            item for item in items.values()
            if item.urgency > 0.8 and item.status == "pending"
        ]

        if not urgent_items:
            return conflicts

        # Посчитать суммарный запрос
        total_demand = ResourceCost()
        for item in urgent_items:
            total_demand += item.resource_cost

        # Если превышает доступное
        if not total_demand.can_afford_with(available_resources):
            conflicts.append({
                'type': 'resource_shortage',
                'demanded_cpu': total_demand.cpu_percent,
                'available_cpu': available_resources.cpu_percent,
                'demanded_memory': total_demand.memory_mb,
                'available_memory': available_resources.memory_mb,
                'competing_items': [item.id for item in urgent_items]
            })

        return conflicts

    def _detect_deadline_conflicts(
        self,
        items: Dict[str, WishlistItem]
    ) -> List[Dict[str, Any]]:
        """Найти конфликты deadline"""
        conflicts = []
        now = time.time()

        for item_id, item in items.items():
            if not item.deadline or item.status != "pending":
                continue

            # Проверить просрочено ли с невыполненными зависимостями
            if item.deadline < now and item.dependencies:
                unmet_deps = [
                    dep_id for dep_id in item.dependencies
                    if dep_id in items and items[dep_id].status != "completed"
                ]

                if unmet_deps:
                    conflicts.append({
                        'type': 'deadline_conflict',
                        'item': item_id,
                        'deadline': item.deadline,
                        'unmet_dependencies': unmet_deps,
                        'description': f"Просрочено: {item.description}"
                    })

        return conflicts

    def resolve_conflict(
        self,
        conflict: Dict[str, Any],
        items: Dict[str, WishlistItem]
    ) -> str:
        """
        Разрешить конфликт

        Returns:
            Описание действия
        """
        conflict_type = conflict['type']

        if conflict_type == 'circular_dependency':
            return self._resolve_circular(conflict, items)
        elif conflict_type == 'resource_shortage':
            return self._resolve_resource_shortage(conflict, items)
        elif conflict_type == 'deadline_conflict':
            return self._resolve_deadline_conflict(conflict, items)

        return "Unknown conflict type"

    def _resolve_circular(
        self,
        conflict: Dict[str, Any],
        items: Dict[str, WishlistItem]
    ) -> str:
        """Разрешить циклическую зависимость"""
        item1_id, item2_id = conflict['items']
        item1 = items[item1_id]
        item2 = items[item2_id]

        # Удалить зависимость у менее срочного
        if item1.urgency < item2.urgency:
            item1.dependencies.remove(item2_id)
            return f"Removed dependency {item1_id} -> {item2_id}"
        else:
            item2.dependencies.remove(item1_id)
            return f"Removed dependency {item2_id} -> {item1_id}"

    def _resolve_resource_shortage(
        self,
        conflict: Dict[str, Any],
        items: Dict[str, WishlistItem]
    ) -> str:
        """Разрешить конфликт ресурсов - отложить менее срочные"""
        competing_ids = conflict['competing_items']
        competing_items = [items[item_id] for item_id in competing_ids]

        # Отсортировать по urgency
        competing_items.sort(key=lambda x: x.urgency)

        # Отложить нижнюю половину
        to_postpone = competing_items[:len(competing_items)//2]

        for item in to_postpone:
            item.urgency *= 0.5  # Снизить срочность

        return f"Postponed {len(to_postpone)} items to resolve resource conflict"

    def _resolve_deadline_conflict(
        self,
        conflict: Dict[str, Any],
        items: Dict[str, WishlistItem]
    ) -> str:
        """Разрешить конфликт deadline"""
        item_id = conflict['item']
        item = items[item_id]

        # Пометить как obsolete если сильно просрочено
        time_overdue = time.time() - item.deadline
        if time_overdue > 3600:  # Более часа
            item.status = "obsolete"
            return f"Marked {item_id} as obsolete (overdue)"

        # Иначе удалить зависимости и попробовать выполнить
        item.dependencies.clear()
        return f"Cleared dependencies for {item_id} to meet deadline"


class WishlistSystem:
    """
    Система управления желаниями

    Жизненный цикл желания:
    1. Создание (от Survival Instinct или других модулей)
    2. Приоритизация (учет ресурсов, зависимостей)
    3. Выполнение (когда ресурсы доступны)
    4. Завершение или устаревание
    """

    def __init__(
        self,
        storage_path: str = "/tmp/wishlist.json",
        max_item_age_seconds: float = 86400.0  # 24 часа
    ):
        self.items: Dict[str, WishlistItem] = {}
        self.storage_path = storage_path
        self.max_item_age = max_item_age_seconds

        self.conflict_resolver = ConflictResolver()

        self.stats = {
            'total_created': 0,
            'total_completed': 0,
            'total_obsolete': 0,
            'conflicts_resolved': 0
        }

        self._load_from_disk()

        logger.info(f"WishlistSystem initialized (max_age: {max_item_age_seconds}s)")

    def add_wish(
        self,
        description: str,
        need_type: NeedType,
        urgency: float,
        resource_cost: ResourceCost,
        parent_id: Optional[str] = None,
        dependencies: Optional[List[str]] = None,
        deadline: Optional[float] = None,
        context: Optional[Dict[str, Any]] = None
    ) -> WishlistItem:
        """Добавить желание в wishlist"""
        item = WishlistItem(
            id=str(uuid.uuid4()),
            description=description,
            need_type=need_type,
            urgency=urgency,
            resource_cost=resource_cost,
            parent_id=parent_id,
            dependencies=dependencies or [],
            deadline=deadline,
            context=context or {}
        )

        self.items[item.id] = item
        self.stats['total_created'] += 1

        # Добавить в children родителя
        if parent_id and parent_id in self.items:
            self.items[parent_id].children.append(item.id)

        logger.info(f"Added wish: {description} (urgency: {urgency:.2f})")

        self._save_to_disk()

        return item

    def get_prioritized_wishes(
        self,
        available_resources: ResourceCost,
        limit: int = 10
    ) -> List[WishlistItem]:
        """
        Получить приоритизированный список желаний

        Учитывает:
        - Urgency
        - Доступность ресурсов
        - Выполнение зависимостей
        - Deadline
        """
        # Только pending items
        pending = [
            item for item in self.items.values()
            if item.status == "pending"
        ]

        # Проверить зависимости
        ready = []
        for item in pending:
            deps_met = all(
                dep_id not in self.items or self.items[dep_id].status == "completed"
                for dep_id in item.dependencies
            )
            if deps_met:
                ready.append(item)

        # Рассчитать приоритеты
        for item in ready:
            item.priority = item.calculate_priority(available_resources)

        # Отсортировать по приоритету
        ready.sort(key=lambda x: x.priority, reverse=True)

        return ready[:limit]

    def cleanup_obsolete(self):
        """Удалить устаревшие желания"""
        obsolete_ids = []

        for item_id, item in self.items.items():
            if item.is_obsolete(self.max_item_age):
                obsolete_ids.append(item_id)
                item.status = "obsolete"
                self.stats['total_obsolete'] += 1

        if obsolete_ids:
            logger.info(f"Marked {len(obsolete_ids)} items as obsolete")
            self._save_to_disk()

        return obsolete_ids

    def detect_and_resolve_conflicts(
        self,
        available_resources: ResourceCost
    ) -> List[str]:
        """Обнаружить и разрешить конфликты"""
        conflicts = self.conflict_resolver.detect_conflicts(
            self.items,
            available_resources
        )

        resolutions = []
        for conflict in conflicts:
            resolution = self.conflict_resolver.resolve_conflict(conflict, self.items)
            resolutions.append(resolution)
            self.stats['conflicts_resolved'] += 1
            logger.info(f"Resolved conflict: {resolution}")

        if resolutions:
            self._save_to_disk()

        return resolutions

    def complete_wish(self, item_id: str, success: bool = True):
        """Отметить желание как выполненное"""
        if item_id not in self.items:
            logger.warning(f"Item {item_id} not found")
            return

        item = self.items[item_id]
        item.status = "completed" if success else "failed"
        self.stats['total_completed'] += 1

        logger.info(f"Completed wish: {item.description}")

        self._save_to_disk()

    def get_stats(self) -> Dict[str, Any]:
        """Получить статистику"""
        return {
            **self.stats,
            'current_pending': len([i for i in self.items.values() if i.status == "pending"]),
            'current_active': len([i for i in self.items.values() if i.status == "active"]),
            'current_completed': len([i for i in self.items.values() if i.status == "completed"])
        }

    def _save_to_disk(self):
        """Сохранить в файл"""
        try:
            data = {
                'items': {item_id: item.to_dict() for item_id, item in self.items.items()},
                'stats': self.stats,
                'saved_at': time.time()
            }

            Path(self.storage_path).parent.mkdir(parents=True, exist_ok=True)

            with open(self.storage_path, 'w') as f:
                json.dump(data, f, indent=2)

        except Exception as e:
            logger.error(f"Failed to save wishlist: {e}")

    def _load_from_disk(self):
        """Загрузить из файла"""
        try:
            if not Path(self.storage_path).exists():
                return

            with open(self.storage_path, 'r') as f:
                data = json.load(f)

            # Восстановить items
            for item_id, item_data in data.get('items', {}).items():
                resource_cost = ResourceCost(**item_data['resource_cost'])
                item = WishlistItem(
                    id=item_data['id'],
                    description=item_data['description'],
                    need_type=NeedType(item_data['need_type']),
                    urgency=item_data['urgency'],
                    resource_cost=resource_cost,
                    parent_id=item_data.get('parent_id'),
                    children=item_data.get('children', []),
                    dependencies=item_data.get('dependencies', []),
                    status=item_data['status'],
                    created_at=item_data['created_at'],
                    deadline=item_data.get('deadline'),
                    context=item_data.get('context', {})
                )
                self.items[item_id] = item

            self.stats = data.get('stats', self.stats)

            logger.info(f"Loaded {len(self.items)} items from disk")

        except Exception as e:
            logger.error(f"Failed to load wishlist: {e}")


async def create_wishlist_system(
    storage_path: str = "/tmp/wishlist.json",
    max_item_age_seconds: float = 86400.0
) -> WishlistSystem:
    """
    Создать Wishlist System

    Args:
        storage_path: Путь к файлу хранения
        max_item_age_seconds: Максимальный возраст желания

    Returns:
        WishlistSystem instance
    """
    return WishlistSystem(storage_path, max_item_age_seconds)
