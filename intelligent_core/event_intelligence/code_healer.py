"""
Code Healer - Автоматическое исправление кода intelligent-core

🔧 УМНОЕ ИСПРАВЛЕНИЕ:
- Анализ импортов и автофикс
- Установка недостающих зависимостей
- Исправление путей и относительных импортов
- Адаптация портов и конфигураций
- Обучение на ошибках

Использует:
- AST парсинг
- Pattern matching
- AI-powered suggestions
"""

import ast
import os
import sys
import logging
import subprocess
from pathlib import Path
from typing import Dict, List, Set, Optional, Tuple
from dataclasses import dataclass
from collections import defaultdict

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class CodeIssue:
    """Проблема в коде"""
    file_path: str
    line_number: int
    issue_type: str  # 'missing_import', 'wrong_import', 'missing_dependency'
    description: str
    fix_code: str
    confidence: float  # 0-1


@dataclass
class HealingResult:
    """Результат исправления"""
    file_path: str
    issues_found: int
    issues_fixed: int
    remaining_issues: List[CodeIssue]
    success: bool


class CodeHealer:
    """
    Автоматическое исправление кода на основе анализа ошибок

    Возможности:
    1. Автофикс импортов
    2. Установка зависимостей
    3. Исправление путей
    4. Адаптация конфигураций
    """

    def __init__(self, project_root: str = "/Users/MD/AI-Platform-ISO"):
        self.project_root = Path(project_root)
        self.intelligent_core = self.project_root / "intelligent-core"
        self.shared = self.project_root / "shared"

        # База знаний: что где находится
        self.import_map = self._build_import_map()

        # История исправлений
        self.healing_history: List[HealingResult] = []

    def _build_import_map(self) -> Dict[str, str]:
        """Строит карту: что откуда импортировать"""
        return {
            # EventBus
            'get_eventbus': 'shared.eventbus',
            'init_eventbus': 'shared.eventbus',
            'EventBus': 'shared.eventbus',

            # Database
            'get_db': 'shared.database',
            'get_supabase_client': 'shared.database',

            # AI Foundation
            'LLMRouter': 'ai_foundation.llm.llm_router',
            'RAGPipeline': 'ai_foundation.rag.pipeline',
            'ContextAdvisor': 'ai_foundation.context',

            # Workflow Intelligence (как библиотека)
            'WorkflowEngine': 'workflow_intelligence.core.workflow_engine',
            'StateMachine': 'workflow_intelligence.core.state_machine',
            'CaseCollector': 'workflow_intelligence.storage.case_collector',

            # Common types
            'asyncpg': 'asyncpg',  # External dependency
        }

    # ========================================================================
    # MAIN HEALING PROCESS
    # ========================================================================

    async def heal_service(self, service_name: str, dry_run: bool = False) -> HealingResult:
        """
        Исцеляет один сервис

        Args:
            service_name: Имя сервиса (community_intelligence, predictive, etc.)
            dry_run: Только показать что будет исправлено

        Returns:
            HealingResult с результатами
        """
        logger.info(f"🏥 Healing service: {service_name}")

        service_dir = self.intelligent_core / service_name
        if not service_dir.exists():
            logger.error(f"❌ Service not found: {service_dir}")
            return HealingResult(str(service_dir), 0, 0, [], False)

        # Собираем все Python файлы
        py_files = list(service_dir.glob("**/*.py"))
        logger.info(f"   Found {len(py_files)} Python files")

        all_issues = []
        fixed_count = 0

        # Анализируем каждый файл
        for py_file in py_files:
            if 'venv' in str(py_file) or '__pycache__' in str(py_file):
                continue

            issues = self._analyze_file(py_file)
            all_issues.extend(issues)

            # Применяем исправления
            if not dry_run and issues:
                fixed = self._apply_fixes(py_file, issues)
                fixed_count += fixed

        # Проверяем dependencies
        missing_deps = self._check_dependencies(service_dir)
        if missing_deps and not dry_run:
            self._install_dependencies(missing_deps)
            fixed_count += len(missing_deps)

        remaining = [i for i in all_issues if i.confidence < 0.8]
        success = len(remaining) == 0

        result = HealingResult(
            file_path=str(service_dir),
            issues_found=len(all_issues),
            issues_fixed=fixed_count,
            remaining_issues=remaining,
            success=success
        )

        self.healing_history.append(result)

        logger.info(f"✅ Healed {service_name}: {fixed_count}/{len(all_issues)} issues fixed")
        return result

    # ========================================================================
    # FILE ANALYSIS
    # ========================================================================

    def _analyze_file(self, file_path: Path) -> List[CodeIssue]:
        """Анализирует файл на проблемы"""
        issues = []

        try:
            with open(file_path, 'r') as f:
                content = f.read()
                tree = ast.parse(content)
        except SyntaxError as e:
            logger.warning(f"⚠️ Syntax error in {file_path}: {e}")
            return []
        except Exception as e:
            logger.warning(f"⚠️ Cannot parse {file_path}: {e}")
            return []

        # Анализируем импорты
        issues.extend(self._analyze_imports(file_path, tree, content))

        # Анализируем использование undefined names
        issues.extend(self._find_undefined_names(file_path, tree))

        return issues

    def _analyze_imports(self, file_path: Path, tree: ast.AST, content: str) -> List[CodeIssue]:
        """Анализирует импорты"""
        issues = []
        lines = content.split('\n')

        for node in ast.walk(tree):
            # From X import Y
            if isinstance(node, ast.ImportFrom):
                if node.module:
                    # Проверяем relative imports
                    if node.module.startswith('.'):
                        # Relative import _ может не работать при запуске
                        if 'main.py' in str(file_path):
                            fix = self._fix_relative_import(node, file_path)
                            if fix:
                                issues.append(CodeIssue(
                                    file_path=str(file_path),
                                    line_number=node.lineno,
                                    issue_type='relative_import_in_main',
                                    description=f"Relative import {node.module} in main.py won't work",
                                    fix_code=fix,
                                    confidence=0.9
                                ))

                    # Проверяем несуществующие модули
                    for alias in node.names:
                        name = alias.name
                        # Проверяем в import_map
                        if name in self.import_map and node.module != self.import_map[name]:
                            fix = f"from {self.import_map[name]} import {name}"
                            issues.append(CodeIssue(
                                file_path=str(file_path),
                                line_number=node.lineno,
                                issue_type='wrong_import',
                                description=f"Wrong import path for {name}",
                                fix_code=fix,
                                confidence=0.95
                            ))

        return issues

    def _fix_relative_import(self, node: ast.ImportFrom, file_path: Path) -> Optional[str]:
        """Исправляет relative import на absolute"""
        # Определяем, где мы находимся относительно intelligent-core
        try:
            rel_path = file_path.relative_to(self.intelligent_core)
            parts = rel_path.parts[:-1]  # Убираем имя файла

            # Если это .config, то intelligent_core.service.config
            if node.module.startswith('.'):
                module_parts = node.module.lstrip('.').split('.')
                full_module = '.'.join(parts) + '.' + '.'.join(module_parts)

                names = ', '.join(alias.name for alias in node.names)
                return f"from {full_module} import {names}"
        except ValueError:
            pass

        return None

    def _find_undefined_names(self, file_path: Path, tree: ast.AST) -> List[CodeIssue]:
        """Находит использование неопределённых имён"""
        issues = []

        # Собираем все определённые имена
        defined = set()
        imported = set()

        for node in ast.walk(tree):
            # Импорты
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imported.add(alias.asname or alias.name)
            elif isinstance(node, ast.ImportFrom):
                for alias in node.names:
                    imported.add(alias.asname or alias.name)

            # Определения
            elif isinstance(node, ast.FunctionDef):
                defined.add(node.name)
            elif isinstance(node, ast.ClassDef):
                defined.add(node.name)
            elif isinstance(node, ast.Assign):
                for target in node.targets:
                    if isinstance(target, ast.Name):
                        defined.add(target.id)

        # Проверяем использование
        for node in ast.walk(tree):
            if isinstance(node, ast.Name) and isinstance(node.ctx, ast.Load):
                name = node.id

                # Если не определено и не импортировано - возможно проблема
                if name not in defined and name not in imported and name not in dir(__builtins__):
                    # Проверяем, знаем ли мы этот импорт
                    if name in self.import_map:
                        module = self.import_map[name]
                        fix = f"from {module} import {name}"
                        issues.append(CodeIssue(
                            file_path=str(file_path),
                            line_number=node.lineno,
                            issue_type='missing_import',
                            description=f"Undefined name: {name}",
                            fix_code=fix,
                            confidence=0.85
                        ))

        return issues

    # ========================================================================
    # APPLYING FIXES
    # ========================================================================

    def _apply_fixes(self, file_path: Path, issues: List[CodeIssue]) -> int:
        """Применяет исправления к файлу"""
        fixed_count = 0

        # Группируем по типу
        high_confidence = [i for i in issues if i.confidence >= 0.8]

        if not high_confidence:
            return 0

        try:
            with open(file_path, 'r') as f:
                lines = f.readlines()

            # Добавляем недостающие импорты в начало (после docstring)
            missing_imports = [i for i in high_confidence if i.issue_type == 'missing_import']

            if missing_imports:
                # Найдём место для вставки (после docstring и существующих импортов)
                insert_line = self._find_import_insertion_point(lines)

                # Собираем уникальные импорты
                import_fixes = set(i.fix_code for i in missing_imports)

                for fix in import_fixes:
                    lines.insert(insert_line, fix + '\n')
                    insert_line += 1
                    fixed_count += 1

                # Сохраняем
                with open(file_path, 'w') as f:
                    f.writelines(lines)

                logger.info(f"   ✅ Added {len(import_fixes)} imports to {file_path.name}")

        except Exception as e:
            logger.error(f"   ❌ Error fixing {file_path}: {e}")

        return fixed_count

    def _find_import_insertion_point(self, lines: List[str]) -> int:
        """Находит точку для вставки импортов"""
        in_docstring = False
        last_import = 0

        for i, line in enumerate(lines):
            stripped = line.strip()

            # Пропускаем docstring
            if '"""' in line or "'''" in line:
                in_docstring = not in_docstring
                continue

            if in_docstring:
                continue

            # Нашли import или from
            if stripped.startswith('import ') or stripped.startswith('from '):
                last_import = i + 1

            # Если нашли код после импортов - вставляем перед ним
            if stripped and not stripped.startswith('#') and last_import > 0:
                if not (stripped.startswith('import ') or stripped.startswith('from ')):
                    return last_import

        return max(last_import, 3)  # Минимум после 3-й строки

    # ========================================================================
    # DEPENDENCIES
    # ========================================================================

    def _check_dependencies(self, service_dir: Path) -> Set[str]:
        """Проверяет недостающие зависимости"""
        missing = set()

        # Проверяем requirements.txt
        req_file = service_dir / "requirements.txt"
        if req_file.exists():
            with open(req_file, 'r') as f:
                required = {line.split('==')[0].split('>=')[0].strip()
                           for line in f if line.strip() and not line.startswith('#')}
        else:
            required = set()

        # Проверяем что установлено
        try:
            installed_output = subprocess.check_output(
                ['pip3', 'list', '--format=freeze'],
                stderr=subprocess.DEVNULL
            ).decode()
            installed = {line.split('==')[0] for line in installed_output.split('\n') if line}
        except Exception:
            installed = set()

        # Известные зависимости из import_map
        known_deps = {'asyncpg', 'apscheduler', 'uvicorn', 'fastapi'}

        for dep in known_deps:
            if dep in self.import_map.values() or any(dep in v for v in self.import_map.values()):
                if dep not in installed:
                    missing.add(dep)

        return missing

    def _install_dependencies(self, deps: Set[str]):
        """Устанавливает недостающие зависимости"""
        logger.info(f"📦 Installing {len(deps)} dependencies: {deps}")

        for dep in deps:
            try:
                subprocess.check_call(
                    ['pip3', 'install', dep, '--quiet'],
                    stdout=subprocess.DEVNULL
                )
                logger.info(f"   ✅ Installed {dep}")
            except subprocess.CalledProcessError as e:
                logger.error(f"   ❌ Failed to install {dep}: {e}")

    # ========================================================================
    # BATCH HEALING
    # ========================================================================

    async def heal_all_services(self, dry_run: bool = False) -> List[HealingResult]:
        """Исцеляет все сервисы в intelligent-core"""
        logger.info("🏥 Starting batch healing of intelligent-core services...")

        services = [
            'community_intelligence',
            'predictive',
            'collective',
        ]

        results = []
        for service in services:
            result = await self.heal_service(service, dry_run=dry_run)
            results.append(result)

        self._print_summary(results)
        return results

    def _print_summary(self, results: List[HealingResult]):
        """Выводит сводку"""
        print("\n" + "="*70)
        print("🏥 CODE HEALER SUMMARY")
        print("="*70)

        total_issues = sum(r.issues_found for r in results)
        total_fixed = sum(r.issues_fixed for r in results)

        print(f"\n📊 Total Issues: {total_issues}")
        print(f"✅ Fixed: {total_fixed}")
        print(f"⚠️ Remaining: {total_issues - total_fixed}")

        print(f"\n📁 Services:")
        for r in results:
            status = "✅" if r.success else "⚠️"
            service_name = Path(r.file_path).name
            print(f"  {status} {service_name}: {r.issues_fixed}/{r.issues_found} fixed")

        print("\n" + "="*70 + "\n")


async def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(description='Code Healer - Auto-fix intelligent-core')
    parser.add_argument('--service', type=str, help='Specific service to heal')
    parser.add_argument('--all', action='store_true', help='Heal all services')
    parser.add_argument('--dry-run', action='store_true', help='Show what would be done')

    args = parser.parse_args()

    healer = CodeHealer()

    if args.all:
        await healer.heal_all_services(dry_run=args.dry_run)
    elif args.service:
        await healer.heal_service(args.service, dry_run=args.dry_run)
    else:
        print("Usage: python3 code_healer.py --all [--dry-run]")
        print("   or: python3 code_healer.py --service <name> [--dry-run]")


if __name__ == '__main__':
    import asyncio
    asyncio.run(main())
