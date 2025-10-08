#!/usr/bin/env python3
"""
Event Intelligence System - Саморазвивающаяся система управления событиями

Автоматически обнаруживает:
1. Потенциальные события на основе кода
2. Недостающие publishers/subscribers
3. Несоответствия между схемой и реализацией
4. Предлагает улучшения архитектуры

Использование:
    python3 event_intelligence_system.py --scan
    python3 event_intelligence_system.py --validate
    python3 event_intelligence_system.py --suggest
"""

import os
import json
import ast
import yaml
import logging
from pathlib import Path
from typing import Dict, List, Set, Tuple, Optional
from dataclasses import dataclass, asdict
from collections import defaultdict

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class EventDefinition:
    """Определение события"""
    name: str
    domain: str
    source_file: str
    line_number: int
    type: str  # 'publisher', 'subscriber', 'schema'
    payload_schema: Optional[Dict] = None
    confidence: float = 1.0  # Уверенность в правильности обнаружения


@dataclass
class EventGap:
    """Пробел в покрытии событий"""
    event_name: str
    gap_type: str  # 'missing_publisher', 'missing_subscriber', 'orphaned'
    severity: str  # 'critical', 'warning', 'info'
    suggestion: str
    affected_services: List[str]


@dataclass
class PotentialEvent:
    """Потенциальное событие, которое должно быть создано"""
    suggested_name: str
    reason: str
    source_context: str
    confidence: float
    suggested_implementation: str


