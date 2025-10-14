"""
Virtuous Learning Cycle - Complete Cross-Learning Integration

Orchestrates the complete learning cycle:
Human Activity → AI Learning → Knowledge Creation → Human Learning → Improved Performance

This is the core of the unified learning-knowledge system.
"""

import logging
from typing import Dict, List, Optional, Any
from datetime import datetime
import asyncio

from ..creators.article_creator import ArticleCreator
from ..creators.lesson_creator import LessonCreator

logger = logging.getLogger(__name__)


class VirtuousLearningCycle:
    """
    Complete virtuous learning cycle orchestrator

    Cycle Flow:
    1. User completes BIA workflow → Case saved
    2. Pattern detector finds success pattern → Pattern recorded
    3. Article creator makes KB article → Knowledge created
    4. Lesson creator makes training → Training material created
    5. Other users learn from article → Competency improved
    6. More users succeed using pattern → Success rate increases
    7. AI model improves predictions → Platform gets smarter
    8. → Cycle repeats ♻️
    """

    def __init__(
        self,
        knowledge_base_url: str = "http://localhost:8040",
        ai_orchestrator_url: str = "http://localhost:8000"
    ):
        self.article_creator = ArticleCreator(
            knowledge_base_url=knowledge_base_url,
            ai_orchestrator_url=ai_orchestrator_url
        )
        self.lesson_creator = LessonCreator(
            knowledge_base_url=knowledge_base_url,
            ai_orchestrator_url=ai_orchestrator_url
        )

        # Cycle metrics
        self.cycles_completed = 0
        self.articles_created = 0
        self.lessons_created = 0
        self.patterns_processed = 0
        self.cases_processed = 0

    async def process_workflow_completion(
        self,
        workflow_case: Dict[str, Any],
        tenant_id: str
    ) -> Dict[str, Any]:
        """
        Process completed workflow - Entry point #1 of virtuous cycle

        Args:
            workflow_case: Completed workflow case data
            tenant_id: Tenant identifier

        Returns:
            {
                'case_saved': bool,
                'lesson_created': bool,
                'lesson_id': Optional[str],
                'cycle_status': str
            }
        """
        try:
            logger.info(f"Processing workflow completion: {workflow_case.get('case_id')}")

            result = {
                'case_saved': False,
                'lesson_created': False,
                'lesson_id': None,
                'cycle_status': 'processing'
            }

            # Step 1: Save case (assumed handled elsewhere)
            result['case_saved'] = True
            self.cases_processed += 1

            # Step 2: Create lesson from successful case
            if workflow_case.get('success_score', 0) >= 0.8:
                lesson_id = await self.lesson_creator.create_lesson_from_case(
                    case=workflow_case,
                    tenant_id=tenant_id
                )

                if lesson_id:
                    result['lesson_created'] = True
                    result['lesson_id'] = lesson_id
                    self.lessons_created += 1
                    logger.info(f"✅ Lesson created from case: {lesson_id}")
                else:
                    logger.warning(f"Failed to create lesson from case {workflow_case.get('case_id')}")

            result['cycle_status'] = 'completed' if result['lesson_created'] else 'partial'

            return result

        except Exception as e:
            logger.error(f"Workflow processing failed: {e}")
            return {
                'case_saved': False,
                'lesson_created': False,
                'lesson_id': None,
                'cycle_status': 'failed',
                'error': str(e)
            }

    async def process_pattern_detection(
        self,
        pattern: Dict[str, Any],
        tenant_id: str
    ) -> Dict[str, Any]:
        """
        Process detected pattern - Entry point #2 of virtuous cycle

        Args:
            pattern: Detected pattern data
            tenant_id: Tenant identifier

        Returns:
            {
                'pattern_recorded': bool,
                'article_created': bool,
                'article_id': Optional[str],
                'cycle_status': str
            }
        """
        try:
            logger.info(f"Processing pattern detection: {pattern.get('pattern_name')}")

            result = {
                'pattern_recorded': False,
                'article_created': False,
                'article_id': None,
                'cycle_status': 'processing'
            }

            # Step 1: Record pattern (assumed handled elsewhere)
            result['pattern_recorded'] = True
            self.patterns_processed += 1

            # Step 2: Create article from pattern
            if pattern.get('occurrence_count', 0) >= 5:
                article_id = await self.article_creator.create_article_from_pattern(
                    pattern=pattern,
                    tenant_id=tenant_id
                )

                if article_id:
                    result['article_created'] = True
                    result['article_id'] = article_id
                    self.articles_created += 1
                    logger.info(f"✅ Article created from pattern: {article_id}")
                else:
                    logger.warning(f"Failed to create article from pattern {pattern.get('pattern_name')}")

            result['cycle_status'] = 'completed' if result['article_created'] else 'partial'

            return result

        except Exception as e:
            logger.error(f"Pattern processing failed: {e}")
            return {
                'pattern_recorded': False,
                'article_created': False,
                'article_id': None,
                'cycle_status': 'failed',
                'error': str(e)
            }

    async def run_full_cycle_batch(
        self,
        workflows: List[Dict[str, Any]],
        patterns: List[Dict[str, Any]],
        tenant_id: str
    ) -> Dict[str, Any]:
        """
        Run full virtuous cycle on batch of data

        Args:
            workflows: List of completed workflow cases
            patterns: List of detected patterns
            tenant_id: Tenant identifier

        Returns:
            Complete cycle statistics
        """
        try:
            logger.info(f"Running full virtuous cycle batch: {len(workflows)} workflows, {len(patterns)} patterns")

            # Process workflows and patterns in parallel
            workflow_tasks = [
                self.process_workflow_completion(workflow, tenant_id)
                for workflow in workflows
            ]
            pattern_tasks = [
                self.process_pattern_detection(pattern, tenant_id)
                for pattern in patterns
            ]

            workflow_results = await asyncio.gather(*workflow_tasks, return_exceptions=True)
            pattern_results = await asyncio.gather(*pattern_tasks, return_exceptions=True)

            # Aggregate results
            cycle_stats = {
                'cycles_completed': self.cycles_completed + 1,
                'workflows_processed': len([r for r in workflow_results if isinstance(r, dict) and r.get('case_saved')]),
                'patterns_processed': len([r for r in pattern_results if isinstance(r, dict) and r.get('pattern_recorded')]),
                'lessons_created': len([r for r in workflow_results if isinstance(r, dict) and r.get('lesson_created')]),
                'articles_created': len([r for r in pattern_results if isinstance(r, dict) and r.get('article_created')]),
                'lesson_ids': [r.get('lesson_id') for r in workflow_results if isinstance(r, dict) and r.get('lesson_id')],
                'article_ids': [r.get('article_id') for r in pattern_results if isinstance(r, dict) and r.get('article_id')],
                'errors': [
                    r.get('error') for r in workflow_results + pattern_results
                    if isinstance(r, dict) and r.get('error')
                ],
                'timestamp': datetime.utcnow().isoformat()
            }

            self.cycles_completed += 1

            logger.info(
                f"✅ Virtuous cycle batch complete: "
                f"{cycle_stats['lessons_created']} lessons, "
                f"{cycle_stats['articles_created']} articles created"
            )

            return cycle_stats

        except Exception as e:
            logger.error(f"Batch cycle processing failed: {e}")
            return {
                'cycles_completed': self.cycles_completed,
                'error': str(e),
                'timestamp': datetime.utcnow().isoformat()
            }

    async def analyze_cycle_effectiveness(self, tenant_id: str) -> Dict[str, Any]:
        """
        Analyze virtuous cycle effectiveness

        Metrics:
        - Knowledge creation rate
        - Learning impact (users completing lessons)
        - Performance improvement (before/after pattern articles)
        - Cycle velocity (time from detection to knowledge)
        """
        try:
            return {
                'total_cycles': self.cycles_completed,
                'knowledge_created': {
                    'articles': self.articles_created,
                    'lessons': self.lessons_created,
                    'total': self.articles_created + self.lessons_created
                },
                'inputs_processed': {
                    'patterns': self.patterns_processed,
                    'cases': self.cases_processed,
                    'total': self.patterns_processed + self.cases_processed
                },
                'conversion_rate': {
                    'pattern_to_article': (
                        self.articles_created / self.patterns_processed
                        if self.patterns_processed > 0 else 0
                    ),
                    'case_to_lesson': (
                        self.lessons_created / self.cases_processed
                        if self.cases_processed > 0 else 0
                    )
                },
                'cycle_health': self._assess_cycle_health(),
                'timestamp': datetime.utcnow().isoformat()
            }

        except Exception as e:
            logger.error(f"Cycle analysis failed: {e}")
            return {'error': str(e)}

    def _assess_cycle_health(self) -> str:
        """Assess overall health of virtuous cycle"""
        if self.cycles_completed == 0:
            return 'not_started'

        knowledge_per_cycle = (self.articles_created + self.lessons_created) / self.cycles_completed

        if knowledge_per_cycle >= 5:
            return 'excellent'
        elif knowledge_per_cycle >= 3:
            return 'good'
        elif knowledge_per_cycle >= 1:
            return 'fair'
        else:
            return 'needs_improvement'

    def get_cycle_metrics(self) -> Dict[str, Any]:
        """Get current cycle metrics"""
        return {
            'cycles_completed': self.cycles_completed,
            'articles_created': self.articles_created,
            'lessons_created': self.lessons_created,
            'patterns_processed': self.patterns_processed,
            'cases_processed': self.cases_processed,
            'cycle_health': self._assess_cycle_health()
        }
