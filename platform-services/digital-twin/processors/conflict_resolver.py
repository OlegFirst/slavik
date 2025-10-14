"""
Conflict Resolver

Resolves data conflicts from multiple sources using trust scores and strategies
"""

import logging
from typing import Dict, List, Optional, Any, Callable
from datetime import datetime
from enum import Enum

from core.models.base import DataSourceType, ConflictValue

logger = logging.getLogger(__name__)


# ============================================
# RESOLUTION STRATEGIES
# ============================================

class ResolutionStrategy(str, Enum):
    """Conflict resolution strategies"""
    MOST_RECENT = "most_recent"  # Use most recent value
    HIGHEST_QUALITY = "highest_quality"  # Use highest quality source
    MOST_COMPLETE = "most_complete"  # Use most complete value
    CONSENSUS = "consensus"  # Use value that appears most often
    TRUSTED_SOURCE = "trusted_source"  # Use value from most trusted source
    MANUAL = "manual"  # Require manual resolution


class ConflictType(str, Enum):
    """Types of conflicts"""
    VALUE_MISMATCH = "value_mismatch"  # Different values for same field
    TYPE_MISMATCH = "type_mismatch"  # Different data types
    MISSING_VALUE = "missing_value"  # Value missing in some sources
    OUTDATED_VALUE = "outdated_value"  # Value outdated in some sources


# ============================================
# CONFLICT RESOLVER
# ============================================

