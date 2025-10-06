"""
Entity Resolver

Resolves duplicate entities from different data sources using fuzzy matching
Implements entity resolution logic inspired by digital-twin-platform
"""

import logging
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime
from difflib import SequenceMatcher
import re

from core.models.base import Organization, DataSourceType

logger = logging.getLogger(__name__)


# ============================================
# SIMILARITY METRICS
# ============================================

class SimilarityMetric:
    """Similarity calculation utilities"""

    @staticmethod
    def string_similarity(str1: Optional[str], str2: Optional[str]) -> float:
        """
        Calculate string similarity using SequenceMatcher

        Args:
            str1: First string
            str2: Second string

        Returns:
            Similarity score (0-1)
        """
        if not str1 or not str2:
            return 0.0

        # Normalize strings
        s1 = str1.lower().strip()
        s2 = str2.lower().strip()

        if s1 == s2:
            return 1.0

        # Use SequenceMatcher for fuzzy comparison
        return SequenceMatcher(None, s1, s2).ratio()

    @staticmethod
    def email_similarity(email1: Optional[str], email2: Optional[str]) -> float:
        """
        Calculate email similarity

        Args:
            email1: First email
            email2: Second email

        Returns:
            Similarity score (0-1)
        """
        if not email1 or not email2:
            return 0.0

        # Exact match on email is strong signal
        if email1.lower().strip() == email2.lower().strip():
            return 1.0

        # Check if domains match (weaker signal)
        domain1 = email1.split('@')[-1].lower() if '@' in email1 else ''
        domain2 = email2.split('@')[-1].lower() if '@' in email2 else ''

        if domain1 and domain2 and domain1 == domain2:
            return 0.7

        return 0.0

    @staticmethod
    def phone_similarity(phone1: Optional[str], phone2: Optional[str]) -> float:
        """
        Calculate phone number similarity

        Args:
            phone1: First phone
            phone2: Second phone

        Returns:
            Similarity score (0-1)
        """
        if not phone1 or not phone2:
            return 0.0

        # Normalize phone numbers (remove non-digits)
        p1 = re.sub(r'\D', '', phone1)
        p2 = re.sub(r'\D', '', phone2)

        if not p1 or not p2:
            return 0.0

        # Exact match
        if p1 == p2:
            return 1.0

        # Match last N digits (phone extensions might differ)
        min_len = min(len(p1), len(p2))
        if min_len >= 7:
            # Compare last 7+ digits
            if p1[-7:] == p2[-7:]:
                return 0.9

        return 0.0

    @staticmethod
    def domain_similarity(domain1: Optional[str], domain2: Optional[str]) -> float:
        """
        Calculate domain/website similarity

        Args:
            domain1: First domain
            domain2: Second domain

        Returns:
            Similarity score (0-1)
        """
        if not domain1 or not domain2:
            return 0.0

        # Extract domain from URL
        d1 = re.sub(r'^https?://(www\.)?', '', domain1.lower().strip()).split('/')[0]
        d2 = re.sub(r'^https?://(www\.)?', '', domain2.lower().strip()).split('/')[0]

        if d1 == d2:
            return 1.0

        # Check if one is subdomain of another
        if d1 in d2 or d2 in d1:
            return 0.8

        return SimilarityMetric.string_similarity(d1, d2)


# ============================================
# ENTITY RESOLVER
# ============================================

