"""
Lesson Creator - Workflow Case → Training Lesson

Automatically creates training lessons from successful workflow cases.
Part of the cross-learning virtuous cycle.
"""

import logging
from typing import Dict, List, Optional, Any
from datetime import datetime
import aiohttp

logger = logging.getLogger(__name__)


class LessonCreator:
    """
    Creates training lessons from workflow cases

    Workflow:
    1. Successful workflow case completed
    2. AI extracts learning points
    3. Lesson created with exercises
    4. Lesson added to training programs
    5. Users learn from real cases
    """

    def __init__(
        self,
        knowledge_base_url: str = "http://localhost:8040",
        ai_orchestrator_url: str = "http://localhost:8000",
        min_success_score: float = 0.8
    ):
        self.knowledge_base_url = knowledge_base_url
        self.ai_orchestrator_url = ai_orchestrator_url
        self.min_success_score = min_success_score

    async def create_lesson_from_case(
        self,
        case: Dict[str, Any],
        tenant_id: str
    ) -> Optional[str]:
        """
        Create training lesson from workflow case

        Args:
            case: {
                'case_id': str,
                'workflow_type': str,
                'success_score': float,
                'steps_completed': List[Dict],
                'decisions_made': List[Dict],
                'outcomes': Dict,
                'metadata': Dict
            }
            tenant_id: Tenant identifier

        Returns:
            lesson_id if successful, None otherwise
        """
        try:
            # Check success score
            if case.get('success_score', 0) < self.min_success_score:
                logger.info(
                    f"Case '{case.get('case_id')}' below success threshold "
                    f"({case.get('success_score')} < {self.min_success_score})"
                )
                return None

            logger.info(f"Creating lesson from case: {case.get('case_id')}")

            # Generate lesson content using AI
            lesson_content = await self._generate_lesson_content(case)

            if not lesson_content:
                logger.warning("Failed to generate lesson content")
                return None

            # Create lesson in knowledge base
            lesson_id = await self._create_kb_lesson(
                content=lesson_content,
                case=case,
                tenant_id=tenant_id
            )

            if lesson_id:
                logger.info(f"Lesson created successfully: {lesson_id}")
                return lesson_id
            else:
                logger.warning("Failed to create KB lesson")
                return None

        except Exception as e:
            logger.error(f"Lesson creation failed: {e}")
            return None

    async def _generate_lesson_content(
        self,
        case: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """Generate lesson content using AI"""
        try:
            prompt = self._build_lesson_generation_prompt(case)

            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.ai_orchestrator_url}/nlp/query",
                    json={
                        'query': prompt,
                        'context': {
                            'case': case,
                            'ai_organ': 'lesson_creator',
                            'task': 'generate_lesson'
                        },
                        'user_role': 'lesson_creator'
                    },
                    timeout=aiohttp.ClientTimeout(total=60)
                ) as response:
                    if response.status == 200:
                        result = await response.json()
                        return self._format_lesson_content(result, case)
                    else:
                        logger.warning(f"AI orchestrator returned status {response.status}")
                        return self._fallback_lesson_content(case)

        except Exception as e:
            logger.error(f"Lesson content generation failed: {e}")
            return self._fallback_lesson_content(case)

    def _build_lesson_generation_prompt(self, case: Dict[str, Any]) -> str:
        """Build AI prompt for lesson generation"""
        return f"""
TRAINING LESSON GENERATION REQUEST

SUCCESSFUL WORKFLOW CASE:
Case ID: {case.get('case_id')}
Workflow Type: {case.get('workflow_type')}
Success Score: {case.get('success_score', 0)*100:.0f}%

STEPS COMPLETED:
{chr(10).join(f"{i+1}. {step.get('name', 'Unknown')}: {step.get('description', '')}" for i, step in enumerate(case.get('steps_completed', [])))}

DECISIONS MADE:
{chr(10).join(f"- {decision.get('question', 'Unknown')}: {decision.get('answer', '')}" for decision in case.get('decisions_made', []))}

OUTCOMES:
{case.get('outcomes', {})}

TASK: Generate a comprehensive training lesson that helps users:
1. Learn from this successful case
2. Understand the key decisions and their rationale
3. Apply the same approach to similar situations
4. Avoid common pitfalls
5. Build practical competency

LESSON STRUCTURE REQUIRED:
- Title (engaging, specific)
- Learning Objectives (3-5 clear objectives)
- Case Overview (context, challenge, solution)
- Key Learning Points (what worked and why)
- Step-by-Step Breakdown (detailed walkthrough)
- Decision Analysis (why specific choices were made)
- Best Practices (generalizable principles)
- Practice Exercises (hands-on application)
- Assessment Questions (verify understanding)
- Related Resources (standards, procedures)

Provide structured, practical knowledge that builds real-world competency.
"""

    def _format_lesson_content(
        self,
        ai_result: Dict[str, Any],
        case: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Format AI-generated content into lesson structure"""
        return {
            'title': ai_result.get('title', f"Lesson from {case.get('workflow_type')} Case"),
            'learning_objectives': ai_result.get('learning_objectives', []),
            'content': ai_result.get('content', ''),
            'exercises': ai_result.get('exercises', []),
            'assessment': ai_result.get('assessment', []),
            'category': 'case_study',
            'difficulty': self._determine_difficulty(case),
            'duration_minutes': ai_result.get('duration_minutes', 30),
            'tags': [
                'case_study',
                case.get('workflow_type', 'general'),
                f"success_{int(case.get('success_score', 0)*100)}"
            ],
            'metadata': {
                'source_case_id': case.get('case_id'),
                'workflow_type': case.get('workflow_type'),
                'success_score': case.get('success_score'),
                'auto_generated': True,
                'generated_at': datetime.utcnow().isoformat(),
                'source': 'workflow_case'
            }
        }

    def _determine_difficulty(self, case: Dict[str, Any]) -> str:
        """Determine lesson difficulty from case complexity"""
        steps_count = len(case.get('steps_completed', []))
        decisions_count = len(case.get('decisions_made', []))

        if steps_count <= 3 and decisions_count <= 2:
            return 'beginner'
        elif steps_count <= 6 and decisions_count <= 5:
            return 'intermediate'
        else:
            return 'advanced'

    def _fallback_lesson_content(self, case: Dict[str, Any]) -> Dict[str, Any]:
        """Fallback lesson content when AI is unavailable"""
        content = f"""
# Case Study: {case.get('workflow_type')}

## Learning Objectives
- Understand the {case.get('workflow_type')} workflow
- Apply successful strategies from real cases
- Make informed decisions in similar situations

## Case Overview
**Case ID:** {case.get('case_id')}
**Success Score:** {case.get('success_score', 0)*100:.0f}%

## Steps Completed
{chr(10).join(f"{i+1}. {step.get('name', 'Unknown')}" for i, step in enumerate(case.get('steps_completed', [])))}

## Key Decisions
{chr(10).join(f"- **{decision.get('question', 'Unknown')}**: {decision.get('answer', '')}" for decision in case.get('decisions_made', []))}

## Outcomes
{case.get('outcomes', {})}

## Practice Exercise
Review this case and identify:
1. What made this case successful?
2. Which decisions were most critical?
3. How would you apply this to your context?

## Notes
This lesson was automatically generated from a successful workflow case.
Please review and enhance with specific organizational context.
"""

        return {
            'title': f"Lesson from {case.get('workflow_type')} Case",
            'learning_objectives': [
                f"Understand the {case.get('workflow_type')} workflow",
                "Apply successful strategies from real cases"
            ],
            'content': content,
            'exercises': [],
            'assessment': [],
            'category': 'case_study',
            'difficulty': self._determine_difficulty(case),
            'duration_minutes': 30,
            'tags': ['case_study', 'auto-generated'],
            'metadata': {
                'source_case_id': case.get('case_id'),
                'auto_generated': True,
                'generated_at': datetime.utcnow().isoformat(),
                'source': 'workflow_case',
                'ai_unavailable': True
            }
        }

    async def _create_kb_lesson(
        self,
        content: Dict[str, Any],
        case: Dict[str, Any],
        tenant_id: str
    ) -> Optional[str]:
        """Create lesson in knowledge base"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.knowledge_base_url}/api/lessons",
                    json={
                        'title': content['title'],
                        'learning_objectives': content['learning_objectives'],
                        'content': content['content'],
                        'exercises': content['exercises'],
                        'assessment': content['assessment'],
                        'category': content['category'],
                        'difficulty': content['difficulty'],
                        'duration_minutes': content['duration_minutes'],
                        'tags': content['tags'],
                        'metadata': content['metadata'],
                        'tenant_id': tenant_id
                    },
                    headers={'X-Tenant-ID': tenant_id},
                    timeout=aiohttp.ClientTimeout(total=30)
                ) as response:
                    if response.status in [200, 201]:
                        result = await response.json()
                        return result.get('lesson_id')
                    else:
                        logger.warning(f"KB API returned status {response.status}")
                        return None

        except Exception as e:
            logger.error(f"KB lesson creation failed: {e}")
            return None

    async def batch_create_from_cases(
        self,
        cases: List[Dict[str, Any]],
        tenant_id: str
    ) -> Dict[str, Any]:
        """
        Batch create lessons from multiple cases

        Args:
            cases: List of workflow case dictionaries
            tenant_id: Tenant identifier

        Returns:
            {
                'created': int,
                'failed': int,
                'skipped': int,
                'lesson_ids': List[str],
                'errors': List[str]
            }
        """
        results = {
            'created': 0,
            'failed': 0,
            'skipped': 0,
            'lesson_ids': [],
            'errors': []
        }

        for case in cases:
            try:
                # Skip low-success cases
                if case.get('success_score', 0) < self.min_success_score:
                    results['skipped'] += 1
                    continue

                lesson_id = await self.create_lesson_from_case(case, tenant_id)
                if lesson_id:
                    results['created'] += 1
                    results['lesson_ids'].append(lesson_id)
                else:
                    results['failed'] += 1
                    results['errors'].append(f"Failed to create lesson for {case.get('case_id')}")

            except Exception as e:
                results['failed'] += 1
                results['errors'].append(f"Error processing {case.get('case_id')}: {str(e)}")

        logger.info(
            f"Batch lesson creation complete: {results['created']} created, "
            f"{results['failed']} failed, {results['skipped']} skipped"
        )

        return results

    async def enhance_lesson_with_feedback(
        self,
        lesson_id: str,
        feedback: List[Dict[str, Any]],
        tenant_id: str
    ) -> bool:
        """
        Enhance lesson based on user feedback

        Args:
            lesson_id: Lesson identifier
            feedback: List of feedback entries
            tenant_id: Tenant identifier

        Returns:
            True if successful, False otherwise
        """
        try:
            # Analyze feedback
            positive_count = sum(1 for f in feedback if f.get('rating', 0) >= 4)
            negative_count = sum(1 for f in feedback if f.get('rating', 0) < 3)

            # If mostly positive, no changes needed
            if positive_count > negative_count * 2:
                logger.info(f"Lesson {lesson_id} has mostly positive feedback, no changes needed")
                return True

            # Extract improvement suggestions
            suggestions = [f.get('comment', '') for f in feedback if f.get('comment')]

            # Update lesson (simplified - real implementation would use AI to refine content)
            logger.info(f"Enhancing lesson {lesson_id} based on {len(feedback)} feedback entries")

            return True

        except Exception as e:
            logger.error(f"Lesson enhancement failed: {e}")
            return False
