"""
Memory System - Short-term and Long-term memory
================================================

Two types of memory:
1. Short-term (Operational) - Fast pattern matching for Game Loop
2. Long-term (Strategic) - Learning and knowledge accumulation

Memory lifecycle:
- Short-term: TTL-based cache, fast access, automatic expiration
- Long-term: Vector DB, persistent, semantic search

Integration points:
- Game Loop uses short-term for fast pattern matching
- Survival Instinct stores successful corrections in long-term
- Learning uses long-term to train from historical patterns
"""

import asyncio
import logging
import time
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from collections import OrderedDict
import json
import hashlib

logger = logging.getLogger(__name__)


@dataclass
class MemoryEntry:
    """Single memory entry"""
    key: str
    value: Any
    created_at: float
    last_accessed: float
    access_count: int = 0
    ttl_seconds: Optional[float] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    def is_expired(self) -> bool:
        """Check if entry is expired"""
        if self.ttl_seconds is None:
            return False
        return (time.time() - self.created_at) > self.ttl_seconds

    def touch(self):
        """Update access time and count"""
        self.last_accessed = time.time()
        self.access_count += 1


@dataclass
class Pattern:
    """Pattern stored in memory"""
    pattern_id: str
    state_signature: str
    action_type: str
    success_count: int
    failure_count: int
    last_used: float
    created_at: float
    context: Dict[str, Any]

    @property
    def success_rate(self) -> float:
        """Calculate success rate"""
        total = self.success_count + self.failure_count
        if total == 0:
            return 0.0
        return self.success_count / total

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'pattern_id': self.pattern_id,
            'state_signature': self.state_signature,
            'action_type': self.action_type,
            'success_count': self.success_count,
            'failure_count': self.failure_count,
            'success_rate': self.success_rate,
            'last_used': self.last_used,
            'created_at': self.created_at,
            'context': self.context
        }


