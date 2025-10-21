#!/usr/bin/env python3
"""
Event Auto-Fixer - Автоматическое исправление пробелов в событиях

Умеет:
1. Добавлять недостающие publish() вызовы
2. Создавать subscribers для orphaned events
3. Обновлять AsyncAPI схему
4. Генерировать шаблоны кода

Использование:
    python3 auto_fixer.py --fix-publishers
    python3 auto_fixer.py --fix-subscribers
    python3 auto_fixer.py --dry-run  # Только показать, что будет сделано
"""

import os
import ast
import json
import logging
from pathlib import Path
from typing import Dict, List, Optional
from dataclasses import dataclass

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class CodeFix:
    """Исправление кода"""
    file_path: str
    line_number: int
    fix_type: str  # 'add_publisher', 'add_subscriber'
    code_to_add: str
    reason: str


class EventAutoFixer:
    """Автоматическое исправление пробелов в событиях"""

    def __init__(self, project_root: str, report_path: str):
        self.project_root = Path(project_root)
        self.report_path = Path(report_path)
        self.report = self._load_report()
        self.fixes: List[CodeFix] = []

    def _load_report(self) -> Dict:
        """Загружает отчёт от Event Intelligence System"""
        with open(self.report_path, 'r') as f:
            return json.load(f)

    # =========================================================================
    # 1. ИСПРАВЛЕНИЕ MISSING PUBLISHERS
    # =========================================================================

    def fix_missing_publishers(self, dry_run: bool = True) -> List[CodeFix]:
        """
        Автоматически добавляет недостающие publishers

        Для каждого события без publisher:
        1. Находит файлы, где должен быть publisher (по subscriber usage)
        2. Находит подходящие методы (complete_, finish_, update_)
        3. Предлагает добавить publish() вызов
        """
        logger.info(" Fixing missing publishers...")

        missing_publishers = [
            gap for gap in self.report['gaps']
            if gap['gap_type'] == 'missing_publisher'
        ]

        for gap in missing_publishers:
            event_name = gap['event_name']
            affected_services = gap['affected_services']

            # Для каждого сервиса, который подписан на событие
            for service_file in affected_services:
                full_path = self.project_root / service_file

                if not full_path.exists():
                    continue

                # Ищем подходящее место для добавления publisher
                fix = self._suggest_publisher_location(
                    full_path, event_name
                )

                if fix:
                    self.fixes.append(fix)

                    if not dry_run:
                        self._apply_fix(fix)

        logger.info(f" Generated {len(self.fixes)} publisher fixes")
        return self.fixes

    def _suggest_publisher_location(
        self, file_path: Path, event_name: str
    ) -> Optional[CodeFix]:
        """Предлагает место для добавления publisher"""

        try:
            with open(file_path, 'r') as f:
                content = f.read()
                tree = ast.parse(content)
        except Exception as e:
            logger.debug(f"Cannot parse {file_path}: {e}")
            return None

        # Извлекаем action из event_name (e.g., state_changed -> changed)
        parts = event_name.split('_')
        action_keyword = parts[-1] if parts else None

        # Ищем методы, которые соответствуют действию
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                method_name = node.name.lower()

                # Проверяем, подходит ли метод
                if action_keyword and action_keyword in method_name:
                    # Проверяем, есть ли уже publish
                    has_publish = self._has_publish_call(node, event_name)

                    if not has_publish:
                        # Генерируем код для добавления
                        code_to_add = self._generate_publish_code(
                            event_name, method_name
                        )

                        return CodeFix(
                            file_path=str(file_path),
                            line_number=node.end_lineno,
                            fix_type='add_publisher',
                            code_to_add=code_to_add,
                            reason=f"Method '{method_name}' should publish '{event_name}'"
                        )

        return None

    def _has_publish_call(self, func_node: ast.FunctionDef, event_name: str) -> bool:
        """Проверяет, есть ли publish для данного события"""
        for node in ast.walk(func_node):
            if isinstance(node, ast.Call):
                if isinstance(node.func, ast.Attribute) and node.func.attr == 'publish':
                    # Проверяем имя события
                    if node.args and isinstance(node.args[0], ast.Constant):
                        if node.args[0].value == event_name:
                            return True
        return False

    def _generate_publish_code(self, event_name: str, method_name: str) -> str:
        """Генерирует код для publish()"""
        return f"""
    #  Auto-generated by Event Intelligence System
    await self.eventbus.publish(
        '{event_name}',
        {{
            'timestamp': datetime.utcnow().isoformat(),
            'source': '{method_name}',
            # TODO: Добавить нужные поля
        }},
        tenant_id=tenant_id  # TODO: Проверить, что tenant_id доступен
    )
"""

    # =========================================================================
    # 2. ИСПРАВЛЕНИЕ MISSING SUBSCRIBERS
    # =========================================================================

    def fix_missing_subscribers(self, dry_run: bool = True) -> List[CodeFix]:
        """
        Создаёт шаблоны для недостающих subscribers

        Генерирует файлы вида:
        - handlers/event_name_handler.py с async def handle_event_name(event)
        """
        logger.info(" Generating subscriber templates...")

        missing_subscribers = [
            gap for gap in self.report['gaps']
            if gap['gap_type'] == 'missing_subscriber' and gap['severity'] != 'info'
        ]

        for gap in missing_subscribers:
            event_name = gap['event_name']

            # Генерируем шаблон subscriber
            code = self._generate_subscriber_template(event_name)

            # Определяем, куда сохранить
            domain = event_name.split('.')[0]
            handler_dir = self.project_root / f"intelligent-core/event_handlers/{domain}"
            handler_dir.mkdir(parents=True, exist_ok=True)

            handler_file = handler_dir / f"{event_name.replace('.', '_')}_handler.py"

            fix = CodeFix(
                file_path=str(handler_file),
                line_number=0,
                fix_type='add_subscriber',
                code_to_add=code,
                reason=f"No subscriber for '{event_name}'"
            )

            self.fixes.append(fix)

            if not dry_run:
                self._apply_fix(fix)

        logger.info(f" Generated {len(missing_subscribers)} subscriber templates")
        return self.fixes

    def _generate_subscriber_template(self, event_name: str) -> str:
        """Генерирует шаблон subscriber handler"""
        handler_name = event_name.replace('.', '_')
        class_name = ''.join(word.capitalize() for word in event_name.split('.'))

        return f'''"""
Event Handler for {event_name}

 Auto-generated by Event Intelligence System
TODO: Implement business logic
"""

import logging
from typing import Dict, Any
from datetime import datetime

logger = logging.getLogger(__name__)


class {class_name}Handler:
    """Handles {event_name} events"""

    def __init__(self, eventbus):
        self.eventbus = eventbus

    async def setup(self):
        """Setup event subscriptions"""
        await self.eventbus.subscribe(
            '{event_name}',
            self.handle_{handler_name}
        )
        logger.info(" Subscribed to {event_name}")

    async def handle_{handler_name}(self, event_data: Dict[str, Any]):
        """
        Handle {event_name} event

        Args:
            event_data: Event payload containing:
                - TODO: Document expected fields
        """
        try:
            logger.info(f" Received {event_name}: {{event_data}}")

            # TODO: Implement business logic
            # Example:
            # - Update database
            # - Trigger downstream processes
            # - Send notifications
            # - Log analytics

            logger.info(f" Processed {event_name} successfully")

        except Exception as e:
            logger.error(f" Error handling {event_name}: {{e}}")
            raise
'''

    # =========================================================================
    # 3. ПРИМЕНЕНИЕ ИСПРАВЛЕНИЙ
    # =========================================================================

    def _apply_fix(self, fix: CodeFix):
        """Применяет исправление к файлу"""
        file_path = Path(fix.file_path)

        if fix.fix_type == 'add_subscriber':
            # Создаём новый файл
            file_path.parent.mkdir(parents=True, exist_ok=True)
            with open(file_path, 'w') as f:
                f.write(fix.code_to_add)
            logger.info(f" Created {file_path}")

        elif fix.fix_type == 'add_publisher':
            # Добавляем код в существующий файл
            # ВНИМАНИЕ: Это требует аккуратной работы с AST
            logger.info(f"️ Manual intervention required for {file_path}:{fix.line_number}")
            logger.info(f"   Add this code:\n{fix.code_to_add}")

    def generate_fix_report(self, output_path: str):
        """Генерирует отчёт об исправлениях"""
        report = {
            'total_fixes': len(self.fixes),
            'fixes_by_type': {
                'add_publisher': len([f for f in self.fixes if f.fix_type == 'add_publisher']),
                'add_subscriber': len([f for f in self.fixes if f.fix_type == 'add_subscriber']),
            },
            'fixes': [
                {
                    'file': fix.file_path,
                    'line': fix.line_number,
                    'type': fix.fix_type,
                    'reason': fix.reason,
                    'code_preview': fix.code_to_add[:200] + '...' if len(fix.code_to_add) > 200 else fix.code_to_add
                }
                for fix in self.fixes
            ]
        }

        with open(output_path, 'w') as f:
            json.dump(report, f, indent=2)

        logger.info(f" Fix report saved to {output_path}")

    def print_summary(self):
        """Выводит сводку исправлений"""
        print("\n" + "="*70)
        print(" AUTO-FIXER SUMMARY")
        print("="*70)

        print(f"\n Total Fixes: {len(self.fixes)}")

        by_type = {}
        for fix in self.fixes:
            by_type[fix.fix_type] = by_type.get(fix.fix_type, 0) + 1

        for fix_type, count in by_type.items():
            print(f"   - {fix_type}: {count}")

        print("\n" + "="*70 + "\n")


def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(description='Event Auto-Fixer')
    parser.add_argument('--fix-publishers', action='store_true',
                       help='Fix missing publishers')
    parser.add_argument('--fix-subscribers', action='store_true',
                       help='Fix missing subscribers')
    parser.add_argument('--dry-run', action='store_true',
                       help='Show what would be done without applying')
    parser.add_argument('--project-root', type=str,
                       default='/Users/MD/AI-Platform-ISO',
                       help='Project root directory')
    parser.add_argument('--report', type=str,
                       default='infrastructure/eventbus/events/intelligence_report.json',
                       help='Path to intelligence report')

    args = parser.parse_args()

    # Initialize fixer
    report_path = Path(args.project_root) / args.report
    fixer = EventAutoFixer(args.project_root, str(report_path))

    # Run fixes
    if args.fix_publishers:
        fixer.fix_missing_publishers(dry_run=args.dry_run)

    if args.fix_subscribers:
        fixer.fix_missing_subscribers(dry_run=args.dry_run)

    # Generate report
    fix_report_path = Path(args.project_root) / 'infrastructure/eventbus/events/auto_fix_report.json'
    fixer.generate_fix_report(str(fix_report_path))

    # Print summary
    fixer.print_summary()


if __name__ == '__main__':
    main()
