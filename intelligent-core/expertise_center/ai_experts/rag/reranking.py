"""
Reranking Module

Re-ranks retrieval results based on additional criteria:
- Recency
- Source priority
- Relevance refinement
"""

from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)


class Reranker:
    """
    Result Reranker

    Re-ranks search results using multiple signals:
    - Base retrieval score
    - Recency boost
    - Source priority
    - Context relevance
    """

    def __init__(
        self,
        recency_weight: float = 0.2,
        source_weight: float = 0.15,
        base_weight: float = 0.65
    ):
        """
        Initialize reranker

        Args:
            recency_weight: Weight for recency score
            source_weight: Weight for source priority
            base_weight: Weight for base retrieval score
        """
        self.recency_weight = recency_weight
        self.source_weight = source_weight
        self.base_weight = base_weight

        # Normalize weights
        total = recency_weight + source_weight + base_weight
        self.recency_weight = recency_weight / total
        self.source_weight = source_weight / total
        self.base_weight = base_weight / total

        # Source priority mapping
        self.source_priorities = {
            'iso_standard': 1.0,      # Official ISO standards
            'bci_guidelines': 0.95,   # BCI Good Practice Guidelines
            'case_study': 0.8,        # Real case studies
            'community': 0.7,         # Community annotations
            'documentation': 0.6,     # General documentation
            'forum': 0.5              # Forum discussions
        }

    def rerank(
        self,
        results: List[Dict[str, Any]],
        context: Optional[Dict[str, Any]] = None,
        top_k: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        Rerank search results

        Args:
            results: Search results with scores
            context: Additional context for relevance
            top_k: Number of results to return (None = all)

        Returns:
            Reranked results
        """

        if not results:
            return []

        reranked = []

        for result in results:
            # Base retrieval score
            base_score = result.get('score', 0.0)

            # Recency score
            recency_score = self._calculate_recency_score(result)

            # Source priority score
            source_score = self._calculate_source_score(result)

            # Context relevance score (if context provided)
            context_boost = 0.0
            if context:
                context_boost = self._calculate_context_boost(result, context)

            # Combined rerank score
            rerank_score = (
                self.base_weight * base_score +
                self.recency_weight * recency_score +
                self.source_weight * source_score +
                context_boost
            )

            reranked_result = result.copy()
            reranked_result['rerank_score'] = rerank_score
            reranked_result['original_score'] = base_score
            reranked_result['recency_score'] = recency_score
            reranked_result['source_score'] = source_score

            reranked.append(reranked_result)

        # Sort by rerank score
        reranked.sort(key=lambda x: x['rerank_score'], reverse=True)

        # Return top-k if specified
        if top_k:
            return reranked[:top_k]

        return reranked

    def _calculate_recency_score(self, result: Dict[str, Any]) -> float:
        """
        Calculate recency score

        Args:
            result: Search result with optional date

        Returns:
            Recency score (0-1)
        """

        # Check for date field
        date_str = result.get('date') or result.get('created_at') or result.get('updated_at')

        if not date_str:
            # No date = assume medium recency
            return 0.5

        try:
            # Parse date
            if isinstance(date_str, str):
                doc_date = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
            elif isinstance(date_str, datetime):
                doc_date = date_str
            else:
                return 0.5

            # Calculate age
            age_days = (datetime.now(doc_date.tzinfo) - doc_date).days

            # Recency scoring:
            # - Last 30 days: 1.0
            # - Last 90 days: 0.8
            # - Last 180 days: 0.6
            # - Last year: 0.4
            # - Older: 0.2

            if age_days <= 30:
                return 1.0
            elif age_days <= 90:
                return 0.8
            elif age_days <= 180:
                return 0.6
            elif age_days <= 365:
                return 0.4
            else:
                return 0.2

        except Exception as e:
            logger.warning(f"Failed to parse date: {e}")
            return 0.5

    def _calculate_source_score(self, result: Dict[str, Any]) -> float:
        """
        Calculate source priority score

        Args:
            result: Search result with optional source

        Returns:
            Source priority score (0-1)
        """

        source = result.get('source') or result.get('source_type')

        if not source:
            return 0.5  # Default if no source specified

        # Normalize source
        source_lower = source.lower()

        # Check priority mapping
        for key, score in self.source_priorities.items():
            if key in source_lower:
                return score

        # Unknown source = medium priority
        return 0.5

    def _calculate_context_boost(
        self,
        result: Dict[str, Any],
        context: Dict[str, Any]
    ) -> float:
        """
        Calculate context relevance boost

        Args:
            result: Search result
            context: Query context

        Returns:
            Context boost (0-0.2)
        """

        boost = 0.0

        # Industry match
        result_industry = result.get('industry')
        context_industry = context.get('industry')

        if result_industry and context_industry:
            if result_industry.lower() == context_industry.lower():
                boost += 0.05

        # Organization size match
        result_size = result.get('org_size')
        context_size = context.get('size') or context.get('org_size')

        if result_size and context_size:
            if result_size.lower() == context_size.lower():
                boost += 0.05

        # Module match
        result_module = result.get('module')
        context_module = context.get('module') or context.get('current_module')

        if result_module and context_module:
            if result_module.lower() == context_module.lower():
                boost += 0.05

        # Stage match
        result_stage = result.get('stage')
        context_stage = context.get('current_stage') or context.get('stage')

        if result_stage and context_stage:
            if result_stage.lower() in context_stage.lower():
                boost += 0.05

        return boost


class DiversityReranker:
    """
    Diversity-aware reranker

    Ensures diversity in results (avoid redundant information).
    """

    def __init__(self, diversity_threshold: float = 0.85):
        """
        Initialize diversity reranker

        Args:
            diversity_threshold: Similarity threshold for diversity (0-1)
        """
        self.diversity_threshold = diversity_threshold

    def rerank_with_diversity(
        self,
        results: List[Dict[str, Any]],
        top_k: int = 5,
        embedding_generator=None
    ) -> List[Dict[str, Any]]:
        """
        Rerank with diversity

        Args:
            results: Search results
            top_k: Number of results to return
            embedding_generator: Embedding generator for similarity calculation

        Returns:
            Diverse top-k results
        """

        if not results or len(results) <= top_k:
            return results

        # Start with highest-scored result
        diverse_results = [results[0]]

        # Add diverse results
        for result in results[1:]:
            if len(diverse_results) >= top_k:
                break

            # Check diversity against selected results
            is_diverse = True

            if embedding_generator and 'embedding' in result:
                for selected in diverse_results:
                    if 'embedding' not in selected:
                        continue

                    similarity = embedding_generator.cosine_similarity(
                        result['embedding'],
                        selected['embedding']
                    )

                    if similarity > self.diversity_threshold:
                        # Too similar, skip
                        is_diverse = False
                        break

            # Use text similarity if embeddings not available
            else:
                is_diverse = self._check_text_diversity(
                    result.get('text', ''),
                    [r.get('text', '') for r in diverse_results]
                )

            if is_diverse:
                diverse_results.append(result)

        return diverse_results

    def _check_text_diversity(
        self,
        text: str,
        selected_texts: List[str]
    ) -> bool:
        """
        Check text diversity (simple keyword overlap)

        Args:
            text: New result text
            selected_texts: Already selected result texts

        Returns:
            True if diverse enough
        """

        text_words = set(text.lower().split())

        for selected_text in selected_texts:
            selected_words = set(selected_text.lower().split())

            if not text_words or not selected_words:
                continue

            # Calculate Jaccard similarity
            intersection = len(text_words & selected_words)
            union = len(text_words | selected_words)

            similarity = intersection / union if union > 0 else 0

            if similarity > self.diversity_threshold:
                return False

        return True
