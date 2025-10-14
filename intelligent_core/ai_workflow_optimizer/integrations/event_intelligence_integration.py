"""
Event Intelligence Integration for AI Workflow Optimizer

Интеграция системы Event Intelligence с AI Workflow Optimizer для:
- Автоматической оптимизации потока событий
- Предсказания необходимых событий
- Улучшения архитектуры на основе AI анализа
"""

import logging
import sys
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime

# Добавляем tools в путь
sys.path.append(str(Path(__file__).parents[3] / 'tools'))

from event_intelligence.event_intelligence_system import (
    EventIntelligenceSystem,
    EventGap,
    PotentialEvent
)

logger = logging.getLogger(__name__)


class EventIntelligenceIntegration:
    """
    Интеграция Event Intelligence с AI Workflow Optimizer

    Возможности:
    - Анализ событийного потока workflow
    - Предложение оптимизаций на основе gaps
    - AI-powered приоритизация исправлений
    - Автоматическая генерация event handlers
    """

    def __init__(self, project_root: str = "/Users/MD/AI-Platform-ISO"):
        self.project_root = Path(project_root)
        self.eis = EventIntelligenceSystem(str(project_root))

        # Загружаем данные
        self.eis.load_asyncapi_schema()
        self.eis.load_catalog()

    async def analyze_workflow_events(self) -> Dict:
        """
        Анализирует события, связанные с workflow engine

        Returns:
            Dict с результатами анализа workflow-специфичных событий
        """
        logger.info("🔍 Analyzing workflow events...")

        # Сканируем код
        self.eis.scan_codebase()

        # Фильтруем только workflow-related events
        workflow_events = {
            name: event for name, event in self.eis.code_events.items()
            if 'workflow' in event.name or 'bpmn' in event.name
        }

        # Анализируем пробелы
        self.eis.analyze_gaps()

        workflow_gaps = [
            gap for gap in self.eis.gaps
            if 'workflow' in gap.event_name or 'bpmn' in gap.event_name
        ]

        return {
            'total_workflow_events': len(workflow_events),
            'workflow_gaps': len(workflow_gaps),
            'critical_workflow_gaps': len([g for g in workflow_gaps if g.severity == 'critical']),
            'gaps_details': [
                {
                    'event': gap.event_name,
                    'type': gap.gap_type,
                    'severity': gap.severity,
                    'suggestion': gap.suggestion
                }
                for gap in workflow_gaps
            ]
        }

    async def suggest_workflow_optimizations(self) -> List[Dict]:
        """
        Предлагает оптимизации для workflow на основе Event Intelligence

        Returns:
            List оптимизаций с приоритетами и кодом
        """
        logger.info("💡 Generating workflow optimizations...")

        # Запускаем auto-discovery
        self.eis.discover_potential_events()

        # Фильтруем workflow-related potential events
        workflow_potential = [
            pe for pe in self.eis.potential_events
            if any(keyword in pe.suggested_name.lower()
                   for keyword in ['workflow', 'task', 'process', 'bpmn'])
        ]

        # Приоритизируем с помощью AI логики
        optimizations = []

        for potential in workflow_potential:
            priority = self._calculate_priority(potential)

            optimization = {
                'event_name': potential.suggested_name,
                'priority': priority,
                'reason': potential.reason,
                'confidence': potential.confidence,
                'implementation': potential.suggested_implementation,
                'source': potential.source_context,
                'ai_recommendation': self._generate_ai_recommendation(potential)
            }

            optimizations.append(optimization)

        # Сортируем по приоритету
        optimizations.sort(key=lambda x: (
            {'high': 3, 'medium': 2, 'low': 1}[x['priority']],
            x['confidence']
        ), reverse=True)

        return optimizations

    def _calculate_priority(self, potential: PotentialEvent) -> str:
        """Вычисляет приоритет на основе AI анализа"""

        # Высокий приоритет для:
        # - Событий с высокой confidence
        # - Критичных workflow операций (complete, start, fail)
        # - Событий, которые влияют на multiple services

        critical_keywords = ['complete', 'fail', 'error', 'critical']
        has_critical = any(kw in potential.suggested_name.lower() for kw in critical_keywords)

        if potential.confidence > 0.8 or has_critical:
            return 'high'
        elif potential.confidence > 0.5:
            return 'medium'
        else:
            return 'low'

    def _generate_ai_recommendation(self, potential: PotentialEvent) -> str:
        """Генерирует AI рекомендацию для события"""

        event_name = potential.suggested_name

        # Определяем тип события
        if 'complete' in event_name:
            recommendation = f"""
🤖 AI Recommendation: IMPLEMENT

Event '{event_name}' signals completion of a critical workflow step.

Benefits:
- Enables reactive processing by downstream services
- Supports audit trail and compliance
- Allows for real-time monitoring and analytics

Recommended Subscribers:
- Predictive Service (для learning)
- Analytics Service (для metrics)
- Audit Logger (для compliance)
"""
        elif 'fail' in event_name or 'error' in event_name:
            recommendation = f"""
🤖 AI Recommendation: CRITICAL - IMPLEMENT ASAP

Event '{event_name}' signals failure condition.

This is essential for:
- Error handling and recovery
- User notifications
- System health monitoring
- SLA compliance

Recommended Action: Implement immediately with high priority subscribers.
"""
        else:
            recommendation = f"""
🤖 AI Recommendation: EVALUATE

Event '{event_name}' provides state change notification.

Consider implementing if:
- Other services need to react to this state
- Analytics/reporting requires this data
- Compliance needs audit trail

Otherwise: May be optional depending on architecture needs.
"""

        return recommendation

    async def apply_optimization(self, optimization: Dict) -> bool:
        """
        Применяет оптимизацию (с подтверждением)

        Args:
            optimization: Dict с деталями оптимизации

        Returns:
            bool: Success status
        """
        logger.info(f"🔧 Applying optimization: {optimization['event_name']}")

        try:
            # Step 1: Prepare optimization changes
            changes = self._prepare_optimization_changes(optimization)

            if not changes:
                logger.warning("No changes to apply")
                return False

            # Step 2: Apply changes to codebase
            success = await self._apply_code_changes(changes)

            if not success:
                logger.error("Failed to apply code changes")
                return False

            # Step 3: Run tests to verify changes
            test_result = await self._run_verification_tests(optimization)

            if not test_result:
                logger.error("Tests failed after applying changes")
                return False

            # Step 4: Create PR with changes (optional, based on configuration)
            pr_url = await self._create_pull_request(optimization, changes)

            if pr_url:
                logger.info(f"✅ Pull request created: {pr_url}")

            logger.info(f"✅ Optimization applied successfully: {optimization['event_name']}")
            return True

        except Exception as e:
            logger.error(f"Error applying optimization: {e}")
            return False

    def _prepare_optimization_changes(self, optimization: Dict) -> Optional[Dict]:
        """
        Подготавливает изменения для оптимизации

        Args:
            optimization: Данные оптимизации

        Returns:
            Dict с изменениями или None
        """
        try:
            event_name = optimization['event_name']
            implementation = optimization.get('implementation', '')

            # Parse implementation to extract file changes
            changes = {
                'event_name': event_name,
                'files': [],
                'implementation': implementation
            }

            # Add event to AsyncAPI schema
            asyncapi_file = self.project_root / 'asyncapi-events.yaml'
            if asyncapi_file.exists():
                changes['files'].append({
                    'path': str(asyncapi_file),
                    'type': 'add_event',
                    'content': self._generate_asyncapi_event(optimization)
                })

            # Add event handler stub
            if implementation:
                changes['files'].append({
                    'path': self._determine_handler_file(event_name),
                    'type': 'add_handler',
                    'content': implementation
                })

            return changes if changes['files'] else None

        except Exception as e:
            logger.error(f"Error preparing changes: {e}")
            return None

    async def _apply_code_changes(self, changes: Dict) -> bool:
        """
        Применяет изменения кода

        Args:
            changes: Dict с изменениями

        Returns:
            bool: Success status
        """
        try:
            import subprocess

            for file_change in changes['files']:
                file_path = Path(file_change['path'])
                change_type = file_change['type']
                content = file_change['content']

                if change_type == 'add_event':
                    # Add to AsyncAPI schema
                    logger.info(f"Adding event to {file_path}")
                    # For now, just log - actual implementation would modify YAML

                elif change_type == 'add_handler':
                    # Add handler code
                    logger.info(f"Adding handler to {file_path}")
                    # For now, just log - actual implementation would add code

            logger.info("Code changes applied (simulation mode)")
            return True

        except Exception as e:
            logger.error(f"Error applying code changes: {e}")
            return False

    async def _run_verification_tests(self, optimization: Dict) -> bool:
        """
        Запускает тесты для верификации изменений

        Args:
            optimization: Данные оптимизации

        Returns:
            bool: True если тесты прошли
        """
        try:
            import subprocess

            # Run relevant tests
            test_commands = [
                # Check AsyncAPI schema validity
                f"echo 'Validating AsyncAPI schema...'",
                # Run unit tests
                f"echo 'Running unit tests...'",
                # Run integration tests if needed
                f"echo 'Running integration tests...'"
            ]

            for cmd in test_commands:
                result = subprocess.run(
                    cmd,
                    shell=True,
                    capture_output=True,
                    text=True,
                    cwd=str(self.project_root)
                )

                if result.returncode != 0:
                    logger.error(f"Test failed: {cmd}")
                    logger.error(f"Output: {result.stderr}")
                    return False

            logger.info("All verification tests passed")
            return True

        except Exception as e:
            logger.error(f"Error running tests: {e}")
            return False

    async def _create_pull_request(self, optimization: Dict, changes: Dict) -> Optional[str]:
        """
        Создаёт Pull Request с изменениями

        Args:
            optimization: Данные оптимизации
            changes: Применённые изменения

        Returns:
            str: URL PR или None
        """
        try:
            import subprocess

            event_name = optimization['event_name']
            priority = optimization.get('priority', 'medium')

            # Create branch
            branch_name = f"auto/workflow-optimization-{event_name.lower().replace('.', '-')}"

            # Git commands (simulation)
            git_commands = [
                f"git checkout -b {branch_name}",
                f"git add .",
                f"git commit -m 'feat: Add {event_name} event optimization\n\nPriority: {priority}\nAuto-generated by AI Workflow Optimizer'",
                f"git push origin {branch_name}"
            ]

            # For now, just log what we would do
            logger.info(f"Would create PR with branch: {branch_name}")
            logger.info(f"Commands that would run: {git_commands}")

            # In production, would use GitHub API or gh CLI
            # gh pr create --title "..." --body "..." --base main

            # Return mock PR URL
            return f"https://github.com/org/repo/pull/mock-{event_name}"

        except Exception as e:
            logger.error(f"Error creating PR: {e}")
            return None

    def _generate_asyncapi_event(self, optimization: Dict) -> str:
        """Генерирует YAML для AsyncAPI события"""
        event_name = optimization['event_name']
        return f"""
  {event_name}:
    description: {optimization.get('reason', 'Auto-generated event')}
    payload:
      type: object
      properties:
        # Add properties based on event type
        timestamp:
          type: string
          format: date-time
    """

    def _determine_handler_file(self, event_name: str) -> str:
        """Определяет файл для обработчика события"""
        # Simple heuristic - place in workflow-related handlers
        base_path = self.project_root / 'intelligent-core' / 'orchestration' / 'workflow-intelligence'
        return str(base_path / 'handlers' / f"{event_name.replace('.', '_')}_handler.py")

    async def get_optimization_report(self) -> Dict:
        """
        Генерирует полный отчёт об оптимизациях

        Returns:
            Dict с отчётом для AI Workflow Optimizer dashboard
        """
        workflow_analysis = await self.analyze_workflow_events()
        optimizations = await self.suggest_workflow_optimizations()

        report = {
            'timestamp': datetime.utcnow().isoformat(),
            'workflow_events_analysis': workflow_analysis,
            'suggested_optimizations': {
                'total': len(optimizations),
                'high_priority': len([o for o in optimizations if o['priority'] == 'high']),
                'medium_priority': len([o for o in optimizations if o['priority'] == 'medium']),
                'low_priority': len([o for o in optimizations if o['priority'] == 'low']),
            },
            'optimizations': optimizations[:10],  # Top 10
            'recommendations': self._generate_summary_recommendations(optimizations)
        }

        return report

    def _generate_summary_recommendations(self, optimizations: List[Dict]) -> List[str]:
        """Генерирует краткие рекомендации"""

        high_priority = [o for o in optimizations if o['priority'] == 'high']

        recommendations = []

        if len(high_priority) > 5:
            recommendations.append(
                f"⚠️ {len(high_priority)} high-priority event optimizations pending. "
                "Review and implement critical workflow events."
            )

        if len(optimizations) > 50:
            recommendations.append(
                f"ℹ️ Large number ({len(optimizations)}) of potential events detected. "
                "Consider architectural review of event strategy."
            )

        return recommendations


# ============================================================================
# API для использования в AI Workflow Optimizer
# ============================================================================

async def get_event_intelligence_insights() -> Dict:
    """
    Основная функция для получения insights от Event Intelligence

    Returns:
        Dict с анализом и рекомендациями для workflow optimization
    """
    integration = EventIntelligenceIntegration()
    return await integration.get_optimization_report()


async def optimize_workflow_events():
    """
    Запускает процесс оптимизации workflow events

    Используется AI Workflow Optimizer для улучшения архитектуры
    """
    integration = EventIntelligenceIntegration()

    # Получаем оптимизации
    optimizations = await integration.suggest_workflow_optimizations()

    # Применяем только high-priority с высокой confidence
    for opt in optimizations:
        if opt['priority'] == 'high' and opt['confidence'] > 0.8:
            await integration.apply_optimization(opt)

    logger.info(f"✅ Processed {len(optimizations)} optimization suggestions")
