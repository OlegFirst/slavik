"""
Event Executor - Исполнитель event-related задач

Функции:
- Добавление publishers в код
- Добавление subscribers в код
- Фикс event gaps автоматически
- Создание PR с изменениями
"""

import logging
import os
import ast
import astor
from typing import Dict, List, Optional
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

logger = logging.getLogger(__name__)


@dataclass
class FileChange:
    """Изменение в файле"""
    file_path: str
    original_content: str
    modified_content: str
    change_type: str  # 'add_publisher', 'add_subscriber', 'fix_gap'
    description: str


@dataclass
class EventGap:
    """Event gap для фикса"""
    event_name: str
    gap_type: str  # 'missing_publisher', 'missing_subscriber', 'orphaned'
    severity: str  # 'critical', 'warning', 'info'
    service: str
    file_path: str
    recommendation: str


class EventExecutor:
    """
    Исполнитель event-related задач

    Возможности:
    - Автоматическое добавление publishers
    - Автоматическое добавление subscribers
    - Фикс event gaps
    - Создание PR с изменениями
    """

    def __init__(self, workspace_root: str = "/Users/MD/AI-Platform-ISO"):
        self.workspace_root = Path(workspace_root)
        self.changes: List[FileChange] = []

    async def add_publisher(
        self,
        service: str,
        event: str,
        file_path: str,
        method_name: str,
        position: str = "end"
    ) -> Dict:
        """
        Добавляет publisher в указанный метод

        Args:
            service: Имя сервиса
            event: Имя события
            file_path: Путь к файлу
            method_name: Имя метода куда добавить
            position: Позиция ('start', 'end', 'before_return')

        Returns:
            Result dict
        """
        logger.info(f"🔧 Adding publisher for {event} in {service}/{method_name}")

        try:
            full_path = self.workspace_root / file_path
            if not full_path.exists():
                return {'success': False, 'error': f'File not found: {file_path}'}

            # Читаем файл
            with open(full_path, 'r', encoding='utf-8') as f:
                original_content = f.read()

            # Генерируем код publisher
            publisher_code = self._generate_publisher_code(event, method_name)

            # Вставляем в нужное место
            modified_content = self._insert_publisher(
                original_content, method_name, publisher_code, position
            )

            # Сохраняем изменение
            change = FileChange(
                file_path=str(file_path),
                original_content=original_content,
                modified_content=modified_content,
                change_type='add_publisher',
                description=f"Added publisher for {event} in {method_name}"
            )
            self.changes.append(change)

            # Применяем изменение
            with open(full_path, 'w', encoding='utf-8') as f:
                f.write(modified_content)

            logger.info(f"✅ Publisher added successfully")

            return {
                'success': True,
                'file_path': str(file_path),
                'change': change.description
            }

        except Exception as e:
            logger.error(f"❌ Error adding publisher: {e}")
            return {'success': False, 'error': str(e)}

    async def add_subscriber(
        self,
        service: str,
        event: str,
        file_path: str,
        handler_name: Optional[str] = None
    ) -> Dict:
        """
        Добавляет subscriber и handler для события

        Args:
            service: Имя сервиса
            event: Имя события
            file_path: Путь к файлу
            handler_name: Имя handler функции (auto-generate if None)

        Returns:
            Result dict
        """
        logger.info(f"🔧 Adding subscriber for {event} in {service}")

        try:
            full_path = self.workspace_root / file_path
            if not full_path.exists():
                return {'success': False, 'error': f'File not found: {file_path}'}

            # Читаем файл
            with open(full_path, 'r', encoding='utf-8') as f:
                original_content = f.read()

            # Генерируем handler name если не указан
            if not handler_name:
                handler_name = self._generate_handler_name(event)

            # Генерируем код handler
            handler_code = self._generate_handler_code(event, handler_name)

            # Генерируем код subscribe
            subscribe_code = self._generate_subscribe_code(event, handler_name)

            # Вставляем handler и subscribe
            modified_content = self._insert_subscriber(
                original_content, handler_code, subscribe_code
            )

            # Сохраняем изменение
            change = FileChange(
                file_path=str(file_path),
                original_content=original_content,
                modified_content=modified_content,
                change_type='add_subscriber',
                description=f"Added subscriber for {event} with handler {handler_name}"
            )
            self.changes.append(change)

            # Применяем изменение
            with open(full_path, 'w', encoding='utf-8') as f:
                f.write(modified_content)

            logger.info(f"✅ Subscriber added successfully")

            return {
                'success': True,
                'file_path': str(file_path),
                'handler_name': handler_name,
                'change': change.description
            }

        except Exception as e:
            logger.error(f"❌ Error adding subscriber: {e}")
            return {'success': False, 'error': str(e)}

    async def fix_event_gap(self, gap: EventGap) -> Dict:
        """
        Автоматически фиксит event gap

        Args:
            gap: EventGap для фикса

        Returns:
            Result dict
        """
        logger.info(f"🔧 Fixing gap: {gap.gap_type} for {gap.event_name}")

        if gap.gap_type == 'missing_publisher':
            # Определяем где добавить publisher
            method_name = self._suggest_publisher_location(gap)
            return await self.add_publisher(
                gap.service, gap.event_name, gap.file_path, method_name
            )

        elif gap.gap_type == 'missing_subscriber':
            return await self.add_subscriber(
                gap.service, gap.event_name, gap.file_path
            )

        elif gap.gap_type == 'orphaned':
            logger.info(f"ℹ️  Orphaned event {gap.event_name} - manual review needed")
            return {
                'success': True,
                'action': 'manual_review',
                'message': f'Orphaned event {gap.event_name} needs manual review'
            }

        else:
            return {'success': False, 'error': f'Unknown gap type: {gap.gap_type}'}

    async def create_pr(self, branch_name: Optional[str] = None) -> Dict:
        """
        Создает PR с накопленными изменениями

        Args:
            branch_name: Имя ветки (auto-generate if None)

        Returns:
            Result dict
        """
        if not self.changes:
            return {'success': False, 'error': 'No changes to commit'}

        if not branch_name:
            timestamp = datetime.utcnow().strftime("%Y%m%d-%H%M%S")
            branch_name = f"fix/event-gaps-{timestamp}"

        logger.info(f"🔧 Creating PR with {len(self.changes)} changes")

        try:
            # Формируем описание PR
            pr_description = self._generate_pr_description()

            # Создаем коммит
            commit_result = await self._create_commit(branch_name, pr_description)

            if not commit_result['success']:
                return commit_result

            # Создаем PR через GitHub API
            pr_result = await self._create_github_pr(branch_name, pr_description)

            # Очищаем изменения
            self.changes = []

            return {
                'success': True,
                'branch': branch_name,
                'pr_url': pr_result.get('url'),
                'changes_count': len(self.changes)
            }

        except Exception as e:
            logger.error(f"❌ Error creating PR: {e}")
            return {'success': False, 'error': str(e)}

    async def rollback_changes(self) -> Dict:
        """
        Откатывает все изменения к original content

        Returns:
            Result dict
        """
        logger.info(f"🔄 Rolling back {len(self.changes)} changes")

        try:
            for change in self.changes:
                full_path = self.workspace_root / change.file_path
                with open(full_path, 'w', encoding='utf-8') as f:
                    f.write(change.original_content)

            changes_count = len(self.changes)
            self.changes = []

            logger.info(f"✅ Rolled back {changes_count} changes")

            return {'success': True, 'rolled_back': changes_count}

        except Exception as e:
            logger.error(f"❌ Error rolling back: {e}")
            return {'success': False, 'error': str(e)}

    # ========== Helper Methods ==========

    def _generate_publisher_code(self, event: str, method_name: str) -> str:
        """Генерирует код для publisher"""
        return f"""
        # Auto-generated publisher
        await self.eventbus.publish(
            '{event}',
            {{
                'timestamp': datetime.utcnow().isoformat(),
                'method': '{method_name}',
                'service': self.__class__.__name__
            }},
            tenant_id=tenant_id
        )
        """

    def _generate_handler_code(self, event: str, handler_name: str) -> str:
        """Генерирует код для handler"""
        # Преобразуем event name в handler name
        # bcm.bia.started -> handle_bcm_bia_started
        return f"""
    async def {handler_name}(self, event_name: str, payload: Dict, tenant_id: str):
        \"\"\"
        Handler for {event}
        Auto-generated by Event Executor
        \"\"\"
        logger.info(f"📨 Received {{event_name}}: {{payload}}")

        # TODO: Implement business logic
        pass
        """

    def _generate_subscribe_code(self, event: str, handler_name: str) -> str:
        """Генерирует код для subscribe"""
        return f"""
        # Auto-generated subscriber
        await self.eventbus.subscribe(
            '{event}',
            self.{handler_name},
            tenant_id=tenant_id
        )
        """

    def _generate_handler_name(self, event: str) -> str:
        """Генерирует имя handler из event name"""
        # bcm.bia.started -> handle_bcm_bia_started
        clean_name = event.replace('.', '_').replace('-', '_')
        return f"handle_{clean_name}"

    def _insert_publisher(
        self,
        content: str,
        method_name: str,
        publisher_code: str,
        position: str
    ) -> str:
        """Вставляет publisher code в метод"""
        lines = content.split('\n')

        # Ищем метод
        method_line = None
        indent_level = 0

        for i, line in enumerate(lines):
            if f"def {method_name}(" in line or f"async def {method_name}(" in line:
                method_line = i
                indent_level = len(line) - len(line.lstrip())
                break

        if method_line is None:
            # Метод не найден - добавляем в конец класса
            logger.warning(f"Method {method_name} not found, adding to end")
            return content + "\n" + publisher_code

        # Находим позицию вставки
        insert_line = method_line + 1  # После def

        # Добавляем indent
        indented_code = self._add_indent(publisher_code, indent_level + 4)

        lines.insert(insert_line, indented_code)
        return '\n'.join(lines)

    def _insert_subscriber(
        self,
        content: str,
        handler_code: str,
        subscribe_code: str
    ) -> str:
        """Вставляет subscriber и handler"""
        # Добавляем handler в конец класса
        lines = content.split('\n')

        # Ищем последний метод класса
        last_method_line = 0
        for i, line in enumerate(lines):
            if 'def ' in line or 'async def ' in line:
                last_method_line = i

        # Вставляем handler после последнего метода
        lines.insert(last_method_line + 1, handler_code)

        # Ищем __init__ или startup для subscribe
        init_line = None
        for i, line in enumerate(lines):
            if 'def __init__' in line or 'def startup' in line:
                init_line = i
                break

        if init_line:
            # Вставляем subscribe в конец __init__
            indent_level = len(lines[init_line]) - len(lines[init_line].lstrip())
            indented_subscribe = self._add_indent(subscribe_code, indent_level + 4)
            lines.insert(init_line + 1, indented_subscribe)

        return '\n'.join(lines)

    def _add_indent(self, code: str, indent: int) -> str:
        """Добавляет indent к коду"""
        spaces = ' ' * indent
        return '\n'.join(spaces + line if line.strip() else line for line in code.split('\n'))

    def _suggest_publisher_location(self, gap: EventGap) -> str:
        """Предлагает где добавить publisher"""
        event_parts = gap.event_name.split('.')

        # bcm.bia.started -> start_bia, execute_bia, etc.
        action = event_parts[-1] if len(event_parts) > 0 else 'execute'
        domain = event_parts[-2] if len(event_parts) > 1 else ''

        return f"{action}_{domain}"

    def _generate_pr_description(self) -> str:
        """Генерирует описание PR"""
        description = "# Auto-generated Event Fixes\n\n"
        description += f"This PR contains {len(self.changes)} event-related fixes:\n\n"

        for i, change in enumerate(self.changes, 1):
            description += f"{i}. **{change.change_type}**: {change.description}\n"
            description += f"   - File: `{change.file_path}`\n\n"

        description += "\n---\n"
        description += "🤖 Generated by Event Executor\n"

        return description

    async def _create_commit(self, branch_name: str, message: str) -> Dict:
        """Создает коммит с изменениями"""
        # TODO: Implement git commit logic
        logger.info(f"Creating commit on branch {branch_name}")
        return {'success': True, 'branch': branch_name}

    async def _create_github_pr(self, branch_name: str, description: str) -> Dict:
        """Создает PR через GitHub API"""
        # TODO: Implement GitHub PR creation
        logger.info(f"Creating GitHub PR for branch {branch_name}")
        return {'success': True, 'url': f'https://github.com/org/repo/pull/XXX'}