class EventIntelligenceSystem:
    """
    Интеллектуальная система управления событиями

    Возможности:
    - Сканирует код и находит все события
    - Сравнивает с AsyncAPI схемой
    - Находит пробелы (gaps)
    - Предлагает новые события
    - Генерирует отчёты и метрики
    """

    def __init__(self, project_root: str):
        self.project_root = Path(project_root)
        self.intelligent_core = self.project_root / "intelligent-core"
        self.asyncapi_path = self.project_root / "infrastructure/eventbus/events/asyncapi.yaml"
        self.catalog_path = self.project_root / "infrastructure/eventbus/events/events_catalog.json"

        # Загруженные данные
        self.schema_events: Dict[str, Dict] = {}
        self.code_events: Dict[str, EventDefinition] = {}
        self.catalog_data: Dict = {}

        # Результаты анализа
        self.gaps: List[EventGap] = []
        self.potential_events: List[PotentialEvent] = []

    # =========================================================================
    # 1. ЗАГРУЗКА ДАННЫХ
    # =========================================================================

    def load_asyncapi_schema(self) -> Dict[str, Dict]:
        """Загружает схему событий из AsyncAPI"""
        if not self.asyncapi_path.exists():
            logger.warning(f"AsyncAPI schema not found: {self.asyncapi_path}")
            return {}

        with open(self.asyncapi_path, 'r') as f:
            schema = yaml.safe_load(f)

        events = {}
        if 'channels' in schema:
            for event_name, event_def in schema['channels'].items():
                events[event_name] = {
                    'description': event_def.get('description', ''),
                    'messages': event_def.get('messages', {}),
                    'address': event_def.get('address', event_name)
                }

        logger.info(f"✅ Loaded {len(events)} events from AsyncAPI schema")
        self.schema_events = events
        return events

    def load_catalog(self) -> Dict:
        """Загружает существующий каталог событий"""
        if not self.catalog_path.exists():
            logger.warning(f"Catalog not found: {self.catalog_path}")
            return {}

        with open(self.catalog_path, 'r') as f:
            catalog = json.load(f)

        logger.info(f"✅ Loaded catalog: {catalog.get('stats', {})}")
        self.catalog_data = catalog
        return catalog

    # =========================================================================
    # 2. СКАНИРОВАНИЕ КОДА
    # =========================================================================

    def scan_codebase(self) -> Dict[str, EventDefinition]:
        """Сканирует весь codebase и находит все события"""
        logger.info("🔍 Scanning codebase for events...")

        events = {}
        python_files = list(self.intelligent_core.rglob("*.py"))

        for py_file in python_files:
            if 'node_modules' in str(py_file) or '__pycache__' in str(py_file):
                continue

            file_events = self._scan_file(py_file)
            events.update(file_events)

        logger.info(f"✅ Found {len(events)} event references in code")
        self.code_events = events
        return events

    def _scan_file(self, file_path: Path) -> Dict[str, EventDefinition]:
        """Сканирует один файл"""
        events = {}

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                tree = ast.parse(content, filename=str(file_path))
        except Exception as e:
            logger.debug(f"Could not parse {file_path}: {e}")
            return events

        # Ищем вызовы publish() и subscribe()
        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                # publish(event_name, ...)
                if self._is_publish_call(node):
                    event_name = self._extract_event_name(node)
                    if event_name:
                        key = f"{event_name}_pub_{file_path}"
                        events[key] = EventDefinition(
                            name=event_name,
                            domain=self._extract_domain(event_name),
                            source_file=str(file_path.relative_to(self.project_root)),
                            line_number=node.lineno,
                            type='publisher'
                        )

                # subscribe(event_name, handler)
                elif self._is_subscribe_call(node):
                    event_name = self._extract_event_name(node)
                    if event_name:
                        key = f"{event_name}_sub_{file_path}"
                        events[key] = EventDefinition(
                            name=event_name,
                            domain=self._extract_domain(event_name),
                            source_file=str(file_path.relative_to(self.project_root)),
                            line_number=node.lineno,
                            type='subscriber'
                        )

        return events

    def _is_publish_call(self, node: ast.Call) -> bool:
        """Проверяет, является ли вызов publish()"""
        if isinstance(node.func, ast.Attribute):
            return node.func.attr == 'publish'
        elif isinstance(node.func, ast.Name):
            return node.func.id == 'publish'
        return False

    def _is_subscribe_call(self, node: ast.Call) -> bool:
        """Проверяет, является ли вызов subscribe()"""
        if isinstance(node.func, ast.Attribute):
            return node.func.attr == 'subscribe'
        elif isinstance(node.func, ast.Name):
            return node.func.id == 'subscribe'
        return False

    def _extract_event_name(self, node: ast.Call) -> Optional[str]:
        """Извлекает имя события из вызова"""
        if node.args and isinstance(node.args[0], ast.Constant):
            return node.args[0].value
        elif node.args and isinstance(node.args[0], ast.Str):
            return node.args[0].s
        return None

    def _extract_domain(self, event_name: str) -> str:
        """Извлекает домен из имени события (bcm.bia.started -> bcm)"""
        parts = event_name.split('.')
        return parts[0] if parts else 'unknown'

    # =========================================================================
    # 3. АНАЛИЗ ПРОБЕЛОВ (GAPS)
    # =========================================================================

    def analyze_gaps(self) -> List[EventGap]:
        """Находит пробелы в покрытии событий"""
        logger.info("🔍 Analyzing event coverage gaps...")

        gaps = []

        # События из каталога
        catalog_events = self.catalog_data.get('events', {})

        for event_name, event_data in catalog_events.items():
            publishers = event_data.get('publishers', [])
            subscribers = event_data.get('subscribers', [])

            # Событие без publishers
            if not publishers:
                gaps.append(EventGap(
                    event_name=event_name,
                    gap_type='missing_publisher',
                    severity='warning',
                    suggestion=f"Добавить publish('{event_name}', ...) в соответствующий модуль",
                    affected_services=subscribers
                ))

            # Событие без subscribers (возможно не критично)
            if not subscribers:
                gaps.append(EventGap(
                    event_name=event_name,
                    gap_type='missing_subscriber',
                    severity='info',
                    suggestion=f"Рассмотреть подписку на '{event_name}' для реактивной обработки",
                    affected_services=publishers
                ))

            # События в схеме, но не в коде
            if event_name in self.schema_events:
                code_has_event = any(
                    ed.name == event_name for ed in self.code_events.values()
                )
                if not code_has_event:
                    gaps.append(EventGap(
                        event_name=event_name,
                        gap_type='orphaned',
                        severity='critical',
                        suggestion=f"Событие '{event_name}' в схеме, но не реализовано в коде",
                        affected_services=[]
                    ))

        logger.info(f"⚠️ Found {len(gaps)} coverage gaps")
        self.gaps = gaps
        return gaps

    # =========================================================================
    # 4. ОБНАРУЖЕНИЕ ПОТЕНЦИАЛЬНЫХ СОБЫТИЙ
    # =========================================================================

    def discover_potential_events(self) -> List[PotentialEvent]:
        """
        Обнаруживает потенциальные события на основе анализа кода

        Ищет паттерны:
        - Методы вида complete_*, finish_*, update_* без publish
        - Изменения состояния без уведомлений
        - CRUD операции без событий
        """
        logger.info("🤖 Discovering potential events...")

        potential = []
        python_files = list(self.intelligent_core.rglob("*.py"))

        for py_file in python_files:
            if 'node_modules' in str(py_file) or '__pycache__' in str(py_file):
                continue

            file_potential = self._analyze_file_for_potential_events(py_file)
            potential.extend(file_potential)

        logger.info(f"💡 Discovered {len(potential)} potential events")
        self.potential_events = potential
        return potential

    def _analyze_file_for_potential_events(self, file_path: Path) -> List[PotentialEvent]:
        """Анализирует файл на предмет потенциальных событий"""
        potential = []

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                tree = ast.parse(content, filename=str(file_path))
        except Exception:
            return potential

        # Ищем методы, которые должны генерировать события
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                method_name = node.name

                # Паттерны методов, которые должны публиковать события
                event_patterns = [
                    ('complete_', 'completed'),
                    ('finish_', 'finished'),
                    ('start_', 'started'),
                    ('update_', 'updated'),
                    ('create_', 'created'),
                    ('delete_', 'deleted'),
                    ('approve_', 'approved'),
                    ('reject_', 'rejected'),
                    ('escalate_', 'escalated'),
                    ('resolve_', 'resolved'),
                ]

                for prefix, suffix in event_patterns:
                    if method_name.startswith(prefix):
                        # Проверяем, есть ли publish внутри метода
                        has_publish = self._method_has_publish(node)

                        if not has_publish:
                            entity = method_name[len(prefix):]
                            suggested_event = f"{entity}.{suffix}"

                            potential.append(PotentialEvent(
                                suggested_name=suggested_event,
                                reason=f"Метод '{method_name}' изменяет состояние, но не публикует событие",
                                source_context=f"{file_path.relative_to(self.project_root)}:{node.lineno}",
                                confidence=0.7,
                                suggested_implementation=f"""
async def {method_name}(self, ...):
    # Существующий код
    result = await self._do_{entity}_operation(...)

    # ✨ Добавить:
    await self.eventbus.publish(
        '{suggested_event}',
        {{
            'entity_id': result.id,
            'timestamp': datetime.utcnow().isoformat(),
            'tenant_id': tenant_id
        }},
        tenant_id=tenant_id
    )

    return result
"""
                            ))

        return potential

    def _method_has_publish(self, func_node: ast.FunctionDef) -> bool:
        """Проверяет, есть ли вызов publish в методе"""
        for node in ast.walk(func_node):
            if isinstance(node, ast.Call):
                if self._is_publish_call(node):
                    return True
        return False

    # =========================================================================
    # 5. ГЕНЕРАЦИЯ ОТЧЁТОВ
    # =========================================================================

    def generate_report(self, output_path: Optional[str] = None) -> Dict:
        """Генерирует полный отчёт о состоянии событий"""

        report = {
            'timestamp': str(Path(__file__).stat().st_mtime),
            'summary': {
                'schema_events': len(self.schema_events),
                'code_events': len(set(e.name for e in self.code_events.values())),
                'gaps_found': len(self.gaps),
                'potential_events': len(self.potential_events),
            },
            'gaps': [asdict(gap) for gap in self.gaps],
            'potential_events': [asdict(pe) for pe in self.potential_events],
            'recommendations': self._generate_recommendations()
        }

        if output_path:
            output_file = Path(output_path)
            output_file.parent.mkdir(parents=True, exist_ok=True)

            with open(output_file, 'w') as f:
                json.dump(report, f, indent=2)

            logger.info(f"📄 Report saved to {output_file}")

        return report

    def _generate_recommendations(self) -> List[Dict]:
        """Генерирует рекомендации по улучшению"""
        recommendations = []

        # Критические пробелы
        critical_gaps = [g for g in self.gaps if g.severity == 'critical']
        if critical_gaps:
            recommendations.append({
                'priority': 'high',
                'category': 'schema_mismatch',
                'title': f'Исправить {len(critical_gaps)} критических расхождений схемы',
                'description': 'События объявлены в AsyncAPI, но не реализованы в коде'
            })

        # Потенциальные события с высокой уверенностью
        high_confidence = [pe for pe in self.potential_events if pe.confidence > 0.8]
        if high_confidence:
            recommendations.append({
                'priority': 'medium',
                'category': 'missing_events',
                'title': f'Добавить {len(high_confidence)} рекомендуемых событий',
                'description': 'Методы изменяют состояние без уведомления через события'
            })

        # Подписчики без издателей
        missing_publishers = [g for g in self.gaps if g.gap_type == 'missing_publisher']
        if len(missing_publishers) > 10:
            recommendations.append({
                'priority': 'high',
                'category': 'architecture',
                'title': f'Много событий ({len(missing_publishers)}) без publishers',
                'description': 'Возможно, events определены слишком широко или не используются'
            })

        return recommendations

    def print_summary(self):
        """Выводит краткую сводку в консоль"""
        print("\n" + "="*70)
        print("📊 EVENT INTELLIGENCE SYSTEM - SUMMARY")
        print("="*70)

        print(f"\n📋 Schema Events: {len(self.schema_events)}")
        print(f"💻 Code Events: {len(set(e.name for e in self.code_events.values()))}")

        print(f"\n⚠️ Gaps Found: {len(self.gaps)}")
        for severity in ['critical', 'warning', 'info']:
            count = len([g for g in self.gaps if g.severity == severity])
            if count > 0:
                print(f"   - {severity.capitalize()}: {count}")

        print(f"\n💡 Potential Events: {len(self.potential_events)}")
        high_conf = len([pe for pe in self.potential_events if pe.confidence > 0.7])
        print(f"   - High confidence (>0.7): {high_conf}")

        print("\n" + "="*70 + "\n")


def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(description='Event Intelligence System')
    parser.add_argument('--scan', action='store_true', help='Scan codebase for events')
    parser.add_argument('--validate', action='store_true', help='Validate against schema')
    parser.add_argument('--suggest', action='store_true', help='Suggest potential events')
    parser.add_argument('--report', type=str, help='Output report path')
    parser.add_argument('--project-root', type=str, default='/Users/MD/AI-Platform-ISO',
                       help='Project root directory')

    args = parser.parse_args()

    # Initialize system
    eis = EventIntelligenceSystem(args.project_root)

    # Load existing data
    eis.load_asyncapi_schema()
    eis.load_catalog()

    # Run operations
    if args.scan or not any([args.validate, args.suggest]):
        eis.scan_codebase()

    if args.validate:
        eis.analyze_gaps()

    if args.suggest:
        eis.discover_potential_events()

    # Generate report
    report_path = args.report or '/Users/MD/AI-Platform-ISO/infrastructure/eventbus/events/intelligence_report.json'
    eis.generate_report(report_path)

    # Print summary
    eis.print_summary()


if __name__ == '__main__':
    main()