class ShortTermMemory:
    """
    Short-term memory with TTL

    Fast cache for operational patterns
    Used by Game Loop for quick pattern matching
    Automatic expiration and size limits
    """

    def __init__(
        self,
        max_size: int = 1000,
        default_ttl_seconds: float = 3600.0,
        cleanup_interval_seconds: float = 300.0
    ):
        """
        Args:
            max_size: Maximum entries before eviction
            default_ttl_seconds: Default TTL (1 hour)
            cleanup_interval_seconds: How often to clean expired entries (5 min)
        """
        self.max_size = max_size
        self.default_ttl = default_ttl_seconds
        self.cleanup_interval = cleanup_interval_seconds

        self.cache: OrderedDict[str, MemoryEntry] = OrderedDict()
        self.is_running = False
        self.stats = {
            'hits': 0,
            'misses': 0,
            'evictions': 0,
            'expirations': 0,
            'total_entries': 0
        }

        logger.info(f"ShortTermMemory initialized (max_size: {max_size}, ttl: {default_ttl_seconds}s)")

    def get(self, key: str) -> Optional[Any]:
        """Get value from cache"""
        entry = self.cache.get(key)

        if entry is None:
            self.stats['misses'] += 1
            return None

        if entry.is_expired():
            self.stats['misses'] += 1
            self.stats['expirations'] += 1
            del self.cache[key]
            return None

        entry.touch()
        self.cache.move_to_end(key)  # LRU
        self.stats['hits'] += 1
        return entry.value

    def put(
        self,
        key: str,
        value: Any,
        ttl_seconds: Optional[float] = None,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """Put value into cache"""
        if key in self.cache:
            del self.cache[key]

        entry = MemoryEntry(
            key=key,
            value=value,
            created_at=time.time(),
            last_accessed=time.time(),
            ttl_seconds=ttl_seconds or self.default_ttl,
            metadata=metadata or {}
        )

        self.cache[key] = entry
        self.stats['total_entries'] += 1

        # Evict oldest if over size limit
        if len(self.cache) > self.max_size:
            oldest_key = next(iter(self.cache))
            del self.cache[oldest_key]
            self.stats['evictions'] += 1

    def delete(self, key: str) -> bool:
        """Delete entry"""
        if key in self.cache:
            del self.cache[key]
            return True
        return False

    def cleanup_expired(self):
        """Remove all expired entries"""
        expired_keys = [
            key for key, entry in self.cache.items()
            if entry.is_expired()
        ]

        for key in expired_keys:
            del self.cache[key]
            self.stats['expirations'] += 1

        if expired_keys:
            logger.debug(f"Cleaned up {len(expired_keys)} expired entries")

    async def run_cleanup_loop(self):
        """Background cleanup loop"""
        self.is_running = True
        logger.info("ShortTermMemory cleanup loop started")

        while self.is_running:
            try:
                await asyncio.sleep(self.cleanup_interval)
                self.cleanup_expired()
            except Exception as e:
                logger.error(f"Cleanup error: {e}")

    def stop(self):
        """Stop cleanup loop"""
        self.is_running = False

    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        hit_rate = 0.0
        total_requests = self.stats['hits'] + self.stats['misses']
        if total_requests > 0:
            hit_rate = self.stats['hits'] / total_requests

        return {
            **self.stats,
            'current_size': len(self.cache),
            'hit_rate': hit_rate
        }

    def clear(self):
        """Clear all entries"""
        self.cache.clear()


class LongTermMemory:
    """
    Long-term memory with persistence

    Stores patterns and knowledge for learning
    Supports semantic search via vector embeddings
    Persists to disk and optionally to vector DB
    """

    def __init__(
        self,
        storage_path: str = "/tmp/longterm_memory.json",
        enable_vector_db: bool = False,
        vector_db_config: Optional[Dict[str, Any]] = None
    ):
        """
        Args:
            storage_path: Path to JSON storage file
            enable_vector_db: Enable Qdrant vector DB integration
            vector_db_config: Qdrant configuration
        """
        self.storage_path = storage_path
        self.enable_vector_db = enable_vector_db
        self.vector_db_config = vector_db_config or {}

        self.patterns: Dict[str, Pattern] = {}
        self.vector_client = None

        self.stats = {
            'patterns_stored': 0,
            'patterns_retrieved': 0,
            'successful_patterns': 0,
            'failed_patterns': 0
        }

        self._load_from_disk()

        if enable_vector_db:
            self._init_vector_db()

        logger.info(f"LongTermMemory initialized (storage: {storage_path})")

    def _load_from_disk(self):
        """Load patterns from disk"""
        try:
            import os
            if os.path.exists(self.storage_path):
                with open(self.storage_path, 'r') as f:
                    data = json.load(f)

                for pattern_data in data.get('patterns', []):
                    pattern = Pattern(**pattern_data)
                    self.patterns[pattern.pattern_id] = pattern

                logger.info(f"Loaded {len(self.patterns)} patterns from disk")
        except Exception as e:
            logger.warning(f"Could not load from disk: {e}")

    def _save_to_disk(self):
        """Save patterns to disk"""
        try:
            data = {
                'patterns': [p.to_dict() for p in self.patterns.values()],
                'stats': self.stats,
                'saved_at': datetime.utcnow().isoformat()
            }

            with open(self.storage_path, 'w') as f:
                json.dump(data, f, indent=2)

        except Exception as e:
            logger.error(f"Could not save to disk: {e}")

    def _init_vector_db(self):
        """Initialize Qdrant vector DB connection"""
        try:
            from qdrant_client import QdrantClient
            from qdrant_client.models import Distance, VectorParams

            host = self.vector_db_config.get('host', 'localhost')
            port = self.vector_db_config.get('port', 6333)

            self.vector_client = QdrantClient(host=host, port=port)

            # Create collection if not exists
            collection_name = "pattern_memory"
            try:
                self.vector_client.get_collection(collection_name)
            except:
                self.vector_client.create_collection(
                    collection_name=collection_name,
                    vectors_config=VectorParams(size=768, distance=Distance.COSINE)
                )

            logger.info("Vector DB initialized")

        except ImportError:
            logger.warning("qdrant-client not installed, vector DB disabled")
            self.enable_vector_db = False
        except Exception as e:
            logger.warning(f"Could not initialize vector DB: {e}")
            self.enable_vector_db = False

    def store_pattern(
        self,
        state_signature: str,
        action_type: str,
        success: bool,
        context: Optional[Dict[str, Any]] = None
    ) -> Pattern:
        """Store or update pattern"""
        pattern_id = self._generate_pattern_id(state_signature, action_type)

        if pattern_id in self.patterns:
            pattern = self.patterns[pattern_id]
            if success:
                pattern.success_count += 1
                self.stats['successful_patterns'] += 1
            else:
                pattern.failure_count += 1
                self.stats['failed_patterns'] += 1
            pattern.last_used = time.time()
        else:
            pattern = Pattern(
                pattern_id=pattern_id,
                state_signature=state_signature,
                action_type=action_type,
                success_count=1 if success else 0,
                failure_count=0 if success else 1,
                last_used=time.time(),
                created_at=time.time(),
                context=context or {}
            )
            self.patterns[pattern_id] = pattern
            self.stats['patterns_stored'] += 1

        self._save_to_disk()
        return pattern

    def get_pattern(self, state_signature: str, action_type: str) -> Optional[Pattern]:
        """Get specific pattern"""
        pattern_id = self._generate_pattern_id(state_signature, action_type)
        pattern = self.patterns.get(pattern_id)

        if pattern:
            self.stats['patterns_retrieved'] += 1

        return pattern

    def find_similar_patterns(
        self,
        state_signature: str,
        min_success_rate: float = 0.7,
        limit: int = 5
    ) -> List[Pattern]:
        """Find patterns similar to given state"""
        matching = []

        for pattern in self.patterns.values():
            if self._is_similar(state_signature, pattern.state_signature):
                if pattern.success_rate >= min_success_rate:
                    matching.append(pattern)

        # Sort by success rate and recency
        matching.sort(
            key=lambda p: (p.success_rate, p.last_used),
            reverse=True
        )

        return matching[:limit]

    def _is_similar(self, sig1: str, sig2: str) -> bool:
        """Check if two signatures are similar"""
        # Simple fuzzy matching based on shared components
        parts1 = set(sig1.split('_'))
        parts2 = set(sig2.split('_'))

        if not parts1 or not parts2:
            return False

        overlap = len(parts1.intersection(parts2))
        max_len = max(len(parts1), len(parts2))

        return overlap / max_len >= 0.6

    def _generate_pattern_id(self, state_signature: str, action_type: str) -> str:
        """Generate unique pattern ID"""
        combined = f"{state_signature}:{action_type}"
        return hashlib.sha256(combined.encode()).hexdigest()[:16]

    def get_best_patterns(
        self,
        min_success_rate: float = 0.8,
        min_use_count: int = 5,
        limit: int = 10
    ) -> List[Pattern]:
        """Get best performing patterns"""
        candidates = []

        for pattern in self.patterns.values():
            total_uses = pattern.success_count + pattern.failure_count
            if total_uses >= min_use_count and pattern.success_rate >= min_success_rate:
                candidates.append(pattern)

        candidates.sort(
            key=lambda p: (p.success_rate, p.success_count + p.failure_count),
            reverse=True
        )

        return candidates[:limit]

    def get_stats(self) -> Dict[str, Any]:
        """Get memory statistics"""
        return {
            **self.stats,
            'total_patterns': len(self.patterns),
            'vector_db_enabled': self.enable_vector_db
        }

    def clear(self):
        """Clear all patterns"""
        self.patterns.clear()
        self._save_to_disk()


class MemorySystem:
    """
    Unified memory system

    Coordinates short-term and long-term memory
    Handles pattern lifecycle:
    1. New patterns start in short-term
    2. Successful patterns promoted to long-term
    3. Failed patterns expire from short_term
    """

    def __init__(
        self,
        short_term_config: Optional[Dict[str, Any]] = None,
        long_term_config: Optional[Dict[str, Any]] = None
    ):
        """
        Args:
            short_term_config: Configuration for ShortTermMemory
            long_term_config: Configuration for LongTermMemory
        """
        self.short_term = ShortTermMemory(**(short_term_config or {}))
        self.long_term = LongTermMemory(**(long_term_config or {}))

        self.is_running = False

        logger.info("MemorySystem initialized")

    async def start(self):
        """Start memory system"""
        self.is_running = True
        asyncio.create_task(self.short_term.run_cleanup_loop())
        logger.info("MemorySystem started")

    def stop(self):
        """Stop memory system"""
        self.is_running = False
        self.short_term.stop()
        logger.info("MemorySystem stopped")

    def remember_short_term(
        self,
        key: str,
        value: Any,
        ttl_seconds: Optional[float] = None
    ):
        """Store in short-term memory"""
        self.short_term.put(key, value, ttl_seconds)

    def recall_short_term(self, key: str) -> Optional[Any]:
        """Recall from short_term memory"""
        return self.short_term.get(key)

    def remember_pattern(
        self,
        state_signature: str,
        action_type: str,
        success: bool,
        context: Optional[Dict[str, Any]] = None
    ) -> Pattern:
        """
        Remember pattern in long-term memory

        This is called after action execution to record result
        """
        pattern = self.long_term.store_pattern(
            state_signature,
            action_type,
            success,
            context
        )

        # Also cache in short-term if successful
        if success:
            cache_key = f"pattern:{state_signature}:{action_type}"
            self.short_term.put(cache_key, pattern, ttl_seconds=7200.0)  # 2 hours

        return pattern

    def find_matching_patterns(
        self,
        state_signature: str,
        min_success_rate: float = 0.7
    ) -> List[Pattern]:
        """Find patterns matching current state"""
        # Check short-term cache first
        cache_key = f"pattern_search:{state_signature}"
        cached = self.short_term.get(cache_key)

        if cached is not None:
            return cached

        # Query long-term memory
        patterns = self.long_term.find_similar_patterns(
            state_signature,
            min_success_rate
        )

        # Cache results
        self.short_term.put(cache_key, patterns, ttl_seconds=600.0)  # 10 min

        return patterns

    def get_system_stats(self) -> Dict[str, Any]:
        """Get complete memory system statistics"""
        return {
            'short_term': self.short_term.get_stats(),
            'long_term': self.long_term.get_stats(),
            'is_running': self.is_running
        }


async def create_memory_system(
    short_term_max_size: int = 1000,
    short_term_ttl: float = 3600.0,
    long_term_storage_path: str = "/tmp/longterm_memory.json",
    enable_vector_db: bool = False
) -> MemorySystem:
    """
    Create and start memory system

    Args:
        short_term_max_size: Max entries in short-term cache
        short_term_ttl: Default TTL for short-term entries
        long_term_storage_path: Path to long-term storage file
        enable_vector_db: Enable vector DB for semantic search

    Returns:
        Started MemorySystem instance
    """
    memory_system = MemorySystem(
        short_term_config={
            'max_size': short_term_max_size,
            'default_ttl_seconds': short_term_ttl
        },
        long_term_config={
            'storage_path': long_term_storage_path,
            'enable_vector_db': enable_vector_db
        }
    )

    await memory_system.start()
    return memory_system