class EntityResolver:
    """
    Entity Resolver

    Resolves duplicate entities from different sources using fuzzy matching
    and confidence scoring
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize entity resolver

        Args:
            config: Configuration options
        """
        self.config = config or {}

        # Similarity thresholds
        self.threshold_high = self.config.get('threshold_high', 0.9)  # Auto-merge
        self.threshold_medium = self.config.get('threshold_medium', 0.7)  # Review
        self.threshold_low = self.config.get('threshold_low', 0.5)  # Ignore

        # Field weights for similarity calculation
        self.field_weights = {
            'name': 0.3,
            'email': 0.25,
            'phone': 0.15,
            'website': 0.15,
            'address': 0.1,
            'vat': 0.05,
        }

        logger.info("Entity Resolver initialized")

    async def resolve_entities(
        self,
        entities: List[Dict[str, Any]],
        entity_type: str = 'organization'
    ) -> Dict[str, Any]:
        """
        Resolve duplicate entities

        Args:
            entities: List of entities from different sources
            entity_type: Type of entities

        Returns:
            Resolution result with merged entities
        """
        logger.info(f"Resolving {len(entities)} {entity_type} entities")

        if len(entities) < 2:
            return {
                'merged_entities': entities,
                'groups': [],
                'statistics': {
                    'input_count': len(entities),
                    'output_count': len(entities),
                    'duplicates_found': 0
                }
            }

        try:
            # Group similar entities
            groups = await self._group_by_similarity(entities, entity_type)

            # Merge entities in each group
            merged_entities = []
            for group in groups:
                merged = await self._merge_entities(group['entities'], entity_type)
                merged_entities.append(merged)

            logger.info(
                f"Resolution complete: {len(entities)} → {len(merged_entities)} entities "
                f"({len(groups)} groups)"
            )

            return {
                'merged_entities': merged_entities,
                'groups': groups,
                'statistics': {
                    'input_count': len(entities),
                    'output_count': len(merged_entities),
                    'duplicates_found': len(entities) - len(merged_entities),
                    'groups_count': len(groups)
                }
            }

        except Exception as e:
            logger.error(f"Entity resolution failed: {e}", exc_info=True)
            raise

    async def _group_by_similarity(
        self,
        entities: List[Dict[str, Any]],
        entity_type: str
    ) -> List[Dict[str, Any]]:
        """
        Group similar entities using clustering

        Args:
            entities: List of entities
            entity_type: Entity type

        Returns:
            List of entity groups
        """
        groups = []
        assigned = set()

        for i, entity1 in enumerate(entities):
            if i in assigned:
                continue

            # Start new group with this entity
            group_entities = [entity1]
            group_indices = {i}

            # Find similar entities
            for j, entity2 in enumerate(entities):
                if j <= i or j in assigned:
                    continue

                similarity = await self._calculate_similarity(
                    entity1,
                    entity2,
                    entity_type
                )

                # Add to group if similar enough
                if similarity['score'] >= self.threshold_medium:
                    group_entities.append(entity2)
                    group_indices.add(j)

            # Mark as assigned
            assigned.update(group_indices)

            # Create group
            canonical_id = self._generate_canonical_id(group_entities)

            groups.append({
                'canonical_id': canonical_id,
                'entities': group_entities,
                'size': len(group_entities),
                'sources': list(set(e.get('source', 'unknown') for e in group_entities))
            })

        logger.info(f"Grouped {len(entities)} entities into {len(groups)} groups")

        return groups

    async def _calculate_similarity(
        self,
        entity1: Dict[str, Any],
        entity2: Dict[str, Any],
        entity_type: str
    ) -> Dict[str, Any]:
        """
        Calculate similarity between two entities

        Args:
            entity1: First entity
            entity2: Second entity
            entity_type: Entity type

        Returns:
            Similarity result with score and breakdown
        """
        scores = {}
        total_score = 0.0
        total_weight = 0.0

        # Calculate field similarities
        if entity_type == 'organization':
            # Name similarity
            if 'name' in entity1 and 'name' in entity2:
                name_sim = SimilarityMetric.string_similarity(
                    entity1.get('name'),
                    entity2.get('name')
                )
                scores['name'] = name_sim
                total_score += name_sim * self.field_weights['name']
                total_weight += self.field_weights['name']

            # Email similarity
            if 'email' in entity1 and 'email' in entity2:
                email_sim = SimilarityMetric.email_similarity(
                    entity1.get('email'),
                    entity2.get('email')
                )
                scores['email'] = email_sim
                total_score += email_sim * self.field_weights['email']
                total_weight += self.field_weights['email']

            # Phone similarity
            if 'phone' in entity1 and 'phone' in entity2:
                phone_sim = SimilarityMetric.phone_similarity(
                    entity1.get('phone'),
                    entity2.get('phone')
                )
                scores['phone'] = phone_sim
                total_score += phone_sim * self.field_weights['phone']
                total_weight += self.field_weights['phone']

            # Website similarity
            if 'website' in entity1 and 'website' in entity2:
                website_sim = SimilarityMetric.domain_similarity(
                    entity1.get('website'),
                    entity2.get('website')
                )
                scores['website'] = website_sim
                total_score += website_sim * self.field_weights['website']
                total_weight += self.field_weights['website']

        # Calculate weighted average
        final_score = total_score / total_weight if total_weight > 0 else 0.0

        return {
            'score': final_score,
            'breakdown': scores,
            'confidence': self._assess_confidence(final_score, scores)
        }

    async def _merge_entities(
        self,
        entities: List[Dict[str, Any]],
        entity_type: str
    ) -> Dict[str, Any]:
        """
        Merge multiple entities into one

        Args:
            entities: List of entities to merge
            entity_type: Entity type

        Returns:
            Merged entity
        """
        if len(entities) == 1:
            return entities[0]

        logger.info(f"Merging {len(entities)} entities")

        # Start with empty merged entity
        merged = {
            '_metadata': {
                'merged_from': len(entities),
                'sources': [],
                'source_ids': {},
                'merged_at': datetime.utcnow().isoformat()
            }
        }

        # Collect all sources
        for entity in entities:
            source = entity.get('source', 'unknown')
            source_id = entity.get('source_id', entity.get('id'))

            if source not in merged['_metadata']['sources']:
                merged['_metadata']['sources'].append(source)

            if source_id:
                merged['_metadata']['source_ids'][source] = source_id

        # Merge fields using best value selection
        all_fields = set()
        for entity in entities:
            all_fields.update(entity.keys())

        for field in all_fields:
            if field.startswith('_'):
                continue  # Skip metadata fields

            # Get all non-null values for this field
            values = [
                (entity.get(field), entity.get('_metadata', {}).get('quality', 'unknown'))
                for entity in entities
                if field in entity and entity[field] is not None
            ]

            if not values:
                continue

            # Select best value
            merged[field] = self._select_best_value(field, values, entity_type)

        return merged

    def _select_best_value(
        self,
        field: str,
        values: List[Tuple[Any, str]],
        entity_type: str
    ) -> Any:
        """
        Select best value from multiple sources

        Args:
            field: Field name
            values: List of (value, quality) tuples
            entity_type: Entity type

        Returns:
            Best value
        """
        if len(values) == 1:
            return values[0][0]

        # Quality ranking
        quality_rank = {
            'excellent': 5,
            'good': 4,
            'acceptable': 3,
            'poor': 2,
            'incomplete': 1,
            'unknown': 0
        }

        # Sort by quality
        sorted_values = sorted(
            values,
            key=lambda x: quality_rank.get(x[1], 0),
            reverse=True
        )

        # For string fields, prefer longer/more complete values
        if field in ['name', 'address', 'description']:
            # Among same quality, prefer longer
            best_quality = sorted_values[0][1]
            same_quality = [v for v in sorted_values if v[1] == best_quality]

            if len(same_quality) > 1:
                return max(same_quality, key=lambda x: len(str(x[0])))[0]

        # For numeric fields, prefer larger values (except for year founded)
        if field in ['employee_count', 'annual_revenue']:
            try:
                numeric_values = [(float(v), q) for v, q in sorted_values if v is not None]
                if numeric_values:
                    return max(numeric_values, key=lambda x: x[0])[0]
            except (ValueError, TypeError):
                pass

        # Default: return highest quality value
        return sorted_values[0][0]

    def _generate_canonical_id(self, entities: List[Dict[str, Any]]) -> str:
        """
        Generate canonical ID for entity group

        Args:
            entities: List of entities

        Returns:
            Canonical ID
        """
        # Use first entity's ID as base
        base_id = entities[0].get('id', entities[0].get('source_id', 'unknown'))

        # Add hash of all source IDs for uniqueness
        source_ids = '_'.join(
            sorted(str(e.get('source_id', e.get('id', ''))) for e in entities)
        )

        import hashlib
        id_hash = hashlib.md5(source_ids.encode()).hexdigest()[:8]

        return f"merged_{base_id}_{id_hash}"

    def _assess_confidence(
        self,
        score: float,
        breakdown: Dict[str, float]
    ) -> str:
        """
        Assess confidence level of match

        Args:
            score: Overall similarity score
            breakdown: Field-level scores

        Returns:
            Confidence level (high/medium/low)
        """
        # Check for strong signals (exact matches)
        has_exact_match = any(v >= 0.99 for v in breakdown.values())

        if score >= self.threshold_high:
            return 'high'
        elif score >= self.threshold_medium:
            return 'medium' if has_exact_match else 'low'
        else:
            return 'low'

    async def find_duplicates(
        self,
        entity: Dict[str, Any],
        candidates: List[Dict[str, Any]],
        entity_type: str = 'organization'
    ) -> List[Dict[str, Any]]:
        """
        Find potential duplicates for an entity

        Args:
            entity: Entity to check
            candidates: List of candidate entities
            entity_type: Entity type

        Returns:
            List of potential duplicates with similarity scores
        """
        duplicates = []

        for candidate in candidates:
            similarity = await self._calculate_similarity(entity, candidate, entity_type)

            if similarity['score'] >= self.threshold_low:
                duplicates.append({
                    'entity': candidate,
                    'similarity': similarity['score'],
                    'confidence': similarity['confidence'],
                    'breakdown': similarity['breakdown']
                })

        # Sort by similarity
        duplicates.sort(key=lambda x: x['similarity'], reverse=True)

        return duplicates

    def get_statistics(self) -> Dict[str, Any]:
        """
        Get resolver statistics

        Returns:
            Statistics dictionary
        """
        return {
            'thresholds': {
                'high': self.threshold_high,
                'medium': self.threshold_medium,
                'low': self.threshold_low
            },
            'field_weights': self.field_weights
        }