class ConflictResolver:
    """
    Conflict Resolver

    Resolves data conflicts from multiple sources using configurable strategies
    and trust scoring
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize conflict resolver

        Args:
            config: Configuration options
        """
        self.config = config or {}

        # Default resolution strategies by field type
        self.default_strategies = {
            'id': ResolutionStrategy.TRUSTED_SOURCE,
            'name': ResolutionStrategy.MOST_COMPLETE,
            'email': ResolutionStrategy.HIGHEST_QUALITY,
            'phone': ResolutionStrategy.MOST_RECENT,
            'address': ResolutionStrategy.MOST_COMPLETE,
            'created_at': ResolutionStrategy.MOST_RECENT,
            'updated_at': ResolutionStrategy.MOST_RECENT,
        }

        # Source trust scores (0-1)
        self.source_trust_scores = self.config.get('trust_scores', {
            DataSourceType.ODOO.value: 0.9,
            DataSourceType.SALESFORCE.value: 0.85,
            DataSourceType.HUBSPOT.value: 0.8,
            DataSourceType.CUSTOM.value: 0.5,
        })

        # Custom resolvers for specific fields
        self.custom_resolvers: Dict[str, Callable] = {}

        # Statistics
        self.stats = {
            'conflicts_resolved': 0,
            'manual_required': 0,
            'by_strategy': {}
        }

        logger.info("Conflict Resolver initialized")

    async def resolve_conflicts(
        self,
        field_name: str,
        values: List[ConflictValue],
        strategy: Optional[ResolutionStrategy] = None
    ) -> Dict[str, Any]:
        """
        Resolve conflicts for a field

        Args:
            field_name: Field name
            values: List of conflicting values
            strategy: Resolution strategy (optional)

        Returns:
            Resolution result
        """
        if len(values) == 0:
            return {
                'resolved_value': None,
                'strategy': None,
                'confidence': 0.0,
                'conflict_type': None
            }

        if len(values) == 1:
            return {
                'resolved_value': values[0].value,
                'strategy': 'no_conflict',
                'confidence': 1.0,
                'source': values[0].source.value,
                'conflict_type': None
            }

        logger.info(f"Resolving conflict for field '{field_name}' with {len(values)} values")

        try:
            # Detect conflict type
            conflict_type = self._detect_conflict_type(values)

            # Determine strategy
            if not strategy:
                strategy = self._select_strategy(field_name, conflict_type, values)

            # Check for custom resolver
            if field_name in self.custom_resolvers:
                resolved = await self._apply_custom_resolver(field_name, values)
            else:
                # Apply strategy
                resolved = await self._apply_strategy(strategy, values, field_name)

            self.stats['conflicts_resolved'] += 1
            self.stats['by_strategy'][strategy.value] = \
                self.stats['by_strategy'].get(strategy.value, 0) + 1

            logger.info(
                f"Resolved conflict for '{field_name}': "
                f"strategy={strategy.value}, confidence={resolved['confidence']:.2f}"
            )

            return {
                **resolved,
                'strategy': strategy.value,
                'conflict_type': conflict_type.value,
                'alternatives': [
                    {
                        'value': v.value,
                        'source': v.source.value,
                        'timestamp': v.timestamp.isoformat(),
                        'quality_score': v.quality_score
                    }
                    for v in values
                ]
            }

        except Exception as e:
            logger.error(f"Conflict resolution failed for '{field_name}': {e}", exc_info=True)
            raise

    async def resolve_all_conflicts(
        self,
        conflicts: Dict[str, List[ConflictValue]]
    ) -> Dict[str, Any]:
        """
        Resolve all conflicts in a dataset

        Args:
            conflicts: Dictionary of field_name -> conflicting values

        Returns:
            Resolved data and metadata
        """
        logger.info(f"Resolving {len(conflicts)} conflicting fields")

        resolved_data = {}
        resolution_metadata = {}

        for field_name, values in conflicts.items():
            result = await self.resolve_conflicts(field_name, values)

            resolved_data[field_name] = result['resolved_value']
            resolution_metadata[field_name] = {
                'strategy': result['strategy'],
                'confidence': result['confidence'],
                'conflict_type': result.get('conflict_type'),
                'alternatives_count': len(values)
            }

        return {
            'data': resolved_data,
            'metadata': resolution_metadata,
            'statistics': {
                'total_fields': len(conflicts),
                'resolved': len([m for m in resolution_metadata.values() if m['strategy'] != 'manual']),
                'manual_required': len([m for m in resolution_metadata.values() if m['strategy'] == 'manual'])
            }
        }

    def _detect_conflict_type(self, values: List[ConflictValue]) -> ConflictType:
        """
        Detect type of conflict

        Args:
            values: Conflicting values

        Returns:
            Conflict type
        """
        # Check for None/missing values
        none_count = sum(1 for v in values if v.value is None)
        if none_count > 0:
            return ConflictType.MISSING_VALUE

        # Check for type mismatches
        types = set(type(v.value) for v in values)
        if len(types) > 1:
            return ConflictType.TYPE_MISMATCH

        # Check for outdated values (based on timestamps)
        now = datetime.utcnow()
        old_values = [v for v in values if (now - v.timestamp).days > 90]
        if len(old_values) > 0 and len(old_values) < len(values):
            return ConflictType.OUTDATED_VALUE

        # Default: value mismatch
        return ConflictType.VALUE_MISMATCH

    def _select_strategy(
        self,
        field_name: str,
        conflict_type: ConflictType,
        values: List[ConflictValue]
    ) -> ResolutionStrategy:
        """
        Select appropriate resolution strategy

        Args:
            field_name: Field name
            conflict_type: Conflict type
            values: Conflicting values

        Returns:
            Resolution strategy
        """
        # Use default strategy for known fields
        if field_name in self.default_strategies:
            return self.default_strategies[field_name]

        # Strategy based on conflict type
        if conflict_type == ConflictType.MISSING_VALUE:
            return ResolutionStrategy.HIGHEST_QUALITY

        if conflict_type == ConflictType.TYPE_MISMATCH:
            return ResolutionStrategy.TRUSTED_SOURCE

        if conflict_type == ConflictType.OUTDATED_VALUE:
            return ResolutionStrategy.MOST_RECENT

        # Check if consensus exists
        value_counts = {}
        for v in values:
            val_str = str(v.value)
            value_counts[val_str] = value_counts.get(val_str, 0) + 1

        if max(value_counts.values()) >= len(values) * 0.6:  # 60% consensus
            return ResolutionStrategy.CONSENSUS

        # Default: use trusted source
        return ResolutionStrategy.TRUSTED_SOURCE

    async def _apply_strategy(
        self,
        strategy: ResolutionStrategy,
        values: List[ConflictValue],
        field_name: str
    ) -> Dict[str, Any]:
        """
        Apply resolution strategy

        Args:
            strategy: Resolution strategy
            values: Conflicting values
            field_name: Field name

        Returns:
            Resolved value and confidence
        """
        if strategy == ResolutionStrategy.MOST_RECENT:
            return self._resolve_most_recent(values)

        elif strategy == ResolutionStrategy.HIGHEST_QUALITY:
            return self._resolve_highest_quality(values)

        elif strategy == ResolutionStrategy.MOST_COMPLETE:
            return self._resolve_most_complete(values)

        elif strategy == ResolutionStrategy.CONSENSUS:
            return self._resolve_consensus(values)

        elif strategy == ResolutionStrategy.TRUSTED_SOURCE:
            return self._resolve_trusted_source(values)

        elif strategy == ResolutionStrategy.MANUAL:
            self.stats['manual_required'] += 1
            return {
                'resolved_value': None,
                'confidence': 0.0,
                'source': 'manual_required',
                'reason': 'Conflict requires manual resolution'
            }

        else:
            # Fallback
            return self._resolve_trusted_source(values)

    def _resolve_most_recent(self, values: List[ConflictValue]) -> Dict[str, Any]:
        """Resolve by selecting most recent value"""
        most_recent = max(values, key=lambda v: v.timestamp)

        return {
            'resolved_value': most_recent.value,
            'confidence': 0.8,
            'source': most_recent.source.value,
            'timestamp': most_recent.timestamp.isoformat()
        }

    def _resolve_highest_quality(self, values: List[ConflictValue]) -> Dict[str, Any]:
        """Resolve by selecting highest quality value"""
        # Filter out None values
        non_null = [v for v in values if v.value is not None]

        if not non_null:
            return {
                'resolved_value': None,
                'confidence': 0.0,
                'source': 'none_available'
            }

        highest_quality = max(non_null, key=lambda v: v.quality_score)

        return {
            'resolved_value': highest_quality.value,
            'confidence': highest_quality.quality_score,
            'source': highest_quality.source.value,
            'quality_score': highest_quality.quality_score
        }

    def _resolve_most_complete(self, values: List[ConflictValue]) -> Dict[str, Any]:
        """Resolve by selecting most complete value"""
        # Filter out None values
        non_null = [v for v in values if v.value is not None]

        if not non_null:
            return {
                'resolved_value': None,
                'confidence': 0.0,
                'source': 'none_available'
            }

        # For strings, prefer longer values
        if isinstance(non_null[0].value, str):
            most_complete = max(non_null, key=lambda v: len(str(v.value)))
        else:
            # For non-strings, use quality score
            most_complete = max(non_null, key=lambda v: v.quality_score)

        return {
            'resolved_value': most_complete.value,
            'confidence': 0.75,
            'source': most_complete.source.value
        }

    def _resolve_consensus(self, values: List[ConflictValue]) -> Dict[str, Any]:
        """Resolve by finding consensus value"""
        # Count occurrences of each value
        value_counts = {}
        value_sources = {}

        for v in values:
            val_str = str(v.value)
            value_counts[val_str] = value_counts.get(val_str, 0) + 1

            if val_str not in value_sources:
                value_sources[val_str] = v

        # Find most common value
        max_count = max(value_counts.values())
        consensus_val_str = max(value_counts, key=value_counts.get)

        confidence = max_count / len(values)
        consensus_value = value_sources[consensus_val_str]

        return {
            'resolved_value': consensus_value.value,
            'confidence': confidence,
            'source': f'consensus_{max_count}/{len(values)}',
            'votes': max_count,
            'total': len(values)
        }

    def _resolve_trusted_source(self, values: List[ConflictValue]) -> Dict[str, Any]:
        """Resolve by selecting value from most trusted source"""
        # Score each value by source trust
        scored_values = []

        for v in values:
            source_name = v.source.value
            trust_score = self.source_trust_scores.get(source_name, 0.5)

            # Combine with source trust score
            combined_score = (trust_score + v.source_trust_score) / 2

            scored_values.append((v, combined_score))

        # Sort by score
        scored_values.sort(key=lambda x: x[1], reverse=True)
        best_value, best_score = scored_values[0]

        return {
            'resolved_value': best_value.value,
            'confidence': best_score,
            'source': best_value.source.value,
            'trust_score': best_score
        }

    async def _apply_custom_resolver(
        self,
        field_name: str,
        values: List[ConflictValue]
    ) -> Dict[str, Any]:
        """Apply custom resolver for field"""
        resolver = self.custom_resolvers[field_name]

        try:
            result = await resolver(values)
            return result
        except Exception as e:
            logger.error(f"Custom resolver failed for '{field_name}': {e}")
            # Fallback to trusted source
            return self._resolve_trusted_source(values)

    def register_custom_resolver(
        self,
        field_name: str,
        resolver: Callable
    ) -> None:
        """
        Register custom resolver for specific field

        Args:
            field_name: Field name
            resolver: Resolver function
        """
        self.custom_resolvers[field_name] = resolver
        logger.info(f"Registered custom resolver for field: {field_name}")

    def set_source_trust_score(
        self,
        source: str,
        score: float
    ) -> None:
        """
        Set trust score for source

        Args:
            source: Source name
            score: Trust score (0-1)
        """
        if not 0 <= score <= 1:
            raise ValueError("Trust score must be between 0 and 1")

        self.source_trust_scores[source] = score
        logger.info(f"Set trust score for {source}: {score}")

    def set_default_strategy(
        self,
        field_name: str,
        strategy: ResolutionStrategy
    ) -> None:
        """
        Set default strategy for field

        Args:
            field_name: Field name
            strategy: Resolution strategy
        """
        self.default_strategies[field_name] = strategy
        logger.info(f"Set default strategy for {field_name}: {strategy.value}")

    def get_statistics(self) -> Dict[str, Any]:
        """
        Get resolver statistics

        Returns:
            Statistics dictionary
        """
        return {
            **self.stats,
            'trust_scores': self.source_trust_scores,
            'custom_resolvers': list(self.custom_resolvers.keys())
        }
