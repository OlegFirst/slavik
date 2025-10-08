"""
Knowledge Base Connector - Integrated Version

Uses shared platform components:
- RAGConnector for semantic search
- KnowledgeClient for structured KB operations

Extends with Learning System specific logic
"""

import logging
import sys
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime
import asyncio

# Add shared to path
shared_path = Path(__file__).parent.parent.parent.parent / "shared"
sys.path.insert(0, str(shared_path))

from integrations.rag_connector import RAGConnector, RAGQueryBuilder
from integrations.knowledge_client import KnowledgeClient, KnowledgeType, KnowledgeArticleBuilder

logger = logging.getLogger(__name__)


class IntegratedKnowledgeConnector:
    """
    Learning System's knowledge connector using shared platform services

    Combines:
    - RAG for semantic search
    - KB for structured operations
    - Learning-specific logic
    """

    def __init__(
        self,
        rag_service_url: str = "http://localhost:8050",
        kb_service_url: str = "http://localhost:8040"
    ):
        self.rag = RAGConnector(rag_service_url)
        self.kb = KnowledgeClient(kb_service_url)

    async def search_resources_for_gap(
        self,
        gap_keyword: str,
        user_id: Optional[str] = None,
        competency_level: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Search learning resources for competency gap

        Uses RAG semantic search with Learning System context

        Args:
            gap_keyword: Competency gap (e.g., "escalation", "communication")
            user_id: User ID for personalization
            competency_level: Current level (beginner, intermediate, advanced)

        Returns:
            List of relevant learning resources
        """
        # Build RAG query with context
        query_builder = RAGQueryBuilder()
        query_builder.with_query(f"learning resources for {gap_keyword}")

        # Add context for better results
        context = {
            'domain': 'BCM',
            'purpose': 'learning',
            'gap': gap_keyword
        }
        if user_id:
            context['user_id'] = user_id
        if competency_level:
            context['level'] = competency_level

        query_builder.with_context(**context)

        # Filter for learning materials
        query_builder.filter_by_type(
            'training_material',
            'procedure',
            'guideline',
            'best_practice'
        )

        # Execute search
        results = await self.rag.search_knowledge(
            query=query_builder.query,
            context=query_builder.context,
            filters=query_builder.filters,
            limit=10
        )

        logger.info(f"Found {len(results)} resources for gap '{gap_keyword}'")
        return results

    async def create_learning_path_from_resources(
        self,
        user_id: str,
        competency_gap: str,
        resources: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Create learning path from KB resources

        Args:
            user_id: User ID
            competency_gap: Gap to address
            resources: Resources from search

        Returns:
            Learning path structure
        """
        if not resources:
            logger.warning(f"No resources for gap '{competency_gap}'")
            return {
                'gap': competency_gap,
                'resources': [],
                'path': []
            }

        # Sort by relevance and difficulty
        sorted_resources = sorted(
            resources,
            key=lambda r: (
                r.get('score', 0),
                self._get_difficulty_order(r.get('metadata', {}).get('difficulty', 'intermediate'))
            ),
            reverse=True
        )

        # Create learning path structure
        learning_path = {
            'user_id': user_id,
            'gap': competency_gap,
            'total_resources': len(sorted_resources),
            'estimated_hours': sum(r.get('metadata', {}).get('duration_hours', 1) for r in sorted_resources),
            'path': []
        }

        # Structure into phases
        for idx, resource in enumerate(sorted_resources[:6]):  # Max 6 resources
            phase = {
                'order': idx + 1,
                'resource_id': resource.get('id'),
                'title': resource.get('metadata', {}).get('title', 'Resource'),
                'type': resource.get('metadata', {}).get('type', 'article'),
                'difficulty': resource.get('metadata', {}).get('difficulty', 'intermediate'),
                'duration_hours': resource.get('metadata', {}).get('duration_hours', 1),
                'relevance_score': resource.get('score', 0.5)
            }
            learning_path['path'].append(phase)

        logger.info(f"Created learning path with {len(learning_path['path'])} resources")
        return learning_path

    async def auto_create_knowledge_from_pattern(
        self,
        pattern: Dict[str, Any],
        threshold_occurrences: int = 5
    ) -> Optional[str]:
        """
        Auto-create knowledge article from detected pattern

        Args:
            pattern: Detected pattern data
            threshold_occurrences: Min occurrences to create article

        Returns:
            Article ID if created
        """
        occurrences = pattern.get('occurrence_count', 0)

        if occurrences < threshold_occurrences:
            logger.debug(f"Pattern occurrences ({occurrences}) below threshold ({threshold_occurrences})")
            return None

        # Check if article already exists
        pattern_name = pattern.get('pattern_name', '')
        existing = await self.kb.search(
            query=pattern_name,
            filters={'type': 'pattern'},
            limit=1
        )

        if existing:
            logger.info(f"Article for pattern '{pattern_name}' already exists")
            return existing[0].get('id')

        # Build article
        article_builder = KnowledgeArticleBuilder()
        article_builder.with_title(f"Pattern: {pattern_name}")

        # Generate content
        content = self._generate_pattern_article_content(pattern)
        article_builder.with_content(content)

        # Metadata
        article_builder.with_category('patterns')
        article_builder.with_type(KnowledgeType.PATTERN)
        article_builder.add_tag(
            'auto_generated',
            pattern.get('pattern_type', 'unknown'),
            pattern.get('pattern_category', 'unknown')
        )
        article_builder.with_severity(pattern.get('severity', 'medium'))
        article_builder.add_metadata('occurrence_count', occurrences)
        article_builder.add_metadata('confidence', pattern.get('confidence', 0))

        # Create article
        article_data = article_builder.build()
        article_id = await self.kb.create_article(**article_data)

        if article_id:
            logger.info(f"Auto-created knowledge article: {article_id}")
            # Also add to RAG for semantic search
            await self.rag.add_knowledge(
                content=content,
                metadata={
                    'kb_article_id': article_id,
                    **article_data
                },
                knowledge_type='pattern'
            )

        return article_id

    async def sync_external_knowledge(
        self,
        source: str,
        knowledge_items: List[Dict[str, Any]]
    ) -> int:
        """
        Sync external knowledge (ISO standards, threats, etc.)

        Args:
            source: Source name (iso_standards, threat_feeds, etc.)
            knowledge_items: Items to sync

        Returns:
            Count of synced items
        """
        synced_count = 0

        for item in knowledge_items:
            try:
                # Check if already exists
                existing = await self.kb.search(
                    query=item.get('title', ''),
                    filters={'source': source},
                    limit=1
                )

                if existing:
                    # Update existing
                    await self.kb.update_article(
                        article_id=existing[0]['id'],
                        updates={
                            'content': item.get('content', ''),
                            'updated_at': datetime.utcnow().isoformat()
                        }
                    )
                else:
                    # Create new
                    await self.kb.create_article(
                        title=item.get('title', ''),
                        content=item.get('content', ''),
                        category=item.get('category', 'external'),
                        tags=item.get('tags', []) + [source],
                        metadata={
                            'source': source,
                            **item.get('metadata', {})
                        }
                    )

                synced_count += 1

            except Exception as e:
                logger.error(f"Error syncing item: {e}")

        logger.info(f"Synced {synced_count}/{len(knowledge_items)} items from {source}")
        return synced_count

    def _generate_pattern_article_content(self, pattern: Dict[str, Any]) -> str:
        """Generate markdown content for pattern article"""
        content = f"""# {pattern.get('pattern_name', 'Pattern')}

## Overview

{pattern.get('description', 'No description available.')}

## Statistics

- **Occurrences**: {pattern.get('occurrence_count', 0)}
- **Confidence**: {pattern.get('confidence', 0)*100:.1f}%
- **Severity**: {pattern.get('severity', 'unknown')}
- **Pattern Type**: {pattern.get('pattern_type', 'unknown')}

## Affected Areas

{self._format_affected_areas(pattern.get('affected_areas', []))}

## Recommended Actions

{self._format_recommended_actions(pattern.get('recommended_actions', []))}

## Evidence

{self._format_evidence(pattern.get('evidence_data', {}))}

---
*Auto-generated from pattern detection on {datetime.utcnow().strftime('%Y-%m-%d')}*
"""
        return content

    def _format_affected_areas(self, areas: List[str]) -> str:
        """Format affected areas as markdown list"""
        if not areas:
            return "*No specific areas identified*"
        return "\n".join(f"- {area}" for area in areas)

    def _format_recommended_actions(self, actions: List[str]) -> str:
        """Format actions as markdown list"""
        if not actions:
            return "*No recommended actions*"
        return "\n".join(f"1. {action}" for action in actions)

    def _format_evidence(self, evidence: Dict[str, Any]) -> str:
        """Format evidence as markdown"""
        if not evidence:
            return "*No evidence data*"

        lines = []
        for key, value in evidence.items():
            lines.append(f"- **{key}**: {value}")
        return "\n".join(lines)

    def _get_difficulty_order(self, difficulty: str) -> int:
        """Get difficulty order for sorting"""
        order = {
            'beginner': 1,
            'intermediate': 2,
            'advanced': 3,
            'expert': 4
        }
        return order.get(difficulty.lower(), 2)

    async def close(self):
        """Close connections"""
        await self.rag.close()
        await self.kb.close()


class ExternalKnowledgeSyncManager:
    """
    Manages syncing external knowledge sources

    Sources:
    - ISO standards updates
    - Threat intelligence feeds
    - Industry best practices
    """

    def __init__(self, connector: IntegratedKnowledgeConnector):
        self.connector = connector

    async def sync_iso_standards(self) -> int:
        """
        Sync ISO 22301 and related standards

        In production, would fetch from ISO API or standards database
        """
        logger.info("Syncing ISO standards...")

        # Mock ISO updates - in production, fetch from API
        iso_updates = [
            {
                'title': 'ISO 22301:2019 - Business Continuity Management Systems',
                'content': '## Requirements\n\nOrganization shall establish, implement...',
                'category': 'standards',
                'tags': ['iso22301', 'bcm', 'requirements'],
                'metadata': {
                    'standard_id': 'ISO22301:2019',
                    'last_updated': '2019-10-31'
                }
            }
        ]

        return await self.connector.sync_external_knowledge('iso_standards', iso_updates)

    async def sync_threat_intelligence(self) -> int:
        """
        Sync latest threat intelligence

        In production, would fetch from threat feeds (MISP, STIX/TAXII, etc.)
        """
        logger.info("Syncing threat intelligence...")

        # Mock threat updates - in production, fetch from threat feeds
        threat_updates = [
            {
                'title': 'Emerging Ransomware Threat - BlackCat Variant',
                'content': '## Threat Overview\n\nNew ransomware variant...',
                'category': 'threats',
                'tags': ['ransomware', 'cyber', 'critical'],
                'metadata': {
                    'threat_level': 'high',
                    'first_seen': '2025-01-15'
                }
            }
        ]

        return await self.connector.sync_external_knowledge('threat_feeds', threat_updates)

    async def sync_all(self) -> Dict[str, int]:
        """Sync all external sources"""
        results = {}

        results['iso_standards'] = await self.sync_iso_standards()
        results['threat_intelligence'] = await self.sync_threat_intelligence()

        logger.info(f"External sync complete: {results}")
        return results
