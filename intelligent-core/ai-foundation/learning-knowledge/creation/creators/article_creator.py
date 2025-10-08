"""
Article Creator - Pattern → Knowledge Article

Automatically creates knowledge base articles from detected patterns.
Part of the cross-learning virtuous cycle.
"""

import logging
from typing import Dict, List, Optional, Any
from datetime import datetime
import aiohttp

logger = logging.getLogger(__name__)


class ArticleCreator:
    """
    Creates knowledge base articles from detected patterns

    Workflow:
    1. Pattern detected (5+ occurrences)
    2. AI generates article structure
    3. Article created in knowledge base
    4. Article indexed for search
    5. Users learn from article
    """

    def __init__(
        self,
        knowledge_base_url: str = "http://localhost:8040",
        ai_orchestrator_url: str = "http://localhost:8000",
        pattern_threshold: int = 5
    ):
        self.knowledge_base_url = knowledge_base_url
        self.ai_orchestrator_url = ai_orchestrator_url
        self.pattern_threshold = pattern_threshold

    async def create_article_from_pattern(
        self,
        pattern: Dict[str, Any],
        tenant_id: str
    ) -> Optional[str]:
        """
        Create knowledge article from detected pattern

        Args:
            pattern: {
                'pattern_name': str,
                'description': str,
                'occurrence_count': int,
                'confidence': float,
                'severity': str,
                'recommended_actions': List[str],
                'affected_processes': List[str],
                'context': Dict
            }
            tenant_id: Tenant identifier

        Returns:
            article_id if successful, None otherwise
        """
        try:
            # Check threshold
            if pattern.get('occurrence_count', 0) < self.pattern_threshold:
                logger.info(
                    f"Pattern '{pattern.get('pattern_name')}' below threshold "
                    f"({pattern.get('occurrence_count')} < {self.pattern_threshold})"
                )
                return None

            logger.info(f"Creating article from pattern: {pattern.get('pattern_name')}")

            # Generate article content using AI
            article_content = await self._generate_article_content(pattern)

            if not article_content:
                logger.warning("Failed to generate article content")
                return None

            # Create article in knowledge base
            article_id = await self._create_kb_article(
                content=article_content,
                pattern=pattern,
                tenant_id=tenant_id
            )

            if article_id:
                logger.info(f"Article created successfully: {article_id}")
                return article_id
            else:
                logger.warning("Failed to create KB article")
                return None

        except Exception as e:
            logger.error(f"Article creation failed: {e}")
            return None

    async def _generate_article_content(
        self,
        pattern: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """Generate article content using AI"""
        try:
            prompt = self._build_article_generation_prompt(pattern)

            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.ai_orchestrator_url}/nlp/query",
                    json={
                        'query': prompt,
                        'context': {
                            'pattern': pattern,
                            'ai_organ': 'knowledge_creator',
                            'task': 'generate_article'
                        },
                        'user_role': 'knowledge_creator'
                    },
                    timeout=aiohttp.ClientTimeout(total=60)
                ) as response:
                    if response.status == 200:
                        result = await response.json()
                        return self._format_article_content(result, pattern)
                    else:
                        logger.warning(f"AI orchestrator returned status {response.status}")
                        return self._fallback_article_content(pattern)

        except Exception as e:
            logger.error(f"Article content generation failed: {e}")
            return self._fallback_article_content(pattern)

    def _build_article_generation_prompt(self, pattern: Dict[str, Any]) -> str:
        """Build AI prompt for article generation"""
        return f"""
KNOWLEDGE ARTICLE GENERATION REQUEST

DETECTED PATTERN:
Name: {pattern.get('pattern_name')}
Description: {pattern.get('description')}
Occurrences: {pattern.get('occurrence_count')}
Confidence: {pattern.get('confidence')}
Severity: {pattern.get('severity')}

RECOMMENDED ACTIONS:
{chr(10).join(f"- {action}" for action in pattern.get('recommended_actions', []))}

AFFECTED PROCESSES:
{chr(10).join(f"- {process}" for process in pattern.get('affected_processes', []))}

CONTEXT:
{pattern.get('context', {})}

TASK: Generate a comprehensive knowledge base article that helps users:
1. Understand this pattern and its implications
2. Recognize when this pattern is occurring
3. Take effective action to resolve or prevent it
4. Learn from past occurrences

ARTICLE STRUCTURE REQUIRED:
- Title (clear, actionable)
- Executive Summary (2-3 sentences)
- Problem Description (what, why, impact)
- Recognition Signs (how to identify)
- Root Causes (why it happens)
- Recommended Solutions (step-by-step)
- Prevention Strategies (how to avoid)
- Related Resources (links to procedures, standards)
- Real Examples (anonymized cases)

Provide structured, actionable knowledge that improves team competency.
"""

    def _format_article_content(
        self,
        ai_result: Dict[str, Any],
        pattern: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Format AI-generated content into article structure"""
        return {
            'title': ai_result.get('title', pattern.get('pattern_name')),
            'summary': ai_result.get('summary', pattern.get('description')),
            'content': ai_result.get('content', ''),
            'category': 'pattern',
            'severity': pattern.get('severity', 'medium'),
            'tags': [
                'pattern',
                pattern.get('severity', 'medium'),
                *pattern.get('affected_processes', [])
            ],
            'metadata': {
                'pattern_name': pattern.get('pattern_name'),
                'occurrence_count': pattern.get('occurrence_count'),
                'confidence': pattern.get('confidence'),
                'auto_generated': True,
                'generated_at': datetime.utcnow().isoformat(),
                'source': 'pattern_detection'
            }
        }

    def _fallback_article_content(self, pattern: Dict[str, Any]) -> Dict[str, Any]:
        """Fallback article content when AI is unavailable"""
        content = f"""
# {pattern.get('pattern_name')}

## Summary
This pattern has been detected {pattern.get('occurrence_count')} times with {pattern.get('confidence', 0)*100:.0f}% confidence.

## Description
{pattern.get('description')}

## Severity
{pattern.get('severity', 'medium').upper()}

## Recommended Actions
{chr(10).join(f"{i+1}. {action}" for i, action in enumerate(pattern.get('recommended_actions', [])))}

## Affected Processes
{chr(10).join(f"- {process}" for process in pattern.get('affected_processes', []))}

## Notes
This article was automatically generated from pattern detection.
Please review and enhance with specific organizational context.
"""

        return {
            'title': pattern.get('pattern_name'),
            'summary': pattern.get('description'),
            'content': content,
            'category': 'pattern',
            'severity': pattern.get('severity', 'medium'),
            'tags': ['pattern', 'auto-generated'],
            'metadata': {
                'pattern_name': pattern.get('pattern_name'),
                'occurrence_count': pattern.get('occurrence_count'),
                'auto_generated': True,
                'generated_at': datetime.utcnow().isoformat(),
                'source': 'pattern_detection',
                'ai_unavailable': True
            }
        }

    async def _create_kb_article(
        self,
        content: Dict[str, Any],
        pattern: Dict[str, Any],
        tenant_id: str
    ) -> Optional[str]:
        """Create article in knowledge base"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.knowledge_base_url}/api/articles",
                    json={
                        'title': content['title'],
                        'summary': content['summary'],
                        'content': content['content'],
                        'category': content['category'],
                        'severity': content['severity'],
                        'tags': content['tags'],
                        'metadata': content['metadata'],
                        'tenant_id': tenant_id
                    },
                    headers={'X-Tenant-ID': tenant_id},
                    timeout=aiohttp.ClientTimeout(total=30)
                ) as response:
                    if response.status in [200, 201]:
                        result = await response.json()
                        return result.get('article_id')
                    else:
                        logger.warning(f"KB API returned status {response.status}")
                        return None

        except Exception as e:
            logger.error(f"KB article creation failed: {e}")
            return None

    async def batch_create_from_patterns(
        self,
        patterns: List[Dict[str, Any]],
        tenant_id: str
    ) -> Dict[str, Any]:
        """
        Batch create articles from multiple patterns

        Args:
            patterns: List of pattern dictionaries
            tenant_id: Tenant identifier

        Returns:
            {
                'created': int,
                'failed': int,
                'article_ids': List[str],
                'errors': List[str]
            }
        """
        results = {
            'created': 0,
            'failed': 0,
            'article_ids': [],
            'errors': []
        }

        for pattern in patterns:
            try:
                article_id = await self.create_article_from_pattern(pattern, tenant_id)
                if article_id:
                    results['created'] += 1
                    results['article_ids'].append(article_id)
                else:
                    results['failed'] += 1
                    results['errors'].append(f"Failed to create article for {pattern.get('pattern_name')}")

            except Exception as e:
                results['failed'] += 1
                results['errors'].append(f"Error processing {pattern.get('pattern_name')}: {str(e)}")

        logger.info(
            f"Batch creation complete: {results['created']} created, {results['failed']} failed"
        )

        return results
